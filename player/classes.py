from .base import Player
from .warrior import Warrior, WARRIOR_DESCRIPTIONS
from .mage import Mage, MAGE_DESCRIPTIONS
from .fighter import Fighter, FIGHTER_DESCRIPTIONS
from .druid import Druid, DRUID_DESCRIPTIONS
from .paladin import Paladin, PALADIN_DESCRIPTIONS
from .monk import Monk, MONK_DESCRIPTIONS
from .cultist import Cultist, CULTIST_DESCRIPTIONS
from .wanderer import Wanderer, WANDERER_DESCRIPTIONS
from .spectre import Spectre, SPECTRE_DESCRIPTIONS
from .wretch import Wretch, WRETCH_DESCRIPTIONS

from typing import Dict

CLASSES: Dict[str, Player] = {
    "Warrior": Warrior,
    "Mage": Mage,
    "Fighter": Fighter,
    "Druid": Druid,
    "Paladin": Paladin,
    "Monk": Monk,
    "Cultist": Cultist,
    "Wanderer": Wanderer,
    "Spectre": Spectre,
    "Wretch": Wretch,
}

ASCENDANCIES = {
    "Warrior": {
        'Warlord', 'Pyromancer', 'Juggernaut', 'Blood Reaver', 'Flamewarden', 'Annihilist'
    },
    "Mage" : {
        'Elementalist', 'Arcanist', 'Battlemage', 'Stormbringer', 'Cryomancer', 'Calamity', 'Archon',
    },
    "Fighter": {
        'Bladedancer', 'Champion', 'Barbarian', 'Brawler', 'Marshal'
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
    },
    "Wretch": {
        'Exsanguinator', 'Bloodletter', 'Plaguebearer', 'Necrose', 'Necromancer'
    }
}

DESCRIPTIONS = {
    "Cultist": CULTIST_DESCRIPTIONS,

    "Druid": DRUID_DESCRIPTIONS,

    "Fighter": FIGHTER_DESCRIPTIONS,

    "Monk": MONK_DESCRIPTIONS,

    "Mage": MAGE_DESCRIPTIONS,

    "Paladin": PALADIN_DESCRIPTIONS,

    "Spectre": SPECTRE_DESCRIPTIONS,

    "Wanderer": WANDERER_DESCRIPTIONS,

    "Warrior": WARRIOR_DESCRIPTIONS,

    "Wretch": WRETCH_DESCRIPTIONS,
}
