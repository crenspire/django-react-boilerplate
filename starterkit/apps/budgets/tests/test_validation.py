from decimal import Decimal

from django.test import SimpleTestCase

from apps.budgets.domain.models import Status
from apps.budgets.dto.budget_requests import BudgetRequestInputDTO, ReviewInputDTO
from apps.budgets.services.validation import (
    NOTE_REQUIRED_ON_REJECT,
    REQUIRED,
    clean_request_input,
    clean_review_input,
)


def request_input(**overrides):
    values = {"title": "Laptops", "amount": "1500.00", "justification": "Old hardware."}
    values.update(overrides)
    return BudgetRequestInputDTO(**values)


class RequestInputTests(SimpleTestCase):
    def test_valid_input_is_trimmed_and_converted(self):
        clean, errors = clean_request_input(request_input(title="  Laptops  ", amount=" 1,500.5 "))
        self.assertEqual(errors, {})
        self.assertEqual(clean.title, "Laptops")
        self.assertEqual(clean.amount, Decimal("1500.50"))

    def test_required_fields(self):
        _, errors = clean_request_input(request_input(title=" ", amount="", justification=""))
        self.assertEqual(errors, {"title": [REQUIRED], "amount": [REQUIRED], "justification": [REQUIRED]})

    def test_invalid_amounts(self):
        for amount in ("abc", "NaN", "Infinity", "0", "-1", "1.001", "10000000000"):
            with self.subTest(amount=amount):
                clean, errors = clean_request_input(request_input(amount=amount))
                self.assertIsNone(clean)
                self.assertIn("amount", errors)

    def test_length_limits(self):
        _, errors = clean_request_input(request_input(title="x" * 201, justification="y" * 5001))
        self.assertEqual(set(errors), {"title", "justification"})


class ReviewInputTests(SimpleTestCase):
    def test_approval_note_is_optional(self):
        clean, errors = clean_review_input(ReviewInputDTO(decision="APPROVED", note=""))
        self.assertEqual(errors, {})
        self.assertEqual(clean.status, Status.APPROVED)

    def test_rejection_needs_a_note(self):
        _, errors = clean_review_input(ReviewInputDTO(decision="REJECTED", note="   "))
        self.assertEqual(errors, {"note": [NOTE_REQUIRED_ON_REJECT]})
        clean, errors = clean_review_input(ReviewInputDTO(decision="REJECTED", note=" Too costly "))
        self.assertEqual((clean.status, clean.note), (Status.REJECTED, "Too costly"))

    def test_only_approve_or_reject(self):
        for decision in ("PENDING", "WITHDRAWN", "approved", ""):
            with self.subTest(decision=decision):
                _, errors = clean_review_input(ReviewInputDTO(decision=decision, note="x"))
                self.assertIn("decision", errors)

    def test_note_length(self):
        _, errors = clean_review_input(ReviewInputDTO(decision="APPROVED", note="n" * 2001))
        self.assertIn("note", errors)
