from django.contrib import admin
from .models import Customer, ServiceTypeList, RateTemplateEntry, TaxTemplateEntry, CourierPickupList

class ServiceTypeInline(admin.TabularInline):
    model = ServiceTypeList
    extra = 1

class RateTemplateInline(admin.TabularInline):
    model = RateTemplateEntry
    extra = 1

class TaxTemplateInline(admin.TabularInline):
    model = TaxTemplateEntry
    extra = 1

class CourierPickupInline(admin.TabularInline):
    model = CourierPickupList
    extra = 1

@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
    list_display = ('customer_name', 'id', 'customer_brand_name', 'customer_cnic', 'customer_phone_number', 'sales_person', 'customer_branch', 'customer_status')
    search_fields = ('customer_name', 'customer_brand_name', 'customer_cnic', 'customer_phone_number')
    list_filter = ('customer_status', 'customer_branch')

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