<div align="center">

# 🩺 OSS Doctor

**Turn “where do I start?” into a clear open-source launch checklist.**

Zero dependencies. Actionable advice. Beautiful reports.

[![CI](https://github.com/LittleCurry/oss-doctor/actions/workflows/ci.yml/badge.svg)](https://github.com/LittleCurry/oss-doctor/actions/workflows/ci.yml)
[![License: MIT](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![Python](https://img.shields.io/badge/python-3.9%2B-blue.svg)](https://www.python.org/)
[![OSS Doctor](docs/badge.svg)](docs/example-report.html)

[Quick start](#quick-start) · [Why OSS Doctor?](#why-oss-doctor) · [Examples](#examples) · [Contributing](CONTRIBUTING.md)

</div>

---

A healthy repository helps people **understand, trust, use, and contribute** to your work. OSS Doctor audits the files and workflows that make that possible, then gives every finding a concrete next step.

It is a local, read-only CLI—not another dashboard you have to configure.

```text
OSS Doctor · ~/code/awesome-project
Score: 88/100 (grade B)

✅ README: Found a substantive README.md.
✅ Quick start: Install, usage, and code examples found.
✅ License: Found LICENSE.
⚠️ Security policy: No Security policy found.
   → Add supported versions and a private vulnerability reporting channel.
✅ Continuous integration: CI configuration found.
...

11 passed · 3 warnings · 0 failed
```

## Why OSS Doctor?

- **Useful in 30 seconds:** run one command and get a prioritized checklist.
- **Zero runtime dependencies:** only Python 3.9+ and the standard library.
- **Human and machine friendly:** terminal, JSON, Markdown, HTML, and SVG output.
- **Safe by default:** auditing never changes files or reads Git credentials.
- **Practical scaffolding:** `fix` adds missing community files without overwriting yours.
- **CI ready:** enforce a minimum score on every pull request.
- **Language agnostic:** audit Python, JavaScript, Go, Rust, Java, or mixed repositories.

> The score is a maintainability hint, not a measure of a project's worth. OSS Doctor does not promise stars or rank projects by popularity.

## Quick start

### Option A: run from source

```bash
git clone https://github.com/LittleCurry/oss-doctor.git
cd oss-doctor
python3 -m pip install .
oss-doctor /path/to/your/project
```

### Option B: install directly from GitHub

```bash
python3 -m pip install "git+https://github.com/LittleCurry/oss-doctor.git"
oss-doctor /path/to/your/project
```

### Option C: no installation

```bash
git clone https://github.com/LittleCurry/oss-doctor.git
PYTHONPATH=oss-doctor/src python3 -m oss_doctor check /path/to/your/project
```

## Examples

### Audit the current directory

```bash
oss-doctor
# The explicit form works too:
oss-doctor check .
```

### Generate a report for an issue, wiki, or pull request

```bash
oss-doctor check . --format markdown --output oss-health.md
oss-doctor check . --format html --output oss-health.html
oss-doctor check . --format json --output oss-health.json
```

[View the example HTML report](docs/example-report.html) · [Read the checks and scoring guide](docs/checks.md)

### Add a live score badge

```bash
oss-doctor badge . --output docs/oss-health.svg
```

Then commit the badge and add it to your README:

```markdown
![OSS Doctor](docs/oss-health.svg)
```

Regenerate it during releases so the score stays honest and current.

### Add missing community-health files

```bash
# Preview first
oss-doctor fix . --dry-run

# Create only files that do not exist
oss-doctor fix .
```

This scaffolds `CONTRIBUTING.md`, `CODE_OF_CONDUCT.md`, `SECURITY.md`, issue templates, and a pull request template. Existing files are **never overwritten**. README and license choices are intentionally left to you.

### Enforce a baseline in CI

```yaml
name: Repository health
on: [pull_request, push]
permissions:
  contents: read
jobs:
  oss-doctor:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: LittleCurry/oss-doctor@v0.1.0
        with:
          path: .
          fail-under: 70
```

Pin to a release tag instead of `main` for reproducible builds. See the [CI guide](docs/ci.md) for report artifacts and Dependabot-compatible workflows.

## What does it check?

| Area | What good looks like |
|---|---|
| First impression | A substantive README, installation, usage, and runnable examples |
| Legal clarity | A recognized license file |
| Discoverability | A clear package description and project metadata |
| Contribution path | Contributing guide, code of conduct, and PR template |
| Support & trust | Issue templates and a private security reporting policy |
| Engineering health | CI, automated tests, ignore rules, docs, and release notes |

Every check has a documented weight, finding, and recommendation. A warning earns half the available points; scores are normalized to 100. See [checks.md](docs/checks.md).

## Development

```bash
git clone https://github.com/LittleCurry/oss-doctor.git
cd oss-doctor
python3 -m pip install -e .
python3 -m unittest discover -s tests -v
PYTHONPATH=src python3 -m oss_doctor check . --fail-under 90
```

No linter or test framework installation is required. We target Python 3.9+ and keep the runtime dependency-free.

## Roadmap

- [x] Local repository audit with 14 built-in checks
- [x] Console, JSON, Markdown, HTML, and SVG reports
- [x] Conservative community-file scaffolding
- [x] Reusable GitHub Action
- [ ] Remote GitHub metadata checks (description, topics, discussions)
- [ ] Custom rules through a simple configuration file
- [ ] Baseline comparison to track improvements over time
- [ ] More community health rules based on maintainer feedback

Have a use case we missed? [Open an issue](https://github.com/LittleCurry/oss-doctor/issues/new/choose). Thoughtful bug reports and small pull requests are the fastest way to shape the roadmap.

## Contributing

Contributions are welcome—from fixing a typo to designing a new check. Read [CONTRIBUTING.md](CONTRIBUTING.md), look for [`good first issue`](https://github.com/LittleCurry/oss-doctor/labels/good%20first%20issue), and tell us what would make your repository easier to maintain.

If OSS Doctor saved you time, a star helps other maintainers discover it. Please only star it if you genuinely find it useful.

## License

[MIT](LICENSE) · Made for healthier open-source communities.
