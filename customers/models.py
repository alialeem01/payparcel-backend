from django.db import models

class Customer(models.Model):
    STATUS_CHOICES = [('Active', 'Active'), ('Inactive', 'Inactive')]
    YES_NO = [('Yes', 'Yes'), ('No', 'No')]

    # Personal Details
    customer_name = models.CharField(max_length=255)
    customer_display_name = models.CharField(max_length=255, blank=True, null=True)
    customer_city = models.CharField(max_length=100, blank=True, null=True)
    customer_branch = models.CharField(max_length=100, blank=True, null=True)
    customer_user = models.CharField(max_length=100, blank=True, null=True)
    customer_brand_name = models.CharField(max_length=255, blank=True, null=True)
    customer_email = models.EmailField(blank=True, null=True)
    customer_cnic = models.CharField(max_length=20, blank=True, null=True)
    customer_phone_number = models.CharField(max_length=20)
    customer_alternate_phone = models.CharField(max_length=20, blank=True, null=True)
    sales_person = models.CharField(max_length=255, blank=True, null=True)
    customer_status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='Active')
    return_details_show = models.CharField(max_length=3, choices=YES_NO, default='No')

    show_billing_section = models.CharField(max_length=3, choices=YES_NO, default='Yes')
    show_balance = models.CharField(max_length=3, choices=YES_NO, default='Yes')
    show_dc = models.CharField(max_length=3, choices=YES_NO, default='Yes')

    customer_product_details = models.TextField(blank=True, null=True)
    customer_address = models.TextField(blank=True, null=True)
    customer_pickup_address = models.TextField(blank=True, null=True)

    third_party_booking_auto = models.CharField(max_length=3, choices=YES_NO, default='No')
    third_party_booking = models.CharField(max_length=100, blank=True, null=True)
    third_party_booking_type = models.CharField(max_length=50, default='OVERNIGHT')
    third_party_booking_by = models.CharField(max_length=50, default='Selected')
    alternate_third_party_booking = models.CharField(max_length=100, blank=True, null=True)
    alternate_third_party_booking_type = models.CharField(max_length=100, blank=True, null=True)

    show_shipper_logo_in_label = models.CharField(max_length=3, choices=YES_NO, default='No')
    shipper_allow_to_open = models.CharField(max_length=3, choices=YES_NO, default='No')
    auto_update_pickup_status = models.CharField(max_length=3, choices=YES_NO, default='No')
    show_third_party_label = models.CharField(max_length=3, choices=YES_NO, default='No')
    live_tpl_tracking = models.CharField(max_length=3, choices=YES_NO, default='Yes')
    show_tpl_tracking_cn = models.CharField(max_length=3, choices=YES_NO, default='Yes')
    show_direct_tpl_status = models.CharField(max_length=3, choices=YES_NO, default='No')
    select_courier_in_loadsheet = models.CharField(max_length=3, choices=YES_NO, default='No')
    customer_prefix = models.CharField(max_length=20, blank=True, null=True)

    shipper_brand_logo = models.ImageField(upload_to='shipper_logos/', blank=True, null=True)
    default_intractions = models.CharField(max_length=255, blank=True, null=True)
    api_key = models.CharField(max_length=255, blank=True, null=True, editable=False)

    weight_calculate = models.CharField(max_length=50, default='Full KG 1.0')
    additional_calculate = models.CharField(max_length=50, default='Weight Same')
    calculate_type = models.CharField(max_length=50, default='Unlimited Weights')
    return_rate_apply = models.CharField(max_length=3, choices=YES_NO, default='Yes')
    limited_service_type = models.CharField(max_length=3, choices=YES_NO, default='No')
    zone_type = models.CharField(max_length=50, default='Two Zone')
    default_rate_template = models.CharField(max_length=100, blank=True, null=True)
    default_tax_template = models.CharField(max_length=100, blank=True, null=True)

    customer_bank_title = models.CharField(max_length=255, blank=True, null=True)
    customer_bank_name = models.CharField(max_length=255, blank=True, null=True)
    customer_bank_ac = models.CharField(max_length=100, blank=True, null=True)
    customer_bank_ibn_number = models.CharField(max_length=100, blank=True, null=True)

    def __str__(self):
        return self.customer_name


class ServiceTypeList(models.Model):
    customer = models.ForeignKey(Customer, related_name='service_type_list', on_delete=models.CASCADE)
    service_type = models.CharField(max_length=100)
    date = models.DateField(auto_now_add=True)


class RateTemplateEntry(models.Model):
    customer = models.ForeignKey(Customer, related_name='rate_templates', on_delete=models.CASCADE)
    zone = models.CharField(max_length=100, blank=True, null=True)
    service_type = models.CharField(max_length=100, blank=True, null=True)
    charge_type = models.CharField(max_length=100, blank=True, null=True)
    unit = models.CharField(max_length=50, blank=True, null=True)
    rate = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    return_rate = models.DecimalField(max_digits=10, decimal_places=2, default=0)


class TaxTemplateEntry(models.Model):
    customer = models.ForeignKey(Customer, related_name='tax_templates', on_delete=models.CASCADE)
    service_type = models.CharField(max_length=100, blank=True, null=True)
    tax_type = models.CharField(max_length=100, blank=True, null=True)
    formula_type = models.CharField(max_length=100, blank=True, null=True)
    rate = models.DecimalField(max_digits=10, decimal_places=2, default=0)


class CourierPickupList(models.Model):
    customer = models.ForeignKey(Customer, related_name='courier_pickup_list', on_delete=models.CASCADE)
    courier = models.CharField(max_length=100, blank=True, null=True)
    pickup_id = models.CharField(max_length=100, blank=True, null=True)
    date = models.DateField(auto_now_add=True)