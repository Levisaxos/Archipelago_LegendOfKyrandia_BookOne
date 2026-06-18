from __future__ import annotations

from dataclasses import dataclass

from Options import Choice, DeathLink, PerGameCommonOptions, Toggle


class Goal(Choice):
    """What counts as completing The Legend of Kyrandia - Book 1.

    defeat_malcolm: Recover the royal regalia (Crown, Sceptre, Royal Chalice),
                    obtain the Mirror and the Red amulet power, then confront
                    Malcolm and turn him to stone. (Only goal in V1.)
    """
    display_name = "Goal"
    option_defeat_malcolm = 0
    default = 0


class StartWithAmulet(Toggle):
    """Start the run already holding the Amulet.

    The Amulet gates every spell, so receiving it early makes generation looser.
    For V1 testing this is a convenient way to broaden the logic. Off by default
    (the Amulet is shuffled into the multiworld like any other progression item).
    """
    display_name = "Start With Amulet"
    default = 0


class BirthstoneHints(Choice):
    """How much help NPCs give for the 4-gem birthstone altar.

    The altar's required gems (and their slots) are randomized per seed. NPCs who
    know about birthstones (e.g. Darm) can reveal them so the puzzle isn't blind.

    none:           no help; discover the gems by trial (vanilla-like blind).
    gems:           NPCs name WHICH four birthstones the altar needs.
    gems_and_slots: NPCs name the gems AND which slot (1-4) each goes in.
    """
    display_name = "Birthstone Hints"
    option_none = 0
    option_gems = 1
    option_gems_and_slots = 2
    default = 1


@dataclass
class KyrandiaOptions(PerGameCommonOptions):
    goal: Goal
    start_with_amulet: StartWithAmulet
    birthstone_hints: BirthstoneHints
    death_link: DeathLink


# Option keys carried in slot_data / restored on UT re-gen. Every option that
# influences regions, rules or the item pool must be listed here. (birthstone_hints
# is cosmetic — it changes NPC text, not reachability — so it is not listed.)
LOGIC_OPTION_KEYS = ("goal", "start_with_amulet")
