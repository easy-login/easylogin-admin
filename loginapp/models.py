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
