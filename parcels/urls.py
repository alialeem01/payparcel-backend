from django.urls import path
from . import views

urlpatterns = [
    path('track/<str:cn>/', views.track_parcel, name='track_parcel'),
]