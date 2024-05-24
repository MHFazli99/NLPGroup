import unittest
from regex_classifier import *
from utils import prettify_matches

class TestMatchRegex(unittest.TestCase):
    def __init__(self, methodName: str = "runTest") -> None:
        super().__init__(methodName)
        self.clf = RegexClassifier()
    def test_matcher(self):
        matches = self.clf.match_input_pattern('234-324', '\d+\-\d+')
        self.assertTrue(matches)
        matches = self.clf.match_input_pattern('234-324', '\d+')
        self.assertFalse(matches)
        matches = self.clf.match_input_pattern('qwerty@gmail.com', '[0-9a-z]+@gmail.com')
        self.assertTrue(matches)
    def test_add_pattern_and_match(self):
        self.clf.add_pattern("number", "\d+")
        matches = self.clf.match_patterns("234")
        self.assertRegex(prettify_matches(matches), "type: number")
    def test_extract_regex(self):
        examples = ["هرچی 2", "هرچی 1"]
        pattern = self.clf.extract_regex_pattern(examples)
        self.assertEqual(pattern, "هرچی\ \d")


if __name__ == '__main__':
    unittest.main()