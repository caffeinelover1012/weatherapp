from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.utils import timezone
from .forms import LoginForm, RegistrationForm
from .models import Customer, Message
import json
from .forms import UploadFileForm
from .utils import process_excel

from datetime import datetime
from django.http import HttpResponse


# Create your views here.
def index(request):
    return render(request, 'index.html')

def about(request):
    return render(request, 'index.html')

# User authentication views
def user_login(request):
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                next_url = request.GET.get('next','index')  # get the 'next' parameter, if it doesn't exist, default to 'search'
                return redirect(next_url)
            else:
                messages.error(request, "Invalid username or password.")
    else:
        form = LoginForm()
    return render(request, 'login.html', {'form': form})

def register(request):
    if request.user.is_authenticated:
        return redirect('login')
    
    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Account created successfully.")
            return redirect('login')
    else:
        form = RegistrationForm()
    return render(request, 'register.html', {'form': form, 'errors': form.errors, 'messages': messages.get_messages(request)})


@login_required
def user_logout(request):
    logout(request)
    return redirect('index')

def parse_excel(request):
    if request.method == 'POST':
        form = UploadFileForm(request.POST, request.FILES)
        if form.is_valid():
            file = request.FILES['file']
            nrows = request.POST.get('nrows', 700)  # Adjust this as necessary
            df = process_excel(file, nrows)

            # Now you have a DataFrame `df` that you can use to create Customer objects
            # Here's a simple example of how you could do it:
            for index, row in df.iterrows():
                try:
                    Customer.objects.create(
                        phone_number=row['PhoneNumbers'],
                        email=row['Email'],
                        full_name=row['FullName'],
                        address=row['BillingAddress'],
                        zip_code=row['ShippingAddress']
                    )
                except:
                    print("SAME DETAILS:", row['PhoneNumbers'], row['Email'])

            return render(request, 'success.html')  # Render a success page

    else:
        form = UploadFileForm()
    
    return render(request, 'upload.html', {'form': form})
    

def customers(request):
    customers = Customer.objects.all()
    return render(request, 'customers.html', {'customers': customers})

def create_message(request):
    return render(request, 'create-message.html', {})

def message_sent(request):
    if request.method == 'POST':
        subject = request.POST.get('subject')
        message = request.POST.get('message')
        # process the message data as needed

        new_message = Message(subject=subject, body=message, date_time=datetime.now())
        new_message.save()
        return HttpResponse('LIGMA request.')
    else:
        return HttpResponse('Invalid request.')