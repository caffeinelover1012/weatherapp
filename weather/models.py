from django.db import models
from django.utils import timezone

# Create your models here.
class Customer(models.Model):
    phone_number = models.CharField(max_length=20, blank=True, null=True)
    email = models.EmailField(max_length=100, blank=True, null=True)
    full_name = models.CharField(max_length=100)
    address = models.CharField(max_length=200, blank=True, null=True)
    zip_code = models.CharField(max_length=10, blank=True, null=True)

    class Meta:
        constraints = [
            models.CheckConstraint(
                check=models.Q(phone_number__isnull=False) | models.Q(email__isnull=False), 
                name='At least one of phone number or email must be provided.'
            ),
            models.UniqueConstraint(
                fields=['phone_number', 'email'],
                name='unique_phone_email'
            )
        ]

    def __str__(self):
        return f'Customer {self.full_name}'

class Message(models.Model):
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)
    text = models.TextField()
    send_date = models.DateTimeField(default=timezone.now)
    sent = models.BooleanField(default=False)

    def __str__(self):
        return f'Message to {self.customer.full_name} at {self.send_date}'