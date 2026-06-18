@echo off
REM Compile the AP bridge into ap_bridge.lib, quarantining apclientpp/asio/websocketpp.
REM MUST match ScummVM's runtime (/MD MultiThreadedDLL) so it links into scummvm.exe.
REM Locates VS 2022 (any edition) via vswhere; repo path derived from this script's location.
set "VSWHERE=%ProgramFiles(x86)%\Microsoft Visual Studio\Installer\vswhere.exe"
if not exist "%VSWHERE%" (echo vswhere not found - is Visual Studio installed? & exit /b 1)
for /f "usebackq tokens=*" %%i in (`"%VSWHERE%" -latest -products * -requires Microsoft.VisualStudio.Component.VC.Tools.x86.x64 -property installationPath`) do set "VSINSTALL=%%i"
if not defined VSINSTALL (echo No VS install with the C++ workload found & exit /b 1)
call "%VSINSTALL%\Common7\Tools\VsDevCmd.bat" -arch=amd64 -host_arch=amd64 >nul
set "AP=%~dp0deps\ap"
cd /d "%AP%\bridge"
cl /nologo /c /MD /EHsc /std:c++17 /Zc:__cplusplus /O2 ^
  /DASIO_STANDALONE /DAP_NO_SCHEMA /DWSWRAP_NO_SSL /DWSWRAP_NO_COMPRESSION /D_WIN32_WINNT=0x0601 /DWIN32_LEAN_AND_MEAN ^
  /I "%AP%\apclientpp" /I "%AP%\wswrap\include" /I "%AP%\asio\asio\include" /I "%AP%\websocketpp" /I "%AP%\json" ^
  ap_bridge.cpp /Fo:ap_bridge.obj
if errorlevel 1 (echo COMPILE FAILED & exit /b 1)
lib /nologo /OUT:ap_bridge.lib ap_bridge.obj
echo ===AP_BRIDGE BUILD EXITCODE %errorlevel%===
