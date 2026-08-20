from rest_framework import serializers
from .models import CustomerParcel

class TrackingSerializer(serializers.ModelSerializer):
    shipper_name = serializers.CharField(source='shipper.customer_name', read_only=True)

    class Meta:
        model = CustomerParcel
        fields = ['cn', 'status', 'destination', 'consignee', 'shipment_date', 'shipper_name', 'delivery_date']