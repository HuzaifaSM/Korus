import json
from typing import Optional, Dict, Set, Any, List
import random
from .styles import console, printError
from copy import deepcopy
from os.path import exists

class Affix:
    def __init__(self, id: str, name: str, levelReq: int, tier: int, stat: str,
                 minVal: float, maxVal: float,
                 isPercent: bool = False, kind: str = "prefix",
                 weight: int = 100, categories: list[str] | None = None, isMythic: bool = False,
                 isGlobal: bool = False, **kwargs):
        self.id = id
        self.name = name
        self.levelReq = levelReq
        self.tier = tier
        self.stat = stat
        self.minVal = minVal
        self.maxVal = maxVal
        self.baseValue = None
        self.mastery = 0
        self.isPercent = isPercent
        self.kind = kind
        self.weight = weight
        self.categories = categories if categories is not None else []
        self.data = kwargs
        self.locked = False
        self.soulbound = False
        self.isMythic = isMythic
        self.isGlobal = isGlobal

    @property
    def isMaxTier(self) -> bool:
        return self.name.startswith('[orange_red1 bold underline]')

    def rollValue(self):
        """Sets value of an affix between min and max roll range, also returns value"""
        if self.minVal is None or self.maxVal is None:
            printError(f"Cannot roll value for {self.id} {self.name}: min/max not set.")

        if isinstance(self.minVal, float) or isinstance(self.maxVal, float):
            self.baseValue = round(random.uniform(self.minVal, self.maxVal), 2)
        else:
            self.baseValue = random.randint(int(self.minVal), int(self.maxVal))

        return self.baseValue

    @property
    def value(self):
        if self.baseValue is not None:
            mastery = min(0.2, self.mastery / 100) # mastery cannot exceed 20%
            if isinstance(self.baseValue, float):
                return round(self.baseValue * (1 + mastery), 2)
            else:
                return round(self.baseValue * (1 + mastery))
        return None

    @property
    def isFlat(self):
        return self.name.startswith('added') or self.name.startswith('flat') or not self.isPercent

    @property
    def isIncreased(self):
        return self.name.startswith('increased') or self.name.startswith('more') or self.isPercent

    def __rich__(self):
        return self.__str__()

    def __str__(self):
        if self.value is not None:
            prefix = "+" if self.value > 0 else ""
            if self.isPercent:
                suffix = "% Global Increased" if self.isGlobal else "% Increased"
            else:
                suffix = ""
            value = self.value
        else:
            prefix = ""
            suffix = ""
            value = f"Range: {self.minVal} - {self.maxVal}"
        statDisplay = self.stat.replace('_', ' ').title()
        lockedStr = ""
        if self.locked:
            lockedStr = "[steel_blue bold underline]LOCKED[/steel_blue bold underline] "
        soulStr = ""
        if self.soulbound:
            soulStr = "[gold3 bold underline]SOULBOUND[/gold3 bold underline] "
        mythicStr = ""
        if self.isMythic:
           mythicStr = "[indian_red bold underline]MYTHIC[/indian_red bold unerline]"
        return f"{lockedStr}{soulStr}{mythicStr}{prefix}{value}{suffix} {statDisplay} | [dim]Tier {self.tier}[/dim]"

    # def detailed(self): # not used anywhere
    #     string = self.__rich__()
    #     ranges = f"Range: {self.minVal} - {self.maxVal}"
    #     bonusInfo = f"[dim][bold]Roll Range:[/bold] {ranges} | [bold]Tier:[/bold] {self.tier} | [bold]Level Requirement:[/bold] {self.levelReq} | [bold]Tags:[/bold] {self.categories}[/dim]"
    #     string += f"\n{bonusInfo}"
    #     return string

    def _serialise(self):
        return {
            'id': self.id,
            'name': self.name,
            'levelReq': self.levelReq,
            'tier': self.tier,
            'stat': self.stat,
            'minVal': self.minVal,
            'maxVal': self.maxVal,
            'baseValue': self.baseValue,
            'mastery': self.mastery,
            'isPercent': self.isPercent,
            'kind': self.kind,
            'weight': self.weight,
            'categories': self.categories,
            'locked': self.locked,
            'soulbound': self.soulbound,
            'isMythic': self.isMythic,
            'isGlobal': self.isGlobal
        }

    @classmethod
    def deserialise(cls, data: Dict[str, Any]):
        if not data.get('soulbound', False):
            affix = cls(
                id=data.get('id', ''),
                name=data.get('name', ''),
                levelReq=data.get('levelReq', 1),
                tier=data.get('tier', int(data.get('id', '',).split('_t')[-1])),
                stat=data.get('stat', ''),
                minVal=data.get('minVal', 0),
                maxVal=data.get('maxVal', 1),
                isPercent=data.get('isPercent', False),
                kind=data.get('kind', 'prefix'),
                weight=data.get('weight', 100),
                categories=data.get('categories', []),
                isGlobal=data.get('isGlobal', False)
            )
        else: # soulbound
            affix = cls(
                id=data.get('id', ''),
                name=data.get('name', ''),
                levelReq=data.get('levelReq', 1),
                tier=0,
                stat=data.get('stat', ''),
                minVal=data.get('minVal', 0),
                maxVal=data.get('maxVal', 1),
                isPercent=data.get('isPercent', False),
                kind=data.get('kind', 'prefix'),
                weight=0,
                categories=data.get('categories', []),
                isGlobal=data.get('isGlobal', False)
            )
        affix.baseValue = data.get('baseValue')
        affix.mastery = data.get('mastery', 0)
        affix.locked = data.get('locked', False)
        return affix

