import string
import unittest
from unittest.mock import patch

from password_manager.generator import generate_password


class GeneratorTests(unittest.TestCase):
    def test_lengths_and_character_classes(self):
        for length in (8, 20, 32, 1024):
            with self.subTest(length=length):
                result = generate_password(length)
                self.assertEqual(len(result), length)
                groups = (string.ascii_lowercase, string.ascii_uppercase,
                          string.digits, string.punctuation)
                self.assertTrue(all(any(char in group for char in result)
                                    for group in groups))
                self.assertTrue(set(result) <= set("".join(groups)))

    def test_no_symbols(self):
        result = generate_password(32, symbols=False)
        self.assertTrue(set(result) <= set(string.ascii_letters + string.digits))
        for group in (string.ascii_lowercase, string.ascii_uppercase, string.digits):
            self.assertTrue(any(char in group for char in result))

    def test_secrets_choice_is_used_with_enabled_alphabet(self):
        sample = "aB3!cD5?"
        with patch("password_manager.generator.secrets.choice",
                   side_effect=sample) as choose:
            self.assertEqual(generate_password(8), sample)
        self.assertEqual(choose.call_count, 8)
        alphabet = string.ascii_letters + string.digits + string.punctuation
        for call in choose.call_args_list:
            self.assertEqual(call.args, (alphabet,))

    def test_rejects_candidate_missing_a_character_class(self):
        with patch("password_manager.generator.secrets.choice",
                   side_effect="aaaaaaaaaB3!cD5?") as choose:
            self.assertEqual(generate_password(8), "aB3!cD5?")
        self.assertEqual(choose.call_count, 16)

    def test_no_symbols_alphabet(self):
        with patch("password_manager.generator.secrets.choice",
                   side_effect="aB3cdE5f") as choose:
            self.assertEqual(generate_password(8, symbols=False), "aB3cdE5f")
        for call in choose.call_args_list:
            self.assertEqual(call.args, (string.ascii_letters + string.digits,))

    def test_invalid_lengths(self):
        for length in (-1, 0, 7, 1025, 1.5, "20", None, True):
            with self.subTest(length=length), self.assertRaises(ValueError):
                generate_password(length)

    def test_invalid_symbols_option(self):
        with self.assertRaises(ValueError):
            generate_password(symbols="false")


if __name__ == "__main__":
    unittest.main()
