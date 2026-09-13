import random
from typing import Dict, List, Tuple

CRAFTING_SETS: Dict[str, dict] = {
    'cultivators': {
        'displayName': "Cultivator's",
        'description': "Growth + Revealing heavy - safe, low-risk, ends with a full item.",
        'runes': [
            ('growth', 'greater', 8),
            ('growth', 'abundant', 6),
            ('growth', 'greater_prefix', 6),
            ('growth', 'greater_suffix', 6),
            ('growth', 'majestic', 3),
            ('growth', 'divine', 1),
            ('revealing', 'greater', 4),
            ('revealing', 'abundant', 4),
            ('revealing', 'perfect', 2),
        ],
    },
    'chaosweavers': {
        'displayName': "Chaosweaver's",
        'description': "Chaos + Fusion heavy - remix-heavy, iterate toward a specific combo.",
        'runes': [
            ('chaos', 'greater', 8),
            ('chaos', 'perfect', 4),
            ('chaos', 'spreading', 5),
            ('chaos', 'unstable', 4),
            ('chaos', 'devouring', 4),
            ('manipulation', 'greater_fusion', 4),
            ('manipulation', 'heavy_fusion', 3),
            ('manipulation', 'perfect_fusion', 2),
        ],
    },
    'artisans': {
        'displayName': "Artisan's",
        'description': "Manipulation (equilibrium/sacrifice) + a little Growth - precise, sequence-dependent.",
        'runes': [
            ('manipulation', 'equilibrium', 8),
            ('manipulation', 'greater_equilibrium', 5),
            ('manipulation', 'sacrifice', 5),
            ('manipulation', 'greater_sacrifice', 3),
            ('manipulation', 'perfect_sacrifice', 1),
            ('manipulation', 'prefix', 4),
            ('manipulation', 'suffix', 4),
            ('growth', 'greater_prefix', 3),
            ('growth', 'greater_suffix', 3),
        ],
    },
    'seers': {
        'displayName': "Seer's",
        'description': "Mostly Revealing - maximum control, least RNG.",
        'runes': [
            ('revealing', 'revealing', 8),
            ('revealing', 'abundant', 5),
            ('revealing', 'greater', 4),
            ('revealing', 'divine', 2),
            ('revealing', 'perfect', 2),
            ('revealing', 'focused', 1),
            ('revealing', 'pinpoint', 1),
        ],
    },
    'anomalous': {
        'displayName': "Anomalous",
        'description': "A grab bag of everything - swings for extremes over affix precision.",
        'runes': [
            ('growth', 'greater', 3),
            ('growth', 'majestic', 2),
            ('chaos', 'greater', 3),
            ('erasing', 'greater', 3),
            ('revealing', 'greater', 5),
            ('manipulation', 'greater_fusion', 2),
            ('manipulation', 'greater_equilibrium', 2),
            ('manipulation', 'greater_sacrifice', 2),
            ('randomiser', 'greater_value', 2),
            ('randomiser', 'greater_tier', 2),
        ],
    },
}

# Present in every hand regardless of table, per-item on top of the table roster.
UNIVERSAL_RUNES: List[Tuple[str, str, int]] = [
    ('mastery', 'wild', 3),
    ('randomiser', 'mastery', 3),
]

# Copies of the guaranteed fill-everything/clear-everything reset pair in every hand.
RESET_PAIR_COPIES = 3

def rollCraftingTable() -> str:
    return random.choice(list(CRAFTING_SETS.keys()))

def buildCuratedHand(tableKey: str, item) -> List[dict]:
    table = CRAFTING_SETS[tableKey]
    hand = [
        {'category': cat, 'runeType': runeType, 'count': count}
        for cat, runeType, count in table['runes']
    ]
    hand.extend(
        {'category': cat, 'runeType': runeType, 'count': count}
        for cat, runeType, count in UNIVERSAL_RUNES
    )

    if item.level >= 80:
        destabType = 'perfect' if random.random() < 0.2 else 'greater'
    else:
        destabType = 'greater'
    hand.append({'category': 'destabilisation', 'runeType': destabType, 'count': 1})

    hand.append({'category': 'growth', 'runeType': 'overflowing', 'count': RESET_PAIR_COPIES})
    hand.append({'category': 'erasing', 'runeType': 'blank', 'count': RESET_PAIR_COPIES})

    return hand
