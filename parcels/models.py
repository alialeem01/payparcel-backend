import qrcode
from io import BytesIO
from django.core.files.base import ContentFile
from django.db import models
from customers.models import Customer

PAKISTAN_CITIES = [
    ('Karachi', 'Karachi'), ('Lahore', 'Lahore'), ('Islamabad', 'Islamabad'), ('Rawalpindi', 'Rawalpindi'),
    ('Faisalabad', 'Faisalabad'), ('Multan', 'Multan'), ('Peshawar', 'Peshawar'), ('Quetta', 'Quetta'),
    ('Sialkot', 'Sialkot'), ('Gujranwala', 'Gujranwala'), ('Hyderabad', 'Hyderabad'), ('Bahawalpur', 'Bahawalpur'),
    ('Sargodha', 'Sargodha'), ('Sukkur', 'Sukkur'), ('Larkana', 'Larkana'), ('Sheikhupura', 'Sheikhupura'),
    ('Rahim Yar Khan', 'Rahim Yar Khan'), ('Jhang', 'Jhang'), ('Gujrat', 'Gujrat'), ('Mardan', 'Mardan'),
    ('Kasur', 'Kasur'), ('Dera Ghazi Khan', 'Dera Ghazi Khan'), ('Sahiwal', 'Sahiwal'), ('Nawabshah', 'Nawabshah'),
    ('Mingora', 'Mingora'), ('Okara', 'Okara'), ('Mirpur Khas', 'Mirpur Khas'), ('Chiniot', 'Chiniot'),
    ('Kamoke', 'Kamoke'), ('Mandi Bahauddin', 'Mandi Bahauddin'), ('Jhelum', 'Jhelum'), ('Sadiqabad', 'Sadiqabad'),
    ('Jacobabad', 'Jacobabad'), ('Shikarpur', 'Shikarpur'), ('Khanewal', 'Khanewal'), ('Hafizabad', 'Hafizabad'),
    ('Kohat', 'Kohat'), ('Muzaffargarh', 'Muzaffargarh'), ('Khanpur', 'Khanpur'), ('Gojra', 'Gojra'),
    ('Mandi Bahauddin', 'Mandi Bahauddin'), ('Abbottabad', 'Abbottabad'), ('Turbat', 'Turbat'), ('Dadu', 'Dadu'),
    ('Bahawalnagar', 'Bahawalnagar'), ('Muridke', 'Muridke'), ('Pakpattan', 'Pakpattan'), ('Attock', 'Attock'),
    ('Vehari', 'Vehari'), ('Nowshera', 'Nowshera'), ('Chakwal', 'Chakwal'), ('Swabi', 'Swabi'),
    ('Dera Ismail Khan', 'Dera Ismail Khan'), ('Chishtian', 'Chishtian'), ('Daska', 'Daska'), ('Mansehra', 'Mansehra'),
    ('Nankana Sahib', 'Nankana Sahib'), ('Wah Cantt', 'Wah Cantt'), ('Kot Addu', 'Kot Addu'), ('Toba Tek Singh', 'Toba Tek Singh'),
    ('Ahmedpur East', 'Ahmedpur East'), ('Khairpur', 'Khairpur'), ('Chaman', 'Chaman'), ('Zhob', 'Zhob'),
    ('Gwadar', 'Gwadar'), ('Khuzdar', 'Khuzdar'), ('Muzaffarabad', 'Muzaffarabad'), ('Mirpur (AJK)', 'Mirpur (AJK)'),
    ('Gilgit', 'Gilgit'), ('Skardu', 'Skardu'), ('Charsadda', 'Charsadda'), ('Hangu', 'Hangu'),
    ('Ferozwala', 'Ferozwala'), ('Burewala', 'Burewala'), ('Jaranwala', 'Jaranwala'), ('Kabirwala', 'Kabirwala'),
]

