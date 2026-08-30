from django.contrib import admin

CUSTOM_ORDER = [
    'customer',       # 01 Customers
    'customerparcel',  # 03 Customer Parcels
    'pickupsheet',     # 03 Pickup Sheet
    'deliverysheet',   # 04 Delivery Sheet
    'invoice',         # 05 Customer Payment Invoices
    'branch',          # 06 Branches
    'Groups',          # 07 Groups
    'Users',           # 08 Users
]

def get_app_list(self, request, app_label=None):
    app_dict = self._build_app_dict(request)
    if not app_dict:
        return []

    all_models = []
    for app in app_dict.values():
        all_models.extend(app['models'])

    def sort_key(model):
        object_name = model['object_name'].lower()
        if object_name in CUSTOM_ORDER:
            return CUSTOM_ORDER.index(object_name)
        return 999

    all_models.sort(key=sort_key)

    merged_app = {
        'name': '',
        'app_label': 'app',
        'app_url': '#',
        'has_module_perms': True,
        'models': all_models,
    }

    return [merged_app]

admin.site.get_app_list = get_app_list.__get__(admin.site, type(admin.site))