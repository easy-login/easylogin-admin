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
    id = models.CharField(max_length=15, primary_key=True)
    version = models.CharField(max_length=7)
    permission = models.CharField(max_length=1023)


class App(models.Model):
    created_at = models.DateTimeField()
    modified_at = models.DateTimeField(auto_now_add=True)
    domain = models.CharField(max_length=67)
    api_key = models.CharField(max_length=127)
    callback_uri = models.URLField(max_length=2047)
    allowed_ips = models.CharField(max_length=127)
    description = models.TextField()
    owner_id = models.IntegerField()
    # owner_id = models.Foreignkey(User, on_delete=models.CASCADE)


class Channel(models.Model):
    created_at = models.DateTimeField()
    modified_at = models.DateTimeField(auto_now_add=True)
    provider = models.ForeignKey(Provider, on_delete=models.CASCADE)
    client_id = models.CharField(max_length=255)
    client_secret = models.CharField(max_length=255)
    permissions = models.CharField(max_length=1023)