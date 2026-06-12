#ifndef KYRA_AP_BRIDGE_H
#define KYRA_AP_BRIDGE_H

// Plain C++ interface to the Archipelago client (apclientpp).
//
// This header deliberately exposes ONLY plain types (no AP / asio / websocketpp /
// nlohmann types), so ScummVM engine code can include it while staying compiled
// with ScummVM's own strict settings (no exceptions, forbidden-symbol guards).
// All the heavy template/websocket machinery lives in ap_bridge.cpp, which is
// compiled separately (C++17, exceptions on) into ap_bridge.lib.

namespace KyraAP {

// Begin connecting to an Archipelago server (non-blocking).
//   uri:      e.g. "ws://localhost:38281"
//   slot:     player/slot name in the multiworld
//   password: room password ("" if none)
void init(const char *uri, const char *slot, const char *password);

// Pump the client. Call once per frame; internal callbacks fire from here.
void poll();

// True once the slot is connected and authenticated.
bool isConnected();

// Human-readable status line for on-screen display (never null).
const char *statusText();

// Report a location check to the server.
void sendCheck(long long locationId);

// Pop the next received AP item id; returns false if the queue is empty.
bool nextReceivedItem(long long *apItemId);

// Tear down the client.
void shutdown();

} // namespace KyraAP

#endif
