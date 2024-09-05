@echo off
setlocal enabledelayedexpansion

REM 
set "DATA_DIR=%~dp0"
set "DB_DIRECTORY=%DATA_DIR%"
set "CERT_FILE=%DATA_DIR%\electrumz.crt"
set "KEY_FILE=%DATA_DIR%\electrumz.key"
set "CSR_FILE=%DATA_DIR%\electrumz.csr"
set "CERT_SUBJECT=/C=US/ST=State/L=City/O=SpaceZ/CN=BTCZCommunity"
set "OPENSSL_TOOL=%DATA_DIR%\tools\openssl"
set "VENV_DIR=%DATA_DIR%\env"
set "REQUIREMENTS_FILE=%DATA_DIR%\requirements.txt"
set "FIREWALL_RULE_PREFIX=ElectrumZ"


REM 
echo.
echo Checking for Python installation...
where python >nul 2>&1
if %errorlevel% neq 0 (
    echo Python is not installed. Please install Python and try again.
    pause
    exit /b 1
)
echo Python is installed.

REM 
echo Setting up Python virtual environment...
echo.
timeout /t 1 /nobreak >nul

python -m venv %VENV_DIR%
call %VENV_DIR%\Scripts\activate.bat
python -m pip install --upgrade pip
pip install -r %REQUIREMENTS_FILE%
call %VENV_DIR%\Scripts\deactivate.bat
echo.
echo Python virtual environment setup completed.

timeout /t 1 /nobreak >nul

REM 
echo Generating private key...
%OPENSSL_TOOL% genpkey -algorithm RSA -out "%KEY_FILE%" -pass pass:bitcoinzcommunity2024

timeout /t 1 /nobreak >nul

REM 
echo Generating CSR...
%OPENSSL_TOOL% req -new -key "%KEY_FILE%" -out "%CSR_FILE%" -subj %CERT_SUBJECT% -passin pass:bitcoinzcommunity2024

timeout /t 1 /nobreak >nul

REM 
echo Generating self-signed certificate...
%OPENSSL_TOOL% x509 -req -days 365 -in "%CSR_FILE%" -signkey "%KEY_FILE%" -out "%CERT_FILE%"

timeout /t 1 /nobreak >nul

REM 
del "%CSR_FILE%"
echo CSR file deleted.

timeout /t 1 /nobreak >nul

REM 
echo Creating configuration file...
(
    echo ALLOW_ROOT=1
    echo DB_DIRECTORY=%DB_DIRECTORY%
    echo SERVICES=tcp://127.0.0.1:50001,ssl://127.0.0.1:50002,wss://127.0.0.1:50004,rpc://127.0.0.1:8000
    echo SSL_CERTFILE=%CERT_FILE%
    echo SSL_KEYFILE=%KEY_FILE%
    echo INITIAL_CONCURRENT=1000000
    echo COST_SOFT_LIMIT=1000000
    echo COST_HARD_LIMIT=1000000
    echo REQUEST_SLEEP=0
    echo HOST=127.0.0.1
) > "%DB_DIRECTORY%\config.env"
echo Configuration file created at %DB_DIRECTORY%\config.env

timeout /t 1 /nobreak >nul

REM 
echo Adding firewall rules...
echo allow port 50001...
timeout /t 1 /nobreak >nul
netsh advfirewall firewall add rule name="%FIREWALL_RULE_PREFIX% TCP 50001" protocol=TCP dir=in localport=50001 action=allow
echo allow port 50002...
timeout /t 1 /nobreak >nul
netsh advfirewall firewall add rule name="%FIREWALL_RULE_PREFIX% SSL 50002" protocol=TCP dir=in localport=50002 action=allow
echo allow port 50004...
timeout /t 1 /nobreak >nul
netsh advfirewall firewall add rule name="%FIREWALL_RULE_PREFIX% WSS 50004" protocol=TCP dir=in localport=50004 action=allow
echo allow port 8000...
timeout /t 1 /nobreak >nul
netsh advfirewall firewall add rule name="%FIREWALL_RULE_PREFIX% RPC 8000" protocol=TCP dir=in localport=8000 action=allow
timeout /t 1 /nobreak >nul

echo Script completed.
pause
