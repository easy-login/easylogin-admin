from django.db import models
from django.contrib.auth.models import AbstractUser, PermissionsMixin, BaseUserManager, User
from django.utils.translation import ugettext_lazy as _

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


class Provider(models.Model):
    id = models.CharField(max_length=30, primary_key=True)
    version = models.CharField(max_length=7)
    permission = models.CharField(max_length=1023)

    def permission_as_list(self):
        return self.permission.split(",")

    def __str__(self):
        return u'{0}'.format(self.id)


class App(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now_add=True)
    name = models.CharField(max_length=67)
    api_key = models.CharField(max_length=127)
    callback_uri = models.URLField(max_length=2047)
    allowed_ips = models.CharField(max_length=127)
    description = models.TextField()
    # owner_id = models.IntegerField()
    owner_id = models.ForeignKey(User, on_delete=models.CASCADE)


class Channel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now_add=True)
    provider = models.CharField(max_length=30)
    client_id = models.CharField(max_length=255)
    client_secret = models.CharField(max_length=255)
    permissions = models.CharField(max_length=1023)
    app_id = models.ForeignKey(App, on_delete=models.CASCADE)