def _createAffixList() -> Dict[str, Dict[str, Affix]] | Dict[str, Affix]:
    fp = 'Korus/data/affixes.json' if exists('Korus') else 'data/affixes.json'
    with open(fp, 'r') as f:
        affixData = json.load(f)

    affixPool = {
        'weapon': {'prefixes': {}, 'suffixes': {}},
        'head': {'prefixes': {}, 'suffixes': {}},
        'chest': {'prefixes': {}, 'suffixes': {}},
        'legs': {'prefixes': {}, 'suffixes': {}},
        'feet': {'prefixes': {}, 'suffixes': {}},
        'ring': {'prefixes': {}, 'suffixes': {}},
        'amulet': {'prefixes': {}, 'suffixes': {}},
    }
    maxTiers: Dict[tuple[str, str], int] = {}

    for equipType in ['weapon',
                      'head', 'chest', 'legs', 'feet',
                      'ring', 'amulet'
                      ]:
        if equipType not in affixData:
            continue

        for affixType in ['prefixes', 'suffixes']:
            if affixType not in affixData[equipType]:
                continue

            for affixId, affixInfo in affixData[equipType][affixType].items():
                maxTier = int(max(list(affixInfo['tiers'].keys())))
                if maxTier > 6:
                    topEnd = maxTier - 1
                    highEnd = maxTier - 3
                else:
                    topEnd = maxTier - 1
                    highEnd = maxTier - 2
                maxMarkup = 'orange_red1 bold underline'
                topMarkup = 'dark_orange bold'
                highMarkup = 'orange1'
                for tierId, tierData in affixInfo['tiers'].items():
                    uniqueId = f"{affixId}_t{tierId}"

                    tierId = int(tierId)

                    markup = ""
                    if tierId == maxTier:
                        markup = maxMarkup
                    elif tierId >= topEnd:
                        markup = topMarkup
                    elif tierId >= highEnd:
                        markup = highMarkup

                    if markup != "":
                        name = f"[{markup}]{tierData['name']}[/{markup}]"
                    else:
                        name = tierData['name']

                    affix = Affix(
                        id=uniqueId,
                        name=name,
                        levelReq=tierData['levelReq'],
                        tier=tierId,
                        stat=affixInfo['stat'],
                        minVal=tierData['min'],
                        maxVal=tierData['max'],
                        isPercent=affixInfo.get('isPercent', False),
                        kind=affixType[:-2], #prefixes => prefix
                        weight=tierData.get('weight', 100),
                        categories=affixInfo['categories'],
                        isGlobal=affixInfo.get('isGlobal', False),
                    )

                    affixPool[equipType][affixType][uniqueId] = affix
                    maxTiers[(equipType, uniqueId.split('_t')[0])] = maxTier
                    
    return affixPool, maxTiers

