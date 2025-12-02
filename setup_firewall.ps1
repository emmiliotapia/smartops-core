# SmartOps Firewall Configuration Script
# Run as Administrator

# Open port 8001 for FastAPI
netsh advfirewall firewall add rule name="SmartOps FastAPI 8001" dir=in action=allow protocol=tcp localport=8001
netsh advfirewall firewall add rule name="SmartOps FastAPI 8001" dir=out action=allow protocol=tcp localport=8001

# Open port 5432 for PostgreSQL
netsh advfirewall firewall add rule name="SmartOps PostgreSQL 5432" dir=in action=allow protocol=tcp localport=5432
netsh advfirewall firewall add rule name="SmartOps PostgreSQL 5432" dir=out action=allow protocol=tcp localport=5432

# Display results
Write-Host "✅ Firewall rules added successfully" -ForegroundColor Green
Write-Host ""
Write-Host "Ports opened:" -ForegroundColor Cyan
Write-Host "  8001  - FastAPI (API backend)"
Write-Host "  5432  - PostgreSQL (Database)"
Write-Host ""
Write-Host "You can now run: python start.py" -ForegroundColor Green
