# -*- encoding: utf-8 -*-
"""
Copyright (c) 2019 - present AppSeed.us
"""

from django import forms
from django.views import generic
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from django.contrib.auth.models import User

class LoginForm(forms.Form):
    username = forms.CharField(
        widget=forms.TextInput(
            attrs={
                "placeholder" : "Username",                
                "class": "form-control"
            }
        ))
    password = forms.CharField(
        widget=forms.PasswordInput(
            attrs={
                "placeholder" : "Password",                
                "class": "form-control"
            }
        ))

class SignUpForm(UserCreationForm):
    username = forms.CharField(
        widget=forms.TextInput(
            attrs={
                "placeholder" : "Username",                
                "class": "form-control"
            }
        ))
    email = forms.EmailField(
        widget=forms.EmailInput(
            attrs={
                "placeholder" : "Email",                
                "class": "form-control"
            }
        ))
    password1 = forms.CharField(
        widget=forms.PasswordInput(
            attrs={
                "placeholder" : "Password",                
                "class": "form-control"
            }
        ))
    password2 = forms.CharField(
        widget=forms.PasswordInput(
            attrs={
                "placeholder" : "Password check",                
                "class": "form-control"
            }
        ))
    firstname = forms.CharField(
        widget=forms.TextInput(
            attrs={
                "placeholder" : "First name",                
                "class": "form-control"
            }
        ))
    lastname = forms.CharField(
        widget=forms.TextInput(
            attrs={
                "placeholder" : "Last name",                
                "class": "form-control"
            }
        ))

    class Meta:
        model = User
        fields = ('username', 'email', 'password1', 'password2', 'firstname', 'lastname')

class UserUpdateForm(forms.ModelForm):
    username = forms.CharField(
        max_length = 20,
        widget=forms.TextInput(
            attrs={
                "placeholder" : "Username",                
                "class": "form-control"
            }
        ))
    email = forms.EmailField(
        widget=forms.EmailInput(
            attrs={
                "placeholder" : "Email",                
                "class": "form-control"
            }
        ))
    first_name = forms.CharField(
        max_length = 20,
        widget=forms.TextInput(
            attrs={
                "placeholder" : "First name",                
                "class": "form-control"
            }
        ))
    last_name = forms.CharField(
        max_length = 20,
        widget=forms.TextInput(
            attrs={
                "placeholder" : "Last name",                
                "class": "form-control"
            }
        ))

    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email']