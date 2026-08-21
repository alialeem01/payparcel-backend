from django.urls import path
from . import views

urlpatterns = [
    path('register/', views.register_customer, name='register_customer'),
    path('login/', views.login_customer, name='login_customer'),
]

from django.urls import path
from . import views

urlpatterns = [
    path('register/', views.register_customer, name='register_customer'),
    path('login/', views.login_customer, name='login_customer'),
    path('me/', views.get_current_customer, name='get_current_customer'),
]

path('update-profile/', views.update_customer_profile, name='update_customer_profile'),