"""Liu's method math.

Liu, J. M. (1982). Simple technique for measurements of pulsed Gaussian-beam
spot sizes. Optics Letters, 7(5), 196.

Plot D² vs ln(E); linear regression yields:
    slope a = 2 w₀²        ⇒  w₀ = √(a/2),  d = 2 w₀
    intercept b such that  ln(E_th) = -b/a
                           E_th     = exp(-b/a)
                           F_th     = 2 E_th / (π w₀²)

All inputs in mJ and µm; F_th comes out in J/cm² (note the unit conversions
inside derive_results()).
"""
from __future__ import annotations

import math
from collections.abc import Iterable

import numpy as np

from .models import (
    INVALID_FIT,
    INVALID_RESULTS,
    DerivedResults,
    FitResult,
    Group,
    Measurement,
)

GROUP_TOLERANCE_PCT = 0.5  # energies within this % are treated as replicates


def group_rows(
    rows: Iterable[Measurement], tol_pct: float = GROUP_TOLERANCE_PCT
) -> list[Group]:
    """Group rows whose pulse energies differ by less than `tol_pct` percent.

    Returned list is sorted ascending by energy.
    """
    accum: list[dict] = []
    for r in rows:
        if not (r.E > 0 and r.D > 0):
            continue
        match = next(
            (g for g in accum if abs(g["E"] - r.E) / g["E"] < tol_pct / 100),
            None,
        )
        if match is None:
            accum.append({"E": r.E, "diameters": [r.D], "ids": [r.id]})
        else:
            match["diameters"].append(r.D)
            match["ids"].append(r.id)
    accum.sort(key=lambda g: g["E"])
    return [
        Group(E=g["E"], diameters=tuple(g["diameters"]), ids=tuple(g["ids"]))
        for g in accum
    ]


def fit_liu(groups: list[Group]) -> FitResult:
    """OLS fit on (ln E, D²), expanding replicates to individual points."""
    distinct = len({g.E for g in groups})
    if distinct < 2:
        return INVALID_FIT

    xs: list[float] = []
    ys: list[float] = []
    for g in groups:
        for d in g.diameters:
            xs.append(math.log(g.E))
            ys.append(d * d)

    if len(xs) < 2:
        return INVALID_FIT

    x = np.asarray(xs, dtype=float)
    y = np.asarray(ys, dtype=float)
    n = len(x)
    mx = float(x.mean())
    my = float(y.mean())
    Sxx = float(np.sum((x - mx) ** 2))
    Sxy = float(np.sum((x - mx) * (y - my)))
    Syy = float(np.sum((y - my) ** 2))
    if Sxx <= 0:
        return INVALID_FIT

    a = Sxy / Sxx
    b = my - a * mx
    SSres = float(np.sum((y - (a * x + b)) ** 2))

    if n > 2:
        sigma = math.sqrt(SSres / (n - 2))
        sa = sigma / math.sqrt(Sxx)
        sb = sigma * math.sqrt(1.0 / n + (mx * mx) / Sxx)
        cov_ab = -mx * sigma * sigma / Sxx
    else:
        sigma, sa, sb, cov_ab = 0.0, 0.0, 0.0, 0.0

    r2 = 1.0 - SSres / Syy if Syy > 0 else 1.0

    return FitResult(
        valid=True,
        slope=a,
        intercept=b,
        sigma_slope=sa,
        sigma_intercept=sb,
        cov_slope_intercept=cov_ab,
        sigma=sigma,
        r_squared=r2,
        n=n,
    )


def derive_results(fit: FitResult) -> DerivedResults:
    """Convert OLS fit into physical quantities (F_th, w₀, d) with 1σ uncertainties.

    Slope a [µm²] = 2 w₀² ⇒  w₀ [µm] = √(a/2),  d [µm] = 2 w₀ = √(2a)
    x-intercept ln(E_th [mJ]) = -b/a
    F_th [J/cm²] = 2·E_th [J] / (π · w₀² [cm²])
    """
    if not fit.valid or fit.slope <= 0:
        return INVALID_RESULTS

    a, b = fit.slope, fit.intercept
    sa, sb = fit.sigma_slope, fit.sigma_intercept
    cov_ab = fit.cov_slope_intercept

    w0_um = math.sqrt(a / 2)
    d_um = 2 * w0_um

    # Δd = (1 / √(2a)) · σ_a
    dd_um = sa / math.sqrt(2 * a) if sa > 0 and a > 0 else 0.0
    dw0_um = dd_um / 2

    lnEth = -b / a
    E_th_mJ = math.exp(lnEth)

    # Convert to SI: E in J (×1e-3 from mJ), w₀ in cm (×1e-4 from µm)
    w0_cm = w0_um * 1e-4
    E_th_J = E_th_mJ * 1e-3
    F_th = 2.0 * E_th_J / (math.pi * w0_cm * w0_cm)

    # 1σ on F_th via log-derivative propagation through the full 2x2
    # covariance of the fit. Slope and intercept of an OLS line are
    # correlated, so the cross term is not optional.
    # ln(F_th) = const + (-b/a) - ln(a/2)
    # ∂ln(F_th)/∂b = -1/a
    # ∂ln(F_th)/∂a = b/a² - 1/a
    dlnF_db = -1.0 / a
    dlnF_da = b / (a * a) - 1.0 / a
    var_lnF = (
        (dlnF_da * sa) ** 2
        + (dlnF_db * sb) ** 2
        + 2.0 * dlnF_da * dlnF_db * cov_ab
    )
    sigma_lnF = math.sqrt(max(var_lnF, 0.0))
    dF_th = F_th * sigma_lnF

    return DerivedResults(
        valid=True,
        F_th=F_th,
        dF_th=dF_th,
        w0=w0_um,
        dw0=dw0_um,
        d=d_um,
        dd=dd_um,
        E_th=E_th_mJ,
        R2=fit.r_squared,
    )


def fit_and_derive(
    rows: Iterable[Measurement],
) -> tuple[list[Group], FitResult, DerivedResults]:
    """Group → fit → derive in one shot. Convenience for UI code."""
    groups = group_rows(rows)
    fit = fit_liu(groups)
    res = derive_results(fit)
    return groups, fit, res
