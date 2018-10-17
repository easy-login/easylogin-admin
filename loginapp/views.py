import datetime
import json

from django import forms
from django.contrib import messages
from django.contrib.auth import login as signin, logout as signout, update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.core.serializers.json import DjangoJSONEncoder
from django.db import IntegrityError
from django.http import HttpResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.template import loader

from loginapp.backends import AuthenticationWithEmailBackend
from loginapp.forms import RegisterForm, UpdateProfileForm, ChangePasswordForm, AppForm, ChannelForm
from loginapp.models import App, Provider, Channel
from loginapp.reports import get_auth_report_per_provider, get_total_provider_report, \
    get_total_auth_report, get_user_report
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
def list_apps(request):
    order_by = request.GET.get('order_by') if request.GET.get('order_by') else '-modified_at'
    apps1 = App.objects.filter(owner=request.user.id).order_by(order_by)
    if request.GET.get("search"):
        apps1 = apps1.filter(name__contains=request.GET.get("search"))
    apps = App.objects.filter(owner=request.user.id).order_by('name')
    return render(request, 'loginapp/app_list.html', {'apps1': apps1, 'apps': apps})


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
                app.owner = request.user
                app.save()
                messages.success(request, "App was successfully created!")
                return redirect('dashboard')
        else:
            push_messages_error(request, form)
            print(form.errors)

    else:
        form = AppForm()
    apps = App.objects.filter(owner=request.user.id).order_by('name')
    return render(request, 'loginapp/app_add.html', {'apps': apps, 'form': form})


@login_required
def app_detail(request, app_id):
    app = get_object_or_404(App, pk=app_id, owner=request.user.id)
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
    apps = App.objects.filter(owner=request.user.id).order_by('name')
    return render(request, 'loginapp/app_detail.html',
                  {'app': app, 'apps': apps, 'form': form, })


@login_required
def delete_app(request, app_id):
    if request.method == 'POST':
        app = get_object_or_404(App, pk=app_id, owner=request.user.id)
        app.delete()
        messages.success(request, "App was deleted!")
        return redirect('dashboard')
    else:
        messages.error(request, 'Delete failed APP!')
        return redirect('app_detail', app_id=app_id)


@login_required
def user_report(request, app_id):
    app = get_object_or_404(App, pk=app_id, owner=request.user.id)
    column_dic = {
        '1': 'user_id',
        '2': 'social_id',
        '3': 'last_login',
        '4': 'login_total'
    }

    if request.GET.get('flag_loading'):
        page_length = int(request.GET.get('length', 25))
        start_page = int(request.GET.get('start', 0))
        search_value = request.GET.get('search[value]')

        order_col = column_dic[request.GET.get('order[0][column]', '1')]
        order_dir = request.GET.get('order[0][dir]', 'asc')
        order_by = order_col + ' ' + order_dir

        records_total, profiles = get_user_report(app_id=app_id, search_value=search_value,
                                                  page_length=page_length, start_page=start_page,
                                                  order_by=order_by)
        records_filtered = len(profiles)
        data = []
        providers = Provider.provider_names()
        for id, profile in enumerate(profiles):
            row_data = [id + 1,
                        profile['user_id'],
                        str(profile['social_id']),
                        profile['last_login'].strftime('%Y-%m-%d %H:%M:%S'),
                        profile['login_total']]
            linked_providers = profile['linked_providers']
            for provider in providers:
                if provider in linked_providers:
                    row_data.append(1)
                else:
                    row_data.append(0)

            data.append(row_data)
        json_data_table = {'recordsTotal': records_total, 'recordsFiltered': records_filtered, 'data': data}
        return HttpResponse(json.dumps(json_data_table, cls=DjangoJSONEncoder), content_type='application/json')
    else:
        apps = App.objects.filter(owner=request.user.id).order_by('name')
        providers = Provider.objects.order_by('name')
        return render(request, 'loginapp/statistic_login.html', {'apps': apps, 'app': app, 'providers': providers})


