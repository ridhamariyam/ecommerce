from django.shortcuts import render, redirect
from ecommerce_app.models import *
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import login as auth_login
from django.contrib.auth import logout as django_logout
from .models import Address
from django.core.exceptions import SuspiciousOperation
from authentication.models import *



def signup(request):
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save()
            return redirect('login')
    else:
        form = SignUpForm()
    
    return render(request, 'registration/signup.html', {'form': form, 'errors': form.errors})

def login(request):
    if request.user.is_authenticated:  
        if request.user.is_superuser:
            return redirect('dashboard')
        else:
            return redirect('home')
    
    if request.method == 'POST':
        try:
            form = AuthenticationForm(request, data=request.POST)
            if form.is_valid():
                user = form.get_user()
                auth_login(request, user)
                if user.is_superuser:
                    return redirect('dashboard')
                else:
                    return redirect('home')
        except SuspiciousOperation:
           
            return render(request, 'registration/login.html') 
    else:
        form = AuthenticationForm()
    return render(request, 'registration/login.html', {'form': form})

def logout(request):
    django_logout(request)
    return redirect('login')