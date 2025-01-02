@echo off
setlocal enabledelayedexpansion

REM
set "DATA_DIR=%~dp0"
set "VENV_DIR=%DATA_DIR%\env"

REM
echo Checking for Python installation...
where python >nul 2>&1
if %errorlevel% neq 0 (
    echo Python is not installed. Please install Python 3.9 and try again.
    pause
    exit /b 1
)

REM 
for /f "delims=" %%v in ('python --version 2^>nul') do set python_version=%%v

REM 
for /f "tokens=2 delims= " %%a in ("!python_version!") do set version=%%a
for /f "tokens=1,2 delims=." %%a in ("!version!") do (
    set major=%%a
    set minor=%%b
)

REM 
if "!major!"=="3" (
    if "!minor!"=="9" (
        echo Python version is 3.9
    ) else (
        echo Unsupported Python version: !major!.!minor!
        echo Required version: 3.9 
        pause
        exit /b 1
    )
) else (
    echo Unsupported Python version: !major!.!minor!
    pause
    exit /b 1
)

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
pip install pythonnet==3.0.5

REM
echo Open configuration window
python configuration
call make.bat

echo Building completed !
del make.bat
del electrumz.conf
pause

