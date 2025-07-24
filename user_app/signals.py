from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import User
from .models import MainArea

# [Az] to create main area for the user on regestration
@receiver(post_save, sender=User)
def create_main_area(sender, instance, created, **kwargs):
    if created:
        MainArea.objects.create(user=instance)
