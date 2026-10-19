$ErrorActionPreference = 'Stop'
$projectRoot = Split-Path -Parent $PSScriptRoot
$pythonPath = Join-Path $projectRoot '.venv/Scripts/python.exe'
if (-not (Test-Path -LiteralPath $pythonPath)) { throw 'Run ./scripts/setup.ps1 first.' }
Push-Location $projectRoot
try {
    $apiProcess = Start-Process -FilePath $pythonPath -ArgumentList @('-m', 'uvicorn', 'app.main:app', '--app-dir', 'backend', '--host', '127.0.0.1', '--port', '8000') -WorkingDirectory $projectRoot -PassThru -WindowStyle Hidden
    try {
        Push-Location frontend
        try { npm.cmd run dev } finally { Pop-Location }
    } finally {
        if (-not $apiProcess.HasExited) { Stop-Process -Id $apiProcess.Id }
    }
} finally { Pop-Location }
