import json
import random
from os.path import exists
from typing import Any, Dict, List, Optional

def _mythicAffixDataPath() -> str:
    return 'Korus/scripts/items/data/mythicAffixes.json' if exists('Korus') else 'scripts/items/data/mythicAffixes.json'

def _loadMythicAffixData() -> Dict[str, Dict]:
    with open(_mythicAffixDataPath(), 'r', encoding='utf-8') as f:
        return json.load(f)

def _rollRangeValue(minVal, maxVal):
    if isinstance(minVal, float) or isinstance(maxVal, float):
        return round(random.uniform(minVal, maxVal), 2)
    return random.randint(minVal, maxVal)

def _formatValue(value) -> str:
    if isinstance(value, float) and value.is_integer():
        value = int(value)
    return str(value)

class MythicAffixLine:
    def __init__(self, effect: str, text: str, values: Dict[str, float] = None,
                 percentFlags: Dict[str, bool] = None, meta: Dict = None, affixId: str = None,
                 mastery: float = 0):
        self.effect = effect
        self.text = text
        self._baseValues = values or {}
        self.percentFlags = percentFlags or {}
        self.meta = meta or {}
        self.affixId = affixId  # owning MythicAffix's id, used to look up bespoke onActions handlers
        self.mastery = mastery  # kept in sync with Equipment.mastery via Equipment.applyMastery()

    @property
    def values(self) -> Dict[str, float]:
        mastery = self.mastery / 100
        scaled = {}
        for key, base in self._baseValues.items():
            if isinstance(base, float):
                scaled[key] = round(base * (1 + mastery), 2)
            else:
                scaled[key] = round(base * (1 + mastery))
        return scaled

    @property
    def description(self) -> str:
        desc = self.text
        for key, value in self.values.items():
            desc = desc.replace(f'[{key}]', _formatValue(value))
        return desc

    @property
    def onActions(self) -> Dict[str, Any]:
        from . import mythicEffects
        return mythicEffects.getHandlers(self.affixId, self.effect)

    def serialise(self) -> dict:
        return {
            'effect': self.effect,
            'text': self.text,
            'values': self._baseValues,
            'percentFlags': self.percentFlags,
            'meta': self.meta,
            'affixId': self.affixId,
            'mastery': self.mastery,
        }

    @classmethod
    def deserialise(cls, data: dict) -> 'MythicAffixLine':
        return cls(data['effect'], data['text'], data.get('values', {}),
                   data.get('percentFlags', {}), data.get('meta', {}), data.get('affixId'),
                   data.get('mastery', 0))

    @classmethod
    def roll(cls, lineData: dict, affixId: str = None) -> 'MythicAffixLine':
        effect = lineData['effect']
        text = lineData['text']
        values: Dict[str, float] = {}
        percentFlags: Dict[str, bool] = {}

        if 'rolls' in lineData:
            for rollSpec in lineData['rolls']:
                key = rollSpec['key']
                values[key] = _rollRangeValue(rollSpec['min'], rollSpec['max'])
                percentFlags[key] = rollSpec.get('isPercent', False)
        elif 'perLevel' in lineData:
            perLevel = lineData['perLevel']
            values['x'] = _rollRangeValue(perLevel['min'], perLevel['max'])
            percentFlags['x'] = lineData.get('isPercent', False)

        meta = {k: v for k, v in lineData.items() if k not in ('effect', 'text', 'rolls', 'perLevel')}

        return cls(effect, text, values, percentFlags, meta, affixId)

    def __str__(self):
        return self.description

class MythicAffix:
    def __init__(self, affixId: str, name: str, levelReq: int, equipType: str,
                 categories: List[str], lines: List[MythicAffixLine], kind: str = 'suffix'):
        self.id = affixId
        self.name = name
        self.levelReq = levelReq
        self.equipType = equipType
        self.categories = categories
        self.lines = lines
        self.kind = kind  # 'prefix' or 'suffix' - which half of the item name this occupies

    @property
    def description(self) -> str:
        return '\n'.join(line.description for line in self.lines)

    def serialise(self) -> dict:
        return {
            'id': self.id,
            'name': self.name,
            'levelReq': self.levelReq,
            'equipType': self.equipType,
            'categories': self.categories,
            'lines': [line.serialise() for line in self.lines],
            'kind': self.kind,
        }

    @classmethod
    def deserialise(cls, data: dict) -> 'MythicAffix':
        return cls(
            data['id'], data['name'], data['levelReq'], data['equipType'],
            data['categories'], [MythicAffixLine.deserialise(l) for l in data['lines']],
            data.get('kind', 'suffix'),
        )

    def __str__(self):
        return self.description

MYTHIC_AFFIX_DATA: Dict[str, Dict] = _loadMythicAffixData()

def rollMythicAffix(equipType: str, itemLevel: int, rarity: object = None) -> Optional[MythicAffix]:
    from .items import ItemRarity
    if rarity is not None and rarity != ItemRarity.MYTHIC:
        return None

    pool = MYTHIC_AFFIX_DATA.get(equipType)
    if not pool:
        return None

    eligible = [(affixId, info) for affixId, info in pool.items() if info['levelReq'] <= itemLevel]
    if not eligible:
        return None

    affixId, info = random.choice(eligible)
    lines = [MythicAffixLine.roll(lineData, affixId) for lineData in info['lines']]
    return MythicAffix(affixId, info['name'], info['levelReq'], equipType, info['categories'], lines,
                       info.get('kind', 'suffix'))
