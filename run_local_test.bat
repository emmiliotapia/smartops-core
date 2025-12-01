@echo off
REM ════════════════════════════════════════════════════════════════
REM  SMARTOPS CORE - LOCAL TEST LAUNCHER (Windows)
REM  Ejecuta FastAPI + PostgreSQL en una sola ventana
REM ════════════════════════════════════════════════════════════════

setlocal enabledelayedexpansion

echo.
echo [INFO] SmartOps Core - Local Test Launcher
echo [INFO] ═══════════════════════════════════════════════════

REM Check if .venv exists
if not exist ".venv" (
    echo [ERROR] Virtual environment not found
    echo [INFO] Run: python local_test_setup.py
    pause
    exit /b 1
)

REM Check if requirements are installed
.venv\Scripts\python -m pip show fastapi >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Dependencies not installed
    echo [INFO] Run: python local_test_setup.py
    pause
    exit /b 1
)

echo [OK] Virtual environment found
echo [OK] Dependencies installed

echo.
echo [INFO] Starting PostgreSQL + pgvector in Docker...
docker-compose up -d postgres
if %errorlevel% neq 0 (
    echo [WARN] Docker start failed - continuing anyway
    echo [INFO] You can start manually: docker-compose up -d postgres
)

REM Wait for DB to be ready
echo [INFO] Waiting 10 seconds for PostgreSQL to start...
timeout /t 10 /nobreak

echo.
echo [OK] ═══════════════════════════════════════════════════════════
echo [OK] Setup Complete - FastAPI Ready to Launch
echo [OK] ═══════════════════════════════════════════════════════════
echo.

echo [INFO] Starting FastAPI server on http://localhost:8001
echo [INFO] Press Ctrl+C to stop
echo.

.venv\Scripts\activate && uvicorn app.main:app --reload --port 8001 --host 0.0.0.0

pause
