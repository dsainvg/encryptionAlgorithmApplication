<#
.SYNOPSIS
    Build script for the C++ pybind11 extension (encryption_backend) on Windows.
.DESCRIPTION
    Automates configuration + build steps for the encryption backend using CMake.
.PARAMETER Configuration
    Build configuration (Release or Debug). Default: Release
.PARAMETER Generator
    CMake generator (defaults to latest Visual Studio found). Example: "Visual Studio 17 2022"
.EXAMPLE
    powershell -ExecutionPolicy Bypass -File build.ps1
.EXAMPLE
    ./build.ps1 -Configuration Debug
#>
param(
    [string]$Configuration = "Release",
    [string]$Generator = "Visual Studio 17 2022",
    [switch]$Clean
)

$ErrorActionPreference = 'Stop'

$script:Root = Split-Path -Parent (Split-Path -Parent $MyInvocation.MyCommand.Path)
Set-Location $script:Root

Write-Host "Python Build Configuration" -ForegroundColor Magenta
Write-Host "Note: This module requires Python to run" -ForegroundColor Yellow
Write-Host ""

$buildDir = Join-Path $Root 'build'
if (!(Test-Path $buildDir)) { New-Item -ItemType Directory -Path $buildDir | Out-Null }
if ($Clean) {
    Write-Host "Cleaning build directory..." -ForegroundColor Yellow
    Remove-Item -Recurse -Force (Join-Path $buildDir '*') -ErrorAction SilentlyContinue
}

Write-Host "Configuring (Generator=$Generator, Config=$Configuration)..." -ForegroundColor Cyan
Push-Location $buildDir

$srcDir = Join-Path $Root 'cpp'
$configureArgs = @(
    '-G', $Generator,
    '-A', 'x64',
    '-DPYBIND11_FINDPYTHON=ON',
    $srcDir
)

Write-Host "Running: cmake $($configureArgs -join ' ')" -ForegroundColor DarkGray
cmake @configureArgs

Write-Host "Building ($Configuration)..." -ForegroundColor Cyan
cmake --build . --config $Configuration

$artifact = Join-Path $buildDir $Configuration | Join-Path -ChildPath 'encryption_backend.pyd'
if (Test-Path $artifact) {
    Write-Host "Build succeeded: $artifact" -ForegroundColor Green
    $dest = Join-Path $Root 'python'
    Copy-Item $artifact $dest -Force
    Write-Host "Copied module to: $dest" -ForegroundColor Green
} else {
    Write-Warning "encryption_backend.pyd not found; check build output."
}

Pop-Location
