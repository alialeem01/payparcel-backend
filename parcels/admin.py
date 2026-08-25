from django.contrib import admin
from django.contrib import messages
from django.shortcuts import render
from unfold.admin import ModelAdmin
from unfold.contrib.filters.admin import ChoicesDropdownFilter
from django_unfold_admin_listfilter_dropdown.filters import DropdownFilter
from .models import CustomerParcel, StatusNarration


@admin.register(CustomerParcel)
class CustomerParcelAdmin(ModelAdmin):
    list_display = ('cn', 'shipper', 'order_number', 'status', 'customer_payment_status', 'destination', 'city',
                     'delivery_rider_service_provider', 'cod', 'net_total', 'branch', 'payment_status_display', 'active')
    list_editable = ('status', 'customer_payment_status')
    search_fields = ('cn', 'order_number', 'consignee', 'api_tracking_no')
    list_filter_submit = True
    list_filter = ( ('city', DropdownFilter),
        ('status', ChoicesDropdownFilter),
        'active',
        ('customer_payment_status', ChoicesDropdownFilter),
        ('tpl_payment_status', ChoicesDropdownFilter),
        ('destination', DropdownFilter),
    )
    readonly_fields = ('cn', 'net_total', 'last_update', 'shipment_date', 'tracking_qr_code')
    actions = ['assign_to_rider']

    fieldsets = (
        ('Parcel Details', {
            'fields': (
                ('cn', 'shipper', 'city', 'destination'),
                ('delivery_rider_service_provider', 'api_sp_type'),
                ('api_tracking_no', 'tpl_payment_status', 'customer_payment_status'),
                ('assigned_rider', 'tracking_qr_code'),
                ('consignee', 'consignee_phone'),
                ('alternate_phone', 'order_number', 'issue_destination'),
                ('cod', 'rts_cod', 'parcel_declared_value', 'discount'),
                ('service_type', 'parcel_weight', 'number_of_pieces', 'replace'),
                ('product', 'instructions'),
                ('flyer_size', 'flyer_qty'),
                'address',
                'location',
                ('shipper_advice_remark', 'message'),
                ('active', 'status', 'reason'),
                'proof_image',
                ('delivery_date', 'delivery_time', 'share'),
                ('order_from', 'store_order_number', 'loadsheet', 'customer_loadsheet'),
                ('last_update', 'shipment_date'),
                ('branch', 'user'),
            )
        }),
        ('Total Charges', {
            'fields': (
                'rate_calculation_mode',
                ('total_gst', 'total_feul_tax', 'total_return', 'flyer_charges'),
                ('third_party_charge', 'tpl_net_total'),
                ('delivery_charge', 'net_total'),
            )
        }),
        ('BarCodes', {
            'fields': (
                ('qr_code_upload', 'bar_code_upload'),
                ('pl_qr_code_upload', 'pl_bar_code_upload'),
            )
        }),
    )

    def payment_status_display(self, obj):
        return obj.tpl_payment_status
    payment_status_display.short_description = 'Payment Status'

    def assign_to_rider(self, request, queryset):
        from riders.models import Rider
        from operations.models import PickupSheet

        if queryset.exclude(status='Order').exists():
            self.message_user(request, 'Only parcels with status "Order" can be assigned to a rider.', level=messages.ERROR)
            return

        if 'apply' in request.POST:
            rider_id = request.POST.get('rider')
            rider = Rider.objects.get(pk=rider_id)

            shippers = set(queryset.values_list('shipper_id', flat=True))
            sheet_shipper_id = shippers.pop() if len(shippers) == 1 else None

            sheet = PickupSheet.objects.create(rider=rider, shipper_id=sheet_shipper_id)
            sheet.parcels.set(queryset)

            queryset.update(status='Ready to Pickup', assigned_rider=rider)

            self.message_user(request, f'{queryset.count()} parcel(s) assigned to {rider.name}. Pickup Sheet {sheet.sheet_number} created.')
            return

        riders = Rider.objects.filter(is_active=True)
        context = {
            **self.admin_site.each_context(request),
            'title': 'Assign to Rider',
            'queryset': queryset,
            'riders': riders,
            'opts': self.model._meta,
            'action_checkbox_name': 'admin-action-form',
        }
        return render(request, 'admin/parcels/assign_rider_action.html', context)

    assign_to_rider.short_description = 'Assign selected orders to a rider'


@admin.register(StatusNarration)
class StatusNarrationAdmin(ModelAdmin):
    list_display = ('status', 'narration')