from rest_framework import serializers
from django.contrib.auth.models import User
from .models import Customer

class RegisterSerializer(serializers.Serializer):
    business_name = serializers.CharField()
    contact_person = serializers.CharField()
    email = serializers.EmailField()
    phone = serializers.CharField()
    password = serializers.CharField(write_only=True)
    address = serializers.CharField(required=False, allow_blank=True)

    def create(self, validated_data):
        user = User.objects.create_user(
            username=validated_data['email'],
            email=validated_data['email'],
            password=validated_data['password']
        )
        customer = Customer.objects.create(
            customer_name=validated_data['contact_person'],
            customer_brand_name=validated_data['business_name'],
            customer_email=validated_data['email'],
            customer_phone_number=validated_data['phone'],
            customer_address=validated_data.get('address', ''),
            customer_user=user.username,
        )
        return customer