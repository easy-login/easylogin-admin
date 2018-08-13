from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.template import loader

from loginapp.forms import RegisterForm
from django.contrib.auth import login as signin, authenticate
# Create your views here.

def index(request):
	template = loader.get_template('loginapp/index.html')
	return HttpResponse(template.render())

def login(request):
	template = loader.get_template('loginapp/page-login.html')
	return HttpResponse(template.render())

def register(request):
	if request.method == 'POST':
		form = RegisterForm(request.POST)
		if form.is_valid():			
			user = form.save(commit=False)
			email = form.cleaned_data.get('email')
			password = form.cleaned_data.get('password')
			user.set_password(password)
			user.save()
			# user_auth = authenticate(email=email, password=password)
			# signin(request, user_auth)
			return redirect('login')
		else:
			print(form.errors)
	else:
		form = RegisterForm() 

	return render(request, 'loginapp/page-register.html', {'form': form})

	
def recover(request):
	template = loader.get_template('loginapp/page-recoverpw.html')
	return HttpResponse(template.render())

def error404(request):
	template = loader.get_template('loginapp/page-404.html')
	return HttpResponse(template.render())
