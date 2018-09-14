import hashlib
import pytz
import re
import MySQLdb
from datetime import datetime, timedelta
from django.utils import timezone
from django.utils.deprecation import MiddlewareMixin


class TimezoneMiddleware(MiddlewareMixin):
    def process_request(self, request):
        tzname = request.session.get('local_timezone')
        print("timezone:" + str(tzname))
        if tzname:
            timezone.activate(pytz.timezone(tzname))
        else:
            timezone.deactivate()


def generateApiKey(seed):
    return hashlib.sha1(seed).hexdigest()


def validateURL(url):
    regex = re.compile(
        r'^(?:http|ftp)s?://'  # http:// or https://
        r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+(?:[A-Z]{2,6}\.?|[A-Z0-9-]{2,}\.?)|'  # domain...
        r'localhost|'  # localhost...
        r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'  # ...or ip
        r'(?::\d+)?'  # optional port
        r'(?:/?|[/?]\S+)$', re.IGNORECASE)

    return re.match(regex, url) is not None


def getOrderValue(column, value):
    column_dic = {
        '1': 'deleted',
        '2': 'user_id',
        '3': 'last_login',
        '4': 'login_total'
    }
    column_name = column_dic.get(column, 'user_id')
    return '-' + column_name if value == 'desc' else column_name


def getChartColor(provider):
    color_dic = {
        'total': '#188ae2',
        'line': '#10c469',
        'yahoojp': '#ef5350',
        'amazon': '#f9c851',
    }
    return color_dic.get(provider)


def init_mysql_connection(host, user, passwd, db):
    return MySQLdb.connect(host, user, passwd, db)


def get_total_auth_report(db, app_id, is_login):
    cursor = db.cursor()
    cursor.execute("""
        SELECT provider, count(_id) 
        FROM auth_logs 
        WHERE app_id = %s and status = 'succeeded' and is_login = %s
        GROUP BY provider""", (app_id, is_login))
    rows = cursor.fetchmany(1000)
    return [(row[0], row[1]) if row else (None, None) for row in rows]


def get_auth_report_per_provider(db, app_id, from_dt=None, to_dt=None, is_login=1):
    cursor = db.cursor()
    _from = datetime.strptime(from_dt, '%Y-%m-%d')
    _to = datetime.strptime(to_dt, '%Y-%m-%d')

    results = {'line': {}, 'yahoojp': {}, 'amazon': {}, 'total': {}}
    for provider in ['line', 'yahoojp', 'amazon', 'total']:
        results[provider] = {}

    while _from <= _to:
        dt_str = _from.strftime('%Y-%m-%d')
        for provider in ['line', 'yahoojp', 'amazon', 'total']:
            results[provider][dt_str] = 0
        _from += timedelta(days=1)

    from_dt += ' 00:00:00'
    to_dt += ' 23:59:59'
    cursor.execute("""
        SELECT provider, DATE(modified_at), COUNT(provider) 
        FROM auth_logs 
        WHERE app_id = %s AND modified_at BETWEEN %s and %s AND status = 'succeeded' AND is_login = %s
        GROUP BY DATE(modified_at), provider""", (app_id, from_dt, to_dt, is_login))

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
    return results
