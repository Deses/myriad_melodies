@echo off
cd /d "%~dp0"

net session >nul 2>&1
if errorlevel 1 (
    echo [!] Not running as administrator. Relaunching with elevation...
    powershell -Command "Start-Process '%~f0' -Verb RunAs"
    exit /b
)

where python >nul 2>&1
if not errorlevel 1 goto :have_python

echo [!] Python not found.
set /p INSTALL_PY="    Install Python 3.14 via winget? [Y/N] "
if /i not "%INSTALL_PY%"=="Y" (
    echo [!] Python is required. Aborting.
    pause
    exit /b 1
)

echo [*] Installing Python 3.14...
winget install --id Python.Python.3.14 -e --scope machine
if errorlevel 1 (
    echo [!] winget install failed or was cancelled.
    pause
    exit /b 1
)

echo [*] Refreshing PATH...
for /f "usebackq delims=" %%p in (`powershell -NoProfile -Command "[Environment]::GetEnvironmentVariable('PATH','Machine') + ';' + [Environment]::GetEnvironmentVariable('PATH','User')"`) do set "PATH=%%p"

where python >nul 2>&1
if errorlevel 1 (
    echo [*] Not in PATH yet, checking common install locations...
    if exist "%ProgramFiles%\Python314\python.exe" (
        set "PATH=%ProgramFiles%\Python314;%ProgramFiles%\Python314\Scripts;%PATH%"
    ) else if exist "%LOCALAPPDATA%\Programs\Python\Python314\python.exe" (
        set "PATH=%LOCALAPPDATA%\Programs\Python\Python314;%LOCALAPPDATA%\Programs\Python\Python314\Scripts;%PATH%"
    ) else (
        echo [!] Could not locate Python 3.14. Please restart this script.
        pause
        exit /b 1
    )
)

where python >nul 2>&1
if errorlevel 1 (
    echo [!] Python still not found. Please restart this script.
    pause
    exit /b 1
)
echo [*] Python ready.

:have_python

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
