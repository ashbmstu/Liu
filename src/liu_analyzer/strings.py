"""UI strings, indexed by language code.

English is the default. Chinese, Spanish, French and Russian are selectable from
the header menu. Every language must carry exactly the keys English does;
tests/test_strings.py enforces that, so a missing translation fails the build
rather than raising KeyError in front of a user.
"""
from __future__ import annotations

from collections.abc import Mapping

DEFAULT_LANG = "en"

SIGNATURE = "designed by ASH, 2026"

# Language names appear in their own script in every language, which is the
# convention for a language picker: someone who cannot read the current UI can
# still find their own language in the menu.
_LANGUAGE_NAMES = {
    "lang_en": "English",
    "lang_zh": "中文",
    "lang_es": "Español",
    "lang_fr": "Français",
    "lang_ru": "Русский",
}

_SOURCE_LINK = "<a href='https://github.com/ashbmstu/Liu'>github.com/ashbmstu/Liu</a>"
_LICENCE_LINK = "<a href='https://creativecommons.org/licenses/by-sa/3.0/'>CC BY-SA 3.0</a>"

# Shared markup, identical in every language: the displayed formulas and the
# styles around them. Only prose is translated.
_FORMULA_STYLE = (
    "<p align='center' style='font-family:Cambria,serif; "
    "font-style:italic; background:#fafbfc; padding:8px 12px; margin:8px 0;'>"
)
_FORMULA_STYLE_SMALL = (
    "<p align='center' style='font-family:Cambria,serif; "
    "font-style:italic; background:#fafbfc; padding:8px 12px; "
    "margin:8px 0; font-size:13px'>"
)
_LIU_EQUATION = _FORMULA_STYLE + "D² = 2·w₀² · ln(F / F<sub>th</sub>)</p>"
_TABLE_OPEN = (
    "<table cellpadding='4' cellspacing='0' width='100%' "
    "style='border-collapse:collapse; margin:8px 0; font-size:13px'>"
)
_H3_FIRST = "<h3 style='margin-top:0; color:#0e1116'>"
_H3 = "<h3 style='margin-top:18px; color:#0e1116'>"
_NOTE = "<p style='font-size:12px; color:#6b7380'>"
_SMALL = "<p style='color:#888; font-size:11px; margin-top:14px'>"


def _error_block(res: str) -> str:
    """The error-propagation formulas; `res` is the local subscript for residual."""
    return (
        _FORMULA_STYLE_SMALL
        + f"σ<sub>a</sub> = σ<sub>{res}</sub> / √S<sub>xx</sub><br>"
        + f"σ<sub>b</sub> = σ<sub>{res}</sub> · √(1/n + x̄²/S<sub>xx</sub>)<br><br>"
        + "Δd = σ<sub>a</sub> / √(2a),&nbsp;&nbsp;Δw₀ = Δd / 2<br><br>"
        + "ln F<sub>th</sub> = const − b/a − ln(a/2)<br>"
        + "ΔF<sub>th</sub> = F<sub>th</sub> · √[(b/a² − 1/a)²σ<sub>a</sub>² "
        + "+ (1/a)²σ<sub>b</sub>²]</p>"
    )


def _results_table(head: tuple[str, str, str], rows: tuple[str, ...],
                   units: tuple[str, str, str, str], res: str, tot: str) -> str:
    """The derived-quantities table. `rows` are the five quantity descriptions."""
    formulas = (
        "w₀ = √(a / 2)",
        "d = 2·w₀",
        "E<sub>th</sub> = exp(−b / a)",
        "F<sub>th</sub> = 2·E<sub>th</sub> / (π·w₀²)",
        f"R² = 1 − SS<sub>{res}</sub> / SS<sub>{tot}</sub>",
    )
    cells = (*units, "—")
    body = "".join(
        f"<tr><td>{row}</td><td align='center'><i>{formula}</i></td>"
        f"<td align='center'>{unit}</td></tr>"
        for row, formula, unit in zip(rows, formulas, cells, strict=True)
    )
    return (
        _TABLE_OPEN
        + "<tr style='background:#fafbfc'>"
        + f"<th align='left'>{head[0]}</th>"
        + f"<th align='center'>{head[1]}</th>"
        + f"<th align='center'>{head[2]}</th></tr>"
        + body
        + "</table>"
    )


