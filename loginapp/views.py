from django.shortcuts import render, redirect, render_to_response, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.template import loader
from django.contrib.auth import login as signin, logout as signout, authenticate, update_session_auth_hash
from django.contrib import messages
from django import forms

from loginapp.forms import RegisterForm, UpdateProfileForm, ChangePasswordForm, AppForm, ChannelForm
from loginapp.backends import AuthenticationWithEmailBackend
from loginapp.utils import generateApiKey
from loginapp.models import App, Provider, Channel
import string
import random
import datetime


# Create your views here.

def index(request):
    return render(request, 'loginapp/index.html')


def login(request):
    if request.user.is_authenticated:
        return redirect('index')
    message = ''
    if request.method == 'POST':
        email = request.POST['email']
        password = request.POST['password']
        user = AuthenticationWithEmailBackend.authenticate(None, username=email, password=password)
        if user is not None:
            request.session.set_expiry(86400)
            signin(request, user)
            return redirect('index')
        else:
            message = 'Email or Password Incorrect !'

    return render(request, 'loginapp/page-login.html', {'message': message})


@login_required
def logout(request):
    signout(request)
    return redirect('index')


def register(request):
    if request.user.is_authenticated:
        return redirect('index')
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            password = form.cleaned_data.get('password')
            email = form.cleaned_data.get('email')
            user.set_password(password)
            user.email = email
            user.save()
            return redirect('login')
        else:
            print(form.errors)
    else:
        form = RegisterForm()

    return render(request, 'loginapp/page-register.html', {'form': form})


@login_required
def dashboard(request):
    apps = App.objects.all().filter(owner_id=request.user.id)
    print(len(apps))
    return render(request, 'loginapp/dashboard.html', {'apps': apps})


@login_required
def profile(request):
    if request.method == 'POST':
        form = UpdateProfileForm(request.POST, instance=request.user)
        if form.is_valid():
            user = form.save(commit=False)
            email = form.cleaned_data.get('email')
            user.email = email
            user.save()
            messages.success(request, 'Your profile was successfully updated!')
            return redirect('profile')
        else:
            print(form.errors)
    else:
        form = UpdateProfileForm()

    return render(request, 'loginapp/profile.html', {'form': form})


@login_required
def change_password_profile(request):
    if request.method == 'POST':
        form = ChangePasswordForm(request.POST, instance=request.user)
        if form.is_valid():
            old_password = request.POST['old_password']
            if request.user.check_password(old_password):
                user = form.save(commit=False)
                password = form.cleaned_data.get('new_password')
                user.set_password(password)
                user.save()
                update_session_auth_hash(request, user)
                messages.success(request, 'Password Updated!')
                return redirect('change_password')
            else:
                messages.error(request, 'Old Password Incorrect!')
        else:
            print(form.errors)

    else:
        form = ChangePasswordForm()

    return render(request, 'loginapp/changepass.html', {'form': form})


# application, provider, channel
# Application
@login_required
def add_app(request):
    if request.method == 'POST':
        form = AppForm(request.POST)
        if form.is_valid():
            app = form.save(commit=False)
            app.owner_id = request.user
            app.save()
            return redirect('dashboard')
        else:
            print(form.errors)

    else:
        form = AppForm()
    return render(request, 'loginapp/add_app.html', {'form': form})


@login_required
def app_detail(request, app_id):
    if request.method == 'POST':
        app = get_object_or_404(App, pk=app_id)
        form = AppForm(request.POST, instance=app)
        if form.is_valid():
            app_update = form.save(commit=False)
            app_update.modified_at = datetime.datetime.now();
            app_update.save()
            messages.success(request, "Application was successfully updated!")
            return redirect('app_detail', app_id=app_id)

    app = get_object_or_404(App, pk=app_id)
    apps = App.objects.filter(owner_id=request.user.id)
    channels = Channel.objects.filter(app_id=app_id)
    providers = Provider.objects.all()

    form = AppForm()
    channel_form = ChannelForm()
    channel_form.fields['app_id'].widget = forms.HiddenInput()

    return render(request, 'loginapp/app_detail.html',
                  {'app': app, 'apps': apps, 'channels': channels, 'providers': providers, 'form': form,
                   'channel_form': channel_form})


@login_required
def add_channel(request):
    if request.method == 'POST':
        form = ChannelForm(request.POST)
        if form.is_valid():
            channel = form.save(commit=False)
            permissions = request.POST.getlist('permission')
            app_id = request.POST['app_id']
            if len(permissions) == 0:
                messages.error(request, "Add channel failed: permission is required!")
                return redirect('app_detail', app_id=app_id)
            else:
                perm_value = ''
                for perm in permissions:
                    perm_value += perm + ","
                perm_value = perm_value[:-1]
                channel.permissions = perm_value
            if app_id is None:
                messages.error(request, "Add channel failed: App ID is required!")
                return redirect('dashboard')
            else:
                channel.app_id = App.objects.get(pk=app_id)
            messages.success(request, "Channel was successfully created!")
            channel.save()
            return redirect('app_detail', app_id=app_id)
        else:
            print(form.errors)

    return redirect('index')


@login_required
def delete_channel(request, app_id, channel_id):
    channel = get_object_or_404(Channel, pk=channel_id)
    channel.delete()
    messages.success(request, "Channel was deleted!")
    return redirect('app_detail', app_id=app_id)


@login_required
def get_api_key(request):
    try:
        return HttpResponse(generateApiKey(
            ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(10)).encode('utf-8')),
            content_type='text/plain')
    except Exception as e:
        return HttpResponse(e, status=404)


# Channel
# @login_required
# def add_channel(request):

# link not found
def error404(request):
    template = loader.get_template('loginapp/page-404.html')
    return HttpResponse(template.render())
