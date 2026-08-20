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