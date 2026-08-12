import random
from typing import List, Tuple, Optional

from crafting.chaosRune import CHAOS_RUNES
from crafting.erasingRune import ERASING_RUNES
from crafting.growthRune import GROWTH_RUNES
from crafting.randomiserRunes import RANDOMISER_RUNES
from crafting.uniqueRunes import UNIQUE_RUNES
from crafting.masteryRune import MASTERY_RUNES
from crafting.rarityRune import RARITY_RUNES
from crafting.destabilisationRune import DESTABILISATION_RUNES
from crafting.revealingRune import REVEALING_RUNES
from crafting.manipulationRune import MANIPULATION_RUNES
from crafting.base import CraftingItem

ALL_RUNES = {
    'chaos': CHAOS_RUNES,
    'erasing': ERASING_RUNES,
    'growth': GROWTH_RUNES,
    'randomiser': RANDOMISER_RUNES,
    'unique': UNIQUE_RUNES,
    'mastery': MASTERY_RUNES,
    'rarity': RARITY_RUNES,
    'destabilisation': DESTABILISATION_RUNES,
    'revealing': REVEALING_RUNES,
    'manipulation': MANIPULATION_RUNES,
}

def calculateRuneWeight(runeMinLevel: int, enemyLevel: int, baseWeight: float = 100.0) -> float:
    levelDiff = enemyLevel - runeMinLevel if runeMinLevel is not None else enemyLevel

    if levelDiff < 0: # too high level
        return 0
    
    if enemyLevel > 90 and levelDiff <= 30: #high level + tier runes
        return baseWeight * 1.2
    
    if levelDiff <= 15:
        return baseWeight * 1.5
    
    elif levelDiff <= 30:
        return baseWeight
    
    elif levelDiff <= 45:
        return baseWeight * 0.5
    
    elif levelDiff <= 60:
        return baseWeight * 0.2
    
    else: # very low level (>60 levels below current level)
        return baseWeight * 0.05

def getDropChanceForLevel(level: int) -> Tuple[float, float]:
    if level <= 20:
        return (0.12, 0.02)
    elif level <= 40:
        return (0.18, 0.05)
    elif level <= 60:
        return (0.25, 0.10)
    elif level <= 80:
        return (0.35, 0.15)
    elif level <= 100:
        return (0.45, 0.25)
    else:
        return (0.55, 0.35)
    
def rollRuneDrops(level: int, isBoss: bool = False) -> List[Tuple[str, str]]:
    baseChance, multiChance = getDropChanceForLevel(level)

    if isBoss:
        baseChance = min(0.95, baseChance * 2.0)
        multiChance = min(0.75, multiChance * 2.5)

    drops = []

    if random.random() < baseChance:
        rune = _rollSingleRune(level)
        if rune:
            drops.append(rune)

        maxDrops = 3 if not isBoss else 5
        while random.random() < multiChance and len(drops) < maxDrops:
            rune = _rollSingleRune(level)
            if rune:
                drops.append(rune)

    return drops

def _rollSingleRune(level: int) -> Tuple[str, str]:
    validRunes = []
    weights = []

    for category, runeDict in ALL_RUNES.items():
        for runeType, rune in runeDict.items():
            runeMinLevel = getattr(rune, 'minItemLevel', 1)

            weight = calculateRuneWeight(runeMinLevel, level, baseWeight=rune.dropWeight)

            if weight > 0:
                validRunes.append((category, runeType))
                weights.append(weight)

    if not validRunes:
        return None
    
    chosen = random.choices(validRunes, weights=weights, k=1)[0]
    return chosen

def getRuneObject(category: str, runeType: str) -> Optional[CraftingItem]:
    if category in ALL_RUNES and runeType in ALL_RUNES[category]:
        return ALL_RUNES[category][runeType]
    return None

def getRuneString(rune: CraftingItem) -> str:
    """returns exact rune string: f'{category}_{runeType}'"""
    for category in ALL_RUNES:
        for runeType in ALL_RUNES[category]:
            if ALL_RUNES[category][runeType] == rune:
                return f'{category}_{runeType}'
    return None

...