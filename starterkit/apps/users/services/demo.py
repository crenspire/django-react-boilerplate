from django.contrib.auth import get_user_model
from django.db import transaction

from apps.users.domain.models import UserProfile
from apps.users.domain.roles import Role

User = get_user_model()

DEMO_PASSWORD = "budget-demo-2026"

DEMO_USERS = (
    ("client1", "Aisha", "Khan", Role.CLIENT),
    ("client2", "Bilal", "Ahmed", Role.CLIENT),
    ("manager1", "Sara", "Malik", Role.MANAGER),
    ("admin1", "Omar", "Raza", Role.ADMIN),
)


@transaction.atomic
def seed_demo_users() -> list[dict]:
    accounts = []
    for username, first_name, last_name, role in DEMO_USERS:
        user, _ = User.objects.get_or_create(username=username)
        user.first_name = first_name
        user.last_name = last_name
        user.email = f"{username}@example.com"
        user.is_active = True
        user.set_password(DEMO_PASSWORD)
        user.save()
        UserProfile.objects.update_or_create(user=user, defaults={"role": role})
        accounts.append({"username": username, "password": DEMO_PASSWORD, "role": role.label})
    return accounts