class CustomerParcel(models.Model):
    YES_NO = [('Yes', 'Yes'), ('No', 'No')]
    STATUS_CHOICES = [
        ('Order', 'Order'),
        ('Ready to Pickup', 'Ready to Pickup'),
        ('Picked', 'Picked'),
        ('In Transit', 'In Transit'),
        ('Delivered', 'Delivered'),
        ('Parcel Not Available', 'Parcel Not Available'),
        ('Returned', 'Returned'),
    ]
    PAYMENT_STATUS = [('Paid', 'Paid'), ('Unpaid', 'Unpaid')]
    SHARE_CHOICES = [('No Share', 'No Share')]
    RATE_MODE = [('Automatic', 'Automatic'), ('Manual', 'Manual')]

    API_SP_TYPE_CHOICES = [
        ('PostEx Normal', 'PostEx Normal'), ('PostEx Reversed', 'PostEx Reversed'), ('PostEx Replacement', 'PostEx Replacement'),
        ('Rush Trax', 'Rush Trax'), ('Trax Swift', 'Trax Swift'), ('Trax Saver plus', 'Trax Saver plus'), ('Trax Same day', 'Trax Same day'),
        ('Orio COD', 'Orio COD'),
        ('Digi detain', 'Digi detain'), ('Digi overnight', 'Digi overnight'), ('Digi overland', 'Digi overland'),
        ('Rocket LEO', 'Rocket LEO'), ('Rocket LEO - Detain', 'Rocket LEO - Detain'), ('Rocket LEO - Overland', 'Rocket LEO - Overland'),
        ('Rocket POSTEX', 'Rocket POSTEX'), ('Rocket TRAX', 'Rocket TRAX'), ('Rocket TRAX - Detain', 'Rocket TRAX - Detain'),
        ('Rocket', 'Rocket'), ('Rocket Detain', 'Rocket Detain'), ('Rocket Overland', 'Rocket Overland'),
        ('IEPS COD', 'IEPS COD'), ('IEPS Non COD', 'IEPS Non COD'), ('IEPS Detain', 'IEPS Detain'),
        ('IEPS Overland (Non COD)', 'IEPS Overland (Non COD)'), ('IEPS overland COD', 'IEPS overland COD'), ('IEPS Bulk', 'IEPS Bulk'),
        ('M&P Overnight', 'M&P Overnight'), ('M&P Second Day', 'M&P Second Day'),
        ('TCS Express', 'TCS Express'), ('TCS Economy Express', 'TCS Economy Express'), ('TCS MYO (SELF COLLECTION)', 'TCS MYO (SELF COLLECTION)'),
        ('LEOPARD DETAIN', 'LEOPARD DETAIN'), ('LEOPARD OVERLAND', 'LEOPARD OVERLAND'), ('LEOPARD OVERNIGHT', 'LEOPARD OVERNIGHT'),
        ('BLUE CARGO (BG)', 'BLUE CARGO (BG)'), ('BLUE TRUNK (BT)', 'BLUE TRUNK (BT)'), ('BLUE EDGE (BE)', 'BLUE EDGE (BE)'),
        ('Heavy Shipment', 'Heavy Shipment'), ('Normal', 'Normal'),
        ('Rush Trax | overnight (Digi) | Orio COD', 'Rush Trax | overnight (Digi) | Orio COD'),
        ('Saver plus Trax | detain (Digi)', 'Saver plus Trax | detain (Digi)'),
        ('Swift Trax | overland (Digi)', 'Swift Trax | overland (Digi)'),
        ('Same day Trax', 'Same day Trax'),
        ('COD', 'COD'), ('Non COD', 'Non COD'), ('Detain', 'Detain'),
        ('Overland (Non COD)', 'Overland (Non COD)'), ('overland COD', 'overland COD'), ('Bulk', 'Bulk'),
        ('Overnight M&P', 'Overnight M&P'), ('Second Day M&P', 'Second Day M&P'),
        ('Express', 'Express'), ('Economy Express', 'Economy Express'), ('MYO (SELF COLLECTION)', 'MYO (SELF COLLECTION)'),
        ('OVERLAND', 'OVERLAND'), ('OVERNIGHT', 'OVERNIGHT'),
        ('Reversed (PostEx)', 'Reversed (PostEx)'), ('Replacement (PostEx)', 'Replacement (PostEx)'),
    ]

    cn = models.CharField(max_length=50, blank=True, editable=False)
    shipper = models.ForeignKey(Customer, on_delete=models.CASCADE, related_name='parcels')
    city = models.CharField(max_length=100, choices=PAKISTAN_CITIES, blank=True, null=True)
    delivery_rider_service_provider = models.CharField(max_length=100, blank=True, null=True)
    api_sp_type = models.CharField(max_length=100, choices=API_SP_TYPE_CHOICES, default='OVERNIGHT')
    api_tracking_no = models.CharField(max_length=100, blank=True, null=True)
    tpl_payment_status = models.CharField(max_length=10, choices=PAYMENT_STATUS, default='Unpaid')
    customer_payment_status = models.CharField(max_length=10, choices=PAYMENT_STATUS, default='Unpaid')

    assigned_rider = models.ForeignKey(
        'riders.Rider', on_delete=models.SET_NULL,
        null=True, blank=True, related_name='assigned_parcels'
    )
    tracking_qr_code = models.ImageField(upload_to='parcel_qr/', blank=True, null=True, editable=False)

    consignee = models.CharField(max_length=255, blank=True, null=True)
    consignee_phone = models.CharField(max_length=20, blank=True, null=True)
    alternate_phone = models.CharField(max_length=20, blank=True, null=True)
    order_number = models.CharField(max_length=100, blank=True, null=True)
    issue_destination = models.CharField(max_length=100, blank=True, null=True)

    cod = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    rts_cod = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    parcel_declared_value = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    discount = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    service_type = models.CharField(max_length=50, default='COD')
    parcel_weight = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    third_party_weight = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    number_of_pieces = models.PositiveIntegerField(default=1)
    replace = models.CharField(max_length=3, choices=YES_NO, default='No')

    product = models.TextField(blank=True, null=True, default='No')
    instructions = models.TextField(blank=True, null=True, default='Handle with Care')

    flyer_size = models.CharField(max_length=50, blank=True, null=True)
    flyer_qty = models.PositiveIntegerField(default=0)

    address = models.TextField(blank=True, null=True)
    location = models.CharField(max_length=255, blank=True, null=True)

    shipper_advice_remark = models.TextField(blank=True, null=True)
    message = models.TextField(blank=True, null=True)

    active = models.CharField(max_length=3, choices=YES_NO, default='Yes')
    status = models.CharField(max_length=30, choices=STATUS_CHOICES, default='Order')
    reason = models.CharField(max_length=100, blank=True, null=True)

    proof_image = models.ImageField(upload_to='proof_images/', blank=True, null=True)

    delivery_date = models.DateField(blank=True, null=True)
    delivery_time = models.TimeField(blank=True, null=True)
    share = models.CharField(max_length=50, choices=SHARE_CHOICES, default='No Share')

    order_from = models.CharField(max_length=100, blank=True, null=True)
    store_order_number = models.CharField(max_length=100, blank=True, null=True)
    loadsheet = models.CharField(max_length=100, blank=True, null=True)
    customer_loadsheet = models.CharField(max_length=100, blank=True, null=True)

    last_update = models.DateTimeField(auto_now=True)
    shipment_date = models.DateTimeField(blank=True, null=True)

    branch = models.CharField(max_length=100, blank=True, null=True)
    user = models.CharField(max_length=100, blank=True, null=True)

    rate_calculation_mode = models.CharField(max_length=20, choices=RATE_MODE, default='Automatic')
    total_gst = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    total_feul_tax = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    total_return = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    flyer_charges = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    third_party_charge = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    tpl_net_total = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    delivery_charge = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    net_total = models.DecimalField(max_digits=10, decimal_places=2, default=0, editable=False)

    qr_code_upload = models.ImageField(upload_to='qr_codes/', blank=True, null=True)
    bar_code_upload = models.ImageField(upload_to='bar_codes/', blank=True, null=True)
    pl_qr_code_upload = models.ImageField(upload_to='pl_qr_codes/', blank=True, null=True)
    pl_bar_code_upload = models.ImageField(upload_to='pl_bar_codes/', blank=True, null=True)

    created_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        self.net_total = (self.delivery_charge + self.flyer_charges + self.total_gst +
                           self.total_feul_tax + self.tpl_net_total) - self.discount
        if not self.cn:
            self.cn = f"PP{1000000 + (CustomerParcel.objects.count() + 1)}"
        super().save(*args, **kwargs)

        if not self.tracking_qr_code:
            from django.conf import settings
            tracking_url = f"{settings.SITE_BASE_URL}/track/{self.cn}/"
            qr_img = qrcode.make(tracking_url)
            buffer = BytesIO()
            qr_img.save(buffer, format='PNG')
            self.tracking_qr_code.save(f"{self.cn}_qr.png", ContentFile(buffer.getvalue()), save=False)
            super().save(update_fields=['tracking_qr_code'])

    def __str__(self):
        return self.cn or f"Parcel #{self.pk}"


class StatusNarration(models.Model):
    status = models.CharField(max_length=30, choices=CustomerParcel.STATUS_CHOICES, unique=True)
    narration = models.TextField(help_text="Customer-facing message shown for this status")

    def __str__(self):
        return self.status