from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import User
from .models import Traveler

@receiver(post_save, sender=User)
def create_traveler(sender, instance, created, **kwargs):
    """
    Signal to automatically create a Traveler instance when a User is created.
    """
    if created:
        Traveler.objects.create(user=instance)

@receiver(post_save, sender=User)
def save_traveler(sender, instance, **kwargs):
    """
    Signal to save the Traveler instance when the User is saved.
    """
    try:
        instance.traveler.save()
    except Traveler.DoesNotExist:
        # In case traveler doesn't exist for some reason, create it
        Traveler.objects.create(user=instance)