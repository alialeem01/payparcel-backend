from django.contrib import admin
from django.contrib.auth import get_user_model
from unfold.admin import ModelAdmin
from .models import Rider


@admin.register(Rider)
class RiderAdmin(ModelAdmin):
    list_display = ('name', 'phone_number', 'cnic_number', 'branch', 'is_active', 'created_at')
    search_fields = ('name', 'phone_number', 'cnic_number')
    list_filter = ('is_active',)
    fields = ('name', 'phone_number', 'cnic_number', 'cnic_front_image', 'cnic_back_image', 'branch', 'is_active', 'user')

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == 'user':
            User = get_user_model()
            linked_user_ids = Rider.objects.exclude(pk=request.resolver_match.kwargs.get('object_id')).values_list('user_id', flat=True)
            kwargs['queryset'] = User.objects.filter(is_staff=False).exclude(pk__in=linked_user_ids)
        return super().formfield_for_foreignkey(db_field, request, **kwargs)