from decimal import Decimal

from django.core.exceptions import PermissionDenied
from django.http import Http404
from django.test import TestCase

from apps.budgets.domain.models import BudgetRequest, Status
from apps.budgets.dto.budget_requests import BudgetRequestInputDTO, ReviewInputDTO
from apps.budgets.services import budget_requests as services
from apps.budgets.tests.factories import make_request, make_superuser, make_user
from apps.users.selectors.roles import Role


def form(**overrides):
    values = {"title": "Laptops", "amount": "1500.00", "justification": "Old hardware."}
    values.update(overrides)
    return BudgetRequestInputDTO(**values)


class WorkflowTestCase(TestCase):
    def setUp(self):
        self.client_user = make_user("client", role=Role.CLIENT)
        self.other_client = make_user("other", role=Role.CLIENT)
        self.manager = make_user("manager", role=Role.MANAGER)
        self.admin = make_user("admin", role=Role.ADMIN)
        self.root = make_superuser()

    def reload(self, request):
        return BudgetRequest.objects.get(pk=request.pk)


class CreateRequestTests(WorkflowTestCase):
    def test_client_creates_a_pending_request(self):
        result = services.create_request(actor=self.client_user, data=form())
        self.assertTrue(result.success)
        request = BudgetRequest.objects.get(pk=result.request_id)
        self.assertEqual(request.requester, self.client_user)
        self.assertEqual(request.status, Status.PENDING)
        self.assertEqual(request.amount, Decimal("1500.00"))

    def test_invalid_input_creates_nothing(self):
        result = services.create_request(actor=self.client_user, data=form(amount="-1", title=""))
        self.assertFalse(result.success)
        self.assertEqual(set(result.errors), {"amount", "title"})
        self.assertFalse(BudgetRequest.objects.exists())

    def test_other_roles_cannot_create(self):
        for actor in (self.manager, self.admin, self.root):
            with self.subTest(actor=actor.username), self.assertRaises(PermissionDenied):
                services.create_request(actor=actor, data=form())
        self.assertFalse(BudgetRequest.objects.exists())


class UpdateAndWithdrawTests(WorkflowTestCase):
    def setUp(self):
        super().setUp()
        self.request = make_request(self.client_user)

    def test_owner_updates_a_pending_request(self):
        result = services.update_request(
            actor=self.client_user, request_id=self.request.pk, data=form(title="Monitors", amount="99.9")
        )
        self.assertTrue(result.success)
        request = self.reload(self.request)
        self.assertEqual((request.title, request.amount), ("Monitors", Decimal("99.90")))

    def test_owner_withdraws_a_pending_request(self):
        result = services.withdraw_request(actor=self.client_user, request_id=self.request.pk)
        self.assertTrue(result.success)
        self.assertEqual(self.reload(self.request).status, Status.WITHDRAWN)

    def test_reviewed_requests_are_immutable_for_the_owner(self):
        for status in (Status.APPROVED, Status.REJECTED, Status.WITHDRAWN):
            request = make_request(self.client_user, status=status, title="Original")
            with self.subTest(status=status):
                update = services.update_request(actor=self.client_user, request_id=request.pk, data=form())
                withdraw = services.withdraw_request(actor=self.client_user, request_id=request.pk)
                self.assertFalse(update.success)
                self.assertFalse(withdraw.success)
                self.assertEqual(update.errors, {"non_field_errors": [services.ALREADY_REVIEWED_ERROR]})
                reloaded = self.reload(request)
                self.assertEqual((reloaded.status, reloaded.title), (status, "Original"))

    def test_other_clients_get_404_so_ids_are_not_disclosed(self):
        with self.assertRaises(Http404):
            services.update_request(actor=self.other_client, request_id=self.request.pk, data=form())
        with self.assertRaises(Http404):
            services.withdraw_request(actor=self.other_client, request_id=self.request.pk)
        self.assertEqual(self.reload(self.request).status, Status.PENDING)

    def test_managers_and_admins_cannot_change_a_clients_request(self):
        for actor in (self.manager, self.admin):
            with self.subTest(actor=actor.username):
                with self.assertRaises(PermissionDenied):
                    services.update_request(actor=actor, request_id=self.request.pk, data=form(title="Hacked"))
                with self.assertRaises(PermissionDenied):
                    services.withdraw_request(actor=actor, request_id=self.request.pk)
        self.assertEqual(self.reload(self.request).title, "New laptops")

    def test_invalid_update_changes_nothing(self):
        result = services.update_request(actor=self.client_user, request_id=self.request.pk, data=form(amount="x"))
        self.assertEqual(set(result.errors), {"amount"})
        self.assertEqual(self.reload(self.request).amount, Decimal("100.00"))

    def test_missing_request_is_404(self):
        with self.assertRaises(Http404):
            services.withdraw_request(actor=self.client_user, request_id=999_999)


