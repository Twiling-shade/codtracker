from django import forms
from .models import users
from django.core.exceptions import ValidationError


class RegUser(forms.ModelForm):
    class Meta:
        model = users
        fields = ['user', 'mp', 'wz', 'cw']
        widgets = {
            'user': forms.TextInput(attrs={
                'class': 'form-control form-control-user',
                'placeholder': 'User#battletag'
            }),
            'mp' : forms.CheckboxInput(attrs={'class': 'custom-control-input'}),
            'wz' : forms.CheckboxInput(attrs={'class': 'custom-control-input'}),
            'cw' : forms.CheckboxInput(attrs={'class': 'custom-control-input'}),
            }
