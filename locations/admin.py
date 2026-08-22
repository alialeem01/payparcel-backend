from django.contrib import admin
from .models import Destination, Branch

@admin.register(Destination)
class DestinationAdmin(admin.ModelAdmin):
    list_display = ('name', 'short_name', 'location', 'zone', 'date', 'status')
    search_fields = ('name', 'short_name')
    list_filter = ('status', 'zone')
    change_form_template = 'admin/locations/destination/change_form.html'
    add_form_template = 'admin/locations/destination/change_form.html'
    fields = ('name', 'short_name', 'zone', 'status', 'location')

@admin.register(Branch)
class BranchAdmin(admin.ModelAdmin):
    list_display = ('branch_name', 'contact_number', 'manager_name', 'status')
    search_fields = ('branch_name',)
    list_filter = ('status',)