import payparcel.admin_config
from django.contrib import admin
from django.urls import path, include
from parcels.views import track_parcel, confirm_pickup
from operations.views import track_pickup_sheet, print_pickup_sheet

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('parcels.urls')),
    path('api/customers/', include('customers.urls')),
    path('track/<str:cn>/', track_parcel, name='track_parcel'),
    path('track/<str:cn>/confirm-pickup/', confirm_pickup, name='confirm_pickup'),
    path('track/pickupsheet/<str:sheet_number>/', track_pickup_sheet, name='track_pickup_sheet'),
    path('track/pickupsheet/<str:sheet_number>/print/', print_pickup_sheet, name='print_pickup_sheet'),
]