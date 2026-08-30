import payparcel.admin_config
from django.contrib import admin
from django.urls import path, include
from parcels.views import track_parcel
from operations.views import track_pickup_sheet, print_pickup_sheet, print_delivery_sheet
from riders.views import rider_login, rider_pickup_sheets, scan_delivery_sheet, rider_delivery_sheets
from operations.views import view_delivery_sheet
from riders.views import scan_parcel_delivery
import payparcel.group_admin
import payparcel.user_admin

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('parcels.urls')),
    path('api/customers/', include('customers.urls')),
    path('api/rider/login/', rider_login),
    path('api/rider/delivery-sheets/', rider_delivery_sheets),
    path('api/rider/scan-delivery/<str:tracking_number>/', scan_delivery_sheet),
    path('track/<str:cn>/', track_parcel, name='track_parcel'),
    path('track/pickupsheet/<str:sheet_number>/', track_pickup_sheet, name='track_pickup_sheet'),
    path('track/pickupsheet/<str:sheet_number>/print/', print_pickup_sheet, name='print_pickup_sheet'),
    path('track/deliverysheet/<str:tracking_number>/print/', print_delivery_sheet, name='print_delivery_sheet'),
    path('deliverysheet/<str:tracking_number>/view/', view_delivery_sheet, name='view_delivery_sheet'),    
    path('api/rider/scan-delivery-parcel/<str:cn>/', scan_parcel_delivery),
]