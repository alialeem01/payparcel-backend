from django.db import models
from customers.models import Customer
from parcels.models import CustomerParcel

class Invoice(models.Model):
    STATUS_CHOICES = [('Paid', 'Paid'), ('Unpaid', 'Unpaid')]
    ACCOUNT_CHOICES = [('Via Bank', 'Via Bank'), ('EasyPaisa', 'EasyPaisa'), ('JazzCash', 'JazzCash'), ('Cash', 'Cash')]

    invoice_number = models.CharField(max_length=50, blank=True, editable=False)
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, related_name='invoices')
    parcels = models.ManyToManyField(CustomerParcel, related_name='invoices', blank=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='Unpaid')
    date = models.DateField(auto_now_add=True)
    account_name = models.CharField(max_length=20, choices=ACCOUNT_CHOICES, default='Via Bank')

    cod = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    flyer_charges = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    total_tax = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    delivery_charges = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    parcel_from = models.CharField(max_length=100, blank=True, null=True)
    parcel_to = models.CharField(max_length=100, blank=True, null=True)

    @property
    def net_amount(self):
        return float(self.cod) - float(self.flyer_charges) - float(self.total_tax) - float(self.delivery_charges)

    @property
    def total_parcel(self):
        return self.parcels.count()

    def save(self, *args, **kwargs):
        if not self.invoice_number:
            from datetime import date
            today = date.today().strftime('%d%m%y')
            self.invoice_number = f"PDF {today}-{Invoice.objects.count() + 1}"
        super().save(*args, **kwargs)

    def __str__(self):
        return self.invoice_number