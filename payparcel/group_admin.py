import json
from django.contrib import admin
from django.contrib.auth.models import Group, Permission
from django.shortcuts import render, redirect, get_object_or_404
from unfold.admin import ModelAdmin

OPERATIONAL_APPS = ['customers', 'parcels', 'operations', 'invoices', 'locations']
RIDER_CUSTOM_PERMS = ['can_scan_delivery_sheet', 'can_scan_parcel_delivery']
EXCLUDED_APPS = ['admin', 'contenttypes', 'sessions', 'auth', 'loadsheets']


class CustomGroupAdmin(ModelAdmin):
    list_display = ('name',)

    def get_urls(self):
        from django.urls import path
        urls = super().get_urls()
        custom = [
            path('add/', self.admin_site.admin_view(self.custom_add_view), name='auth_group_add'),
            path('<int:object_id>/change/', self.admin_site.admin_view(self.custom_change_view), name='auth_group_change'),
        ]
        return custom + urls

    def _grouped_modules(self, selected_ids=None):
        selected_ids = selected_ids or set()
        perms = Permission.objects.select_related('content_type').exclude(
            content_type__app_label__in=EXCLUDED_APPS
        ).order_by('content_type__app_label', 'content_type__model', 'codename')

        grouped = {}
        for p in perms:
            app = p.content_type.app_label
            grouped.setdefault(app, {'view': [], 'write': [], 'custom': []})
            entry = {'id': p.id, 'codename': p.codename, 'name': p.name, 'checked': p.id in selected_ids}
            if p.codename.startswith('view_'):
                grouped[app]['view'].append(entry)
            elif p.codename in RIDER_CUSTOM_PERMS:
                grouped[app]['custom'].append(entry)
            else:
                grouped[app]['write'].append(entry)
        return grouped

    def _handle_post(self, request, group):
        name = request.POST.get('name', '').strip()
        if not name:
            self.message_user(request, 'Group name is required.', level='error')
            return None
        group.name = name
        group.save()
        perm_ids = request.POST.getlist('permissions')
        group.permissions.set(Permission.objects.filter(id__in=perm_ids))
        self.message_user(request, f'Group "{name}" saved.')
        return redirect('admin:auth_group_changelist')

    def custom_add_view(self, request):
        if request.method == 'POST':
            result = self._handle_post(request, Group())
            if result:
                return result
        context = {
            **self.admin_site.each_context(request),
            'title': 'Add Group',
            'group_name': '',
            'grouped_modules': self._grouped_modules(),
            'operational_apps': json.dumps(OPERATIONAL_APPS),
            'rider_perms': json.dumps(RIDER_CUSTOM_PERMS),
            'opts': self.model._meta,
        }
        return render(request, 'admin/auth/group/custom_form.html', context)

    def custom_change_view(self, request, object_id):
        group = get_object_or_404(Group, pk=object_id)
        if request.method == 'POST':
            result = self._handle_post(request, group)
            if result:
                return result
        selected_ids = set(group.permissions.values_list('id', flat=True))
        context = {
            **self.admin_site.each_context(request),
            'title': f'Edit Group - {group.name}',
            'group_name': group.name,
            'grouped_modules': self._grouped_modules(selected_ids),
            'operational_apps': json.dumps(OPERATIONAL_APPS),
            'rider_perms': json.dumps(RIDER_CUSTOM_PERMS),
            'opts': self.model._meta,
        }
        return render(request, 'admin/auth/group/custom_form.html', context)

    def has_add_permission(self, request):
        return request.user.is_superuser

    def has_change_permission(self, request, obj=None):
        return request.user.is_superuser

    def has_delete_permission(self, request, obj=None):
        return request.user.is_superuser


admin.site.unregister(Group)
admin.site.register(Group, CustomGroupAdmin)