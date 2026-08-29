from django.shortcuts import render, get_object_or_404
from .models import PickupSheet


def track_pickup_sheet(request, sheet_number):
    sheet = get_object_or_404(PickupSheet, sheet_number=sheet_number)
    context = {
        'sheet': sheet,
        'parcels': sheet.parcels.all(),
    }
    return render(request, 'tracking/track_pickup_sheet.html', context)


def print_pickup_sheet(request, sheet_number):
    sheet = get_object_or_404(PickupSheet, sheet_number=sheet_number)
    parcels = sheet.parcels.select_related('shipper').all()

    totals = {
        'count': parcels.count(),
        'quantity': sum(p.number_of_pieces or 0 for p in parcels),
        'weight': sum(float(p.parcel_weight or 0) for p in parcels),
        'cod': sum(float(p.cod or 0) for p in parcels),
    }

    context = {
        'sheet': sheet,
        'parcels': parcels,
        'totals': totals,
    }
    return render(request, 'tracking/print_pickup_sheet.html', context)

from .models import DeliverySheet

def print_delivery_sheet(request, tracking_number):
    ds = get_object_or_404(DeliverySheet, tracking_number=tracking_number)
    context = {'ds': ds, 'parcels': ds.parcels.all()}
    return render(request, 'tracking/print_delivery_sheet.html', context)