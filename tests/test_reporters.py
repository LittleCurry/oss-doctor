import json
import tempfile
import unittest
from pathlib import Path

from oss_doctor.models import Report, Result
from oss_doctor.reporters import badge, console, html_report, json_report, markdown


class ReporterTests(unittest.TestCase):
    def setUp(self):
        self.report = Report(Path("/tmp/<demo>"), [
            Result("readme", "README", "pass", "Found <README>.", "Keep it.", 8),
            Result("license", "License", "fail", "Missing | license.", "Add one.", 12),
        ])

    def test_console_contains_score_and_recommendation(self):
        output = console(self.report, color=False)
        self.assertIn("40/100", output)
        self.assertIn("Add one.", output)

    def test_console_ascii_fallback(self):
        output = console(self.report, color=False, unicode_output=False)
        output.encode("ascii")
        self.assertIn("[PASS]", output)
        self.assertIn("-> Add one.", output)

    def test_json_is_machine_readable(self):
        parsed = json.loads(json_report(self.report))
        self.assertEqual(40, parsed["score"])
        self.assertEqual(2, len(parsed["results"]))
        self.assertEqual("1.0", parsed["schema_version"])

    def test_markdown_escapes_table_pipes(self):
        output = markdown(self.report)
        self.assertIn("Missing \\| license.", output)
        self.assertIn("Grade F", output)

    def test_html_escapes_repository_content(self):
        output = html_report(self.report)
        self.assertIn("&lt;README&gt;", output)
        self.assertIn("&lt;demo&gt;", output)
        self.assertNotIn("<README>", output)

    def test_badge_is_svg_with_score(self):
        output = badge(self.report)
        self.assertTrue(output.startswith("<svg"))
        self.assertIn("40/100", output)

    def test_grade_boundaries(self):
        for score, grade in ((90, "A"), (80, "B"), (70, "C"), (60, "D"), (59, "F")):
            result = Result("x", "X", "pass", "", "", score)
            filler = Result("y", "Y", "fail", "", "", 100 - score)
            self.assertEqual(grade, Report(Path("."), [result, filler]).grade)


if __name__ == "__main__":
    unittest.main()
