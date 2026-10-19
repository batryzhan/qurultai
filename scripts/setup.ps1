$ErrorActionPreference = 'Stop'
$projectRoot = Split-Path -Parent $PSScriptRoot
Push-Location $projectRoot
try {
    if (-not (Test-Path -LiteralPath '.venv/Scripts/python.exe')) {
        python -m venv .venv
        if ($LASTEXITCODE -ne 0) { throw 'Creating the Python environment failed.' }
    }
    & ./.venv/Scripts/python.exe -m pip install -e './backend[dev]'
    if ($LASTEXITCODE -ne 0) { throw 'Backend dependency installation failed.' }
    if (-not (Test-Path -LiteralPath '.env')) {
        Copy-Item -LiteralPath '.env.example' -Destination '.env'
    }
    Push-Location frontend
    try {
        npm.cmd ci
        if ($LASTEXITCODE -ne 0) { throw 'Frontend dependency installation failed.' }
    } finally { Pop-Location }
    Write-Host 'Setup complete. Run ./scripts/start.ps1, then open http://127.0.0.1:5173.'
} finally { Pop-Location }
