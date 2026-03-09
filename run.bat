@echo off
cd /d "%~dp0"
set "PATH=%~dp0ffmpeg\bin;%PATH%"

REM If venv is missing, run setup first
if not exist "venv\Scripts\python.exe" (
    echo  First run detected - running setup...
    call install_and_run.bat
    exit /b
)

start "" "%~dp0venv\Scripts\python.exe" "%~dp0main.py"
