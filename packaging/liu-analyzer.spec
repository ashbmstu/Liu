# PyInstaller spec for Liu Threshold Analyzer.
# Build: pyinstaller --clean packaging/liu-analyzer.spec
# Output: dist/LiuAnalyzer.exe
#
# Goal: single self-contained Windows .exe with no runtime dependencies.

# ruff: noqa
from pathlib import Path

block_cipher = None

PROJECT_ROOT = Path(SPECPATH).parent.resolve()
SRC = PROJECT_ROOT / "src"
ENTRY = SRC / "liu_analyzer" / "__main__.py"
VERSION = PROJECT_ROOT / "packaging" / "version_info.txt"

RESOURCES = SRC / "liu_analyzer" / "resources"
ICON = RESOURCES / "icon.ico"
RESOURCE_DATAS = [
    (str(RESOURCES / name), "liu_analyzer/resources")
    for name in ("laser_scheme.png", "icon.ico")
    if (RESOURCES / name).exists()
]

a = Analysis(
    [str(ENTRY)],
    pathex=[str(SRC)],
    binaries=[],
    datas=RESOURCE_DATAS,
    hiddenimports=[
        "PySide6.QtPrintSupport",
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[
        "PyQt5",
        "PyQt6",
        "tkinter",
        "scipy",
        "pandas",
        "IPython",
        "jupyter",
        "notebook",
        "PIL.ImageQt",
        # NOTE: do NOT exclude `unittest` or `test` here.
        # pyparsing.testing (auto-imported by pyparsing/__init__.py, which
        # matplotlib pulls in transitively) does `import unittest` at module
        # top-level, so excluding it crashes the .exe with ModuleNotFoundError.
    ],
    cipher=block_cipher,
    noarchive=False,
)

# Strip Qt translations, large Qt modules, and ancillary DLLs we don't use.
# Keep QtPrintSupport — matplotlib's Qt6Agg backend touches it.
DROP = (
    # Big Qt6 modules
    "Qt6Qml", "Qt6Quick", "Qt6Quick3D", "Qt6QuickWidgets", "Qt6QmlMeta",
    "Qt6QmlModels", "Qt6Multimedia", "Qt6Web", "Qt6Pdf", "Qt6Sensors",
    "Qt6Bluetooth", "Qt6Nfc", "Qt6Charts", "Qt6DataVisualization",
    "Qt6Designer", "Qt6VirtualKeyboard",
    # Software OpenGL fallback (~20 MB)
    "opengl32sw.dll",
    # OpenSSL — only used by Qt6Network, which we don't ship
    "libcrypto-3", "libssl-3",
    # Image format plugins (matplotlib uses Pillow directly, not Qt plugins)
    "imageformats\\qjpeg", "imageformats\\qwebp", "imageformats\\qtiff",
    "imageformats\\qgif", "imageformats\\qicns", "imageformats\\qico",
    "imageformats\\qsvg", "imageformats\\qtga", "imageformats\\qwbmp",
    "imageformats\\qpdf",
    # TLS / network plugins
    "tls\\qopensslbackend", "tls\\qschannelbackend", "tls\\qcertonlybackend",
    "networkinformation",
)
a.binaries = [b for b in a.binaries if not any(m in b[0] for m in DROP)]
a.datas = [
    d for d in a.datas
    if "translations" not in d[0].lower() and "qml" not in d[0].lower()
]

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name="LiuAnalyzer",
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=False,
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=str(ICON) if ICON.exists() else None,
    version=str(VERSION) if VERSION.exists() else None,
)
# Note: onefile mode is implicit when binaries/zipfiles/datas are passed
# directly to EXE() and no COLLECT step follows.

