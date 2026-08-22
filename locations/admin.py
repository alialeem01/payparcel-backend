from django.contrib import admin
from .models import Destination, Branch

@admin.register(Destination)
class DestinationAdmin(admin.ModelAdmin):
    list_display = ('name', 'customer', 'short_name', 'location', 'zone', 'date', 'status')
    search_fields = ('city_name',)
    list_filter = ('status', 'zone')

@admin.register(Branch)
class BranchAdmin(admin.ModelAdmin):
    list_display = ('branch_name', 'city', 'contact_number', 'manager_name', 'status')
    search_fields = ('branch_name', 'city__city_name')
    list_filter = ('status', 'city')