from django.shortcuts import render, redirect, get_object_or_404
from loginapp.models import App


def admin_list_users(request):
    if not request.user.is_superuser:
        redirect('dashboard')


    apps = App.get_all_app(request.user)
    return render(request, 'loginapp/admin_user_list.html', {'apps': apps})
