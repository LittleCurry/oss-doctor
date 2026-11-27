import contextlib
import io
import json
import tempfile
import unittest
from pathlib import Path

from oss_doctor.cli import main
from oss_doctor.fixes import TEMPLATES, scaffold


class CliTests(unittest.TestCase):
    def setUp(self):
        self.tempdir = tempfile.TemporaryDirectory()
        self.root = Path(self.tempdir.name)

    def tearDown(self):
        self.tempdir.cleanup()

    def run_cli(self, *args):
        stdout, stderr = io.StringIO(), io.StringIO()
        with contextlib.redirect_stdout(stdout), contextlib.redirect_stderr(stderr):
            code = main(list(args))
        return code, stdout.getvalue(), stderr.getvalue()

    def test_default_command_audits_path(self):
        code, output, _ = self.run_cli(str(self.root))
        self.assertEqual(0, code)
        self.assertIn("OSS Doctor", output)

    def test_json_output(self):
        code, output, _ = self.run_cli("check", str(self.root), "--format", "json", "--no-color")
        self.assertEqual(0, code)
        self.assertLess(json.loads(output)["score"], 10)

    def test_fail_under(self):
        code, _, _ = self.run_cli("check", str(self.root), "--fail-under", "80")
        self.assertEqual(1, code)

    def test_invalid_path_is_clean_error(self):
        code, _, error = self.run_cli("check", str(self.root / "absent"))
        self.assertEqual(2, code)
        self.assertIn("not a directory", error)

    def test_report_file(self):
        output = self.root / "reports" / "health.md"
        code, _, _ = self.run_cli("check", self.root.as_posix(), "--format", "markdown", "--output", str(output))
        self.assertEqual(0, code)
        self.assertIn("# OSS Doctor report", output.read_text())

    def test_badge_file(self):
        output = self.root / "badge.svg"
        code, _, _ = self.run_cli("badge", str(self.root), "--output", str(output))
        self.assertEqual(0, code)
        self.assertIn("<svg", output.read_text())

    def test_fix_creates_and_preserves_templates(self):
        custom = self.root / "CONTRIBUTING.md"
        custom.write_text("my guide")
        created, skipped = scaffold(self.root)
        self.assertEqual(len(TEMPLATES) - 1, len(created))
        self.assertIn(custom.resolve(), skipped)
        self.assertEqual("my guide", custom.read_text())
        self.assertIn("Security Policy", (self.root / "SECURITY.md").read_text())

    def test_dry_run_does_not_write(self):
        created, _ = scaffold(self.root, dry_run=True)
        self.assertEqual(len(TEMPLATES), len(created))
        self.assertFalse((self.root / "SECURITY.md").exists())

    def test_version(self):
        with self.assertRaises(SystemExit) as raised:
            self.run_cli("--version")
        self.assertEqual(0, raised.exception.code)


if __name__ == "__main__":
    unittest.main()
