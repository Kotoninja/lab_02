import argparse
import sys
from pathlib import Path

from . import errors
from .analysis import Stats
from .parser import get_parser
from .report import create_report


def service(args):
    stats = Stats()

    data_parser = get_parser(args.format)
    for path in set(args.input):
        for event in data_parser(path, args.skip_invalid, stats):
            stats.add(event)

    create_report(args.output, stats)


def create_parser() -> argparse.ArgumentParser:
    """Generate main parser

    Returns:
        argparse.ArgumentParser: parser
    """
    parser = argparse.ArgumentParser(
        prog="streamstats",
        description="CLI app for analyze csv or json files",
    )
    subparsers = parser.add_subparsers(required=True)

    analyze_parser = subparsers.add_parser("analyze")
    analyze_parser.add_argument(
        "input",
        nargs="+",
        type=Path,
    )
    analyze_parser.add_argument(
        "--format",
        nargs="?",
        choices=["csv", "jsonl"],
        required=True,
    )
    analyze_parser.add_argument(
        "--output",
        required=True,
        type=Path,
    )
    analyze_parser.add_argument(
        "--skip-invalid",
        action="store_true",
    )
    analyze_parser.set_defaults(func=service)

    return parser


if __name__ == "__main__":
    parser = create_parser()

    args = parser.parse_args()
    try:
        args.func(args)
        sys.stdout.write("\n")
        sys.exit(0)
    except (errors.StreamStatsError, FileNotFoundError) as e:
        sys.stderr.write(f"\033[31mError: {e}\033[0m\n")
        sys.exit(2)