STRINGS: dict[str, dict[str, str]] = {
    "en": {
        "title": "Liu Threshold Analyzer",
        "header_new": "New",
        "header_settings": "Settings",
        "header_lang": "EN",
        **_LANGUAGE_NAMES,
        "series_placeholder": "name of this series",
        "axis_x_log": "Pulse Energy, mJ (log scale)",
        "axis_x_linear": "Pulse Energy, mJ",
        "axis_y": "Crater Diameter Squared, µm²",
        "add_E_label": "Pulse Energy =",
        "add_E_unit": "mJ",
        "add_D_label": "Diameter =",
        "add_D_unit": "µm",
        "add_button_tip": "Add measurement (Enter)",
        "table_idx": "#",
        "table_E": "E, mJ",
        "table_D": "D, µm",
        "table_D2": "D², µm²",
        "table_empty": "no measurements — enter a pair below",
        "footer_instructions": "Instructions",
        "footer_save": "Save",
        "footer_about": "About",
        "result_Fth": "Ablation threshold, J/cm²",
        "result_d": "Beam waist diameter, µm",
        "fit_insufficient": "≥ 2 distinct energies required for fit",
        "add_error": "Enter positive E and D values",
        "save_ok": "Saved to {path}",
        "save_error": "Could not save: {err}",
        "save_no_data": "no measurements to save yet",
        "delete_tip": "Delete row",
        "button_ok": "OK",
        "button_cancel": "Cancel",
        "button_close": "Close",
        "instructions_title": "Instructions",
        "about_title": "About",
        "settings_title": "Settings",
        "settings_scale": "X-axis scale",
        "settings_scale_log": "Logarithmic",
        "settings_scale_linear": "Linear",
        "settings_theme": "Theme",
        "settings_theme_light": "Light",
        "settings_theme_dark": "Dark",
        "settings_show_fit": "Show fit line",
        "save_filter_png": "PNG image (plot + data) (*.png)",
        "save_filter_json": "JSON session (*.json)",
        "footer_open": "Open",
        "open_ok": "Opened {path}",
        "open_error": "Could not open: {err}",
        "scheme_caption": "Gaussian beam through a focusing lens — typical Liu's-method optics",
        "attribution": SIGNATURE,
        "instructions_html": (
            _H3_FIRST + "How it works</h3>"
            "<p>Liu's method extracts both the <b>laser ablation threshold "
            "fluence</b> F<sub>th</sub> and the <b>beam waist diameter</b> d "
            "from a series of crater measurements. It exploits the linear "
            "relationship between the squared crater diameter and the "
            "logarithm of pulse energy:</p>"
            + _LIU_EQUATION
            + "{scheme}"
            "<ol>"
            "<li>Irradiate the sample with single pulses at varying energies.</li>"
            "<li>Measure each crater diameter D in µm.</li>"
            "<li>Enter (E, D) pairs in the inline row; press <b>+</b> or <b>Enter</b>.</li>"
            "<li>Repeat the same energy several times to obtain error bars.</li>"
            "<li>Read F<sub>th</sub> and beam waist diameter d from the plot.</li>"
            "</ol>"
            + _H3 + "Calculated values</h3>"
            "<p>Ordinary least squares on (ln E, D²) yields slope <i>a</i> "
            "and intercept <i>b</i>. From those:</p>"
            + _results_table(
                ("Quantity", "Formula", "Units"),
                (
                    "w₀ — beam waist radius",
                    "d — beam waist diameter",
                    "E<sub>th</sub> — threshold pulse energy",
                    "F<sub>th</sub> — threshold fluence",
                    "R² — coefficient of determination",
                ),
                ("µm", "µm", "mJ", "J/cm²"),
                "res", "tot",
            )
            + _H3 + "Error calculations (1σ)</h3>"
            "<p>Standard errors of the OLS coefficients propagate to "
            "physical quantities by the chain rule:</p>"
            + _error_block("res")
            + _NOTE + "Replicate measurements at the same energy add visible "
            "error bars (sample standard deviation of D²).</p>"
            "<p style='margin-top:14px'>Use <b>New</b> to clear all "
            "measurements and start a new run.</p>"
        ),
        "about_html": (
            "<p><b>Liu Threshold Analyzer</b> v{version}</p>"
            "<p>Companion tool to the linear-regression method described by "
            "J. M. Liu (Opt. Lett., 1982) for extracting the ablation-threshold "
            "fluence and Gaussian-beam waist from squared crater-diameter data.</p>"
            "<ul>"
            "<li>Fit: ordinary least squares on (ln E, D²)</li>"
            "<li>Uncertainties: 1σ, propagated from regression covariance</li>"
            "<li>Replicate measurements at the same energy show error bars "
            "(sample standard deviation)</li>"
            "</ul>"
            "<p style='margin-top:14px'><b>Designed by:</b> ASH<br>"
            "<b>Source:</b> " + _SOURCE_LINK + "</p>"
            + _SMALL + "<b>Figure credit:</b> the Gaussian-beam diagram is by "
            "Rodolfo Hermans, after Dr. Bob, from Wikimedia Commons, used under "
            + _LICENCE_LINK + ".</p>"
            + _SMALL + "For research and educational use.</p>"
        ),
    },
    "zh": {
        "title": "Liu 阈值分析器",
        "header_new": "新建",
        "header_settings": "设置",
        "header_lang": "CN",
        **_LANGUAGE_NAMES,
        "series_placeholder": "本系列名称",
        "axis_x_log": "脉冲能量，mJ（对数坐标）",
        "axis_x_linear": "脉冲能量，mJ",
        "axis_y": "烧蚀坑直径的平方，µm²",
        "add_E_label": "脉冲能量 =",
        "add_E_unit": "mJ",
        "add_D_label": "直径 =",
        "add_D_unit": "µm",
        "add_button_tip": "添加测量（Enter）",
        "table_idx": "#",
        "table_E": "E, mJ",
        "table_D": "D, µm",
        "table_D2": "D², µm²",
        "table_empty": "暂无测量 — 请在下方输入一组数据",
        "footer_instructions": "使用说明",
        "footer_save": "保存",
        "footer_about": "关于",
        "result_Fth": "烧蚀阈值，J/cm²",
        "result_d": "束腰直径，µm",
        "fit_insufficient": "拟合至少需要 2 个不同的能量值",
        "add_error": "请输入正的 E 和 D 值",
        "save_ok": "已保存至 {path}",
        "save_error": "无法保存：{err}",
        "save_no_data": "暂无可保存的测量数据",
        "delete_tip": "删除此行",
        "button_ok": "确定",
        "button_cancel": "取消",
        "button_close": "关闭",
        "instructions_title": "使用说明",
        "about_title": "关于",
        "settings_title": "设置",
        "settings_scale": "X 轴刻度",
        "settings_scale_log": "对数",
        "settings_scale_linear": "线性",
        "settings_theme": "主题",
        "settings_theme_light": "浅色",
        "settings_theme_dark": "深色",
        "settings_show_fit": "显示拟合线",
        "save_filter_png": "PNG 图像（图表 + 数据）(*.png)",
        "save_filter_json": "JSON 会话 (*.json)",
        "footer_open": "打开",
        "open_ok": "已打开 {path}",
        "open_error": "无法打开：{err}",
        "scheme_caption": "高斯光束经聚焦透镜 — Liu 方法的典型光路",
        "attribution": SIGNATURE,
        "instructions_html": (
            _H3_FIRST + "工作原理</h3>"
            "<p>Liu 方法可根据一系列烧蚀坑的测量结果，同时求出"
            "<b>激光烧蚀阈值能量密度</b> F<sub>th</sub> 和"
            "<b>光束束腰直径</b> d。该方法利用了烧蚀坑直径的平方与"
            "脉冲能量的对数之间的线性关系：</p>"
            + _LIU_EQUATION
            + "{scheme}"
            "<ol>"
            "<li>用不同能量的单个脉冲辐照样品。</li>"
            "<li>测量每个烧蚀坑的直径 D，单位为 µm。</li>"
            "<li>在输入行中输入 (E, D) 数据对，然后按 <b>+</b> 或 <b>Enter</b>。</li>"
            "<li>在同一能量下重复测量数次，以获得误差棒。</li>"
            "<li>从图中读取 F<sub>th</sub> 和束腰直径 d。</li>"
            "</ol>"
            + _H3 + "计算量</h3>"
            "<p>对 (ln E, D²) 进行普通最小二乘拟合，得到斜率 <i>a</i> "
            "和截距 <i>b</i>。由此可得：</p>"
            + _results_table(
                ("物理量", "公式", "单位"),
                (
                    "w₀ — 束腰半径",
                    "d — 束腰直径",
                    "E<sub>th</sub> — 阈值脉冲能量",
                    "F<sub>th</sub> — 阈值能量密度",
                    "R² — 决定系数",
                ),
                ("µm", "µm", "mJ", "J/cm²"),
                "res", "tot",
            )
            + _H3 + "误差计算（1σ）</h3>"
            "<p>最小二乘系数的标准误差按链式法则传递到各物理量：</p>"
            + _error_block("res")
            + _NOTE + "在同一能量下重复测量会显示误差棒（D² 的样本标准差）。</p>"
            "<p style='margin-top:14px'>点击<b>新建</b>可清除所有测量，"
            "开始新的系列。</p>"
        ),
        "about_html": (
            "<p><b>Liu 阈值分析器</b> v{version}</p>"
            "<p>配合 J. M. Liu（Opt. Lett., 1982）提出的线性回归方法使用的工具，"
            "用于根据烧蚀坑直径的平方数据求出烧蚀阈值能量密度和高斯光束束腰。</p>"
            "<ul>"
            "<li>拟合：对 (ln E, D²) 进行普通最小二乘</li>"
            "<li>不确定度：1σ，由回归协方差传递</li>"
            "<li>同一能量下的重复测量显示误差棒（样本标准差）</li>"
            "</ul>"
            "<p style='margin-top:14px'><b>设计：</b>ASH<br>"
            "<b>源代码：</b>" + _SOURCE_LINK + "</p>"
            + _SMALL + "<b>图片来源：</b>高斯光束示意图由 Rodolfo Hermans "
            "根据 Dr. Bob 的原图绘制，来自 Wikimedia Commons，依据 "
            + _LICENCE_LINK + " 许可使用。</p>"
            + _SMALL + "仅供科研与教学使用。</p>"
        ),
    },
    "es": {
        "title": "Analizador de umbral de Liu",
        "header_new": "Nuevo",
        "header_settings": "Ajustes",
        "header_lang": "ES",
        **_LANGUAGE_NAMES,
        "series_placeholder": "nombre de esta serie",
        "axis_x_log": "Energía del pulso, mJ (escala log.)",
        "axis_x_linear": "Energía del pulso, mJ",
        "axis_y": "Diámetro del cráter al cuadrado, µm²",
        "add_E_label": "Energía =",
        "add_E_unit": "mJ",
        "add_D_label": "Diámetro =",
        "add_D_unit": "µm",
        "add_button_tip": "Añadir medición (Enter)",
        "table_idx": "#",
        "table_E": "E, mJ",
        "table_D": "D, µm",
        "table_D2": "D², µm²",
        "table_empty": "sin mediciones — introduzca un par abajo",
        "footer_instructions": "Instrucciones",
        "footer_save": "Guardar",
        "footer_about": "Acerca de",
        "result_Fth": "Umbral de ablación, J/cm²",
        "result_d": "Diámetro de la cintura del haz, µm",
        "fit_insufficient": "se necesitan ≥ 2 energías distintas para el ajuste",
        "add_error": "Introduzca valores positivos de E y D",
        "save_ok": "Guardado en {path}",
        "save_error": "No se pudo guardar: {err}",
        "save_no_data": "aún no hay mediciones que guardar",
        "delete_tip": "Eliminar fila",
        "button_ok": "Aceptar",
        "button_cancel": "Cancelar",
        "button_close": "Cerrar",
        "instructions_title": "Instrucciones",
        "about_title": "Acerca de",
        "settings_title": "Ajustes",
        "settings_scale": "Escala del eje X",
        "settings_scale_log": "Logarítmica",
        "settings_scale_linear": "Lineal",
        "settings_theme": "Tema",
        "settings_theme_light": "Claro",
        "settings_theme_dark": "Oscuro",
        "settings_show_fit": "Mostrar la recta de ajuste",
        "save_filter_png": "Imagen PNG (gráfico + datos) (*.png)",
        "save_filter_json": "Sesión JSON (*.json)",
        "footer_open": "Abrir",
        "open_ok": "Abierto: {path}",
        "open_error": "No se pudo abrir: {err}",
        "scheme_caption": (
            "Haz gaussiano a través de una lente de enfoque — "
            "montaje típico del método de Liu"
        ),
        "attribution": SIGNATURE,
        "instructions_html": (
            _H3_FIRST + "Cómo funciona</h3>"
            "<p>El método de Liu obtiene a la vez la <b>fluencia umbral de "
            "ablación láser</b> F<sub>th</sub> y el <b>diámetro de la cintura "
            "del haz</b> d a partir de una serie de mediciones de cráteres. Se "
            "basa en la relación lineal entre el cuadrado del diámetro del "
            "cráter y el logaritmo de la energía del pulso:</p>"
            + _LIU_EQUATION
            + "{scheme}"
            "<ol>"
            "<li>Irradie la muestra con pulsos únicos de distintas energías.</li>"
            "<li>Mida el diámetro D de cada cráter en µm.</li>"
            "<li>Introduzca los pares (E, D) en la fila de entrada y pulse "
            "<b>+</b> o <b>Enter</b>.</li>"
            "<li>Repita varias veces la misma energía para obtener barras de error.</li>"
            "<li>Lea F<sub>th</sub> y el diámetro de la cintura d en el gráfico.</li>"
            "</ol>"
            + _H3 + "Valores calculados</h3>"
            "<p>Los mínimos cuadrados ordinarios sobre (ln E, D²) dan la "
            "pendiente <i>a</i> y la ordenada en el origen <i>b</i>. A partir "
            "de ellas:</p>"
            + _results_table(
                ("Magnitud", "Fórmula", "Unidades"),
                (
                    "w₀ — radio de la cintura del haz",
                    "d — diámetro de la cintura del haz",
                    "E<sub>th</sub> — energía umbral del pulso",
                    "F<sub>th</sub> — fluencia umbral",
                    "R² — coeficiente de determinación",
                ),
                ("µm", "µm", "mJ", "J/cm²"),
                "res", "tot",
            )
            + _H3 + "Cálculo de errores (1σ)</h3>"
            "<p>Los errores estándar de los coeficientes de mínimos cuadrados se "
            "propagan a las magnitudes físicas mediante la regla de la cadena:</p>"
            + _error_block("res")
            + _NOTE + "Las mediciones repetidas a la misma energía añaden barras "
            "de error visibles (desviación estándar muestral de D²).</p>"
            "<p style='margin-top:14px'>Use <b>Nuevo</b> para borrar todas las "
            "mediciones y empezar una nueva serie.</p>"
        ),
        "about_html": (
            "<p><b>Analizador de umbral de Liu</b> v{version}</p>"
            "<p>Herramienta complementaria del método de regresión lineal descrito "
            "por J. M. Liu (Opt. Lett., 1982) para obtener la fluencia umbral de "
            "ablación y la cintura del haz gaussiano a partir del cuadrado del "
            "diámetro de los cráteres.</p>"
            "<ul>"
            "<li>Ajuste: mínimos cuadrados ordinarios sobre (ln E, D²)</li>"
            "<li>Incertidumbres: 1σ, propagadas desde la covarianza de la regresión</li>"
            "<li>Las mediciones repetidas a la misma energía muestran barras de "
            "error (desviación estándar muestral)</li>"
            "</ul>"
            "<p style='margin-top:14px'><b>Diseñado por:</b> ASH<br>"
            "<b>Código fuente:</b> " + _SOURCE_LINK + "</p>"
            + _SMALL + "<b>Crédito de la figura:</b> el diagrama del haz gaussiano "
            "es de Rodolfo Hermans, a partir de un original de Dr. Bob, de "
            "Wikimedia Commons, y se usa bajo " + _LICENCE_LINK + ".</p>"
            + _SMALL + "Para uso en investigación y docencia.</p>"
        ),
    },
    "fr": {
        "title": "Analyseur de seuil de Liu",
        "header_new": "Nouveau",
        "header_settings": "Paramètres",
        "header_lang": "FR",
        **_LANGUAGE_NAMES,
        "series_placeholder": "nom de cette série",
        "axis_x_log": "Énergie d'impulsion, mJ (échelle log.)",
        "axis_x_linear": "Énergie d'impulsion, mJ",
        "axis_y": "Diamètre du cratère au carré, µm²",
        "add_E_label": "Énergie =",
        "add_E_unit": "mJ",
        "add_D_label": "Diamètre =",
        "add_D_unit": "µm",
        "add_button_tip": "Ajouter une mesure (Entrée)",
        "table_idx": "#",
        "table_E": "E, mJ",
        "table_D": "D, µm",
        "table_D2": "D², µm²",
        "table_empty": "aucune mesure — saisissez une paire ci-dessous",
        "footer_instructions": "Instructions",
        "footer_save": "Enregistrer",
        "footer_about": "À propos",
        "result_Fth": "Seuil d'ablation, J/cm²",
        "result_d": "Diamètre du col du faisceau, µm",
        "fit_insufficient": "l'ajustement requiert ≥ 2 énergies distinctes",
        "add_error": "Saisissez des valeurs positives de E et D",
        "save_ok": "Enregistré dans {path}",
        "save_error": "Échec de l'enregistrement : {err}",
        "save_no_data": "aucune mesure à enregistrer pour l'instant",
        "delete_tip": "Supprimer la ligne",
        "button_ok": "OK",
        "button_cancel": "Annuler",
        "button_close": "Fermer",
        "instructions_title": "Instructions",
        "about_title": "À propos",
        "settings_title": "Paramètres",
        "settings_scale": "Échelle de l'axe X",
        "settings_scale_log": "Logarithmique",
        "settings_scale_linear": "Linéaire",
        "settings_theme": "Thème",
        "settings_theme_light": "Clair",
        "settings_theme_dark": "Sombre",
        "settings_show_fit": "Afficher la droite d'ajustement",
        "save_filter_png": "Image PNG (graphique + données) (*.png)",
        "save_filter_json": "Session JSON (*.json)",
        "footer_open": "Ouvrir",
        "open_ok": "Ouvert : {path}",
        "open_error": "Impossible d'ouvrir : {err}",
        "scheme_caption": (
            "Faisceau gaussien à travers une lentille de focalisation — "
            "montage typique de la méthode de Liu"
        ),
        "attribution": SIGNATURE,
        "instructions_html": (
            _H3_FIRST + "Principe</h3>"
            "<p>La méthode de Liu détermine à la fois la <b>fluence seuil "
            "d'ablation laser</b> F<sub>th</sub> et le <b>diamètre du col du "
            "faisceau</b> d à partir d'une série de mesures de cratères. Elle "
            "repose sur la relation linéaire entre le carré du diamètre du "
            "cratère et le logarithme de l'énergie d'impulsion&nbsp;:</p>"
            + _LIU_EQUATION
            + "{scheme}"
            "<ol>"
            "<li>Irradiez l'échantillon avec des impulsions uniques d'énergies "
            "différentes.</li>"
            "<li>Mesurez le diamètre D de chaque cratère en µm.</li>"
            "<li>Saisissez les paires (E, D) dans la ligne de saisie, puis "
            "appuyez sur <b>+</b> ou <b>Entrée</b>.</li>"
            "<li>Répétez plusieurs fois la même énergie pour obtenir des barres "
            "d'erreur.</li>"
            "<li>Lisez F<sub>th</sub> et le diamètre du col d sur le graphique.</li>"
            "</ol>"
            + _H3 + "Grandeurs calculées</h3>"
            "<p>Les moindres carrés ordinaires sur (ln E, D²) donnent la pente "
            "<i>a</i> et l'ordonnée à l'origine <i>b</i>. On en déduit&nbsp;:</p>"
            + _results_table(
                ("Grandeur", "Formule", "Unités"),
                (
                    "w₀ — rayon du col du faisceau",
                    "d — diamètre du col du faisceau",
                    "E<sub>th</sub> — énergie d'impulsion seuil",
                    "F<sub>th</sub> — fluence seuil",
                    "R² — coefficient de détermination",
                ),
                ("µm", "µm", "mJ", "J/cm²"),
                "res", "tot",
            )
            + _H3 + "Calcul des incertitudes (1σ)</h3>"
            "<p>Les erreurs types des coefficients des moindres carrés se "
            "propagent aux grandeurs physiques par la règle de dérivation en "
            "chaîne&nbsp;:</p>"
            + _error_block("res")
            + _NOTE + "Les mesures répétées à la même énergie ajoutent des barres "
            "d'erreur visibles (écart type empirique de D²).</p>"
            "<p style='margin-top:14px'>Utilisez <b>Nouveau</b> pour effacer "
            "toutes les mesures et commencer une nouvelle série.</p>"
        ),
        "about_html": (
            "<p><b>Analyseur de seuil de Liu</b> v{version}</p>"
            "<p>Outil d'accompagnement de la méthode de régression linéaire décrite "
            "par J. M. Liu (Opt. Lett., 1982) pour déterminer la fluence seuil "
            "d'ablation et le col du faisceau gaussien à partir du carré du "
            "diamètre des cratères.</p>"
            "<ul>"
            "<li>Ajustement&nbsp;: moindres carrés ordinaires sur (ln E, D²)</li>"
            "<li>Incertitudes&nbsp;: 1σ, propagées à partir de la covariance de "
            "la régression</li>"
            "<li>Les mesures répétées à la même énergie affichent des barres "
            "d'erreur (écart type empirique)</li>"
            "</ul>"
            "<p style='margin-top:14px'><b>Conçu par&nbsp;:</b> ASH<br>"
            "<b>Code source&nbsp;:</b> " + _SOURCE_LINK + "</p>"
            + _SMALL + "<b>Crédit de la figure&nbsp;:</b> le schéma du faisceau "
            "gaussien est de Rodolfo Hermans, d'après un original de Dr. Bob, "
            "issu de Wikimedia Commons et utilisé sous licence "
            + _LICENCE_LINK + ".</p>"
            + _SMALL + "Pour la recherche et l'enseignement.</p>"
        ),
    },
    "ru": {
        "title": "Анализатор порога Лиу",
        "header_new": "Новый",
        "header_settings": "Настройки",
        "header_lang": "RU",
        **_LANGUAGE_NAMES,
        "series_placeholder": "название серии",
        "axis_x_log": "Энергия импульса, мДж (лог. шкала)",
        "axis_x_linear": "Энергия импульса, мДж",
        "axis_y": "Квадрат диаметра кратера, мкм²",
        "add_E_label": "Энергия импульса =",
        "add_E_unit": "мДж",
        "add_D_label": "Диаметр =",
        "add_D_unit": "мкм",
        "add_button_tip": "Добавить измерение (Enter)",
        "table_idx": "№",
        "table_E": "E, мДж",
        "table_D": "D, мкм",
        "table_D2": "D², мкм²",
        "table_empty": "нет измерений — введите пару ниже",
        "footer_instructions": "Инструкции",
        "footer_save": "Сохранить",
        "footer_about": "О программе",
        "result_Fth": "Порог абляции, Дж/см²",
        "result_d": "Диаметр перетяжки, мкм",
        "fit_insufficient": "для аппроксимации требуется ≥ 2 различных значений энергии",
        "add_error": "Введите положительные значения E и D",
        "save_ok": "Сохранено в {path}",
        "save_error": "Не удалось сохранить: {err}",
        "save_no_data": "пока нет измерений для сохранения",
        "delete_tip": "Удалить строку",
        "button_ok": "ОК",
        "button_cancel": "Отмена",
        "button_close": "Закрыть",
        "instructions_title": "Инструкции",
        "about_title": "О программе",
        "settings_title": "Настройки",
        "settings_scale": "Масштаб оси X",
        "settings_scale_log": "Логарифмический",
        "settings_scale_linear": "Линейный",
        "settings_theme": "Тема",
        "settings_theme_light": "Светлая",
        "settings_theme_dark": "Тёмная",
        "settings_show_fit": "Показывать линию аппроксимации",
        "save_filter_png": "PNG-изображение (график + данные) (*.png)",
        "save_filter_json": "JSON-сессия (*.json)",
        "footer_open": "Открыть",
        "open_ok": "Открыт файл {path}",
        "open_error": "Не удалось открыть: {err}",
        "scheme_caption": "Схема лазерного луча с распределением Гаусса",
        "attribution": SIGNATURE,
        "instructions_html": (
            _H3_FIRST + "Как это работает</h3>"
            "<p>Метод Лиу определяет одновременно <b>порог лазерной "
            "абляции</b> F<sub>th</sub> и <b>диаметр перетяжки пучка</b> d "
            "по серии измерений диаметров кратеров. Метод опирается на "
            "линейную зависимость квадрата диаметра кратера от логарифма "
            "энергии импульса:</p>"
            + _LIU_EQUATION
            + "{scheme}"
            "<ol>"
            "<li>Облучите образец одиночными импульсами с различной энергией.</li>"
            "<li>Измерьте диаметр D каждого кратера в мкм.</li>"
            "<li>Введите пары (E, D) во встроенной строке; нажмите <b>+</b> или "
            "<b>Enter</b>.</li>"
            "<li>Повторите измерения с одной и той же энергией для получения "
            "погрешностей.</li>"
            "<li>Считайте F<sub>th</sub> и диаметр перетяжки d с графика.</li>"
            "</ol>"
            + _H3 + "Вычисляемые величины</h3>"
            "<p>МНК на (ln E, D²) даёт наклон <i>a</i> и свободный член "
            "<i>b</i>. Из них:</p>"
            + _results_table(
                ("Величина", "Формула", "Ед."),
                (
                    "w₀ — радиус перетяжки",
                    "d — диаметр перетяжки",
                    "E<sub>th</sub> — пороговая энергия импульса",
                    "F<sub>th</sub> — порог абляции",
                    "R² — коэффициент детерминации",
                ),
                ("мкм", "мкм", "мДж", "Дж/см²"),
                "ост", "общ",
            )
            + _H3 + "Расчёт погрешностей (1σ)</h3>"
            "<p>Стандартные ошибки коэффициентов МНК пересчитываются в "
            "неопределённости физических величин по правилу цепочки:</p>"
            + _error_block("ост")
            + _NOTE + "Повторные измерения при одной и той же энергии добавляют "
            "усы погрешностей (выборочное СКО D²).</p>"
            "<p style='margin-top:14px'>Кнопка <b>Новый</b> очищает все "
            "измерения и начинает новую серию.</p>"
        ),
        "about_html": (
            "<p><b>Анализатор порога Лиу</b> v{version}</p>"
            "<p>Программный спутник к методу линейной регрессии, описанному "
            "Дж. М. Лиу (Opt. Lett., 1982), для определения порога абляционной "
            "плотности энергии и перетяжки гауссова пучка по данным квадрата "
            "диаметра кратера.</p>"
            "<ul>"
            "<li>Аппроксимация: МНК на (ln E, D²)</li>"
            "<li>Погрешности: 1σ, распространение из ковариационной матрицы</li>"
            "<li>Повторные измерения с одной энергией отображаются как погрешности "
            "(выборочное стандартное отклонение)</li>"
            "</ul>"
            "<p style='margin-top:14px'><b>Автор:</b> ASH<br>"
            "<b>Исходный код:</b> " + _SOURCE_LINK + "</p>"
            + _SMALL + "<b>Иллюстрация:</b> схема гауссова пучка — Rodolfo Hermans, "
            "по оригиналу Dr. Bob, Wikimedia Commons, лицензия "
            + _LICENCE_LINK + ".</p>"
            + _SMALL + "Для исследовательских и образовательных целей.</p>"
        ),
    },
}


def get(lang: str = DEFAULT_LANG) -> Mapping[str, str]:
    """Return the strings dict for the given language code (falls back to default)."""
    return STRINGS.get(lang, STRINGS[DEFAULT_LANG])
