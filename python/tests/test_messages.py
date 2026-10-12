import unittest
from plan import build_message


class MessageTests(unittest.TestCase):
    def setUp(self):
        self.invoice = {
            "id": "INV-1",
            "customer": "Alder Fabrication Ltd",
            "amount": 1250,
            "currency": "EUR",
            "due_date": "2026-09-30",
        }

    def test_message_contains_required_invoice_details(self):
        message = build_message(self.invoice, "friendly", 12)

        for detail in [
            "Alder Fabrication Ltd",
            "INV-1",
            "2026-09-30",
            "EUR 1250.00",
            "12 days overdue",
        ]:
            with self.subTest(detail=detail):
                self.assertIn(detail, message)

    def test_firm_message_uses_firm_tone(self):
        message = build_message(self.invoice, "firm", 12)
        self.assertIn("Please arrange payment as soon as possible", message)

    def test_final_message_uses_urgent_tone(self):
        message = build_message(self.invoice, "final", 24)
        self.assertIn("urgent attention", message)


if __name__ == "__main__":
    unittest.main()