@echo off
REM Compile the AP bridge into ap_bridge.lib, quarantining apclientpp/asio/websocketpp.
REM MUST match ScummVM's runtime (/MD MultiThreadedDLL) so it links into scummvm.exe.
set "PATH=C:\Program Files (x86)\Microsoft Visual Studio\Installer;%PATH%"
call "C:\Program Files\Microsoft Visual Studio\2022\Professional\Common7\Tools\VsDevCmd.bat" -arch=amd64 -host_arch=amd64 >nul
set "AP=D:\GIT-Home\LegendOfKyrandia\build\deps\ap"
cd /d "%AP%\bridge"
cl /nologo /c /MD /EHsc /std:c++17 /Zc:__cplusplus /O2 ^
  /DASIO_STANDALONE /DAP_NO_SCHEMA /DWSWRAP_NO_SSL /DWSWRAP_NO_COMPRESSION /D_WIN32_WINNT=0x0601 /DWIN32_LEAN_AND_MEAN ^
  /I "%AP%\apclientpp" /I "%AP%\wswrap\include" /I "%AP%\asio\asio\include" /I "%AP%\websocketpp" /I "%AP%\json" ^
  ap_bridge.cpp /Fo:ap_bridge.obj
if errorlevel 1 (echo COMPILE FAILED & exit /b 1)
lib /nologo /OUT:ap_bridge.lib ap_bridge.obj
echo ===AP_BRIDGE BUILD EXITCODE %errorlevel%===
