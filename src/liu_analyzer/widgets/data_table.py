"""Data table for measurements with sort, hover sync, and row deletion."""
from __future__ import annotations

from collections.abc import Mapping

from PySide6.QtCore import (
    QAbstractTableModel,
    QModelIndex,
    QSortFilterProxyModel,
    Qt,
    Signal,
)
from PySide6.QtGui import QColor
from PySide6.QtWidgets import (
    QAbstractItemView,
    QHeaderView,
    QTableView,
)

from ..models import Measurement

# (key, header label) — labels resolved at runtime from strings dict.
COL_IDX, COL_E, COL_D, COL_D2, COL_DEL = 0, 1, 2, 3, 4
COLUMN_KEYS = ("idx", "E", "D", "D2", "del")


class MeasurementsModel(QAbstractTableModel):
    def __init__(self, headers: Mapping[str, str], parent=None):
        super().__init__(parent)
        self._headers = dict(headers)
        self._rows: list[Measurement] = []
        self._grouped_ids: set[int] = set()
        self._hover_id: int | None = None
        self._is_demo: bool = False

    # ── public API ─────────────────────────────────────────────────────

    def set_rows(self, rows: list[Measurement], is_demo: bool = False) -> None:
        self.beginResetModel()
        self._rows = list(rows)
        self._is_demo = bool(is_demo)
        self.endResetModel()

    @property
    def is_demo(self) -> bool:
        return self._is_demo

    def set_grouped_ids(self, ids: set[int]) -> None:
        self._grouped_ids = set(ids)
        self._signal_visual_change()

    def set_hover(self, mid: int | None) -> None:
        if mid == self._hover_id:
            return
        self._hover_id = mid
        self._signal_visual_change()

    def measurement_at(self, row: int) -> Measurement | None:
        if 0 <= row < len(self._rows):
            return self._rows[row]
        return None

    def _signal_visual_change(self) -> None:
        if not self._rows:
            return
        top = self.index(0, 0)
        bot = self.index(self.rowCount() - 1, self.columnCount() - 1)
        self.dataChanged.emit(top, bot, [Qt.ItemDataRole.BackgroundRole])

    # ── Qt model interface ─────────────────────────────────────────────

    def rowCount(self, parent=QModelIndex()) -> int:
        return 0 if parent.isValid() else len(self._rows)

    def columnCount(self, parent=QModelIndex()) -> int:
        return 0 if parent.isValid() else len(COLUMN_KEYS)

    def headerData(self, section, orientation, role=Qt.ItemDataRole.DisplayRole):
        if role != Qt.ItemDataRole.DisplayRole:
            return None
        if orientation != Qt.Orientation.Horizontal:
            return None
        key = COLUMN_KEYS[section]
        if key == "idx":
            return self._headers.get("table_idx", "#")
        if key == "E":
            return self._headers.get("table_E", "E")
        if key == "D":
            return self._headers.get("table_D", "D")
        if key == "D2":
            return self._headers.get("table_D2", "D²")
        if key == "del":
            return ""
        return None

    def data(self, index, role=Qt.ItemDataRole.DisplayRole):
        if not index.isValid():
            return None
        row = index.row()
        if not (0 <= row < len(self._rows)):
            return None
        r = self._rows[row]
        key = COLUMN_KEYS[index.column()]

        if role == Qt.ItemDataRole.DisplayRole:
            if key == "idx":
                return f"{row + 1:02d}"
            if key == "E":
                return f"{r.E:.3f}".rstrip("0").rstrip(".") or "0"
            if key == "D":
                return f"{r.D:.2f}"
            if key == "D2":
                return f"{r.D2:.2f}"
            if key == "del":
                # Demo rows are read-only — no delete affordance.
                return "" if self._is_demo else "−"
            return ""

        if role == Qt.ItemDataRole.TextAlignmentRole:
            if key in ("E", "D", "D2"):
                return int(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
            return int(Qt.AlignmentFlag.AlignCenter)

        if role == Qt.ItemDataRole.BackgroundRole and self._hover_id is not None and (
            r.id == self._hover_id
            or (r.id in self._grouped_ids and self._hover_id in self._grouped_ids)
        ):
            return QColor("#e8f0fb")

        if role == Qt.ItemDataRole.ForegroundRole:
            if self._is_demo:
                # All cells in demo mode go to muted grey, italic-feeling.
                return QColor("#9aa0a8")
            if key == "idx":
                return QColor("#6b7380")
            if key == "del":
                return QColor("#888888")

        if role == Qt.ItemDataRole.FontRole and self._is_demo:
            from PySide6.QtGui import QFont
            f = QFont()
            f.setItalic(True)
            return f

        if role == Qt.ItemDataRole.UserRole:
            # Numeric sort key
            if key == "idx":
                return r.id
            if key == "E":
                return r.E
            if key == "D":
                return r.D
            if key == "D2":
                return r.D2
            return 0

        if role == Qt.ItemDataRole.ToolTipRole and key == "del":
            return self._headers.get("delete_tip", "Delete row")

        return None


class DataTable(QTableView):
    """Table view backed by MeasurementsModel via a numeric sort proxy."""

    deleteRequested = Signal(int)
    hoverChanged = Signal(object)  # int id or None

    def __init__(self, strings: Mapping[str, str], parent=None):
        super().__init__(parent)
        self._model = MeasurementsModel(strings, self)
        self._proxy = QSortFilterProxyModel(self)
        self._proxy.setSourceModel(self._model)
        self._proxy.setSortRole(Qt.ItemDataRole.UserRole)
        self.setModel(self._proxy)

        self.setSortingEnabled(True)
        self.setSelectionMode(QAbstractItemView.SelectionMode.NoSelection)
        self.setShowGrid(False)
        self.setMouseTracking(True)
        self.verticalHeader().setVisible(False)

        h = self.horizontalHeader()
        h.setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        h.setSectionResizeMode(COL_IDX, QHeaderView.ResizeMode.ResizeToContents)
        h.setSectionResizeMode(COL_DEL, QHeaderView.ResizeMode.Fixed)
        h.resizeSection(COL_DEL, 32)
        h.setStretchLastSection(False)

        self.setMaximumHeight(220)

        self.clicked.connect(self._on_click)
        self.entered.connect(self._on_entered)
        self.viewportEntered.connect(lambda: self.hoverChanged.emit(None))

    # ── public API ─────────────────────────────────────────────────────

    def set_rows(self, rows: list[Measurement], is_demo: bool = False) -> None:
        self._model.set_rows(rows, is_demo=is_demo)

    def set_grouped_ids(self, ids: set[int]) -> None:
        self._model.set_grouped_ids(ids)

    def set_hover(self, mid: int | None) -> None:
        self._model.set_hover(mid)

    # ── helpers ────────────────────────────────────────────────────────

    def _row_id(self, proxy_index) -> int | None:
        src = self._proxy.mapToSource(proxy_index)
        m = self._model.measurement_at(src.row())
        return m.id if m else None

    def _on_click(self, idx) -> None:
        if self._model.is_demo:
            return  # demo rows are read-only
        if COLUMN_KEYS[idx.column()] == "del":
            mid = self._row_id(idx)
            if mid is not None:
                self.deleteRequested.emit(mid)

    def _on_entered(self, idx) -> None:
        self.hoverChanged.emit(self._row_id(idx))

    def leaveEvent(self, e):
        super().leaveEvent(e)
        self.hoverChanged.emit(None)
