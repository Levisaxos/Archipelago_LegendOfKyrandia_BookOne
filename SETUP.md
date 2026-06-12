# Setup — reconstituting a buildable tree

This repo deliberately excludes the vanilla ScummVM source and all third-party
build dependencies (large, re-fetchable). After a fresh clone, do the following
once. Windows + Visual Studio 2022 (Desktop C++ workload + a Windows SDK).

## 1. Restore the ScummVM 2.0.0 source

Only our **modified** `engines/kyra/` files are tracked. Get the rest of the
vanilla 2.0.0 tree from the GOG build's `scummvm-2.0.0.zip` (ships inside the GOG
*Legend of Kyrandia* install, under `scummvm/`):

```powershell
# extract the vanilla tree into scummvm-2.0.0\
Expand-Archive "<path to>\scummvm-2.0.0.zip" -DestinationPath . -Force
# the extract overwrites our 4 modified files with vanilla — restore ours:
git checkout -- scummvm-2.0.0/engines/kyra/
```

## 2. Fetch the third-party dependencies

```powershell
# SDL2 (prebuilt VC libs)
curl -L -o build\deps\SDL2-devel-2.32.2-VC.zip https://www.libsdl.org/release/SDL2-devel-2.32.2-VC.zip
Expand-Archive build\deps\SDL2-devel-2.32.2-VC.zip -DestinationPath build\deps -Force

# Archipelago client lib + its deps — PINNED versions (latest asio/websocketpp are incompatible)
cd build\deps\ap
git clone --depth 1 https://github.com/black-sliver/apclientpp.git
git clone --depth 1 https://github.com/black-sliver/wswrap.git
git clone --depth 1 --branch asio-1-12-2 https://github.com/chriskohlhoff/asio.git
git clone --depth 1 --branch 0.8.2 https://github.com/zaphoyd/websocketpp.git
mkdir json\nlohmann
curl -L -o json\nlohmann\json.hpp https://github.com/nlohmann/json/releases/latest/download/json.hpp
cd ..\..\..
```

## 3. Generate data + build

```powershell
python pyscripts\gen_ap_item_map.py        # regenerates build\deps\ap\bridge\ap_item_map.h
cmd /c build\build_create_project.bat      # build create_project.exe (once)
# generate the minimal Kyra+SDL2 MSVC solution (run once, from build\msvc\):
#   create_project ..\..\scummvm-2.0.0 --msvc --msvc-version 15 --disable-all-engines
#     --enable-engine=kyra --disable-libz --disable-mad --disable-vorbis --disable-flac
#     --disable-png --disable-theora --disable-freetype --disable-jpeg --disable-fluidsynth
#     --disable-libcurl --disable-sdlnet --disable-nasm
# then append the AP bridge include dir + ap_bridge.lib;ws2_32.lib;shell32.lib to
# ScummVM_Global64.props (see the props edits), and:
cmd /c build\build_ap_bridge.bat           # build ap_bridge.lib
cmd /c build\build_scummvm.bat             # build scummvm.exe (retargets to v143)
copy build\deps\SDL2-2.32.2\lib\x64\SDL2.dll build\msvc\Release64\
```

Output: `build\msvc\Release64\scummvm.exe`. Run it pointed at your own GOG
Kyrandia `DAT\` folder. See `roadmap/ROADMAP.md` and the project notes for the
build-environment quirks (VS install paths, `VsDevCmd` PATH fix, etc.).

> Tip: the exact dependency versions, defines, and link flags are encoded in the
> `build\*.bat` scripts — those are the source of truth for the build recipe.
