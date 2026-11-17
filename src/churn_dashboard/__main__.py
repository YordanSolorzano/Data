"""Command line entry point: ``python -m churn_dashboard site/index.html``."""

from __future__ import annotations

import argparse
import sys

from churn_dashboard.checks import validate
from churn_dashboard.data import DashboardDataError, load_dashboard


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Validate the churn dashboard data.")
    parser.add_argument("path", help="Path to the dashboard HTML file")
    args = parser.parse_args(argv)

    try:
        data = load_dashboard(args.path)
    except (OSError, DashboardDataError) as error:
        print(f"Could not read the dashboard: {error}", file=sys.stderr)
        return 2

    problems = validate(data)
    for problem in problems:
        print(f"FAIL  {problem}")
    if problems:
        return 1
    print("OK    The dashboard data is consistent and anonymous.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
