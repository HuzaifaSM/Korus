import json
import random
from copy import deepcopy
from os.path import exists
from ..styles import highlightKeywords
from typing import Dict, Optional

class EnemyAffix:
    def __init__(self, kind: str, name: str, category: str, weight: int, levelReq: int, 
                 effects: dict, lootBonus: dict, tags: list[str], excludes: list[str] = None):
        self.kind = kind
        self.name = name
        self.category = category
        self.weight = weight
        self.levelReq = levelReq
        self.effects = effects
        self.lootBonus = lootBonus
        self.tags = tags
        self.excludes = excludes or []

    def __rich__(self):
        return self.__str__()

    def __str__(self):
        statStr = "[bold]Stat Changes:[/bold]"
        for stat, val in self.effects.items():
            label = stat.replace('_', ' ').title()
            if isinstance(val, str):
                statStr += f"\n- {self.name}: {label} ({val})"
            else:
                perc = 'increased' in stat or isinstance(val, float)
                statStr += f"\n- {self.name}: {'+' if val > 0 else '-'}{val}{'%' if perc else ''} {label}"
        lootStr = "[bold]Loot Bonuses:[/bold]"
        for loot, val in self.lootBonus.items():
            if loot == 'rarity':
                loot = 'Item Rarity'
            elif loot == 'quantity':
                loot = 'Item Quantity'
            elif loot == 'xp':
                loot = 'XP'
            elif loot == 'gold':
                loot = 'Gold'
            lootStr += f"\n- {'+' if val > 0 else ''}{val} {loot}"
        return highlightKeywords(f"{statStr}\n{lootStr}")

def _createAffixList() -> Dict[str, Dict[str, EnemyAffix]]:
    fp = 'Korus/scripts/enemies/enemyAffixes.json' if exists('Korus') else 'scripts/enemies/enemyAffixes.json'
    with open(fp, 'r') as f:
        affixData = json.load(f)

    affixPool = {
        'prefixes': {},
        'suffixes': {}
    }

    for affixType in ['prefixes', 'suffixes']:
        for affixName, affixInfo in affixData[affixType].items():
            ea = EnemyAffix(
                affixType, affixInfo['name'], affixInfo['category'], affixInfo['weight'], affixInfo['level_req'],
                affixInfo['effects'], affixInfo['loot_bonus'], affixInfo['tags'], affixInfo['excludes']
            )
            affixPool[affixType][affixName] = ea

    return affixPool

def rollAffix(affixType: str, enemyLevel: int, enemyRarity, excludeNames: set[str], noEmpty: bool = False) -> Optional[EnemyAffix]:
    from .enemy import EnemyRarity
    baseEmptyChance = {
        EnemyRarity.COMMON: 0.3,
        EnemyRarity.RARE: 0.2,
        EnemyRarity.EPIC: 0.1,
        EnemyRarity.LEGENDARY: 0.01
    }.get(enemyRarity)

    if noEmpty:
        baseEmptyChance = 0.0

    if random.random() < baseEmptyChance:
        return None

    excludeNames = excludeNames or set()

    if affixType == 'prefix':
        affixType = 'prefixes'
    elif affixType == 'suffix':
        affixType = 'suffixes'

    availableAffixes = ENEMY_AFFIX_POOL[affixType]
    validAffixes: list[EnemyAffix] = []
    weights = []

    for affixName, affix in availableAffixes.items():
        if enemyLevel >= affix.levelReq and affix.name not in excludeNames and affixName not in excludeNames:
            validAffixes.append(affix)
            weights.append(affix.weight)

    if not validAffixes:
        return None

    chosenAffix = random.choices(validAffixes, weights, k=1)[0]

    rolledAffix = EnemyAffix(
        chosenAffix.kind, chosenAffix.name, chosenAffix.category, chosenAffix.weight, chosenAffix.levelReq,
        chosenAffix.effects , chosenAffix.lootBonus, chosenAffix.tags, chosenAffix.excludes
    )
    return rolledAffix

ENEMY_AFFIX_POOL = _createAffixList()