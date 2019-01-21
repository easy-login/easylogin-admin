import datetime
import json
import requests
import collections
import time

from django import forms
from django.contrib import messages
from django.contrib.auth import login as signin, logout as signout, update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.core.serializers.json import DjangoJSONEncoder
from django.db import IntegrityError
from django.http import HttpResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.template import loader
from django.conf import settings

from loginapp.backends import AuthenticationWithEmailBackend
from loginapp.forms import RegisterForm, UpdateProfileForm, ChangePasswordForm, AppForm, ChannelForm
from loginapp.models import App, Provider, Channel, User
from loginapp.reports import get_auth_report_per_provider, get_total_provider_report, \
    get_total_auth_report, get_user_report, get_social_users
from loginapp.utils import generateApiKey, getChartColor


# Create your views here.
def index(request):
    return render(request, 'loginapp/index.html')


def login(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
    if request.method == 'POST':
        email = request.POST['email']
        password = request.POST['password']
        user = AuthenticationWithEmailBackend.authenticate(username=email, password=password)
        if user is not None:
            request.session.set_expiry(86400)
            request.session['last_auth'] = time.time()
            signin(request, user)
            next_redirect = request.POST.get('next') if request.POST.get('next') else 'dashboard'
            return redirect(next_redirect)
        else:
            messages.error(request, 'Email or Password Incorrect !')

    return render(request, 'loginapp/page-login.html')


@login_required
def logout(request):
    del request.session['last_auth']
    request.session.modified = True
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
def list_apps(request):
    order_by = request.GET.get('order_by') if request.GET.get('order_by') else '-modified_at'
    user_id = int(request.GET.get('user_id')) if request.GET.get('user_id') else -1

    apps1 = App.get_all_app(user=request.user, order_by=order_by, owner_id=user_id)
    if request.GET.get('search'):
        apps1 = apps1.filter(name__contains=request.GET.get('search'))
    apps = App.get_all_app(user=request.user)
    users = User.get_all_user(user=request.user)
    return render(request, 'loginapp/app_list.html', {'apps1': apps1, 'apps': apps, 'users': users})


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
            options = request.POST.getlist('option')

            if len(allowed_ips) > 0:
                app.set_allowed_ips(allowed_ips)
            if len(callback_uris) == 0:
                messages.error(request, 'Add failed app: callback uris is required!')
            else:
                app.set_options(options)
                app.set_callback_uris(callback_uris)
                app.owner = request.user
                app.save()
                messages.success(request, 'App was successfully created!')
                return redirect('dashboard')
        else:
            push_messages_error(request, form)
            print(form.errors)

    else:
        form = AppForm()
    apps = App.get_all_app(user=request.user)
    return render(request, 'loginapp/app_add.html', {'apps': apps, 'form': form})


@login_required
def app_detail(request, app_id):
    app = App.get_app_by_user(app_id=app_id, user=request.user)
    if request.method == 'POST':
        form = AppForm(request.POST, instance=app)
        if form.is_valid():
            app_update = form.save(commit=False)
            app_update.update_modified_at()

            callback_uris = request.POST.getlist('callback_uris')
            allowed_ips = request.POST.getlist('allowed_ips')
            options = request.POST.getlist('option')

            if len(allowed_ips) > 0:
                app_update.set_allowed_ips(allowed_ips)
            if len(callback_uris) == 0:
                messages.error(request, 'Update failed app: callback uris is required!')
            else:
                app_update.set_options(options)
                app_update.set_callback_uris(callback_uris)
                app_update.save()
                messages.success(request, 'Application was successfully updated!')
                return redirect('app_detail', app_id=app_id)
        else:
            push_messages_error(request, form)

    form = AppForm()
    apps = App.get_all_app(user=request.user)
    return render(request, 'loginapp/app_detail.html',
                  {'app': app, 'apps': apps, 'form': form, })


@login_required
def delete_app(request, app_id):
    if request.method == 'POST':
        app = App.get_app_by_user(app_id=app_id, user=request.user)
        app.deleted = 1
        app.save()
        messages.success(request, 'App was deleted!')
        return redirect('dashboard')
    else:
        messages.error(request, 'Delete failed APP!')
        return redirect('app_detail', app_id=app_id)


@login_required
def user_report(request, app_id):
    app = App.get_app_by_user(app_id=app_id, user=request.user)
    column_dic = {
        '1': 'user_pk',
        '2': 'social_id',
        '3': 'last_login',
        '4': 'login_total'
    }

    if request.GET.get('flag_loading'):
        page_length = int(request.GET.get('length', 25))
        start_row = int(request.GET.get('start', 0))
        search_value = request.GET.get('search[value]')

        order_col = column_dic[request.GET.get('order[0][column]', '1')]
        order_dir = request.GET.get('order[0][dir]', 'asc')
        order_by = order_col + ' ' + order_dir

        records_total, profiles = get_user_report(app_id=app_id, search_value=search_value,
                                                  page_length=page_length, start_row=start_row,
                                                  order_by=order_by)
        records_filtered = records_total
        data = []
        providers = Provider.provider_names()
        for id, profile in enumerate(profiles):
            row_data = [id + 1,
                        profile['user_pk'],
                        str(profile['social_id']) + '|' + str(profile['prohibited']) + '|' + str(app_id),
                        profile['last_login'].strftime('%Y-%m-%d %H:%M:%S'),
                        profile['login_total'], ]
            linked_providers = profile['linked_providers']
            for provider in providers:
                if provider in linked_providers:
                    row_data.append(1)
                else:
                    row_data.append(0)
            row_data.append(str(app_id) + '|' + str(profile['social_id']) + '|' + str(profile['prohibited']))
            data.append(row_data)
        json_data_table = {'recordsTotal': records_total, 'recordsFiltered': records_filtered, 'data': data}
        return HttpResponse(json.dumps(json_data_table, cls=DjangoJSONEncoder), content_type='application/json')
    else:
        apps = App.get_all_app(user=request.user)
        provider_names = Provider.provider_names()
        return render(request, 'loginapp/statistic_login.html',
                      {'apps': apps, 'app': app, 'provider_names': provider_names})


@login_required
def list_social_users(request, app_id, social_id):
    app = App.get_app_by_user(app_id=app_id, user=request.user)
    last_auth = int(request.session.get('last_auth', 0))
    if time.time() - last_auth > settings.TIME_AUTH_SECONDS:
        return render(request, 'loginapp/page-auth.html',
                      {'next_url': '/apps/' + str(app_id) + '/users/' + str(social_id) + '/'})
    data = {}
    profiles = get_social_users(social_id)
    for profile in profiles:
        if profile['provider'] != 'twitter' and profile['provider'] != 'google':
            data[profile['provider']] = collections.OrderedDict(sorted(json.loads(profile['attrs']).items()))
    apps = App.get_all_app(user=request.user)
    return render(request, 'loginapp/social_user_detail.html', {'apps': apps, 'profiles': data})


@login_required
def re_auth(request):
    if request.method == 'POST':
        email = request.POST['email']
        password = request.POST['password']
        user = AuthenticationWithEmailBackend.authenticate(username=email, password=password)
        if user is not None:
            request.session['last_auth'] = time.time()
        else:
            messages.error(request, 'Email or Password Incorrect !')
        next_redirect = request.POST.get('next') if request.POST.get('next') else 'dashboard'
        return redirect(next_redirect)
    return redirect('dashboard')


@login_required
def password_confirm(request):
    body = json.loads(request.body)
    if request.method == 'POST' and 'password' in body:
        user = AuthenticationWithEmailBackend.authenticate(username=request.user.email,
                                                           password=body['password'])
        if user is not None:
            return HttpResponse(json.dumps({'authenticate_ok': True}), content_type='application/json')
    return HttpResponse(json.dumps({'authenticate_ok': False}), content_type='application/json')


@login_required
def delete_user_social(request, app_id):
    app = App.get_app_by_user(app_id=app_id, user=request.user)
    api_key = app.api_key
    if request.method == 'POST':
        App.get_app_by_user(app_id, request.user)
        social_id = request.POST.get('social_id', '')

        response_user = requests.delete('https://api.easy-login.jp/' + str(app_id) + '/users',
                                        json={'social_id': social_id}, verify=False,
                                        headers={'X-Api-Key': api_key})
        if response_user.status_code != 200:
            return HttpResponse(
                json.dumps({'status': 'failed', 'message': 'Delete failed social user!'}, cls=DjangoJSONEncoder),
                content_type='application/json')
        return HttpResponse(
            json.dumps({'status': 'success', 'message': 'Delete success social user!'}, cls=DjangoJSONEncoder),
            content_type='application/json')
    return HttpResponse(
        json.dumps({'status': 'failed', 'message': 'Delete failed social user!'}, cls=DjangoJSONEncoder),
        content_type='application/json')


@login_required
def delete_user_social_info(request, app_id):
    app = App.get_app_by_user(app_id=app_id, user=request.user)
    api_key = app.api_key
    if request.method == 'POST':
        App.get_app_by_user(app_id, request.user)
        social_id = request.POST.get('social_id', '')

        response_info = requests.put('https://api.easy-login.jp/' + str(app_id) + '/users/delete_info',
                                     json={'social_id': social_id}, verify=False,
                                     headers={'X-Api-Key': api_key})
        if response_info.status_code != 200:
            return HttpResponse(
                json.dumps({'status': 'failed', 'message': 'Delete failed social user info!'}, cls=DjangoJSONEncoder),
                content_type='application/json')
        return HttpResponse(
            json.dumps({'status': 'success', 'message': 'Delete success social user info!'}, cls=DjangoJSONEncoder),
            content_type='application/json')
    return HttpResponse(
        json.dumps({'status': 'failed', 'message': 'Delete failed social user info!'}, cls=DjangoJSONEncoder),
        content_type='application/json')


@login_required
def app_report(request, app_id):
    app = App.get_app_by_user(app_id=app_id, user=request.user)

    if request.GET.get('chart_loading'):
        auth_state = request.GET.get('auth_state', '1')
        provider = request.GET.get('provider', 'all')
        startDate = request.GET.get('startDate', datetime.datetime
                                    .strftime(datetime.datetime.today() - datetime.timedelta(days=7), '%Y-%m-%d'))
        endDate = request.GET.get('endDate', datetime.datetime.strftime(datetime.datetime.today(), '%Y-%m-%d'))

        labels, dataChart = get_auth_report_per_provider(app_id=app_id, auth_state=int(auth_state),
                                                         from_dt=startDate, to_dt=endDate)
        datasets = []
        maxy = 0
        check_zero = True
        labels = sorted(labels)
        providerNames = ['total']
        providerNames.extend(Provider.provider_names())

        if provider != 'all':
            providerNames = [provider]
            dataChart = {provider: dataChart.get(provider)}
        for key in providerNames:
            datasetPoint = {'label': key.capitalize(),
                            'fill': False,
                            'borderColor': getChartColor(key),
                            'backgroundColor': getChartColor(key),
                            }
            dataPoint = []
            for key1 in labels:
                value1 = dataChart.get(key).get(key1)
                if value1 > 0:
                    check_zero = False
                if value1 > maxy:
                    maxy = value1
                dataPoint.append(value1)
            datasets.append(datasetPoint)
            datasetPoint.update({'data': dataPoint})
        if check_zero:
            maxy = 999
        dataChartJson = {'maxy': maxy, 'data': {'labels': labels, 'datasets': datasets}}

        return HttpResponse(json.dumps(dataChartJson), content_type='application/json')
    else:
        total_data_auth = get_total_auth_report(app_id=app_id)
        total_data_provider = get_total_provider_report(app_id=app_id)
        provider_names = Provider.provider_names()
        apps = App.get_all_app(user=request.user)

        return render(request, 'loginapp/report_app.html', {
            'app': app, 'apps': apps,
            'provider_names': provider_names,
            'total_data_auth': total_data_auth,
            'total_data_provider': total_data_provider
        })


@login_required
def list_channels(request, app_id):
    app = App.get_app_by_user(app_id=app_id, user=request.user)
    channels = Channel.objects.filter(app=app_id).order_by('-created_at')
    apps = App.get_all_app(user=request.user)
    providers = Provider.objects.all()
    channel_form = ChannelForm()
    channel_form.fields['app_id'].widget = forms.HiddenInput()

    return render(request, 'loginapp/channel_list.html',
                  {'app': app, 'apps': apps, 'providers': providers, 'channels': channels,
                   'channel_form': channel_form})


@login_required
def add_channel(request):
    if request.method == 'POST':
        form = ChannelForm(request.POST)
        if form.is_valid():
            channel = form.save(commit=False)
            provider_id = request.POST.get('api_version')
            if provider_id is None:
                messages.error(request, 'Add channel failed: API version is required!')
                return redirect('dashboard')
            provider = Provider.objects.filter(pk=provider_id).first()
            provider_name = request.POST.get('provider')
            api_version = provider.version
            required_permission = provider.required_permissions
            field_permission = request.POST.getlist('required_field')
            required_fields = ''
            permissions = set()
            for item in field_permission:
                item_split = item.split(':')
                required_fields += item_split[0] + '|'
                if item_split[1]:
                    permissions.add(item_split[1])
            required_fields = required_fields[:-1]
            permissions = permissions.union(set(required_permission.split('|')))
            options = ''
            options_map = provider.options_as_restrict_map()
            for item in request.POST.getlist('option'):
                if item in options_map:
                    if request.user.level in options_map[item]:
                        options += item + '|'
                else:
                    options += item + '|'
            options = options[:-1]
            channel.provider = provider_name
            channel.api_version = api_version
            channel.permissions = '|'.join(permissions)
            channel.required_fields = required_fields
            channel.options = options

            app_id = request.POST['app_id']
            if app_id is None:
                messages.error(request, 'Add channel failed: App ID is required!')
                return redirect('dashboard')
            else:
                channel.app = App.get_app_by_user(app_id=app_id, user=request.user)

            app = App.get_app_by_user(app_id=app_id, user=request.user)
            # try to catch exception unique but it catch more
            try:
                channel.save()
                app.update_modified_at()
                app.save()
                messages.success(request, 'Channel was successfully created!')
            except IntegrityError as error:
                messages.error(request, 'Channel with ' + channel.provider + ' provider already exists!')

            return redirect('channel_list', app_id=app_id)
        else:
            push_messages_error(request, form)
            print(form.errors)

    return redirect('dashboard')


@login_required
def channel_detail(request, app_id, channel_id):
    app = App.get_app_by_user(app_id=app_id, user=request.user)
    channel = get_object_or_404(Channel, pk=channel_id, app=app_id)
    if request.method == 'POST':
        form = ChannelForm(request.POST, instance=channel)
        if form.is_valid():
            channel_update = form.save(commit=False)
            channel_update.modified_at = datetime.datetime.now()

            provider = request.POST.get('api_version')
            if provider is None:
                messages.error(request, 'Add channel failed: API version is required!')
                return redirect('dashboard')
            provider = Provider.objects.filter(pk=provider).first()
            provider_name = request.POST.get('provider')
            api_version = provider.version
            required_permission = provider.required_permissions
            field_permission = request.POST.getlist('required_field')
            required_fields = ''
            permissions = set()
            for item in field_permission:
                item_split = item.split(':')
                required_fields += item_split[0] + '|'
                if item_split[1]:
                    permissions.add(item_split[1])
            required_fields = required_fields[:-1]
            permissions = permissions.union(set(required_permission.split('|')))
            options = ''
            options_map = provider.options_as_restrict_map()
            print(request.POST.getlist('option'))
            for item in request.POST.getlist('option'):
                if item in options_map:
                    if request.user.level in options_map[item]:
                        options += item + '|'
                else:
                    options += item + '|'
            options = options[:-1]
            channel_update.provider = provider_name
            channel_update.api_version = api_version
            channel_update.permissions = '|'.join(permissions)
            channel_update.required_fields = required_fields
            channel_update.options = options

            channel.app = app

            # try to catch exception unique but it catch more
            try:
                channel_update.save()
                app.update_modified_at()
                app.save()
                messages.success(request, 'Channel was successfully updated!')
            except IntegrityError as error:
                messages.error(request, 'Channel with ' + channel.provider + ' provider already exists!')

            return redirect('channel_detail', app_id=app_id, channel_id=channel_id)
        else:
            push_messages_error(request, form)
            print(form.errors)

    channels = Channel.objects.filter(app=app_id)
    apps = App.get_all_app(user=request.user)
    providers = Provider.objects.all()
    provider_name_list = list(set(Provider.objects.values_list('name', flat=True)))
    provider = Provider.objects.filter(name=channel.provider, version=channel.api_version).first()
    form = ChannelForm()
    form.fields['app_id'].widget = forms.HiddenInput()

    return render(request, 'loginapp/channel_detail.html',
                  {'app': app, 'apps': apps, 'channel': channel, 'channels': channels, 'providers': providers,
                   'provider_names': provider_name_list, 'provider_id': provider.id, 'form': form})


@login_required
def delete_channel(request, app_id, channel_id):
    if request.method == 'POST':
        app = App.get_app_by_user(app_id=app_id, user=request.user)
        channel = get_object_or_404(Channel, pk=channel_id, app=app_id)
        channel.delete()
        app.update_modified_at()
        messages.success(request, 'Channel was deleted!')
        return redirect('channel_list', app_id=app_id)
    else:
        messages.error(request, 'Delete failed Channel!')
        return redirect('channel_list', app_id=app_id)


@login_required
def get_api_key(request):
    try:
        return HttpResponse(generateApiKey(nbytes=48), content_type='text/plain')
    except Exception as e:
        return HttpResponse(e, status=404)


# pass messages error
def push_messages_error(request, form):
    for key, val in form.errors.as_data().items():
        key = key.replace('_', ' ').capitalize()
        for validError in val:
            errors = validError.messages
            for error in errors:
                messages.error(request, 'Update failed! ' + key + ': ' + error)


# link not found
def error404(request):
    template = loader.get_template('loginapp/page-404.html')
    return HttpResponse(template.render())
