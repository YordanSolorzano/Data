import pytest

from churn_dashboard.data import DashboardDataError, extract_data, load_dashboard


def test_extract_data_returns_embedded_json(html, data):
    assert extract_data(html) == data


def test_extract_data_fails_without_data_block():
    with pytest.raises(DashboardDataError, match="data-blob"):
        extract_data("<html><body>No data here</body></html>")


def test_extract_data_fails_on_broken_json():
    page = '<script id="data-blob" type="application/json">{"kpi": </script>'
    with pytest.raises(DashboardDataError, match="not valid JSON"):
        extract_data(page)


def test_extract_data_fails_when_json_is_not_an_object():
    page = '<script id="data-blob" type="application/json">[1, 2, 3]</script>'
    with pytest.raises(DashboardDataError, match="JSON object"):
        extract_data(page)


def test_load_dashboard_reads_file(tmp_path, html, data):
    page = tmp_path / "index.html"
    page.write_text(html, encoding="utf-8")
    assert load_dashboard(page) == data
