import unittest

from plan import validate_amount


class ValidateAmountTests(unittest.TestCase):

    def test_positive_integer(self):
        self.assertTrue(validate_amount(100))

    def test_positive_decimal(self):
        self.assertTrue(validate_amount(1250.50))

    def test_zero_is_invalid(self):
        self.assertFalse(validate_amount(0))

    def test_negative_amount_is_invalid(self):
        self.assertFalse(validate_amount(-10))

    def test_boolean_is_invalid(self):
        self.assertFalse(validate_amount(True))

    def test_string_is_invalid(self):
        self.assertFalse(validate_amount("100"))

    def test_none_is_invalid(self):
        self.assertFalse(validate_amount(None))


if __name__ == "__main__":
    unittest.main()