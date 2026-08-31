from django.conf import settings
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User
from unfold.admin import ModelAdmin

admin.site.unregister(User)


@admin.register(User)
class CustomUserAdmin(UserAdmin, ModelAdmin):
    list_display = ('username', 'email', 'is_staff', 'is_active')
    list_filter = ('is_staff', 'is_active', 'groups')

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.username != settings.MASTER_ADMIN_USERNAME:
            qs = qs.exclude(username=settings.MASTER_ADMIN_USERNAME)
        return qs

    def has_change_permission(self, request, obj=None):
        if obj and obj.username == settings.MASTER_ADMIN_USERNAME and request.user.username != settings.MASTER_ADMIN_USERNAME:
            return False
        if obj and obj.is_superuser and not request.user.is_superuser:
            return False
        return super().has_change_permission(request, obj)

    def has_delete_permission(self, request, obj=None):
        if obj and obj.username == settings.MASTER_ADMIN_USERNAME:
            return False
        return super().has_delete_permission(request, obj)