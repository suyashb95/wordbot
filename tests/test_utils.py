import unittest
from utils import italics, bold


class TestUtils(unittest.TestCase):
    def test_italics(self):
        # Test a regular string
        self.assertEqual(italics("test"), "_test_")
        # Test an empty string
        self.assertEqual(italics(""), "__")
        # Test a string with spaces
        self.assertEqual(italics("hello world"), "_hello world_")
        # Test a string with special characters
        self.assertEqual(italics("!@#$%^&*()"), "_!@#$%^&*()_")

    def test_bold(self):
        # Test a regular string
        self.assertEqual(bold("test"), "*test*")
        # Test an empty string
        self.assertEqual(bold(""), "**")
        # Test a string with spaces
        self.assertEqual(bold("hello world"), "*hello world*")
        # Test a string with special characters
        self.assertEqual(bold("!@#$%^&*()"), "*!@#$%^&*()*")


if __name__ == "__main__":
    unittest.main()