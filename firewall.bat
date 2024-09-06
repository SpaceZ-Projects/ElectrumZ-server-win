@echo off
setlocal enabledelayedexpansion

set "FIREWALL_RULE_PREFIX=ElectrumZ"

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