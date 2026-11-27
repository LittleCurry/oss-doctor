import tempfile
import unittest
from pathlib import Path

from oss_doctor.checks import audit
from oss_doctor.models import Report, Result


class AuditTests(unittest.TestCase):
    def setUp(self):
        self.tempdir = tempfile.TemporaryDirectory()
        self.root = Path(self.tempdir.name)

    def tearDown(self):
        self.tempdir.cleanup()

    def write(self, relative, content="example"):
        path = self.root / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")
        return path

    def test_empty_repository_has_failing_grade(self):
        report = audit(self.root)
        self.assertLess(report.score, 10)
        self.assertEqual(0, report.counts["pass"])
        self.assertEqual("F", report.grade)

    def test_nonexistent_repository_raises_value_error(self):
        with self.assertRaises(ValueError):
            audit(self.root / "missing")

    def test_readme_accepts_case_insensitive_filename(self):
        self.write("readme.MD", "# Project\n\n" + "Useful documentation. " * 30)
        result = next(item for item in audit(self.root).results if item.check_id == "readme")
        self.assertEqual("pass", result.status)

    def test_short_readme_gets_warning(self):
        self.write("README.md", "tiny")
        result = next(item for item in audit(self.root).results if item.check_id == "readme")
        self.assertEqual("warn", result.status)

    def test_complete_quickstart_passes(self):
        self.write("README.md", "# X\n\n## Installation\n```sh\npip install x\n```\n## Usage\n```sh\nx .\n```")
        result = next(item for item in audit(self.root).results if item.check_id == "quickstart")
        self.assertEqual("pass", result.status)

    def test_missing_usage_is_actionable(self):
        self.write("README.md", "## Installation\n```sh\npip install x\n```")
        result = next(item for item in audit(self.root).results if item.check_id == "quickstart")
        self.assertIn("usage", result.message)

    def test_pyproject_description_is_detected(self):
        self.write("pyproject.toml", '[project]\ndescription = "Useful tools"\n')
        result = next(item for item in audit(self.root).results if item.check_id == "metadata")
        self.assertEqual("pass", result.status)

    def test_package_json_description_is_detected(self):
        self.write("package.json", '{"description": "Useful tools"}')
        result = next(item for item in audit(self.root).results if item.check_id == "metadata")
        self.assertEqual("pass", result.status)

    def test_invalid_package_json_does_not_crash(self):
        self.write("package.json", '{not json')
        result = next(item for item in audit(self.root).results if item.check_id == "metadata")
        self.assertEqual("warn", result.status)

    def test_cargo_package_description_is_detected(self):
        self.write("Cargo.toml", '[package]\nname = "demo"\n  description = "Useful Rust tools" # comment\n')
        result = next(item for item in audit(self.root).results if item.check_id == "metadata")
        self.assertEqual("pass", result.status)

    def test_cargo_literal_description_is_detected(self):
        self.write("Cargo.toml", "[package]\ndescription = 'Useful Rust tools'\n")
        result = next(item for item in audit(self.root).results if item.check_id == "metadata")
        self.assertEqual("pass", result.status)

    def test_cargo_missing_description_warns(self):
        self.write("Cargo.toml", '[package]\nname = "demo"\n[package.metadata]\ndescription = "not the package description"\n')
        result = next(item for item in audit(self.root).results if item.check_id == "metadata")
        self.assertEqual("warn", result.status)

    def test_invalid_cargo_description_does_not_crash(self):
        for description in ('description = "unterminated', 'description = ""', 'description = 42'):
            with self.subTest(description=description):
                self.write("Cargo.toml", "[package]\n" + description + "\n")
                result = next(item for item in audit(self.root).results if item.check_id == "metadata")
                self.assertEqual("warn", result.status)

    def test_docs_community_files_are_detected(self):
        self.write("docs/CONTRIBUTING.md")
        self.write("docs/SECURITY.md")
        results = {item.check_id: item for item in audit(self.root).results}
        self.assertEqual("pass", results["contributing"].status)
        self.assertEqual("pass", results["security"].status)

    def test_issue_template_directory_is_detected(self):
        self.write(".github/ISSUE_TEMPLATE/bug.md")
        result = next(item for item in audit(self.root).results if item.check_id == "issues")
        self.assertEqual("pass", result.status)

    def test_gitlab_ci_is_detected(self):
        self.write(".gitlab-ci.yml", "test:\n  script: make test")
        result = next(item for item in audit(self.root).results if item.check_id == "ci")
        self.assertEqual("pass", result.status)

    def test_test_pattern_without_test_directory_is_detected(self):
        self.write("src/math_test.go", "package math")
        result = next(item for item in audit(self.root).results if item.check_id == "tests")
        self.assertEqual("pass", result.status)

    def test_empty_tests_directory_still_counts(self):
        (self.root / "tests").mkdir()
        result = next(item for item in audit(self.root).results if item.check_id == "tests")
        self.assertEqual("pass", result.status)

    def test_weights_are_normalized_to_100(self):
        result = Result("x", "X", "pass", "ok", "", 7)
        report = Report(self.root, [result])
        self.assertEqual(100, report.score)

    def test_warning_earns_half_points(self):
        result = Result("x", "X", "warn", "almost", "", 10)
        report = Report(self.root, [result])
        self.assertEqual(50, report.score)

    def test_symlinked_readme_is_not_followed(self):
        outside = Path(self.tempdir.name).parent / "outside-oss-doctor-test"
        outside.write_text("secret", encoding="utf-8")
        try:
            (self.root / "README.md").symlink_to(outside)
            result = next(item for item in audit(self.root).results if item.check_id == "readme")
            self.assertEqual("fail", result.status)
        finally:
            outside.unlink()


if __name__ == "__main__":
    unittest.main()
