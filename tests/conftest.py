"""Shared fixtures: a small, valid dataset that each test can break on purpose."""

from __future__ import annotations

import copy
import json
from typing import Any

import pytest

VALID_DATA: dict[str, Any] = {
    "kpi": {"total_clientes": 10, "total_transacciones": 30, "total_revenue": 300.0},
    "months": ["2025-01", "2025-02"],
    "store_series": {"TIENDA NORTE": [100.0, 50.0], "TIENDA SUR": [90.0, 60.0]},
    "por_tienda": [
        {"local": "TIENDA NORTE", "revenue": 150.0, "clientes": 6, "transacciones": 18},
        {"local": "TIENDA SUR", "revenue": 150.0, "clientes": 5, "transacciones": 12},
    ],
    "top_marcas": [{"marca": "MARCA A", "revenue": 200.0}],
    "top_lineas": [{"linea": "ZAPATO", "revenue": 200.0}],
    "riesgo_hist": {"counts": [4, 6], "edges": [0.0, 0.5, 1.0]},
    "segmentos": {"En riesgo": 7, "Fiel": 3},
    "top_vip_riesgo": [{"cedula_masked": "***1234", "tienda": "TIENDA NORTE"}],
    "model": {
        "auc_logit": 0.70,
        "auc_gb": 0.72,
        "best_auc": 0.72,
        "n_train": 7,
        "n_test": 3,
        "roc_points": [[0.0, 0.0], [0.2, 0.6], [1.0, 1.0]],
    },
}


@pytest.fixture
def data() -> dict[str, Any]:
    return copy.deepcopy(VALID_DATA)


@pytest.fixture
def html(data: dict[str, Any]) -> str:
    blob = json.dumps(data)
    return f'<html><script id="data-blob" type="application/json">{blob}</script></html>'
