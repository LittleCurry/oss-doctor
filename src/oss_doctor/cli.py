"""Command-line interface for OSS Doctor."""

import argparse
from pathlib import Path
import sys
from typing import List, Optional

from . import __version__
from .checks import audit
from .fixes import scaffold
from .reporters import FORMATTERS, badge, console


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="oss-doctor",
        description="Actionable health checks for open-source repositories.",
    )
    parser.add_argument("--version", action="version", version=f"%(prog)s {__version__}")
    subparsers = parser.add_subparsers(dest="command", required=True)

    check = subparsers.add_parser("check", help="audit a local repository")
    check.add_argument("path", nargs="?", default=".", help="repository path (default: current directory)")
    check.add_argument("--format", choices=sorted(FORMATTERS), default="console")
    check.add_argument("--output", type=Path, help="write the report to a file")
    check.add_argument("--fail-under", type=int, default=0, metavar="SCORE",
                       help="exit 1 when the score is below SCORE (0-100)")
    check.add_argument("--no-color", action="store_true", help="disable ANSI colors")

    badge_parser = subparsers.add_parser("badge", help="generate an SVG score badge")
    badge_parser.add_argument("path", nargs="?", default=".")
    badge_parser.add_argument("--output", type=Path, default=Path("oss-doctor-badge.svg"))

    fix = subparsers.add_parser("fix", help="add missing community-health templates")
    fix.add_argument("path", nargs="?", default=".")
    fix.add_argument("--dry-run", action="store_true", help="list changes without writing files")
    return parser


def _path_argument(args: argparse.Namespace) -> Path:
    return Path(args.path)


def main(argv: Optional[List[str]] = None) -> int:
    arguments = list(sys.argv[1:] if argv is None else argv)
    commands = {"check", "badge", "fix"}
    # Keep `oss-doctor .` as a friendly shorthand for `oss-doctor check .`.
    if not arguments or (arguments[0] not in commands and arguments[0] not in {"-h", "--help", "--version"}):
        arguments.insert(0, "check")
    parser = build_parser()
    args = parser.parse_args(arguments)

    try:
        if args.command == "fix":
            created, skipped = scaffold(_path_argument(args), dry_run=args.dry_run)
            prefix = "Would create" if args.dry_run else "Created"
            for path in created:
                print(f"{prefix}: {path}")
            for path in skipped:
                print(f"Kept existing: {path}")
            print(f"{len(created)} file(s) {'planned' if args.dry_run else 'created'}; {len(skipped)} unchanged.")
            return 0

        report = audit(_path_argument(args))
        if args.command == "badge":
            args.output.write_text(badge(report), encoding="utf-8")
            print(f"Badge written to {args.output} (score {report.score}/100).")
            return 0

        if not 0 <= args.fail_under <= 100:
            parser.error("--fail-under must be between 0 and 100")
        if args.format == "console":
            use_color = not args.no_color and sys.stdout.isatty() and args.output is None
            rendered = console(report, color=use_color)
            try:
                rendered.encode(sys.stdout.encoding or "utf-8")
            except UnicodeEncodeError:
                rendered = console(report, color=use_color, unicode_output=False)
        else:
            rendered = FORMATTERS[args.format](report)
        if args.output:
            args.output.parent.mkdir(parents=True, exist_ok=True)
            args.output.write_text(rendered, encoding="utf-8")
            print(f"Report written to {args.output}")
        else:
            sys.stdout.write(rendered)
        return 1 if report.score < args.fail_under else 0
    except (OSError, ValueError) as error:
        print(f"oss-doctor: {error}", file=sys.stderr)
        return 2
    except KeyboardInterrupt:
        print("\noss-doctor: interrupted", file=sys.stderr)
        return 130


if __name__ == "__main__":
    raise SystemExit(main())
