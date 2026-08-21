from django.db import models
from customers.models import Customer
from parcels.models import CustomerParcel

class Loadsheet(models.Model):
    loadsheet_no = models.CharField(max_length=50, blank=True, editable=False)
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, related_name='loadsheets')
    parcels = models.ManyToManyField(CustomerParcel, related_name='loadsheets', blank=True)
    created_by = models.CharField(max_length=100, blank=True, null=True)
    loadsheet_date = models.DateTimeField(auto_now_add=True)
    qr_code = models.ImageField(upload_to='loadsheet_qr/', blank=True, null=True)

    @property
    def total_weight(self):
        return sum(float(p.parcel_weight or 0) for p in self.parcels.all())

    @property
    def total_consignee(self):
        return self.parcels.count()

    @property
    def total_pieces(self):
        return sum(p.number_of_pieces or 0 for p in self.parcels.all())

    @property
    def total_cod(self):
        return sum(float(p.cod or 0) for p in self.parcels.all())

    def save(self, *args, **kwargs):
        if not self.loadsheet_no:
            self.loadsheet_no = f"LSH{2025}{Loadsheet.objects.count() + 1:02d}"
        super().save(*args, **kwargs)

    def __str__(self):
        return self.loadsheet_no