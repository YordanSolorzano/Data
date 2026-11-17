from churn_dashboard.checks import (
    check_model,
    check_privacy,
    check_series_lengths,
    check_structure,
    check_totals,
    validate,
)


def test_valid_data_has_no_problems(data):
    assert validate(data) == []


def test_missing_section_is_reported(data):
    del data["model"]
    assert check_structure(data) == ["Missing section: model"]


def test_validate_stops_at_missing_sections(data):
    del data["segmentos"]
    assert validate(data) == ["Missing section: segmentos"]


def test_store_with_missing_month_is_reported(data):
    data["store_series"]["TIENDA SUR"] = [90.0]
    assert check_series_lengths(data) == ["TIENDA SUR: 1 monthly values, expected 2"]


def test_segments_must_cover_every_customer(data):
    data["segmentos"]["Fiel"] = 2
    assert any("Segments add up to 9" in problem for problem in check_totals(data))


def test_histogram_must_cover_every_customer(data):
    data["riesgo_hist"]["counts"] = [4, 5]
    assert any("Risk histogram adds up to 9" in problem for problem in check_totals(data))


def test_histogram_needs_one_more_edge_than_bins(data):
    data["riesgo_hist"]["edges"] = [0.0, 1.0]
    assert any("2 bins but 2 edges" in problem for problem in check_totals(data))


def test_store_revenue_must_match_total(data):
    data["por_tienda"][0]["revenue"] = 100.0
    assert any("revenue" in problem for problem in check_totals(data))


def test_revenue_allows_rounding_differences(data):
    data["por_tienda"][0]["revenue"] = 150.004
    assert check_totals(data) == []


def test_store_lists_must_match(data):
    data["store_series"]["TIENDA ESTE"] = [0.0, 0.0]
    assert any("different stores" in problem for problem in check_totals(data))


def test_auc_below_chance_is_reported(data):
    data["model"]["auc_logit"] = 0.4
    assert any("auc_logit" in problem for problem in check_model(data))


def test_best_auc_must_be_the_highest(data):
    data["model"]["best_auc"] = 0.70
    assert any("not the highest AUC" in problem for problem in check_model(data))


def test_roc_curve_must_not_decrease(data):
    data["model"]["roc_points"] = [[0.0, 0.0], [0.5, 0.8], [0.4, 0.9]]
    assert "ROC points must not decrease" in check_model(data)


def test_unmasked_customer_id_is_reported(data):
    data["top_vip_riesgo"][0]["cedula_masked"] = "0912345678"
    assert check_privacy(data) == ["A customer ID is not masked as ***1234"]


def test_real_store_name_is_reported(data):
    data["top_vip_riesgo"][0]["tienda"] = "Acme Downtown"
    assert check_privacy(data) == ["Store name is not anonymous: Acme Downtown"]


def test_real_brand_name_is_reported(data):
    data["top_marcas"][0]["marca"] = "Acme Shoes"
    assert check_privacy(data) == ["Brand name is not anonymous: Acme Shoes"]
