export DJANGO_SETTINGS_MODULE=SocialPlus.settings

gunicorn -w 2 -b 0.0.0.0:8000 SocialPlus.wsgi:application
