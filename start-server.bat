@echo off
setlocal enabledelayedexpansion


REM Define variables
set "DATA_DIR=%~dp0"
set "DB_DIRECTORY=%DATA_DIR%"
set "VENV_DIR=%DATA_DIR%\env"
set "ELECTRUMZ_SERVER=%DATA_DIR%\electrumz_server"
set "DAEMON_URL=http://SpaceZProjects:SpaceZProjects@2042@127.0.0.1:1979"
set "COIN=BitcoinZ"


REM Check if Python is installed
echo Checking for Python installation...
where python >nul 2>&1
if %errorlevel% neq 0 (
    echo Python is not installed. Please install Python and try again.
    pause
    exit /b 1
)
echo Python is installed.

call %VENV_DIR%\Scripts\activate.bat

REM Check if the ElectrumZ server script exists
if not exist "%ELECTRUMZ_SERVER%" (
    echo ElectrumZ server script not found at %ELECTRUMZ_SERVER%.
    echo Please verify the file exists and the path is correct.
    pause
    exit /b 1
)

echo Starting ElectrumZ server...
echo.

REM
python "%ELECTRUMZ_SERVER%"

echo ElectrumZ server started successfully.

endlocal
exit
