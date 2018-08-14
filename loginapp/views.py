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
    message = ""
    if request.method == 'POST':
        email = request.POST['email']
        password = request.POST['password']
        user = authenticate(username=email, password=password)
        if user is not None:
            signin(request, user)
            redirect('index')
        else:
            message = "Email or Password Incorrect !"

    return render(request, 'loginapp/page-login.html', {'message': message})


def register(request):
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            password = form.cleaned_data.get('password')
            user.set_password(password)
            user.save()
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
