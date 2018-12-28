from django.shortcuts import render, redirect, HttpResponse, get_object_or_404
from django.contrib import messages
from django.core.serializers.json import DjangoJSONEncoder
from django.contrib.auth import update_session_auth_hash

from loginapp.models import App, User, AdminSetting
from loginapp.forms import RegisterForm
from loginapp.views import push_messages_error
from loginapp.reports import get_list_admin_users, get_list_apps, get_register_report
import json


def admin_list_users(request):
    if not request.user.is_superuser:
        redirect('dashboard')
    column_dic = {
        '1': 'admins.username',
        '2': 'admins.email',
        '3': 'number_apps',
        '4': 'last_login',
        '5': 'admins.level',
        '6': 'admins.deleted'
    }

    if request.GET.get('flag_loading'):
        page_length = int(request.GET.get('length', 25))
        start_page = int(request.GET.get('start', 0))
        search_value = request.GET.get('search[value]')

        order_col = column_dic[request.GET.get('order[0][column]', '0')]
        order_dir = request.GET.get('order[0][dir]', 'asc')
        order_by = order_col + ' ' + order_dir

        records_total, profiles = get_list_admin_users(page_length=page_length,
                                                       start_page=start_page, order_by=order_by,
                                                       search_value=search_value)

        records_filtered = len(profiles)
        data = []
        for id, profile in enumerate(profiles):
            row_data = [id + 1,
                        profile['username'],
                        profile['email'],
                        profile['last_login'].strftime('%Y-%m-%d %H:%M:%S') if profile['last_login'] else 'Never',
                        profile['total_apps'],
                        profile['level'],
                        profile['deleted'],
                        str(profile['user_id']) + "|" + str(profile['level'])]
            data.append(row_data)
        json_data_table = {'recordsTotal': records_total, 'recordsFiltered': records_filtered, 'data': data}
        return HttpResponse(json.dumps(json_data_table, cls=DjangoJSONEncoder), content_type='application/json')
    else:
        apps = App.get_all_app(request.user)
        form = RegisterForm()
        return render(request, 'loginapp/admin_user_list.html', {'form': form, 'apps': apps})


def admin_add_user(request):
    if not request.user.is_superuser:
        return redirect('dashboard')
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            password = form.cleaned_data.get('password')
            email = form.cleaned_data.get('email')
            user.set_password(password)
            user.email = email
            user.save()
            messages.success(request, "User was successfully created!")
            return redirect('admin_users')
        else:
            push_messages_error(request, form)
            print(form.errors)

    return redirect('admin_users')


def admin_delete_user(request, user_id):
    if not request.user.is_superuser:
        return redirect('dashboard')
    if request.method == 'POST':
        user = get_object_or_404(User, pk=user_id)
        user.deleted = 1
        user.save()
        App.objects.filter(owner=user_id).update(deleted=1)
        messages.success(request, 'User was deleted!')
        return redirect('admin_users')
    else:
        messages.error(request, 'Delete failed User!')
        return redirect('admin_users')


def admin_update_user(request):
    if not request.user.is_superuser:
        return redirect('dashboard')

    if request.method == 'POST':
        if not request.POST.get('user_id', ''):
            messages.error(request, 'Update failed User: user id is required!')
            return redirect('admin_users')
        user_id = request.POST['user_id']
        user = get_object_or_404(User, pk=user_id)
        if request.POST.get('email', ''):
            user.email = request.POST['email']
        if request.POST.get('username', ''):
            user.username = request.POST['username']
        if request.POST.get('password', ''):
            user.set_password(request.POST['password'])
            update_session_auth_hash(request, user)
        if request.POST.get('level', ''):
            user.level = request.POST['level']
        user.save()

        messages.success(request, "User was successfully updated!")
    return redirect('admin_users')


def admin_list_apps(request):
    if not request.user.is_superuser:
        redirect('dashboard')
    column_dic = {
        '1': 'a.id',
        '2': 'a.name',
        '3': 'o.username',
        '4': 'total_user',
        '5': 'a.created_at',
        '6': 'a.modified_at',
        '7': 'a.deleted'
    }

    if request.GET.get('flag_loading'):
        page_length = int(request.GET.get('length', 25))
        start_page = int(request.GET.get('start', 0))
        search_value = request.GET.get('search[value]')

        order_col = column_dic[request.GET.get('order[0][column]', '1')]
        order_dir = request.GET.get('order[0][dir]', 'asc')
        order_by = order_col + ' ' + order_dir

        records_total, profiles = get_list_apps(page_length=page_length, start_page=start_page, order_by=order_by,
                                                search_value=search_value)

        records_filtered = len(profiles)
        data = []
        for id, profile in enumerate(profiles):
            row_data = [id + 1,
                        profile['id'],
                        profile['name'],
                        profile['owner'],
                        profile['total_user'],
                        profile['created_at'].strftime('%Y-%m-%d %H:%M:%S'),
                        profile['modified_at'].strftime('%Y-%m-%d %H:%M:%S'),
                        profile['deleted']]
            data.append(row_data)
        json_data_table = {'recordsTotal': records_total, 'recordsFiltered': records_filtered, 'data': data}
        return HttpResponse(json.dumps(json_data_table, cls=DjangoJSONEncoder), content_type='application/json')
    else:
        apps = App.get_all_app(request.user)
        return render(request, 'loginapp/admin_app_list.html', {'apps': apps})


def admin_report_register(request):
    if not request.user.is_superuser:
        redirect('dashboard')
    column_dic = {
        '1': 'a.id',
        '2': 'a.name',
        '3': 'o.username',
        '4': 'created_at',
        '5': 'modified_at',
        '6': 'total',
        '7': 'authorized',
        '8': 'register_done',
        '9': 'a.deleted',
    }

    if request.GET.get('flag_loading'):
        page_length = int(request.GET.get('length', 25))
        start_page = int(request.GET.get('start', 0))
        search_value = request.GET.get('search[value]')

        order_col = column_dic[request.GET.get('order[0][column]', '1')]
        order_dir = request.GET.get('order[0][dir]', 'asc')
        order_by = order_col + ' ' + order_dir

        records_total, profiles = get_register_report(page_length=page_length, start_page=start_page, order_by=order_by,
                                                      search_value=search_value)

        records_filtered = len(profiles)
        data = []
        for id, profile in enumerate(profiles):
            row_data = [id + 1,
                        profile['id'],
                        profile['name'],
                        profile['username'],
                        profile['created_at'],
                        profile['modified_at'],
                        profile['total'],
                        profile['authorized'],
                        profile['register_done'],
                        profile['deleted']]
            data.append(row_data)
        json_data_table = {'recordsTotal': records_total, 'recordsFiltered': records_filtered, 'data': data}
        return HttpResponse(json.dumps(json_data_table, cls=DjangoJSONEncoder), content_type='application/json')
    else:
        apps = App.get_all_app(request.user)
        return render(request, 'loginapp/admin_register_report.html', {'apps': apps})


def admin_setting(request):
    if not request.user.is_superuser:
        redirect('dashboard')
    if request.method == 'POST':
        for k in request.POST:
            if k == 'csrfmiddlewaretoken':
                continue
            setting, created = AdminSetting.objects.get_or_create(name=k)
            setting.name = k
            setting.value = request.POST[k]
            setting.save()
        return redirect('admin_setting')
    settings = AdminSetting.objects.all()
    settings_map = {}
    for setting in settings:
        settings_map[setting.name] = setting.value
    return render(request, 'loginapp/admin_setting.html', {'settings': settings_map})
