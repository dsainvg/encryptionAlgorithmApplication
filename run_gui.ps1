#!/usr/bin/env pwsh
# Run GUI with Python 3.13
# This script ensures the application runs with the correct Python version

Write-Host "Starting Secure File Encrypter GUI..." -ForegroundColor Cyan
Write-Host "Using Python 3.13" -ForegroundColor Yellow
Write-Host ""

$pythonPath = "python"
$guiScript = "gui.py"
$pythonDir = Join-Path $PSScriptRoot "python"

try {
    Push-Location $pythonDir
    & $pythonPath $guiScript
    Pop-Location
} catch {
    Write-Host "ERROR: python not found or script failed. Please ensure python is in your PATH." -ForegroundColor Red
    Read-Host "Press Enter to exit"
    Pop-Location
}
