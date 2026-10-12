import unittest
from datetime import date

from plan import calculate_days_overdue


class OverdueTests(unittest.TestCase):

    def test_invoice_overdue_by_twelve_days(self):
        due_date = date(2026, 9, 30)
        today = date(2026, 10, 12)

        self.assertEqual(
            calculate_days_overdue(due_date, today),
            12,
        )

    def test_invoice_due_today(self):
        today = date(2026, 10, 12)

        self.assertEqual(
            calculate_days_overdue(today, today),
            0,
        )

    def test_invoice_due_in_future(self):
        due_date = date(2026, 10, 20)
        today = date(2026, 10, 12)

        self.assertEqual(
            calculate_days_overdue(due_date, today),
            -8,
        )


if __name__ == "__main__":
    unittest.main()