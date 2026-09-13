"""Inline 'Pulse Energy = [..] mJ ; Diameter = [..] µm  +' row."""
from __future__ import annotations

from collections.abc import Mapping

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QDoubleSpinBox,
    QFrame,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QSizePolicy,
)


def _spin(decimals: int, step: float) -> QDoubleSpinBox:
    s = QDoubleSpinBox()
    s.setProperty("class", "inlineInput")
    s.setObjectName("inlineInput")
    s.setRange(0.0, 1e6)
    s.setDecimals(decimals)
    s.setSingleStep(step)
    s.setAlignment(Qt.AlignmentFlag.AlignRight)
    s.setButtonSymbols(QDoubleSpinBox.ButtonSymbols.NoButtons)
    s.setFixedWidth(82)
    return s


class AddRow(QFrame):
    """Inline measurement-entry widget.

    Emits `submitted(E, D)` with positive values; emits `invalid()` when the
    user tries to add with E=0 or D=0.
    """

    submitted = Signal(float, float)
    invalid = Signal()

    def __init__(self, strings: Mapping[str, str], parent=None):
        super().__init__(parent)
        self.setObjectName("addRow")
        self._t = strings

        self.e_input = _spin(decimals=3, step=0.01)
        self.d_input = _spin(decimals=2, step=1.0)

        e_label = QLabel(strings["add_E_label"])
        e_label.setProperty("class", "addToken")
        e_unit = QLabel(strings["add_E_unit"])
        e_unit.setProperty("class", "addUnit")

        sep = QLabel(";")
        sep.setStyleSheet("color: #c8ccd2; padding: 0 4px;")

        d_label = QLabel(strings["add_D_label"])
        d_label.setProperty("class", "addToken")
        d_unit = QLabel(strings["add_D_unit"])
        d_unit.setProperty("class", "addUnit")

        self.add_btn = QPushButton("+")
        self.add_btn.setObjectName("addButton")
        self.add_btn.setToolTip(strings["add_button_tip"])
        self.add_btn.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
        self.add_btn.setFixedSize(34, 34)
        self.add_btn.clicked.connect(self._emit)

        # Enter-key support inside either spinbox
        for w in (self.e_input, self.d_input):
            w.lineEdit().returnPressed.connect(self._emit)

        layout = QHBoxLayout(self)
        layout.setContentsMargins(12, 10, 12, 10)
        layout.setSpacing(6)
        layout.addWidget(e_label)
        layout.addWidget(self.e_input)
        layout.addWidget(e_unit)
        layout.addWidget(sep)
        layout.addWidget(d_label)
        layout.addWidget(self.d_input)
        layout.addWidget(d_unit)
        layout.addStretch(1)
        layout.addWidget(self.add_btn)

    def _emit(self) -> None:
        e = self.e_input.value()
        d = self.d_input.value()
        if e > 0 and d > 0:
            self.submitted.emit(e, d)
            self.e_input.setValue(0.0)
            self.d_input.setValue(0.0)
            self.e_input.setFocus()
        else:
            self.invalid.emit()
