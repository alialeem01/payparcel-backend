from django.conf import settings
from django.contrib import admin, messages
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User, Group
from django.contrib.auth.hashers import make_password
from django.shortcuts import render, redirect
from django.urls import path
from unfold.admin import ModelAdmin
from riders.models import Rider

admin.site.unregister(User)


@admin.register(User)
class CustomUserAdmin(UserAdmin, ModelAdmin):
    list_display = ('username', 'email', 'is_staff', 'is_active')
    list_filter = ('is_staff', 'is_active', 'groups')

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.username != settings.MASTER_ADMIN_USERNAME:
            qs = qs.exclude(username=settings.MASTER_ADMIN_USERNAME)
        from customers.models import Customer
        customer_usernames = Customer.objects.values_list('customer_user', flat=True)
        qs = qs.exclude(username__in=customer_usernames, is_staff=False)
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

    def get_urls(self):
        urls = super().get_urls()
        custom = [
            path('add/', self.admin_site.admin_view(self.custom_add_view), name='auth_user_add'),
        ]
        return custom + urls

    def custom_add_view(self, request):
        user_type = request.GET.get('type') or request.POST.get('type')
        groups = Group.objects.all()

        if request.method == 'POST' and user_type:
            username = request.POST.get('username', '').strip()
            password = request.POST.get('password', '')

            if not username or not password:
                self.message_user(request, 'Username and password are required.', level=messages.ERROR)
                return redirect(f'{request.path}?type={user_type}')

            if user_type == 'Rider':
                name = request.POST.get('name', '').strip()
                phone_number = request.POST.get('phone_number', '').strip()
                cnic_number = request.POST.get('cnic_number', '').strip()
                cnic_front_image = request.FILES.get('cnic_front_image')
                cnic_back_image = request.FILES.get('cnic_back_image')
                branch = request.POST.get('branch', '').strip()

                if not (name and phone_number and cnic_number and cnic_front_image and cnic_back_image):
                    self.message_user(request, 'All rider fields including both CNIC images are required.', level=messages.ERROR)
                    return redirect(f'{request.path}?type={user_type}')

                user = User.objects.create(username=username, password=make_password(password), is_staff=False)
                Rider.objects.create(
                    user=user, name=name, phone_number=phone_number, cnic_number=cnic_number,
                    cnic_front_image=cnic_front_image, cnic_back_image=cnic_back_image,
                    branch=branch, is_active=True,
                )
                self.message_user(request, f'Rider "{name}" created.')
                return redirect('admin:riders_rider_changelist')

            else:
                email = request.POST.get('email', '').strip()
                if not email:
                    self.message_user(request, 'Email is required.', level=messages.ERROR)
                    return redirect(f'{request.path}?type={user_type}')

                user = User.objects.create(
                    username=username, email=email, password=make_password(password), is_staff=True
                )
                try:
                    group = Group.objects.get(name=user_type)
                    user.groups.add(group)
                    if user_type == 'Admin':
                        user.is_superuser = True
                        user.save()
                except Group.DoesNotExist:
                    pass

                self.message_user(request, f'User "{username}" created.')
                return redirect('admin:auth_user_changelist')

        context = {
            **self.admin_site.each_context(request),
            'title': 'Create User',
            'groups': groups,
            'selected_type': user_type,
            'opts': self.model._meta,
        }
        return render(request, 'admin/auth/user/create_user.html', context)