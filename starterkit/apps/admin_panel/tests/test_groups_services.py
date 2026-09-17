from django.contrib.auth.models import Group, Permission
from django.core.exceptions import PermissionDenied
from django.db import IntegrityError
from django.http import Http404
from django.test import TestCase
from unittest import mock

from apps.admin_panel.dto.common import ListQueryDTO
from apps.admin_panel.dto.groups import GroupFormInputDTO
from apps.admin_panel.services import groups as group_services
from apps.admin_panel.tests.factories import GROUP_PERMS, make_staff, make_superuser, make_user


def query(**overrides) -> ListQueryDTO:
    values = {"search": "", "order_by": "", "page": 1, "page_size": 25}
    values.update(overrides)
    return ListQueryDTO(**values)


class GroupListPageTests(TestCase):
    def test_requires_view_permission(self):
        with self.assertRaises(PermissionDenied):
            group_services.get_group_list_page(actor=make_staff(), query=query())

    def test_counts_and_invalid_order(self):
        group = Group.objects.create(name="Editors")
        make_user("a").groups.add(group)
        make_user("b").groups.add(group)
        group.permissions.set(Permission.objects.all()[:3])

        props = group_services.get_group_list_page(actor=make_superuser(), query=query(order_by="bogus"))

        self.assertEqual(props["filters"]["order_by"], "name")
        self.assertEqual(props["groups"][0]["user_count"], 2)
        self.assertEqual(props["groups"][0]["permission_count"], 3)


class CreateGroupTests(TestCase):
    def setUp(self):
        self.root = make_superuser()

    def test_create_group_with_permissions(self):
        permission = Permission.objects.first()
        result = group_services.create_group(
            actor=self.root, data=GroupFormInputDTO(name="Editors", permission_ids=(permission.pk,))
        )
        self.assertTrue(result.success, result.errors)
        group = Group.objects.get(pk=result.group_id)
        self.assertEqual(list(group.permissions.all()), [permission])

    def test_duplicate_name_fails(self):
        Group.objects.create(name="Existing")
        result = group_services.create_group(
            actor=self.root, data=GroupFormInputDTO(name="Existing", permission_ids=())
        )
        self.assertFalse(result.success)
        self.assertIn("name", result.errors)

    def test_blank_name_fails(self):
        result = group_services.create_group(
            actor=self.root, data=GroupFormInputDTO(name="  ", permission_ids=())
        )
        self.assertIn("name", result.errors)

    def test_requires_add_permission(self):
        with self.assertRaises(PermissionDenied):
            group_services.create_group(
                actor=make_staff(), data=GroupFormInputDTO(name="Editors", permission_ids=())
            )

    def test_non_superuser_cannot_assign_permissions(self):
        staff = make_staff(perms=GROUP_PERMS)
        permission = Permission.objects.first()
        result = group_services.create_group(
            actor=staff, data=GroupFormInputDTO(name="Editors", permission_ids=(permission.pk,))
        )
        self.assertFalse(result.success)
        self.assertIn("permission_ids", result.errors)
        self.assertFalse(Group.objects.filter(name="Editors").exists())

    def test_integrity_error_race_is_reported_as_field_error(self):
        with mock.patch.object(Group, "save", side_effect=IntegrityError):
            result = group_services.create_group(
                actor=self.root, data=GroupFormInputDTO(name="Editors", permission_ids=())
            )
        self.assertIn("name", result.errors)


class UpdateGroupTests(TestCase):
    def setUp(self):
        self.root = make_superuser()
        self.group = Group.objects.create(name="OldName")

    def test_update_group_success(self):
        result = group_services.update_group(
            actor=self.root,
            group_id=self.group.pk,
            data=GroupFormInputDTO(name="NewName", permission_ids=()),
        )
        self.assertTrue(result.success, result.errors)
        self.group.refresh_from_db()
        self.assertEqual(self.group.name, "NewName")

    def test_non_superuser_can_rename_but_not_change_permissions(self):
        staff = make_staff(perms=GROUP_PERMS)
        permission = Permission.objects.first()

        renamed = group_services.update_group(
            actor=staff, group_id=self.group.pk, data=GroupFormInputDTO(name="Renamed", permission_ids=())
        )
        escalated = group_services.update_group(
            actor=staff,
            group_id=self.group.pk,
            data=GroupFormInputDTO(name="Renamed", permission_ids=(permission.pk,)),
        )

        self.assertTrue(renamed.success, renamed.errors)
        self.assertIn("permission_ids", escalated.errors)
        self.assertFalse(self.group.permissions.exists())

    def test_missing_group_raises_404(self):
        with self.assertRaises(Http404):
            group_services.update_group(
                actor=self.root, group_id=999_999, data=GroupFormInputDTO(name="x", permission_ids=())
            )


class DeleteGroupTests(TestCase):
    def test_delete_group_success(self):
        group = Group.objects.create(name="ToDelete")
        result = group_services.delete_group(actor=make_superuser(), group_id=group.pk)
        self.assertTrue(result.success)
        self.assertFalse(Group.objects.filter(pk=group.pk).exists())

    def test_requires_delete_permission(self):
        group = Group.objects.create(name="ToDelete")
        with self.assertRaises(PermissionDenied):
            group_services.delete_group(actor=make_staff(perms=("change_group",)), group_id=group.pk)
