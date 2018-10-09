from django.db import models
from django.contrib.auth.models import AbstractUser, PermissionsMixin, BaseUserManager, User
from django.utils.translation import ugettext_lazy as _
import datetime
from django.utils import timezone
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

    class Meta:
        db_table = "admins"


class Provider(models.Model):
    name = models.CharField(max_length=30)
    version = models.CharField(max_length=7)
    required_permissions = models.CharField(max_length=1023)
    basic_fields = models.CharField(max_length=4095)
    advanced_fields = models.CharField(max_length=4095)
    options = models.CharField(null=True, max_length=4095)

    def required_permissions_as_list(self):
        if self.required_permissions == "":
            return []
        return self.required_permissions.split("|")

    def basic_fields_as_object(self):
        return json.loads(self.basic_fields)

    def advanced_fields_as_object(self):
        return json.loads(self.advanced_fields)

    def options_as_object(self):
        return json.loads(self.options)

    def __str__(self):
        return u'{0}'.format(self.name)

    class Meta:
        db_table = "providers"


class App(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now_add=True)
    name = models.CharField(max_length=67)
    api_key = models.CharField(max_length=127)
    callback_uris = models.URLField(max_length=2047)
    allowed_ips = models.CharField(max_length=127)
    description = models.TextField()
    owner = models.ForeignKey(User, on_delete=models.CASCADE)

    def callback_uris_as_list(self):
        if self.callback_uris == "":
            return []
        callback_uris_view = parse.unquote_plus(self.callback_uris)
        return callback_uris_view.split('|')

    def set_callback_uris(self, callback_uri_list):
        cu_value = ''
        for uri in callback_uri_list:
            cu_value += parse.quote_plus(uri) + "|"
        cu_value = cu_value[:-1]
        self.callback_uris = cu_value

    def allowed_ips_as_list(self):
        if self.allowed_ips == "":
            return []
        return self.allowed_ips.split('|')

    def set_allowed_ips(self, allowed_ips_list):
        ai_value = ''
        for ip in allowed_ips_list:
            if ip:
                ai_value += ip + "|"
        ai_value = ai_value[:-1]
        self.allowed_ips = ai_value

    def get_number_of_channels(self):
        return len(Channel.objects.filter(app_id=self.id))

    def update_modified_at(self):
        self.modified_at = timezone.now()
        # self.modified_at = datetime.datetime.now()

    class Meta:
        db_table = "apps"


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

    def required_fields_as_list(self):
        return self.required_fields.split('|')

    def options_as_list(self):
        return self.options.split('|')

    class Meta:
        db_table = "channels"
        unique_together = ('app', 'provider')
