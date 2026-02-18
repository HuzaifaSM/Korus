from .base import Player
from .warrior import Warrior, WARRIOR_DESCRIPTIONS
from .rogue import Rogue, ROGUE_DESCRIPTIONS
from .mage import Mage, MAGE_DESCRIPTIONS
from .fighter import Fighter, FIGHTER_DESCRIPTIONS
from .ranger import Ranger, RANGER_DESCRIPTIONS
from .druid import Druid, DRUID_DESCRIPTIONS
from .paladin import Paladin, PALADIN_DESCRIPTIONS
from .monk import Monk, MONK_DESCRIPTIONS
from .cultist import Cultist, CULTIST_DESCRIPTIONS
from .wanderer import Wanderer, WANDERER_DESCRIPTIONS
from .spectre import Spectre, SPECTRE_DESCRIPTIONS

from typing import Dict

CLASSES: Dict[str, Player] = {
    "Warrior": Warrior,
    "Rogue": Rogue,
    "Mage": Mage,
    "Fighter": Fighter,
    "Ranger": Ranger,
    "Druid": Druid,
    "Paladin": Paladin,
    "Monk": Monk,
    "Cultist": Cultist,
    "Wanderer": Wanderer,
    "Spectre": Spectre,
}

ASCENDANCIES = {
    "Warrior": {
        'Warlord', 'Pyromancer', 'Juggernaut', 'Blood Reaver', 'Flamewarden', 'Annihilist'
    },
    "Rogue": {
        'Assassin', 'Shadow', 'Trickster', 'Nightblade', 'Voidwalker'
    },
    "Mage" : {
        'Elementalist', 'Arcanist', 'Battlemage', 'Stormbringer', 'Cryomancer', 'Calamity', 'Archon',
    },
    "Fighter": {
        'Bladedancer', 'Champion', 'Barbarian', 'Brawler', 'Marshal'
    },
    "Ranger": {
        'Sniper', 'Windwalker', 'Hunter', 'Skirmisher', 'Tempest', 'Pathfinder'
    },
    "Druid": {
        'Primalist', 'Arbiter', 'Moonkin', 'Chimera', 'Earthshaper'
    },
    "Paladin": {
        'Templar', 'Guardian', 'Inquisitor', 'Justicar', 'Crusader'
    },
    "Monk": {
        'Enlightened', 'Stormwalker', 'Glacierfist', 'Ascetic', 'Psychopath', 'Avatar'
    },
    'Cultist': {
        'Umbralist', 'Harbinger', 'Doomsayer', 'Ritualist', 'Hellseer'
    },
    'Wanderer': {
        'Fractured', 'Manifestation', 'Weaver', 'Abyssal', 'Warper', 'Mindbreaker'
    },
    'Spectre': {
        'Wraith', 'Reaper', 'Phantasm', 'Revenant', 'Lich'
    }
}

SUB_TYPES = {
    'Warrior': {
        'Savage', 'Colossus', 'Titan'
    },
    'Rogue': {
        'Duelist', 'Vanguard', 'Shade'
    },
    'Mage': {
        'Sage', 'Warlock', 'Chronicler'
    },
    'Fighter': {
        'Bruiser', 'Samurai', 'Veteran'
    },
    'Ranger':{
        'Sharpshooter', 'Scout', 'Warden'
    },
    'Druid': {
        'Feral', 'Wildling', 'Ironbark'
    },
    'Paladin': {
        'Fanatic', 'Cleric', 'Templar'
    },
    'Monk': {
        'Pugilist', 'Manafist', 'Dualist'
    },
    'Cultist': {
        'Acolyte', 'Conduit', 'Preacher'
    },
    'Wanderer': {
        'Drifter', 'Vessel', 'Shattered'
    },
    'Spectre': {
        'Haunt', 'Incorporeal', 'Cursed'
    }
}

DESCRIPTIONS = {
    "Cultist": CULTIST_DESCRIPTIONS,

    "Druid": DRUID_DESCRIPTIONS,

    "Fighter": FIGHTER_DESCRIPTIONS,

    "Monk": MONK_DESCRIPTIONS,

    "Mage": MAGE_DESCRIPTIONS,

    "Paladin": PALADIN_DESCRIPTIONS,

    "Ranger": RANGER_DESCRIPTIONS,

    "Rogue": ROGUE_DESCRIPTIONS,

    "Spectre": SPECTRE_DESCRIPTIONS,

    "Wanderer": WANDERER_DESCRIPTIONS,

    "Warrior": WARRIOR_DESCRIPTIONS,
}
