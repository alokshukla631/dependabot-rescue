"""CLI entrypoint for dependabot-rescue."""

from __future__ import annotations

import argparse


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="dep-rescue")
    subparsers = parser.add_subparsers(dest="command")
    analyze = subparsers.add_parser("analyze", help="Analyze a dependency update PR.")
    analyze.add_argument("--event-path", help="Path to a GitHub event payload JSON file.")
    analyze.add_argument(
        "--log-file",
        action="append",
        default=[],
        help="Path to a CI log file. May be passed multiple times.",
    )
    analyze.add_argument("--format", choices=["markdown", "json"], default="markdown")
    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()
    if args.command != "analyze":
        parser.print_help()
        return 1

    print("dependabot-rescue MVP is being built. Analysis command wiring comes next.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
