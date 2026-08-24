from django.contrib import admin
from unfold.admin import ModelAdmin
from unfold.contrib.filters.admin import ChoicesDropdownFilter
from .models import Destination, Branch


@admin.register(Destination)
class DestinationAdmin(ModelAdmin):
    list_display = ('name', 'short_name', 'location', 'zone', 'date', 'status')
    search_fields = ('name', 'short_name')
    list_filter_submit = True
    list_filter = (
        ('status', ChoicesDropdownFilter),
        ('zone', ChoicesDropdownFilter),
    )
    change_form_template = 'admin/locations/destination/change_form.html'
    add_form_template = 'admin/locations/destination/change_form.html'
    fields = ('name', 'address', 'short_name', 'zone', 'status', 'location')


@admin.register(Branch)
class BranchAdmin(ModelAdmin):
    list_display = ('branch_name', 'contact_number', 'manager_name', 'status')
    search_fields = ('branch_name',)
    list_filter_submit = True
    list_filter = (
        ('status', ChoicesDropdownFilter),
    )