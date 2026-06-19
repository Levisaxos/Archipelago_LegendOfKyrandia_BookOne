@echo off
setlocal
REM ---------------------------------------------------------------------------
REM Quick PopTracker test cycle: close PopTracker, repackage the pack folder into
REM a zip, drop it in PopTracker's packs dir, relaunch PopTracker.
REM (PopTracker auto-loads the last-used pack on startup, so once you've opened
REM  the zipped "legend_of_kyrandia" pack once, each run reloads it fresh.)
REM ---------------------------------------------------------------------------

set "SRC_PARENT=%~dp0poptracker"
set "PT_DIR=D:\Multiworld\Trackers\poptracker"
set "DEST=%PT_DIR%\packs\legend_of_kyrandia.zip"
set "EXE=%PT_DIR%\poptracker.exe"

echo Closing PopTracker...
taskkill /IM poptracker.exe /F >nul 2>&1
REM brief pause so Windows releases the lock on the old zip
ping -n 2 127.0.0.1 >nul

echo Zipping pack -^> %DEST%
del "%DEST%" >nul 2>&1
REM Use tar (bsdtar, ships with Windows 10/11) -- it writes spec-correct forward-slash
REM zip entries, unlike PowerShell's Compress-Archive which uses backslashes that
REM PopTracker can't read. -C cd's into the parent so the archive root is the pack folder.
tar.exe -a -c -f "%DEST%" -C "%SRC_PARENT%" legend_of_kyrandia
if errorlevel 1 (
  echo.
  echo ZIP FAILED - source folder present?  %SRC_PARENT%\legend_of_kyrandia
  pause
  exit /b 1
)

echo Launching PopTracker...
start "" "%EXE%"
endlocal
