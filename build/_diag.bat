@echo off
REM Diagnostic: locate VS 2022 (any edition) via vswhere and confirm cl is on PATH.
set "VSWHERE=%ProgramFiles(x86)%\Microsoft Visual Studio\Installer\vswhere.exe"
if not exist "%VSWHERE%" (echo vswhere not found - is Visual Studio installed? & exit /b 1)
for /f "usebackq tokens=*" %%i in (`"%VSWHERE%" -latest -products * -requires Microsoft.VisualStudio.Component.VC.Tools.x86.x64 -property installationPath`) do set "VSINSTALL=%%i"
if not defined VSINSTALL (echo No VS install with the C++ workload found & exit /b 1)
echo VSINSTALL=%VSINSTALL%
call "%VSINSTALL%\Common7\Tools\VsDevCmd.bat" -arch=amd64 -host_arch=amd64
echo ===EXITCODE %errorlevel%===
echo ===WHERE CL===
where cl
