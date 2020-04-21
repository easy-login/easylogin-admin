export DJANGO_SETTINGS_MODULE=SocialPlus.settings

gunicorn SocialPlus.wsgi:application