class ReviewRequestTests(WorkflowTestCase):
    def setUp(self):
        super().setUp()
        self.request = make_request(self.client_user)

    def review(self, decision, note="", actor=None, request_id=None):
        return services.review_request(
            actor=actor or self.manager,
            request_id=request_id or self.request.pk,
            data=ReviewInputDTO(decision=decision, note=note),
        )

    def test_manager_approves_with_optional_note(self):
        result = self.review("APPROVED")
        self.assertTrue(result.success)
        self.assertEqual(result.message, 'Request "New laptops" was approved.')
        request = self.reload(self.request)
        self.assertEqual((request.status, request.reviewer, request.review_note), (Status.APPROVED, self.manager, ""))
        self.assertIsNotNone(request.reviewed_at)

    def test_manager_rejects_with_a_note(self):
        self.assertTrue(self.review("REJECTED", note="Over budget").success)
        request = self.reload(self.request)
        self.assertEqual((request.status, request.review_note), (Status.REJECTED, "Over budget"))

    def test_rejection_without_note_is_refused(self):
        result = self.review("REJECTED", note="")
        self.assertIn("note", result.errors)
        self.assertEqual(self.reload(self.request).status, Status.PENDING)

    def test_decisions_are_final(self):
        self.review("APPROVED")
        result = self.review("REJECTED", note="Changed my mind", actor=make_user("m2", role=Role.MANAGER))
        self.assertEqual(result.errors, {"non_field_errors": [services.NOT_PENDING_ERROR]})
        request = self.reload(self.request)
        self.assertEqual((request.status, request.reviewer), (Status.APPROVED, self.manager))

    def test_withdrawn_requests_cannot_be_reviewed(self):
        services.withdraw_request(actor=self.client_user, request_id=self.request.pk)
        self.assertFalse(self.review("APPROVED").success)
        self.assertEqual(self.reload(self.request).status, Status.WITHDRAWN)

    def test_only_managers_review(self):
        for actor in (self.client_user, self.admin, self.root):
            with self.subTest(actor=actor.username), self.assertRaises(PermissionDenied):
                self.review("APPROVED", actor=actor)
        self.assertEqual(self.reload(self.request).status, Status.PENDING)

    def test_non_managers_get_403_even_for_missing_requests(self):
        with self.assertRaises(PermissionDenied):
            self.review("APPROVED", actor=self.client_user, request_id=999_999)
        with self.assertRaises(Http404):
            self.review("APPROVED", request_id=999_999)


class DeleteRequestTests(WorkflowTestCase):
    def test_admins_and_superusers_delete_permanently(self):
        for actor in (self.admin, self.root):
            request = make_request(self.client_user, status=Status.APPROVED)
            with self.subTest(actor=actor.username):
                result = services.delete_request(actor=actor, request_id=request.pk)
                self.assertTrue(result.success)
                self.assertFalse(BudgetRequest.objects.filter(pk=request.pk).exists())

    def test_nobody_else_can_delete(self):
        request = make_request(self.client_user)
        for actor in (self.client_user, self.manager):
            with self.subTest(actor=actor.username), self.assertRaises(PermissionDenied):
                services.delete_request(actor=actor, request_id=request.pk)
        self.assertTrue(BudgetRequest.objects.filter(pk=request.pk).exists())

    def test_missing_request_is_404(self):
        with self.assertRaises(Http404):
            services.delete_request(actor=self.admin, request_id=999_999)
