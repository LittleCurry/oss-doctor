# CI integration

## Reusable GitHub Action

```yaml
name: Repository health
on:
  pull_request:
  push:
    branches: [main]
permissions:
  contents: read
jobs:
  health:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: LittleCurry/oss-doctor@v0.1.0
        id: doctor
        with:
          path: .
          fail-under: 70
      - run: echo "Repository health is ${{ steps.doctor.outputs.score }}/100"
```

For reproducible automation, replace `main` with a specific release tag. The action runs on the standard Python setup action, writes a Markdown job summary, and exposes the numeric `score` output.

## Save a report artifact

```yaml
- uses: actions/setup-python@v5
  with:
    python-version: "3.12"
- run: python -m pip install "git+https://github.com/LittleCurry/oss-doctor.git"
- run: oss-doctor check . --format html --output health.html
- uses: actions/upload-artifact@v4
  with:
    name: repository-health
    path: health.html
    retention-days: 14
```

## Adopt gradually

1. Run locally and fix findings that matter to users.
2. Record the current score and set `fail-under` slightly below it.
3. Raise the baseline only when improvements land.
4. Keep the audit informational for repositories that intentionally differ from the defaults.

A health score should support maintainers, not block urgent fixes or discourage experiments.
