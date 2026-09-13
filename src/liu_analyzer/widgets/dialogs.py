"""Modal dialogs: Instructions, About, Settings."""
from __future__ import annotations

import base64
import sys
from collections.abc import Mapping
from pathlib import Path

from PySide6.QtWidgets import (
    QButtonGroup,
    QCheckBox,
    QDialog,
    QDialogButtonBox,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QRadioButton,
    QTextBrowser,
    QVBoxLayout,
)


def _resource_dir() -> Path:
    """Locate liu_analyzer/resources/ in dev and inside PyInstaller bundles."""
    if getattr(sys, "frozen", False):
        base = Path(getattr(sys, "_MEIPASS", Path(sys.executable).parent))
        return base / "liu_analyzer" / "resources"
    return Path(__file__).resolve().parent.parent / "resources"


def _data_uri(filename: str, mime: str = "image/png") -> str:
    """Read a bundled file and return a base64 data URI for HTML embedding."""
    path = _resource_dir() / filename
    if not path.exists():
        return ""
    return f"data:{mime};base64,{base64.b64encode(path.read_bytes()).decode('ascii')}"


def _make_html_dialog(parent, title: str, html: str, close_text: str | None = None) -> QDialog:
    d = QDialog(parent)
    d.setWindowTitle(title)
    d.setModal(True)
    d.resize(480, 440)

    layout = QVBoxLayout(d)
    layout.setContentsMargins(0, 0, 0, 0)
    layout.setSpacing(0)

    header = QLabel(title)
    header.setStyleSheet(
        "background:#fff; color:#0e1116; padding:14px 18px; "
        "font-weight:600; font-size:14px; border-bottom:1px solid #e3e6ea;"
    )
    layout.addWidget(header)

    body = QTextBrowser()
    body.setHtml(html)
    body.setOpenExternalLinks(True)
    body.setStyleSheet(
        "QTextBrowser { background:#fff; border:0; padding:14px 20px; "
        "font-size:12px; color:#2c333d; }"
    )
    layout.addWidget(body, 1)

    buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Close)
    # Qt's own translations are not bundled, so standard buttons would stay
    # in English whatever the interface language.
    if close_text:
        buttons.button(QDialogButtonBox.StandardButton.Close).setText(close_text)
    buttons.rejected.connect(d.reject)
    buttons.accepted.connect(d.accept)
    buttons.setStyleSheet(
        "QDialogButtonBox { padding: 8px 18px; background:#fff; "
        "border-top:1px solid #e3e6ea; }"
    )
    layout.addWidget(buttons)

    return d


def show_instructions(parent, strings: Mapping[str, str]) -> None:
    html = strings["instructions_html"]
    scheme_uri = _data_uri("laser_scheme.png")
    if scheme_uri:
        caption = strings.get("scheme_caption", "Gaussian beam through a focusing lens")
        scheme_html = (
            f'<p align="center" style="margin-top:10px">'
            f'<img src="{scheme_uri}" width="400"/></p>'
            f'<p align="center" style="color:#6b7380; font-size:11px; '
            f'font-style:italic; margin-top:-4px">{caption}</p>'
        )
    else:
        scheme_html = ""
    # New layout: HTML embeds {scheme} inside section 1.
    # Older layout (no placeholder): append at the bottom for backward compat.
    if "{scheme}" in html:
        html = html.replace("{scheme}", scheme_html)
    else:
        html += scheme_html
    _make_html_dialog(parent, strings["instructions_title"], html, strings["button_close"]).exec()


def show_about(parent, strings: Mapping[str, str], version: str = "1.0.0") -> None:
    _make_html_dialog(
        parent,
        strings["about_title"],
        strings["about_html"].format(version=version),
        strings["button_close"],
    ).exec()


class SettingsDialog(QDialog):
    """X-axis scale (log/linear), theme (light/dark), fit-line on/off."""

    def __init__(self, parent, strings: Mapping[str, str], current: dict):
        super().__init__(parent)
        self.setWindowTitle(strings["settings_title"])
        self.setModal(True)
        self.resize(360, 280)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(18, 16, 18, 14)
        layout.setSpacing(12)

        # X-axis scale
        scale_box = QGroupBox(strings["settings_scale"])
        sl = QHBoxLayout(scale_box)
        self.r_log = QRadioButton(strings["settings_scale_log"])
        self.r_lin = QRadioButton(strings["settings_scale_linear"])
        sl.addWidget(self.r_log)
        sl.addWidget(self.r_lin)
        sl.addStretch(1)
        scale_group = QButtonGroup(self)
        scale_group.addButton(self.r_log)
        scale_group.addButton(self.r_lin)
        if current.get("x_scale", "log") == "log":
            self.r_log.setChecked(True)
        else:
            self.r_lin.setChecked(True)
        layout.addWidget(scale_box)

        # Theme
        theme_box = QGroupBox(strings["settings_theme"])
        tl = QHBoxLayout(theme_box)
        self.r_light = QRadioButton(strings["settings_theme_light"])
        self.r_dark = QRadioButton(strings["settings_theme_dark"])
        tl.addWidget(self.r_light)
        tl.addWidget(self.r_dark)
        tl.addStretch(1)
        theme_group = QButtonGroup(self)
        theme_group.addButton(self.r_light)
        theme_group.addButton(self.r_dark)
        if current.get("theme", "light") == "dark":
            self.r_dark.setChecked(True)
        else:
            self.r_light.setChecked(True)
        layout.addWidget(theme_box)

        # Fit line toggle
        self.show_fit = QCheckBox(strings["settings_show_fit"])
        self.show_fit.setChecked(bool(current.get("show_fit", True)))
        layout.addWidget(self.show_fit)

        layout.addStretch(1)

        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        )
        buttons.button(QDialogButtonBox.StandardButton.Ok).setText(strings["button_ok"])
        buttons.button(QDialogButtonBox.StandardButton.Cancel).setText(strings["button_cancel"])
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

    def values(self) -> dict:
        return {
            "x_scale": "log" if self.r_log.isChecked() else "linear",
            "theme": "dark" if self.r_dark.isChecked() else "light",
            "show_fit": self.show_fit.isChecked(),
        }
