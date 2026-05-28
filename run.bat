@echo off
cd /d "%~dp0"

net session >nul 2>&1
if errorlevel 1 (
    echo [!] Not running as administrator. Relaunching with elevation...
    powershell -Command "Start-Process '%~f0' -Verb RunAs"
    exit /b
)

where python >nul 2>&1
if errorlevel 1 (
    echo [!] Python not found.
    set /p INSTALL_PY="    Install Python 3.14 + launcher via winget? [Y/N] "
    if /i "%INSTALL_PY%"=="Y" (
        echo [*] Installing Python 3.14...
        winget install --id Python.Python.3.14 -e
        echo [*] Done. Restart this script to continue.
    ) else (
        echo [!] Python is required. Aborting.
    )
    pause
    exit /b 1
)

if not exist .venv (
    echo [*] Creating virtual environment...
    python -m venv .venv
    if errorlevel 1 (
        echo ERROR: Could not create venv.
        pause
        exit /b 1
    )
    echo [*] Installing requirements...
    call .venv\Scripts\activate.bat
    pip install -r requirements.txt --prefer-binary --quiet
    if errorlevel 1 (
        echo ERROR: Failed to install requirements.
        pause
        exit /b 1
    )
    echo [*] Requirements installed.
) else (
    call .venv\Scripts\activate.bat
)

echo [*] Starting bot...
python main.py
