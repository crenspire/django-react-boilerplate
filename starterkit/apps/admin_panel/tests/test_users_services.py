from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.core.exceptions import PermissionDenied
from django.db import IntegrityError
from django.http import Http404
from django.test import TestCase
from unittest import mock

from apps.admin_panel.dto.common import ListQueryDTO
from apps.admin_panel.dto.users import UserFormInputDTO
from apps.admin_panel.services import users as user_services
from apps.admin_panel.tests.factories import (
    STRONG_PASSWORD,
    USER_PERMS,
    make_staff,
    make_superuser,
    make_user,
)

User = get_user_model()


def form(**overrides) -> UserFormInputDTO:
    values = {
        "username": "newuser",
        "email": "new@example.com",
        "first_name": "New",
        "last_name": "User",
        "is_staff": False,
        "is_superuser": False,
        "is_active": True,
        "group_ids": (),
        "password": STRONG_PASSWORD,
    }
    values.update(overrides)
    return UserFormInputDTO(**values)


def form_for(user, **overrides) -> UserFormInputDTO:
    values = {
        "username": user.username,
        "email": user.email,
        "first_name": user.first_name,
        "last_name": user.last_name,
        "is_staff": user.is_staff,
        "is_superuser": user.is_superuser,
        "is_active": user.is_active,
        "group_ids": tuple(user.groups.values_list("pk", flat=True)),
        "password": "",
    }
    values.update(overrides)
    return UserFormInputDTO(**values)


def query(**overrides) -> ListQueryDTO:
    values = {"search": "", "order_by": "", "page": 1, "page_size": 25}
    values.update(overrides)
    return ListQueryDTO(**values)


class UserListPageTests(TestCase):
    def setUp(self):
        self.root = make_superuser()

    def test_requires_view_permission(self):
        with self.assertRaises(PermissionDenied):
            user_services.get_user_list_page(actor=make_staff(), query=query())

    def test_invalid_order_falls_back_to_default(self):
        props = user_services.get_user_list_page(actor=self.root, query=query(order_by="password"))
        self.assertEqual(props["filters"]["order_by"], "username")

    def test_out_of_range_page_is_clamped(self):
        for i in range(3):
            make_user(f"user{i}")
        props = user_services.get_user_list_page(actor=self.root, query=query(page=99, page_size=2))
        self.assertEqual(props["pagination"], {"page": 2, "page_size": 2, "total": 4, "total_pages": 2})

    def test_page_size_is_clamped(self):
        props = user_services.get_user_list_page(actor=self.root, query=query(page_size=10_000))
        self.assertEqual(props["pagination"]["page_size"], 100)

    def test_rows_carry_per_user_capabilities(self):
        staff = make_staff("manager", perms=USER_PERMS)
        make_user("regular")
        rows = {
            row["username"]: row
            for row in user_services.get_user_list_page(actor=staff, query=query())["users"]
        }
        self.assertTrue(rows["regular"]["can_edit"])
        self.assertFalse(rows["root"]["can_edit"])
        self.assertFalse(rows["manager"]["can_delete"])


class CreateUserTests(TestCase):
    def setUp(self):
        self.root = make_superuser()

    def test_create_user_success(self):
        group = Group.objects.create(name="Editors")
        result = user_services.create_user(actor=self.root, data=form(group_ids=(group.pk,)))

        self.assertTrue(result.success, result.errors)
        user = User.objects.get(pk=result.user_id)
        self.assertTrue(user.check_password(STRONG_PASSWORD))
        self.assertEqual(list(user.groups.all()), [group])

    def test_requires_add_permission(self):
        with self.assertRaises(PermissionDenied):
            user_services.create_user(actor=make_staff(perms=("change_user",)), data=form())

    def test_duplicate_username_fails(self):
        make_user("existing")
        result = user_services.create_user(actor=self.root, data=form(username="existing"))
        self.assertFalse(result.success)
        self.assertIn("username", result.errors)
        self.assertEqual(result.page_props["errors"], result.errors)

    def test_invalid_username_and_email_fail_model_validation(self):
        result = user_services.create_user(
            actor=self.root, data=form(username="bad name!", email="not-an-email")
        )
        self.assertFalse(result.success)
        self.assertIn("username", result.errors)
        self.assertIn("email", result.errors)

    def test_password_is_required(self):
        result = user_services.create_user(actor=self.root, data=form(password=""))
        self.assertEqual(result.errors["password"], ["This field is required."])

    def test_weak_password_is_rejected(self):
        result = user_services.create_user(actor=self.root, data=form(password="1"))
        self.assertFalse(result.success)
        self.assertIn("password", result.errors)
        self.assertFalse(User.objects.filter(username="newuser").exists())

    def test_password_is_never_echoed(self):
        result = user_services.create_user(actor=self.root, data=form(username=""))
        self.assertEqual(result.page_props["form"]["password"], "")

    def test_non_superuser_cannot_grant_privileges(self):
        staff = make_staff(perms=USER_PERMS)
        group = Group.objects.create(name="Admins")

        result = user_services.create_user(
            actor=staff, data=form(is_staff=True, is_superuser=True, group_ids=(group.pk,))
        )

        self.assertFalse(result.success)
        self.assertEqual(set(result.errors), {"is_staff", "is_superuser", "group_ids"})
        self.assertFalse(User.objects.filter(username="newuser").exists())

    def test_non_superuser_can_create_plain_user(self):
        result = user_services.create_user(actor=make_staff(perms=USER_PERMS), data=form())
        self.assertTrue(result.success, result.errors)

    def test_integrity_error_race_is_reported_as_field_error(self):
        with mock.patch.object(User, "save", side_effect=IntegrityError):
            result = user_services.create_user(actor=self.root, data=form())
        self.assertFalse(result.success)
        self.assertIn("username", result.errors)

    def test_failed_group_assignment_rolls_back_user(self):
        with mock.patch(
            "apps.admin_panel.selectors.groups.groups_by_ids", side_effect=IntegrityError
        ):
            result = user_services.create_user(actor=self.root, data=form())
        self.assertFalse(result.success)
        self.assertFalse(User.objects.filter(username="newuser").exists())


