from django.urls import path
from django.conf.urls import url
from django.conf import settings
from django.contrib.auth import views as auth_views

from . import views, admin_views

urlpatterns = [
    url(r'^$', views.login, name='index'),

    url(r'^login/$', views.login, name='login'),

    url(r'^re_auth/$', views.re_auth, name='re_auth'),

    url(r'^password-confirmation/$', views.password_confirm, name='password_confirmation'),

    url(r'^logout/$', views.logout, name='logout'),

    # url(r'^register/$', views.register, name='register'),

    url(r'^request-password-reset/$',
        auth_views.PasswordResetView.as_view(template_name='loginapp/password_reset_email.html',
                                             email_template_name='loginapp/password_reset_email_form.html'),
        name='password_reset_email'),

    url(r'^request-password-reset/confirm/$',
        auth_views.PasswordResetDoneView.as_view(template_name='loginapp/password_reset_email_done.html'),
        name='password_reset_done'),

    url(r'^password-reset/(?P<uidb64>[0-9A-Za-z_\-]+)/(?P<token>[0-9A-Za-z]{1,13}-[0-9A-Za-z]{1,20})/$',
        auth_views.PasswordResetConfirmView.as_view(template_name='loginapp/password_reset_confirm.html'),
        name='password_reset_confirm'),

    url(r'^password-reset/complete/$',
        auth_views.PasswordResetCompleteView.as_view(template_name='loginapp/password_reset_complete.html'),
        name='password_reset_complete'),

    # url(r'^dashboard/$', views.dashboard, name='dashboard'),

    url(r'^apps/$', views.list_apps, name='dashboard'),

    url(r'^profile/settings', views.profile, name='profile'),

    url(r'^profile/change-password/$', views.change_password_profile, name='change_password'),

    url(r'^add-app/$', views.add_app, name='add_app'),

    url(r'^issue-api-key/$', views.get_api_key, name='get_api_key'),

    path('apps/<int:app_id>/settings', views.app_detail, name='app_detail'),

    path('apps/<int:app_id>/users/', views.user_report, name='statistic_login'),

    path('apps/<int:app_id>/dashboard', views.app_report, name='report_app'),

    path('apps/<int:app_id>/delete', views.delete_app, name='delete_app'),

    path('apps/<int:app_id>/channels/', views.list_channels, name='channel_list'),

    url(r'^apps/add-channel/$', views.add_channel, name='add_channel'),

    path('apps/<int:app_id>/channels/<int:channel_id>/', views.channel_detail, name='channel_detail'),

    path('apps/<int:app_id>/channels/<int:channel_id>/delete', views.delete_channel, name='delete_channel'),

    path('apps/<int:app_id>/users/<str:social_id>/', views.list_social_users, name='social_users_detail'),

    path('apps/<int:app_id>/users-social/delete', views.delete_user_social, name='delete_user_social'),

    path('apps/<int:app_id>/users-social-info/delete', views.delete_user_social_info, name='delete_user_social_info'),

    url(r'^admin/users/$', admin_views.admin_list_users, name='admin_users'),

    url(r'^add-user/$', admin_views.admin_add_user, name='admin_add_user'),

    path('users/<int:user_id>/delete', admin_views.admin_delete_user, name='admin_delete_user'),

    url(r'^update-user/$', admin_views.admin_update_user, name='admin_update_user'),

    url(r'^admin/apps/$', admin_views.admin_list_apps, name='admin_apps'),

    url(r'^admin/report/$', admin_views.admin_report_register, name='admin_report'),

    url(r'^admin/setting/$', admin_views.admin_setting, name='admin_setting'),
]
