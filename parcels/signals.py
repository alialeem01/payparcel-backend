from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import CustomerParcel

@receiver(post_save, sender=CustomerParcel)
def auto_create_pickup_sheet(sender, instance, created, **kwargs):
    if created:
        from operations.models import PickupSheet
        sheet = PickupSheet.objects.create(shipper=instance.shipper)
        sheet.parcels.add(instance)