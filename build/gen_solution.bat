@echo off
REM Generate the minimal Kyra-only MSVC solution into build\msvc\ using create_project.exe.
REM Prereq: build_create_project.bat has produced create_project.exe.
REM NOTE: after this runs you must re-apply the AP bridge edits to build\msvc\ScummVM_Global64.props
REM   - AdditionalIncludeDirectories: add  %~dp0deps\ap\bridge
REM   - AdditionalDependencies:       add  ap_bridge.lib;ws2_32.lib;shell32.lib
REM   (the generated solution does not know about the AP bridge; these edits wire it in)
set "CP=%~dp0..\scummvm-2.0.0\devtools\create_project\create_project.exe"
if not exist "%CP%" (echo create_project.exe missing - run build_create_project.bat first & exit /b 1)
if not exist "%~dp0msvc" mkdir "%~dp0msvc"
cd /d "%~dp0msvc"
"%CP%" ..\..\scummvm-2.0.0 --msvc --msvc-version 15 --disable-all-engines ^
  --enable-engine=kyra --disable-libz --disable-mad --disable-vorbis --disable-flac ^
  --disable-png --disable-theora --disable-freetype --disable-jpeg --disable-fluidsynth ^
  --disable-libcurl --disable-sdlnet --disable-nasm
echo ===GEN_SOLUTION EXITCODE %errorlevel%===
