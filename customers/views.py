from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import authenticate
from .serializers import RegisterSerializer

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