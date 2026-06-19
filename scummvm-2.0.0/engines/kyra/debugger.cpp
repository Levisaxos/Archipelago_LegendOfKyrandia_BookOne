/* ScummVM - Graphic Adventure Engine
 *
 * ScummVM is the legal property of its developers, whose names
 * are too numerous to list here. Please refer to the COPYRIGHT
 * file distributed with this source distribution.
 *
 * This program is free software; you can redistribute it and/or
 * modify it under the terms of the GNU General Public License
 * as published by the Free Software Foundation; either version 2
 * of the License, or (at your option) any later version.
 *
 * This program is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 * GNU General Public License for more details.
 *
 * You should have received a copy of the GNU General Public License
 * along with this program; if not, write to the Free Software
 * Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA.
 *
 */

#include "kyra/debugger.h"
#include "kyra/kyra_lok.h"
#include "kyra/animator_lok.h"
#include "kyra/kyra_hof.h"
#include "kyra/timer.h"
#include "kyra/resource.h"
#include "kyra/lol.h"
#include "kyra/eobcommon.h"
#include "kyra/wsamovie.h"

#include "common/system.h"
#include "common/config-manager.h"
#include "common/file.h"
#include "common/util.h"

namespace Kyra {

// AP: defined in kyra_v1.cpp — human-readable names for known game flags.
const char *kyraApFlagName(int flag);

Debugger::Debugger(KyraEngine_v1 *vm)
	: ::GUI::Debugger(), _vm(vm) {
}

void Debugger::initialize() {
	registerCmd("continue",           WRAP_METHOD(Debugger, cmdExit));
	registerCmd("screen_debug_mode",  WRAP_METHOD(Debugger, cmdSetScreenDebug));
	registerCmd("load_palette",       WRAP_METHOD(Debugger, cmdLoadPalette));
	registerCmd("facings",            WRAP_METHOD(Debugger, cmdShowFacings));
	registerCmd("gamespeed",          WRAP_METHOD(Debugger, cmdGameSpeed));
	registerCmd("flags",              WRAP_METHOD(Debugger, cmdListFlags));
	registerCmd("toggleflag",         WRAP_METHOD(Debugger, cmdToggleFlag));
	registerCmd("queryflag",          WRAP_METHOD(Debugger, cmdQueryFlag));
	registerCmd("timers",             WRAP_METHOD(Debugger, cmdListTimers));
	registerCmd("settimercountdown",  WRAP_METHOD(Debugger, cmdSetTimerCountdown));
}

bool Debugger::cmdSetScreenDebug(int argc, const char **argv) {
	if (argc > 1) {
		if (scumm_stricmp(argv[1], "enable") == 0)
			_vm->screen()->enableScreenDebug(true);
		else if (scumm_stricmp(argv[1], "disable") == 0)
			_vm->screen()->enableScreenDebug(false);
		else
			debugPrintf("Use screen_debug_mode <enable/disable> to enable or disable it.\n");
	} else {
		debugPrintf("Screen debug mode is %s.\n", (_vm->screen()->queryScreenDebug() ? "enabled" : "disabled"));
		debugPrintf("Use screen_debug_mode <enable/disable> to enable or disable it.\n");
	}
	return true;
}

bool Debugger::cmdLoadPalette(int argc, const char **argv) {
	Palette palette(_vm->screen()->getPalette(0).getNumColors());

	if (argc <= 1) {
		debugPrintf("Use load_palette <file> [start_col] [end_col]\n");
		return true;
	}

	if (_vm->game() != GI_KYRA1 && _vm->resource()->getFileSize(argv[1]) != 768) {
		uint8 *buffer = new uint8[320 * 200 * sizeof(uint8)];
		if (!buffer) {
			debugPrintf("ERROR: Cannot allocate buffer for screen region!\n");
			return true;
		}

		_vm->screen()->copyRegionToBuffer(5, 0, 0, 320, 200, buffer);
		_vm->screen()->loadBitmap(argv[1], 5, 5, 0);
		palette.copy(_vm->screen()->getCPagePtr(5), 0, 256);
		_vm->screen()->copyBlockToPage(5, 0, 0, 320, 200, buffer);

		delete[] buffer;
	} else if (!_vm->screen()->loadPalette(argv[1], palette)) {
		debugPrintf("ERROR: Palette '%s' not found!\n", argv[1]);
		return true;
	}

	int startCol = 0;
	int endCol = palette.getNumColors();
	if (argc > 2)
		startCol = MIN(palette.getNumColors(), MAX(0, atoi(argv[2])));
	if (argc > 3)
		endCol = MIN(palette.getNumColors(), MAX(0, atoi(argv[3])));

	if (startCol > 0)
		palette.copy(_vm->screen()->getPalette(0), 0, startCol);
	if (endCol < palette.getNumColors())
		palette.copy(_vm->screen()->getPalette(0), endCol);

	_vm->screen()->setScreenPalette(palette);
	_vm->screen()->updateScreen();

	return true;
}

bool Debugger::cmdShowFacings(int argc, const char **argv) {
	debugPrintf("Facing directions:\n");
	debugPrintf("7  0  1\n");
	debugPrintf(" \\ | / \n");
	debugPrintf("6--*--2\n");
	debugPrintf(" / | \\\n");
	debugPrintf("5  4  3\n");
	return true;
}

bool Debugger::cmdGameSpeed(int argc, const char **argv) {
	if (argc == 2) {
		int val = atoi(argv[1]);

		if (val < 1 || val > 1000) {
			debugPrintf("speed must lie between 1 and 1000 (default: 60)\n");
			return true;
		}

		_vm->_tickLength = (uint8)(1000.0 / val);
	} else {
		debugPrintf("Syntax: gamespeed <value>\n");
	}

	return true;
}

bool Debugger::cmdListFlags(int argc, const char **argv) {
	for (int i = 0, p = 0; i < (int)sizeof(_vm->_flagsTable) * 8; i++, ++p) {
		debugPrintf("(%-3i): %-2i", i, _vm->queryGameFlag(i));
		if (p == 5) {
			debugPrintf("\n");
			p -= 6;
		}
	}
	debugPrintf("\n");
	// --- AP: also dump every SET flag to the engine log so we can diff two states
	//     (e.g. broken vs repaired bridge) offline. Prefix "APFLAGDUMP". ---
	for (int i = 0; i < (int)sizeof(_vm->_flagsTable) * 8; i++)
		if (_vm->queryGameFlag(i))
			warning("APFLAGDUMP flag=%d (0x%X) %s", i, i, kyraApFlagName(i));
	return true;
}

bool Debugger::cmdToggleFlag(int argc, const char **argv) {
	if (argc > 1) {
		uint flag = atoi(argv[1]);
		if (_vm->queryGameFlag(flag))
			_vm->resetGameFlag(flag);
		else
			_vm->setGameFlag(flag);
		debugPrintf("Flag %i is now %i\n", flag, _vm->queryGameFlag(flag));
	} else {
		debugPrintf("Syntax: toggleflag <flag>\n");
	}

	return true;
}

bool Debugger::cmdQueryFlag(int argc, const char **argv) {
	if (argc > 1) {
		uint flag = atoi(argv[1]);
		debugPrintf("Flag %i is %i\n", flag, _vm->queryGameFlag(flag));
	} else {
		debugPrintf("Syntax: queryflag <flag>\n");
	}

	return true;
}

bool Debugger::cmdListTimers(int argc, const char **argv) {
	debugPrintf("Current time: %-8u\n", g_system->getMillis());
	for (int i = 0; i < _vm->timer()->count(); i++)
		debugPrintf("Timer %-2i: Active: %-3s Countdown: %-6i %-8u\n", i, _vm->timer()->isEnabled(i) ? "Yes" : "No", _vm->timer()->getDelay(i), _vm->timer()->getNextRun(i));

	return true;
}

bool Debugger::cmdSetTimerCountdown(int argc, const char **argv) {
	if (argc > 2) {
		uint timer = atoi(argv[1]);
		uint countdown = atoi(argv[2]);
		_vm->timer()->setCountdown(timer, countdown);
		debugPrintf("Timer %i now has countdown %i\n", timer, _vm->timer()->getDelay(timer));
	} else {
		debugPrintf("Syntax: settimercountdown <timer> <countdown>\n");
	}

	return true;
}

#pragma mark -

Debugger_LoK::Debugger_LoK(KyraEngine_LoK *vm)
	: Debugger(vm), _vm(vm) {
}

void Debugger_LoK::initialize() {
	registerCmd("enter",              WRAP_METHOD(Debugger_LoK, cmdEnterRoom));
	registerCmd("scenes",             WRAP_METHOD(Debugger_LoK, cmdListScenes));
	registerCmd("give",               WRAP_METHOD(Debugger_LoK, cmdGiveItem));
	registerCmd("birthstones",        WRAP_METHOD(Debugger_LoK, cmdListBirthstones));
	registerCmd("dumpscenes",         WRAP_METHOD(Debugger_LoK, cmdDumpScenes));
	registerCmd("dumproomtable",      WRAP_METHOD(Debugger_LoK, cmdDumpRoomTable));
	registerCmd("dumpitems",          WRAP_METHOD(Debugger_LoK, cmdDumpItems));
	registerCmd("dumpamulet",         WRAP_METHOD(Debugger_LoK, cmdDumpAmulet));
	Debugger::initialize();
}

// AP dev: write a sub-region of a kyra screen page (8bpp indexed) out as a 24-bit BMP,
// expanding each palette index through the currently applied palette (slot 0) and
// nearest-neighbour upscaling by an integer factor. 24-bit keeps it viewer-agnostic and
// sidesteps indexed-BMP palette quirks; integer scaling adds no detail, just bigger pixels.
static void dumpRegionToBmp(Screen *screen, int page, int srcX, int srcY, int srcW, int srcH,
                            int scale, const Common::String &filename) {
	if (scale < 1)
		scale = 1;

	uint8 *indices = new uint8[srcW * srcH];
	screen->copyRegionToBuffer(page, srcX, srcY, srcW, srcH, indices);
	uint8 *pal = screen->getPalette(0).fetchRealPalette();   // 256 * RGB, caller deletes

	Common::DumpFile out;
	if (!out.open(filename, true)) {   // createPath: makes the output dir if needed
		warning("APDUMP could not open %s for writing", filename.c_str());
		delete[] indices;
		delete[] pal;
		return;
	}

	const int outW = srcW * scale;
	const int outH = srcH * scale;
	const uint32 stride = outW * 3;
	const uint32 pad = (4 - (stride & 3)) & 3;   // BMP rows are 4-byte aligned
	const uint32 rowSize = stride + pad;
	const uint32 imageSize = rowSize * outH;
	const uint32 dataOffset = 14 + 40;

	// BITMAPFILEHEADER
	out.writeByte('B');
	out.writeByte('M');
	out.writeUint32LE(dataOffset + imageSize);
	out.writeUint32LE(0);
	out.writeUint32LE(dataOffset);
	// BITMAPINFOHEADER
	out.writeUint32LE(40);
	out.writeUint32LE(outW);
	out.writeUint32LE(outH);
	out.writeUint16LE(1);
	out.writeUint16LE(24);
	out.writeUint32LE(0);
	out.writeUint32LE(imageSize);
	out.writeUint32LE(0);
	out.writeUint32LE(0);
	out.writeUint32LE(0);
	out.writeUint32LE(0);

	// Pixel rows are stored bottom-up and as BGR; each source pixel becomes a scale x scale block.
	uint8 *row = new uint8[rowSize];
	for (int oy = outH - 1; oy >= 0; --oy) {
		const uint8 *src = indices + (oy / scale) * srcW;
		uint8 *d = row;
		for (int sx = 0; sx < srcW; ++sx) {
			const uint8 *c = pal + src[sx] * 3;
			for (int s = 0; s < scale; ++s) {
				*d++ = c[2];   // B
				*d++ = c[1];   // G
				*d++ = c[0];   // R
			}
		}
		for (uint32 p = 0; p < pad; ++p)
			*d++ = 0;
		out.write(row, rowSize);
	}
	delete[] row;

	out.finalize();
	out.close();
	delete[] indices;
	delete[] pal;
}

bool Debugger_LoK::cmdEnterRoom(int argc, const char **argv) {
	uint direction = 0;
	if (argc > 1) {
		int room = atoi(argv[1]);

		// game will crash if entering a non-existent room
		if (room < 0 || room >= _vm->_roomTableSize) {
			debugPrintf("room number must be any value between (including) 0 and %d\n", _vm->_roomTableSize - 1);
			return true;
		}

		// some in-range room slots have no actual room data (invalid nameIndex) and
		// would crash on load — reject those instead of entering them.
		if (_vm->_roomTable[room].nameIndex >= _vm->_roomFilenameTableSize) {
			debugPrintf("room %d is not a valid scene (no room data)\n", room);
			return true;
		}

		// unused slots can have an in-range nameIndex but no real room (no exits) and
		// still crash on a cold teleport — reject those too. Real scenes have >=1 exit.
		if (_vm->_roomTable[room].northExit == 0xFFFF && _vm->_roomTable[room].eastExit == 0xFFFF &&
		    _vm->_roomTable[room].southExit == 0xFFFF && _vm->_roomTable[room].westExit == 0xFFFF) {
			debugPrintf("room %d has no exits (likely not a real scene)\n", room);
			return true;
		}

		if (argc > 2) {
			direction = atoi(argv[2]);
		} else {
			if (_vm->_roomTable[room].northExit != 0xFFFF)
				direction = 3;
			else if (_vm->_roomTable[room].eastExit != 0xFFFF)
				direction = 4;
			else if (_vm->_roomTable[room].southExit != 0xFFFF)
				direction = 1;
			else if (_vm->_roomTable[room].westExit != 0xFFFF)
				direction = 2;
		}

		_vm->_system->hideOverlay();
		_vm->_currentCharacter->facing = direction;

		_vm->enterNewScene(room, _vm->_currentCharacter->facing, 0, 0, 1);
		while (!_vm->_screen->isMouseVisible())
			_vm->_screen->showMouse();

		detach();
		return false;
	}

	debugPrintf("Syntax: room <roomnum> <direction>\n");
	return true;
}

bool Debugger_LoK::cmdListScenes(int argc, const char **argv) {
	for (int i = 0; i < _vm->_roomTableSize; i++) {
		debugPrintf("%-3i: %-10s", i, _vm->_roomFilenameTable[_vm->_roomTable[i].nameIndex]);
		if (!(i % 8))
			debugPrintf("\n");
	}
	debugPrintf("\n");
	debugPrintf("Current room: %i\n", _vm->_currentRoom);
	return true;
}

// AP dev: walk every room and dump one BMP each — the rendered in-game view with the
// background, ground items and scene animations, but with the actor sprites (Brandon +
// NPCs) suppressed. Files land in a "dumps" subfolder of ScummVM's working directory
// as dumps/kyra_scene_<NNN>_<ROOM>.bmp.
// Usage: dumpscenes [first] [last]
bool Debugger_LoK::cmdDumpScenes(int argc, const char **argv) {
	int first = 0;
	int last = _vm->_roomTableSize - 1;
	if (argc > 1)
		first = atoi(argv[1]);
	if (argc > 2)
		last = atoi(argv[2]);
	first = CLIP(first, 0, _vm->_roomTableSize - 1);
	last = CLIP(last, first, _vm->_roomTableSize - 1);

	const int savedRoom = _vm->_currentCharacter->sceneId;
	const int savedFacing = _vm->_currentCharacter->facing;

	// Capture static scenes: don't run the per-scene entry scripts (cutscenes/dialogue).
	_vm->_dumpSceneMode = true;

	int count = 0;
	for (int room = first; room <= last; ++room) {
		if (_vm->_roomTable[room].nameIndex >= _vm->_roomFilenameTableSize)
			continue;

		const char *name = _vm->_roomFilenameTable[_vm->_roomTable[room].nameIndex];

		// Skip dead/placeholder room-table entries whose scene data was never shipped
		// (e.g. MAPLE) — entering one would crash on the missing scene file. Real rooms
		// ship a loose archive (talkie: NAME.PAK/.VRM/.APK that setupSceneResource mounts)
		// or have NAME.DAT in the global archive (non-talkie). MAPLE has none of these.
		Common::String base(name);
		bool hasData = _vm->_res->exists((base + ".PAK").c_str())
		            || _vm->_res->exists((base + ".VRM").c_str())
		            || _vm->_res->exists((base + ".APK").c_str())
		            || _vm->_res->exists((base + ".DAT").c_str());
		if (!hasData) {
			debugPrintf("skipped %d: %s (no data file)\n", room, name);
			continue;
		}

		_vm->enterNewScene(room, _vm->_currentCharacter->facing, 0, 0, 1);

		// Re-composite the play area (page 2 -> page 0) with actors suppressed, so the
		// scene art, items and animations remain but Brandon/NPCs are erased.
		_vm->_animator->_noDrawCharactersFlag = 1;
		_vm->_animator->restoreAllObjectBackgrounds();   // erase all sprites from page 2
		_vm->_animator->prepDrawAllObjects();            // redraw items/anims only (no actors)
		_vm->_screen->copyRegion(8, 8, 8, 8, 304, 128, 2, 0, Screen::CR_NO_P_CHECK);
		_vm->_animator->_noDrawCharactersFlag = 0;

		// Capture only the scene viewport (304x128 at 8,8) — no UI border, name bar,
		// OPTIONS or inventory — upscaled 2x to 608x256.
		Common::String path = Common::String::format("dumps/kyra_scene_%03d_%s.bmp", room, name);
		dumpRegionToBmp(_vm->_screen, 0, 8, 8, 304, 128, 2, path);

		// Redraw actors so the live view is consistent again before the next entry.
		_vm->_animator->updateAllObjectShapes();

		++count;
		debugPrintf("dumped %d: %s\n", room, name);
	}

	// Restore normal scripting and re-enter the player's original scene properly.
	_vm->_dumpSceneMode = false;
	_vm->enterNewScene(savedRoom, savedFacing, 0, 0, 1);
	while (!_vm->_screen->isMouseVisible())
		_vm->_screen->showMouse();

	debugPrintf("Done. Dumped %d character-free scenes to the 'dumps' folder.\n", count);
	return true;
}

// AP dev: dump the room exit table as CSV (id,name,north,east,south,west) to
// dumps/room_table.csv (and echo to the console). Exit value 0xFFFF (no exit) is
// written as -1. This is the spatial adjacency that drives the PopTracker scene
// grid: north -> row-1, south -> row+1, east -> col+1, west -> col-1.
// Usage: dumproomtable
bool Debugger_LoK::cmdDumpRoomTable(int argc, const char **argv) {
	Common::DumpFile out;
	bool toFile = out.open("dumps/room_table.csv");
	if (!toFile)
		debugPrintf("Could not open dumps/room_table.csv; printing to console only.\n");

	const char *header = "id,name,north,east,south,west\n";
	if (toFile)
		out.writeString(header);
	debugPrintf("%s", header);

	for (int i = 0; i < _vm->_roomTableSize; i++) {
		const char *name = (_vm->_roomTable[i].nameIndex < _vm->_roomFilenameTableSize)
		                       ? _vm->_roomFilenameTable[_vm->_roomTable[i].nameIndex] : "?";
		int n = (_vm->_roomTable[i].northExit == 0xFFFF) ? -1 : _vm->_roomTable[i].northExit;
		int e = (_vm->_roomTable[i].eastExit  == 0xFFFF) ? -1 : _vm->_roomTable[i].eastExit;
		int s = (_vm->_roomTable[i].southExit == 0xFFFF) ? -1 : _vm->_roomTable[i].southExit;
		int w = (_vm->_roomTable[i].westExit  == 0xFFFF) ? -1 : _vm->_roomTable[i].westExit;
		Common::String line = Common::String::format("%d,%s,%d,%d,%d,%d\n", i, name, n, e, s, w);
		if (toFile)
			out.writeString(line);
		debugPrintf("%s", line.c_str());
	}

	if (toFile) {
		out.close();
		debugPrintf("Wrote %d rooms to dumps/room_table.csv\n", _vm->_roomTableSize);
	}
	return true;
}

// AP dev: dump every inventory item sprite (16x16) to dumps/kyra_item_<NNN>.bmp.
// Items live at _shapes[216 + id] (id 0..106; some alias to a shared shape). The shape
// is drawn onto a box pre-filled with colour 0; palette index 0 is temporarily forced
// to magenta so the transparent background keys out cleanly in post-processing. Sprites
// are integer-upscaled (x4 -> 64x64) for visibility / use as PopTracker icons.
// Usage: dumpitems
bool Debugger_LoK::cmdDumpItems(int argc, const char **argv) {
	const int X = 16, Y = 16, W = 16, H = 16, SCALE = 4;

	// Force colour 0 (the shape transparency index) to magenta in the dump palette,
	// without touching the live display (no setScreenPalette). Restored at the end.
	Palette &pal = _vm->_screen->getPalette(0);
	const uint8 sr = pal[0], sg = pal[1], sb = pal[2];
	pal[0] = 63; pal[1] = 0; pal[2] = 63;   // 6-bit VGA magenta -> 0xFF00FF in the BMP

	int count = 0;
	for (int item = 0; item <= 106; ++item) {
		if (!_vm->_shapes[216 + item])
			continue;
		_vm->_screen->fillRect(X, Y, X + W - 1, Y + H - 1, 0, 0);
		_vm->_screen->drawShape(0, _vm->_shapes[216 + item], X, Y, 0, 0);
		Common::String path = Common::String::format("dumps/kyra_item_%03d.bmp", item);
		dumpRegionToBmp(_vm->_screen, 0, X, Y, W, H, SCALE, path);
		++count;
	}

	pal[0] = sr; pal[1] = sg; pal[2] = sb;   // restore index 0
	debugPrintf("Done. Dumped %d item sprites (16x16, x%d) to the 'dumps' folder.\n",
	            count, SCALE);
	return true;
}

// AP dev: dump the amulet UI graphic and its four power jewels. The base amulet is the
// AMULET.WSA movie (played via _amuleteAnim onto 224,152, same as o1_makeAmuletAppear);
// the jewels are shapes 0x144-0x147 drawn at the four _amuletX/_amuletY anchor points
// (same as drawAmulet). Produces dumps/kyra_amulet_full.bmp (base + all 4 jewels) and
// kyra_amulet_pos0..3.bmp (base + a single jewel) so each power gets a distinct icon.
// Palette index 0 is keyed magenta for clean transparency. Usage: dumpamulet
bool Debugger_LoK::cmdDumpAmulet(int argc, const char **argv) {
	const int BX = 216, BY = 150, BW = 96, BH = 50, SCALE = 4;
	// jewel shape per anchor (matches the final frame of each amuletTable in drawAmulet).
	const int jewelShape[4] = { 0x145, 0x147, 0x144, 0x146 };
	const uint16 *jx = _vm->_amuletX, *jy = _vm->_amuletY;

	Palette &pal = _vm->_screen->getPalette(0);
	const uint8 sr = pal[0], sg = pal[1], sb = pal[2];
	pal[0] = 63; pal[1] = 0; pal[2] = 63;   // magenta transparency key

	Movie *amulet = _vm->createWSAMovie();
	if (!amulet || !amulet->open("AMULET.WSA", 1, 0) || !amulet->opened()) {
		debugPrintf("Could not open AMULET.WSA\n");
		pal[0] = sr; pal[1] = sg; pal[2] = sb;
		delete amulet;
		return true;
	}

	// variant 0 = full amulet (all 4 jewels); variants 1..4 = base + single jewel i-1.
	for (int variant = 0; variant <= 4; ++variant) {
		_vm->_screen->fillRect(BX, BY, BX + BW - 1, BY + BH - 1, 0, 0);
		for (int i = 0; _vm->_amuleteAnim[i] != 0xFF; ++i)
			amulet->displayFrame(_vm->_amuleteAnim[i], 0, 224, 152, 0, 0, 0);

		Common::String path;
		if (variant == 0) {
			for (int i = 0; i < 4; ++i)
				_vm->_screen->drawShape(0, _vm->_shapes[jewelShape[i]], jx[i], jy[i], 0, 0);
			path = "dumps/kyra_amulet_full.bmp";
		} else {
			int i = variant - 1;
			_vm->_screen->drawShape(0, _vm->_shapes[jewelShape[i]], jx[i], jy[i], 0, 0);
			path = Common::String::format("dumps/kyra_amulet_pos%d.bmp", i);
		}
		dumpRegionToBmp(_vm->_screen, 0, BX, BY, BW, BH, SCALE, path);
	}

	delete amulet;
	pal[0] = sr; pal[1] = sg; pal[2] = sb;
	debugPrintf("Done. Dumped amulet (full + 4 single-jewel) to the 'dumps' folder.\n");
	return true;
}

bool Debugger_LoK::cmdGiveItem(int argc, const char **argv) {
	if (argc == 2) {
		int item = atoi(argv[1]);

		// Kyrandia 1 has only 108 items (-1 to 106), otherwise it will crash
		if (item < -1 || item > 106) {
			debugPrintf("'itemid' must be any value between (including) -1 and 106\n");
			return true;
		}

		_vm->setMouseItem(item);
		_vm->_itemInHand = item;
	} else {
		debugPrintf("Syntax: give <itemid>\n");
	}

	return true;
}

bool Debugger_LoK::cmdListBirthstones(int argc, const char **argv) {
	debugPrintf("Needed birthstone gems:\n");
	for (int i = 0; i < ARRAYSIZE(_vm->_birthstoneGemTable); ++i)
		debugPrintf("%-3d '%s'\n", _vm->_birthstoneGemTable[i], _vm->_itemList[_vm->_birthstoneGemTable[i]]);
	return true;
}

#pragma mark -

Debugger_v2::Debugger_v2(KyraEngine_v2 *vm) : Debugger(vm), _vm(vm) {
}

void Debugger_v2::initialize() {
	registerCmd("character_info",     WRAP_METHOD(Debugger_v2, cmdCharacterInfo));
	registerCmd("enter",              WRAP_METHOD(Debugger_v2, cmdEnterScene));
	registerCmd("scenes",             WRAP_METHOD(Debugger_v2, cmdListScenes));
	registerCmd("scene_info",         WRAP_METHOD(Debugger_v2, cmdSceneInfo));
	registerCmd("scene_to_facing",    WRAP_METHOD(Debugger_v2, cmdSceneToFacing));
	registerCmd("give",               WRAP_METHOD(Debugger_v2, cmdGiveItem));
	Debugger::initialize();
}

bool Debugger_v2::cmdEnterScene(int argc, const char **argv) {
	uint direction = 0;
	if (argc > 1) {
		int scene = atoi(argv[1]);

		// game will crash if entering a non-existent scene
		if (scene >= _vm->_sceneListSize) {
			debugPrintf("scene number must be any value between (including) 0 and %d\n", _vm->_sceneListSize - 1);
			return true;
		}

		if (argc > 2) {
			direction = atoi(argv[2]);
		} else {
			if (_vm->_sceneList[scene].exit1 != 0xFFFF)
				direction = 4;
			else if (_vm->_sceneList[scene].exit2 != 0xFFFF)
				direction = 6;
			else if (_vm->_sceneList[scene].exit3 != 0xFFFF)
				direction = 0;
			else if (_vm->_sceneList[scene].exit4 != 0xFFFF)
				direction = 2;
		}

		_vm->_system->hideOverlay();
		_vm->_mainCharacter.facing = direction;

		_vm->enterNewScene(scene, _vm->_mainCharacter.facing, 0, 0, 1);
		while (!_vm->screen_v2()->isMouseVisible())
			_vm->screen_v2()->showMouse();

		detach();
		return false;
	}

	debugPrintf("Syntax: %s <scenenum> <direction>\n", argv[0]);
	return true;
}

bool Debugger_v2::cmdListScenes(int argc, const char **argv) {
	int shown = 1;
	for (int i = 0; i < _vm->_sceneListSize; ++i) {
		if (_vm->_sceneList[i].filename1[0]) {
			debugPrintf("%-2i: %-10s", i, _vm->_sceneList[i].filename1);
			if (!(shown % 5))
				debugPrintf("\n");
			++shown;
		}
	}
	debugPrintf("\n");
	debugPrintf("Current scene: %i\n", _vm->_currentScene);
	return true;
}

bool Debugger_v2::cmdSceneInfo(int argc, const char **argv) {
	debugPrintf("Current scene: %d '%s'\n", _vm->_currentScene, _vm->_sceneList[_vm->_currentScene].filename1);
	debugPrintf("\n");
	debugPrintf("Exit information:\n");
	debugPrintf("Exit1: leads to %d, position %dx%d\n", int16(_vm->_sceneExit1), _vm->_sceneEnterX1, _vm->_sceneEnterY1);
	debugPrintf("Exit2: leads to %d, position %dx%d\n", int16(_vm->_sceneExit2), _vm->_sceneEnterX2, _vm->_sceneEnterY2);
	debugPrintf("Exit3: leads to %d, position %dx%d\n", int16(_vm->_sceneExit3), _vm->_sceneEnterX3, _vm->_sceneEnterY3);
	debugPrintf("Exit4: leads to %d, position %dx%d\n", int16(_vm->_sceneExit4), _vm->_sceneEnterX4, _vm->_sceneEnterY4);
	debugPrintf("Special exit information:\n");
	if (!_vm->_specialExitCount) {
		debugPrintf("No special exits.\n");
	} else {
		debugPrintf("This scene has %d special exits.\n", _vm->_specialExitCount);
		for (int i = 0; i < _vm->_specialExitCount; ++i) {
			debugPrintf("SpecialExit%d: facing %d, position (x1/y1/x2/y2): %d/%d/%d/%d\n", i,
			            _vm->_specialExitTable[20 + i], _vm->_specialExitTable[0 + i], _vm->_specialExitTable[5 + i],
			            _vm->_specialExitTable[10 + i], _vm->_specialExitTable[15 + i]);
		}
	}

	return true;
}

bool Debugger_v2::cmdCharacterInfo(int argc, const char **argv) {
	debugPrintf("Main character is in scene: %d '%s'\n", _vm->_mainCharacter.sceneId, _vm->_sceneList[_vm->_mainCharacter.sceneId].filename1);
	debugPrintf("Position: %dx%d\n", _vm->_mainCharacter.x1, _vm->_mainCharacter.y1);
	debugPrintf("Facing: %d\n", _vm->_mainCharacter.facing);
	debugPrintf("Inventory:\n");
	for (int i = 0; i < 20; ++i) {
		debugPrintf("%-2d ", int8(_vm->_mainCharacter.inventory[i]));
		if (i == 9 || i == 19)
			debugPrintf("\n");
	}
	return true;
}

bool Debugger_v2::cmdSceneToFacing(int argc, const char **argv) {
	if (argc == 2) {
		int facing = atoi(argv[1]);
		int16 exit = -1;

		switch (facing) {
		case 0: case 1: case 7:
			exit = _vm->_sceneList[_vm->_currentScene].exit1;
			break;

		case 6:
			exit = _vm->_sceneList[_vm->_currentScene].exit2;
			break;

		case 3: case 4: case 5:
			exit = _vm->_sceneList[_vm->_currentScene].exit3;
			break;

		case 2:
			exit = _vm->_sceneList[_vm->_currentScene].exit4;
			break;

		default:
			break;
		}

		debugPrintf("Exit to facing %d leads to room %d.\n", facing, exit);
	} else {
		debugPrintf("Usage: %s <facing>\n", argv[0]);
	}

	return true;
}

bool Debugger_v2::cmdGiveItem(int argc, const char **argv) {
	if (argc == 2) {
		int item = atoi(argv[1]);

		if (item < -1 || item > _vm->engineDesc().maxItemId) {
			debugPrintf("itemid must be any value between (including) -1 and %d\n", _vm->engineDesc().maxItemId);
			return true;
		}

		_vm->setHandItem(item);
	} else {
		debugPrintf("Syntax: give <itemid>\n");
	}

	return true;
}

#pragma mark -

Debugger_HoF::Debugger_HoF(KyraEngine_HoF *vm) : Debugger_v2(vm), _vm(vm) {
}

void Debugger_HoF::initialize() {
	registerCmd("pass_codes",         WRAP_METHOD(Debugger_HoF, cmdPasscodes));
	Debugger_v2::initialize();
}

bool Debugger_HoF::cmdPasscodes(int argc, const char **argv) {
	if (argc == 2) {
		int val = atoi(argv[1]);

		if (val < 0 || val > 1) {
			debugPrintf("value must be either 1 (on) or 0 (off)\n");
			return true;
		}

		_vm->_dbgPass = val;
	} else {
		debugPrintf("Syntax: pass_codes <0/1>\n");
	}

	return true;
}

#pragma mark -

#ifdef ENABLE_LOL
Debugger_LoL::Debugger_LoL(LoLEngine *vm) : Debugger(vm), _vm(vm) {
}
#endif // ENABLE_LOL

#ifdef ENABLE_EOB
Debugger_EoB::Debugger_EoB(EoBCoreEngine *vm) : Debugger(vm), _vm(vm) {
}

void Debugger_EoB::initialize() {
	registerCmd("import_savefile", WRAP_METHOD(Debugger_EoB, cmdImportSaveFile));
	registerCmd("save_original", WRAP_METHOD(Debugger_EoB, cmdSaveOriginal));
	registerCmd("list_monsters", WRAP_METHOD(Debugger_EoB, cmdListMonsters));
	registerCmd("show_position", WRAP_METHOD(Debugger_EoB, cmdShowPosition));
	registerCmd("set_position", WRAP_METHOD(Debugger_EoB, cmdSetPosition));
	registerCmd("open_door", WRAP_METHOD(Debugger_EoB, cmdOpenDoor));
	registerCmd("close_door", WRAP_METHOD(Debugger_EoB, cmdCloseDoor));
	registerCmd("list_flags", WRAP_METHOD(Debugger_EoB, cmdListFlags));
	registerCmd("set_flag", WRAP_METHOD(Debugger_EoB, cmdSetFlag));
	registerCmd("clear_flag", WRAP_METHOD(Debugger_EoB, cmdClearFlag));
}

bool Debugger_EoB::cmdImportSaveFile(int argc, const char **argv) {
	if (!_vm->_allowImport) {
		debugPrintf("This command only works from the main menu.\n");
		return true;
	}

	if (argc == 3) {
		int slot = atoi(argv[1]);
		if (slot < -1 || slot > 989) {
			debugPrintf("slot must be between (including) -1 and 989 \n");
			return true;
		}

		debugPrintf(_vm->importOriginalSaveFile(slot, argv[2]) ? "Success.\n" : "Failure.\n");
		_vm->loadItemDefs();
	} else {
		debugPrintf("Syntax:   import_savefile <dest slot> <source file>\n              (Imports source save game file to dest slot.)\n          import_savefile -1\n              (Imports all original save game files found and puts them into the first available slots.)\n\n");
	}

	return true;
}

bool Debugger_EoB::cmdSaveOriginal(int argc, const char **argv) {
	if (!_vm->_runFlag) {
		debugPrintf("This command doesn't work during intro or outro sequences,\nfrom the main menu or from the character generation.\n");
		return true;
	}

	Common::String dir = ConfMan.get("savepath");
	if (dir == "None")
		dir.clear();

	Common::FSNode nd(dir);
	if (!nd.isDirectory())
		return false;

	if (_vm->game() == GI_EOB1) {
		if (argc == 1) {
			if (_vm->saveAsOriginalSaveFile()) {
				Common::FSNode nf = nd.getChild(Common::String::format("EOBDATA.SAV"));
				if (nf.isReadable())
					debugPrintf("Saved to file: %s\n\n", nf.getPath().c_str());
				else
					debugPrintf("Failure.\n");
			} else {
				debugPrintf("Failure.\n");
			}
		} else {
			debugPrintf("Syntax:   save_original\n          (Saves game in original file format to a file which can be used with the original game executable.)\n\n");
		}
		return true;

	} else if (argc == 2) {
		int slot = atoi(argv[1]);
		if (slot < 0 || slot > 5) {
			debugPrintf("Slot must be between (including) 0 and 5.\n");
		} else if (_vm->saveAsOriginalSaveFile(slot)) {
			Common::FSNode nf = nd.getChild(Common::String::format("EOBDATA%d.SAV", slot));
			if (nf.isReadable())
				debugPrintf("Saved to file: %s\n\n", nf.getPath().c_str());
			else
				debugPrintf("Failure.\n");
		} else {
			debugPrintf("Failure.\n");
		}
		return true;
	}

	debugPrintf("Syntax:   save_original <slot>\n          (Saves game in original file format to a file which can be used with the original game executable.\n          A save slot between 0 and 5 must be specified.)\n\n");
	return true;
}

bool Debugger_EoB::cmdListMonsters(int, const char **) {
	debugPrintf("\nCurrent level: %d\n----------------------\n\n", _vm->_currentLevel);
	debugPrintf("Id        Type      Unit      Block     Position  Direction Sub Level Mode      Dst.block HP        Flags\n--------------------------------------------------------------------------------------------------------------\n");

	for (int i = 0; i < 30; i++) {
		EoBMonsterInPlay *m = &_vm->_monsters[i];
		debugPrintf("%.02d        %.02d        %.02d        0x%.04x    %d         %d         %d         %.02d        0x%.04x    %.03d/%.03d   0x%.02x\n", i, m->type, m->unit, m->block, m->pos, m->dir, m->sub, m->mode, m->dest, m->hitPointsCur, m->hitPointsMax, m->flags);
	}

	debugPrintf("\n");

	return true;
}

bool Debugger_EoB::cmdShowPosition(int, const char **) {
	debugPrintf("\nCurrent level:      %d\nCurrent Sub Level:  %d\nCurrent block:      %d (0x%.04x)\nNext block:         %d (0x%.04x)\nCurrent direction:  %d\n\n", _vm->_currentLevel, _vm->_currentSub, _vm->_currentBlock, _vm->_currentBlock, _vm->calcNewBlockPosition(_vm->_currentBlock, _vm->_currentDirection), _vm->calcNewBlockPosition(_vm->_currentBlock, _vm->_currentDirection), _vm->_currentDirection);
	return true;
}

bool Debugger_EoB::cmdSetPosition(int argc, const char **argv) {
	if (argc == 4) {
		_vm->_currentBlock = atoi(argv[3]);
		int sub = atoi(argv[2]);
		int level = atoi(argv[1]);

		int maxLevel = (_vm->game() == GI_EOB1) ? 12 : 16;
		if (level < 1 || level > maxLevel) {
			debugPrintf("<level> must be a value from 1 to %d.\n\n", maxLevel);
			return true;
		}

		if (level != _vm->_currentLevel || sub != _vm->_currentSub) {
			_vm->completeDoorOperations();
			_vm->generateTempData();
			_vm->txt()->removePageBreakFlag();
			_vm->screen()->setScreenDim(7);

			_vm->loadLevel(level, sub);

			if (_vm->_dialogueField)
				_vm->restoreAfterDialogueSequence();
		}

		_vm->moveParty(_vm->_currentBlock);

		_vm->_sceneUpdateRequired = true;
		_vm->gui_drawAllCharPortraitsWithStats();
		debugPrintf("Success.\n\n");

	} else {
		debugPrintf("Syntax:   set_position <level>, <sub level>, <block>\n");
		debugPrintf("          (Warning: The sub level and block position parameters will not be checked. Invalid parameters may cause problems.)\n\n");
	}
	return true;
}

bool Debugger_EoB::cmdOpenDoor(int, const char **) {
	debugPrintf("Warning: Using this command may cause glitches.\n");
	uint16 block = _vm->calcNewBlockPosition(_vm->_currentBlock, _vm->_currentDirection);
	int c = (_vm->_wllWallFlags[_vm->_levelBlockProperties[block].walls[0]] & 8) ? 0 : 1;
	int v = _vm->_levelBlockProperties[block].walls[c];
	int flg = (_vm->_flags.gameID == GI_EOB1) ? 1 : 0x10;
	if (_vm->_wllWallFlags[v] & flg) {
		debugPrintf("Couldn't open any door. Make sure you're facing the door you wish to open and standing right in front of it.\n\n");
	} else {
		_vm->openDoor(block);
		debugPrintf("Trying to open door at block %d.\n\n", block);
	}
	return true;
}

bool Debugger_EoB::cmdCloseDoor(int, const char **) {
	debugPrintf("Warning: Using this command may cause glitches.\n");
	uint16 block = _vm->calcNewBlockPosition(_vm->_currentBlock, _vm->_currentDirection);
	int c = (_vm->_wllWallFlags[_vm->_levelBlockProperties[block].walls[0]] & 8) ? 0 : 1;
	int v = _vm->_levelBlockProperties[block].walls[c];
	if ((_vm->_flags.gameID == GI_EOB1 && !(_vm->_wllWallFlags[v] & 1)) || (_vm->_flags.gameID == GI_EOB2 && (_vm->_wllWallFlags[v] & 0x20))) {
		debugPrintf("Couldn't close any door. Make sure you're facing the door you wish to close and standing right in front of it.\n\n");
	} else {
		_vm->closeDoor(block);
		debugPrintf("Trying to close door at block %d.\n\n", block);
	}
	return true;
}

bool Debugger_EoB::cmdListFlags(int, const char **) {
	debugPrintf("Flag           Status\n----------------------\n\n");
	for (int i = 0; i < 32; i++) {
		uint32 flag = 1 << i;
		debugPrintf("%.2d             %s\n", i, _vm->checkScriptFlags(flag) ? "TRUE" : "FALSE");
	}
	debugPrintf("\n");
	return true;
}

bool Debugger_EoB::cmdSetFlag(int argc, const char **argv) {
	if (argc != 2) {
		debugPrintf("Syntax:   set_flag <flag>\n\n");
		return true;
	}

	int flag = atoi(argv[1]);
	if (flag < 0 || flag > 31) {
		debugPrintf("<flag> must be a value from 0 to 31.\n\n");
	} else {
		_vm->setScriptFlags(1 << flag);
		debugPrintf("Flag '%.2d' has been set.\n\n", flag);
	}

	return true;
}

bool Debugger_EoB::cmdClearFlag(int argc, const char **argv) {
	if (argc != 2) {
		debugPrintf("Syntax:   clear_flag <flag>\n\n");
		return true;
	}

	int flag = atoi(argv[1]);
	if (flag < 0 || flag > 31) {
		debugPrintf("<flag> must be a value from 0 to 31.\n\n");
	} else {
		_vm->clearScriptFlags(1 << flag);
		debugPrintf("Flag '%.2d' has been cleared.\n\n", flag);
	}

	return true;
}

#endif // ENABLE_EOB

} // End of namespace Kyra
