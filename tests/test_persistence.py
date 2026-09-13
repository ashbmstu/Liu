"""Tests for liu_analyzer.persistence — JSON round-trip."""
from __future__ import annotations

import json

from liu_analyzer.analysis import fit_and_derive
from liu_analyzer.models import Measurement
from liu_analyzer.persistence import (
    SCHEMA,
    load_session,
    save_session,
    serialize_session,
)

SAMPLE = [
    Measurement(1, 0.10, 22.1),
    Measurement(2, 0.50, 42.8),
    Measurement(3, 1.00, 51.6),
]


def test_serialize_session_shape():
    _, _, results = fit_and_derive(SAMPLE)
    payload = serialize_session(SAMPLE, "demo", results)
    assert payload["schema"] == SCHEMA
    assert payload["series_name"] == "demo"
    assert len(payload["measurements"]) == 3
    assert payload["measurements"][0]["E"] == 0.10
    assert payload["results"]["F_th_J_per_cm2"] is not None


def test_save_and_load_round_trip(tmp_path):
    _, _, results = fit_and_derive(SAMPLE)
    path = tmp_path / "session.json"
    save_session(path, SAMPLE, "round-trip", results)
    assert path.exists()

    rows, name = load_session(path)
    assert name == "round-trip"
    assert len(rows) == 3
    assert rows[0].E == 0.10
    assert rows[2].D == 51.6


def test_save_invalid_results_keeps_nones(tmp_path):
    """When the fit is invalid (e.g. only 1 distinct E), result fields should be null."""
    one_e = [Measurement(1, 0.5, 10.0), Measurement(2, 0.5, 11.0)]
    _, _, results = fit_and_derive(one_e)
    assert not results.valid

    path = tmp_path / "single.json"
    save_session(path, one_e, "single-E", results)
    data = json.loads(path.read_text(encoding="utf-8"))
    assert data["results"]["F_th_J_per_cm2"] is None
    assert data["results"]["beam_waist_diameter_um"] is None
