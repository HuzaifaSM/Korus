import json
import random
from os.path import exists
from typing import Dict, List

class DungeonModifier:
    def __init__(self, name: str, modType: str, effect: str, value, description: str, weight: int = 1):
        self.name = name
        self.modType = modType  # 'positive' or 'negative'
        self.effect = effect
        self.value = value
        self.description = description
        self.weight = weight

    def __repr__(self):
        return f"<{self.name} ({self.modType})>"

def _loadModifierData() -> Dict:
    fp = 'Korus/scripts/dungeons/data/modifiers.json' if exists('Korus') else 'scripts/dungeons/data/modifiers.json'
    with open(fp, 'r') as f:
        return json.load(f)

def _buildPools(modType: str, data: Dict) -> Dict[str, List[DungeonModifier]]:
    return {
        tierName: [
            DungeonModifier(e['name'], modType, e['effect'], e['value'], e['description'], e.get('weight', 1))
            for e in entries
        ]
        for tierName, entries in data[modType].items()
    }

_MODIFIER_DATA = _loadModifierData()
POSITIVE_POOLS = _buildPools('positive', _MODIFIER_DATA)
NEGATIVE_POOLS = _buildPools('negative', _MODIFIER_DATA)

# dungeon tier -> {pool name: weight} - shifts toward rarer, stronger pools as tier rises
TIER_POOL_WEIGHTS = {
    1: {'common': 85, 'rare': 14, 'legendary': 1},
    2: {'common': 70, 'rare': 27, 'legendary': 3},
    3: {'common': 55, 'rare': 35, 'legendary': 10},
    4: {'common': 40, 'rare': 40, 'legendary': 20},
    5: {'common': 25, 'rare': 45, 'legendary': 30},
}

def _rollPoolName(tier: int) -> str:
    weights = TIER_POOL_WEIGHTS[min(5, max(1, tier))]
    return random.choices(list(weights.keys()), weights=list(weights.values()), k=1)[0]

def _rollModifier(pools: Dict[str, List[DungeonModifier]], tier: int, exclude: set) -> DungeonModifier:
    poolName = _rollPoolName(tier)
    candidates = [m for m in pools[poolName] if m.name not in exclude]
    if not candidates:
        candidates = pools[poolName]
    weights = [m.weight for m in candidates]
    return random.choices(candidates, weights=weights, k=1)[0]

def rollDungeonModifiers(tier: int) -> List[DungeonModifier]:
    numPositive = random.randint(1, min(3, 1 + tier // 2))
    numNegative = random.randint(1, min(3, 1 + tier // 2))

    modifiers: List[DungeonModifier] = []
    chosenNames = set()

    for _ in range(numPositive):
        mod = _rollModifier(POSITIVE_POOLS, tier, chosenNames)
        modifiers.append(mod)
        chosenNames.add(mod.name)

    for _ in range(numNegative):
        mod = _rollModifier(NEGATIVE_POOLS, tier, chosenNames)
        modifiers.append(mod)
        chosenNames.add(mod.name)

    return modifiers

def aggregateEffects(modifiers: List[DungeonModifier]) -> Dict:
    """Flattens a modifier list into {effect_name: total_value}. 'item_quantity_and_rarity' fans out
    into both underlying effects; 'guaranteed_drop' entries collect into a 'guaranteed_drops' list
    since they aren't a simple additive number."""
    totals: Dict = {}
    guaranteedDrops = []

    for mod in modifiers:
        if mod.effect == 'item_quantity_and_rarity':
            totals['item_quantity'] = totals.get('item_quantity', 0) + mod.value
            totals['item_rarity'] = totals.get('item_rarity', 0) + mod.value
        elif mod.effect == 'guaranteed_drop':
            guaranteedDrops.append(mod.value)
        else:
            totals[mod.effect] = totals.get(mod.effect, 0) + mod.value

    if guaranteedDrops:
        totals['guaranteed_drops'] = guaranteedDrops

    return totals

def applyEnemyModifiers(enemy, effects: Dict, currentFloor: int = 0):
    """Mutates a freshly-created enemy's base stats to reflect the dungeon's active negative modifiers.
    Mirrors the mutate-then-recalculate pattern the old (pre-rework) dungeon modifiers used."""
    allStats = effects.get('enemy_all_stats', 0)
    floorStack = effects.get('floor_enemy_stack', 0) * currentFloor

    damageMult = 1 + (effects.get('enemy_damage', 0) + allStats + floorStack) / 100
    healthMult = 1 + (effects.get('enemy_health', 0) + allStats + floorStack) / 100
    speedMult = 1 + (effects.get('enemy_speed', 0) + allStats + floorStack) / 100

    if damageMult != 1:
        enemy._baseDamage = int(enemy._baseDamage * damageMult)
    if healthMult != 1:
        enemy._baseHealth = int(enemy._baseHealth * healthMult)
    if speedMult != 1:
        enemy._baseSpeed *= speedMult

    if damageMult != 1 or healthMult != 1 or speedMult != 1:
        enemy._recalculateStats(False)
