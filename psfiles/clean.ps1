param (
    [switch]$keepPyd
)

$baseDir = Split-Path -Path $PSScriptRoot -Parent
$buildDir = Join-Path -Path $baseDir -ChildPath "build"
$pydFile = Join-Path -Path $baseDir -ChildPath "python\encryption_backend.pyd"

Write-Host "Cleaning build files..."

if (Test-Path $buildDir) {
    Write-Host "Removing build directory: $buildDir"
    Remove-Item -Path $buildDir -Recurse -Force
} else {
    Write-Host "Build directory not found."
}

if (-not $keepPyd.IsPresent) {
    if (Test-Path $pydFile) {
        Write-Host "Removing .pyd file: $pydFile"
        Remove-Item -Path $pydFile -Force
    } else {
        Write-Host ".pyd file not found."
    }
} else {
    Write-Host "Keeping .pyd file as requested."
}

Write-Host "Cleanup complete."
