from datetime import datetime, timedelta
import pytz

from django.db import connection
from django.conf import settings

from loginapp.models import Provider
from loginapp.utils import dict_fetchall, convert_to_user_timezone
from loginapp.utils import getChartColor


def get_total_auth_report(app_id):
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT is_login, status, count(id) 
            FROM easylogin_auth_logs 
            WHERE app_id = %s and status IN ('succeeded', 'wait_reg')
            GROUP BY is_login, status""", (app_id,))
        rows = cursor.fetchall()
        results = []
        for row in rows:
            if row[0]:
                results.append(('Login', row[2]))
            else:
                reg_status = 'Pending Registration' if row[1] == 'wait_reg' else 'Done Registration'
                results.append((reg_status, row[2]))
        return results


def get_total_provider_report(app_id):
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT provider, count(id) 
            FROM easylogin_auth_logs 
            WHERE app_id = %s and status = 'succeeded'
            GROUP BY provider ORDER BY provider""", (app_id,))
        rows = cursor.fetchall()
        return [(row[0], row[1], getChartColor(row[0])) for row in rows]


def get_auth_report_per_provider(app_id, from_dt=None, to_dt=None, auth_state=1):
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

        if auth_state == 1:  # login
            is_login = 1
            status = 'succeeded'
        elif auth_state == 2:  # wait register
            is_login = 0
            status = 'wait_reg'
        else:
            is_login = 0
            status = 'succeeded'

        cursor.execute("""
            SELECT provider, DATE(CONVERT_TZ(modified_at, '+00:00', %s)) as dt, COUNT(id) 
            FROM easylogin_auth_logs 
            WHERE app_id = %s 
                AND modified_at BETWEEN %s AND %s 
                AND status = %s 
                AND is_login = %s
            GROUP BY dt, provider
            ORDER BY provider
            """, (settings.TIME_ZONE_OFFSET, app_id, from_dt, to_dt, status, is_login))

        while True:
            rows = cursor.fetchmany(500)
            if not rows:
                break
            for row in rows:
                dt_str = row[1].strftime('%Y-%m-%d')
                provider = row[0]
                results[provider][dt_str] = int(row[2])
                results['total'][dt_str] += int(row[2])

        return list(labels), results


def get_user_report(app_id, page_length, start_row, order_by, search_value):
    with connection.cursor() as cursor:
        offset = start_row
        limit = page_length
        if search_value:
            cursor.execute("""
                SELECT SQL_CALC_FOUND_ROWS p.alias AS social_id, 
                    u.pk AS user_pk,
                    MAX(p.authorized_at) AS last_login, 
                    SUM(p.login_count) AS login_total, 
                    GROUP_CONCAT(p.provider) AS linked_providers,
                    prohibited
                FROM easylogin_social_profiles p
                LEFT JOIN easylogin_users u ON u.id = p.user_id
                WHERE p.app_id = %s AND p.deleted = 0 AND u.pk = %s 
                GROUP BY alias, u.pk, prohibited
                ORDER BY {} LIMIT {}, {}
                """.format(order_by, limit, offset), (app_id, search_value,))
        else:
            cursor.execute("""
                SELECT SQL_CALC_FOUND_ROWS p.alias AS social_id, 
                    u.pk as user_pk,
                    MAX(p.authorized_at) AS last_login,  
                    SUM(p.login_count) AS login_total, 
                    GROUP_CONCAT(p.provider) AS linked_providers,
                    prohibited
                FROM easylogin_social_profiles p 
                LEFT JOIN easylogin_users u ON u.id = p.user_id
                WHERE p.app_id = %s AND p.deleted = 0
                GROUP BY p.alias, u.pk, prohibited
                ORDER BY {} LIMIT {}, {}
                """.format(order_by, offset, limit), (app_id,))

        rows = dict_fetchall(cursor)
        for row in rows:
            row['last_login'] = convert_to_user_timezone(row['last_login'])
            row['linked_providers'] = row['linked_providers'].split(',')
        cursor.execute("""
                    SELECT FOUND_ROWS()
                """)
        records_total = cursor.fetchone()[0]
        return records_total, rows


def get_list_admin_users(page_length, start_row, order_by, search_value):
    with connection.cursor() as cursor:
        offset = start_row
        limit = page_length
        if search_value:
            cursor.execute("""
                SELECT
                    SQL_CALC_FOUND_ROWS 
                    admins.id as user_id,
                    admins.username,
                    admins.email,
                    count(apps.id) as total_apps,
                    DATE(CONVERT_TZ(admins.last_login, '+00:00', %s)) as last_login,
                    admins.deleted ,
                    admins.level
                FROM easylogin_admins admins
                LEFT JOIN easylogin_apps apps 
                    ON admins.id = apps.owner_id AND apps.deleted = 0
                WHERE admins.username=%s 
                GROUP BY admins.id
                ORDER BY {} LIMIT {}, {}
            """.format(order_by, offset, limit), (settings.TIME_ZONE_OFFSET, search_value))
        else:
            cursor.execute("""
                SELECT 
                    SQL_CALC_FOUND_ROWS
                    admins.id as user_id,
                    admins.username,
                    admins.email,
                    count(apps.id) as total_apps,
                    DATE(CONVERT_TZ(admins.last_login, '+00:00', %s)) as last_login,
                    admins.deleted,
                    admins.level
                FROM easylogin_admins admins
                LEFT JOIN easylogin_apps apps
                    ON admins.id = apps.owner_id AND apps.deleted = 0
                GROUP BY admins.id
                ORDER BY {} LIMIT {}, {}
            """.format(order_by, offset, limit), (settings.TIME_ZONE_OFFSET,))
        rows = dict_fetchall(cursor)
        cursor.execute("""
                            SELECT FOUND_ROWS()
                        """)
        records_total = cursor.fetchone()
        print(records_total)
        return records_total, rows


