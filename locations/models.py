from django.db import models

class Destination(models.Model):
    STATUS_CHOICES = [('Active', 'Active'), ('Inactive', 'Inactive')]
    ZONE_CHOICES = [
        ('With in City', 'With in City'),
        ('Different', 'Different'),
        ('Same', 'Same'),
        ('Zone 1', 'Zone 1'),
        ('Zone 2', 'Zone 2'),
        ('Zone 3', 'Zone 3'),
        ('Zone 4', 'Zone 4'),
        ('Zone 5', 'Zone 5'),
        ('Zone 6', 'Zone 6'),
        ('Zone 7', 'Zone 7'),
    ]

    name = models.CharField(max_length=150)
    address = models.TextField(blank=True, null=True)
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
    address = models.TextField(blank=True, null=True)
    contact_number = models.CharField(max_length=20, blank=True, null=True)
    manager_name = models.CharField(max_length=100, blank=True, null=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='Active')

    def __str__(self):
        return self.branch_name