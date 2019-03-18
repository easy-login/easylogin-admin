from django.forms import ModelForm
from django.forms import ModelChoiceField
from django import forms
from django.contrib.auth import password_validation
from django.core.validators import RegexValidator

from loginapp.models import User, App, Channel, Provider
from loginapp import models
from loginapp.utils import validate_length, validate_not_special_characters


class RegisterForm(ModelForm):
    email = forms.EmailField(max_length=models.MAX_LENGTH_SHORT_FIELD, required=True)
    username = forms.CharField(max_length=20, min_length=6, required=True, validators=[
        RegexValidator('^[a-zA-Z0-9_-]*$',
                       message='This value seem to invalid. Valid characters: 0-9, a-z, A-Z, -, _')])
    password = forms.CharField(max_length=20, min_length=6, widget=forms.PasswordInput, strip=False,
                               required=True)
    first_name = forms.CharField(max_length=models.MAX_LENGTH_SHORT_FIELD, required=False)
    last_name = forms.CharField(max_length=models.MAX_LENGTH_SHORT_FIELD, required=False)
    phone = forms.CharField(max_length=models.MAX_LENGTH_SHORT_FIELD, required=False)
    address = forms.CharField(max_length=models.MAX_LENGTH_MEDIUM_FIELD, required=False)
    company = forms.CharField(max_length=models.MAX_LENGTH_SHORT_FIELD, required=False)

    class Meta:
        model = User
        model._meta.get_field('username')._unique = False
        fields = ('email', 'username', 'password', 'first_name', 'last_name', 'phone', 'address', 'company', 'level')


class UpdateProfileForm(ModelForm):
    email = forms.EmailField(max_length=models.MAX_LENGTH_SHORT_FIELD, required=False)
    username = forms.CharField(max_length=models.MAX_LENGTH_SHORT_FIELD, required=True)
    first_name = forms.CharField(max_length=models.MAX_LENGTH_SHORT_FIELD, required=False)
    last_name = forms.CharField(max_length=models.MAX_LENGTH_SHORT_FIELD, required=False)
    phone = forms.CharField(max_length=models.MAX_LENGTH_SHORT_FIELD, required=False)
    address = forms.CharField(max_length=models.MAX_LENGTH_MEDIUM_FIELD, required=False)
    company = forms.CharField(max_length=models.MAX_LENGTH_SHORT_FIELD, required=False)

    class Meta:
        model = User
        model._meta.get_field('username')._unique = False
        fields = ('username', 'first_name', 'last_name', 'phone', 'address', 'company',)

    def clean(self):
        cleaned_data = super(UpdateProfileForm, self).clean()
        username = cleaned_data.get('username')
        if not validate_length(6, 20, username):
            self.add_error('username', 'Username length is invalid. It should be between 6 and 20 characters long')
        if not validate_not_special_characters(username):
            self.add_error('username', 'Username seem to invalid. Valid characters: 0-9, a-z, A-Z, -, _')


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
        if not validate_length(6, 20, new_password):
            self.add_error('password', 'Password length is invalid. It should be between 6 and 20 characters long')


# application, provider, channel
class AppForm(ModelForm):
    name = forms.CharField(max_length=20, required=True)
    api_key = forms.CharField(max_length=127, required=True)
    callback_uris = forms.CharField(max_length=2047)
    allowed_ips = forms.CharField(max_length=127, required=False)
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
        return obj.name


class ChannelForm(ModelForm):
    provider = forms.ChoiceField(choices=[], required=True)
    client_id = forms.CharField(max_length=255, required=True)
    client_secret = forms.CharField(max_length=255, required=True)
    # permission = forms.CharField(max_length=1023, required=True)
    app_id = forms.IntegerField(required=True)

    def __init__(self, *args, **kwargs):
        super(ChannelForm, self).__init__(*args, **kwargs)
        self.fields['provider'].choices = Provider.objects.all().values_list('name', 'name').distinct()

    class Meta:
        model = Channel
        fields = ('provider', 'client_id', 'client_secret',)
