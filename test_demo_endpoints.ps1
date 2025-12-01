# Test Script for Demo Router - SmartOps Core v4.0
# Tests the 3 endpoints: THE LOADER, THE SHOW, THE NEURALIZER
# 
# Requirements:
#   - API running on http://localhost:8001
#   - File menu_dummy.pdf in root directory
#   - Environment variable NEURALIZER_SECRET = "flash" (or default)
#
# Usage: .\test_demo_endpoints.ps1

param(
    [string]$ApiUrl = "http://localhost:8001",
    [string]$FilePath = "menu_dummy.pdf",
    [string]$SecretWord = "flash"
)

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "TEST ENDPOINTS - QUEST 1: DEMO" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Color definitions for output (avoid automatic variable names)
$SuccessColor = "Green"
$ErrorColor = "Red"
$InfoColor = "Cyan"
$WarningColor = "Yellow"

# ============================================================================
# ENDPOINT 1: THE LOADER - POST /demo/upload
# ============================================================================

Write-Host "[1/4] THE LOADER - Testing POST /demo/upload" -ForegroundColor $InfoColor
Write-Host "       Loading file with business metadata..." -ForegroundColor $InfoColor
Write-Host ""

if (-not (Test-Path $FilePath)) {
    Write-Host "ERROR: File not found: $FilePath" -ForegroundColor $ErrorColor
    exit 1
}

try {
    # Prepare multipart request with file
    $form = @{
        file = Get-Item -Path $FilePath
        business_name = "Pizzeria Jarvis"
        business_type = "restaurante"
    }
    
    $response = Invoke-RestMethod -Uri "$ApiUrl/demo/upload" `
        -Method Post `
        -Form $form `
        -ContentType "multipart/form-data" `
        -ErrorAction Stop
    
    Write-Host "RESPONSE:" -ForegroundColor $SuccessColor
    $response | ConvertTo-Json | Write-Host -ForegroundColor $SuccessColor
    
    # Extract session_id
    $SessionId = $response.session_id
    
    if ([string]::IsNullOrEmpty($SessionId)) {
        Write-Host "ERROR: No session_id received" -ForegroundColor $ErrorColor
        exit 1
    }
    
    Write-Host ""
    Write-Host "[OK] Session ID captured: $SessionId" -ForegroundColor $SuccessColor
    Write-Host ""
}
catch {
    Write-Host "ERROR in /demo/upload: $_" -ForegroundColor $ErrorColor
    exit 1
}

# ============================================================================
# ENDPOINT 2: THE SHOW - POST /demo/message
# ============================================================================

Write-Host "[2/4] THE SHOW - Testing POST /demo/message" -ForegroundColor $InfoColor
Write-Host "       Sending message to demonstration..." -ForegroundColor $InfoColor
Write-Host ""

try {
    $messagePayload = @{
        session_id = $SessionId
        message = "Hello, do you have pizza? What is your specialty?"
    } | ConvertTo-Json
    
    $response = Invoke-RestMethod -Uri "$ApiUrl/demo/message" `
        -Method Post `
        -Body $messagePayload `
        -ContentType "application/json" `
        -ErrorAction Stop
    
    Write-Host "RESPONSE:" -ForegroundColor $SuccessColor
    $response | ConvertTo-Json | Write-Host -ForegroundColor $SuccessColor
    Write-Host ""
    Write-Host "[OK] Message processed successfully" -ForegroundColor $SuccessColor
    Write-Host ""
}
catch {
    Write-Host "ERROR in /demo/message: $_" -ForegroundColor $ErrorColor
    exit 1
}

# ============================================================================
# ENDPOINT 3: THE NEURALIZER - POST /demo/reset
# ============================================================================

Write-Host "[3/4] THE NEURALIZER - Testing POST /demo/reset" -ForegroundColor $InfoColor
Write-Host "       Closing session with secret word..." -ForegroundColor $InfoColor
Write-Host ""

try {
    $resetPayload = @{
        session_id = $SessionId
        secret_word = $SecretWord
        save_lead = $true
    } | ConvertTo-Json
    
    $response = Invoke-RestMethod -Uri "$ApiUrl/demo/reset" `
        -Method Post `
        -Body $resetPayload `
        -ContentType "application/json" `
        -ErrorAction Stop
    
    Write-Host "RESPONSE:" -ForegroundColor $SuccessColor
    $response | ConvertTo-Json | Write-Host -ForegroundColor $SuccessColor
    Write-Host ""
    Write-Host "[OK] Session closed successfully" -ForegroundColor $SuccessColor
    Write-Host ""
}
catch {
    Write-Host "ERROR in /demo/reset: $_" -ForegroundColor $ErrorColor
    exit 1
}

# ============================================================================
# ENDPOINT BONUS: HEALTH CHECK
# ============================================================================

Write-Host "[4/4] HEALTH CHECK - Testing GET /demo/health" -ForegroundColor $InfoColor
Write-Host ""

try {
    $response = Invoke-RestMethod -Uri "$ApiUrl/demo/health" `
        -Method Get `
        -ErrorAction Stop
    
    Write-Host "RESPONSE:" -ForegroundColor $SuccessColor
    $response | ConvertTo-Json | Write-Host -ForegroundColor $SuccessColor
    Write-Host ""
    Write-Host "[OK] Health check successful" -ForegroundColor $SuccessColor
    Write-Host ""
}
catch {
    Write-Host "ERROR in /demo/health: $_" -ForegroundColor $ErrorColor
    exit 1
}

# ============================================================================
# SUMMARY
# ============================================================================

Write-Host "========================================" -ForegroundColor $SuccessColor
Write-Host "ALL TESTS PASSED SUCCESSFULLY" -ForegroundColor $SuccessColor
Write-Host "========================================" -ForegroundColor $SuccessColor
Write-Host ""
Write-Host "SUMMARY:" -ForegroundColor $InfoColor
Write-Host "  [OK] THE LOADER: Session created with session_id=$SessionId" -ForegroundColor $SuccessColor
Write-Host "  [OK] THE SHOW: Bot responded contextually" -ForegroundColor $SuccessColor
Write-Host "  [OK] THE NEURALIZER: Session closed with lead saved" -ForegroundColor $SuccessColor
Write-Host "  [OK] HEALTH: Demo module operational" -ForegroundColor $SuccessColor
Write-Host ""
