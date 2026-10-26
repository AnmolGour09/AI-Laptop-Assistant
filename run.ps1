# Start both the LiveKit agent worker and the Jarvis frontend.

$projectRoot = Split-Path -Parent $MyInvocation.MyCommand.Path
$python = Join-Path $projectRoot "venv\Scripts\python.exe"

if (-not (Test-Path $python)) {
    throw "Virtual environment not found at $python. Create it and install requirements.txt first."
}

Push-Location $projectRoot
try {
    & $python ".\run_jarvis.py"
    if ($LASTEXITCODE -ne 0) {
        throw "Jarvis stopped with exit code $LASTEXITCODE."
    }
}
finally {
    Pop-Location
}
