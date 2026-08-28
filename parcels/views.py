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
        data = serializer.data
        try:
            narration = StatusNarration.objects.get(status=parcel.status)
            data['status_message'] = narration.narration
        except StatusNarration.DoesNotExist:
            data['status_message'] = ''
        return Response(data)
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

import openpyxl
from django.core.files.uploadedfile import InMemoryUploadedFile

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def bulk_book_orders(request):
    try:
        customer = Customer.objects.get(customer_user=request.user.username)
    except Customer.DoesNotExist:
        return Response({'error': 'Customer profile not found'}, status=404)

    file = request.FILES.get('file')
    if not file:
        return Response({'error': 'No file uploaded'}, status=400)

    wb = openpyxl.load_workbook(file)
    sheet = wb.active
    rows = list(sheet.iter_rows(min_row=2, values_only=True))  # skip header row

    if len(rows) > 100:
        return Response({'error': 'Bulk Booking Limit is 100'}, status=400)

    created = []
    errors = []
    for i, row in enumerate(rows, start=2):
        if not row or not row[0]:
            continue
        try:
            # Expected column order: Receiver Name, Receiver Phone, Alt Receiver Phone,
            # Order ID, Service Type, Destination City, Address, COD Amount, Product,
            # Instructions, Parcel Weight, Pcs
            parcel = CustomerParcel.objects.create(
                shipper=customer,
                consignee=row[0],
                consignee_phone=row[1],
                alternate_phone=row[2] or '',
                order_number=row[3] or '',
                service_type=row[4] or 'COD',
                destination=row[5],
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
    destination = request.GET.get('destination')
    status_filter = request.GET.get('status')
    active = request.GET.get('active')
    consignee_phone = request.GET.get('consignee_phone')
    date_from = request.GET.get('from')
    date_to = request.GET.get('to')

    if cn:
        qs = qs.filter(cn__icontains=cn)
    if service_type:
        qs = qs.filter(service_type=service_type)
    if destination:
        qs = qs.filter(destination__icontains=destination)
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
            'destination': p.destination,
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

from loadsheets.models import Loadsheet

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def loadsheet_list(request):
    try:
        customer = Customer.objects.get(customer_user=request.user.username)
    except Customer.DoesNotExist:
        return Response({'error': 'Customer profile not found'}, status=404)

    sheets = Loadsheet.objects.filter(customer=customer).order_by('-loadsheet_date')
    data = [{
        'loadsheet_no': ls.loadsheet_no,
        'customer': customer.customer_name,
        'total_weight': ls.total_weight,
        'total_consignee': ls.total_consignee,
        'total_pieces': ls.total_pieces,
        'total_cod': ls.total_cod,
        'created_by': ls.created_by,
        'loadsheet_date': ls.loadsheet_date,
    } for ls in sheets]

    return Response({'results': data})

from django.shortcuts import render, get_object_or_404
from .models import CustomerParcel, StatusNarration


def track_parcel(request, cn):
    parcel = get_object_or_404(CustomerParcel, cn=cn)
    narration = StatusNarration.objects.filter(status=parcel.status).first()
    context = {
        'parcel': parcel,
        'narration': narration.narration if narration else None,
    }
    return render(request, 'tracking/track_parcel.html', context)

from django.shortcuts import redirect

def confirm_pickup(request, cn):
    parcel = get_object_or_404(CustomerParcel, cn=cn)

    if request.method != 'POST':
        return render(request, 'tracking/track_parcel.html', {
            'parcel': parcel,
            'narration': None,
        })

    if not parcel.pickup_sheets.exists():
        return render(request, 'tracking/scan_result.html', {'success': False, 'message': 'Parcel is not assigned to a Pickup Sheet.'})

    if parcel.status != 'Ready for Pickup':
        return render(request, 'tracking/scan_result.html', {'success': False, 'message': 'Invalid or duplicate scan. This parcel is not pending pickup.'})

    parcel.status = 'Departed from Origin'
    parcel.save()
    return render(request, 'tracking/scan_result.html', {'success': True, 'message': f'Pickup confirmed for {parcel.cn}.'})