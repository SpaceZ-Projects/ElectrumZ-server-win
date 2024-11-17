@echo off
setlocal enabledelayedexpansion

REM
set "DATA_DIR=%~dp0"
set "VENV_DIR=%DATA_DIR%\env"
set "REQUIREMENTS_FILE=%DATA_DIR%\requirements.txt"
set "ELECTRUMZ_FILE_EXE=%DATA_DIR%\dist\ElectrumZ-Server.exe"
set "BUILD_DIR=%DATA_DIR%\dist"

REM
echo Checking for Python installation...
where python >nul 2>&1
if %errorlevel% neq 0 (
    echo Python is not installed. Please install Python and try again.
    pause
    exit /b 1
)
echo Python is installed.

REM
echo.
echo Setting up Python virtual environment...
timeout /t 1 /nobreak >nul

if not exist "%VENV_DIR%\Scripts\activate.bat" (
    echo Virtual environment does not exist, creating it...
    python -m venv %VENV_DIR%
) else (
    echo Virtual environment already exists, skipping creation...
)

call %VENV_DIR%\Scripts\activate.bat
python -m pip install --upgrade pip
echo Installing required packages from %REQUIREMENTS_FILE%...
pip install -r %REQUIREMENTS_FILE%

REM
echo Running PyInstaller to build the executable...
pyinstaller ./deterministic.spec

REM
call %VENV_DIR%\Scripts\deactivate.bat

REM
where makensis >nul 2>&1
if %errorlevel% neq 0 (
    echo NSIS is not installed. Skipping NSIS packaging.
) else (
    echo Running NSIS to create installer...
    makensis ./electrumz.nsi
)

echo Build completed.
pause
