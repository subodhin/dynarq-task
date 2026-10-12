import unittest
from plan import select_reminder_step


class ReminderStepTests(unittest.TestCase):
    def test_not_overdue_enough(self):
        self.assertIsNone(select_reminder_step(2))

    def test_friendly_threshold(self):
        self.assertEqual(select_reminder_step(3), "friendly")

    def test_firm_threshold(self):
        self.assertEqual(select_reminder_step(10), "firm")

    def test_final_threshold(self):
        self.assertEqual(select_reminder_step(24), "final")

    def test_highest_step_wins(self):
        self.assertEqual(select_reminder_step(30), "final")


if __name__ == "__main__":
    unittest.main()