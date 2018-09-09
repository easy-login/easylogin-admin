import hashlib
import pytz
import re
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
