from django.http import HttpResponseRedirect
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.urls import reverse
from django.utils import timezone
from .forms import CustomerForm, LoginForm, RegistrationForm
from .models import Customer
import json
from .forms import UploadFileForm
from .utils import process_excel
from django.shortcuts import get_object_or_404
from twilio.rest import Client
from .models import Message, Customer
from django.conf import settings
from django import forms
from .forms import MessageForm
from .filters import CustomerFilter
from django.views.generic.edit import UpdateView, DeleteView, FormView
from django.urls import reverse_lazy
from django.shortcuts import get_object_or_404

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
    
def send_message(message_id):
    message = get_object_or_404(Message, id=message_id)

    # You need to set these values to your Twilio Account SID and Auth token
    account_sid = 'AC42589e35c4322239bc687d7a46d47632'
    auth_token = 'f9edf75550296ce6847705832344730a'
    client = Client(account_sid, auth_token)
    # print(message)
    phone_number = message.customer.phone_number
    # print(message.customer)
    # print(phone_number)
    if phone_number:
        twilio_message = client.messages.create(
            body=message.text,
            from_='+18556425052',  # This is your Twilio phone number
            to=phone_number
        )

        # Update the message as sent
        message.sent = True
        message.save()
    return 
    # return HttpResponseRedirect(reverse('messages'))

def send_message_view(request):
    if request.method == 'POST':
        form = MessageForm(request.POST)
        if form.is_valid():
            message = form.save(commit=False)
            message.sender = request.user
            message.save()

            send_message(message.id)  # Call the function to send the message

            messages.success(request, "Message sent successfully.")
            return redirect('send_message_view')
    else:
        form = MessageForm()

    return render(request, 'send_message.html', {'form': form})

def message_history(request):
    message_history = Message.objects.all().order_by('-send_date')
    return render(request, 'message_history.html', {'message_history': message_history})

def customers(request):
    filter = CustomerFilter(request.GET, queryset=Customer.objects.all())
    return render(request, 'customers.html', {'filter': filter})


def add_customer(request):
    if request.method == "POST":
        form = CustomerForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Customer created successfully.")
            return redirect('customers')
        else:
            messages.error(request, "Could not create customer!")
    else:
        form = CustomerForm()

    return render(request, 'add_customer.html', {'form': form})



# views.py
class CustomerUpdateView(UpdateView):
    model = Customer
    template_name = 'customer.html'
    fields = ['phone_number', 'email', 'full_name', 'address', 'zip_code']

    def get_object(self):
        id_ = self.kwargs.get("id")
        return get_object_or_404(Customer, id=id_)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['customer'] = self.get_object()
        return context

    def get_success_url(self):
        return reverse_lazy('customer', kwargs={'id': self.object.id})

class CustomerDeleteView(DeleteView):
    model = Customer
    template_name = 'confirm_delete.html'
    success_url = reverse_lazy('customers')

    def get_object(self):
        id_ = self.kwargs.get("id")
        return get_object_or_404(Customer, id=id_)

class SendMessageView(FormView):
    template_name = 'send_message.html'
    form_class = MessageForm

    def get_initial(self):
        initial = super().get_initial()
        initial['customer'] = self.kwargs.get('id')
        return initial

    def form_valid(self, form):
        message = form.save(commit=False)
        message.customer = get_object_or_404(Customer, id=self.kwargs.get('id'))
        message.save()
        send_message(message.id)
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['customer'] = get_object_or_404(Customer, id=self.kwargs.get('id'))  # add this line
        return context

    def get_success_url(self):
        return reverse_lazy('customer', kwargs={'id': self.kwargs.get('id')})
