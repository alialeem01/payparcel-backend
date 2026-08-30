from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User
from unfold.admin import ModelAdmin

admin.site.unregister(User)


@admin.register(User)
class CustomUserAdmin(UserAdmin, ModelAdmin):
    list_display = ('username', 'email', 'is_staff', 'is_active')
    list_filter = ('is_staff', 'is_active', 'groups')