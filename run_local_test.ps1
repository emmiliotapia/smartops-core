#!/usr/bin/env pwsh
<#
    ════════════════════════════════════════════════════════════════
    SMARTOPS CORE - LOCAL TEST LAUNCHER (PowerShell)
    Ejecuta FastAPI + PostgreSQL con mejor manejo de errores
    ════════════════════════════════════════════════════════════════
#>

$ErrorActionPreference = "Continue"

Write-Host ""
Write-Host "╔═══════════════════════════════════════════════════════════╗" -ForegroundColor Cyan
Write-Host "║  SmartOps Core - Local Test Launcher                      ║" -ForegroundColor Cyan
Write-Host "║  FastAPI + PostgreSQL + pgvector                          ║" -ForegroundColor Cyan
Write-Host "╚═══════════════════════════════════════════════════════════╝" -ForegroundColor Cyan
Write-Host ""

# ════════════════════════════════════════════════════════════════
# 1. CHECK VIRTUAL ENVIRONMENT
# ════════════════════════════════════════════════════════════════

$venvPath = ".\.venv"
if (-not (Test-Path $venvPath)) {
    Write-Host "[ERROR] Virtual environment not found at: $venvPath" -ForegroundColor Red
    Write-Host "[INFO]  Run first-time setup:" -ForegroundColor Yellow
    Write-Host "        python local_test_setup.py" -ForegroundColor Green
    Write-Host ""
    Read-Host "Press Enter to exit"
    exit 1
}

Write-Host "[✓] Virtual environment found" -ForegroundColor Green

# ════════════════════════════════════════════════════════════════
# 2. ACTIVATE VENV AND CHECK DEPENDENCIES
# ════════════════════════════════════════════════════════════════

& "$venvPath\Scripts\Activate.ps1"

$pythonExe = "$venvPath\Scripts\python.exe"
& $pythonExe -c "import fastapi, uvicorn, sqlalchemy, pydantic, dotenv" 2>$null
if ($LASTEXITCODE -ne 0) {
    Write-Host "[ERROR] Required packages not installed" -ForegroundColor Red
    Write-Host "[INFO]  Run first-time setup:" -ForegroundColor Yellow
    Write-Host "        python local_test_setup.py" -ForegroundColor Green
    Write-Host ""
    Read-Host "Press Enter to exit"
    exit 1
}

Write-Host "[✓] All required packages installed" -ForegroundColor Green
Write-Host ""

# ════════════════════════════════════════════════════════════════
# 3. START POSTGRESQL IN DOCKER
# ════════════════════════════════════════════════════════════════

Write-Host "[INFO] Checking Docker and PostgreSQL status..." -ForegroundColor Cyan

# Check if docker is available
try {
    $dockerCheck = & docker ps 2>&1
    Write-Host "[✓] Docker is available" -ForegroundColor Green
}
catch {
    Write-Host "[WARN] Docker not found - you may need to start PostgreSQL manually" -ForegroundColor Yellow
    Write-Host "[INFO] To start manually:" -ForegroundColor Yellow
    Write-Host "       docker-compose up -d postgres" -ForegroundColor Green
    Write-Host ""
}

# Check if PostgreSQL container is running
$pgContainer = & docker ps --filter "name=postgres" --quiet 2>$null
if (-not $pgContainer) {
    Write-Host "[INFO] Starting PostgreSQL + pgvector in Docker..." -ForegroundColor Cyan
    & docker-compose up -d postgres 2>&1 | Out-Null
    
    if ($LASTEXITCODE -eq 0) {
        Write-Host "[✓] PostgreSQL started" -ForegroundColor Green
        Write-Host "[INFO] Waiting 15 seconds for PostgreSQL to initialize..." -ForegroundColor Cyan
        Start-Sleep -Seconds 15
    }
    else {
        Write-Host "[WARN] Docker compose failed - PostgreSQL may not start" -ForegroundColor Yellow
        Write-Host "[INFO] You can try manual start:" -ForegroundColor Yellow
        Write-Host "       docker-compose up -d postgres" -ForegroundColor Green
    }
}
else {
    Write-Host "[✓] PostgreSQL is already running" -ForegroundColor Green
}

Write-Host ""

# ════════════════════════════════════════════════════════════════
# 4. TEST DATABASE CONNECTION
# ════════════════════════════════════════════════════════════════

Write-Host "[INFO] Testing database connection..." -ForegroundColor Cyan
$testDbScript = @"
try:
    from sqlalchemy import create_engine, text
    import os
    from dotenv import load_dotenv
    
    load_dotenv()
    db_url = os.getenv('DATABASE_URL', 'postgresql://root:password@localhost:5433/smartops_core')
    engine = create_engine(db_url, pool_pre_ping=True)
    
    with engine.connect() as conn:
        result = conn.execute(text('SELECT 1'))
    
    print('DB_OK')
except Exception as e:
    print(f'DB_FAIL:{str(e)[:50]}')
"@

$dbTest = & $pythonExe -c $testDbScript 2>&1
if ($dbTest -match "DB_OK") {
    Write-Host "[✓] Database connection successful" -ForegroundColor Green
}
else {
    Write-Host "[WARN] Database connection failed" -ForegroundColor Yellow
    Write-Host "        This is OK if Docker is still starting" -ForegroundColor Gray
}

Write-Host ""

# ════════════════════════════════════════════════════════════════
# 5. LAUNCH FASTAPI SERVER
# ════════════════════════════════════════════════════════════════

Write-Host "╔═══════════════════════════════════════════════════════════╗" -ForegroundColor Green
Write-Host "║  ✓ READY TO START FASTAPI                                 ║" -ForegroundColor Green
Write-Host "╚═══════════════════════════════════════════════════════════╝" -ForegroundColor Green
Write-Host ""
Write-Host "📍 FastAPI will run on: http://localhost:8001" -ForegroundColor Cyan
Write-Host "📍 API Docs:           http://localhost:8001/docs" -ForegroundColor Cyan
Write-Host "📍 ReDoc:              http://localhost:8001/redoc" -ForegroundColor Cyan
Write-Host ""
Write-Host "QUICK TEST COMMANDS:" -ForegroundColor Yellow
Write-Host '  curl http://localhost:8001/'
Write-Host '  curl http://localhost:8001/semantic-engine/health'
Write-Host ""
Write-Host "Press Ctrl+C to stop the server" -ForegroundColor Yellow
Write-Host ""

# Start uvicorn
& $pythonExe -m uvicorn app.main:app --reload --port 8001 --host 0.0.0.0

Write-Host ""
Write-Host "Server stopped" -ForegroundColor Yellow
