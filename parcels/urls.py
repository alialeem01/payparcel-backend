from django.urls import path
from . import views

urlpatterns = [
    path('track/<str:cn>/', views.track_parcel, name='track_parcel'),
]

from django.urls import path
from . import views

urlpatterns = [
    path('track/<str:cn>/', views.track_parcel, name='track_parcel'),
    path('orders/', views.list_my_orders, name='list_my_orders'),
]