@login_required
def app_report(request, app_id):
    app = get_object_or_404(App, pk=app_id, owner=request.user.id)

    if request.GET.get('chart_loading'):
        isLogin = request.GET.get('is_login', '1')
        provider = request.GET.get('provider', 'all')
        startDate = request.GET.get('startDate', datetime.datetime
                                    .strftime(datetime.datetime.today() - datetime.timedelta(days=7), '%Y-%m-%d'))
        endDate = request.GET.get('endDate', datetime.datetime.strftime(datetime.datetime.today(), '%Y-%m-%d'))

        labels, dataChart = get_auth_report_per_provider(app_id=app_id, is_login=int(isLogin),
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
        apps = App.objects.filter(owner=request.user.id).order_by('name')

        return render(request, 'loginapp/report_app.html', {
            'app': app, 'apps': apps,
            'total_data_auth': total_data_auth,
            'total_data_provider': total_data_provider
        })


@login_required
def channel_list(request, app_id):
    app = get_object_or_404(App, pk=app_id, owner=request.user.id)
    channels = Channel.objects.filter(app=app_id).order_by('-created_at')
    apps = App.objects.filter(owner=request.user.id).order_by('name')
    providers = Provider.objects.all()
    channel_form = ChannelForm()
    channel_form.fields['app_id'].widget = forms.HiddenInput()

    return render(request, 'loginapp/channel_list.html',
                  {'app': app, 'apps': apps, 'providers': providers, 'channels': channels,
                   'channel_form': channel_form})


@login_required
def add_channel(request):
    if request.method == 'POST':
        print(request.POST)
        form = ChannelForm(request.POST)
        if form.is_valid():
            channel = form.save(commit=False)
            provider_id = request.POST.get('api_version')
            if provider_id is None:
                messages.error(request, "Add channel failed: API version is required!")
                return redirect('dashboard')
            provider = Provider.objects.filter(pk=provider_id).first()
            provider_name = request.POST.get('provider')
            api_version = provider.version
            required_permission = provider.required_permissions
            field_permission = request.POST.getlist('required_field')
            required_fields = ""
            permissions = ""
            for item in field_permission:
                item_split = item.split('|')
                required_fields += item_split[0] + '|'
                permissions += item_split[1] + '|'
            required_fields = required_fields[:-1]
            permissions += required_permission
            permissions = '|'.join(set(permissions.split('|')))
            options = ""
            for item in request.POST.getlist('option'):
                options += item + "|"
            options = options[:-1]
            channel.provider = provider_name
            channel.api_version = api_version
            channel.permissions = permissions
            channel.required_fields = required_fields
            channel.options = options

            app_id = request.POST['app_id']
            if app_id is None:
                messages.error(request, "Add channel failed: App ID is required!")
                return redirect('dashboard')
            else:
                channel.app = get_object_or_404(App, pk=app_id, owner=request.user.id)

            app = get_object_or_404(App, pk=app_id, owner=request.user.id)

            # try to catch exception unique but it catch more
            try:
                channel.save()
                app.update_modified_at()
                app.save()
                messages.success(request, "Channel was successfully created!")
            except IntegrityError as error:
                messages.error(request, "Channel with " + channel.provider + " provider already exists!")

            return redirect('channel_list', app_id=app_id)
        else:
            push_messages_error(request, form)
            print(form.errors)

    return redirect('dashboard')


@login_required
def channel_detail(request, app_id, channel_id):
    app = get_object_or_404(App, pk=app_id, owner=request.user.id)
    channel = get_object_or_404(Channel, pk=channel_id, app=app_id)
    if request.method == 'POST':
        form = ChannelForm(request.POST, instance=channel)
        if form.is_valid():
            channel_update = form.save(commit=False)
            channel_update.modified_at = datetime.datetime.now()

            provider = request.POST.get('api_version')
            if provider is None:
                messages.error(request, "Add channel failed: API version is required!")
                return redirect('dashboard')
            provider = Provider.objects.filter(pk=provider).first()
            provider_name = request.POST.get('provider')
            api_version = provider.version
            required_permission = provider.required_permissions
            field_permission = request.POST.getlist('required_field')
            required_fields = ""
            permissions = ""
            for item in field_permission:
                item_split = item.split('|')
                required_fields += item_split[0] + '|'
                permissions += item_split[1] + '|'
            required_fields = required_fields[:-1]
            permissions += required_permission
            permissions = '|'.join(set(permissions.split('|')))
            options = ""
            for item in request.POST.getlist('option'):
                options += item + "|"
            options = options[:-1]
            channel_update.provider = provider_name
            channel_update.api_version = api_version
            channel_update.permissions = permissions
            channel_update.required_fields = required_fields
            channel_update.options = options

            channel.app = app

            # try to catch exception unique but it catch more
            try:
                channel_update.save()
                app.update_modified_at()
                app.save()
                messages.success(request, "Channel was successfully updated!")
            except IntegrityError as error:
                print('Add channel error', error)
                messages.error(request, "Channel with " + channel.provider + " provider already exists!")

            return redirect('channel_detail', app_id=app_id, channel_id=channel_id)
        else:
            push_messages_error(request, form)
            print(form.errors)

    channels = Channel.objects.filter(app=app_id)
    apps = App.objects.filter(owner=request.user.id)
    providers = Provider.objects.all()
    provider_name_list = list(set(Provider.objects.values_list('name', flat=True)))
    provider = Provider.objects.filter(name=channel.provider, version=channel.api_version).first()
    form = ChannelForm()
    form.fields['app_id'].widget = forms.HiddenInput()

    return render(request, 'loginapp/channel_detail.html',
                  {"app": app, 'apps': apps, 'channel': channel, 'channels': channels, 'providers': providers,
                   'provider_names': provider_name_list, 'provider_id': provider.id, 'form': form})


@login_required
def delete_channel(request, app_id, channel_id):
    if request.method == 'POST':
        app = get_object_or_404(App, pk=app_id, owner=request.user.id)
        channel = get_object_or_404(Channel, pk=channel_id, app=app_id)
        channel.delete()
        app.update_modified_at()
        messages.success(request, "Channel was deleted!")
        return redirect('channel_list', app_id=app_id)
    else:
        messages.error(request, "Delete failed Channel!")
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
        key = key.replace("_", " ").capitalize()
        for validError in val:
            errors = validError.messages
            for error in errors:
                messages.error(request, "Update failed! " + key + ": " + error)


# link not found
def error404(request):
    template = loader.get_template('loginapp/page-404.html')
    return HttpResponse(template.render())
