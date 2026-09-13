"""QApplication setup and program entry point."""
from __future__ import annotations

import logging
import logging.handlers
import sys
from pathlib import Path

# matplotlib must pick a Qt backend before any pyplot/figure import.
# We use FigureCanvasQTAgg directly (not pyplot), but setting this is harmless
# and helps PyInstaller resolve the right backend.
import matplotlib

matplotlib.use("QtAgg")

from PySide6.QtCore import Qt  # noqa: E402
from PySide6.QtGui import QIcon  # noqa: E402
from PySide6.QtWidgets import QApplication  # noqa: E402

from . import __version__
from .persistence import app_data_dir  # noqa: E402
from .strings import DEFAULT_LANG  # noqa: E402
from .widgets.main_window import MainWindow  # noqa: E402

# Status bar stays yellow in both themes — that's the project's signature row.
_STATUSBAR_RULE = """
QStatusBar {
    background: #fff7d6;
    color: #5a3a00;
    border-top: 1px solid #b58a00;
    font-style: italic;
    font-size: 11px;
}
QStatusBar::item { border: 0; }
QLabel#attribution {
    color: #5a3a00;
    font-style: italic;
    font-size: 11px;
    padding-right: 10px;
}
"""

LIGHT_STYLESHEET = """
QMainWindow, QDialog { background: #f4f5f7; color: #0e1116; }
QGroupBox { color: #0e1116; }

QFrame#header { background: #fff; border-bottom: 1px solid #d6dae0; }

QToolButton {
    background: #fff;
    border: 0;
    padding: 0 14px;
    font-size: 12px;
    font-weight: 500;
    color: #2c333d;
    letter-spacing: 0.04em;
}
QToolButton[withBorder="true"] { border-right: 1px solid #e3e6ea; }
QToolButton:hover:!disabled { background: #e8f0fb; color: #2563b8; }
QToolButton:pressed:!disabled { background: #d8e4f6; }
QToolButton:disabled { color: #b5bac1; }
QToolButton::menu-indicator { image: none; width: 0; }

QLabel#promptCaret {
    color: #2563b8;
    font-family: "Consolas", "Courier New", monospace;
    font-size: 14px;
    font-weight: 600;
}
QLineEdit#seriesName {
    border: 0;
    background: transparent;
    font-family: "Consolas", "Courier New", monospace;
    font-size: 12px;
    padding: 4px 0;
    color: #0e1116;
}
QLineEdit#seriesName:focus { border-bottom: 1px solid #2563b8; }
QFrame#seriesRow { background: #fafbfc; border-top: 1px solid #e3e6ea; border-bottom: 1px solid #e3e6ea; }

QFrame#chartFrame { background: #ffffff; border-top: 1px solid #e3e6ea; border-bottom: 1px solid #e3e6ea; }

QFrame#addRow { background: #ffffff; border-bottom: 1px solid #e3e6ea; }
QLabel[class="addToken"] {
    font-family: "Cambria", "Times New Roman", serif;
    font-style: italic; color: #2c333d; font-size: 13px;
}
QLabel[class="addUnit"] { color: #6b7380; font-style: italic; font-size: 11px; }

QDoubleSpinBox#inlineInput {
    background: #fafbfc; border: 1px solid #d6dae0; border-radius: 4px;
    padding: 3px 6px;
    font-family: "Consolas", "Courier New", monospace; font-size: 12px;
    color: #0e1116;
}
QDoubleSpinBox#inlineInput:focus { border-color: #2563b8; background: #ffffff; }

QPushButton#addButton {
    background: #2563b8; color: white;
    border: 0; border-radius: 4px;
    font-size: 18px; font-weight: 300;
}
QPushButton#addButton:hover { background: #1d4f96; }
QPushButton#addButton:pressed { background: #173f78; }

QTableView {
    background: #ffffff; color: #0e1116;
    border: 0; gridline-color: transparent;
    font-family: "Consolas", "Courier New", monospace; font-size: 11px;
    selection-background-color: #e8f0fb; selection-color: #0e1116;
}
QTableView::item { padding: 3px 8px; border-bottom: 1px solid #eef0f3; }
QHeaderView::section {
    background: #fafbfc; color: #6b7380;
    font-family: "Segoe UI", sans-serif;
    font-weight: 600; font-size: 10px;
    padding: 5px 8px;
    border: 0; border-bottom: 1px solid #e3e6ea;
}

QFrame#footer { background: #fff; border-top: 1px solid #d6dae0; }

QMenu { background: #ffffff; border: 1px solid #d6dae0; padding: 4px 0; }
QMenu::item { padding: 6px 22px; color: #0e1116; }
QMenu::item:selected { background: #e8f0fb; color: #2563b8; }
""" + _STATUSBAR_RULE

