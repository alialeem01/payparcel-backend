from rest_framework import serializers
from .models import CustomerParcel

class TrackingSerializer(serializers.ModelSerializer):
    shipper_name = serializers.CharField(source='shipper.customer_name', read_only=True)
    status = serializers.SerializerMethodField()
    destination = serializers.SerializerMethodField()
    consignee = serializers.SerializerMethodField()

    class Meta:
        model = CustomerParcel
        fields = ['cn', 'status', 'destination', 'consignee', 'shipment_date', 'shipper_name', 'delivery_date']

    def get_status(self, obj):
        return obj.status or ''

    def get_destination(self, obj):
        return obj.destination or ''

    def get_consignee(self, obj):
        return obj.consignee or ''