from django.db import models
from django.contrib.auth.models import AbstractUser, PermissionsMixin, BaseUserManager, User
from django.utils.translation import ugettext_lazy as _
from django.utils import timezone
from django.shortcuts import get_object_or_404

from urllib import parse
import json

# Model's constant
MAX_LENGTH_SHORT_FIELD = 100
MAX_LENGTH_MEDIUM_FIELD = 255
MAX_LENGTH_LONG_FIELD = 500


# Create your models here.
class User(AbstractUser):
    email = models.EmailField(unique=True, null=True, max_length=MAX_LENGTH_SHORT_FIELD)
    username = models.CharField(max_length=MAX_LENGTH_SHORT_FIELD)
    phone = models.CharField(max_length=MAX_LENGTH_SHORT_FIELD)
    password = models.CharField(max_length=MAX_LENGTH_SHORT_FIELD)
    first_name = models.CharField(max_length=MAX_LENGTH_SHORT_FIELD)
    last_name = models.CharField(max_length=MAX_LENGTH_SHORT_FIELD)
    address = models.CharField(max_length=MAX_LENGTH_MEDIUM_FIELD)
    company = models.CharField(max_length=MAX_LENGTH_SHORT_FIELD)
    is_superuser = models.SmallIntegerField(default=0)
    is_active = models.SmallIntegerField(default=1)
    deleted = models.SmallIntegerField(default=0)
    level = models.SmallIntegerField(default=0)

    @staticmethod
    def get_all_user(user):
        return User.objects.all() if user.is_superuser else []

    class Meta:
        db_table = 'admins'


class Provider(models.Model):
    name = models.CharField(max_length=30)
    version = models.CharField(max_length=7)
    required_permissions = models.CharField(max_length=1023)
    basic_fields = models.CharField(max_length=4095)
    advanced_fields = models.CharField(max_length=4095)
    options = models.CharField(null=True, max_length=4095)

    PROVIDER_NAMES = []

    def required_permissions_as_list(self):
        if self.required_permissions == '':
            return []
        return self.required_permissions.split('|')

    def basic_fields_as_object(self):
        return json.loads(self.basic_fields)

    def advanced_fields_as_object(self):
        return json.loads(self.advanced_fields)

    def options_as_object(self):
        return json.loads(self.options)

    def __str__(self):
        return u'{0}'.format(self.name)

    class Meta:
        db_table = 'providers'

    @classmethod
    def provider_names(cls):
        if not cls.PROVIDER_NAMES:
            names = Provider.objects.order_by('name').values_list('name').distinct()
            cls.PROVIDER_NAMES = [name[0] for name in names]
        return cls.PROVIDER_NAMES


class App(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now_add=True)
    name = models.CharField(max_length=67)
    api_key = models.CharField(max_length=127)
    callback_uris = models.URLField(max_length=2047)
    allowed_ips = models.CharField(max_length=127)
    description = models.TextField()
    deleted = models.SmallIntegerField(default=0)
    owner = models.ForeignKey(User, on_delete=models.CASCADE)
    options = models.CharField(max_length=255)

    @staticmethod
    def get_all_app(user, owner_id=-1, order_by='name'):
        # if user.is_superuser:
        #     return App.objects.filter(deleted=0).order_by(order_by) if owner_id == -1 \
        #         else App.objects.filter(deleted=0, owner_id=owner_id).order_by(order_by)
        return App.objects.filter(owner_id=user.id, deleted=0).order_by(order_by)

    @staticmethod
    def get_app_by_user(app_id, user):
        return get_object_or_404(App, pk=app_id, owner_id=user.id, deleted=0)
        # get_object_or_404(App, pk=app_id, deleted=0) if user.is_superuser \

    def callback_uris_as_list(self):
        if self.callback_uris == '':
            return []
        callback_uris_view = parse.unquote_plus(self.callback_uris)
        return callback_uris_view.split('|')

    def set_callback_uris(self, callback_uri_list):
        cu_value = ''
        for uri in callback_uri_list:
            cu_value += parse.quote_plus(uri) + '|'
        cu_value = cu_value[:-1]
        self.callback_uris = cu_value

    def allowed_ips_as_list(self):
        if self.allowed_ips == '':
            return []
        return self.allowed_ips.split('|')

    def set_allowed_ips(self, allowed_ips_list):
        ai_value = ''
        for ip in allowed_ips_list:
            if ip:
                ai_value += ip + '|'
        ai_value = ai_value[:-1]
        self.allowed_ips = ai_value

    def get_number_of_channels(self):
        return len(Channel.objects.filter(app_id=self.id))

    def update_modified_at(self):
        self.modified_at = timezone.now()
        # self.modified_at = datetime.datetime.now()

    class Meta:
        db_table = 'apps'


class Channel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now_add=True)
    provider = models.CharField(max_length=30)
    api_version = models.CharField(max_length=7)
    client_id = models.CharField(max_length=255)
    client_secret = models.CharField(max_length=255)
    permissions = models.CharField(max_length=4095)
    required_fields = models.CharField(null=True, max_length=4095)
    options = models.CharField(null=True, max_length=1023)
    app = models.ForeignKey(App, on_delete=models.CASCADE)
    is_premium = models.SmallIntegerField(default=0)

    def required_fields_as_list(self):
        return self.required_fields.split('|')

    def options_as_list(self):
        return self.options.split('|')

    class Meta:
        db_table = 'channels'
        unique_together = ('app', 'provider')
