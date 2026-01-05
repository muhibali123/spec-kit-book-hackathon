@echo off
REM Startup batch file for RAG backend with proper environment loading

REM Navigate to backend directory
cd /d "%~dp0\backend"

REM Load environment variables from .env file using PowerShell
for /f "tokens=*" %%a in ('type .env 2^>nul ^| findstr /v "^#" 2^>nul') do (
    for /f "tokens=1* delims==" %%b in ("%%a") do (
        set "%%b=%%c"
    )
)

REM Display loaded environment variables
echo Environment variables loaded from .env

REM Start the uvicorn server
echo Starting RAG backend server on port 8000...
python -m uvicorn src.main:app --host 0.0.0.0 --port 8000 --reload