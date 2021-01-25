import uuid
from datetime import datetime

from django.apps import AppConfig
from django.db import connection
from django.contrib.auth.hashers import PBKDF2PasswordHasher
from django.conf import settings

from loginapp.init_providers import init_providers


class SocialPlusConfig(AppConfig):
    name = 'loginapp'

    def ready(self):
        try:
            print('Creating admin account if not exist...')
            hasher = PBKDF2PasswordHasher()
            hashed_pw = hasher.encode(settings.SUPER_ADMIN_PASSWORD, uuid.uuid4().hex[:16])

            with connection.cursor() as cursor:
                cursor.execute("SELECT id FROM easylogin_admins WHERE username = 'superadmin'")
                row = cursor.fetchone()
                if not row:
                    cursor.execute("""
                        INSERT INTO easylogin_admins (username, email, password, 
                            is_superuser, is_active, deleted, is_staff, level,
                            date_joined, first_name, last_name,
                            phone, address, company)
                        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                    """, ('superadmin', settings.SUPER_ADMIN_EMAIL, hashed_pw, 
                        1, 1, 0, 0, 65535, 
                        datetime.utcnow(), 'Super', 'Admin', 
                        '0400666905', '1226-14, Kanda Konya-cho, Chiyoda-ku', 'mirabo'))
                    connection.commit()
        except Exception as e:
            print(e)