from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.core.serializers.json import DjangoJSONEncoder

from loginapp.models import App, User
from loginapp.forms import RegisterForm
from loginapp.views import push_messages_error

import json


def admin_list_users(request):
    if not request.user.is_superuser:
        redirect('dashboard')
    column_dic = {
        '1': '_id',
        '2': 'username',
        '3': 'email',
        '4': 'number_apps',
        '5': 'last_login',
        '6': 'is_active'
    }

    if request.GET.get('flag_loading'):
        page_length = int(request.GET.get('length', 25))
        start_page = int(request.GET.get('start', 0))
        search_value = request.GET.get('search[value]')

        order_col = column_dic[request.GET.get('order[0][column]', '1')]
        order_dir = request.GET.get('order[0][dir]', 'asc')
        order_by = order_col + ' ' + order_dir

        records_total = User.objects.all().count()

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
            messages.success(request,"User was successfully created!")
            return redirect('admin_users')
        else:
            push_messages_error(request, form)
            print(form.errors)

    return redirect('admin_users')
