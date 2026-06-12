// Archipelago client bridge implementation. Quarantines apclientpp + asio +
// websocketpp behind the plain interface in ap_bridge.h. Compiled standalone
// (C++17 / exceptions on) into ap_bridge.lib; see build/build_ap_bridge.bat.

#define ASIO_STANDALONE
#define AP_NO_SCHEMA
#define WSWRAP_NO_SSL
#define WSWRAP_NO_COMPRESSION
#define _WIN32_WINNT 0x0601
#define WIN32_LEAN_AND_MEAN

#include <apclient.hpp>
#include <apuuid.hpp>

#include "ap_bridge.h"

#include <deque>
#include <memory>
#include <string>

namespace {

std::unique_ptr<APClient> g_ap;
std::string g_status = "AP: idle";
std::string g_slot;
std::string g_password;
const std::string g_game = "The Legend of Kyrandia - Book 1";
bool g_connected = false;
std::deque<long long> g_items;
int g_nextItemIndex = 0;   // dedup: AP resends all items (index 0..) on reconnect

} // namespace

namespace KyraAP {

void init(const char *uri, const char *slot, const char *password) {
    g_slot = slot ? slot : "";
    g_password = password ? password : "";
    g_connected = false;
    g_items.clear();
    g_nextItemIndex = 0;

    const std::string u = (uri && *uri) ? uri : "ws://localhost:38281";
    std::string uuid = ap_get_uuid("");

    g_ap.reset(new APClient(uuid, g_game, u));
    g_status = "AP: connecting to " + u + " ...";

    g_ap->set_room_info_handler([]() {
        g_status = "AP: authenticating as " + g_slot + " ...";
        // items_handling 7 = remote + own + starting items.
        g_ap->ConnectSlot(g_slot, g_password, 0x7);
    });
    g_ap->set_slot_connected_handler([](const nlohmann::json &) {
        g_connected = true;
        g_status = "AP: connected as " + g_slot;
    });
    g_ap->set_slot_refused_handler([](const std::list<std::string> &errors) {
        g_connected = false;
        std::string msg = "AP: refused:";
        for (const auto &e : errors)
            msg += " " + e;
        g_status = msg;
    });
    g_ap->set_socket_disconnected_handler([]() {
        g_connected = false;
        g_status = "AP: disconnected (retrying)";
    });
    g_ap->set_socket_error_handler([](const std::string &err) {
        g_status = "AP: socket error: " + err;
    });
    g_ap->set_items_received_handler([](const std::list<APClient::NetworkItem> &items) {
        // AP resends the full item list (index 0..) on every (re)connect; only
        // enqueue items we haven't already granted, tracked by absolute index.
        for (const auto &it : items) {
            if (it.index >= g_nextItemIndex) {
                g_items.push_back((long long)it.item);
                g_nextItemIndex = it.index + 1;
            }
        }
    });
}

void poll() {
    if (g_ap)
        g_ap->poll();
}

bool isConnected() {
    return g_connected;
}

const char *statusText() {
    return g_status.c_str();
}

void sendCheck(long long locationId) {
    if (g_ap && g_connected) {
        std::list<int64_t> locs;
        locs.push_back((int64_t)locationId);
        g_ap->LocationChecks(locs);
    }
}

bool nextReceivedItem(long long *apItemId) {
    if (g_items.empty())
        return false;
    if (apItemId)
        *apItemId = g_items.front();
    g_items.pop_front();
    return true;
}

void shutdown() {
    g_ap.reset();
    g_connected = false;
    g_status = "AP: idle";
}

} // namespace KyraAP
