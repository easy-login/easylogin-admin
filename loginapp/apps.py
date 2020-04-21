import uuid

from django.apps import AppConfig
from django.db import connection
from django.contrib.auth.hashers import PBKDF2PasswordHasher

from loginapp.init_providers import init_providers


class SocialPlusConfig(AppConfig):
    name = 'loginapp'

    def ready(self):
        try:
            print('App ready, run init_providers script')
            with connection.cursor() as cursor:
                init_providers(connection, cursor)

            print('Creating admin account...')
            hasher = PBKDF2PasswordHasher()
            hashed_pw = hasher.encode('Mirabo!23', uuid.uuid4().hex[:16])

            with connection.cursor() as cursor:
                cursor.execute("SELECT id FROM admins WHERE username = 'admin'")
                row = cursor.fetchone()
                if not row:
                    cursor.execute("""
                        INSERT INTO admins (username, email, password, is_superuser, level, first_name, last_name)
                        VALUES (%s, %s, %s, %s, %s, %s, %s)
                    """, ('admin', 'anhtn@mirabo.com.vn', hashed_pw, 1, 65535, 'Mirabo', 'Admin'))
                    connection.commit()
        except Exception as e:
            print(e)