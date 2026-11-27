# Contributing to OSS Doctor

Thanks for helping make open-source repositories easier to understand and maintain. Bug reports, documentation improvements, new checks, and focused code changes are all welcome.

## Good places to start

- Check issues labeled **good first issue** and **help wanted**.
- Run OSS Doctor on a repository you maintain and report confusing findings.
- Improve a recommendation so it tells the user exactly what to do next.
- Add tests for a repository layout that is not detected correctly.

Please open an issue before a large new feature so we can agree on scope.

## Development setup

Requires Python 3.9 or newer. There are no runtime dependencies.

```bash
git clone https://github.com/LittleCurry/oss-doctor.git
cd oss-doctor
python3 -m pip install -e .
python3 -m unittest discover -s tests -v
PYTHONPATH=src python3 -m oss_doctor check . --fail-under 95
```

## Design principles

1. **Actionable over judgmental:** every finding should suggest a practical next step.
2. **Zero runtime dependencies:** use the Python standard library unless there is an exceptional reason not to.
3. **Read-only audits:** `check` and `badge` must never modify the audited repository.
4. **Conservative fixes:** `fix` never overwrites existing content.
5. **Portable:** support Linux, macOS, and Windows and Python 3.9+.
6. **Safe output:** escape report content and never include credentials or unrelated files.

## Adding a check

- Add one focused function in `src/oss_doctor/checks.py` and register it in `CHECKS`.
- Give it a stable, lowercase `check_id`, a fair weight, and a specific recommendation.
- Keep file reads bounded and handle missing or malformed files without crashing.
- Add passing, warning/failing, and edge-case tests.
- Update `docs/checks.md` and the README summary when appropriate.

## Pull requests

- Keep each pull request focused.
- Add or update tests and documentation.
- Run the full test suite before submitting.
- Describe the user-visible change and how you tested it.
- Do not include secrets, personal information, or unrelated generated files.

By contributing, you agree that your work is licensed under the MIT License.
