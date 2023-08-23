from django.core.management.base import BaseCommand
from django.contrib.auth.models import User

class Command(BaseCommand):
    help = 'Anonymizes the database for public use'

    def handle(self, *args, **options):
        # Anonymize user data
        for user in User.objects.all():
            user.email = f"user_{user.id}@example.com"
            user.set_password("defaultPassword123!")
            user.save()

        self.stdout.write(self.style.SUCCESS('Successfully anonymized the database'))
