"""Conservative scaffolding for common community-health files."""

from pathlib import Path
from typing import Dict, List, Tuple


TEMPLATES: Dict[str, str] = {
    "CONTRIBUTING.md": """# Contributing

Thanks for helping improve this project!

## Development setup

1. Fork and clone the repository.
2. Follow the installation instructions in the README.
3. Create a focused branch for your change.
4. Add or update tests and run the full test suite locally.

## Pull requests

- Explain the problem and your proposed solution.
- Keep changes focused; unrelated cleanups belong in another pull request.
- Link relevant issues and describe how you tested the change.
- Be open to feedback. Small, early pull requests are welcome.

By contributing, you agree that your work is licensed under the project's license.
""",
    "CODE_OF_CONDUCT.md": """# Code of Conduct

## Our pledge

We pledge to make participation welcoming and harassment-free for everyone.

## Expected behavior

Be respectful, constructive, and patient. Welcome different viewpoints and focus on what is best for the community.

## Unacceptable behavior

Harassment, personal attacks, discriminatory language, trolling, and publishing others' private information are not acceptable.

## Reporting and enforcement

Report incidents privately through the repository owner's GitHub contact options. Maintainers will review reports in good faith, respect privacy, and take appropriate action.

This policy applies in project spaces and when representing the project publicly.
""",
    "SECURITY.md": """# Security Policy

## Reporting a vulnerability

Please do not open a public issue for a suspected vulnerability. Use GitHub's private vulnerability reporting (Security Advisories) when available, or contact the repository owner privately.

Include the affected version, reproduction steps, impact, and any suggested mitigation. Please allow maintainers reasonable time to investigate before public disclosure.

## Supported versions

Security fixes are provided for the latest released version. This section will be updated as the project's support policy evolves.
""",
    ".github/ISSUE_TEMPLATE/bug_report.md": """---
name: Bug report
about: Report a reproducible problem
title: "[Bug] "
labels: bug
---

## What happened?

## What did you expect?

## Steps to reproduce

1.
2.
3.

## Environment

- OS:
- Project version:
- Relevant runtime version:

## Logs or screenshots

```text
Paste relevant output here. Remove credentials and personal information.
```
""",
    ".github/ISSUE_TEMPLATE/feature_request.md": """---
name: Feature request
about: Suggest an improvement
title: "[Feature] "
labels: enhancement
---

## Problem

What user problem would this solve?

## Proposed solution

## Alternatives considered

## Additional context
""",
    ".github/ISSUE_TEMPLATE/config.yml": """blank_issues_enabled: true
contact_links: []
""",
    ".github/PULL_REQUEST_TEMPLATE.md": """## What changed?

## Why?

## How was this tested?

- [ ] Tests pass locally
- [ ] Documentation updated if needed
- [ ] No secrets or generated artifacts included

## Related issues

Closes #
""",
}


def scaffold(root: Path, dry_run: bool = False) -> Tuple[List[Path], List[Path]]:
    """Create only missing templates; existing files are never overwritten."""
    root = root.expanduser().resolve()
    if not root.is_dir():
        raise ValueError(f"Repository path is not a directory: {root}")
    created, skipped = [], []
    for relative, content in TEMPLATES.items():
        destination = root / relative
        if destination.exists():
            skipped.append(destination)
            continue
        created.append(destination)
        if not dry_run:
            destination.parent.mkdir(parents=True, exist_ok=True)
            destination.write_text(content, encoding="utf-8")
    return created, skipped
