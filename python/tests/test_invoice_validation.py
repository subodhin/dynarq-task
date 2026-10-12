import unittest

from plan import build_plan


class InvoiceValidationTests(unittest.TestCase):

    def setUp(self):
        self.today = "2026-10-12"
        self.valid_invoice = {
            "id": "INV-2001",
            "customer": "Example Customer",
            "amount": 100.0,
            "currency": "EUR",
            "due_date": "2026-10-01",
            "paid_date": None,
        }

    def get_skipped_reason(self, invoice):
        plan = build_plan([invoice], [], self.today)
        return plan["skipped"]

    def test_missing_due_date(self):
        invoice = self.valid_invoice.copy()
        invoice.pop("due_date")

        self.assertEqual(
            self.get_skipped_reason(invoice),
            [{"invoice_id": "INV-2001", "reason": "missing_due_date"}],
        )

    def test_null_due_date(self):
        invoice = self.valid_invoice.copy()
        invoice["due_date"] = None

        self.assertEqual(
            self.get_skipped_reason(invoice),
            [{"invoice_id": "INV-2001", "reason": "missing_due_date"}],
        )

    def test_empty_due_date(self):
        invoice = self.valid_invoice.copy()
        invoice["due_date"] = ""

        self.assertEqual(
            self.get_skipped_reason(invoice),
            [{"invoice_id": "INV-2001", "reason": "missing_due_date"}],
        )

    def test_invalid_due_date(self):
        invoice = self.valid_invoice.copy()
        invoice["due_date"] = "2026-02-30"

        self.assertEqual(
            self.get_skipped_reason(invoice),
            [{"invoice_id": "INV-2001", "reason": "invalid_due_date"}],
        )

    def test_invalid_paid_date(self):
        invoice = self.valid_invoice.copy()
        invoice["paid_date"] = "not-a-date"

        self.assertEqual(
            self.get_skipped_reason(invoice),
            [{"invoice_id": "INV-2001", "reason": "invalid_paid_date"}],
        )

    def test_future_paid_date(self):
        invoice = self.valid_invoice.copy()
        invoice["paid_date"] = "2026-10-13"

        self.assertEqual(
            self.get_skipped_reason(invoice),
            [{"invoice_id": "INV-2001", "reason": "invalid_paid_date"}],
        )

    def test_invalid_amount_takes_precedence_over_invalid_due_date(self):
        invoice = self.valid_invoice.copy()
        invoice["amount"] = 0
        invoice["due_date"] = "2026-02-30"

        self.assertEqual(
            self.get_skipped_reason(invoice),
            [{"invoice_id": "INV-2001", "reason": "invalid_amount"}],
        )


if __name__ == "__main__":
    unittest.main()