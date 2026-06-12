@echo off
REM Standalone compile test for the apclientpp library stack (no ScummVM).
set "PATH=C:\Program Files (x86)\Microsoft Visual Studio\Installer;%PATH%"
call "C:\Program Files\Microsoft Visual Studio\2022\Professional\Common7\Tools\VsDevCmd.bat" -arch=amd64 -host_arch=amd64 >nul
cd /d "D:\GIT-Home\LegendOfKyrandia\build\deps\ap"
set "AP=D:\GIT-Home\LegendOfKyrandia\build\deps\ap"
cl /nologo /EHsc /std:c++17 /Zc:__cplusplus ^
  /DASIO_STANDALONE /DAP_NO_SCHEMA /DWSWRAP_NO_SSL /DWSWRAP_NO_COMPRESSION /D_WIN32_WINNT=0x0601 /DWIN32_LEAN_AND_MEAN ^
  /I "%AP%\apclientpp" /I "%AP%\wswrap\include" /I "%AP%\asio\asio\include" /I "%AP%\websocketpp" /I "%AP%\json" ^
  test_connect.cpp ^
  /Fe:test_connect.exe ^
  /link ws2_32.lib shell32.lib
echo ===CL EXITCODE %errorlevel%===
