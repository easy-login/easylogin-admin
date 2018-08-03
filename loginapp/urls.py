from django.urls import path
from . import views

urlpatterns = [
	path('', views.index, name='index'),
	path('login/', views.login_page, name='login_page'),
	path('register/', views.register_page, name='register_page'),
	path('recover/', views.recover_page, name='recover_page'),
]