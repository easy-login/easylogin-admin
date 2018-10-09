import re
import string
import secrets

import pytz
from django.utils import timezone
from django.utils.deprecation import MiddlewareMixin
from django.conf import settings


class TimezoneMiddleware(MiddlewareMixin):
    def process_request(self, request):
        tzname = request.session.get('local_timezone')
        print("timezone:" + str(tzname))
        if tzname:
            timezone.activate(pytz.timezone(tzname))
        else:
            timezone.deactivate()


def convert_to_user_timezone(dt):
    return dt.replace(tzinfo=timezone.utc).astimezone(pytz.timezone(settings.TIME_ZONE))


def generateApiKey(nbytes=32):
    alphabet = string.ascii_letters + string.digits
    return ''.join(secrets.choice(alphabet) for _ in range(nbytes))


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


def dict_fetchall(cursor):
    """Return all rows from a cursor as a dict"""
    columns = [col[0] for col in cursor.description]
    return [
        dict(zip(columns, row))
        for row in cursor.fetchall()
    ]


def namedtuple_fetchall(cursor):
    """Return all rows from a cursor as a namedtuple"""
    from collections import namedtuple
    desc = cursor.description
    nt_result = namedtuple('Result', [col[0] for col in desc])
    return [nt_result(*row) for row in cursor.fetchall()]
