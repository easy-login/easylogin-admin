from django.forms import ModelForm
from django.forms import ModelChoiceField
from django import forms
from django.contrib.auth import password_validation

from loginapp.models import User, App, Channel, Provider
from loginapp import models
from loginapp import utils

from urllib.parse import urlparse


class RegisterForm(ModelForm):
    email = forms.EmailField(max_length=models.MAX_LENGTH_SHORT_FIELD, required=True)
    username = forms.CharField(max_length=models.MAX_LENGTH_SHORT_FIELD, required=True)
    password = forms.CharField(max_length=models.MAX_LENGTH_SHORT_FIELD, widget=forms.PasswordInput, strip=False,
                               required=True)
    first_name = forms.CharField(max_length=models.MAX_LENGTH_SHORT_FIELD, required=False)
    last_name = forms.CharField(max_length=models.MAX_LENGTH_SHORT_FIELD, required=False)
    phone = forms.CharField(max_length=models.MAX_LENGTH_SHORT_FIELD, required=False)
    address = forms.CharField(max_length=models.MAX_LENGTH_MEDIUM_FIELD, required=False)
    company = forms.CharField(max_length=models.MAX_LENGTH_SHORT_FIELD, required=False)

    class Meta:
        model = User
        model._meta.get_field('username')._unique = False
        fields = ('email', 'username', 'password', 'first_name', 'last_name', 'phone', 'address', 'company',)

    def clean(self):
        cleaned_data = super(RegisterForm, self).clean()
        try:
            password = cleaned_data.get('password')
            password_validation.validate_password(password, self.instance)
        except forms.ValidationError as error:
            self.add_error('password', error)


class UpdateProfileForm(ModelForm):
    email = forms.EmailField(max_length=models.MAX_LENGTH_SHORT_FIELD, required=True)
    username = forms.CharField(max_length=models.MAX_LENGTH_SHORT_FIELD, required=True)
    first_name = forms.CharField(max_length=models.MAX_LENGTH_SHORT_FIELD, required=False)
    last_name = forms.CharField(max_length=models.MAX_LENGTH_SHORT_FIELD, required=False)
    phone = forms.CharField(max_length=models.MAX_LENGTH_SHORT_FIELD, required=False)
    address = forms.CharField(max_length=models.MAX_LENGTH_MEDIUM_FIELD, required=False)
    company = forms.CharField(max_length=models.MAX_LENGTH_SHORT_FIELD, required=False)

    class Meta:
        model = User
        model._meta.get_field('username')._unique = False
        fields = ('email', 'username', 'first_name', 'last_name', 'phone', 'address', 'company',)


class ChangePasswordForm(ModelForm):
    old_password = forms.CharField(max_length=models.MAX_LENGTH_SHORT_FIELD, widget=forms.PasswordInput, strip=False,
                                   required=True)
    new_password = forms.CharField(max_length=models.MAX_LENGTH_SHORT_FIELD, widget=forms.PasswordInput, strip=False,
                                   required=True)
    confirm_password = forms.CharField(max_length=models.MAX_LENGTH_SHORT_FIELD, widget=forms.PasswordInput,
                                       strip=False,
                                       required=True)

    class Meta:
        model = User
        fields = ('old_password', 'new_password', 'confirm_password')

    def clean(self):
        cleaned_data = super(ChangePasswordForm, self).clean()
        new_password = cleaned_data.get("new_password")
        confirm_password = cleaned_data.get("confirm_password")

        if new_password != confirm_password:
            raise forms.ValidationError({'confirm_password': [
                "New password and confirm password does not match", ]
            })
        else:
            try:
                password_validation.validate_password(new_password, self.instance)
            except forms.ValidationError as error:
                self.add_error('new_password', error)


# application, provider, channel
class AppForm(ModelForm):
    name = forms.CharField(max_length=67, required=True)
    api_key = forms.CharField(max_length=127, required=True)
    callback_uris = forms.CharField(max_length=2047)
    allowed_ips = forms.CharField(max_length=127, required=True)
    description = forms.CharField(widget=forms.Textarea, required=False)

    class Meta:
        model = App
        fields = ('name', 'api_key', 'description',)

    # def clean(self):
    #     cleaned_data = super(AppForm, self).clean()
    #     callback_uri = cleaned_data.get('callback_uri')
    #     if not utils.validateURL(callback_uri):
    #         raise forms.ValidationError({'callback_uri': [
    #             "Enter a valid URL.", ]
    #         })


# Custom ModelChoiceField Label
class ProviderModelChoiceField(ModelChoiceField):
    def label_from_instance(self, obj):
        return obj.id


class ChannelForm(ModelForm):
    CHOICES = (('label1', 'value1'), ('label2', 'value2'), ('label3', 'value3'))
    provider = ProviderModelChoiceField(Provider.objects.all(), to_field_name='id', required=True, empty_label=None)
    client_id = forms.CharField(max_length=255, required=True)
    client_secret = forms.CharField(max_length=255, required=True)
    # permission = forms.CharField(max_length=1023, required=True)
    app_id = forms.IntegerField(required=True)

    class Meta:
        model = Channel
        fields = ('provider', 'client_id', 'client_secret',)
