from django.conf import settings
from django.core.management import call_command
from django.core.management.base import BaseCommand, CommandError

from apps.budgets.services.demo import seed_demo_requests


class Command(BaseCommand):
    help = "Create demo accounts for every role and a set of budget requests (development only)."

    def handle(self, *args, **options):
        if not settings.DEBUG:
            raise CommandError("Demo data is only created when DEBUG is on.")
        call_command("seed_demo_users", stdout=self.stdout)
        created = seed_demo_requests()
        self.stdout.write(self.style.SUCCESS(f"Created {created} demo budget requests."))
