from django.forms import ModelForm
from django import forms

from loginapp.models import User
from loginapp import models


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
                "New password and confirm password does not match",]
            })


class PasswordResetEmailForm(forms.Form):
    email = forms.EmailField(max_length=models.MAX_LENGTH_SHORT_FIELD, required=true)


# class LoginForm(forms.Form):
# 	email = forms.EmailField(max_length=models.MAX_LENGTH_SHORT_FIELD, required=True)
# 	password = forms.CharField(max_length=models.MAX_LENGTH_SHORT_FIELD, widget=forms.PasswordInput, strip=False, required=True)

# 	class Meta:
#  		model = User
#  		model._meta.get_field('username')._unique = False
#  		fields = ('email', 'password', )
