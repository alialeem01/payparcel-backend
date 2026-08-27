from django.contrib import admin
from django.contrib import messages
from django.utils.html import format_html
from django.urls import reverse
from django.shortcuts import render, redirect, get_object_or_404
from unfold.admin import ModelAdmin
from unfold.contrib.filters.admin import ChoicesDropdownFilter
from django_unfold_admin_listfilter_dropdown.filters import DropdownFilter
from parcels.models import PAKISTAN_CITIES
from .models import PickupSheet, Manifest, DeliverySheet


@admin.register(PickupSheet)
class PickupSheetAdmin(ModelAdmin):
    list_display = ('sheet_number', 'rider', 'total_pickup_parcel', 'user', 'branch', 'pickup_status', 'row_actions')
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
        view_url = reverse('track_pickup_sheet', args=[obj.sheet_number])
        print_url = reverse('print_pickup_sheet', args=[obj.sheet_number])
        return format_html(
            '<a href="{}">Edit</a> | <a href="{}">Delete</a> | <a href="{}" target="_blank">View</a> | <a href="{}" target="_blank">Print</a>',
            edit_url, delete_url, view_url, print_url
        )
    row_actions.short_description = 'Actions'

    def delete_model(self, request, obj):
        obj.parcels.update(status='Order', assigned_rider=None)
        super().delete_model(request, obj)

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

            if '_addanother' in request.POST:
                return redirect('admin:operations_pickupsheet_add')
            if '_continue' in request.POST:
                return redirect('admin:operations_pickupsheet_change', sheet.pk)
            return redirect('admin:operations_pickupsheet_changelist')

        unassigned_orders = CustomerParcel.objects.filter(status='Order').select_related('shipper')

        selected_city = request.GET.get('city', '')
        cities = [c[0] for c in PAKISTAN_CITIES]

        if selected_city:
            unassigned_orders = unassigned_orders.filter(city=selected_city)

        riders = Rider.objects.filter(is_active=True)
        next_sheet_number_preview = f"PS{__import__('datetime').date.today().year}{PickupSheet.objects.count() + 1}"

        context = {
            **self.admin_site.each_context(request),
            'title': 'Create Pickup Sheet',
            'orders': unassigned_orders,
            'riders': riders,
            'cities': cities,
            'selected_city': selected_city,
            'sheet_number_preview': next_sheet_number_preview,
            'opts': self.model._meta,
        }
        return render(request, 'admin/operations/add_pickup_sheet.html', context)

    def change_view(self, request, object_id, form_url='', extra_context=None):
        from parcels.models import CustomerParcel
        from riders.models import Rider

        sheet = get_object_or_404(PickupSheet, pk=object_id)

        if request.method == 'POST':
            rider_id = request.POST.get('rider')
            parcel_ids = set(request.POST.getlist('parcels'))

            if not rider_id:
                self.message_user(request, 'Select a rider.', level=messages.ERROR)
                return redirect('admin:operations_pickupsheet_change', object_id)

            rider = Rider.objects.get(pk=rider_id)

            current_parcel_ids = set(str(pk) for pk in sheet.parcels.values_list('pk', flat=True))
            removed_ids = current_parcel_ids - parcel_ids
            added_ids = parcel_ids - current_parcel_ids

            if removed_ids:
                CustomerParcel.objects.filter(pk__in=removed_ids).update(status='Order', assigned_rider=None)

            if added_ids:
                CustomerParcel.objects.filter(pk__in=added_ids, status='Order').update(status='Ready to Pickup', assigned_rider=rider)

            sheet.rider = rider
            sheet.parcels.set(CustomerParcel.objects.filter(pk__in=parcel_ids))
            sheet.save()

            self.message_user(request, f'Pickup Sheet {sheet.sheet_number} updated.')

            if '_addanother' in request.POST:
                return redirect('admin:operations_pickupsheet_add')
            if '_continue' in request.POST:
                return redirect('admin:operations_pickupsheet_change', object_id)
            return redirect('admin:operations_pickupsheet_changelist')

        assigned_parcels = sheet.parcels.select_related('shipper').all()
        assigned_ids = set(str(pk) for pk in assigned_parcels.values_list('pk', flat=True))

        unassigned_orders = CustomerParcel.objects.filter(status='Order').select_related('shipper')

        selected_city = request.GET.get('city', '')
        cities = [c[0] for c in PAKISTAN_CITIES]
        if selected_city:
            unassigned_orders = unassigned_orders.filter(city=selected_city)

        combined_orders = list(assigned_parcels) + [p for p in unassigned_orders if str(p.pk) not in assigned_ids]

        riders = Rider.objects.filter(is_active=True)

        context = {
            **self.admin_site.each_context(request),
            'title': f'Edit Pickup Sheet - {sheet.sheet_number}',
            'sheet': sheet,
            'orders': combined_orders,
            'assigned_ids': assigned_ids,
            'riders': riders,
            'cities': cities,
            'selected_city': selected_city,
            'opts': self.model._meta,
        }
        return render(request, 'admin/operations/change_pickup_sheet.html', context)


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