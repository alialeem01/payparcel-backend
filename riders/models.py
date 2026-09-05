from django.conf import settings
from django.db import models


class Rider(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
        related_name='rider_profile', null=True, blank=True
    )
    name = models.CharField(max_length=255)
    phone_number = models.CharField(max_length=20)
    cnic_number = models.CharField(max_length=20, default='')
    cnic_front_image = models.ImageField(upload_to='rider_cnic/', default='')
    cnic_back_image = models.ImageField(upload_to='rider_cnic/', default='')
    vehicle_type = models.CharField(max_length=50, blank=True, null=True)
    vehicle_number = models.CharField(max_length=50, blank=True, null=True)
    branch = models.CharField(max_length=100, blank=True, null=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name
        