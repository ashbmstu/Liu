"""Main application window — assembles the UI and wires the data flow."""
from __future__ import annotations

import logging
from pathlib import Path

from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QAction
from PySide6.QtWidgets import (
    QDialog,
    QFileDialog,
    QFrame,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMainWindow,
    QMenu,
    QSizePolicy,
    QStatusBar,
    QToolButton,
    QVBoxLayout,
    QWidget,
)

from ..analysis import fit_and_derive
from ..models import Measurement
from ..persistence import default_save_path, documents_dir, load_session, save_session
from ..strings import DEFAULT_LANG, STRINGS
from ..strings import get as get_strings
from .add_row import AddRow
from .chart_canvas import ChartCanvas, export_plot_with_table_png
from .data_table import DataTable
from .dialogs import SettingsDialog, show_about, show_instructions

log = logging.getLogger(__name__)

WINDOW_WIDTH = 540   # ≈ 520-px layout + Qt chrome
TOAST_MS = 2200

DEFAULT_SETTINGS = {"x_scale": "log", "theme": "light", "show_fit": True}

# Demo dataset shown on first launch, in muted grey, until the user adds
# their first real measurement (or clicks New). The Measurement IDs here
# don't conflict with real ones because the demo is dismissed before any
# real row is appended.
DEMO_ROWS: list[Measurement] = [
    Measurement(1, 0.2, 20.0),
    Measurement(2, 0.2, 30.0),
    Measurement(3, 0.5, 50.0),
    Measurement(4, 0.5, 60.0),
    Measurement(5, 1.0, 75.0),
    Measurement(6, 1.0, 80.0),
]


class _BarButton(QToolButton):
    """Flat button with an optional right border, used in the header/footer."""

    def __init__(self, text: str, *, with_border: bool = True, parent=None):
        super().__init__(parent)
        self.setText(text)
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        self.setMinimumHeight(40)
        self.setProperty("withBorder", with_border)
        self.setCursor(Qt.CursorShape.PointingHandCursor)


