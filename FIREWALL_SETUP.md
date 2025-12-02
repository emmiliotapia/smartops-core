# Firewall Configuration Guide

## Issue
Ports 8001 (FastAPI) and 5432 (PostgreSQL) are blocked by Windows Firewall.

## Solution

### Option 1: Automatic (Recommended)
```bash
# Right-click on setup_firewall.bat
# Select "Run as administrator"
# Wait for confirmation
```

### Option 2: Manual PowerShell (Admin)
```powershell
# Open PowerShell as Administrator, then run:

# Open port 8001 for FastAPI
netsh advfirewall firewall add rule name="SmartOps FastAPI 8001" dir=in action=allow protocol=tcp localport=8001
netsh advfirewall firewall add rule name="SmartOps FastAPI 8001 OUT" dir=out action=allow protocol=tcp localport=8001

# Open port 5432 for PostgreSQL
netsh advfirewall firewall add rule name="SmartOps PostgreSQL 5432" dir=in action=allow protocol=tcp localport=5432
netsh advfirewall firewall add rule name="SmartOps PostgreSQL 5432 OUT" dir=out action=allow protocol=tcp localport=5432
```

### Option 3: Windows Firewall GUI
1. Open Windows Defender Firewall with Advanced Security
2. Click "Inbound Rules" → "New Rule"
3. Port → TCP → Port 8001 → Allow connection → Finish
4. Repeat for port 5432

## Verify Rules Were Added
```powershell
netsh advfirewall firewall show rule name="SmartOps*"
```

## Remove Rules (if needed)
```powershell
netsh advfirewall firewall delete rule name="SmartOps FastAPI 8001"
netsh advfirewall firewall delete rule name="SmartOps PostgreSQL 5432"
```

## After Firewall Configuration
```bash
# Start FastAPI
python start.py

# In another terminal, verify:
curl http://localhost:8001/demo/health
```

Expected response:
```json
{
  "status": "healthy",
  "module": "demo",
  "version": "1.0.0"
}
```
