# Checks and scoring

OSS Doctor runs 14 local, read-only checks. It does not use repository popularity, owner identity, or Git credentials in its score.

| Check | Weight | Pass condition |
|---|---:|---|
| README | 10 | A recognized README with at least 300 characters |
| Quick start | 8 | Installation and usage headings plus a code block |
| License | 12 | A non-empty license or copying file |
| Project metadata | 5 | A description in common Python, JavaScript, or Rust metadata |
| Contributing guide | 8 | A guide at the root, in `.github`, or in `docs` |
| Code of conduct | 5 | A non-empty code of conduct |
| Security policy | 8 | A non-empty security policy |
| Issue templates | 6 | Modern issue templates or a legacy issue template |
| Pull request template | 5 | One or more PR templates |
| Continuous integration | 10 | Configuration for a common CI provider |
| Automated tests | 10 | A conventional test directory or matching test file |
| Git ignore rules | 3 | A non-empty `.gitignore` |
| Release notes | 5 | A changelog or release notes file |
| Documentation | 5 | Documentation in `docs` or a README documentation link |

## Score calculation

- **Pass:** all points for the check.
- **Warning:** half the points for the check.
- **Fail:** no points.

The earned points are divided by the total possible points and normalized to 100. Grade boundaries are A (90+), B (80+), C (70+), D (60+), and F (below 60).

A warning means an improvement is recommended but the area may be intentionally minimal. For example, a small library might not need a standalone changelog during its first days. Use judgment; do not add empty bureaucracy merely to chase a score.

## Scope and limitations

The audit is heuristic. It checks for useful signals, not whether documentation is accurate or tests are effective. Project metadata detection understands descriptions in `pyproject.toml`, `setup.cfg`, `package.json`, and simple single-line quoted `description` values in the `[package]` section of `Cargo.toml`. Multiline or workspace-inherited Cargo descriptions are not resolved; other manifests still signal project structure.

The scanner limits individual text reads and avoids following symlinked top-level community files. Always review generated templates before publishing them. Do not put private vulnerability details, secrets, or personal information in reports.

## JSON schema

JSON output includes a `schema_version`, normalized repository path, score, grade, status counts, and a result array. Each result has `check_id`, `title`, `status`, `message`, `recommendation`, and `weight`. Consumers should tolerate additional fields in future minor versions.
