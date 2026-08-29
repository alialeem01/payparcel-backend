from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import authenticate
from .serializers import RegisterSerializer
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated



@api_view(['POST'])
def register_customer(request):
    serializer = RegisterSerializer(data=request.data)
    if serializer.is_valid():
        customer = serializer.save()
        return Response({'message': 'Registered successfully'}, status=201)
    return Response(serializer.errors, status=400)

@api_view(['POST'])
def login_customer(request):
    email = request.data.get('email')
    password = request.data.get('password')
    user = authenticate(username=email, password=password)
    if user is not None:
        refresh = RefreshToken.for_user(user)
        return Response({
            'access': str(refresh.access_token),
            'refresh': str(refresh),
        })
    return Response({'error': 'Invalid credentials'}, status=401)

from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import permission_classes
from .models import Customer

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_current_customer(request):
    try:
        customer = Customer.objects.get(customer_user=request.user.username)
        return Response({
            'business_name': customer.customer_brand_name,
            'contact_person': customer.customer_name,
            'email': customer.customer_email,
            'phone': customer.customer_phone_number,
            'address': customer.customer_address,
        })
    except Customer.DoesNotExist:
        return Response({'error': 'Customer profile not found'}, status=404)

@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def update_customer_profile(request):
    try:
        customer = Customer.objects.get(customer_user=request.user.username)
    except Customer.DoesNotExist:
        return Response({'error': 'Customer profile not found'}, status=404)

    customer.customer_brand_name = request.data.get('business_name', customer.customer_brand_name)
    customer.customer_name = request.data.get('contact_person', customer.customer_name)
    customer.customer_phone_number = request.data.get('phone', customer.customer_phone_number)
    customer.customer_address = request.data.get('address', customer.customer_address)
    customer.save()
    return Response({'message': 'Profile updated successfully'})

from invoices.models import Invoice

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def billing_summary(request):
    try:
        customer = Customer.objects.get(customer_user=request.user.username)
    except Customer.DoesNotExist:
        return Response({'error': 'Customer profile not found'}, status=404)

    invoices = Invoice.objects.filter(customer=customer).order_by('-date')

    balance_payment = sum(inv.net_amount for inv in invoices.filter(status='Unpaid'))
    cod_delivered_return = float(invoices.aggregate(t=models.Sum('cod'))['t'] or 0)
    delivery_flyer_charges = float(invoices.aggregate(t=models.Sum('delivery_charges'))['t'] or 0)

    invoice_list = [{
        'invoice_number': inv.invoice_number,
        'status': inv.status,
        'date': inv.date,
        'account_name': inv.account_name,
        'cod': float(inv.cod),
        'flyer_charges': float(inv.flyer_charges),
        'total_tax': float(inv.total_tax),
        'delivery_charges': float(inv.delivery_charges),
        'net_amount': inv.net_amount,
        'parcel_from': inv.parcel_from,
        'parcel_to': inv.parcel_to,
        'total_parcel': inv.total_parcel,
    } for inv in invoices]

    return Response({
        'balance_payment': balance_payment,
        'cod_delivered_return': cod_delivered_return,
        'delivery_flyer_charges': delivery_flyer_charges,
        'invoices': invoice_list,
    })

from operations.models import DeliverySheet

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def customer_delivery_sheets(request):
    try:
        customer = Customer.objects.get(customer_user=request.user.username)
    except Customer.DoesNotExist:
        return Response({'error': 'Customer profile not found'}, status=404)

    sheets = DeliverySheet.objects.filter(shipper=customer)
    data = [{
        'ds_number': s.ds_number,
        'tracking_number': s.tracking_number,
        'date': s.date,
        'status': s.sheet_status,
        'rider_name': s.rider.name if s.rider else None,
        'rider_contact': s.rider.phone_number if s.rider else None,
        'rider_vehicle': s.rider.vehicle_number if s.rider else None,
        'total_parcels': s.total_parcels,
        'total_weight': s.total_weight,
        'total_cod': s.total_cod,
        'qr_url': s.qr_code.url if s.qr_code else None,
        'print_url': f'/track/deliverysheet/{s.tracking_number}/print/',
    } for s in sheets]
    return Response(data)