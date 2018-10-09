from datetime import datetime, timedelta

from django.db import connection

from loginapp.models import Provider
from loginapp.utils import dict_fetchall, convert_to_user_timezone


def get_total_auth_report(app_id):
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT is_login, count(id) 
            FROM auth_logs 
            WHERE app_id = %s and status = 'succeeded' 
            GROUP BY is_login""", (app_id,))
        rows = cursor.fetchall()
        return [('Login' if int(row[0]) else 'Register', row[1]) for row in rows]


def get_total_provider_report(app_id):
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT provider, count(id) 
            FROM auth_logs 
            WHERE app_id = %s and status = 'succeeded'
            GROUP BY provider ORDER BY provider""", (app_id,))
        rows = cursor.fetchall()
        return [(row[0], row[1]) for row in rows]


def get_auth_report_per_provider(app_id, from_dt=None, to_dt=None, is_login=1):
    with connection.cursor() as cursor:
        _from = datetime.strptime(from_dt, '%Y-%m-%d')
        _to = datetime.strptime(to_dt, '%Y-%m-%d')

        providers = Provider.provider_names()
        results = {provider: dict() for provider in providers}
        results['total'] = dict()
        labels = set()

        while _from <= _to:
            dt_str = _from.strftime('%Y-%m-%d')
            labels.add(dt_str)
            for provider in results:
                results[provider][dt_str] = 0
            _from += timedelta(days=1)

        from_dt += ' 00:00:00'
        to_dt += ' 23:59:59'
        cursor.execute("""
            SELECT provider, DATE(modified_at), COUNT(provider) 
            FROM auth_logs 
            WHERE app_id = %s AND modified_at BETWEEN %s and %s AND status = 'succeeded' AND is_login = %s
            GROUP BY DATE(modified_at), provider
            ORDER BY provider""", (app_id, from_dt, to_dt, is_login))

        i = 0
        while True:
            rows = cursor.fetchmany(500)
            if not rows:
                break
            for row in rows:
                i += 1
                dt_str = row[1].strftime('%Y-%m-%d')
                provider = row[0]
                results[provider][dt_str] = int(row[2])
                results['total'][dt_str] += int(row[2])

        return list(labels), results


def get_user_report(app_id, page_length, start_page, order_by, search_value):
    with connection.cursor() as cursor:
        offset = start_page * page_length
        limit = offset + page_length
        if search_value:
            cursor.execute("""
                SELECT alias AS social_id, 
                    user_pk AS user_id, 
                    MAX(authorized_at) AS last_login, 
                    SUM(login_count) AS login_total, 
                    GROUP_CONCAT(provider) AS linked_providers 
                FROM social_profiles
                WHERE app_id = %s AND user_id = %s 
                GROUP BY alias, user_pk
                ORDER BY {} LIMIT {}, {}
                """.format(order_by, offset, limit), (app_id, search_value,))
        else:
            cursor.execute("""
                SELECT alias AS social_id, 
                    user_pk AS user_id, 
                    MAX(authorized_at) AS last_login,  
                    SUM(login_count) AS login_total, 
                    GROUP_CONCAT(provider) AS linked_providers 
                FROM social_profiles
                WHERE app_id = %s
                GROUP BY alias, user_pk
                ORDER BY {} LIMIT {}, {}
                """.format(order_by, offset, limit), (app_id,))

        rows = dict_fetchall(cursor)
        for row in rows:
            row['last_login'] = convert_to_user_timezone(row['last_login'])
            row['linked_providers'] = row['linked_providers'].split(',')
        return len(rows), rows
