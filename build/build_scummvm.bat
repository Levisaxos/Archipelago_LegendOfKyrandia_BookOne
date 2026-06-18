@echo off
REM Build the minimal Kyra+SDL2 ScummVM solution with MSBuild.
REM Retargets the generated VS2017 (v141) projects to the installed v145 toolset (VS 2026) + Win11 SDK.
REM Locates VS 2022 (any edition) + MSBuild via vswhere; repo path derived from this script's location.
set "VSWHERE=%ProgramFiles(x86)%\Microsoft Visual Studio\Installer\vswhere.exe"
if not exist "%VSWHERE%" (echo vswhere not found - is Visual Studio installed? & exit /b 1)
for /f "usebackq tokens=*" %%i in (`"%VSWHERE%" -latest -products * -requires Microsoft.Component.MSBuild -find MSBuild\**\Bin\MSBuild.exe`) do set "MSBUILD=%%i"
if not defined MSBUILD (echo MSBuild not found via vswhere & exit /b 1)
set "SCUMMVM_LIBS=%~dp0deps\SDL2-2.32.2"
set "SLN=%~dp0msvc\scummvm.sln"
"%MSBUILD%" "%SLN%" ^
  /p:Configuration=Release /p:Platform=x64 ^
  /p:PlatformToolset=v145 ^
  /p:WindowsTargetPlatformVersion=10.0.26100.0 ^
  /m /v:minimal /nologo
echo ===MSBUILD EXITCODE %errorlevel%===
