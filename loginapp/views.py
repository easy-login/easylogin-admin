from django.shortcuts import render, redirect, render_to_response
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.template import loader

from loginapp.forms import RegisterForm, UpdateProfileForm
from django.contrib.auth import login as signin, logout as signout, authenticate
from loginapp.backends import AuthenticationWithEmailBackend


# Create your views here.

def index(request):
    return render(request, 'loginapp/index.html')


def login(request):
    message = ''
    if request.method == 'POST':
        email = request.POST['email']
        password = request.POST['password']
        user = AuthenticationWithEmailBackend.authenticate(None, username=email, password=password)
        if user is not None:
            request.session.set_expiry(86400)
            signin(request, user)
            return redirect('index')
        else:
            message = 'Email or Password Incorrect !'

    return render(request, 'loginapp/page-login.html', {'message': message})


@login_required
def logout(request):
    signout(request)
    return redirect('index')


def register(request):
    if request.user.is_authenticated:
        return redirect('index')
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            password = form.cleaned_data.get('password')
            email = form.cleaned_data.get('email')
            user.set_password(password)
            user.email = email
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


@login_required
def dashboard(request):
    return render(request, 'loginapp/dashboard.html')


@login_required
def profile(request):
    if request.method == 'POST':
        form = UpdateProfileForm(request.POST, instance=request.user)
        if form.is_valid():
            user = form.save(commit=False)
            email = form.cleaned_data.get('email')
            user.email = email
            user.save()

            return redirect('profile')
        else:
            print(form.errors)
    else:
        form = UpdateProfileForm()

    return render(request, 'loginapp/profile.html', {'form': form})


def error404(request):
    template = loader.get_template('loginapp/page-404.html')
    return HttpResponse(template.render())
