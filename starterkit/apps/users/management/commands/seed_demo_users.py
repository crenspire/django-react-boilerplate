from django.conf import settings
from django.core.management.base import BaseCommand, CommandError

from apps.users.services.demo import seed_demo_users


class Command(BaseCommand):
    help = "Create or reset the demo client, manager and admin accounts (development only)."

    def handle(self, *args, **options):
        if not settings.DEBUG:
            raise CommandError("Demo accounts use a shared password and are only created when DEBUG is on.")
        for account in seed_demo_users():
            self.stdout.write(f"{account['role']:<8} {account['username']:<10} {account['password']}")
