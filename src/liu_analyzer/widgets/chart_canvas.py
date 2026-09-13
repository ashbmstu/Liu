"""matplotlib chart for D² vs E with fit overlay, error bars, in-plot legend.

Theme-aware (light/dark), supports log or linear X-axis and toggling the fit
line. Strings (axis labels) are passed in via the strings dict.

The chart-rendering code is factored into a free function `render_chart_into`
so it can be reused by the PNG export path (`export_plot_with_table_png`).
"""
from __future__ import annotations

import math
import textwrap
from collections.abc import Iterable, Mapping, Sequence
from pathlib import Path

import numpy as np
from matplotlib import font_manager, rcParams
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure

from ..models import DerivedResults, FitResult, Group, Measurement

# matplotlib's own fonts have no Chinese glyphs. A CJK font listed after the
# usual family is used glyph by glyph for whatever that family lacks, so Latin
# text keeps its look and Chinese labels still render.
_CJK_CANDIDATES = ("Microsoft YaHei", "Noto Sans CJK SC", "PingFang SC", "SimSun")
_installed = {font.name for font in font_manager.fontManager.ttflist}
CJK_FALLBACK = [name for name in _CJK_CANDIDATES if name in _installed]
rcParams["font.family"] = ["sans-serif", *CJK_FALLBACK]
SERIF = ["serif", *CJK_FALLBACK]

THEMES = {
    "light": {
        "bg": "white",
        "panel": "#fcfcfd",
        "ink": "#1a1a1a",
        "grid": "#cfcfcd",
        "muted": "#888888",
        "accent": "#2563b8",
    },
    "dark": {
        "bg": "#2a2d33",
        "panel": "#23262b",
        "ink": "#e8e8e8",
        "grid": "#3a3d44",
        "muted": "#9aa0a8",
        "accent": "#5a9bff",
    },
}


def _nice_max(v: float) -> float:
    """Round v up to a 'nice' number (1, 2, or 5 × 10^n)."""
    if v <= 0:
        return 1.0
    exp = 10 ** math.floor(math.log10(v))
    f = v / exp
    nf = 1 if f <= 1 else 2 if f <= 2 else 5 if f <= 5 else 10
    return nf * exp


