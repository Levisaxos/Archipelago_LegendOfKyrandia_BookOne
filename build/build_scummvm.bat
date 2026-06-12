@echo off
REM Build the minimal Kyra+SDL2 ScummVM solution with MSBuild.
REM Retargets the generated VS2017 (v141) projects to the installed v143 toolset + Win11 SDK.
set "SCUMMVM_LIBS=D:\GIT-Home\LegendOfKyrandia\build\deps\SDL2-2.32.2"
set "MSBUILD=C:\Program Files\Microsoft Visual Studio\2022\Professional\MSBuild\Current\Bin\MSBuild.exe"
set "SLN=D:\GIT-Home\LegendOfKyrandia\build\msvc\scummvm.sln"
"%MSBUILD%" "%SLN%" ^
  /p:Configuration=Release /p:Platform=x64 ^
  /p:PlatformToolset=v143 ^
  /p:WindowsTargetPlatformVersion=10.0.26100.0 ^
  /m /v:minimal /nologo
echo ===MSBUILD EXITCODE %errorlevel%===
