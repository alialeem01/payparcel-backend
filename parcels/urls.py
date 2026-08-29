from django.urls import path
from . import views

urlpatterns = [
    path('orders/', views.list_my_orders, name='list_my_orders'),
    path('orders/book/', views.book_order, name='book_order'),
    path('dashboard-summary/', views.dashboard_summary, name='dashboard_summary'),
    path('orders/bulk-book/', views.bulk_book_orders, name='bulk_book_orders'),
    path('reports/', views.parcel_report, name='parcel_report'),
]