@echo off
set "PATH=C:\Program Files (x86)\Microsoft Visual Studio\Installer;%PATH%"
call "C:\Program Files\Microsoft Visual Studio\2022\Professional\Common7\Tools\VsDevCmd.bat" -arch=amd64 -host_arch=amd64
echo ===EXITCODE %errorlevel%===
echo ===WHERE CL===
where cl
