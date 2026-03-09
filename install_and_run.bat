@echo off
setlocal enabledelayedexpansion
title YouTube MP3 Downloader - Setup
color 0B

echo.
echo  ==========================================
echo   YouTube MP3 Downloader  ^|  Auto-Setup
echo  ==========================================
echo.

REM ── Change to script directory ────────────────────────────────
cd /d "%~dp0"

REM ── Find Python (try py launcher, then python, then python3) ──
set "PYTHON="

py --version >nul 2>&1
if !ERRORLEVEL! equ 0 ( set "PYTHON=py" & goto :PYTHON_OK )

python --version >nul 2>&1
if !ERRORLEVEL! equ 0 ( set "PYTHON=python" & goto :PYTHON_OK )

python3 --version >nul 2>&1
if !ERRORLEVEL! equ 0 ( set "PYTHON=python3" & goto :PYTHON_OK )

echo  [ERROR] Python is not installed.
echo.
echo  Install it from: https://www.python.org/downloads/
echo  IMPORTANT: tick "Add Python to PATH" during install.
echo.
echo  Opening download page...
start https://www.python.org/downloads/
echo  After installing Python, double-click install_and_run.bat again.
echo.
pause
exit /b 1

:PYTHON_OK
for /f "tokens=*" %%V in ('!PYTHON! --version 2^>^&1') do echo  [OK] %%V detected.

REM ── Upgrade pip silently (fixes many SSL/network errors) ──────
echo  [..] Updating pip...
!PYTHON! -m pip install --upgrade pip --quiet ^
  --trusted-host pypi.org ^
  --trusted-host pypi.python.org ^
  --trusted-host files.pythonhosted.org >nul 2>&1

REM ── Validate / create virtual environment ─────────────────────
if exist "venv\Scripts\python.exe" (
    echo  [OK] Virtual environment found.
    goto :VENV_OK
)

REM Venv missing or broken - wipe and recreate
if exist "venv\" ( rd /s /q "venv" >nul 2>&1 )

echo  [..] Creating virtual environment...
!PYTHON! -m venv venv
if !ERRORLEVEL! neq 0 (
    echo  [WARN] Could not create venv, will use system Python instead.
    set "VENV_PYTHON=!PYTHON!"
    goto :INSTALL_DEPS
)

:VENV_OK
set "VENV_PYTHON=%~dp0venv\Scripts\python.exe"

:INSTALL_DEPS
REM ── Install / upgrade yt-dlp ──────────────────────────────────
echo  [..] Installing yt-dlp...
"!VENV_PYTHON!" -m pip install --upgrade yt-dlp --quiet ^
  --trusted-host pypi.org ^
  --trusted-host pypi.python.org ^
  --trusted-host files.pythonhosted.org
if !ERRORLEVEL! neq 0 (
    echo.
    echo  [ERROR] Failed to install yt-dlp.
    echo  Check your internet connection and run this file again.
    echo.
    pause
    exit /b 1
)
echo  [OK] yt-dlp ready.

REM ── Check for ffmpeg ──────────────────────────────────────────
ffmpeg -version >nul 2>&1
if !ERRORLEVEL! equ 0 ( echo  [OK] ffmpeg found in system PATH. & goto :LAUNCH )

if exist "%~dp0ffmpeg\bin\ffmpeg.exe" ( echo  [OK] ffmpeg found in local folder. & goto :LAUNCH )

REM ── Download ffmpeg (curl first, PowerShell fallback) ────────
set "FFMPEG_URL=https://www.gyan.dev/ffmpeg/builds/ffmpeg-release-essentials.zip"
echo  [..] Downloading ffmpeg (~30 MB)...

REM Try curl - built into Windows 10/11, shows a real progress bar
curl --version >nul 2>&1
if !ERRORLEVEL! equ 0 (
    curl -L --progress-bar -o "ffmpeg_dl.zip" "!FFMPEG_URL!"
    goto :FFMPEG_EXTRACT
)

REM Fallback: PowerShell with progress bar enabled
echo  [..] curl not found, using PowerShell...
powershell -NoProfile -ExecutionPolicy Bypass -Command ^
  "try { $ProgressPreference='Continue'; [Net.ServicePointManager]::SecurityProtocol=[Net.SecurityProtocolType]::Tls12; $wc=New-Object System.Net.WebClient; $wc.DownloadFile('!FFMPEG_URL!','ffmpeg_dl.zip'); Write-Host '  [OK] Download complete.' } catch { Write-Host ('  [ERROR] '+$_.Exception.Message); exit 1 }"

:FFMPEG_EXTRACT
if not exist "ffmpeg_dl.zip" (
    echo.
    echo  [WARN] ffmpeg download failed. MP3 conversion may not work.
    echo  You can manually install ffmpeg: https://ffmpeg.org/download.html
    echo.
    goto :LAUNCH
)

echo  [..] Extracting ffmpeg...
powershell -NoProfile -ExecutionPolicy Bypass -Command ^
  "Expand-Archive -Path 'ffmpeg_dl.zip' -DestinationPath 'ffmpeg_temp' -Force"

if not exist "ffmpeg\bin" mkdir "ffmpeg\bin"
for /d %%D in (ffmpeg_temp\ffmpeg-*) do (
    copy /Y "%%D\bin\ffmpeg.exe"  "ffmpeg\bin\ffmpeg.exe"  >nul 2>&1
    copy /Y "%%D\bin\ffprobe.exe" "ffmpeg\bin\ffprobe.exe" >nul 2>&1
)
rd /s /q ffmpeg_temp >nul 2>&1
del ffmpeg_dl.zip >nul 2>&1

if exist "ffmpeg\bin\ffmpeg.exe" (
    echo  [OK] ffmpeg installed locally.
) else (
    echo  [WARN] ffmpeg extraction may have failed. MP3 conversion might not work.
)

:LAUNCH
set "PATH=%~dp0ffmpeg\bin;%PATH%"
echo.
echo  ==========================================
echo   All done! Launching app...
echo  ==========================================
echo.

start "" "!VENV_PYTHON!" "%~dp0main.py"
timeout /t 3 /nobreak >nul
exit /b 0