def render_chart_into(
    fig: Figure,
    ax,
    *,
    groups: Sequence[Group],
    fit: FitResult | None,
    results: DerivedResults | None,
    theme: str = "light",
    x_scale: str = "log",
    show_fit: bool = True,
    strings: Mapping[str, str],
    hover_id: int | None = None,
    is_demo: bool = False,
) -> None:
    """Draw the Liu plot onto the given matplotlib axes (and parent figure).

    When `is_demo=True`, all data marks (points, fit line, errorbars, legend
    text) collapse to a muted grey palette and the fit line is dashed, so
    placeholder demo data is visually distinct from a real measurement.
    """
    c = THEMES.get(theme, THEMES["light"])
    if is_demo:
        # Collapse the foreground palette to muted grey; keep panel/bg/grid
        # so the chart frame still looks consistent with the active theme.
        c = {**c, "ink": c["muted"], "accent": c["muted"]}
    fit_linestyle = "--" if is_demo else "-"
    fit_alpha = 0.7 if is_demo else 1.0
    fig.set_facecolor(c["bg"])
    ax.clear()
    ax.set_facecolor(c["panel"])
    for s in ("top", "right"):
        ax.spines[s].set_visible(False)
    for s in ("left", "bottom"):
        ax.spines[s].set_color(c["ink"])
        ax.spines[s].set_linewidth(1.0)
    ax.tick_params(axis="both", colors=c["ink"], labelsize=9)
    for label in ax.get_xticklabels() + ax.get_yticklabels():
        label.set_color(c["ink"])

    x_label = strings["axis_x_log"] if x_scale == "log" else strings["axis_x_linear"]
    ax.set_xlabel(x_label, fontsize=10, color=c["ink"])
    ax.set_ylabel(strings["axis_y"], fontsize=10, color=c["ink"])

    # X-axis range
    all_E = [g.E for g in groups if g.E > 0]
    if all_E:
        e_min = min(all_E)
        e_max = max(all_E)
        if e_min == e_max:
            e_min /= 3
            e_max *= 3
        if x_scale == "log":
            lo = math.log10(e_min)
            hi = math.log10(e_max)
            e_min = 10 ** (math.floor(lo * 2) / 2 - 0.1)
            e_max = 10 ** (math.ceil(hi * 2) / 2 + 0.1)
        else:
            # Linear scale: always anchor the left edge at zero so the
            # axis origin is visible (and the fit's x-intercept at E_th
            # always falls inside the visible range).
            e_min = 0.0
            e_max = e_max * 1.1 if e_max > 0 else 1.0
    else:
        e_min, e_max = (0.01, 10.0) if x_scale == "log" else (0.0, 1.0)
    ax.set_xscale("log" if x_scale == "log" else "linear")
    ax.set_xlim(e_min, e_max)

    # Y-axis range
    all_D2 = [d * d for g in groups for d in g.diameters]
    y_max = max(all_D2) * 1.15 if all_D2 else 10000.0
    if y_max < 10:
        y_max = 10.0
    y_max = _nice_max(y_max)
    ax.set_ylim(0, y_max)

    ax.grid(True, which="major", linestyle="--", linewidth=0.5,
            color=c["grid"], alpha=0.7)

    # Regression line
    if show_fit and fit and fit.valid:
        if x_scale == "log":
            xx = np.linspace(math.log(e_min), math.log(e_max), 64)
            yy = fit.slope * xx + fit.intercept
            mask = (yy >= 0) & (yy <= y_max)
            if mask.sum() >= 2:
                ax.plot(np.exp(xx[mask]), yy[mask],
                        color=c["accent"], linewidth=1.4,
                        linestyle=fit_linestyle, alpha=fit_alpha, zorder=3)
        else:
            xs = np.linspace(max(e_min, 1e-12), e_max, 256)
            yy = fit.slope * np.log(xs) + fit.intercept
            mask = (yy >= 0) & (yy <= y_max)
            if mask.sum() >= 2:
                ax.plot(xs[mask], yy[mask],
                        color=c["accent"], linewidth=1.4,
                        linestyle=fit_linestyle, alpha=fit_alpha, zorder=3)

        if abs(fit.slope) > 1e-9:
            ln_eth = -fit.intercept / fit.slope
            e_th = math.exp(ln_eth)
            if e_min <= e_th <= e_max:
                ax.axvline(e_th, ymin=0, ymax=0.04,
                           color=c["accent"], linewidth=1.0, alpha=fit_alpha)
                ax.text(
                    e_th, y_max * 0.025, "$E_{th}$",
                    color=c["accent"], ha="center", va="bottom",
                    fontsize=9, fontstyle="italic", alpha=fit_alpha,
                )

    # Data points + error bars
    for g in groups:
        d2s = np.asarray([d * d for d in g.diameters], dtype=float)
        mean = float(d2s.mean())
        err = float(d2s.std(ddof=1)) if d2s.size >= 2 else 0.0
        is_hover = hover_id is not None and hover_id in g.ids

        if err > 0:
            ax.errorbar(
                [g.E], [mean], yerr=[err],
                fmt="none", ecolor=c["ink"], elinewidth=1, capsize=4, capthick=1,
                zorder=4,
            )

        if is_hover:
            ax.scatter([g.E], [mean], s=160, color=c["accent"], alpha=0.18, zorder=4)

        if d2s.size > 1:
            ax.scatter(
                [g.E] * d2s.size, d2s.tolist(),
                marker="_", color=c["muted"], s=20, linewidths=0.8, zorder=4,
            )

        face = c["accent"] if is_hover else c["panel"]
        edge = c["accent"] if is_hover else c["ink"]
        size = 56 if is_hover else 30
        ax.scatter(
            [g.E], [mean],
            s=size, facecolors=face, edgecolors=edge,
            linewidths=1.4 if is_hover else 1.2, zorder=5,
        )

    # In-plot legend (top-left)
    x_text = 0.04
    y0 = 0.96
    if fit and fit.valid and results and results.valid:
        lines = [
            ("$F_{th}$", f"{results.F_th:.2f} ± {results.dF_th:.2f}", "J/cm²"),
            ("$w_0$", f"{results.w0:.2f} ± {results.dw0:.2f}", "µm"),
            ("$d$", f"{results.d:.2f} ± {results.dd:.2f}", "µm"),
            ("$R^2$", f"{fit.r_squared:.4f}", ""),
        ]
        for i, (sym, val, unit) in enumerate(lines):
            txt = f"{sym} = {val}"
            if unit:
                txt += f"  {unit}"
            ax.text(
                x_text, y0 - i * 0.07, txt, transform=ax.transAxes,
                fontsize=10, color=c["ink"], ha="left", va="top",
                family=SERIF,
            )
    else:
        msg = strings.get("fit_insufficient", "≥ 2 distinct pulse energies required")
        wrapped = textwrap.fill(msg, width=24)
        ax.text(
            x_text, y0, wrapped, transform=ax.transAxes,
            fontsize=9, color=c["muted"], ha="left", va="top",
            family=SERIF, style="italic", linespacing=1.4,
        )


