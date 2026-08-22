from rest_framework import serializers
from .models import CustomerParcel

class TrackingSerializer(serializers.ModelSerializer):
    shipper_name = serializers.CharField(source='shipper.customer_name', read_only=True)
    status = serializers.SerializerMethodField()
    destination = serializers.SerializerMethodField()
    consignee = serializers.SerializerMethodField()
    consignee_phone = serializers.SerializerMethodField()
    order_number = serializers.SerializerMethodField()
    service_type = serializers.SerializerMethodField()

    class Meta:
        model = CustomerParcel
        fields = ['cn', 'status', 'destination', 'consignee', 'consignee_phone',
                   'order_number', 'service_type', 'shipment_date', 'shipper_name', 'delivery_date']

    def get_status(self, obj):
        return obj.status or ''

    def get_destination(self, obj):
        return obj.destination or ''

    def get_consignee(self, obj):
        return obj.consignee or ''

    def get_consignee_phone(self, obj):
        return obj.consignee_phone or ''

    def get_order_number(self, obj):
        return obj.order_number or ''

    def get_service_type(self, obj):
        return obj.service_type or ''