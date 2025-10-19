#!/usr/bin/env pwsh
# Run smoke test with Python 3.14
# Quick test to verify the encryption backend module is working

Write-Host "Running Encryption Backend Smoke Test..." -ForegroundColor Cyan
Write-Host "Using Python 3.14" -ForegroundColor Yellow
Write-Host ""

$pythonPath = "C:\Users\dsain\AppData\Local\Programs\Python\Python314\python.exe"
$testScript = Join-Path $PSScriptRoot "python\_smoke_test.py"

if (Test-Path $pythonPath) {
    & $pythonPath $testScript
    if ($LASTEXITCODE -eq 0) {
        Write-Host ""
        Write-Host "✓ Smoke test passed!" -ForegroundColor Green
    } else {
        Write-Host ""
        Write-Host "✗ Smoke test failed!" -ForegroundColor Red
    }
} else {
    Write-Host "ERROR: Python 3.14 not found at expected location" -ForegroundColor Red
    Write-Host "Expected: $pythonPath" -ForegroundColor Yellow
    Write-Host "Please update the path in this script or install Python 3.14" -ForegroundColor Yellow
}

Read-Host "`nPress Enter to exit"
