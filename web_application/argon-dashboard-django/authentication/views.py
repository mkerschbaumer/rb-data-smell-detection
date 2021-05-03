# -*- encoding: utf-8 -*-
"""
Copyright (c) 2019 - present AppSeed.us
"""

from django.shortcuts import render

# Create your views here.
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from django.contrib.auth.models import User
from django.forms.utils import ErrorList
from django.http import HttpResponse
from .forms import LoginForm, SignUpForm, UserUpdateForm
from django.contrib.auth import logout
from django.contrib import messages

def login_view(request):
    form = LoginForm(request.POST or None)

    msg = None

    if request.method == "POST":

        if form.is_valid():
            username = form.cleaned_data.get("username")
            password = form.cleaned_data.get("password")
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                return redirect("/")
            else:    
                msg = 'Invalid credentials'    
        else:
            msg = 'Error validating the form'    

    return render(request, "accounts/login.html", {"form": form, "msg" : msg})

def register_user(request):

    msg     = None
    success = False

    if request.method == "POST":
        form = SignUpForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data.get("username")
            raw_password = form.cleaned_data.get("password1")
            firstname = form.cleaned_data.get("firstname")
            lastname = form.cleaned_data.get("lastname")
            user = authenticate(username=username, password=raw_password)
            new_user = User.objects.get(username=username)
            new_user.first_name = firstname
            new_user.last_name = lastname
            new_user.save()
            msg     = 'User created - please <a href="/login">login</a>.'
            success = True
            
            #return redirect("/login/")

        else:
            msg = 'Form is not valid'    
    else:
        form = SignUpForm()

    return render(request, "accounts/register.html", {"form": form, "msg" : msg, "success" : success })

def logout_view(request):
    logout(request)
    return render(request, "accounts/logout.html", {'some_flag': True})

def profile(request):
    msg = None

    if request.method == "POST":
        if request.POST.get('close') == 'close':
            form = UserUpdateForm(instance=request.user)
        else:
            form = UserUpdateForm(request.POST, instance=request.user)

            if form.is_valid():
                form.save()
    else:
        form = UserUpdateForm(instance=request.user)
    return render(request, "profile.html", {"form": form, "msg" : msg})
