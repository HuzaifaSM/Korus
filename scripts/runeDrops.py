import random
from typing import List, Tuple, Optional

from scripts.crafting.chaosRune import CHAOS_RUNES
from scripts.crafting.erasingRune import ERASING_RUNES
from scripts.crafting.growthRune import GROWTH_RUNES
from scripts.crafting.randomiserRunes import RANDOMISER_RUNES
from scripts.crafting.uniqueRunes import UNIQUE_RUNES
from scripts.crafting.masteryRune import MASTERY_RUNES
from scripts.crafting.rarityRune import RARITY_RUNES
from scripts.crafting.destabilisationRune import DESTABILISATION_RUNES
from scripts.crafting.revealingRune import REVEALING_RUNES
from scripts.crafting.manipulationRune import MANIPULATION_RUNES
from scripts.crafting.base import CraftingItem

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

    if enemyLevel > 90 and levelDiff <= 30:
        return baseWeight * 1.2

    if levelDiff <= 15:
        return baseWeight * 1.5

    elif levelDiff <= 30:
        return baseWeight

    elif levelDiff <= 45:
        return baseWeight * 0.7

    elif levelDiff <= 60:
        return baseWeight * 0.25

    else:
        return baseWeight * 0.1

def getDropChanceForLevel(level: int) -> Tuple[float, float]:
    if level <= 20:
        return (0.15, 0.03)
    elif level <= 40:
        return (0.225, 0.06)
    elif level <= 60:
        return (0.35, 0.10)
    elif level <= 80:
        return (0.45, 0.15)
    elif level <= 100:
        return (0.65, 0.25)
    else:
        return (0.8, 0.35)

def rollRuneDrops(level: int, quantityModifier: float = 1.0) -> List[Tuple[str, str]]:
    baseChance, multiChance = getDropChanceForLevel(level)
    baseChance = min(0.95, baseChance * quantityModifier)
    multiChance = min(0.9, multiChance * quantityModifier)

    drops = []

    if random.random() < baseChance:
        rune = _rollSingleRune(level)
        if rune:
            drops.append(rune)

        maxDrops = max(1, round((3 + (level // 12)) * quantityModifier))
        while random.random() < multiChance and len(drops) < maxDrops:
            rune = _rollSingleRune(level)
            if rune:
                drops.append(rune)

    return drops

def rollGuaranteedRunes(level: int, count: int, minLevel: int = 0, market: bool = False) -> List[Tuple[str, str]]:
    """returns [(category, runeType)]. if market = True, uniques cannot be rolled"""
    drops = []
    for _ in range(count):
        rune = _rollSingleRune(level, minLevel, market)
        if rune:
            drops.append(rune)
    return drops

def _rollSingleRune(level: int, minLevel: int = 0, market: bool = False) -> Tuple[str, str]:
    """returns (category, runeType)"""
    validRunes = []
    weights = []

    for category, runeDict in ALL_RUNES.items():
        if market and category == 'unique':
            continue
        for runeType, rune in runeDict.items():
            runeMinLevel = getattr(rune, 'minItemLevel', 1)

            if minLevel:
                if runeMinLevel < minLevel:
                    continue

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

def getRuneDetails(rune: CraftingItem) -> tuple[str, str]:
    """returns (runeCategory, runeType)"""
    for category in ALL_RUNES:
        for runeType in ALL_RUNES[category]:
            if ALL_RUNES[category][runeType] == rune:
                return (category, runeType)
    return None

...