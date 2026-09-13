"""Save/load measurement sessions to JSON, with sensible Windows paths."""
from __future__ import annotations

import json
import os
from collections.abc import Iterable
from dataclasses import asdict
from datetime import UTC, datetime
from pathlib import Path

from .models import DerivedResults, Measurement

APP_NAME = "LiuAnalyzer"
SCHEMA = "liu-analyzer.session/v1"


def app_data_dir() -> Path:
    """Return %LOCALAPPDATA%\\LiuAnalyzer (created if missing)."""
    base = os.environ.get("LOCALAPPDATA")
    root = Path(base) if base else Path.home() / "AppData" / "Local"
    out = root / APP_NAME
    out.mkdir(parents=True, exist_ok=True)
    return out


def documents_dir() -> Path:
    """Best-effort Documents\\LiuAnalyzer folder (created if missing)."""
    user_profile = os.environ.get("USERPROFILE")
    base = Path(user_profile) if user_profile else Path.home()
    docs = base / "Documents"
    if not docs.exists():
        docs = base
    out = docs / APP_NAME
    out.mkdir(parents=True, exist_ok=True)
    return out


def serialize_session(
    rows: Iterable[Measurement],
    series_name: str,
    results: DerivedResults,
) -> dict:
    """Build the JSON-serializable dict for a session."""
    return {
        "schema": SCHEMA,
        "timestamp": datetime.now(UTC).isoformat(),
        "series_name": series_name,
        "measurements": [asdict(r) for r in rows],
        "results": {
            "F_th_J_per_cm2": results.F_th if results.valid else None,
            "dF_th_J_per_cm2": results.dF_th if results.valid else None,
            "beam_waist_diameter_um": results.d if results.valid else None,
            "d_beam_waist_diameter_um": results.dd if results.valid else None,
            "beam_waist_radius_um": results.w0 if results.valid else None,
            "d_beam_waist_radius_um": results.dw0 if results.valid else None,
            "E_th_mJ": results.E_th if results.valid else None,
            "R2": results.R2 if results.valid else None,
        },
    }


def save_session(
    path: Path,
    rows: Iterable[Measurement],
    series_name: str,
    results: DerivedResults,
) -> None:
    payload = serialize_session(rows, series_name, results)
    path.write_text(
        json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8"
    )


def default_save_path(series_name: str = "") -> Path:
    name = (series_name or "session").strip().replace(" ", "_") or "session"
    stamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    return documents_dir() / f"liu-{name}-{stamp}.json"


def load_session(path: Path) -> tuple[list[Measurement], str]:
    """Read a session JSON. Returns (measurements, series_name)."""
    data = json.loads(path.read_text(encoding="utf-8"))
    rows = [
        Measurement(id=int(m["id"]), E=float(m["E"]), D=float(m["D"]))
        for m in data.get("measurements", [])
    ]
    return rows, str(data.get("series_name", ""))
