import unittest
from plan import already_sent


class SentHistoryTests(unittest.TestCase):
    def setUp(self):
        self.sent = [
            {"invoice_id": "INV-1", "step": "friendly", "sent_on": "2026-10-01"},
            {"invoice_id": "INV-2", "step": "firm", "sent_on": "2026-10-02"},
            {"invoice_id": "INV-3", "step": "final", "sent_on": "2026-10-03"},
        ]

    def test_same_step_already_sent(self):
        self.assertTrue(already_sent("INV-1", "friendly", self.sent))

    def test_higher_step_blocks_lower_step(self):
        self.assertTrue(already_sent("INV-2", "friendly", self.sent))

    def test_lower_step_does_not_block_higher_step(self):
        self.assertFalse(already_sent("INV-1", "firm", self.sent))

    def test_final_blocks_firm(self):
        self.assertTrue(already_sent("INV-3", "firm", self.sent))

    def test_unknown_invoice(self):
        self.assertFalse(already_sent("INV-99", "friendly", self.sent))


if __name__ == "__main__":
    unittest.main()