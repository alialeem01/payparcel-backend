from django.contrib import admin
from .models import Invoice

@admin.register(Invoice)
class InvoiceAdmin(admin.ModelAdmin):
    list_display = ('invoice_number', 'status', 'date', 'customer', 'account_name', 'cod', 'flyer_charges', 'total_tax', 'delivery_charges', 'net_amount', 'parcel_from', 'parcel_to', 'total_parcel')
    filter_horizontal = ('parcels',)
    readonly_fields = ('invoice_number', 'date')
    search_fields = ('invoice_number', 'customer__customer_name')
    list_filter = ('status', 'account_name')