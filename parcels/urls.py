from django.urls import path
from . import views

urlpatterns = [
    path('track/<str:cn>/', views.track_parcel, name='track_parcel'),
    path('orders/', views.list_my_orders, name='list_my_orders'),
    path('orders/book/', views.book_order, name='book_order'),
]

path('dashboard-summary/', views.dashboard_summary, name='dashboard_summary'),