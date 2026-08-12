import json
from typing import Optional, Dict, Any, List, Set
import random
from .styles import console, printError
from copy import deepcopy
from os.path import exists
from .affixes import Affix

descMark = 'plum4'

class MythicAffix(Affix):
    def __init__(self, id, name, levelReq, tier, stat, minVal, maxVal, isPercent = False, kind = "prefix", weight = 100, categories = None, description = "", sign = True, **kwargs):
        super().__init__(id, name, levelReq, tier, stat, minVal, maxVal, isPercent, kind, weight, categories, isMythic = True, **kwargs)
        self.descriptionBase = f'[{descMark}]{description}[/{descMark}]'
        self.sign = sign

    @property
    def description(self) -> str:
        sign = ''
        per = ''
        if self.value is not None:
            if self.sign:
                if self.value > 0:
                    sign = '+'
                elif self.value < 0:
                    sign = '-'
            if self.isPercent:
                per = '%'

        value = f'{sign}{self.value}'
        if '[x]' in self.descriptionBase:
            desc = self.descriptionBase.replace('[x]', f'[bold]{value}{per}[/bold]')
            return desc
        return self.descriptionBase

    def _serialise(self):
        x = super()._serialise()
        x['description'] = self.descriptionBase

    @classmethod
    def deserialise(cls, data):
        affix = super().deserialise(data)
        affix.descriptionBase = data['description']
        return affix
    
    def __str__(self):
        return self.description
    
def _createMythicAffixList() -> Dict[str, Dict[str, Affix]] | Dict[str, Affix]:
    fp = 'Korus/data/mythicAffixes.json' if exists('Korus') else 'data/mythicAffixes.json'
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

    markup = 'bold underline italic dark_magenta'

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
                data = affixInfo['tiers']['1']
                name = data['name']
                name = f'[{markup}]{name}[/{markup}]'
                sign = affixInfo.get('sign', True)

                mAffix = MythicAffix(
                    id=affixId,
                    name=name,
                    levelReq=data['levelReq'],
                    tier=1,
                    stat=affixInfo['stat'],
                    minVal=data['min'],
                    maxVal=data['max'],
                    isPercent=affixInfo.get('isPercent', False),
                    kind=affixType[:-2],
                    weight=data.get('weight', 100),
                    categories=affixInfo['categories'],
                    description=affixInfo['description'],
                    sign=sign,
                )

                affixPool[equipType][affixType][affixId] = mAffix
        
    return affixPool

def rollMythicAffix(equipType: str, affixType: str, itemLevel: int, rarity: str,
                    excludeIds: Set[str], defenseType: str = None,
                    minAffixLevel: int | None = None) -> Optional[Affix]:
    from .items import ItemRarity
    if rarity != ItemRarity.MYTHIC:
        return None
    
    excludeIds = excludeIds or set()

    if equipType not in MYTHIC_AFFIX_POOL:
        return None
    
    if affixType == 'prefix':
        affixType = 'prefixes'
    elif affixType == 'suffix':
        affixType = 'suffixes'

    availableAffixes = MYTHIC_AFFIX_POOL[equipType][affixType]

    minLevelAffix = max(0, min(30, itemLevel - 75))
    if minAffixLevel:
        minLevelAffix = minAffixLevel

    validAffixes = []
    weights = []

    for affixId, affix in availableAffixes.items():
        if minLevelAffix <= affix.levelReq <= itemLevel and affixId not in excludeIds:
            baseId = affix.id
            if baseId not in excludeIds:

                if defenseType:
                    if defenseType == 'energyShield':
                        defenseType = 'energy_shield'
                    defenseTypes = ['armour', 'evasion', 'energy_shield']
                    if affix.stat in defenseTypes:
                        if affix.stat != defenseType:
                            continue

                validAffixes.append(affix)
                weight = affix.weight
                weights.append(weight)

    if not validAffixes:
        return None
    
    aff = random.choices(validAffixes, weights=weights, k=1)[0]

    rolledAffix = MythicAffix(
        id=aff.id,
        name=aff.name,
        levelReq=aff.levelReq,
        tier=aff.tier,
        stat=aff.stat,
        minVal=aff.minVal,
        maxVal=aff.maxVal,
        isPercent=aff.isPercent,
        kind=aff.kind,
        weight=aff.weight,
        categories=list(aff.categories),
        description=aff.descriptionBase,
        sign=aff.sign,
    )
    rolledAffix.rollValue()

    return rolledAffix

MYTHIC_AFFIX_POOL = _createMythicAffixList()