def export_plot_with_table_png(
    path: Path,
    *,
    rows: Iterable[Measurement],
    groups: Sequence[Group],
    fit: FitResult | None,
    results: DerivedResults | None,
    theme: str,
    x_scale: str,
    show_fit: bool,
    strings: Mapping[str, str],
    series_name: str = "",
    dpi: int = 150,
) -> None:
    """Save a composite PNG containing the plot on top and the data table below."""
    from matplotlib.backends.backend_agg import FigureCanvasAgg

    rows = list(rows)
    n_rows = len(rows)
    chart_h = 4.6
    table_h = max(0.6, 0.28 * (n_rows + 1)) if n_rows else 0.6
    title_h = 0.4 if series_name else 0.15
    fig_h = chart_h + table_h + title_h + 0.6
    fig = Figure(figsize=(7.0, fig_h), dpi=dpi, layout="constrained")
    FigureCanvasAgg(fig)  # bind an offscreen canvas

    c = THEMES.get(theme, THEMES["light"])
    fig.patch.set_facecolor(c["bg"])

    height_ratios = [chart_h, table_h]
    gs = fig.add_gridspec(2, 1, height_ratios=height_ratios)
    ax_chart = fig.add_subplot(gs[0])
    ax_table = fig.add_subplot(gs[1])

    render_chart_into(
        fig, ax_chart,
        groups=groups, fit=fit, results=results,
        theme=theme, x_scale=x_scale, show_fit=show_fit, strings=strings,
    )

    if series_name.strip():
        fig.suptitle(series_name.strip(), fontsize=12, color=c["ink"])

    # Data table
    ax_table.axis("off")
    ax_table.set_facecolor(c["bg"])
    if n_rows:
        cell_text = [
            [str(i + 1), f"{r.E:.3f}", f"{r.D:.2f}", f"{r.D * r.D:.2f}"]
            for i, r in enumerate(rows)
        ]
        col_labels = [
            strings.get("table_idx", "#"),
            strings.get("table_E", "E"),
            strings.get("table_D", "D"),
            strings.get("table_D2", "D²"),
        ]
        table = ax_table.table(
            cellText=cell_text,
            colLabels=col_labels,
            loc="upper center",
            cellLoc="center",
            colLoc="center",
        )
        table.auto_set_font_size(False)
        table.set_fontsize(9)
        table.scale(0.85, 1.15)
        for (r_idx, _), cell in table.get_celld().items():
            cell.set_edgecolor(c["grid"])
            cell.set_facecolor(c["panel"] if r_idx == 0 else c["bg"])
            cell.get_text().set_color(c["ink"])
            if r_idx == 0:
                cell.get_text().set_weight("bold")
    else:
        ax_table.text(
            0.5, 0.5, strings.get("table_empty", "(no measurements)"),
            transform=ax_table.transAxes,
            ha="center", va="center",
            color=c["muted"], style="italic", fontsize=10,
        )

    fig.savefig(
        path,
        dpi=dpi,
        bbox_inches="tight",
        facecolor=fig.get_facecolor(),
    )


class ChartCanvas(FigureCanvas):
    """matplotlib canvas. Configurable theme, X-axis scale, fit-line visibility."""

    def __init__(
        self,
        strings: Mapping[str, str],
        parent=None,
        width: float = 5.2,
        height: float = 3.6,
        dpi: int = 100,
    ):
        self._figure = Figure(figsize=(width, height), dpi=dpi)
        super().__init__(self._figure)
        self.setParent(parent)
        self.setMinimumHeight(280)

        self._t = strings
        self._theme = "light"
        self._x_scale = "log"
        self._show_fit = True

        self._ax = self._figure.add_subplot(111)
        self._hover_id: int | None = None
        self._groups: list[Group] = []
        self._fit: FitResult | None = None
        self._results: DerivedResults | None = None
        self._is_demo: bool = False
        self.update_data([], None, None)

    # ── public API ─────────────────────────────────────────────────────

    def set_strings(self, strings: Mapping[str, str]) -> None:
        self._t = strings
        self._redraw()

    def set_theme(self, theme: str) -> None:
        if theme not in THEMES:
            theme = "light"
        self._theme = theme
        self._redraw()

    def set_x_scale(self, scale: str) -> None:
        self._x_scale = "linear" if scale == "linear" else "log"
        self._redraw()

    def set_show_fit(self, show: bool) -> None:
        self._show_fit = bool(show)
        self._redraw()

    def update_data(
        self,
        groups: Sequence[Group],
        fit: FitResult | None,
        results: DerivedResults | None,
        hover_id: int | None = None,
        is_demo: bool = False,
    ) -> None:
        self._groups = list(groups)
        self._fit = fit
        self._results = results
        self._hover_id = hover_id
        self._is_demo = bool(is_demo)
        self._redraw()

    def set_hover(self, hover_id: int | None) -> None:
        if hover_id == self._hover_id:
            return
        self._hover_id = hover_id
        self._redraw()

    def state_snapshot(self) -> dict:
        """Return current chart state — used by the PNG export path."""
        return {
            "groups": list(self._groups),
            "fit": self._fit,
            "results": self._results,
            "theme": self._theme,
            "x_scale": self._x_scale,
            "show_fit": self._show_fit,
            "strings": dict(self._t),
        }

    # ── rendering ──────────────────────────────────────────────────────

    def _redraw(self) -> None:
        render_chart_into(
            self._figure, self._ax,
            groups=self._groups, fit=self._fit, results=self._results,
            theme=self._theme, x_scale=self._x_scale, show_fit=self._show_fit,
            strings=self._t, hover_id=self._hover_id, is_demo=self._is_demo,
        )
        self._figure.tight_layout(pad=1.2)
        self.draw_idle()
