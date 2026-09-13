"""Tests for liu_analyzer.analysis — verify Liu's-method math against reference values."""
from __future__ import annotations

import math

import pytest

from liu_analyzer.analysis import (
    derive_results,
    fit_and_derive,
    fit_liu,
    group_rows,
)
from liu_analyzer.models import Measurement

# A realistic series with two repeated energies, so that grouping and the
# replicate statistics are exercised as well as the fit.
SEED = [
    Measurement(1, 0.05, 12.4),
    Measurement(2, 0.10, 22.1),
    Measurement(3, 0.10, 21.0),
    Measurement(4, 0.20, 30.5),
    Measurement(5, 0.50, 42.8),
    Measurement(6, 1.00, 51.6),
    Measurement(7, 1.00, 53.2),
    Measurement(8, 2.00, 60.1),
]


# ── grouping ─────────────────────────────────────────────────────────────────

def test_group_rows_groups_replicates():
    groups = group_rows(SEED)
    # Distinct E-values in seed: 0.05, 0.10, 0.20, 0.50, 1.00, 2.00 → 6 groups
    assert len(groups) == 6
    # Sorted ascending
    assert [g.E for g in groups] == [0.05, 0.10, 0.20, 0.50, 1.00, 2.00]
    # Replicate at E=0.10 collected 2 diameters
    g010 = next(g for g in groups if g.E == 0.10)
    assert g010.n == 2
    assert set(g010.diameters) == {22.1, 21.0}
    # Replicate at E=1.00 also collected 2
    g100 = next(g for g in groups if g.E == 1.00)
    assert g100.n == 2


def test_group_rows_skips_nonpositive():
    rows = [
        Measurement(1, 0.5, 10.0),
        Measurement(2, 0.0, 20.0),    # E=0
        Measurement(3, -1.0, 5.0),    # negative
        Measurement(4, 1.0, 0.0),     # D=0
        Measurement(5, 2.0, -3.0),    # negative D
        Measurement(6, 1.0, 15.0),    # OK, replicates with id 4 (but that's filtered out)
    ]
    groups = group_rows(rows)
    assert len(groups) == 2
    assert {g.E for g in groups} == {0.5, 1.0}


# ── fit ──────────────────────────────────────────────────────────────────────

def test_fit_returns_invalid_for_one_distinct_energy():
    rows = [Measurement(1, 0.5, 10.0), Measurement(2, 0.5, 12.0)]
    fit = fit_liu(group_rows(rows))
    assert fit.valid is False


def test_fit_simple_synthetic():
    """Fit a noiseless line: D² = 100·ln(E) + 50.

    With slope a = 100 µm² ⇒ w₀ = √50 µm ≈ 7.07 µm, d ≈ 14.14 µm.
    """
    a_true, b_true = 100.0, 50.0
    rows = []
    for i, E in enumerate([0.1, 0.5, 1.0, 2.0, 5.0]):
        D2 = a_true * math.log(E) + b_true
        D = math.sqrt(max(D2, 0.0))
        rows.append(Measurement(i + 1, E, D))

    fit = fit_liu(group_rows(rows))
    assert fit.valid
    assert fit.slope == pytest.approx(a_true, rel=1e-9)
    assert fit.intercept == pytest.approx(b_true, rel=1e-9)
    assert fit.r_squared == pytest.approx(1.0, abs=1e-12)


def test_fit_seed_matches_reference():
    """Pin the OLS results on the seed dataset as a regression check.

    The seed (8 measurements across 6 distinct energies) yields a stable
    OLS fit. These reference numbers were captured from this implementation
    on first run; if either the seed or the math drifts, this test fails.
    """
    fit = fit_liu(group_rows(SEED))
    assert fit.valid
    assert fit.slope == pytest.approx(961.6611, abs=1e-3)
    assert fit.intercept == pytest.approx(2725.9120, abs=1e-3)
    assert fit.r_squared == pytest.approx(0.9766330, abs=1e-6)
    assert fit.n == 8


def test_derive_seed_known_values():
    """Pin the derived physical quantities on the seed dataset."""
    _, _, res = fit_and_derive(SEED)
    assert res.valid
    assert res.w0 == pytest.approx(21.92785, abs=1e-3)
    assert res.d == pytest.approx(43.85570, abs=1e-3)
    assert res.F_th == pytest.approx(7.7775, abs=1e-3)
    assert res.E_th == pytest.approx(0.05874, abs=1e-4)


def test_derive_results_invalid_when_slope_negative():
    from liu_analyzer.models import FitResult
    fit = FitResult(valid=True, slope=-1.0, intercept=10.0)
    res = derive_results(fit)
    assert res.valid is False


def test_derive_results_units_and_sign():
    """For the seed, F_th, w₀, d should all be positive and sane."""
    _, fit, res = fit_and_derive(SEED)
    assert fit.valid and res.valid
    assert res.F_th > 0
    assert res.w0 > 0
    assert res.d == pytest.approx(2 * res.w0, rel=1e-12)
    # Sanity bounds for typical fs-laser ablation experiments
    assert 0.01 < res.F_th < 50.0     # J/cm²
    assert 1.0 < res.w0 < 200.0       # µm


def test_derive_results_uncertainty_nonnegative():
    _, _, res = fit_and_derive(SEED)
    assert res.dF_th >= 0
    assert res.dd >= 0
    assert res.dw0 >= 0
