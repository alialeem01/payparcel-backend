from django.contrib import admin
from unfold.admin import ModelAdmin
from unfold.contrib.filters.admin import ChoicesDropdownFilter
from .models import Branch

@admin.register(Branch)
class BranchAdmin(ModelAdmin):
    list_display = ('branch_name', 'contact_number', 'manager_name', 'status')
    search_fields = ('branch_name',)
    list_filter_submit = True
    list_filter = (
        ('status', ChoicesDropdownFilter),
    )