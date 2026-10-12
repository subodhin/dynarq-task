import unittest
from datetime import date

from plan import parse_date


class ParseDateTests(unittest.TestCase):

    def test_valid_date(self):
        self.assertEqual(
            parse_date("2026-10-12"),
            date(2026, 10, 12)
        )

    def test_impossible_date(self):
        self.assertIsNone(parse_date("2026-02-30"))

    def test_wrong_format(self):
        self.assertIsNone(parse_date("12-10-2026"))

    def test_non_string(self):
        self.assertIsNone(parse_date(None))


if __name__ == "__main__":
    unittest.main()