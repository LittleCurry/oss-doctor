"""Built-in, read-only repository checks.

Checks intentionally inspect only repository contents. They never inspect Git
credentials, environment variables, or files outside the selected repository.
"""

from configparser import ConfigParser, Error as ConfigError
import json
from pathlib import Path
import re
from typing import Callable, List, Optional

from .models import Report, Result


Check = Callable[[Path], Result]


def _entry(directory: Path, *names: str) -> Optional[Path]:
    """Find a direct child case-insensitively without following symlinks."""
    if not directory.is_dir():
        return None
    wanted = {name.lower() for name in names}
    try:
        for child in directory.iterdir():
            if child.name.lower() in wanted and not child.is_symlink():
                return child
    except OSError:
        return None
    return None


def _text(path: Optional[Path], limit: int = 500_000) -> str:
    if path is None or not path.is_file():
        return ""
    try:
        return path.read_text(encoding="utf-8", errors="replace")[:limit]
    except OSError:
        return ""


def _result(
    check_id: str,
    title: str,
    weight: int,
    status: str,
    message: str,
    recommendation: str,
) -> Result:
    return Result(check_id, title, status, message, recommendation, weight)


def readme(root: Path) -> Result:
    path = _entry(root, "README.md", "README.rst", "README.txt", "README")
    if not path or not path.is_file():
        return _result("readme", "README", 10, "fail", "No README found.",
                       "Add a README that explains the problem your project solves.")
    size = len(_text(path).strip())
    if size < 300:
        return _result("readme", "README", 10, "warn", f"{path.name} is only {size} characters.",
                       "Add a clear pitch, screenshot or demo, and links to documentation.")
    return _result("readme", "README", 10, "pass", f"Found a substantive {path.name}.",
                   "Keep the introduction concise and newcomer-friendly.")


def quickstart(root: Path) -> Result:
    path = _entry(root, "README.md", "README.rst", "README.txt", "README")
    content = _text(path).lower()
    has_install = bool(re.search(r"^#{1,4}\s+.*(install|quick ?start|getting started|安装|快速开始)", content, re.M))
    has_usage = bool(re.search(r"^#{1,4}\s+.*(usage|quick ?start|getting started|使用|快速开始)", content, re.M))
    has_code = "```" in content or ".. code-block::" in content
    if has_install and has_usage and has_code:
        return _result("quickstart", "Quick start", 8, "pass", "Install, usage, and code examples found.",
                       "Test the quick start regularly in a clean environment.")
    missing = []
    if not has_install:
        missing.append("installation")
    if not has_usage:
        missing.append("usage")
    if not has_code:
        missing.append("a runnable code block")
    status = "fail" if not path else "warn"
    return _result("quickstart", "Quick start", 8, status,
                   "Missing " + ", ".join(missing) + ".",
                   "Add installation and usage sections with copy-pasteable commands.")


def license_check(root: Path) -> Result:
    path = _entry(root, "LICENSE", "LICENSE.md", "LICENSE.txt", "LICENCE", "COPYING")
    if not path or not _text(path).strip():
        return _result("license", "License", 12, "fail", "No recognizable license file found.",
                       "Choose an OSI-approved license and add it as LICENSE.")
    return _result("license", "License", 12, "pass", f"Found {path.name}.",
                   "Keep the license copyright and source headers up to date.")


def metadata(root: Path) -> Result:
    description = ""
    pyproject = _entry(root, "pyproject.toml")
    if pyproject:
        match = re.search(r'(?m)^description\s*=\s*["\'](.+?)["\']', _text(pyproject))
        description = match.group(1).strip() if match else ""
    package = _entry(root, "package.json")
    if package and not description:
        try:
            value = json.loads(_text(package)).get("description", "")
            description = value.strip() if isinstance(value, str) else ""
        except (ValueError, AttributeError):
            pass
    setup_cfg = _entry(root, "setup.cfg")
    if setup_cfg and not description:
        parser = ConfigParser()
        try:
            parser.read_string(_text(setup_cfg))
            description = parser.get("metadata", "description", fallback="").strip()
        except (ConfigError, UnicodeError):
            # Invalid packaging metadata should not make the entire audit crash.
            description = ""
    if description:
        return _result("metadata", "Project metadata", 5, "pass", "A package description was found.",
                       "Mirror this clear description in the repository metadata.")
    has_manifest = any(_entry(root, name) for name in (
        "pyproject.toml", "setup.py", "setup.cfg", "package.json", "Cargo.toml",
        "go.mod", "pom.xml", "build.gradle", "Gemfile", "composer.json",
    ))
    return _result("metadata", "Project metadata", 5, "warn" if has_manifest else "fail",
                   "No package description found." if has_manifest else "No common project manifest found.",
                   "Add a concise description and package metadata for discoverability.")


def community_file(check_id: str, title: str, weight: int, names: tuple, recommendation: str) -> Check:
    def check(root: Path) -> Result:
        locations = (root, root / ".github", root / "docs")
        path = next((found for location in locations if (found := _entry(location, *names))), None)
        if path and _text(path).strip():
            return _result(check_id, title, weight, "pass", f"Found {path.relative_to(root)}.",
                           "Review this document as the project and community evolve.")
        return _result(check_id, title, weight, "fail", f"No {title} found.", recommendation)
    return check