def rollAffix(equipType: str, affixType: str, itemLevel: int, rarity: str,
              excludeIds: Set[str] = None, tierBias: float = 0.0,
              defenseType: str = None,
              minAffixLevel: int | None = None, noEmpty: bool = False) -> Optional[Affix]:
    from .items import ItemRarity
    baseEmptyChance = {
        ItemRarity.COMMON: 0.4,
        ItemRarity.UNCOMMON: 0.25,
        ItemRarity.RARE: 0.1,
        ItemRarity. EPIC: 0.05,
        ItemRarity.LEGENDARY: 0.02
    }.get(rarity, 0.1)

    if noEmpty:
        baseEmptyChance = 0.0

    levelFactor = max(0.75, 1 - (itemLevel / 100) * 0.25)
    emptyChance = baseEmptyChance * levelFactor
    if random.random() < emptyChance:
        return None

    excludeIds = excludeIds or set()

    if equipType not in AFFIX_POOL:
        return None

    if affixType == 'prefix':
        affixType = 'prefixes'
    elif affixType == 'suffix':
        affixType = 'suffixes'
    
    availableAffixes = AFFIX_POOL[equipType][affixType]

    minLevelAffix = max(0, min(30, itemLevel - 75)) # min lvl 25 at level 100, min 30 at 105
    if minAffixLevel:
        minLevelAffix = minAffixLevel

    validAffixes = []
    weights = []

    for affixId, affix in availableAffixes.items():
        if minLevelAffix <= affix.levelReq <= itemLevel and affixId not in excludeIds:
            baseId = affix.id.split('_t')[0]
            if baseId not in excludeIds:

                if defenseType:
                    if defenseType == 'energyShield':
                        defenseType = 'energy_shield'
                    defenseTypes = ['armour', 'evasion', 'energy_shield']
                    if affix.stat in defenseTypes:
                        if affix.stat != defenseType:
                            continue

                validAffixes.append(affix)
                
                baseWeight = affix.weight

                if tierBias > 0.0:
                    tierNum = int(affixId.split('_t')[1])
                    maxTier = 1
                    for otherId in availableAffixes.keys():
                        otherTier = int(otherId.split('_t')[1])
                        maxTier = max(maxTier, otherTier)

                    tierRatio = tierNum / maxTier
                    multiplier = 1.0 + (tierBias * tierRatio * 3.0)
                    baseWeight = int(baseWeight * multiplier)

                weights.append(baseWeight)

    if not validAffixes:
        return None
    
    chosenAffix = random.choices(validAffixes, weights=weights, k=1)[0]

    rolledAffix = Affix(
        id=chosenAffix.id,
        name=chosenAffix.name,
        levelReq=chosenAffix.levelReq,
        tier=chosenAffix.tier,
        stat=chosenAffix.stat,
        minVal=chosenAffix.minVal,
        maxVal=chosenAffix.maxVal,
        isPercent=chosenAffix.isPercent,
        kind=chosenAffix.kind,
        weight=chosenAffix.weight,
        categories=list(chosenAffix.categories),
        isGlobal=chosenAffix.isGlobal
    )
    rolledAffix.rollValue()

    return rolledAffix

def getAffixById(affixId: str) -> Optional[Affix]:
    for equipType in AFFIX_POOL.values():
        for affixType in equipType.values():
            if affixId in affixType:
                return affixType[affixId]
            
    return None

def getMaxAffixTier(equipType: str, kind: str, affixId: str) -> Optional[int]:
    affixId = affixId.split('_t')[0]
    if equipType in AFFIX_POOL:
        if kind in AFFIX_POOL[equipType]:
            highest = 0
            for affix in AFFIX_POOL[equipType][kind]:
                if affix.split('_t')[0] == affixId:
                    tier = int(affix.split('_t')[1])
                    if tier > highest:
                        highest = tier
            return highest if highest > 0 else None
    return None

def getTierVariants(item, affix) -> List[Affix]:
    equipType = item.slot
    poolType = 'prefixes' if affix.kind == 'prefix' else 'suffixes'
    affixId = affix.id

    candidates = []

    for otherId, otherAffix in AFFIX_POOL[equipType][poolType].items():
        if otherId.split('_t')[0] != affixId.split('_t')[0]:
            continue
        if otherAffix.levelReq > item.level:
            continue
        candidates.append(otherAffix)

    return candidates

def getTieredAffix(slot: str, kind: str, info: Optional[List[Affix, str]] =[], affixId: Optional[str] = None) -> Optional[Affix]:
    """
    kind=prefixes/suffixes\n
    info should be [Affix, tier]\n
    affixId should be exact id to immediately extract from the affix pool e.g. 'added_damage_t4'
    """
    if affixId is None:
        affix = info[0]
        kind = affix.kind
        tier = info[1]
        affixId = affix.id.strip('_t')[0]
        affixId = f'{affixId}_t{tier}'
    if kind == 'prefix':
        kind = 'prefixes'
    elif kind == 'suffix':
        kind = 'suffixes'
    newAffix = AFFIX_POOL[slot][kind].get(affixId, None)
    return deepcopy(newAffix) if newAffix is not None else None

AFFIX_POOL, MAX_TIERS = _createAffixList()
