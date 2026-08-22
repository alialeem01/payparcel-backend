from django.contrib import admin
from .models import Invoice

@admin.register(Invoice)
class InvoiceAdmin(admin.ModelAdmin):
    list_display = ('invoice_number', 'status', 'date', 'customer', 'account_name', 'cod', 'flyer_charges', 'total_tax', 'delivery_charges', 'net_amount', 'parcel_from', 'parcel_to', 'total_parcel')
    filter_horizontal = ('parcels',)
    readonly_fields = ('invoice_number', 'date', 'cod', 'flyer_charges', 'delivery_charges')
    search_fields = ('invoice_number', 'customer__customer_name')
    list_filter = ('status', 'account_name')

    def save_related(self, request, form, formsets, change):
        super().save_related(request, form, formsets, change)
        # Auto-calculate totals from linked parcels
        parcels = form.instance.parcels.all()
        invoice = form.instance
        invoice.cod = sum(float(p.cod or 0) for p in parcels)
        invoice.flyer_charges = sum(float(p.flyer_charges or 0) for p in parcels)
        invoice.delivery_charges = sum(float(p.delivery_charge or 0) for p in parcels)
        invoice.save()