DARK_STYLESHEET = """
QMainWindow, QDialog { background: #1e2024; color: #e8e8e8; }
QGroupBox { color: #e8e8e8; }
QCheckBox, QRadioButton { color: #e8e8e8; }

QFrame#header { background: #2a2d33; border-bottom: 1px solid #3a3d44; }

QToolButton {
    background: #2a2d33;
    border: 0;
    padding: 0 14px;
    font-size: 12px;
    font-weight: 500;
    color: #c8ccd2;
    letter-spacing: 0.04em;
}
QToolButton[withBorder="true"] { border-right: 1px solid #3a3d44; }
QToolButton:hover:!disabled { background: #34404f; color: #5a9bff; }
QToolButton:pressed:!disabled { background: #28344b; }
QToolButton:disabled { color: #5a5d63; }
QToolButton::menu-indicator { image: none; width: 0; }

QLabel#promptCaret {
    color: #5a9bff;
    font-family: "Consolas", "Courier New", monospace;
    font-size: 14px;
    font-weight: 600;
}
QLineEdit#seriesName {
    border: 0;
    background: transparent;
    font-family: "Consolas", "Courier New", monospace;
    font-size: 12px;
    padding: 4px 0;
    color: #e8e8e8;
}
QLineEdit#seriesName:focus { border-bottom: 1px solid #5a9bff; }
QFrame#seriesRow { background: #23262b; border-top: 1px solid #3a3d44; border-bottom: 1px solid #3a3d44; }

QFrame#chartFrame { background: #2a2d33; border-top: 1px solid #3a3d44; border-bottom: 1px solid #3a3d44; }

QFrame#addRow { background: #2a2d33; border-bottom: 1px solid #3a3d44; }
QLabel[class="addToken"] {
    font-family: "Cambria", "Times New Roman", serif;
    font-style: italic; color: #c8ccd2; font-size: 13px;
}
QLabel[class="addUnit"] { color: #9aa0a8; font-style: italic; font-size: 11px; }

QDoubleSpinBox#inlineInput {
    background: #1e2024; border: 1px solid #3a3d44; border-radius: 4px;
    padding: 3px 6px;
    font-family: "Consolas", "Courier New", monospace; font-size: 12px;
    color: #e8e8e8;
    selection-background-color: #34404f;
}
QDoubleSpinBox#inlineInput:focus { border-color: #5a9bff; background: #181a1e; }

QPushButton#addButton {
    background: #5a9bff; color: white;
    border: 0; border-radius: 4px;
    font-size: 18px; font-weight: 300;
}
QPushButton#addButton:hover { background: #4283e6; }
QPushButton#addButton:pressed { background: #2f6fcc; }

QTableView {
    background: #2a2d33; color: #e8e8e8;
    border: 0; gridline-color: transparent;
    font-family: "Consolas", "Courier New", monospace; font-size: 11px;
    selection-background-color: #34404f; selection-color: #e8e8e8;
}
QTableView::item { padding: 3px 8px; border-bottom: 1px solid #34373d; }
QHeaderView::section {
    background: #23262b; color: #9aa0a8;
    font-family: "Segoe UI", sans-serif;
    font-weight: 600; font-size: 10px;
    padding: 5px 8px;
    border: 0; border-bottom: 1px solid #3a3d44;
}

QFrame#footer { background: #2a2d33; border-top: 1px solid #3a3d44; }

QMenu { background: #2a2d33; border: 1px solid #3a3d44; padding: 4px 0; color: #e8e8e8; }
QMenu::item { padding: 6px 22px; color: #e8e8e8; }
QMenu::item:selected { background: #34404f; color: #5a9bff; }

QLineEdit, QTextBrowser { color: #e8e8e8; background: #23262b; }
""" + _STATUSBAR_RULE


def apply_theme(theme: str) -> None:
    """Apply the named theme to the live QApplication."""
    app = QApplication.instance()
    if app is None:
        return
    app.setStyleSheet(DARK_STYLESHEET if theme == "dark" else LIGHT_STYLESHEET)


def _configure_logging() -> None:
    log_path = app_data_dir() / "liu.log"
    handler = logging.handlers.RotatingFileHandler(
        log_path, maxBytes=512_000, backupCount=2, encoding="utf-8"
    )
    handler.setFormatter(
        logging.Formatter("%(asctime)s [%(levelname)s] %(name)s: %(message)s")
    )
    root = logging.getLogger()
    root.setLevel(logging.INFO)
    root.addHandler(handler)
    if sys.stderr is not None and sys.stderr.isatty():
        stream = logging.StreamHandler(sys.stderr)
        stream.setFormatter(logging.Formatter("%(levelname)s: %(message)s"))
        root.addHandler(stream)


def _resource_path(*parts: str) -> Path:
    """Resolve a packaged resource path (works in dev and inside PyInstaller)."""
    if getattr(sys, "frozen", False):
        base = Path(getattr(sys, "_MEIPASS", Path(sys.executable).parent))
    else:
        base = Path(__file__).resolve().parent
    return base.joinpath(*parts)


def main() -> int:
    _configure_logging()
    log = logging.getLogger(__name__)
    log.info("Liu Threshold Analyzer v%s starting", __version__)

    QApplication.setHighDpiScaleFactorRoundingPolicy(
        Qt.HighDpiScaleFactorRoundingPolicy.PassThrough
    )

    app = QApplication(sys.argv)
    app.setApplicationName("Liu Threshold Analyzer")
    app.setOrganizationName("LiuAnalyzer")
    app.setApplicationVersion(__version__)
    app.setStyleSheet(LIGHT_STYLESHEET)

    icon_path = _resource_path("resources", "icon.ico")
    if icon_path.exists():
        app.setWindowIcon(QIcon(str(icon_path)))

    window = MainWindow(lang=DEFAULT_LANG, version=__version__)
    window.show()
    return app.exec()


if __name__ == "__main__":
    sys.exit(main())
