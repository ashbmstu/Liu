#!/usr/bin/env python3
"""Regenerate the screenshots in docs/img from the application itself.

    .venv\\Scripts\\python.exe tools\\screenshots.py

The window is laid out and rendered but never mapped to the desktop, so this
can run while you are doing something else and nothing flashes up in front of
you. Qt's "offscreen" platform plugin would be the obvious way to do that, but
it ships no font database on Windows and every label comes out as a row of
empty boxes; WA_DontShowOnScreen keeps the real platform, and therefore the
real font rendering, while still keeping the window out of the way.

Running this is also a blunt but effective smoke test: it builds every widget,
feeds in measurements, and draws the chart, so an exception here means the
interface is broken even though the unit tests still pass.
"""
from __future__ import annotations

import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "docs" / "img"

# Render at twice the logical size so the images stay sharp on a high-density
# display. Set QT_SCALE_FACTOR=1 for images matching a 96-dpi screen.
os.environ.setdefault("QT_SCALE_FACTOR", "2")
sys.path.insert(0, str(ROOT / "src"))

from PySide6.QtCore import Qt  # noqa: E402
from PySide6.QtWidgets import QApplication  # noqa: E402

import liu_analyzer.app as appmod  # noqa: E402
from liu_analyzer.strings import STRINGS  # noqa: E402
from liu_analyzer.widgets import dialogs  # noqa: E402
from liu_analyzer.widgets.main_window import MainWindow  # noqa: E402

# Pulse energy in mJ, crater diameter in um. Two energies are repeated so that
# the error bars appear, since they are part of what the screenshot is showing.
DATA = [
    (0.05, 12.4),
    (0.10, 22.1),
    (0.10, 21.0),
    (0.20, 30.5),
    (0.50, 42.8),
    (1.00, 51.6),
    (1.00, 53.2),
    (2.00, 60.1),
]

app = QApplication(sys.argv[:1])
app.setStyleSheet(appmod.LIGHT_STYLESHEET)


def settle(rounds: int = 8) -> None:
    for _ in range(rounds):
        app.processEvents()


def save(widget, name: str) -> None:
    settle()
    OUT.mkdir(parents=True, exist_ok=True)
    pixmap = widget.grab()
    pixmap.save(str(OUT / name), "PNG")
    print(f"  {name:<22} {pixmap.width()}x{pixmap.height()}")


def main_window(theme: str) -> MainWindow:
    window = MainWindow(lang="en", version="1.0.0")
    window._settings["theme"] = theme
    window._settings["x_scale"] = "log"
    appmod.apply_theme(theme)
    window.setAttribute(Qt.WA_DontShowOnScreen, True)
    window.resize(980, 940)
    window.show()
    settle()
    for energy, diameter in DATA:
        window._on_add(energy, diameter)
    window._apply_chart_settings()
    window._refresh()
    settle()
    return window


def instructions(parent) -> object:
    """Build the Instructions dialog without the modal exec() that would block."""
    strings = STRINGS["en"]
    html = strings["instructions_html"]
    uri = dialogs._data_uri("laser_scheme.png")
    scheme = ""
    if uri:
        caption = strings.get("scheme_caption", "")
        scheme = (
            f'<p align="center" style="margin-top:10px"><img src="{uri}" width="400"/></p>'
            f'<p align="center" style="color:#6b7380; font-size:11px; '
            f'font-style:italic; margin-top:-4px">{caption}</p>'
        )
    html = html.replace("{scheme}", scheme) if "{scheme}" in html else html + scheme

    dialog = dialogs._make_html_dialog(
        parent, strings["instructions_title"], html, strings["button_close"]
    )
    dialog.setAttribute(Qt.WA_DontShowOnScreen, True)
    dialog.resize(560, 706)
    dialog.show()
    return dialog


def main() -> int:
    light = main_window("light")
    save(light, "main-window.png")

    save(main_window("dark"), "dark-theme.png")

    appmod.apply_theme("light")
    save(instructions(light), "instructions.png")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
