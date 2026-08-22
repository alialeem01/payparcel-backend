from django.contrib import admin
from .models import PickupSheet, Manifest, DeliverySheet

@admin.register(PickupSheet)
class PickupSheetAdmin(admin.ModelAdmin):
    list_display = ('sheet_number', 'rider', 'shipper', 'loadsheet', 'total_pickup_parcel', 'user', 'branch', 'pickup_status', 'date')
    filter_horizontal = ('parcels',)
    readonly_fields = ('sheet_number', 'date')
    search_fields = ('sheet_number',)
    list_filter = ('pickup_status', 'branch')

@admin.register(Manifest)
class ManifestAdmin(admin.ModelAdmin):
    list_display = ('code', 'user', 'branch', 'origin', 'destination', 'mode_of_transportation', 'seal_no', 'total_weight', 'total_pcs', 'total_parcel', 'date')
    filter_horizontal = ('parcels',)
    readonly_fields = ('code', 'date')
    search_fields = ('code',)
    list_filter = ('mode_of_transportation', 'branch')

@admin.register(DeliverySheet)
class DeliverySheetAdmin(admin.ModelAdmin):
    list_display = ('ds_number', 'user', 'branch', 'rider', 'cn_list', 'sheet_status', 'origin', 'area', 'total_parcels', 'total_cod', 'date')
    filter_horizontal = ('parcels',)
    readonly_fields = ('ds_number', 'date')
    search_fields = ('ds_number',)
    list_filter = ('sheet_status', 'branch')