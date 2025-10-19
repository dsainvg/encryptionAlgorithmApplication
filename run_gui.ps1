#!/usr/bin/env pwsh
# Run GUI with Python 3.14
# This script ensures the application runs with the correct Python version

Write-Host "Starting Secure File Encrypter GUI..." -ForegroundColor Cyan
Write-Host "Using Python 3.14" -ForegroundColor Yellow
Write-Host ""

$pythonPath = "C:\Users\dsain\AppData\Local\Programs\Python\Python314\python.exe"
$guiScript = Join-Path $PSScriptRoot "python\gui.py"

if (Test-Path $pythonPath) {
    & $pythonPath $guiScript
} else {
    Write-Host "ERROR: Python 3.14 not found at expected location" -ForegroundColor Red
    Write-Host "Expected: $pythonPath" -ForegroundColor Yellow
    Write-Host "Please update the path in this script or install Python 3.14" -ForegroundColor Yellow
    Read-Host "Press Enter to exit"
}
