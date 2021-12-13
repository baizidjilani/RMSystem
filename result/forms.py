from django import forms
from django.contrib.auth.forms import AuthenticationForm
from .models import *
import datetime



class UserAuthenticationForm(AuthenticationForm):
    def __init__(self, *args, **kwargs):
        super(UserAuthenticationForm, self).__init__(*args, **kwargs)
        self.fields['username'].label = ''
        self.fields['password'].label = ''
        self.fields['username'].widget.attrs['placeholder'] = 'Username'
        self.fields['password'].widget.attrs['placeholder'] = 'Password'


    password = forms.CharField(label='Enter password', 
                                widget=forms.PasswordInput)

    class Meta:
        model = User
        fields = ("username","password")
        help_texts = {
            "username":None,
        }
