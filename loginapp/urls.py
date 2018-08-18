from django.urls import path
from django.conf.urls import url
from django.conf import settings
from . import views

urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^login/$', views.login, name='login'),
    url(r'^logout/$', views.logout, name='logout'),
    url(r'^register/$', views.register, name='register'),
    url(r'^reset-password-email/$', views.password_reset_email, name='password-reset-email'),
    url(r'^reset-password-email-done/$', views.password_reset_email_done, name='password-reset-email-done'),

    url(r'^dashboard/$', views.dashboard, name='dashboard'),
    url(r'^profile/$', views.profile, name='profile'),
    url(r'^change-password/$', views.change_password_profile, name='change_password'),
]
