"""CLI entrypoint for dependabot-rescue."""

from __future__ import annotations

import argparse
from pathlib import Path

from dependabot_rescue.analysis import analyze_pull_request
from dependabot_rescue.providers import (
    context_from_event_payload,
    context_from_manual_fields,
    load_event_payload,
)
from dependabot_rescue.reporting import report_to_json, report_to_markdown

def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="dep-rescue")
    subparsers = parser.add_subparsers(dest="command")
    analyze = subparsers.add_parser("analyze", help="Analyze a dependency update PR.")
    analyze.add_argument("--event-path", help="Path to a GitHub event payload JSON file.")
    analyze.add_argument("--title", help="Pull request title when not using --event-path.")
    analyze.add_argument("--body-path", help="Path to a text file containing the pull request body.")
    analyze.add_argument("--author", default="", help="Pull request author when not using --event-path.")
    analyze.add_argument("--branch", default="", help="Head branch name when not using --event-path.")
    analyze.add_argument("--base-branch", default="", help="Base branch when not using --event-path.")
    analyze.add_argument(
        "--tool",
        choices=["dependabot", "renovate", "unknown"],
        help="Override the inferred update tool when not using --event-path.",
    )
    analyze.add_argument(
        "--log-file",
        action="append",
        default=[],
        help="Path to a CI log file. May be passed multiple times.",
    )
    analyze.add_argument("--format", choices=["markdown", "json"], default="markdown")
    analyze.add_argument("--output", help="Optional path to write the rendered report.")
    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()
    if args.command != "analyze":
        parser.print_help()
        return 1

    if not args.event_path and not args.title:
        parser.error("Provide --event-path or --title for the analyze command.")
    if not args.log_file:
        parser.error("Provide at least one --log-file for the analyze command.")

    body = Path(args.body_path).read_text(encoding="utf-8") if args.body_path else ""
    if args.event_path:
        context = context_from_event_payload(load_event_payload(args.event_path))
    else:
        context = context_from_manual_fields(
            title=args.title,
            body=body,
            author=args.author,
            branch=args.branch,
            base_branch=args.base_branch,
            tool=args.tool,
        )

    log_texts = [Path(path).read_text(encoding="utf-8") for path in args.log_file]
    report = analyze_pull_request(context, log_texts)
    rendered = report_to_json(report) if args.format == "json" else report_to_markdown(report)

    if args.output:
        Path(args.output).write_text(rendered, encoding="utf-8")
    else:
        print(rendered)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
