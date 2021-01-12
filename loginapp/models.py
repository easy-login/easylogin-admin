from django.db import models
from django.contrib.auth.models import AbstractUser, PermissionsMixin, BaseUserManager, User
from django.utils.translation import ugettext_lazy as _
from django.utils import timezone
from django.shortcuts import get_object_or_404

from urllib import parse
import json

# Model's constant7
MAX_LENGTH_SHORT_FIELD = 127
MAX_LENGTH_MEDIUM_FIELD = 255
MAX_LENGTH_LONG_FIELD = 500


# Create your models here.
class User(AbstractUser):
    email = models.EmailField(unique=True, max_length=MAX_LENGTH_SHORT_FIELD)
    username = models.CharField(unique=True, max_length=64)
    phone = models.CharField(max_length=MAX_LENGTH_SHORT_FIELD, null=True)
    password = models.CharField(max_length=MAX_LENGTH_SHORT_FIELD)
    first_name = models.CharField(max_length=MAX_LENGTH_SHORT_FIELD, null=True)
    last_name = models.CharField(max_length=MAX_LENGTH_SHORT_FIELD, null=True)
    address = models.CharField(max_length=MAX_LENGTH_MEDIUM_FIELD, null=True)
    company = models.CharField(max_length=MAX_LENGTH_SHORT_FIELD, null=True)
    is_superuser = models.SmallIntegerField(default=0)
    is_active = models.SmallIntegerField(default=1)
    deleted = models.SmallIntegerField(default=0)
    level = models.IntegerField(default=0)

    @staticmethod
    def get_all_user(user):
        return User.objects.all() if user.is_superuser else []

    class Meta:
        db_table = 'easylogin_admins'


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

    def options_as_restrict_map(self):
        options_list = json.loads(self.options)
        options_map = {}
        for option in options_list:
            if 'restrict_levels' in option:
                options_map[option['key']] = int(option['restrict_levels'])
        return options_map

    def __str__(self):
        return u'{0}'.format(self.name)

    class Meta:
        db_table = 'easylogin_providers'
        unique_together = ('name', 'version')

    @classmethod
    def provider_names(cls):
        if not cls.PROVIDER_NAMES:
            names = Provider.objects.order_by('name').values_list('name').distinct()
            cls.PROVIDER_NAMES = [name[0] for name in names]
        return cls.PROVIDER_NAMES


class App(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now=True)
    name = models.CharField(max_length=127)
    api_key = models.CharField(max_length=127)
    callback_uris = models.URLField(max_length=2047)
    allowed_ips = models.CharField(max_length=255)
    description = models.TextField()
    deleted = models.SmallIntegerField(default=0)
    owner = models.ForeignKey(User, on_delete=models.CASCADE)
    options = models.CharField(max_length=1023)

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
        for idx, uri in enumerate(callback_uri_list):
            if uri and idx < 10:
                cu_value += parse.quote_plus(uri) + '|'
        cu_value = cu_value[:-1]
        self.callback_uris = cu_value

    def allowed_ips_as_list(self):
        if self.allowed_ips == '':
            return []
        return self.allowed_ips.split('|')

    def set_allowed_ips(self, allowed_ips_list):
        ai_value = ''
        for idx, ip in enumerate(allowed_ips_list):
            if ip and idx <= 5:
                ai_value += ip + '|'
        ai_value = ai_value[:-1]
        self.allowed_ips = ai_value

    def get_number_of_channels(self):
        return len(Channel.objects.filter(app_id=self.id))

    def update_modified_at(self):
        self.modified_at = timezone.now()
        # self.modified_at = datetime.datetime.now()

    def set_options(self, options):
        self.options = "|".join(options)

    def get_options_as_list(self):
        if self.options == "":
            return []
        return self.options.split("|")

    class Meta:
        db_table = 'easylogin_apps'


class Channel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now=True)
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
        db_table = 'easylogin_channels'
        unique_together = ('app', 'provider')


class AdminSetting(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now=True)
    name = models.CharField(max_length=64, unique=True)
    value = models.CharField(max_length=64)
    created_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'easylogin_system_settings'


class SocialUser(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now=True)
    ref_id = models.CharField(max_length=128, db_column="pk", null=False)
    deleted = models.SmallIntegerField(default=0)
    app = models.ForeignKey(App, on_delete=models.CASCADE)

    class Meta:
        db_table = 'easylogin_users'


class SocialProfile(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now=True)
    provider = models.CharField(max_length=15, null=False)
    profile_id = models.CharField(max_length=40, db_column="pk", unique=True, null=False)
    attrs = models.CharField(max_length=8191, null=False)
    scope_id = models.CharField(max_length=255, null=False)
    last_authorized_at = models.DateTimeField(null=True, db_column='authorized_at')
    login_count = models.IntegerField(default=0, null=False)
    verified = models.SmallIntegerField(default=0, null=False)
    linked_at = models.DateTimeField(null=True)
    alias = models.BigIntegerField(null=False)

    deleted = models.SmallIntegerField(default=0)
    prohibited = models.SmallIntegerField(default=0)

    app = models.ForeignKey(App, on_delete=models.CASCADE)
    user = models.ForeignKey(SocialUser, on_delete=models.CASCADE, null=True)

    class Meta:
        db_table = 'easylogin_social_profiles'


class Token(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now=True)
    provider = models.CharField(max_length=15)
    oa_version = models.SmallIntegerField()
    token_type = models.CharField(max_length=15)
    access_token = models.CharField(max_length=2047, null=True)
    refresh_token = models.CharField(max_length=2047, null=True)
    id_token = models.CharField(max_length=2047, null=True)
    expires_at = models.DateTimeField(null=True)
    oa1_token = models.CharField(max_length=1023, null=True)
    oa1_secret = models.CharField(max_length=1023, null=True)

    social_profile = models.ForeignKey(SocialProfile, db_column='social_id', on_delete=models.CASCADE)

    class Meta:
        db_table = 'easylogin_tokens'


class AuthLog(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now=True)
    provider = models.CharField(max_length=15)
    callback_uri = models.CharField(max_length=2047)
    callback_if_failed = models.CharField(max_length=2047, db_column='callback_failed', null=True)
    nonce = models.CharField(max_length=32)
    status = models.CharField(max_length=15)
    is_login = models.SmallIntegerField(null=True)
    intent = models.CharField(max_length=32, null=True)
    platform = models.CharField(max_length=8)

    oa1_token = models.CharField(max_length=1023, null=True)
    oa1_secret = models.CharField(max_length=1023, null=True)

    app = models.ForeignKey(App, on_delete=models.CASCADE)
    social_profile = models.ForeignKey(SocialProfile, db_column='social_id', on_delete=models.CASCADE)

    class Meta:
        db_table = 'easylogin_auth_logs'


class AssociateLog(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now=True)
    provider = models.CharField(max_length=15)
    dst_social_id = models.BigIntegerField()
    status = models.CharField(max_length=15)
    nonce = models.CharField(max_length=32)

    app = models.ForeignKey(App, on_delete=models.CASCADE)

    class Meta:
        db_table = 'easylogin_associate_logs'


class JournalLog(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now=True)
    path = models.CharField(max_length=4095, null=True)
    ua = models.CharField(max_length=1023, null=True)
    ip = models.CharField(max_length=15, null=True)
    ref_id = models.IntegerField()

    class Meta:
        db_table = 'easylogin_journal_logs'
