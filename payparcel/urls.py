import payparcel.admin_config
from django.contrib import admin
from django.urls import path, include
from parcels.views import track_parcel
from operations.views import track_pickup_sheet

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('parcels.urls')),
    path('api/customers/', include('customers.urls')),
    path('track/<str:cn>/', track_parcel, name='track_parcel'),
    path('track/pickupsheet/<str:sheet_number>/', track_pickup_sheet, name='track_pickup_sheet'),
]