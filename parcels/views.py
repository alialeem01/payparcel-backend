from rest_framework import serializers
from customers.models import Customer
from rest_framework.decorators import api_view
from rest_framework.response import Response
from .models import CustomerParcel
from .serializers import TrackingSerializer

@api_view(['GET'])
def track_parcel(request, cn):
    try:
        parcel = CustomerParcel.objects.get(cn=cn)
        serializer = TrackingSerializer(parcel)
        return Response(serializer.data)
    except CustomerParcel.DoesNotExist:
        return Response({'error': 'Tracking ID not found'}, status=404)


from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import permission_classes
from customers.models import Customer

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def list_my_orders(request):
    try:
        customer = Customer.objects.get(customer_user=request.user.username)
        orders = CustomerParcel.objects.filter(shipper=customer).order_by('-created_at')
        serializer = TrackingSerializer(orders, many=True)
        return Response(serializer.data)
    except Customer.DoesNotExist:
        return Response({'error': 'Customer profile not found'}, status=404)

class BookOrderSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomerParcel
        fields = ['consignee', 'consignee_phone', 'alternate_phone', 'address',
                   'destination', 'cod', 'parcel_weight', 'number_of_pieces',
                   'service_type', 'product', 'instructions', 'flyer_size']

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def book_order(request):
    try:
        customer = Customer.objects.get(customer_user=request.user.username)
    except Customer.DoesNotExist:
        return Response({'error': 'Customer profile not found'}, status=404)

    serializer = BookOrderSerializer(data=request.data)
    if serializer.is_valid():
        parcel = serializer.save(shipper=customer)
        return Response({'message': 'Order booked successfully', 'cn': parcel.cn}, status=201)
    return Response(serializer.errors, status=400)

from django.db.models import Sum, Count, Q
from datetime import datetime

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def dashboard_summary(request):
    try:
        customer = Customer.objects.get(customer_user=request.user.username)
    except Customer.DoesNotExist:
        return Response({'error': 'Customer profile not found'}, status=404)

    qs = CustomerParcel.objects.filter(shipper=customer)

    # Optional date filtering
    date_from = request.GET.get('from')
    date_to = request.GET.get('to')
    if date_from:
        qs = qs.filter(created_at__gte=date_from)
    if date_to:
        qs = qs.filter(created_at__lte=date_to)

    def count_amount(status_filter):
        filtered = qs.filter(status=status_filter)
        return {
            'count': filtered.count(),
            'amount': float(filtered.aggregate(total=Sum('cod'))['total'] or 0)
        }

    data = {
        'financial': {
            'total_cod': float(qs.aggregate(t=Sum('cod'))['t'] or 0),
            'cod_delivered_return': float(qs.filter(status__in=['Delivered', 'Returned']).aggregate(t=Sum('cod'))['t'] or 0),
            'total_dc_flyer_charges': float(qs.aggregate(t=Sum('delivery_charge') + Sum('flyer_charges'))['t'] or 0) if qs.exists() else 0,
            'delivery_flyer_charges': float(qs.aggregate(t=Sum('delivery_charge'))['t'] or 0),
            'paid_amount': float(qs.filter(tpl_payment_status='Paid').aggregate(t=Sum('net_total'))['t'] or 0),
            'total_balance_payment': float(qs.filter(tpl_payment_status='Unpaid').aggregate(t=Sum('net_total'))['t'] or 0),
        },
        'orders': {
            'total_active': count_amount('Order'),
            'failed_attempt': count_amount('Parcel Not Available'),
            'pending': count_amount('Order'),
            'delivered': count_amount('Delivered'),
            'not_arrived': count_amount('Order'),
            'arrived': count_amount('Picked'),
            'ready_to_return': count_amount('Returned'),
            'rts': count_amount('Returned'),
        },
        'chart': list(
            qs.values('created_at__date').annotate(count=Count('id')).order_by('created_at__date')
        ),
    }
    return Response(data)