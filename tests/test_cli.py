import os
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from click.testing import CliRunner

from password_manager.cli import main


class CliTests(unittest.TestCase):
    def setUp(self):
        self.runner = CliRunner()

    def test_generate_default(self):
        result = self.runner.invoke(main, ["generate"])
        self.assertEqual(result.exit_code, 0, result.output)
        self.assertEqual(len(result.output.rstrip("\n")), 20)
        self.assertEqual(result.output.count("\n"), 1)

    def test_output_is_plain_and_preserves_punctuation(self):
        sample = "[aB3]<>!"
        with patch("password_manager.cli.generate_password", return_value=sample):
            result = self.runner.invoke(main, ["generate", "-l", "8"])
        self.assertEqual(result.exit_code, 0, result.output)
        self.assertEqual(result.output, sample + "\n")

    def test_generate_options(self):
        with patch(
            "password_manager.cli.generate_password", return_value="sample"
        ) as generate:
            result = self.runner.invoke(main, ["generate", "-l", "32", "--no-symbols"])
        self.assertEqual(result.exit_code, 0, result.output)
        generate.assert_called_once_with(length=32, symbols=False)

    def test_rejects_invalid_length(self):
        for length in ("7", "1025", "not-a-number"):
            with self.subTest(length=length):
                result = self.runner.invoke(main, ["generate", "-l", length])
                self.assertEqual(result.exit_code, 2, result.output)

    def test_generate_creates_no_files(self):
        previous = Path.cwd()
        with tempfile.TemporaryDirectory() as directory:
            os.chdir(directory)
            try:
                result = self.runner.invoke(main, ["generate"])
                self.assertEqual(result.exit_code, 0, result.output)
                self.assertEqual(list(Path(directory).iterdir()), [])
            finally:
                os.chdir(previous)

    def test_add_fails_without_password_prompt(self):
        result = self.runner.invoke(main, ["add", "example", "-u", "someone"])
        self.assertEqual(result.exit_code, 1)
        self.assertIn("Nothing was saved", result.output)
        self.assertNotIn("Password:", result.output)
        self.assertNotIn("Added password", result.output)

    def test_legacy_password_option_is_not_accepted(self):
        result = self.runner.invoke(main, ["add", "example", "--password", "test-only"])
        self.assertNotEqual(result.exit_code, 0)
        self.assertNotIn("test-only", result.output)

    def test_get_fails_without_inventing_password(self):
        result = self.runner.invoke(main, ["get", "example"])
        self.assertEqual(result.exit_code, 1)
        self.assertIn("not implemented", result.output)
        self.assertNotIn("********", result.output)

    def test_help_describes_generator_only(self):
        result = self.runner.invoke(main, ["--help"])
        self.assertEqual(result.exit_code, 0, result.output)
        self.assertIn("storage is not implemented", result.output)
        self.assertIn("generate", result.output)
        self.assertNotIn("\n  add ", result.output)

    def test_version(self):
        result = self.runner.invoke(main, ["--version"])
        self.assertEqual(result.exit_code, 0, result.output)
        self.assertIn("0.1.1", result.output)


if __name__ == "__main__":
    unittest.main()
