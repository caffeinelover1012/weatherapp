from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import get_user_model
from .models import Message, Customer
from django.utils import timezone
from django.db import models
import requests

class BulkMessageForm(forms.Form):
    customers = forms.ModelMultipleChoiceField(
        queryset=Customer.objects.all(),
        widget=forms.CheckboxSelectMultiple
    )
    text_template = forms.CharField(widget=forms.Textarea)

class CustomerForm(forms.ModelForm):
    class Meta:
        model = Customer
        fields = ['full_name', 'phone_number', 'email', 'address', 'zip_code']

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

class MessageForm(forms.ModelForm):
    class Meta:
        model = Message
        fields = ['text', 'send_date']
        widgets = {
            'text': forms.Textarea(attrs={'class': 'form-control'}),
            'send_date': forms.DateTimeInput(attrs={'type': 'datetime-local', 'class': 'form-control'})
        }
