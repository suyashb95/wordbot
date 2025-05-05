import unittest
from utils import italics, bold, format_definitions, format_example, format_synonyms, format_antonyms
from dataclass import Word, Definition

class TestUtils(unittest.TestCase):

    def setUp(self):
        self.test_word = Word(
            word="test",
            definitions=[
                Definition(part_of_speech="noun", text="a procedure for critical evaluation"),
                Definition(part_of_speech="verb", text="to assess performance")
            ],
            example="We need to test this code",
            synonyms=["examine", "check"],
            antonyms=["accept", "trust"]
        )

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
    
    def test_format_definitions(self):
        # Test with valid word data
        expected = "*Definitions*\nnoun : a procedure for critical evaluation\n\nverb : to assess performance\n\n"
        self.assertEqual(format_definitions(self.test_word), expected)
        
        # Test with None word
        self.assertIsNone(format_definitions(None))
        
        # Test with word having no definitions
        empty_word = Word(word="empty", definitions=[], example=None, synonyms=[], antonyms=[])
        self.assertIsNone(format_definitions(empty_word))

    def test_format_example(self):
        # Test with valid word data
        expected = "*Examples*\nWe need to test this code\n\n"
        self.assertEqual(format_example(self.test_word), expected)
        
        # Test with None word
        self.assertIsNone(format_example(None))
        
        # Test with word having no example
        no_example_word = Word(
            word="test",
            definitions=[],
            example=None,
            synonyms=[],
            antonyms=[]
        )
        self.assertIsNone(format_example(no_example_word))

    def test_format_synonyms(self):
        # Test with valid word data
        expected = "*Synonyms*\nexamine\ncheck\n"
        self.assertEqual(format_synonyms(self.test_word), expected)
        
        # Test with None word
        self.assertIsNone(format_synonyms(None))
        
        # Test with word having no synonyms
        no_synonyms_word = Word(
            word="test",
            definitions=[],
            example=None,
            synonyms=[],
            antonyms=[]
        )
        self.assertIsNone(format_synonyms(no_synonyms_word))

    def test_format_antonyms(self):
        # Test with valid word data
        expected = "*Antonyms*\naccept\ntrust\n"
        self.assertEqual(format_antonyms(self.test_word), expected)
        
        # Test with None word
        self.assertIsNone(format_antonyms(None))
        
        # Test with word having no antonyms
        no_antonyms_word = Word(
            word="test",
            definitions=[],
            example=None,
            synonyms=[],
            antonyms=[]
        )
        self.assertIsNone(format_antonyms(no_antonyms_word))


if __name__ == "__main__":
    unittest.main()