def issue_templates(root: Path) -> Result:
    directory = root / ".github" / "ISSUE_TEMPLATE"
    has_files = directory.is_dir() and any(p.is_file() and not p.is_symlink() for p in directory.iterdir())
    legacy = _entry(root / ".github", "ISSUE_TEMPLATE.md")
    if has_files or legacy:
        return _result("issues", "Issue templates", 6, "pass", "Issue templates found.",
                       "Keep templates short and ask for actionable reproduction details.")
    return _result("issues", "Issue templates", 6, "fail", "No issue templates found.",
                   "Add bug report and feature request templates under .github/ISSUE_TEMPLATE.")


def pull_request_template(root: Path) -> Result:
    path = _entry(root / ".github", "PULL_REQUEST_TEMPLATE.md", "pull_request_template.md")
    directory = root / ".github" / "PULL_REQUEST_TEMPLATE"
    has_files = directory.is_dir() and any(p.is_file() for p in directory.iterdir())
    if path or has_files:
        return _result("pull_request", "Pull request template", 5, "pass", "Pull request template found.",
                       "Ask contributors to describe testing and link related issues.")
    return _result("pull_request", "Pull request template", 5, "fail", "No pull request template found.",
                   "Add .github/PULL_REQUEST_TEMPLATE.md with a concise review checklist.")


def continuous_integration(root: Path) -> Result:
    candidates = (
        root / ".github" / "workflows", root / ".circleci", root / ".buildkite",
    )
    has_ci = any(p.is_dir() and any(child.is_file() for child in p.iterdir()) for p in candidates)
    has_ci = has_ci or any(_entry(root, name) for name in (
        ".travis.yml", "azure-pipelines.yml", "Jenkinsfile", ".gitlab-ci.yml", "appveyor.yml",
    ))
    if has_ci:
        return _result("ci", "Continuous integration", 10, "pass", "CI configuration found.",
                       "Run tests on every pull request and supported runtime version.")
    return _result("ci", "Continuous integration", 10, "fail", "No common CI configuration found.",
                   "Add CI that installs dependencies and runs tests on pull requests.")


def tests(root: Path) -> Result:
    conventional = any((root / name).is_dir() for name in ("tests", "test", "spec", "__tests__"))
    patterns = ("test_*.py", "*_test.py", "*.test.js", "*.test.ts", "*_test.go", "*Test.java")
    found = conventional
    if not found:
        try:
            found = any(next(root.rglob(pattern), None) is not None for pattern in patterns)
        except OSError:
            found = False
    if found:
        return _result("tests", "Automated tests", 10, "pass", "Test files or a test directory found.",
                       "Measure meaningful behavior and keep the test suite fast.")
    return _result("tests", "Automated tests", 10, "fail", "No automated tests found.",
                   "Add tests for the core workflow and wire them into CI.")


def gitignore(root: Path) -> Result:
    path = _entry(root, ".gitignore")
    if path and _text(path).strip():
        return _result("gitignore", "Git ignore rules", 3, "pass", ".gitignore found.",
                       "Keep generated files, credentials, and local settings out of Git.")
    return _result("gitignore", "Git ignore rules", 3, "warn", "No .gitignore found.",
                   "Add ignore rules for build artifacts, environments, and secrets.")


def changelog(root: Path) -> Result:
    path = next((found for location in (root, root / "docs")
                 if (found := _entry(location, "CHANGELOG.md", "CHANGELOG.rst", "HISTORY.md", "RELEASES.md"))), None)
    if path:
        return _result("changelog", "Release notes", 5, "pass", f"Found {path.relative_to(root)}.",
                       "Document notable changes and follow a consistent release process.")
    return _result("changelog", "Release notes", 5, "warn", "No changelog found.",
                   "Add a changelog so users can upgrade with confidence.")


def documentation(root: Path) -> Result:
    docs = root / "docs"
    has_docs = docs.is_dir() and any(p.is_file() for p in docs.rglob("*") if not p.is_symlink())
    readme_path = _entry(root, "README.md", "README.rst", "README.txt")
    content = _text(readme_path).lower()
    linked = "docs/" in content or "documentation" in content or "文档" in content
    if has_docs or linked:
        return _result("docs", "Documentation", 5, "pass", "Extended documentation or documentation links found.",
                       "Keep examples versioned alongside the code they describe.")
    return _result("docs", "Documentation", 5, "warn", "No extended documentation found.",
                   "Add focused guides for configuration, architecture, and common tasks.")


CHECKS: List[Check] = [
    readme,
    quickstart,
    license_check,
    metadata,
    community_file("contributing", "Contributing guide", 8,
                   ("CONTRIBUTING.md", "CONTRIBUTING.rst", "CONTRIBUTING"),
                   "Add setup instructions, coding conventions, and the pull request process."),
    community_file("code_of_conduct", "Code of conduct", 5,
                   ("CODE_OF_CONDUCT.md", "CODE_OF_CONDUCT.rst"),
                   "Adopt a code of conduct and provide a private enforcement contact."),
    community_file("security", "Security policy", 8,
                   ("SECURITY.md", "SECURITY.rst"),
                   "Add supported versions and a private vulnerability reporting channel."),
    issue_templates,
    pull_request_template,
    continuous_integration,
    tests,
    gitignore,
    changelog,
    documentation,
]


def audit(path: Path) -> Report:
    """Run all built-in checks against *path* without modifying it."""
    root = path.expanduser().resolve()
    if not root.is_dir():
        raise ValueError(f"Repository path is not a directory: {root}")
    return Report(root, [check(root) for check in CHECKS])
