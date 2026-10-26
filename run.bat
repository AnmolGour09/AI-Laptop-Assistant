@echo off
setlocal
cd /d "%~dp0"

if not exist "venv\Scripts\python.exe" (
    echo Virtual environment not found. Create it and install requirements.txt first.
    exit /b 1
)

"venv\Scripts\python.exe" "run_jarvis.py"
exit /b %ERRORLEVEL%
