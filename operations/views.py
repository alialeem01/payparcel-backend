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
    context = {
        'sheet': sheet,
        'parcels': sheet.parcels.all(),
    }
    return render(request, 'tracking/print_pickup_sheet.html', context)