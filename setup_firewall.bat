@echo off
REM SmartOps Firewall Configuration
REM This script must be run as Administrator

color 0A
cls

echo.
echo ========================================
echo  SmartOps Firewall Configuration
echo ========================================
echo.

REM Check for admin privileges
openfiles >nul 2>&1
if errorlevel 1 (
    color 0C
    echo ERROR: This script requires Administrator privileges!
    echo.
    echo To run this script:
    echo 1. Right-click on setup_firewall.bat
    echo 2. Select "Run as administrator"
    echo.
    pause
    exit /b 1
)

color 0A

REM Open port 8001 for FastAPI
echo Opening port 8001 for FastAPI...
netsh advfirewall firewall add rule name="SmartOps FastAPI 8001" dir=in action=allow protocol=tcp localport=8001 >nul 2>&1
netsh advfirewall firewall add rule name="SmartOps FastAPI 8001 OUT" dir=out action=allow protocol=tcp localport=8001 >nul 2>&1

REM Open port 5432 for PostgreSQL
echo Opening port 5432 for PostgreSQL...
netsh advfirewall firewall add rule name="SmartOps PostgreSQL 5432" dir=in action=allow protocol=tcp localport=5432 >nul 2>&1
netsh advfirewall firewall add rule name="SmartOps PostgreSQL 5432 OUT" dir=out action=allow protocol=tcp localport=5432 >nul 2>&1

echo.
echo ========================================
echo  SUCCESS - Firewall Rules Added
echo ========================================
echo.
echo Ports now open:
echo   * 8001  - FastAPI (API backend)
echo   * 5432  - PostgreSQL (Database)
echo.
echo You can now run: python start.py
echo.
pause
