from django.contrib import admin

def get_app_list(self, request, app_label=None):
    app_dict = self._build_app_dict(request)
    if not app_dict:
        return []

    all_models = []
    for app in app_dict.values():
        all_models.extend(app['models'])

    all_models.sort(key=lambda x: x['name'])

    merged_app = {
        'name': 'App',
        'app_label': 'app',
        'app_url': '#',
        'has_module_perms': True,
        'models': all_models,
    }

    return [merged_app]

admin.site.get_app_list = get_app_list.__get__(admin.site, type(admin.site))