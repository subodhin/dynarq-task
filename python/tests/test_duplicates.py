import unittest

from plan import build_plan


class DuplicateInvoiceTests(unittest.TestCase):

    def test_unique_invoice_is_not_skipped_as_duplicate(self):
        invoices = [
            {
                "id": "INV-1001",
                "customer": "Alder Fabrication Ltd",
                "amount": 1250.0,
                "currency": "EUR",
                "due_date": "2026-10-10",
                "paid_date": None,
            }
        ]

        plan = build_plan(invoices, [], "2026-10-12")

        self.assertNotIn(
            {"invoice_id": "INV-1001", "reason": "duplicate_id"},
            plan["skipped"],
        )

    def test_every_invoice_with_duplicate_id_is_skipped(self):
        invoices = [
            {
                "id": "INV-1010",
                "customer": "Juniper Events",
                "amount": 560.0,
                "currency": "EUR",
                "due_date": "2026-09-25",
                "paid_date": None,
            },
            {
                "id": "INV-1010",
                "customer": "Juniper Events",
                "amount": 720.0,
                "currency": "EUR",
                "due_date": "2026-09-28",
                "paid_date": None,
            },
        ]

        plan = build_plan(invoices, [], "2026-10-12")

        self.assertFalse(
            any(action["invoice_id"] == "INV-1010"
                for action in plan["actions"])
        )

        self.assertEqual(
            plan["skipped"].count(
                {"invoice_id": "INV-1010", "reason": "duplicate_id"}
            ),
            1,
        )

    def test_duplicate_id_is_skipped_once_when_three_invoices_share_it(self):
        invoices = [
            {
                "id": "INV-2000",
                "amount": 100,
                "due_date": "2026-10-01",
                "paid_date": None,
            },
            {
                "id": "INV-2000",
                "amount": 200,
                "due_date": "2026-10-02",
                "paid_date": None,
            },
            {
                "id": "INV-2000",
                "amount": 300,
                "due_date": "2026-10-03",
                "paid_date": None,
            },
        ]

        plan = build_plan(invoices, [], "2026-10-12")

        duplicate_entries = [
            item for item in plan["skipped"]
            if item == {
                "invoice_id": "INV-2000",
                "reason": "duplicate_id",
            }
        ]

        self.assertEqual(len(duplicate_entries), 1)
        self.assertFalse(
            any(action["invoice_id"] == "INV-2000"
                for action in plan["actions"])
        )


if __name__ == "__main__":
    unittest.main()