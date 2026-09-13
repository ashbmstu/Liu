@echo off
REM ==============================================================
REM  Liu Threshold Analyzer — one-click build script
REM
REM  Output: dist\LiuAnalyzer.exe
REM
REM  Notes for the synced-folder case (Google Drive / OneDrive):
REM  - PyInstaller's scratch dir is redirected to %TEMP% because
REM    Drive holds locks on `build\` and breaks `--clean`.
REM  - The venv is verified by actually running its python.exe
REM    instead of relying on activate.bat. If the venv was synced
REM    in from another machine the python path won't resolve
REM    locally; we rebuild it cleanly so deps don't silently land
REM    in a system Python's site-packages.
REM ==============================================================
setlocal EnableExtensions
cd /d "%~dp0"

set "VENV_PY=.venv\Scripts\python.exe"

REM ---------- [1/4] Ensure a working Python 3.11 venv ----------
if not exist "%VENV_PY%" goto create_venv

"%VENV_PY%" --version >nul 2>&1
if errorlevel 1 goto rebuild_venv
goto venv_ready

:rebuild_venv
echo === Existing .venv is broken; rebuilding =============================
rmdir /s /q .venv
goto create_venv

:create_venv
if exist .venv rmdir /s /q .venv
echo === [1/4] Creating Python 3.11 venv =================================
py -3.11 -m venv .venv
if errorlevel 1 (
    echo ERROR: could not create venv. Install Python 3.11 from python.org.
    echo        PySide6 6.7.3 does not support Python 3.13 or newer.
    exit /b 1
)

:venv_ready
"%VENV_PY%" --version
if errorlevel 1 (
    echo ERROR: venv python is not runnable. Aborting.
    exit /b 1
)

REM ---------- [2/4] Install dependencies ----------
echo.
echo === [2/4] Installing dependencies ====================================
"%VENV_PY%" -m pip install --upgrade pip wheel
if errorlevel 1 (
    echo ERROR: failed to upgrade pip / wheel.
    exit /b 1
)
"%VENV_PY%" -m pip install -r requirements.txt
if errorlevel 1 (
    echo ERROR: dependency install failed.
    exit /b 1
)

REM ---------- [3/4] Run tests ----------
echo.
echo === [3/4] Running tests ==============================================
"%VENV_PY%" -m pytest tests
if errorlevel 1 (
    echo ERROR: tests failed. Aborting build.
    exit /b 1
)

REM ---------- [4/4] PyInstaller ----------
echo.
echo === [4/4] Building .exe with PyInstaller =============================
set "WORKDIR=%TEMP%\liu-analyzer-build"
if exist "%WORKDIR%" rmdir /s /q "%WORKDIR%" 2>nul
if exist build rmdir /s /q build 2>nul

"%VENV_PY%" -m PyInstaller --clean --workpath "%WORKDIR%" --distpath dist packaging\liu-analyzer.spec
if errorlevel 1 (
    echo ERROR: PyInstaller build failed.
    exit /b 1
)

echo.
echo === Done =============================================================
echo Built dist\LiuAnalyzer.exe
dir /b dist\LiuAnalyzer.exe 2>nul

endlocal
