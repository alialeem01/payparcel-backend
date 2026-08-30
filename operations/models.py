import qrcode
from io import BytesIO
from django.core.files.base import ContentFile
from django.conf import settings
from django.db import models
from customers.models import Customer
from parcels.models import CustomerParcel


class PickupSheet(models.Model):
    STATUS_CHOICES = [('Uncomplete', 'Uncomplete'), ('Complete', 'Complete')]

    sheet_number = models.CharField(max_length=50, blank=True, editable=False)
    rider = models.ForeignKey('riders.Rider', on_delete=models.SET_NULL, null=True, blank=True, related_name='pickup_sheets')
    shipper = models.ForeignKey(Customer, on_delete=models.CASCADE, related_name='pickup_sheets', null=True, blank=True)
    parcels = models.ManyToManyField(CustomerParcel, related_name='pickup_sheets', blank=True)
    user = models.CharField(max_length=100, blank=True, null=True, editable=False)
    branch = models.CharField(max_length=100, blank=True, null=True, editable=False)
    pickup_status = models.CharField(max_length=15, choices=STATUS_CHOICES, default='Uncomplete')
    qr_code = models.ImageField(upload_to='pickup_qr/', blank=True, null=True, editable=False)
    last_update = models.DateTimeField(auto_now=True)
    date = models.DateTimeField(auto_now_add=True)

    @property
    def total_pickup_parcel(self):
        return self.parcels.count()

    def save(self, *args, **kwargs):
        if not self.sheet_number:
            from datetime import date
            self.sheet_number = f"PS{date.today().year}{PickupSheet.objects.count() + 1}"
        super().save(*args, **kwargs)

        if not self.qr_code:
            tracking_url = f"{settings.SITE_BASE_URL}/track/pickupsheet/{self.sheet_number}/"
            qr_img = qrcode.make(tracking_url)
            buffer = BytesIO()
            qr_img.save(buffer, format='PNG')
            self.qr_code.save(f"{self.sheet_number}_qr.png", ContentFile(buffer.getvalue()), save=False)
            super().save(update_fields=['qr_code'])

    def __str__(self):
        return self.sheet_number


class DeliverySheet(models.Model):
    SHEET_STATUS_CHOICES = [('Pending', 'Pending'), ('Picked Up', 'Picked Up'), ('Cancelled', 'Cancelled')]

    ds_number = models.CharField(max_length=50, blank=True, editable=False, unique=True)
    tracking_number = models.CharField(max_length=50, blank=True, editable=False, unique=True)
    shipper = models.ForeignKey(Customer, on_delete=models.CASCADE, related_name='delivery_sheets', null=True, blank=True)
    rider = models.ForeignKey('riders.Rider', on_delete=models.SET_NULL, null=True, blank=True, related_name='delivery_sheets')
    pickup_sheet = models.ForeignKey(PickupSheet, on_delete=models.CASCADE, related_name='delivery_sheets', null=True, blank=True)
    parcels = models.ManyToManyField(CustomerParcel, related_name='delivery_sheets', blank=True)
    sheet_status = models.CharField(max_length=10, choices=SHEET_STATUS_CHOICES, default='Pending')
    qr_code = models.ImageField(upload_to='delivery_qr/', blank=True, null=True, editable=False)
    scanned_at = models.DateTimeField(null=True, blank=True)
    date = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('pickup_sheet', 'shipper')
        permissions = [
            ('can_scan_delivery_sheet', 'Can scan Delivery Sheet QR'),
        ]

    @property
    def total_parcels(self):
        return self.parcels.count()

    @property
    def total_weight(self):
        return sum(float(p.parcel_weight or 0) for p in self.parcels.all())

    @property
    def total_cod(self):
        return sum(float(p.cod or 0) for p in self.parcels.all())

    def save(self, *args, **kwargs):
        if not self.ds_number:
            from datetime import date
            self.ds_number = f"DS{date.today().year}{DeliverySheet.objects.count() + 1}"
        if not self.tracking_number:
            import uuid
            self.tracking_number = f"TRK{uuid.uuid4().hex[:10].upper()}"
        super().save(*args, **kwargs)

        if not self.qr_code:
            scan_url = f"{settings.SITE_BASE_URL}/api/rider/scan-delivery/{self.tracking_number}/"
            qr_img = qrcode.make(scan_url)
            buffer = BytesIO()
            qr_img.save(buffer, format='PNG')
            self.qr_code.save(f"{self.ds_number}_qr.png", ContentFile(buffer.getvalue()), save=False)
            super().save(update_fields=['qr_code'])

    def __str__(self):
        return self.ds_number