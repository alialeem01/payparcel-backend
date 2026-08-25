from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from unfold.admin import ModelAdmin
from unfold.contrib.filters.admin import ChoicesDropdownFilter
from django_unfold_admin_listfilter_dropdown.filters import DropdownFilter
from .models import PickupSheet, Manifest, DeliverySheet
from django.shortcuts import render, redirect
from django.contrib import messages


@admin.register(PickupSheet)
class PickupSheetAdmin(ModelAdmin):
    list_display = ('sheet_number', 'rider', 'loadsheet', 'total_pickup_parcel', 'user', 'branch', 'pickup_status', 'row_actions')
    readonly_fields = ('sheet_number',)
    search_fields = ('sheet_number',)
    list_filter_submit = True
    list_filter = (
        ('pickup_status', ChoicesDropdownFilter),
        ('branch', DropdownFilter),
    )
    actions = None

    def row_actions(self, obj):
        edit_url = reverse('admin:operations_pickupsheet_change', args=[obj.pk])
        delete_url = reverse('admin:operations_pickupsheet_delete', args=[obj.pk])
        return format_html(
            '<a href="{}">Edit</a> | <a href="{}">Delete</a>',
            edit_url, delete_url
        )
    row_actions.short_description = 'Actions'

def add_view(self, request, form_url='', extra_context=None):
    from parcels.models import CustomerParcel
    from riders.models import Rider

    if request.method == 'POST':
        rider_id = request.POST.get('rider')
        parcel_ids = request.POST.getlist('parcels')

        if not rider_id or not parcel_ids:
            self.message_user(request, 'Select a rider and at least one order.', level=messages.ERROR)
            return redirect('admin:operations_pickupsheet_add')

        rider = Rider.objects.get(pk=rider_id)
        parcels = CustomerParcel.objects.filter(pk__in=parcel_ids, status='Order')

        sheet = PickupSheet.objects.create(rider=rider)
        sheet.parcels.set(parcels)
        parcels.update(status='Ready to Pickup', assigned_rider=rider)

        self.message_user(request, f'Pickup Sheet {sheet.sheet_number} created with {parcels.count()} order(s).')
        return redirect('admin:operations_pickupsheet_changelist')

    unassigned_orders = CustomerParcel.objects.filter(status='Order').select_related('shipper')
    riders = Rider.objects.filter(is_active=True)

    context = {
        **self.admin_site.each_context(request),
        'title': 'Create Pickup Sheet',
        'orders': unassigned_orders,
        'riders': riders,
        'opts': self.model._meta,
    }
    return render(request, 'admin/operations/add_pickup_sheet.html', context)


@admin.register(Manifest)
class ManifestAdmin(ModelAdmin):
    list_display = ('code', 'user', 'branch', 'origin', 'destination', 'mode_of_transportation', 'seal_no', 'total_weight', 'total_pcs', 'total_parcel', 'date', 'row_actions')
    filter_horizontal = ('parcels',)
    readonly_fields = ('code', 'date')
    search_fields = ('code',)
    list_filter_submit = True
    list_filter = (
        ('mode_of_transportation', DropdownFilter),
        ('branch', DropdownFilter),
    )
    actions = None

    def save_related(self, request, form, formsets, change):
        super().save_related(request, form, formsets, change)
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
class DeliverySheetAdmin(ModelAdmin):
    list_display = ('ds_number', 'user', 'branch', 'rider', 'cn_list', 'sheet_status', 'origin', 'area', 'total_parcels', 'total_cod', 'date', 'row_actions')
    filter_horizontal = ('parcels',)
    readonly_fields = ('ds_number', 'date')
    search_fields = ('ds_number',)
    list_filter_submit = True
    list_filter = (
        ('sheet_status', ChoicesDropdownFilter),
        ('branch', DropdownFilter),
    )
    actions = None

    def save_related(self, request, form, formsets, change):
        super().save_related(request, form, formsets, change)
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