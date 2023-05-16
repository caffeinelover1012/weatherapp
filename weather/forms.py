from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import get_user_model
from .models import Customer
from django.utils import timezone
from django.db import models

class LoginForm(forms.Form):
    username = forms.CharField(label='Username', max_length=64)
    password = forms.CharField(label='Password', max_length=64, widget=forms.PasswordInput)

    class Meta:
        model = get_user_model()

class RegistrationForm(UserCreationForm):
    email = forms.EmailField(max_length=254, help_text='Required. Enter a valid email address.')
    class Meta:
        model = get_user_model()
        # print(model)
        fields = ('username', 'email', 'password1', 'password2')


class UploadFileForm(forms.Form):
    file = forms.FileField()