@echo off
setlocal enabledelayedexpansion
title YouTube MP3 Downloader - Build EXE
color 0E
cd /d "%~dp0"

echo.
echo  ==========================================
echo   Build: YT-MP3-Downloader.exe
echo  ==========================================
echo.

REM ── Find Python ───────────────────────────────────────────────
set "PYTHON="
py      --version >nul 2>&1 && set "PYTHON=py"      && goto :PY_OK
python  --version >nul 2>&1 && set "PYTHON=python"  && goto :PY_OK
python3 --version >nul 2>&1 && set "PYTHON=python3" && goto :PY_OK
echo  [ERROR] Python not found. Install from https://www.python.org/downloads/
pause & exit /b 1

:PY_OK
for /f "tokens=*" %%V in ('!PYTHON! --version 2^>^&1') do echo  [OK] %%V

REM ── Install build tools ───────────────────────────────────────
echo  [..] Installing pyinstaller + yt-dlp...
!PYTHON! -m pip install --upgrade pyinstaller yt-dlp --quiet ^
  --trusted-host pypi.org --trusted-host files.pythonhosted.org
echo  [OK] Build tools ready.

REM ── Download ffmpeg if not present ────────────────────────────
if exist "ffmpeg_bin\ffmpeg.exe" (
    echo  [OK] ffmpeg already in ffmpeg_bin\
    goto :BUILD
)

echo  [..] Downloading ffmpeg for bundling...
curl --version >nul 2>&1
if !ERRORLEVEL! equ 0 (
    curl -L --progress-bar -o ffmpeg_build.zip "https://www.gyan.dev/ffmpeg/builds/ffmpeg-release-essentials.zip"
) else (
    powershell -NoProfile -ExecutionPolicy Bypass -Command ^
      "[Net.ServicePointManager]::SecurityProtocol=[Net.SecurityProtocolType]::Tls12; (New-Object Net.WebClient).DownloadFile('https://www.gyan.dev/ffmpeg/builds/ffmpeg-release-essentials.zip','ffmpeg_build.zip')"
)

echo  [..] Extracting...
powershell -NoProfile -ExecutionPolicy Bypass -Command "Expand-Archive -Path 'ffmpeg_build.zip' -DestinationPath 'ffmpeg_build_temp' -Force"
if not exist "ffmpeg_bin" mkdir "ffmpeg_bin"
for /d %%D in (ffmpeg_build_temp\ffmpeg-*) do (
    copy /Y "%%D\bin\ffmpeg.exe"  "ffmpeg_bin\ffmpeg.exe"  >nul 2>&1
    copy /Y "%%D\bin\ffprobe.exe" "ffmpeg_bin\ffprobe.exe" >nul 2>&1
)
rd /s /q ffmpeg_build_temp >nul 2>&1
del ffmpeg_build.zip >nul 2>&1
echo  [OK] ffmpeg ready for bundling.

:BUILD
REM ── Run PyInstaller ───────────────────────────────────────────
echo.
echo  [..] Building EXE (this takes 1-3 minutes)...
echo.

!PYTHON! -m PyInstaller --onefile --windowed ^
  --name "YT-MP3-Downloader" ^
  --add-binary "ffmpeg_bin\ffmpeg.exe;." ^
  --add-binary "ffmpeg_bin\ffprobe.exe;." ^
  --clean ^
  main.py

if !ERRORLEVEL! neq 0 (
    echo.
    echo  [ERROR] Build failed. See output above for details.
    pause
    exit /b 1
)

echo.
echo  ==========================================
echo   Build complete!
echo   Output: dist\YT-MP3-Downloader.exe
echo  ==========================================
echo.
echo  The EXE is fully standalone - share dist\YT-MP3-Downloader.exe directly.
echo  No Python, ffmpeg, or installation needed on the target machine.
echo.
pause
