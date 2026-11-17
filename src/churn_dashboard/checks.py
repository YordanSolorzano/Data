"""Consistency and privacy checks for the dashboard data.

Every check takes the data dictionary and returns a list of problems written
for a person to read. An empty list means the check passed.
"""

from __future__ import annotations

import math
import re
from collections.abc import Callable
from itertools import pairwise
from typing import Any

Data = dict[str, Any]
Check = Callable[[Data], list[str]]

REQUIRED_KEYS = (
    "kpi",
    "months",
    "store_series",
    "por_tienda",
    "top_marcas",
    "top_lineas",
    "riesgo_hist",
    "segmentos",
    "top_vip_riesgo",
    "model",
)

MASKED_ID = re.compile(r"^\*{3}\d{4}$")
ANONYMOUS_STORE = re.compile(r"^TIENDA [A-Z ]+$")
ANONYMOUS_BRAND = re.compile(r"^MARCA [A-Z]$")
REVENUE_TOLERANCE = 0.01


def check_structure(data: Data) -> list[str]:
    """Every section the page draws must be present."""
    return [f"Missing section: {key}" for key in REQUIRED_KEYS if key not in data]


def check_series_lengths(data: Data) -> list[str]:
    """Each store needs exactly one sales value per month."""
    expected = len(data["months"])
    return [
        f"{store}: {len(series)} monthly values, expected {expected}"
        for store, series in data["store_series"].items()
        if len(series) != expected
    ]


def check_totals(data: Data) -> list[str]:
    """Figures shown in different sections must add up to the same totals."""
    problems: list[str] = []
    kpi = data["kpi"]
    customers = kpi["total_clientes"]

    segment_total = sum(data["segmentos"].values())
    if segment_total != customers:
        problems.append(f"Segments add up to {segment_total}, expected {customers} customers")

    histogram_total = sum(data["riesgo_hist"]["counts"])
    if histogram_total != customers:
        problems.append(
            f"Risk histogram adds up to {histogram_total}, expected {customers} customers"
        )

    bins = len(data["riesgo_hist"]["counts"])
    edges = len(data["riesgo_hist"]["edges"])
    if edges != bins + 1:
        problems.append(f"Risk histogram has {bins} bins but {edges} edges")

    transactions = sum(store["transacciones"] for store in data["por_tienda"])
    if transactions != kpi["total_transacciones"]:
        problems.append(
            f"Stores add up to {transactions} transactions, expected {kpi['total_transacciones']}"
        )

    revenue = sum(store["revenue"] for store in data["por_tienda"])
    if not math.isclose(revenue, kpi["total_revenue"], abs_tol=REVENUE_TOLERANCE):
        problems.append(
            f"Stores add up to {revenue:.2f} revenue, expected {kpi['total_revenue']:.2f}"
        )

    table_stores = {store["local"] for store in data["por_tienda"]}
    if table_stores != set(data["store_series"]):
        problems.append("The store table and the monthly series list different stores")

    return problems


def check_model(data: Data) -> list[str]:
    """Model metrics must be plausible and agree with each other."""
    problems: list[str] = []
    model = data["model"]
    aucs = {name: value for name, value in model.items() if name.startswith("auc_")}

    for name, value in aucs.items():
        if not 0.5 <= value <= 1.0:
            problems.append(f"{name} = {value} is outside the range 0.5 to 1.0")

    if aucs and model["best_auc"] != max(aucs.values()):
        problems.append(
            f"best_auc = {model['best_auc']} is not the highest AUC ({max(aucs.values())})"
        )

    if model["n_train"] <= 0 or model["n_test"] <= 0:
        problems.append("Train and test sets must both contain customers")

    roc = model["roc_points"]
    if any(not (0 <= fpr <= 1 and 0 <= tpr <= 1) for fpr, tpr in roc):
        problems.append("ROC points must stay between 0 and 1")
    if any(later[0] < earlier[0] or later[1] < earlier[1] for earlier, later in pairwise(roc)):
        problems.append("ROC points must not decrease")

    return problems


def check_privacy(data: Data) -> list[str]:
    """The published page must not expose customers, stores or brands."""
    problems: list[str] = []

    for customer in data["top_vip_riesgo"]:
        if not MASKED_ID.match(customer["cedula_masked"]):
            problems.append("A customer ID is not masked as ***1234")
            break

    stores = set(data["store_series"]) | {store["local"] for store in data["por_tienda"]}
    stores |= {customer["tienda"] for customer in data["top_vip_riesgo"]}
    problems.extend(
        f"Store name is not anonymous: {store}"
        for store in sorted(stores)
        if not ANONYMOUS_STORE.match(store)
    )

    problems.extend(
        f"Brand name is not anonymous: {brand['marca']}"
        for brand in data["top_marcas"]
        if not ANONYMOUS_BRAND.match(brand["marca"])
    )
    return problems


CHECKS: tuple[Check, ...] = (
    check_series_lengths,
    check_totals,
    check_model,
    check_privacy,
)


def validate(data: Data) -> list[str]:
    """Run every check and return all problems found."""
    problems = check_structure(data)
    if problems:
        return problems
    for check in CHECKS:
        problems.extend(check(data))
    return problems
