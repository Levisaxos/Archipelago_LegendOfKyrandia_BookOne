@echo off
REM Compile ScummVM's create_project.exe (the MSVC solution generator).
REM Locates VS 2022 (any edition) via vswhere; repo path derived from this script's location.
set "VSWHERE=%ProgramFiles(x86)%\Microsoft Visual Studio\Installer\vswhere.exe"
if not exist "%VSWHERE%" (echo vswhere not found - is Visual Studio installed? & exit /b 1)
for /f "usebackq tokens=*" %%i in (`"%VSWHERE%" -latest -products * -requires Microsoft.VisualStudio.Component.VC.Tools.x86.x64 -property installationPath`) do set "VSINSTALL=%%i"
if not defined VSINSTALL (echo No VS install with the C++ workload found & exit /b 1)
call "%VSINSTALL%\Common7\Tools\VsDevCmd.bat" -arch=amd64 -host_arch=amd64 >nul
if errorlevel 1 (echo VsDevCmd setup FAILED & exit /b 1)
cd /d "%~dp0..\scummvm-2.0.0\devtools\create_project"
cl /nologo /EHsc /O2 /Fe:create_project.exe *.cpp Rpcrt4.lib
echo ===CREATE_PROJECT BUILD EXITCODE %errorlevel%===
