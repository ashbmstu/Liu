"""Domain models for Liu's-method threshold analysis.

Pure dataclasses — no Qt or I/O dependencies. Safe to import from analysis,
persistence, tests, and any UI module.
"""
from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class Measurement:
    """A single (pulse-energy, crater-diameter) observation."""
    id: int
    E: float    # pulse energy, mJ
    D: float    # crater diameter, µm

    @property
    def D2(self) -> float:
        """Squared crater diameter, µm²."""
        return self.D * self.D


@dataclass(frozen=True, slots=True)
class Group:
    """Replicate measurements at the same pulse energy (within tolerance)."""
    E: float
    diameters: tuple[float, ...]
    ids: tuple[int, ...]

    @property
    def n(self) -> int:
        return len(self.diameters)


@dataclass(frozen=True, slots=True)
class FitResult:
    """Output of OLS fit on (ln E, D²)."""
    valid: bool
    slope: float = 0.0          # a, in µm² per nat-log
    intercept: float = 0.0      # b, in µm²
    sigma_slope: float = 0.0    # σ_a (1σ)
    sigma_intercept: float = 0.0
    sigma: float = 0.0          # residual standard deviation
    r_squared: float = 0.0
    n: int = 0


@dataclass(frozen=True, slots=True)
class DerivedResults:
    """Physical results derived from the fit."""
    valid: bool
    F_th: float = 0.0           # threshold fluence, J/cm²
    dF_th: float = 0.0          # 1σ uncertainty
    w0: float = 0.0             # beam waist radius (1/e²), µm
    dw0: float = 0.0
    d: float = 0.0              # beam waist diameter = 2 w0, µm
    dd: float = 0.0
    E_th: float = 0.0           # threshold pulse energy, mJ
    R2: float = 0.0


INVALID_FIT = FitResult(valid=False)
INVALID_RESULTS = DerivedResults(valid=False)
