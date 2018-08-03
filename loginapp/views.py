from django.shortcuts import render
from django.http import HttpResponse
from django.template import loader
# Create your views here.

def index(request):
	return HttpResponse("Hello World. It's time to make money")

def login_page(request):
	template = loader.get_template('loginapp/page-login.html')
	return HttpResponse(template.render())

def register_page(request):
	template = loader.get_template('loginapp/page-register.html')
	return HttpResponse(template.render())

def recover_page(request):
	template = loader.get_template('loginapp/page-recoverpw.html')
	return HttpResponse(template.render())

