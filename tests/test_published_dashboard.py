"""Checks on the page that is actually published to GitHub Pages."""

from pathlib import Path

import pytest

from churn_dashboard import load_dashboard, validate
from churn_dashboard.__main__ import main

DASHBOARD = Path(__file__).resolve().parents[1] / "site" / "index.html"


@pytest.fixture(scope="module")
def published():
    return load_dashboard(DASHBOARD)


def test_published_dashboard_is_consistent_and_anonymous(published):
    assert validate(published) == []


def test_published_dashboard_covers_seven_stores(published):
    assert len(published["store_series"]) == 7


def test_command_line_accepts_published_dashboard(capsys):
    assert main([str(DASHBOARD)]) == 0
    assert "OK" in capsys.readouterr().out


def test_command_line_reports_missing_file(tmp_path, capsys):
    assert main([str(tmp_path / "missing.html")]) == 2
    assert "Could not read the dashboard" in capsys.readouterr().err
