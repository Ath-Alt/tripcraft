from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from admin_app.models import Traveler  # Replace 'your_app' with your actual app name


class Command(BaseCommand):
    help = 'Create Traveler profiles for any existing users that do not have one'

    def handle(self, *args, **options):
        users_without_travelers = 0
        for user in User.objects.all():
            try:
                # Check if the user has a traveler profile
                _ = user.traveler
            except Traveler.DoesNotExist:
                # Create traveler profile if it doesn't exist
                Traveler.objects.create(user=user)
                users_without_travelers += 1
                self.stdout.write(f"Created Traveler profile for user: {user.username}")

        if users_without_travelers == 0:
            self.stdout.write(self.style.SUCCESS('All users already have Traveler profiles'))
        else:
            self.stdout.write(
                self.style.SUCCESS(f'Successfully created {users_without_travelers} Traveler profiles')
            )