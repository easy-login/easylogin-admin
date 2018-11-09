from django.shortcuts import render, redirect, HttpResponse, get_object_or_404
from django.contrib import messages
from django.core.serializers.json import DjangoJSONEncoder

from loginapp.models import App, User
from loginapp.forms import RegisterForm
from loginapp.views import push_messages_error
from loginapp.reports import get_list_user
import json


def admin_list_users(request):
    if not request.user.is_superuser:
        redirect('dashboard')
    column_dic = {
        '1': 'admins.id',
        '2': 'admins.username',
        '3': 'admins.email',
        '4': 'number_apps',
        '5': 'last_login',
        '6': 'admins.is_active'
    }

    if request.GET.get('flag_loading'):
        page_length = int(request.GET.get('length', 25))
        start_page = int(request.GET.get('start', 0))
        search_value = request.GET.get('search[value]')

        order_col = column_dic[request.GET.get('order[0][column]', '1')]
        order_dir = request.GET.get('order[0][dir]', 'asc')
        order_by = order_col + ' ' + order_dir

        records_total, profiles = get_list_user(page_length=page_length, start_page=start_page, order_by=order_by,
                                                search_value=search_value)

        records_filtered = len(profiles)
        data = []
        for id, profile in enumerate(profiles):
            row_data = [id + 1,
                        profile['user_id'],
                        profile['username'],
                        profile['email'],
                        profile['last_login'].strftime('%Y-%m-%d %H:%M:%S') if profile['last_login'] else 'Never',
                        profile['total_apps'],
                        profile['is_active'],
                        profile['user_id']]
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
        messages.success(request, 'User was deleted!')
        return redirect('admin_users')
    else:
        messages.error(request, 'Delete failed User!')
        return redirect('admin_users')


def admin_list_(request):
    if not request.user.is_superuser:
        redirect('dashboard')
    column_dic = {
        '1': 'admins.id',
        '2': 'admins.username',
        '3': 'admins.email',
        '4': 'number_apps',
        '5': 'last_login',
        '6': 'admins.is_active'
    }

    if request.GET.get('flag_loading'):
        page_length = int(request.GET.get('length', 25))
        start_page = int(request.GET.get('start', 0))
        search_value = request.GET.get('search[value]')

        order_col = column_dic[request.GET.get('order[0][column]', '1')]
        order_dir = request.GET.get('order[0][dir]', 'asc')
        order_by = order_col + ' ' + order_dir

        records_total, profiles = get_list_user(page_length=page_length, start_page=start_page, order_by=order_by,
                                                search_value=search_value)

        records_filtered = len(profiles)
        data = []
        for id, profile in enumerate(profiles):
            row_data = [id + 1,
                        profile['user_id'],
                        profile['username'],
                        profile['email'],
                        profile['last_login'].strftime('%Y-%m-%d %H:%M:%S') if profile['last_login'] else 'Never',
                        profile['total_apps'],
                        profile['is_active'],
                        profile['user_id']]
            data.append(row_data)
        json_data_table = {'recordsTotal': records_total, 'recordsFiltered': records_filtered, 'data': data}
        return HttpResponse(json.dumps(json_data_table, cls=DjangoJSONEncoder), content_type='application/json')
    else:
        apps = App.get_all_app(request.user)
        form = RegisterForm()
        return render(request, 'loginapp/admin_user_list.html', {'form': form, 'apps': apps})