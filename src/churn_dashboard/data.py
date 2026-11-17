"""Read the JSON data embedded in the dashboard HTML page."""

from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any

DATA_BLOB_PATTERN = re.compile(
    r'<script id="data-blob" type="application/json">(?P<json>.*?)</script>',
    re.DOTALL,
)


class DashboardDataError(ValueError):
    """Raised when the dashboard page has no readable data block."""


def extract_data(html: str) -> dict[str, Any]:
    """Return the dashboard data embedded in ``html``.

    The page stores everything it draws in one ``<script id="data-blob">`` tag,
    so the published numbers can be checked without opening a browser.
    """
    match = DATA_BLOB_PATTERN.search(html)
    if match is None:
        raise DashboardDataError('The page has no <script id="data-blob"> tag.')
    try:
        data = json.loads(match.group("json"))
    except json.JSONDecodeError as error:
        raise DashboardDataError(f"The data block is not valid JSON: {error}") from error
    if not isinstance(data, dict):
        raise DashboardDataError("The data block must be a JSON object.")
    return data


def load_dashboard(path: str | Path) -> dict[str, Any]:
    """Read a dashboard HTML file and return its embedded data."""
    return extract_data(Path(path).read_text(encoding="utf-8"))
