=======================================
  YouTube MP3 Downloader - Windows
=======================================

OPTION A: STANDALONE EXE (recommended)
---------------------------------------
Just double-click:  YT-MP3-Downloader.exe
No installation needed. ffmpeg is built in.

If you don't have the .exe yet, get it from:
  https://github.com/jotoltd/YTMP3DL/releases/latest


OPTION B: RUN FROM SOURCE
--------------------------
1. Install Python from https://www.python.org/downloads/
   ** IMPORTANT: Check "Add Python to PATH" during install! **

2. Double-click:  install_and_run.bat
   This automatically installs everything and launches the app.

3. After first install, use:  run.bat


BUILD YOUR OWN EXE (on Windows)
--------------------------------
1. Run install_and_run.bat first (installs dependencies)
2. Double-click:  build_exe.bat
3. Find the finished EXE at:  dist\YT-MP3-Downloader.exe


SELF-UPDATE
-----------
When a new version is released on GitHub, the app shows a yellow
banner at the top. Click "Update Now" to download and apply
automatically. The app restarts with the new version.


NOTES
-----
- Downloaded MP3s are saved to your Downloads folder by default.
- 320 kbps MP3, with metadata and album art embedded.
- ffmpeg is bundled in the EXE - no separate install needed.

FILES IN THIS FOLDER
--------------------
  main.py              - The app source code
  requirements.txt     - Python dependencies
  install_and_run.bat  - First-time setup + launcher (Option B)
  run.bat              - Quick launcher after first install
  build_exe.bat        - Builds standalone EXE on Windows
  README.txt           - This file