def get_list_apps(page_length, start_row, order_by, search_value):
    with connection.cursor() as cursor:
        offset = start_row
        limit = page_length
        if search_value:
            cursor.execute("""
                SELECT SQL_CALC_FOUND_ROWS a.id, a.name, o.username AS owner, 
                    COUNT(p.id) AS total_user, 
                    DATE(CONVERT_TZ(a.created_at, '+00:00', %s)) as created_at, 
                    DATE(CONVERT_TZ(a.modified_at, '+00:00', %s)) as modified_at, 
                    a.deleted
                FROM easylogin_apps AS a
                LEFT OUTER JOIN easylogin_social_profiles AS p ON a.id = p.app_id
                INNER JOIN easylogin_admins AS o ON a.owner_id = o.id
                WHERE a.name=%s OR o.username=%s
                GROUP BY a.id 
                ORDER BY {} LIMIT {}, {}
            """.format(order_by, offset, limit), (settings.TIME_ZONE_OFFSET, settings.TIME_ZONE_OFFSET,
                                                  search_value, search_value))
        else:
            cursor.execute("""
                SELECT SQL_CALC_FOUND_ROWS a.id, a.name, o.username AS owner, 
                    COUNT(p.id) AS total_user, 
                    DATE(CONVERT_TZ(a.created_at, '+00:00', %s)) as created_at, 
                    DATE(CONVERT_TZ(a.modified_at, '+00:00', %s)) as modified_at, 
                    a.deleted
                FROM easylogin_apps AS a
                LEFT OUTER JOIN easylogin_social_profiles AS p ON a.id = p.app_id
                INNER JOIN easylogin_admins AS o ON a.owner_id = o.id
                GROUP BY a.id 
                ORDER BY {} LIMIT {}, {}
            """.format(order_by, offset, limit), (settings.TIME_ZONE_OFFSET, settings.TIME_ZONE_OFFSET))
        rows = dict_fetchall(cursor)
        cursor.execute("""
                            SELECT FOUND_ROWS()
                        """)
        records_total = cursor.fetchone()[0]
        return records_total, rows


def get_register_report(page_length, start_row, order_by, search_value):
    with connection.cursor() as cursor:
        offset = start_row
        limit = page_length
        if search_value:
            cursor.execute("""
                SELECT SQL_CALC_FOUND_ROWS a.id, a.name, o.username, 
                    DATE(CONVERT_TZ(a.created_at, '+00:00', %s)) as created_at, 
                    DATE(CONVERT_TZ(a.modified_at, '+00:00', %s)) as modified_at, 
                    a.deleted,
                    COUNT(p.id) AS total,
                    SUM(CASE WHEN verified = 0 THEN 1 ELSE 0 END) AS authorized,
                    SUM(CASE WHEN verified = 1 THEN 1 ELSE 0 END) AS register_done
                FROM easylogin_social_profiles AS p
                INNER JOIN easylogin_apps AS a ON p.app_id = a.id
                INNER JOIN easylogin_admins AS o ON a.owner_id = o.id
                WHERE o.username = %s
                GROUP BY p.app_id
                ORDER BY {} LIMIT {}, {}
            """.format(order_by, offset, limit), (settings.TIME_ZONE_OFFSET, settings.TIME_ZONE_OFFSET, search_value,))
        else:
            cursor.execute("""
                SELECT SQL_CALC_FOUND_ROWS a.id, a.name, o.username, 
                    DATE(CONVERT_TZ(a.created_at, '+00:00', %s)) as created_at, 
                    DATE(CONVERT_TZ(a.modified_at, '+00:00', %s)) as modified_at, 
                    a.deleted,
                    COUNT(p.id) AS total,
                    SUM(CASE WHEN verified = 0 THEN 1 ELSE 0 END) AS authorized,
                    SUM(CASE WHEN verified = 1 THEN 1 ELSE 0 END) AS register_done
                FROM easylogin_social_profiles AS p
                INNER JOIN easylogin_apps AS a ON p.app_id = a.id
                INNER JOIN easylogin_admins AS o ON a.owner_id = o.id 
                GROUP BY p.app_id
                ORDER BY {} LIMIT {}, {}
            """.format(order_by, offset, limit), (settings.TIME_ZONE_OFFSET, settings.TIME_ZONE_OFFSET))
        rows = dict_fetchall(cursor)
        cursor.execute("""
                            SELECT FOUND_ROWS()
                        """)
        records_total = cursor.fetchone()[0]
        return records_total, rows


def get_social_users(social_id):
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT attrs,provider 
            FROM social_profiles
            WHERE alias = %s
        """, (social_id,))
        rows = dict_fetchall(cursor)
        return rows
