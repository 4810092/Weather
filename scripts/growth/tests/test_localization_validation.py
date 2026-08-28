from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from scripts.check_localizations import (
    compare_apple_strings,
    compare_resources,
    parse_apple_strings,
    read,
)


class LocalizationValidationTest(unittest.TestCase):
    def android_resources(self, content: str) -> dict:
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "strings.xml"
            path.write_text(content, encoding="utf-8")
            return read(path)

    def test_android_blank_string_is_rejected(self) -> None:
        with self.assertRaisesRegex(ValueError, "blank string value"):
            self.android_resources(
                '<resources><string name="forecast">   </string></resources>'
            )

    def test_android_blank_plural_item_is_rejected(self) -> None:
        with self.assertRaisesRegex(ValueError, "blank plural value"):
            self.android_resources(
                "<resources><plurals name=\"days\">"
                '<item quantity="other"> </item>'
                "</plurals></resources>"
            )

    def test_android_placeholder_multiplicity_is_compared(self) -> None:
        canonical = self.android_resources(
            '<resources><string name="summary">%1$s · %1$s · %2$d%%</string></resources>'
        )
        translated = self.android_resources(
            '<resources><string name="summary">%1$s · %2$d%%</string></resources>'
        )
        failures = compare_resources(canonical, translated, "fixture")
        self.assertEqual(len(failures), 1)
        self.assertIn("%1$s", failures[0])

    def test_apple_blank_value_is_rejected(self) -> None:
        with self.assertRaisesRegex(ValueError, "blank string value"):
            parse_apple_strings('"Weather" = "   ";', "fixture")

    def test_apple_malformed_syntax_is_rejected(self) -> None:
        malformed = (
            '"Weather" = ;',
            '"Weather" = "Forecast"',
            '"Weather" = "unterminated;',
            '/* unterminated comment',
        )
        for content in malformed:
            with self.subTest(content=content):
                with self.assertRaises(ValueError):
                    parse_apple_strings(content, "fixture")

    def test_apple_placeholder_type_and_multiplicity_are_compared(self) -> None:
        canonical = parse_apple_strings(
            '"Weather" = "%1$@ · %2$ld · %1$@";', "canonical"
        )
        translated = parse_apple_strings(
            '"Weather" = "%1$@ · %2$d";', "translated"
        )
        failures = compare_apple_strings(canonical, translated, "fixture")
        self.assertEqual(len(failures), 1)
        self.assertIn("expected placeholders", failures[0])

    def test_apple_parser_accepts_comments_and_escaped_values(self) -> None:
        entries = parse_apple_strings(
            '/* Header */\n"Weather" = "Rain \\"soon\\""; // inline\n'
            '"Temperature" = "%1$d°";\n',
            "fixture",
        )
        self.assertEqual(entries["Weather"], 'Rain "soon"')
        self.assertEqual(entries["Temperature"], "%1$d°")


if __name__ == "__main__":
    unittest.main()
