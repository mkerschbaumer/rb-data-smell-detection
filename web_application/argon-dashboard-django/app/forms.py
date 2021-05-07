from django import forms
from django.views import generic
from django.contrib.auth.models import User
from app.models import File, Column, DetectedSmell, SmellType, Parameter

class ParameterForm(forms.ModelForm):
    value = forms.FloatField(
        widget=forms.NumberInput(
            attrs={
                "placeholder": "Value",
                "class": "form-control"
            }
        )
    )

    class Meta:
        model = Parameter
        fields = ('value',)

