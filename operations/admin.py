from django.contrib import admin
from .models import PickupSheet, Manifest, DeliverySheet

@admin.register(PickupSheet)
class PickupSheetAdmin(admin.ModelAdmin):
    list_display = ('sheet_number', 'rider', 'shipper', 'loadsheet', 'total_pickup_parcel', 'user', 'branch', 'pickup_status', 'qr_code', 'date')
    list_editable = ('pickup_status',)
    filter_horizontal = ('parcels',)
    readonly_fields = ('sheet_number', 'total_pickup_parcel', 'user', 'branch', 'qr_code', 'last_update', 'date')
    search_fields = ('sheet_number',)
    list_filter = ('pickup_status', 'branch')

    fields = ('rider', 'shipper', 'parcels', 'user', 'branch', 'total_pickup_parcel', 'pickup_status', 'loadsheet', 'qr_code', 'last_update', 'date')

    def save_model(self, request, obj, form, change):
        if not obj.user:
            obj.user = request.user.username.upper()
        super().save_model(request, obj, form, change)

    def save_related(self, request, form, formsets, change):
        super().save_related(request, form, formsets, change)
        for parcel in form.instance.parcels.all():
            parcel.status = 'Picked'
            parcel.save()


@admin.register(Manifest)
class ManifestAdmin(admin.ModelAdmin):
    list_display = ('code', 'user', 'branch', 'origin', 'destination', 'mode_of_transportation', 'seal_no', 'total_weight', 'total_pcs', 'total_parcel', 'date')
    filter_horizontal = ('parcels',)
    readonly_fields = ('code', 'date')
    search_fields = ('code',)
    list_filter = ('mode_of_transportation', 'branch')

    def save_related(self, request, form, formsets, change):
        super().save_related(request, form, formsets, change)
        # Auto-update linked parcels to "In Transit" status
        for parcel in form.instance.parcels.all():
            parcel.status = 'In Transit'
            parcel.save()


@admin.register(DeliverySheet)
class DeliverySheetAdmin(admin.ModelAdmin):
    list_display = ('ds_number', 'user', 'branch', 'rider', 'cn_list', 'sheet_status', 'origin', 'area', 'total_parcels', 'total_cod', 'date')
    filter_horizontal = ('parcels',)
    readonly_fields = ('ds_number', 'date')
    search_fields = ('ds_number',)
    list_filter = ('sheet_status', 'branch')

    def save_related(self, request, form, formsets, change):
        super().save_related(request, form, formsets, change)
        # Only mark Delivered if the sheet itself is marked Close (completed)
        if form.instance.sheet_status == 'Close':
            for parcel in form.instance.parcels.all():
                parcel.status = 'Delivered'
                parcel.save()