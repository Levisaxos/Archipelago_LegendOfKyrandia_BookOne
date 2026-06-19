@echo off
REM Launch the forked ScummVM (dev/scrape build) on the GOG Kyrandia data.
REM Double-click this file to start the game. The exe is found relative to here;
REM the -p path points at your GOG "DAT" folder (edit if your data moves).
set "REL=%~dp0msvc\Release64"
start "" "%REL%\scummvm.exe" -p "E:\GOG Libriary\Legend of Kyrandia\DAT" kyra1
