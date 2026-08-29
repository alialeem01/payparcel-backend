from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import authenticate
from django.utils import timezone
from .models import Rider
from operations.models import DeliverySheet


@api_view(['POST'])
@permission_classes([AllowAny])
def rider_login(request):
    username = request.data.get('username')
    password = request.data.get('password')
    user = authenticate(username=username, password=password)
    if not user or not hasattr(user, 'rider_profile'):
        return Response({'error': 'Invalid credentials'}, status=401)
    refresh = RefreshToken.for_user(user)
    return Response({'access': str(refresh.access_token), 'refresh': str(refresh), 'rider_name': user.rider_profile.name})


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def rider_pickup_sheets(request):
    rider = request.user.rider_profile
    sheets = rider.pickup_sheets.all()
    data = [{
        'sheet_number': s.sheet_number,
        'date': s.date,
        'status': s.pickup_status,
        'parcels': [{
            'customer': p.shipper.customer_name,
            'address': p.shipper.customer_pickup_address,
            'contact': p.shipper.customer_phone_number,
            'quantity': p.number_of_pieces,
            'weight': str(p.parcel_weight),
        } for p in s.parcels.all()]
    } for s in sheets]
    return Response(data)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def rider_delivery_sheets(request):
    rider = request.user.rider_profile
    sheets = DeliverySheet.objects.filter(rider=rider, sheet_status='Picked Up')
    data = [{
        'ds_number': s.ds_number,
        'tracking_number': s.tracking_number,
        'shipper': s.shipper.customer_name,
        'address': s.shipper.customer_pickup_address,
        'contact': s.shipper.customer_phone_number,
        'status': s.sheet_status,
        'parcels': [{'cn': p.cn, 'quantity': p.number_of_pieces, 'weight': str(p.parcel_weight), 'cod': str(p.cod)} for p in s.parcels.all()],
    } for s in sheets]
    return Response(data)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def scan_delivery_sheet(request, tracking_number):
    rider = request.user.rider_profile
    try:
        ds = DeliverySheet.objects.get(tracking_number=tracking_number)
    except DeliverySheet.DoesNotExist:
        return Response({'error': 'Invalid QR'}, status=404)

    if ds.rider_id != rider.id:
        return Response({'error': 'Not assigned to this rider'}, status=403)
    if ds.sheet_status != 'Pending':
        return Response({'error': 'Already scanned or inactive'}, status=409)

        from django.db import transaction
        with transaction.atomic():
            ds.sheet_status = 'Picked Up'
            ds.scanned_at = timezone.now()
            ds.save()
            ds.parcels.update(status='Out for Delivery')

    return Response({
        'ds_number': ds.ds_number,
        'tracking_number': ds.tracking_number,
        'shipper': ds.shipper.customer_name,
        'address': ds.shipper.customer_pickup_address,
        'contact': ds.shipper.customer_phone_number,
        'parcels': [{'cn': p.cn, 'quantity': p.number_of_pieces, 'weight': str(p.parcel_weight), 'cod': str(p.cod)} for p in ds.parcels.all()],
    })