class MainWindow(QMainWindow):
    """Top-level window orchestrating data, chart, and all subwidgets."""

    measurementAdded = Signal(int)

    def __init__(self, lang: str = DEFAULT_LANG, version: str = "1.0.0"):
        super().__init__()
        self._lang = lang
        self._t = get_strings(lang)
        self._version = version
        self._settings = dict(DEFAULT_SETTINGS)

        self.setMinimumWidth(WINDOW_WIDTH)
        self.resize(WINDOW_WIDTH, 800)

        self._rows: list[Measurement] = []
        self._next_id = 1
        self._demo_active = True   # dismissed on first Add or New

        # Persistent status-bar attribution (right-aligned, always visible)
        self._status = QStatusBar()
        self._status.setSizeGripEnabled(False)
        self.setStatusBar(self._status)
        self._attribution = QLabel()
        self._attribution.setObjectName("attribution")
        self._status.addPermanentWidget(self._attribution)

        self._build_central()
        self._apply_chart_settings()
        # Apply theme via the stylesheet helper after construction
        from ..app import apply_theme
        apply_theme(self._settings["theme"])
        self._refresh()

    # ── builders ───────────────────────────────────────────────────────

    def _build_central(self) -> None:
        """Build (or rebuild, on language change) the central widget hierarchy."""
        self.setWindowTitle(self._t["title"])
        self._attribution.setText(self._t["attribution"])

        central = QWidget()
        self.setCentralWidget(central)
        v = QVBoxLayout(central)
        v.setContentsMargins(0, 0, 0, 0)
        v.setSpacing(0)

        v.addWidget(self._build_header())
        v.addWidget(self._build_series_row())
        v.addWidget(self._build_chart_frame())
        v.addWidget(self._build_add_row())
        v.addWidget(self._build_table(), 1)
        v.addWidget(self._build_footer())

    def _build_header(self) -> QFrame:
        bar = QFrame()
        bar.setObjectName("header")
        h = QHBoxLayout(bar)
        h.setContentsMargins(0, 0, 0, 0)
        h.setSpacing(0)

        new_btn = _BarButton(self._t["header_new"])
        new_btn.clicked.connect(self._on_new)
        h.addWidget(new_btn, 1)

        settings_btn = _BarButton(self._t["header_settings"])
        settings_btn.clicked.connect(self._on_settings)
        h.addWidget(settings_btn, 1)

        lang_btn = _BarButton(self._t["header_lang"] + " ▾", with_border=False)
        lang_btn.setPopupMode(QToolButton.ToolButtonPopupMode.InstantPopup)
        menu = QMenu(lang_btn)
        for code in STRINGS:
            label = self._t.get(f"lang_{code}", code.upper())
            if code == self._lang:
                label = "● " + label
            act = QAction(label, menu)
            act.triggered.connect(lambda _checked=False, c=code: self._on_lang(c))
            menu.addAction(act)
        lang_btn.setMenu(menu)
        h.addWidget(lang_btn, 1)

        return bar

    def _build_series_row(self) -> QFrame:
        bar = QFrame()
        bar.setObjectName("seriesRow")
        layout = QHBoxLayout(bar)
        layout.setContentsMargins(14, 6, 14, 6)
        layout.setSpacing(8)

        prompt = QLabel("›")
        prompt.setObjectName("promptCaret")
        layout.addWidget(prompt)

        self._series_input = QLineEdit()
        self._series_input.setObjectName("seriesName")
        self._series_input.setPlaceholderText(self._t["series_placeholder"])
        layout.addWidget(self._series_input, 1)
        return bar

    def _build_chart_frame(self) -> QFrame:
        frame = QFrame()
        frame.setObjectName("chartFrame")
        layout = QVBoxLayout(frame)
        layout.setContentsMargins(8, 8, 8, 4)
        layout.setSpacing(0)

        self._chart = ChartCanvas(self._t, parent=frame)
        layout.addWidget(self._chart)
        return frame

    def _build_add_row(self) -> AddRow:
        self._add_row = AddRow(self._t)
        self._add_row.submitted.connect(self._on_add)
        self._add_row.invalid.connect(self._on_invalid)
        return self._add_row

    def _build_table(self) -> DataTable:
        self._table = DataTable(self._t)
        self._table.deleteRequested.connect(self._on_delete)
        self._table.hoverChanged.connect(self._on_hover)
        return self._table

    def _build_footer(self) -> QFrame:
        bar = QFrame()
        bar.setObjectName("footer")
        h = QHBoxLayout(bar)
        h.setContentsMargins(0, 0, 0, 0)
        h.setSpacing(0)

        instr = _BarButton(self._t["footer_instructions"])
        instr.clicked.connect(lambda: show_instructions(self, self._t))
        h.addWidget(instr, 1)

        open_btn = _BarButton(self._t["footer_open"])
        open_btn.clicked.connect(self._on_open)
        h.addWidget(open_btn, 1)

        save = _BarButton(self._t["footer_save"])
        save.clicked.connect(self._on_save)
        h.addWidget(save, 1)

        about = _BarButton(self._t["footer_about"], with_border=False)
        about.clicked.connect(lambda: show_about(self, self._t, self._version))
        h.addWidget(about, 1)

        return bar

    # ── actions ────────────────────────────────────────────────────────

    @property
    def _showing_demo(self) -> bool:
        """Demo is visible only on first launch, before any real interaction."""
        return self._demo_active and not self._rows

    def _on_new(self) -> None:
        self._rows = []
        self._next_id = 1
        self._demo_active = False  # New = clean slate; demo doesn't come back
        self._series_input.clear()
        self._refresh()
        log.info("session reset")

    def _on_add(self, e: float, d: float) -> None:
        if self._showing_demo:
            self._demo_active = False  # first real input dismisses the demo
            log.info("demo dismissed by first measurement")
        m = Measurement(id=self._next_id, E=e, D=d)
        self._rows.append(m)
        self._next_id += 1
        log.info("added measurement id=%d E=%.4f D=%.4f", m.id, m.E, m.D)
        self._refresh()
        self.measurementAdded.emit(m.id)

    def _on_invalid(self) -> None:
        self._toast(self._t["add_error"])

    def _on_delete(self, mid: int) -> None:
        before = len(self._rows)
        self._rows = [r for r in self._rows if r.id != mid]
        if len(self._rows) < before:
            log.info("deleted measurement id=%d", mid)
            self._refresh()

    def _on_hover(self, mid: int | None) -> None:
        self._chart.set_hover(mid)
        self._table.set_hover(mid)

    def _on_save(self) -> None:
        if self._showing_demo or not self._rows:
            self._toast(self._t.get("save_no_data", "nothing to save yet"))
            return
        groups, fit, results = fit_and_derive(self._rows)
        suggested = default_save_path(self._series_input.text()).with_suffix(".png")
        png_filter = self._t.get("save_filter_png", "PNG image (*.png)")
        json_filter = self._t.get("save_filter_json", "JSON session (*.json)")
        path_str, selected_filter = QFileDialog.getSaveFileName(
            self,
            self._t["footer_save"],
            str(suggested),
            f"{png_filter};;{json_filter}",
        )
        if not path_str:
            return
        path = Path(path_str)
        ext = path.suffix.lower()
        is_png = ext == ".png" or (ext != ".json" and "png" in (selected_filter or "").lower())
        if is_png and ext != ".png":
            path = path.with_suffix(".png")
        if not is_png and ext != ".json":
            path = path.with_suffix(".json")
        try:
            if is_png:
                export_plot_with_table_png(
                    path,
                    rows=self._rows,
                    groups=groups,
                    fit=fit,
                    results=results,
                    theme=self._settings["theme"],
                    x_scale=self._settings["x_scale"],
                    show_fit=self._settings["show_fit"],
                    strings=self._t,
                    series_name=self._series_input.text(),
                )
            else:
                save_session(path, self._rows, self._series_input.text(), results)
        except OSError as err:
            log.exception("save failed")
            self._toast(self._t["save_error"].format(err=err))
            return
        self._toast(self._t["save_ok"].format(path=path.name))
        log.info("saved %s to %s", "PNG" if is_png else "JSON", path)

    def _on_open(self) -> None:
        json_filter = self._t["save_filter_json"]
        path_str, _ = QFileDialog.getOpenFileName(
            self, self._t["footer_open"], str(documents_dir()), json_filter
        )
        if not path_str:
            return
        path = Path(path_str)
        try:
            rows, series_name = load_session(path)
        except (OSError, ValueError) as err:
            log.exception("open failed")
            self._toast(self._t["open_error"].format(err=err))
            return
        self._rows = rows
        self._next_id = max((r.id for r in rows), default=0) + 1
        self._demo_active = False
        self._series_input.setText(series_name)
        self._refresh()
        self._toast(self._t["open_ok"].format(path=path.name))
        log.info("opened %d measurements from %s", len(rows), path)

    def _on_settings(self) -> None:
        dialog = SettingsDialog(self, self._t, self._settings)
        if dialog.exec() != QDialog.DialogCode.Accepted:
            return
        new = dialog.values()
        old_theme = self._settings["theme"]
        self._settings = new
        if new["theme"] != old_theme:
            from ..app import apply_theme
            apply_theme(new["theme"])
        self._apply_chart_settings()
        self._refresh()
        log.info("settings updated: %s", new)

    def _on_lang(self, code: str) -> None:
        if code == self._lang or code not in STRINGS:
            return
        # Preserve state across rebuild
        rows = self._rows
        next_id = self._next_id
        series_text = self._series_input.text()

        self._lang = code
        self._t = get_strings(code)
        self._build_central()
        self._apply_chart_settings()

        # Restore state
        self._rows = rows
        self._next_id = next_id
        self._series_input.setText(series_text)
        self._refresh()
        log.info("language switched to %s", code)

    # ── helpers ────────────────────────────────────────────────────────

    def _apply_chart_settings(self) -> None:
        self._chart.set_strings(self._t)
        self._chart.set_theme(self._settings["theme"])
        self._chart.set_x_scale(self._settings["x_scale"])
        self._chart.set_show_fit(self._settings["show_fit"])

    def _refresh(self) -> None:
        is_demo = self._showing_demo
        display_rows = DEMO_ROWS if is_demo else self._rows
        groups, fit, results = fit_and_derive(display_rows)
        self._chart.update_data(groups, fit, results, is_demo=is_demo)
        self._table.set_rows(display_rows, is_demo=is_demo)
        grouped_ids = {gid for g in groups if g.n > 1 for gid in g.ids}
        self._table.set_grouped_ids(grouped_ids)

    def _toast(self, msg: str) -> None:
        self._status.showMessage(msg, TOAST_MS)
