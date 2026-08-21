from django.contrib import admin
from .models import Loadsheet

@admin.register(Loadsheet)
class LoadsheetAdmin(admin.ModelAdmin):
    list_display = ('loadsheet_no', 'customer', 'total_weight', 'total_consignee', 'total_pieces', 'total_cod', 'created_by', 'loadsheet_date')
    filter_horizontal = ('parcels',)
    readonly_fields = ('loadsheet_no', 'loadsheet_date')
    search_fields = ('loadsheet_no', 'customer__customer_name')