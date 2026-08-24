from django.contrib import admin
from django.db.models import Sum, Count, F
from unfold.admin import ModelAdmin, TabularInline
from unfold.decorators import display
from django_unfold_admin_listfilter_dropdown.filters import DropdownFilter
from unfold.contrib.filters.admin import ChoicesDropdownFilter, RangeDateFilter
from .models import Customer, ServiceTypeList, RateTemplateEntry, TaxTemplateEntry, CourierPickupList


class ServiceTypeInline(TabularInline):
    model = ServiceTypeList
    extra = 1


class RateTemplateInline(TabularInline):
    model = RateTemplateEntry
    extra = 1


class TaxTemplateInline(TabularInline):
    model = TaxTemplateEntry
    extra = 1


class CourierPickupInline(TabularInline):
    model = CourierPickupList
    extra = 1


@admin.register(Customer)
class CustomerAdmin(ModelAdmin):
    list_display = (
        'customer_name', 'id', 'customer_brand_name', 'customer_cnic',
        'customer_phone_number', 'display_address', 'sales_person',
        'customer_branch', 'customer_status', 'show_balance',
        'total_unpaid_parcel', 'view_account', 'total_balance',
        'customer_created_at',
    )
    search_fields = ('customer_name', 'customer_brand_name', 'customer_cnic', 'customer_phone_number')
    list_filter_submit = True

    list_filter = (
        ('customer_name', DropdownFilter),
        ('sales_person', DropdownFilter),
        ('customer_brand_name', DropdownFilter),
        ('customer_branch', DropdownFilter),
        ('customer_cnic', DropdownFilter),
        ('customer_phone_number', DropdownFilter),
        ('customer_bank_ibn_number', DropdownFilter),
        ('customer_status', ChoicesDropdownFilter),
        ('customer_created_at', RangeDateFilter),
    )

    @display(description='Customer Address')
    def display_address(self, obj):
        return obj.customer_address or '-'

    @display(description='Total Unpaid Parcel')
    def total_unpaid_parcel(self, obj):
        return obj.parcels.filter(
            status='Delivered',
            customer_payment_status='Unpaid'
        ).count()

    @display(description='Total Balance')
    def total_balance(self, obj):
        unpaid = obj.parcels.filter(status='Delivered', customer_payment_status='Unpaid')
        total = unpaid.aggregate(
            balance=Sum(F('cod') - F('total_gst') - F('total_feul_tax') - F('delivery_charge'))
        )['balance']
        return total if total is not None else 0

    @display(description='View Account')
    def view_account(self, obj):
        from django.utils.html import format_html
        from django.urls import reverse
        url = reverse('admin:parcels_customerparcel_changelist') + f'?shipper__id__exact={obj.pk}'
        return format_html('<a href="{}">View</a>', url)

    fieldsets = (
        ('Personal Details', {
            'fields': (
                ('customer_name', 'customer_display_name'),
                ('customer_city', 'customer_branch'),
                ('customer_user', 'customer_brand_name'),
                ('customer_email', 'customer_cnic'),
                ('customer_phone_number', 'customer_alternate_phone'),
                ('sales_person', 'customer_status', 'return_details_show'),
            )
        }),
        ('Display Settings', {
            'fields': (
                ('show_billing_section', 'show_balance', 'show_dc'),
                'customer_product_details',
                ('customer_address', 'customer_pickup_address'),
            )
        }),
        ('Third Party Booking', {
            'fields': (
                ('third_party_booking_auto', 'third_party_booking', 'third_party_booking_type'),
                ('third_party_booking_by', 'alternate_third_party_booking', 'alternate_third_party_booking_type'),
                ('show_shipper_logo_in_label', 'shipper_allow_to_open', 'auto_update_pickup_status'),
                ('show_third_party_label', 'live_tpl_tracking', 'show_tpl_tracking_cn'),
                ('show_direct_tpl_status', 'select_courier_in_loadsheet', 'customer_prefix'),
                ('shipper_brand_logo', 'default_intractions'),
            )
        }),
        ('Rate Details', {
            'fields': (
                ('weight_calculate', 'additional_calculate', 'calculate_type', 'return_rate_apply', 'limited_service_type'),
                ('zone_type', 'default_rate_template', 'default_tax_template'),
            )
        }),
        ('Bank Details', {
            'fields': (
                ('customer_bank_title', 'customer_bank_name'),
                ('customer_bank_ac', 'customer_bank_ibn_number'),
            )
        }),
    )

    inlines = [ServiceTypeInline, RateTemplateInline, TaxTemplateInline, CourierPickupInline]