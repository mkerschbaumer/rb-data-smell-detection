from django import forms
from django.views import generic
from django.contrib.auth.models import User
from app.models import File, Column, DetectedSmell, SmellType, Parameter
from django.core.exceptions import ValidationError

class ParameterForm(forms.ModelForm):
    value = forms.FloatField(
        required=False,
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

    def clean_value(self):
        data = self.cleaned_data['value']
        if data:
            if self.instance.max_value == -1:
                if data < self.instance.min_value:
                    raise forms.ValidationError("Value must be between " + str(self.instance.min_value) + " and inf!")
            else:
                if data < self.instance.min_value or data > self.instance.max_value:
                    raise forms.ValidationError("Value must be between " + str(self.instance.min_value) + " and " + str(self.instance.max_value) + "!")
        return data

