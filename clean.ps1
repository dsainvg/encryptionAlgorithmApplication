# Clean up build artifacts and other generated files

$ErrorActionPreference = "SilentlyContinue"

Write-Host "Cleaning up project..." -ForegroundColor Yellow

# Directories to remove
$dirsToRemove = @(
    "build",
    "python/__pycache__"
)

# Files to remove
$filesToRemove = @(
    "python/encryption_backend.pyd"
)

foreach ($dir in $dirsToRemove) {
    $fullPath = Join-Path $PSScriptRoot $dir
    if (Test-Path $fullPath) {
        Write-Host "Removing directory: $fullPath"
        Remove-Item -Recurse -Force $fullPath
    }
}

foreach ($file in $filesToRemove) {
    $fullPath = Join-Path $PSScriptRoot $file
    if (Test-Path $fullPath) {
        Write-Host "Removing file: $fullPath"
        Remove-Item -Force $fullPath
    }
}

Write-Host "Cleanup complete." -ForegroundColor Green
