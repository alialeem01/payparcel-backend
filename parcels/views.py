from rest_framework import serializers
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.shortcuts import render, redirect, get_object_or_404
from django.db.models import Sum, Count
from customers.models import Customer
from .models import CustomerParcel
from .serializers import TrackingSerializer


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
                  'city', 'cod', 'parcel_weight', 'number_of_pieces',
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


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def dashboard_summary(request):
    try:
        customer = Customer.objects.get(customer_user=request.user.username)
    except Customer.DoesNotExist:
        return Response({'error': 'Customer profile not found'}, status=404)

    qs = CustomerParcel.objects.filter(shipper=customer)

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
            'ready_for_pickup': count_amount('Ready for Pickup'),
            'out_for_delivery': count_amount('Out for Delivery'),
            'ready_to_return': count_amount('Returned'),
            'rts': count_amount('Returned'),
        },
        'chart': list(
            qs.values('created_at__date').annotate(count=Count('id')).order_by('created_at__date')
        ),
    }
    return Response(data)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def bulk_book_orders(request):
    import openpyxl
    try:
        customer = Customer.objects.get(customer_user=request.user.username)
    except Customer.DoesNotExist:
        return Response({'error': 'Customer profile not found'}, status=404)

    file = request.FILES.get('file')
    if not file:
        return Response({'error': 'No file uploaded'}, status=400)

    wb = openpyxl.load_workbook(file)
    sheet = wb.active
    rows = list(sheet.iter_rows(min_row=2, values_only=True))

    if len(rows) > 100:
        return Response({'error': 'Bulk Booking Limit is 100'}, status=400)

    created = []
    errors = []
    for i, row in enumerate(rows, start=2):
        if not row or not row[0]:
            continue
        try:
            parcel = CustomerParcel.objects.create(
                shipper=customer,
                consignee=row[0],
                consignee_phone=row[1],
                alternate_phone=row[2] or '',
                order_number=row[3] or '',
                service_type=row[4] or 'COD',
                city=row[5],
                address=row[6],
                cod=row[7] or 0,
                product=row[8] or '',
                instructions=row[9] or '',
                parcel_weight=row[10] or 0,
                number_of_pieces=row[11] or 1,
            )
            created.append(parcel.cn)
        except Exception as e:
            errors.append({'row': i, 'error': str(e)})

    return Response({'created': created, 'errors': errors, 'total_created': len(created)}, status=201)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def parcel_report(request):
    try:
        customer = Customer.objects.get(customer_user=request.user.username)
    except Customer.DoesNotExist:
        return Response({'error': 'Customer profile not found'}, status=404)

    qs = CustomerParcel.objects.filter(shipper=customer)

    cn = request.GET.get('cn')
    service_type = request.GET.get('service_type')
    city = request.GET.get('city')
    status_filter = request.GET.get('status')
    active = request.GET.get('active')
    consignee_phone = request.GET.get('consignee_phone')
    date_from = request.GET.get('from')
    date_to = request.GET.get('to')

    if cn:
        qs = qs.filter(cn__icontains=cn)
    if service_type:
        qs = qs.filter(service_type=service_type)
    if city:
        qs = qs.filter(city__icontains=city)
    if status_filter:
        qs = qs.filter(status=status_filter)
    if active:
        qs = qs.filter(active=active)
    if consignee_phone:
        qs = qs.filter(consignee_phone__icontains=consignee_phone)
    if date_from:
        qs = qs.filter(created_at__gte=date_from)
    if date_to:
        qs = qs.filter(created_at__lte=date_to)

    data = []
    total_weight = 0
    total_pieces = 0
    for p in qs:
        total_weight += float(p.parcel_weight or 0)
        total_pieces += p.number_of_pieces or 0
        data.append({
            'cn': p.cn,
            'shipper_name': customer.customer_name,
            'shipment_date': p.shipment_date,
            'service_type': p.service_type,
            'consignee': p.consignee,
            'consignee_phone': p.consignee_phone,
            'city': p.city,
            'status': p.status,
            'address': p.address,
            'parcel_weight': float(p.parcel_weight or 0),
            'pieces': p.number_of_pieces,
            'product': p.product,
        })

    return Response({
        'results': data,
        'total_parcels': qs.count(),
        'total_weight': total_weight,
        'total_pieces': total_pieces,
    })


def track_parcel(request, cn):
    parcel = get_object_or_404(CustomerParcel, cn=cn)
    context = {'parcel': parcel}
    return render(request, 'tracking/track_parcel.html', context)
