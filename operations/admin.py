from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from .models import PickupSheet, Manifest, DeliverySheet


@admin.register(PickupSheet)
class PickupSheetAdmin(admin.ModelAdmin):
    list_display = ('sheet_number', 'rider', 'shipper', 'loadsheet', 'total_pickup_parcel', 'user', 'branch', 'pickup_status', 'row_actions')
    readonly_fields = ('sheet_number',)
    search_fields = ('sheet_number',)
    list_filter = ('pickup_status', 'branch')
    actions = None  # removes the bulk action dropdown entirely

    def row_actions(self, obj):
        edit_url = reverse('admin:operations_pickupsheet_change', args=[obj.pk])
        delete_url = reverse('admin:operations_pickupsheet_delete', args=[obj.pk])
        return format_html(
            '<a href="{}">Edit</a> | <a href="{}">Delete</a>',
            edit_url, delete_url
        )
    row_actions.short_description = 'Actions'


@admin.register(Manifest)
class ManifestAdmin(admin.ModelAdmin):
    list_display = ('code', 'user', 'branch', 'origin', 'destination', 'mode_of_transportation', 'seal_no', 'total_weight', 'total_pcs', 'total_parcel', 'date', 'row_actions')
    filter_horizontal = ('parcels',)
    readonly_fields = ('code', 'date')
    search_fields = ('code',)
    list_filter = ('mode_of_transportation', 'branch')
    actions = None

    def save_related(self, request, form, formsets, change):
        super().save_related(request, form, formsets, change)
        # Auto-update linked parcels to "In Transit" status
        for parcel in form.instance.parcels.all():
            parcel.status = 'In Transit'
            parcel.save()

    def row_actions(self, obj):
        edit_url = reverse('admin:operations_manifest_change', args=[obj.pk])
        delete_url = reverse('admin:operations_manifest_delete', args=[obj.pk])
        return format_html(
            '<a href="{}">Edit</a> | <a href="{}">Delete</a>',
            edit_url, delete_url
        )
    row_actions.short_description = 'Actions'


@admin.register(DeliverySheet)
class DeliverySheetAdmin(admin.ModelAdmin):
    list_display = ('ds_number', 'user', 'branch', 'rider', 'cn_list', 'sheet_status', 'origin', 'area', 'total_parcels', 'total_cod', 'date', 'row_actions')
    filter_horizontal = ('parcels',)
    readonly_fields = ('ds_number', 'date')
    search_fields = ('ds_number',)
    list_filter = ('sheet_status', 'branch')
    actions = None

    def save_related(self, request, form, formsets, change):
        super().save_related(request, form, formsets, change)
        # Only mark Delivered if the sheet itself is marked Close (completed)
        if form.instance.sheet_status == 'Close':
            for parcel in form.instance.parcels.all():
                parcel.status = 'Delivered'
                parcel.save()

    def row_actions(self, obj):
        edit_url = reverse('admin:operations_deliverysheet_change', args=[obj.pk])
        delete_url = reverse('admin:operations_deliverysheet_delete', args=[obj.pk])
        return format_html(
            '<a href="{}">Edit</a> | <a href="{}">Delete</a>',
            edit_url, delete_url
        )
    row_actions.short_description = 'Actions'