from django.urls import path
from django.conf.urls import url
from django.conf import settings
from django.contrib.auth import views as auth_views

from . import views

urlpatterns = [
    url(r'^$', views.login, name='index'),

    url(r'^login/$', views.login, name='login'),

    url(r'^logout/$', views.logout, name='logout'),

    url(r'^register/$', views.register, name='register'),

    url(r'^password_reset_email/$',
        auth_views.PasswordResetView.as_view(template_name='loginapp/password_reset_email.html',
                                             email_template_name='loginapp/password_reset_email_form.html'),
        name='password_reset_email'),

    url(r'^password_reset_done/$',
        auth_views.PasswordResetDoneView.as_view(template_name='loginapp/password_reset_email_done.html'),
        name='password_reset_done'),

    url(r'^reset/(?P<uidb64>[0-9A-Za-z_\-]+)/(?P<token>[0-9A-Za-z]{1,13}-[0-9A-Za-z]{1,20})/$',
        auth_views.PasswordResetConfirmView.as_view(template_name='loginapp/password_reset_confirm.html'),
        name='password_reset_confirm'),

    url(r'^password_reset_complete/$',
        auth_views.PasswordResetCompleteView.as_view(template_name='loginapp/password_reset_complete.html'),
        name='password_reset_complete'),

    url(r'^dashboard/$', views.dashboard, name='dashboard'),

    url(r'^profile/$', views.profile, name='profile'),

    url(r'^change_password/$', views.change_password_profile, name='change_password'),

    url(r'^add_app/$', views.add_app, name='add_app'),

    url(r'^get_api_key/$', views.get_api_key, name='get_api_key'),

    path('app/<int:app_id>/', views.app_detail, name='app_detail'),

    path('statistic_login/<int:app_id>/', views.statistic_login, name='statistic_login'),

    path('delete_app/<int:app_id>/', views.delete_app, name='delete_app'),

    path('app/<int:app_id>/channels/', views.channel_list, name='channel_list'),

    url(r'^add_channel/$', views.add_channel, name='add_channel'),

    path('app/<int:app_id>/channel/<int:channel_id>/', views.channel_detail, name='channel_detail'),

    path('delete_channel/<int:app_id>/<int:channel_id>/', views.delete_channel, name='delete_channel'),
]
