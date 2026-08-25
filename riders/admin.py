from django.contrib import admin
from unfold.admin import ModelAdmin
from .models import Rider


@admin.register(Rider)
class RiderAdmin(ModelAdmin):
    list_display = ('name', 'phone_number', 'branch', 'is_active', 'created_at')
    search_fields = ('name', 'phone_number')
    list_filter = ('is_active',)