class UpdateUserTests(TestCase):
    def setUp(self):
        self.root = make_superuser()
        self.target = make_user("target", email="target@example.com")

    def test_update_user_success_keeps_password_when_blank(self):
        result = user_services.update_user(
            actor=self.root, user_id=self.target.pk, data=form_for(self.target, email="new@example.com")
        )
        self.assertTrue(result.success, result.errors)
        self.target.refresh_from_db()
        self.assertEqual(self.target.email, "new@example.com")
        self.assertTrue(self.target.check_password(STRONG_PASSWORD))

    def test_update_sets_new_password(self):
        new_password = "an0ther-Strong-one"
        result = user_services.update_user(
            actor=self.root, user_id=self.target.pk, data=form_for(self.target, password=new_password)
        )
        self.assertTrue(result.success, result.errors)
        self.target.refresh_from_db()
        self.assertTrue(self.target.check_password(new_password))

    def test_update_rejects_weak_password(self):
        result = user_services.update_user(
            actor=self.root, user_id=self.target.pk, data=form_for(self.target, password="123")
        )
        self.assertIn("password", result.errors)

    def test_missing_user_raises_404(self):
        with self.assertRaises(Http404):
            user_services.update_user(actor=self.root, user_id=999_999, data=form())

    def test_staff_cannot_promote_themselves(self):
        staff = make_staff("climber", perms=USER_PERMS)
        with self.assertRaises(PermissionDenied):
            user_services.update_user(
                actor=staff, user_id=staff.pk, data=form_for(staff, is_superuser=True)
            )
        staff.refresh_from_db()
        self.assertFalse(staff.is_superuser)

    def test_staff_cannot_promote_plain_user(self):
        staff = make_staff("manager", perms=USER_PERMS)
        result = user_services.update_user(
            actor=staff, user_id=self.target.pk, data=form_for(self.target, is_staff=True)
        )
        self.assertFalse(result.success)
        self.assertIn("is_staff", result.errors)
        self.target.refresh_from_db()
        self.assertFalse(self.target.is_staff)

    def test_staff_cannot_change_group_membership(self):
        staff = make_staff("manager", perms=USER_PERMS)
        group = Group.objects.create(name="Admins")
        result = user_services.update_user(
            actor=staff, user_id=self.target.pk, data=form_for(self.target, group_ids=(group.pk,))
        )
        self.assertIn("group_ids", result.errors)

    def test_staff_can_edit_profile_of_plain_user(self):
        staff = make_staff("manager", perms=USER_PERMS)
        result = user_services.update_user(
            actor=staff, user_id=self.target.pk, data=form_for(self.target, first_name="Ada")
        )
        self.assertTrue(result.success, result.errors)

    def test_superuser_cannot_lock_themselves_out(self):
        result = user_services.update_user(
            actor=self.root,
            user_id=self.root.pk,
            data=form_for(self.root, is_active=False, is_staff=False, is_superuser=False),
        )
        self.assertFalse(result.success)
        self.assertEqual(set(result.errors), {"is_active", "is_staff", "is_superuser"})

    def test_failed_update_keeps_stored_username_in_header(self):
        result = user_services.update_user(
            actor=self.root, user_id=self.target.pk, data=form_for(self.target, username="")
        )
        self.assertEqual(result.page_props["user"], {"id": self.target.pk, "username": "target"})
        self.assertEqual(result.page_props["form"]["username"], "")


class EditPageTests(TestCase):
    def test_edit_page_hides_delete_for_own_account(self):
        root = make_superuser()
        props = user_services.get_user_edit_page(actor=root, user_id=root.pk)
        self.assertFalse(props["can"]["delete"])
        self.assertTrue(props["can"]["grant_privileges"])

    def test_non_superuser_cannot_open_privileged_account(self):
        staff = make_staff(perms=USER_PERMS)
        with self.assertRaises(PermissionDenied):
            user_services.get_user_edit_page(actor=staff, user_id=make_superuser().pk)


class DeleteUserTests(TestCase):
    def setUp(self):
        self.root = make_superuser()

    def test_delete_user_success(self):
        target = make_user("todelete")
        result = user_services.delete_user(actor=self.root, user_id=target.pk)
        self.assertTrue(result.success)
        self.assertFalse(User.objects.filter(pk=target.pk).exists())

    def test_cannot_delete_own_account(self):
        result = user_services.delete_user(actor=self.root, user_id=self.root.pk)
        self.assertFalse(result.success)
        self.assertTrue(User.objects.filter(pk=self.root.pk).exists())

    def test_staff_cannot_delete_superuser(self):
        staff = make_staff(perms=USER_PERMS)
        result = user_services.delete_user(actor=staff, user_id=self.root.pk)
        self.assertFalse(result.success)
        self.assertTrue(User.objects.filter(pk=self.root.pk).exists())

    def test_requires_delete_permission(self):
        with self.assertRaises(PermissionDenied):
            user_services.delete_user(actor=make_staff(), user_id=make_user("x").pk)
