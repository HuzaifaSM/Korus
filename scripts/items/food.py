import json
import random
from os.path import exists
from typing import Optional, Dict, Any

def _foodAffixDataPath() -> str:
    return 'Korus/scripts/campAreas/data/foodAffixes.json' if exists('Korus') else 'scripts/campAreas/data/foodAffixes.json'

def _loadFoodAffixData() -> dict:
    with open(_foodAffixDataPath(), 'r', encoding='utf-8') as f:
        return json.load(f)

FOOD_AFFIX_DATA = _loadFoodAffixData()

RESISTANCE_DAMAGE_TYPES = [
    'physical', 'fire', 'cold', 'lightning', 'earth', 'holy', 'dark', 'arcane', 'chaos', 'ethereal', 'psychic'
]

BASE_HEAL_PER_SUPPLY = 0.5  # 2 supplies = 1% Max HP
MAX_SUPPLIES_FOR_BASE_HEAL = 40  # caps the base heal at 20% Max HP - the "+% Max HP Healed" suffix can push past this

def _rollFoodAffix(kind: str, campfireLevel: int) -> Optional[Dict[str, Any]]:
    """kind = 'prefixes' or 'suffixes'. Picks uniformly among stats/tiers unlocked at campfireLevel."""
    pool = FOOD_AFFIX_DATA.get(kind, {})
    candidates = []
    for statKey, info in pool.items():
        eligibleTiers = [
            (int(tierNum), tierData) for tierNum, tierData in info['tiers'].items()
            if tierData['campfireLevel'] <= campfireLevel
        ]
        if eligibleTiers:
            candidates.append((info, eligibleTiers))

    if not candidates:
        return None

    info, eligibleTiers = random.choice(candidates)
    tierNum, tierData = random.choice(eligibleTiers)
    value = random.randint(tierData['min'], tierData['max'])

    resolvedStat = info['stat']
    displayName = info['name']
    if info.get('randomDamageType'):
        damageType = random.choice(RESISTANCE_DAMAGE_TYPES)
        resolvedStat = damageType  # matches the bare-damage-type key convention _getExtraBonuses(damageType) reads
        displayName = f"{info['name']} ({damageType.title()})"

    return {
        'name': displayName,
        'stat': resolvedStat,
        'value': value,
        'tier': tierNum,
    }

def _displayStatName(stat: str) -> str:
    if stat in RESISTANCE_DAMAGE_TYPES:
        return f"{stat.title()} Resistance"
    return stat.replace('_', ' ').title()

class FoodItem:
    def __init__(self, name: str, baseHealPercent: float, prefix: Optional[dict], suffix: Optional[dict]):
        self.name = name
        self.baseHealPercent = baseHealPercent
        self.prefix = prefix
        self.suffix = suffix

    @property
    def buffDuration(self) -> int:
        duration = 2
        if self.prefix and self.prefix['stat'] == 'buff_duration':
            duration += self.prefix['value']
        return duration

    @property
    def totalHealPercent(self) -> float:
        bonus = self.suffix['value'] if self.suffix and self.suffix['stat'] == 'extra_heal_percent' else 0
        return self.baseHealPercent + bonus

    @property
    def combatPrefix(self) -> Optional[dict]:
        """The prefix, only if it's an actual per-turn combat buff (not the duration-extension utility one)."""
        return self.prefix if self.prefix and self.prefix['stat'] != 'buff_duration' else None

    @property
    def combatSuffix(self) -> Optional[dict]:
        """The suffix, only if it's an actual per-turn combat buff (not the immediate heal-bonus one)."""
        return self.suffix if self.suffix and self.suffix['stat'] != 'extra_heal_percent' else None

    def describe(self) -> str:
        parts = [f"Recovers {self.totalHealPercent:.0f}% Max HP"]
        if self.prefix:
            if self.prefix['stat'] == 'buff_duration':
                parts.append(f"{self.prefix['name']} (+{self.prefix['value']} Buff Duration)")
            else:
                parts.append(f"{self.prefix['name']} (+{self.prefix['value']} {_displayStatName(self.prefix['stat'])})")
        if self.suffix and self.suffix['stat'] != 'extra_heal_percent':
            parts.append(f"{self.suffix['name']} (+{self.suffix['value']} {_displayStatName(self.suffix['stat'])})")
        return f"{self.name} - " + ", ".join(parts) + f" [buffs last {self.buffDuration} turns]"

    def serialise(self) -> dict:
        return {'name': self.name, 'baseHealPercent': self.baseHealPercent, 'prefix': self.prefix, 'suffix': self.suffix}

    @classmethod
    def deserialise(cls, data: dict) -> 'FoodItem':
        return cls(data['name'], data['baseHealPercent'], data.get('prefix'), data.get('suffix'))

def cookFood(suppliesSpent: int, campfireLevel: int) -> FoodItem:
    suppliesSpent = max(0, min(suppliesSpent, MAX_SUPPLIES_FOR_BASE_HEAL))
    baseHealPercent = suppliesSpent * BASE_HEAL_PER_SUPPLY
    prefix = _rollFoodAffix('prefixes', campfireLevel)
    suffix = _rollFoodAffix('suffixes', campfireLevel)
    return FoodItem("Cooked Meal", baseHealPercent, prefix, suffix)
