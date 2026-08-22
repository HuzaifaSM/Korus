from .base import Player
from .warrior import Warrior, WARRIOR_DESCRIPTIONS
from .mage import Mage, MAGE_DESCRIPTIONS
from .fighter import Fighter, FIGHTER_DESCRIPTIONS
from .druid import Druid, DRUID_DESCRIPTIONS
from .paladin import Paladin, PALADIN_DESCRIPTIONS
from .cultist import Cultist, CULTIST_DESCRIPTIONS
from .wanderer import Wanderer, WANDERER_DESCRIPTIONS
from .spectre import Spectre, SPECTRE_DESCRIPTIONS
from .wretch import Wretch, WRETCH_DESCRIPTIONS
from .marauder import Marauder, MARAUDER_DESCRIPTIONS
from .tempest import Tempest, TEMPEST_DESCRIPTIONS

from typing import Dict

CLASSES: Dict[str, Player] = {
    "Cultist": Cultist,
    #"Druid": Druid,
    #"Fighter": Fighter,
    "Mage": Mage,
    "Marauder": Marauder,
    "Paladin": Paladin,
    "Spectre": Spectre,
    "Tempest": Tempest,
    "Wanderer": Wanderer,
    "Warrior": Warrior,
    "Wretch": Wretch,
}

DESCRIPTIONS = {
    "Cultist": CULTIST_DESCRIPTIONS,

    "Druid": DRUID_DESCRIPTIONS,

    "Fighter": FIGHTER_DESCRIPTIONS,

    "Mage": MAGE_DESCRIPTIONS,

    "Marauder": MARAUDER_DESCRIPTIONS,

    "Paladin": PALADIN_DESCRIPTIONS,

    "Spectre": SPECTRE_DESCRIPTIONS,

    "Tempest": TEMPEST_DESCRIPTIONS,

    "Wanderer": WANDERER_DESCRIPTIONS,

    "Warrior": WARRIOR_DESCRIPTIONS,

    "Wretch": WRETCH_DESCRIPTIONS,
}

ASCENDANCIES: dict[str, list[str]] = {}
for className, descriptions in DESCRIPTIONS.items():
    ASCENDANCIES[className] = []
    for asc in descriptions.keys():
        if asc != className:
            ASCENDANCIES[className].append(asc)
