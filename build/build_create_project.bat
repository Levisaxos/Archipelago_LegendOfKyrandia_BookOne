@echo off
REM Compile ScummVM's create_project.exe (the MSVC solution generator).
REM Uses VS 2022 Professional (v143) developer environment.
set "PATH=C:\Program Files (x86)\Microsoft Visual Studio\Installer;%PATH%"
call "C:\Program Files\Microsoft Visual Studio\2022\Professional\Common7\Tools\VsDevCmd.bat" -arch=amd64 -host_arch=amd64 >nul
if errorlevel 1 (echo VsDevCmd setup FAILED & exit /b 1)
cd /d "D:\GIT-Home\LegendOfKyrandia\scummvm-2.0.0\devtools\create_project"
cl /nologo /EHsc /O2 /Fe:create_project.exe *.cpp Rpcrt4.lib
