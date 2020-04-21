from django.apps import AppConfig
from django.db import connection

from loginapp.init_providers import init_providers


class SocialPlusConfig(AppConfig):
    name = 'loginapp'

    def ready(self):
        with connection.cursor() as cursor:
            init_providers(connection, cursor)
