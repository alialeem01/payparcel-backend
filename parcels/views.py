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