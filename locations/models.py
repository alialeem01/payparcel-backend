from django.db import models
from customers.models import Customer

class Destination(models.Model):
    STATUS_CHOICES = [('Active', 'Active'), ('Inactive', 'Inactive')]
    ZONE_CHOICES = [('With in City', 'With in City'), ('Different', 'Different'), ('Same', 'Same')]

    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, related_name='destinations', null=True, blank=True)
    name = models.CharField(max_length=150)
    short_name = models.CharField(max_length=50, blank=True, null=True)
    location = models.CharField(max_length=100, blank=True, null=True, help_text="Latitude,Longitude")
    zone = models.CharField(max_length=20, choices=ZONE_CHOICES, blank=True, null=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='Active')
    date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name


class Branch(models.Model):
    STATUS_CHOICES = [('Active', 'Active'), ('Inactive', 'Inactive')]

    branch_name = models.CharField(max_length=100, unique=True)
    city = models.ForeignKey(Destination, on_delete=models.SET_NULL, null=True, blank=True, related_name='branches')
    address = models.TextField(blank=True, null=True)
    contact_number = models.CharField(max_length=20, blank=True, null=True)
    manager_name = models.CharField(max_length=100, blank=True, null=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='Active')

    def __str__(self):
        return self.branch_name