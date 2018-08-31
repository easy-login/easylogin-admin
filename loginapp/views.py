from django.shortcuts import render, redirect, render_to_response, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.template import loader
from django.contrib.auth import login as signin, logout as signout, authenticate, update_session_auth_hash
from django.contrib import messages
from django import forms
from django.urls import reverse

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
    if request.method == 'POST':
        email = request.POST['email']
        password = request.POST['password']
        user = AuthenticationWithEmailBackend.authenticate(None, username=email, password=password)
        if user is not None:
            request.session.set_expiry(86400)
            signin(request, user)
            print(request.POST.get('next'))
            next_redirect = request.POST.get('next') if request.POST.get('next') else 'dashboard'
            return redirect(next_redirect)
        else:
            messages.error(request, 'Email or Password Incorrect !')

    return render(request, 'loginapp/page-login.html')


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
    order_by = request.GET.get('order_by') if request.GET.get('order_by') else '-modified_at'
    apps = App.objects.all().filter(owner_id=request.user.id).order_by(order_by)
    if request.GET.get("search"):
        apps = apps.filter(name__contains=request.GET.get("search"))
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
            push_messages_error(request, form)
            print(form.errors)

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

            callback_uris = request.POST.getlist('callback_uris')
            allowed_ips = request.POST.getlist('allowed_ips')
            if len(callback_uris) == 0:
                messages.error(request, "Add failed app: callback uris is required!")
            if len(allowed_ips) != 0:
                app.set_allowed_ips(allowed_ips)
            if len(callback_uris) > 0:
                app.set_callback_uris(callback_uris)
                app.owner_id = request.user
                app.save()
                messages.success(request, "App was successfully created!")
                return redirect('dashboard')
        else:
            push_messages_error(request, form)
            print(form.errors)

    else:
        form = AppForm()
    return render(request, 'loginapp/add_app.html', {'form': form})


@login_required
def app_detail(request, app_id):
    app = get_object_or_404(App, pk=app_id, owner_id=request.user.id)
    if request.method == 'POST':
        form = AppForm(request.POST, instance=app)
        if form.is_valid():
            app_update = form.save(commit=False)
            app_update.update_modified_at()

            callback_uris = request.POST.getlist('callback_uris')
            allowed_ips = request.POST.getlist('allowed_ips')
            if len(callback_uris) == 0:
                messages.error(request, "Add failed app: callback uris is required!")
            if len(allowed_ips) != 0:
                app_update.set_allowed_ips(allowed_ips)
            if len(callback_uris) > 0 and len(allowed_ips) > 0:
                app_update.set_callback_uris(callback_uris)
                app_update.save()
                messages.success(request, "Application was successfully updated!")
                return redirect('app_detail', app_id=app_id)
        else:
            push_messages_error(request, form)

    form = AppForm()
    apps = App.objects.filter(owner_id=request.user.id)
    channels = Channel.objects.filter(app_id=app_id).order_by('-created_at')
    providers = Provider.objects.all()
    channel_form = ChannelForm()
    channel_form.fields['app_id'].widget = forms.HiddenInput()

    return render(request, 'loginapp/app_detail.html',
                  {'app': app, 'apps': apps, 'channels': channels, 'providers': providers, 'form': form,
                   'channel_form': channel_form})


@login_required
def delete_app(request, app_id):
    if request.method == 'POST':
        app = get_object_or_404(App, pk=app_id, owner_id=request.user.id)
        app.delete()
        messages.success(request, "App was deleted!")
        return redirect('dashboard')
    else:
        messages.error(request, 'Delete failed APP!')
        return redirect('app_detail', app_id=app_id)


@login_required
def add_channel(request):
    if request.method == 'POST':
        form = ChannelForm(request.POST)
        if form.is_valid():
            channel = form.save(commit=False)
            permissions = request.POST.getlist('permission')
            app_id = request.POST['app_id']
            if len(permissions) == 0:
                messages.error(request, "Add failed channel: permission is required!")
                return redirect('app_detail', app_id=app_id)
            else:
                channel.set_permissions(permissions)
            if app_id is None:
                messages.error(request, "Add channel failed: App ID is required!")
                return redirect('dashboard')
            else:
                channel.app_id = get_object_or_404(App, pk=app_id, owner_id=request.user.id)
            messages.success(request, "Channel was successfully created!")
            app = get_object_or_404(App, pk=app_id, owner_id=request.user.id)
            app.update_modified_at()
            app.save()
            channel.save()
            return redirect('app_detail', app_id=app_id)
        else:
            push_messages_error(request, form)
            print(form.errors)

    return redirect('dashboard')


@login_required
def channel_detail(request, app_id, channel_id):
    app = get_object_or_404(App, pk=app_id, owner_id=request.user.id)
    channel = get_object_or_404(Channel, pk=channel_id, app_id=app_id)
    if request.method == 'POST':
        form = ChannelForm(request.POST, instance=channel)
        if form.is_valid():
            channel_update = form.save(commit=False)
            channel_update.modified_at = datetime.datetime.now()

            permissions = request.POST.getlist('permission')
            if len(permissions) == 0:
                messages.error(request, "Update failed channel: permission is required!")
                return redirect('channel_detail', app_id=app_id, channel_id=channel_id)
            else:
                channel.set_permissions(permissions)

            channel.app_id = app
            messages.success(request, "Channel was successfully updated!")
            app.update_modified_at()
            app.save()
            channel.save()
            return redirect('channel_detail', app_id=app_id, channel_id=channel_id)
        else:
            push_messages_error(request, form)
            print(form.errors)

    channels = Channel.objects.filter(app_id=app_id)
    providers = Provider.objects.all()
    form = ChannelForm()
    form.fields['app_id'].widget = forms.HiddenInput()

    return render(request, 'loginapp/channel_detail.html',
                  {"app": app, 'channel': channel, 'channels': channels, 'providers': providers, 'form': form})


@login_required
def delete_channel(request, app_id, channel_id):
    if request.method == 'POST':
        app = get_object_or_404(App, pk=app_id, owner_id=request.user.id)
        channel = get_object_or_404(Channel, pk=channel_id, app_id=app_id)
        channel.delete()
        app.update_modified_at()
        messages.success(request, "Channel was deleted!")
        return redirect('app_detail', app_id=app_id)
    else:
        messages.error(request, "Delete failed Channel!")
        return redirect('channel_detail', app_id=app_id, channel_id=channel_id)


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

# pass messages error
def push_messages_error(request, form):
    for key, val in form.errors.as_data().items():
        key = key.replace("_", " ").capitalize()
        for validError in val:
            errors = validError.messages
            for error in errors:
                messages.error(request, "Update failed! " + key + ": " + error)


# link not found
def error404(request):
    template = loader.get_template('loginapp/page-404.html')
    return HttpResponse(template.render())
