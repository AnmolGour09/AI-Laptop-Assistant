$ErrorActionPreference = "Stop"

$python = Join-Path (Get-Location) "venv\Scripts\python.exe"
if (-not (Test-Path $python)) {
    throw "Virtual environment not found at $python. Create it and install requirements.txt first."
}

& $python ".\web_server.py"
