from .items import Item, ItemRarity, ItemType, RARITY_SERIALS, RARITY_VALUES
from ..items.affixes import Affix, rollAffix
from ..styles import console, printError
from ..korusFeedClient import reportItem
from ..items.mythicAffixes import rollMythicAffix, MythicAffix
from typing import Optional, List, Dict, Any, Tuple
import random
import json
import itertools
from os.path import exists
import uuid

_equipmentIdCounter = itertools.count(1)

def _nextEquipmentId() -> int:
    return next(_equipmentIdCounter)

def peekNextEquipmentId() -> int:
    """Returns the next id that would be issued, without consuming it. Used by Game to serialise counter state."""
    global _equipmentIdCounter
    value = next(_equipmentIdCounter)
    _equipmentIdCounter = itertools.count(value)
    return value

def setNextEquipmentId(value: int) -> None:
    """Restores counter state on load so ids stay unique and stable across saves."""
    global _equipmentIdCounter
    _equipmentIdCounter = itertools.count(value)

def _loadEquipmentBases() -> dict:
    fp = 'Korus/scripts/items/equipmentBases.json' if exists('Korus') else 'scripts/items/equipmentBases.json'
    with open(fp, 'r', encoding='utf-8') as f:
        return json.load(f)

EQUIPMENT_BASES = _loadEquipmentBases()

def _classOk(data: dict, className: Optional[str] = None) -> bool:
    requiredClass = data.get('requiredClass')
    return requiredClass is None or requiredClass == className

def _bracketAnchor(pool: Dict[str, dict], level: int) -> List[Tuple[str, dict]]:
    levels = sorted({data['minLevel'] for data in pool.values() if data['minLevel'] <= level})
    if not levels:
        return []
    bracketLevels = levels[-2:]
    anchorLevel = bracketLevels[0] if len(bracketLevels) == 1 else random.choices(bracketLevels, weights=[30, 70], k=1)[0]
    return [(name, data) for name, data in pool.items() if data['minLevel'] == anchorLevel]

def _selectTier(tiers: dict, level: int, className: Optional[str] = None) -> Tuple[str, dict]:
    usable = {name: data for name, data in tiers.items() if _classOk(data, className)}
    if not usable:
        usable = tiers

    progression = {name: data for name, data in usable.items() if 'weight' not in data}
    specials = {name: data for name, data in usable.items() if 'weight' in data}

    candidates = _bracketAnchor(progression, level) + _bracketAnchor(specials, level)
    if not candidates:
        return min(usable.items(), key=lambda nd: nd[1]['minLevel'])

    weights = [data.get('weight', 100) for _, data in candidates]
    return random.choices(candidates, weights=weights, k=1)[0]

ENTROPY_RESISTANCE = {
    ItemRarity.COMMON: 0.0,
    ItemRarity.UNCOMMON: 0.05,
    ItemRarity.RARE: 0.125,
    ItemRarity.EPIC: 0.20,
    ItemRarity.LEGENDARY: 0.35,
    ItemRarity.MYTHIC: 0.5,
    ItemRarity.BLANK: 0.0,
}

MAX_PRESERVATIONS = {
    ItemRarity.COMMON: 1,
    ItemRarity.UNCOMMON: 1,
    ItemRarity.RARE: 2,
    ItemRarity.EPIC: 2,
    ItemRarity.LEGENDARY: 3,
    ItemRarity.MYTHIC: 4,
    ItemRarity.BLANK: 0,
}

DAMAGE_TYPES = [
    'physical',
    'fire', 'cold', 'lightning', 'earth',
    'dark', 'holy', 'arcane',
    'ethereal', 'psychic', 'chaos'
]

class AffixSlot:
    def __init__(self, kind: str, affix: Optional[Affix] = None):
        self.kind = kind
        self.affix: Affix | None = None if affix is None else affix

    @property
    def locked(self):
        return self.affix.locked
    
    @property
    def soulbound(self):
        if self.affix is not None:
            return self.affix.soulbound
        return False

    @property
    def isEmpty(self):
        return self.affix is None
    
    def lock(self):
        self.affix.locked = True

    def __rich__(self):
        return self.__str__()

    def __str__(self):
        if self.locked:
            console.print(f"[steel_blue bold underline]LOCKED[/steel_blue bold underline] {self.affix}")
        else:
            console.print(self.affix)

    def serialise(self):
        if self.isEmpty:
            return {
                'kind': self.kind,
                'affix': None
            }
        else:
            return {
                'kind': self.kind,
                'affix': self.affix._serialise()
            }

    @classmethod
    def deserialise(cls, slotData):
        kind = slotData['kind']
        affixData = slotData.get('affix', None)
        if affixData is not None:
            if 'soulbound_soulbound_' in affixData['id']:
                affixData['soulbound'] = True
            affix = Affix.deserialise(affixData)
        else:
            affix = None
        return cls(
            kind=kind,
            affix=affix
        )

ARMOUR_SLOTS = ['head', 'chest', 'legs', 'feet', 'offhand']
EQUIPMENT_BASES_KEY = {'offhand': 'shield'}  # equipment.slot -> equipmentBases.json top-level key, where they differ

RARITY_MULTIPLIERS = {
    ItemRarity.COMMON: 1,
    ItemRarity.UNCOMMON: 1.2,
    ItemRarity.RARE: 1.5,
    ItemRarity.EPIC: 1.8,
    ItemRarity.LEGENDARY: 2.2,
    ItemRarity.MYTHIC: 2.5,
    ItemRarity.BLANK: 2.5,
}

# implicit stat keys whose value is a percentage rather than a flat amount, for display purposes
PERCENT_IMPLICIT_STATS = frozenset({
    'ailment_avoidance', 'stun_avoidance', 'crit_resistance', 'crit_chance', 'crit_multi',
    'crit_chance_when_faster', 'resistance_penetration', 'lifesteal', 'damage_reduction',
    'increased_defenses', 'chance_to_block', 'chance_to_bleed', 'chance_to_multihit',
    'chance_to_apply_vulnerable', 'chance_to_apply_exposed', 'chance_to_stun',
    'buff_effect_increased_low_hp', 'mana_cost_reduced', 'mana_damage_return_increased',
    'insanity_swing_increased', 'insanity_penalty_reduction', 'insanity_extreme_effect_increased',
    'lost_damage_increased', 'favour_defensive_effect_increased', 'favour_heal_increased',
    'unleash_cost_reduced', 'vengeance_consume_crit_damage_increased', 'ghostly_heal_increased',
    'echo_damage_increased',
    'physical_resistance', 'fire_resistance', 'cold_resistance', 'lightning_resistance',
    'earth_resistance', 'dark_resistance', 'holy_resistance', 'arcane_resistance',
    'chaos_resistance', 'ethereal_resistance', 'psychic_resistance', 'all_resistance',
    'elemental_resistance', 'otherworld_resistance', 'divine_resistance',
    'max_physical_resistance', 'max_fire_resistance', 'max_cold_resistance',
    'max_lightning_resistance', 'max_earth_resistance', 'max_dark_resistance',
    'max_holy_resistance', 'max_arcane_resistance', 'max_chaos_resistance',
    'max_ethereal_resistance', 'max_psychic_resistance', 'max_all_resistance',
    'max_elemental_resistance', 'max_otherworld_resistance', 'max_divine_resistance',
})

def _formatImplicitLine(stat: str, value) -> str:
    isPercent = stat in PERCENT_IMPLICIT_STATS
    prefix = "+" if value > 0 else ""
    suffix = "%" if isPercent else ""
    statDisplay = stat.replace('_', ' ').title()
    return f"    |-> [cyan]{prefix}{value}{suffix} {statDisplay}[/cyan]"


class Equipment(Item):
    def __init__(self, slot: str, rarity: ItemRarity = ItemRarity.COMMON,
                 defenses: dict[str, int] = {}, damages: dict[str, Any] = {}, implicits: dict[str, float] = {},
                 prefixes: List[Affix] = None, suffixes: List[Affix] = None, numPrefixes: int = 1, numSuffixes: int = 1,
                 level: int = 1, maxEntropy: float | None = None, baseTypeName: Optional[str] = None):

        itemType = ItemType.EQUIPMENT

        super().__init__("", itemType, rarity)
        self.id = _nextEquipmentId()
        self.feedId = str(uuid.uuid4())
        self.slot = slot  # weapon, offhand, head, chest, legs, feet, ring, amulet, sigil
        self.prefixSlots = [AffixSlot('prefix') for _ in range(numPrefixes)]
        for slot, affix in zip(self.prefixSlots, prefixes or []):
            slot.affix = affix
        self.suffixSlots = [AffixSlot('suffix') for _ in range(numSuffixes)]
        for slot, affix in zip(self.suffixSlots, suffixes or []):
            slot.affix = affix

        self.level = level
        self.defenseType: str = defenses.get('defenseType', None)
        self.defenseValue: int = defenses.get('defenseValue', 0)
        self.baseDefenseValue = defenses.get('baseDefenseValue', 0)

        self.damage = damages.get('damage', 0)
        self.baseDamage = damages.get('baseDamage', 0)
        self.damageType = damages.get('damageType', None)
        self.twoHanded: bool = bool(damages.get('twoHanded', False))

        self.implicits: Dict[str, float] = dict(implicits or {})
        self.baseTypeName: Optional[str] = baseTypeName

        self._generateName()

        self.entropy = 0
        self.entropyPreserved = False
        self.numPreserved = 0
        self.maxPreservations = MAX_PRESERVATIONS[rarity]
        self.maxEntropy = maxEntropy if maxEntropy is not None else 1.0
        self.baseEntropyResistance = ENTROPY_RESISTANCE[rarity]
        self.destabilised = False
        self.destabilisedAffixes = []
        self.parallel = False
        self.foresighted = False
        self.mythicAffix: Optional[MythicAffix] = None

        self.blankCuratedHand: Optional[List[Dict]] = None
        self.blankTableKey: Optional[str] = None

        self.foresightResults: Dict[object, dict[str, List[str, AffixSlot] | str]] = {}
        """stores { CraftingItem: { 'pre'/'suf': [ 'slot': <int>, 'affixSlot': <AffixSlot> ], 'message': <str> } } }"""

        self.mastery = 0

        self._statsDirty = True
        self.update()
        self.baseMaxDurability = self.maxDurability
        self.durability = self.maxDurability

    def _ensureStatsCache(self):
        if not self._statsDirty:
            return
        prefixes = [s.affix for s in self.prefixSlots if s.affix]
        suffixes = [s.affix for s in self.suffixSlots if s.affix]
        allSlots = self.prefixSlots + self.suffixSlots

        self._prefixesCache = prefixes
        self._suffixesCache = suffixes
        self._statsCache = prefixes + suffixes
        self._allSlotsFilledCache = all(s.affix is not None for s in allSlots)
        self._allSlotsEmptyCache = all(s.affix is None for s in allSlots)
        self._lockedCache = any(affix.locked for affix in self._statsCache)
        self._statsDirty = False

    @property
    def prefixes(self) -> List[Affix]:
        self._ensureStatsCache()
        return self._prefixesCache

    @property
    def suffixes(self) -> List[Affix]:
        self._ensureStatsCache()
        return self._suffixesCache

    @property
    def stats(self) -> List[Affix]:
        self._ensureStatsCache()
        return self._statsCache

    @property
    def allSlotsFilled(self) -> bool:
        self._ensureStatsCache()
        return self._allSlotsFilledCache

    @property
    def allSlotsEmpty(self) -> bool:
        self._ensureStatsCache()
        return self._allSlotsEmptyCache

    @property
    def locked(self) -> bool:
        self._ensureStatsCache()
        return self._lockedCache

    @property
    def weaponType(self) -> Optional[str]:
        if self.slot != 'weapon' or not self.baseTypeName:
            return None
        handedness = 'two_handed' if self.twoHanded else 'one_handed'
        for wType, tiers in EQUIPMENT_BASES['weapons'][handedness].items():
            if self.baseTypeName in tiers:
                return wType
        return None

    @property
    def sigilType(self) -> Optional[str]:
        if self.slot != 'sigil' or not self.baseTypeName:
            return None
        for category, tiers in EQUIPMENT_BASES['sigil'].items():
            if self.baseTypeName in tiers:
                return category
        return None

    @property
    def soulbound(self) -> bool:
        for slot in self.prefixSlots + self.suffixSlots:
            if slot.soulbound:
                return True
        return False

    @property
    def entropyLocked(self) -> bool:
        return self.entropy >= self.maxEntropy

    @property
    def craftable(self) -> bool:
        return not (
            self.entropyLocked or self.destabilised or self.parallel
        )

    @property
    def preservable(self) -> bool:
        if self.numPreserved >= self.maxPreservations:
            return False
        return True

    def serialise(self):
        temp = super().serialise()
        temp['id'] = self.id
        temp['feedId'] = self.feedId
        temp['slot'] = self.slot
        temp['prefixSlots'] = [s.serialise() for s in self.prefixSlots]
        temp['suffixSlots'] = [s.serialise() for s in self.suffixSlots]
        temp['level'] = self.level

        temp['durability'] = self.durability
        temp['maxDurability'] = self.maxDurability
        temp['baseMaxDurability'] = self.baseMaxDurability

        temp['mastery'] = self.mastery

        temp['defenseType'] = self.defenseType
        temp['defenseValue'] = self.defenseValue
        temp['baseDefenseValue'] = self.baseDefenseValue

        temp['damage'] = self.damage
        temp['baseDamage'] = self.baseDamage
        temp['damageType'] = self.damageType
        temp['twoHanded'] = self.twoHanded

        temp['implicits'] = self.implicits
        temp['baseTypeName'] = self.baseTypeName

        temp['entropy'] = self.entropy
        temp['entropyPreserved'] = self.entropyPreserved
        temp['maxEntropy'] = self.maxEntropy
        temp['baseEntropyResistance'] = self.baseEntropyResistance
        temp['entropyResistance'] = self.entropyResistance
        temp['entropyLocked'] = self.entropyLocked
        temp['destabilised'] = self.destabilised
        temp['foresighted'] = self.foresighted
        temp['foresightResults'] = {
            runeName: {
                'prefixes': [
                    {
                        'slot': p['slot'],
                        'affix': p['affix']._serialise()
                    } for p in self.foresightResults[runeName]['prefixes']
                ],
                'suffixes': [
                    {
                        'slot': s['slot'],
                        'affix': s['affix']._serialise()
                    } for s in self.foresightResults[runeName]['suffixes']
                ],
                'message': self.foresightResults[runeName]['message']
            } for runeName in self.foresightResults.keys()
        }
        temp['destabilisedAffixes'] = [
            {
                'name': da.name,
                'stat': da.stat,
                'value': da.value,
                'isPercent': da.isPercent
            } for da in getattr(self, 'destabilisedAffixes', [])
        ]
        temp['mythicAffix'] = self.mythicAffix.serialise() if self.mythicAffix else None
        temp['blankCuratedHand'] = self.blankCuratedHand
        temp['blankTableKey'] = self.blankTableKey

        return temp

    @classmethod
    def deserialise(cls, data):
        prefixes = []
        prefixSlots = []
        for slotData in data.get('prefixSlots', []):
            if slotData:
                slot = AffixSlot.deserialise(slotData)
                if slot.affix is not None:
                    prefixes.append(slot.affix)
            prefixSlots.append(slot)
        suffixes = []
        suffixSlots = []
        for slotData in data.get('suffixSlots', []):
            if slotData:
                slot = AffixSlot.deserialise(slotData)
                if slot.affix is not None:
                    suffixes.append(slot.affix)
            suffixSlots.append(slot)
        
        e = cls(
            data.get('slot'),
            RARITY_SERIALS[data.get('rarity', 'common')],
            {
                'defenseType': data.get('defenseType', None),
                'defenseValue': data.get('defenseValue', 0),
                'baseDefenseValue': data.get('baseDefenseValue', 0)
            },
            {
                'damage': data.get('damage', 0),
                'baseDamage': data.get('baseDamage', 0),
                'damageType': data.get('damageType', None),
                'twoHanded': data.get('twoHanded', False)
            },
            data.get('implicits', {}),
            prefixes,
            suffixes,
            len(prefixSlots), len(suffixSlots),
            data.get('level', 1),
            baseTypeName=data.get('baseTypeName', None)
        )
        i = super().deserialise(data)

        if data.get('id') is not None:
            e.id = data['id']  # old saves without an id keep the fresh one __init__ assigned
        if data.get('feedId') is not None:
            e.feedId = data['feedId']

        e.prefixSlots = prefixSlots
        e.suffixSlots = suffixSlots

        e.name = i.name
        e.itemType = i.itemType
        e.value = i.value
        e.rarity = i.rarity
        e.stackable = i.stackable or False
        e.maxStack  = i.maxStack or 1

        e.mastery = data.get('mastery', 0)
        e.entropy = data.get('entropy', 0)
        e.entropyPreserved = data.get('entropyPreserved', False)
        e.maxEntropy = data.get('maxEntropy', 1.0)
        e.baseEntropyResistance = data.get('baseEntropyResistance', ENTROPY_RESISTANCE[e.rarity])
        e.entropyResistance = data.get('entropyResistance', e.baseEntropyResistance)
        e.foresighted = data.get('foresighted', False)
        e.foresightResults = {}
        for runeName, forData in data.get('foresightResults', {}).items():
            e.foresightResults[runeName] = {
                'prefixes': [
                    {
                        'slot': p['slot'],
                        'affix': Affix.deserialise(p['affix'])
                    } for p in forData['prefixes']
                ],
                'suffixes': [
                    {
                        'slot': s['slot'],
                        'affix': Affix.deserialise(s['affix'])
                    } for s in forData['suffixes']
                ],
                'message': forData['message']
            }
        e.destabilised = data.get('destabilised', False)
        from scripts.crafting.destabilisationRune import DestabilisedAffix
        e.destabilisedAffixes = []
        for daData in data.get('destabilisedAffixes', []):
            da = DestabilisedAffix(
                name=daData['name'],
                stat=daData['stat'],
                value=daData['value'],
                isPercent=daData['isPercent']
            )
            e.destabilisedAffixes.append(da)

        mythicAffixData = data.get('mythicAffix')
        e.mythicAffix = MythicAffix.deserialise(mythicAffixData) if mythicAffixData else None
        e.blankCuratedHand = data.get('blankCuratedHand', None)
        e.blankTableKey = data.get('blankTableKey', None)

        e.update()
        e.baseMaxDurability = data.get('baseMaxDurability', e.maxDurability)
        e.durability = data.get('durability', e.maxDurability)

        return e

    def calculateValue(self) -> int:
        value = 100 + self.level
        tiers = [a.tier for a in (self.prefixes + self.suffixes)]
        value += sum(tiers) * 75
        value += (len(self.prefixes) + len(self.suffixes)) * random.randint(30, 70)
        value = int(value * RARITY_VALUES[self.rarity.value])

        self.value = value

    def __rich__(self):
        return self.__str__()

    def __str__(self):
        stat_string = ""
        if len(self.prefixSlots) > 0:
            stat_string += "[bold dim] === PREFIXES ===[/bold dim]\n"
            for slot in self.prefixSlots:
                if slot.isEmpty:
                    stat_string += "    |-> [-] EMPTY PREFIX\n"
                else:
                    stat_string += f"    |-> {slot.affix}\n"
        if len(self.suffixSlots) > 0:
            stat_string += "[bold dim] === SUFFIXES ===[/bold dim]\n"
            for slot in self.suffixSlots:
                if slot.isEmpty:
                    stat_string += "    |-> [-] EMPTY SUFFIX\n"
                else:
                    stat_string += f"    |-> {slot.affix}\n"
        corruptedString = ""
        if hasattr(self, 'destabilisedAffixes') and len(self.destabilisedAffixes) > 0:
            corruptedString += "[bold dim dark_red] === DESTABILISED ===[/bold dim dark_red]\n"
            for da in self.destabilisedAffixes:
                corruptedString += f"    |-> {da}\n"
        defenseString = ""
        if self.defenseType and self.defenseValue:
            defenseFormatted = self.defenseType.replace('energy_shield', 'Energy Shield').title()
            defenseString = f"\n[cyan]{defenseFormatted}:[/cyan] {self.defenseValue} (Base: {self.baseDefenseValue})"
        damageString = ""
        if self.damage:
            typeStr = ""
            if self.damageType is not None:
                dType = self.damageType
                typeStr = f" | [cyan]Damage Type:[/cyan] [{dType}]{dType.title()}[/{dType}]"
            damageString = f"\n[cyan]Damage:[/cyan] {self.damage} (Base: {self.baseDamage}){typeStr}"
        implicitString = ""
        if self.implicits:
            implicitLines = "\n".join(
                _formatImplicitLine(stat, value) for stat, value in self.implicits.items()
            )
            implicitString = f"\n[bold dim] === IMPLICITS ===[/bold dim]\n{implicitLines}"
        mythicAffixString = ""
        if self.mythicAffix:
            mythicLines = "\n".join(f"    |-> {line}" for line in self.mythicAffix.description.split("\n"))
            mythicAffixString = f"\n[mythic] === MYTHIC: {self.mythicAffix.name} ===[/mythic]\n{mythicLines}"
        entropyString = f"\n[red3 bold]Entropy:[/red3 bold] {self.entropy} / {self.maxEntropy} | [hot_pink]Entropy Resistance:[/hot_pink] {round(self.entropyResistance * 100)}%"
        if self.numPreserved > 0:
            if self.preservable:
                entropyString += f" | [spring_green3 bold]Preservation Uses Remaining:[/spring_green3 bold] {self.maxPreservations - self.numPreserved}"
            else:
                entropyString += " | [dim green]Out of Preservations[/dim green]"
        if self.entropyLocked:
            entropyString += " | [red3 bold]ENTROPY LOCKED[/red3 bold]"
        if self.entropyPreserved:
            entropyString += " | [spring_green3 bold]Entropy Preserved[/spring_green3 bold]"
        destabilisedString = ""
        if self.destabilised:
            destabilisedString = '[dark_red bold underline]DESTABILISED[/dark_red bold underline] | '
        parStr = ""
        if self.parallel:
            parStr = " [misty_rose3 bold underline]Parallel Item[/misty_rose3 bold underline] | "
        masteryString = f" | [gold1]Mastery:[/gold1] {self.mastery}%"
        return f"{destabilisedString}{parStr}{self.name} | [bold]Durability:[/bold] {self.durability} / {self.maxDurability}{masteryString}{entropyString}{damageString}{defenseString}{implicitString}{mythicAffixString}\n{stat_string}{corruptedString}"

    def calculateMaxDurability(self):
        if hasattr(self, 'maxDurability') and hasattr(self, 'durability'):
            if self.maxDurability == float('inf') or self.durability == float('inf'):
                return
        durabilityValues = {
            ItemRarity.COMMON: 50,
            ItemRarity.UNCOMMON: 100,
            ItemRarity.RARE: 200,
            ItemRarity.EPIC: 400,
            ItemRarity.LEGENDARY: 800,
            ItemRarity.MYTHIC: 1100,
            ItemRarity.BLANK: 1100,
        }
        if not hasattr(self, 'baseMaxDurability'):
            baseDurability = durabilityValues[self.rarity] + (self.level * (random.randint(1, 5)))
        else:
            baseDurability = self.baseMaxDurability

        added = 0
        increased = 0
        for affix in self.suffixes: #suffix increases durability
            if affix.stat == 'durability':
                if affix.isFlat:
                    added += affix.value
                elif affix.isIncreased:
                    increased += affix.value / 100

        durability = round((baseDurability + added) * (1 + increased))

        self.maxDurability = durability
        if hasattr(self, 'durability'):
            self.durability = min(self.durability, self.maxDurability)

    @property
    def maxMastery(self) -> float:
        """Base cap is 20%, extended by a mythic mastery_bonus line if present."""
        cap = 20
        if self.mythicAffix:
            for line in self.mythicAffix.lines:
                if line.effect == 'mastery_bonus':
                    cap += line.values.get('x', 0)
        return cap

    def gainMastery(self, amount: int):
        cap = self.maxMastery
        if self.mastery >= cap:
            return
        maxGain = cap - self.mastery
        gained = amount
        if amount > maxGain:
            gained = maxGain
        if gained > 0:
            self.mastery += gained
            console.print(f"[bold][gold1]Gained {gained}% Mastery[/gold1] on {self.name}. New Amount: [gold1]{self.mastery} / {cap}[/gold1][/bold]")
            self.update()
        else:
            self.mastery += gained
            console.print(f"[bold][red1]Lost {abs(gained)}%[/red1] [gold1]Mastery[/gold1] on {self.name}. New Amount: [gold1]{self.mastery} / {cap}[/gold1][/bold]")

    def applyMastery(self):
        for slot in self.prefixSlots + self.suffixSlots:
            if slot.affix is not None:
                slot.affix.mastery  = self.mastery
        if self.mythicAffix:
            for line in self.mythicAffix.lines:
                line.mastery = self.mastery

    def getExcludedIds(self) -> List[List]:
        """Returns [excludedPrefixes, excludedSuffixes] as two separate variables"""
        excludedPre = set()
        excludedSuf = set()

        if hasattr(self, 'defenseType') and self.defenseValue > 0:
            if self.defenseType == 'armour':
                excludedPre.add('added_evasion')
                excludedPre.add('increased_evasion')
                excludedPre.add('added_energy_shield')
                excludedPre.add('increased_energy_shield')
            elif self.defenseType == 'evasion':
                excludedPre.add('added_armour')
                excludedPre.add('increased_armour')
                excludedPre.add('added_energy_shield')
                excludedPre.add('increased_energy_shield')
            else:
                excludedPre.add('added_armour')
                excludedPre.add('increased_armour')
                excludedPre.add('added_energy_shield')
                excludedPre.add('increased_energy_shield')

        for affix in self.prefixes:
            baseId = affix.id.split('_t')[0]
            excludedPre.add(baseId)
        for affix in self.suffixes:
            baseId = affix.id.split('_t')[0]
            excludedSuf.add(baseId)

        if self.rarity == ItemRarity.BLANK: # entropy 100% dead stat on blank items
            for entropyId in ('added_entropy', 'increased_entropy', 'entropy_resistance'):
                excludedPre.add(entropyId)
                excludedSuf.add(entropyId)

        return excludedPre, excludedSuf

    @staticmethod
    def _rollRangeValue(baseMin: float, baseMax: float, rarity: ItemRarity, level: int, halveForES: bool = False) -> int:
        """Shared rarity/level scaling used by both the damage and defense base rolls."""
        multiplier = RARITY_MULTIPLIERS.get(rarity, 1) + level / 100
        if halveForES:
            multiplier = round(multiplier / 2, 3)
        return random.randint(int(baseMin * multiplier), int(baseMax * multiplier))

    @staticmethod
    def _calculateDefenseRoll(slot: str, level: int, rarity: ItemRarity, defenseType: str = None, className: Optional[str] = None) -> Tuple[Optional[str], int, dict, Optional[str]]:
        if slot not in ARMOUR_SLOTS:
            return None, 0, {}, None

        selectedType = defenseType or random.choice(['armour', 'evasion', 'energy_shield'])
        tiers = EQUIPMENT_BASES[EQUIPMENT_BASES_KEY.get(slot, slot)][selectedType]
        tierName, tierData = _selectTier(tiers, level, className)

        defenseValue = Equipment._rollRangeValue(
            tierData['defenseMin'], tierData['defenseMax'], rarity, level, halveForES=(selectedType == 'energy_shield')
        )
        implicits = dict(tierData.get('implicits', {}))

        return selectedType, defenseValue, implicits, tierName

    WEAPON_HANDEDNESS_WEIGHTS = {'one_handed': 65, 'two_handed': 35}
    WEAPON_TYPE_WEIGHTS = {
        'one_handed': {'sword': 1, 'axe': 1, 'dagger': 1, 'mace': 1, 'claw': 1},
        'two_handed': {'sword': 1, 'axe': 1, 'mace': 1, 'quarterstaff': 1, 'maul': 1, 'spear': 1},
    }

    @staticmethod
    def _pickWeaponBase(level: int, className: Optional[str] = None) -> Tuple[bool, str, str, dict]:
        """Returns (twoHanded, weaponType, tierName, tierData)."""
        handedness = random.choices(
            list(Equipment.WEAPON_HANDEDNESS_WEIGHTS),
            weights=list(Equipment.WEAPON_HANDEDNESS_WEIGHTS.values()), k=1
        )[0]
        typeWeights = Equipment.WEAPON_TYPE_WEIGHTS[handedness]
        weaponType = random.choices(list(typeWeights), weights=list(typeWeights.values()), k=1)[0]
        tiers = EQUIPMENT_BASES['weapons'][handedness][weaponType]
        tierName, tierData = _selectTier(tiers, level, className)
        return handedness == 'two_handed', weaponType, tierName, tierData

    @staticmethod
    def _calculateDamageRoll(slot: str, level: int, rarity: ItemRarity, className: Optional[str] = None) -> Tuple[int, Optional[str], dict, bool, str, Optional[str]]:
        if slot != 'weapon':
            return 0, None, {}, False, None

        twoHanded, weaponType, tierName, tierData = Equipment._pickWeaponBase(level, className)
        damage = Equipment._rollRangeValue(tierData['damageMin'], tierData['damageMax'], rarity, level)

        if random.random() <= 0.3:
            damageType = random.choice(DAMAGE_TYPES)
        else:
            damageType = None

        implicits = dict(tierData.get('implicits', {}))

        return damage, damageType, implicits, twoHanded, weaponType, tierName

    @staticmethod
    def _rollImplicitRange(rng: dict) -> float:
        if isinstance(rng['min'], float) or isinstance(rng['max'], float):
            return round(random.uniform(rng['min'], rng['max']), 2)
        return random.randint(rng['min'], rng['max'])

    @staticmethod
    def _pickFromFamilies(entries: dict, level: int, className: Optional[str] = None) -> Tuple[Optional[str], dict]:
        families: Dict[str, dict] = {}
        for name, data in entries.items():
            statKey = next(iter(data['implicits']))
            families.setdefault(statKey, {})[name] = data

        eligibleFamilies = {
            stat: fam for stat, fam in families.items()
            if any(d['minLevel'] <= level and _classOk(d, className) for d in fam.values())
        }
        if not eligibleFamilies:
            return None, {}

        def familyWeight(fam: dict) -> float:
            eligible = [d for d in fam.values() if d['minLevel'] <= level and _classOk(d, className)]
            newest = max(eligible, key=lambda d: d['minLevel'])
            return newest.get('weight', 100)

        statOptions = list(eligibleFamilies.keys())
        familyWeights = [familyWeight(eligibleFamilies[stat]) for stat in statOptions]
        chosenStat = random.choices(statOptions, weights=familyWeights, k=1)[0]
        tierName, tierData = _selectTier(eligibleFamilies[chosenStat], level, className)
        value = Equipment._rollImplicitRange(tierData['implicits'][chosenStat])

        result = {chosenStat: value}
        for extraStat, extraVal in tierData.get('extraImplicits', {}).items():
            result[extraStat] = Equipment._rollImplicitRange(extraVal) if isinstance(extraVal, dict) else extraVal

        return tierName, result

    @staticmethod
    def _pickAccessoryImplicit(slot: str, level: int, className: Optional[str] = None) -> Tuple[Optional[str], dict]:
        return Equipment._pickFromFamilies(EQUIPMENT_BASES[slot], level, className)

    @staticmethod
    def _pickSigilImplicit(level: int, className: Optional[str] = None) -> Tuple[Optional[str], dict, str]:
        category = random.choice(['offensive', 'defensive'])
        tierName, implicits = Equipment._pickFromFamilies(EQUIPMENT_BASES['sigil'][category], level, className)
        return tierName, implicits, category

    @staticmethod
    def _rerollBaseType(item: 'Equipment') -> bool:
        if not item.baseTypeName:
            return False

        if item.slot == 'weapon':
            handedness = 'two_handed' if item.twoHanded else 'one_handed'
            weaponTypes = EQUIPMENT_BASES['weapons'][handedness]

            currentType, currentLevel, currentData = None, None, None
            for wType, tiers in weaponTypes.items():
                if item.baseTypeName in tiers:
                    currentType, currentLevel, currentData = wType, tiers[item.baseTypeName]['minLevel'], tiers[item.baseTypeName]
                    break
            if currentType is None:
                return False

            currentClass = currentData.get('requiredClass')
            candidates = [
                (name, data) for wType, tiers in weaponTypes.items() if wType != currentType
                for name, data in tiers.items()
                if data['minLevel'] == currentLevel and data.get('requiredClass') == currentClass
            ]
            if not candidates:
                return False

            weights = [data.get('weight', 100) for _, data in candidates]
            tierName, tierData = random.choices(candidates, weights=weights, k=1)[0]
            item.baseDamage = Equipment._rollRangeValue(tierData['damageMin'], tierData['damageMax'], item.rarity, item.level)
            item.baseDamage += tierData.get('implicits', {}).get('damage', 0)
            item.damage = item.baseDamage
            item.implicits = dict(tierData.get('implicits', {}))
            item.baseTypeName = tierName
            return True

        if item.slot in ARMOUR_SLOTS:
            poolKey = EQUIPMENT_BASES_KEY.get(item.slot, item.slot)
            defenseTypes = EQUIPMENT_BASES[poolKey]

            currentType, currentLevel, currentData = None, None, None
            for dType, tiers in defenseTypes.items():
                if item.baseTypeName in tiers:
                    currentType, currentLevel, currentData = dType, tiers[item.baseTypeName]['minLevel'], tiers[item.baseTypeName]
                    break
            if currentType is None:
                return False

            currentClass = currentData.get('requiredClass')
            candidates = [
                (name, data, dType) for dType, tiers in defenseTypes.items() if dType != currentType
                for name, data in tiers.items()
                if data['minLevel'] == currentLevel and data.get('requiredClass') == currentClass
            ]
            if not candidates:
                return False

            weights = [data.get('weight', 100) for _, data, _ in candidates]
            tierName, tierData, newType = random.choices(candidates, weights=weights, k=1)[0]
            oldType = currentType
            item.defenseType = newType
            item.baseDefenseValue = Equipment._rollRangeValue(
                tierData['defenseMin'], tierData['defenseMax'], item.rarity, item.level, halveForES=(newType == 'energy_shield')
            )
            item.implicits = dict(tierData.get('implicits', {}))
            item.baseTypeName = tierName

            from scripts.items.affixes import getTieredAffix
            for slot in item.prefixSlots:
                if slot.affix is None or slot.affix.stat != oldType:
                    continue
                version = 'added' if slot.affix.isFlat else 'increased'
                newAffix = getTieredAffix(item.slot, 'prefixes', affixId=f'{version}_{newType}_t{slot.affix.tier}')
                if newAffix is not None:
                    newAffix.rollValue()
                    slot.affix = newAffix

            return True

        if item.slot in ('ring', 'amulet'):
            entries = EQUIPMENT_BASES[item.slot]
            if item.baseTypeName not in entries:
                return False
            currentEntry = entries[item.baseTypeName]
            currentLevel = currentEntry['minLevel']
            currentStat = next(iter(item.implicits)) if item.implicits else None
            currentClass = currentEntry.get('requiredClass')

            candidates = [
                (name, data) for name, data in entries.items()
                if data['minLevel'] == currentLevel and next(iter(data['implicits'])) != currentStat
                and data.get('requiredClass') == currentClass
            ]
            if not candidates:
                return False

            weights = [data.get('weight', 100) for _, data in candidates]
            tierName, tierData = random.choices(candidates, weights=weights, k=1)[0]
            chosenStat = next(iter(tierData['implicits']))
            newImplicits = {chosenStat: Equipment._rollImplicitRange(tierData['implicits'][chosenStat])}
            for extraStat, extraVal in tierData.get('extraImplicits', {}).items():
                newImplicits[extraStat] = Equipment._rollImplicitRange(extraVal) if isinstance(extraVal, dict) else extraVal
            item.implicits = newImplicits
            item.baseTypeName = tierName
            return True

        return False

    def update(self):
        self._statsDirty = True
        self._applyMythicDamageTypeLock()
        self.applyMastery()
        self.recalculateDamage()
        self.recalculateDefenses()
        self.calculateMaxDurability()
        self.calculateEntropyResistance()
        self.calculateTotalEntropy()
        self.calculateValue()

    def _applyMythicDamageTypeLock(self):
        if not self.mythicAffix or self.slot != 'weapon':
            return
        for line in self.mythicAffix.lines:
            if line.effect == 'damage_type_double':
                forcedType = line.meta.get('damage_type')
                if forcedType:
                    self.damageType = forcedType

    def _mythicScalingBonus(self, stat: str) -> float:
        if not self.mythicAffix:
            return 0
        bonus = 0
        for line in self.mythicAffix.lines:
            if line.effect == 'scale_with_item_level' and line.meta.get('stat') == stat:
                cappedLevel = min(self.level, line.meta.get('cap', self.level))
                bonus += cappedLevel * line.values.get('x', 0)
        return bonus

    def recalculateDefenses(self):
        flat = 0
        increased = 0
        mastery = 1 + (self.mastery / 100)

        for affix in self.prefixes + self.destabilisedAffixes:
            if affix.stat == self.defenseType:
                if affix.isFlat:
                    flat += affix.value
                elif affix.isIncreased:
                    increased += affix.value / 100

        flat += self._mythicScalingBonus(self.defenseType)

        self.defenseValue = int(((self.baseDefenseValue + flat) * (1 + increased)) * mastery)

    def recalculateDamage(self):
        flat = 0
        increased = 0
        mastery = 1 + (self.mastery / 100)

        for affix in self.prefixes + self.destabilisedAffixes:
            if affix.stat == 'damage':
                if affix.isFlat:
                    flat += affix.value
                elif affix.isIncreased:
                    increased += affix.value / 100

        flat += self._mythicScalingBonus('damage')

        self.damage = int(((self.baseDamage + flat) * (1 + increased)) * mastery)

    def calculateTotalEntropy(self):
        if self.rarity == ItemRarity.BLANK:
            self.addEntropy(0)
            return
        flat = 0
        increased = 0
        for affix in self.prefixes + self.suffixes:
            if affix.stat == 'entropy':
                if affix.isFlat:
                    flat += affix.value
                elif affix.isIncreased:
                    increased += affix.value / 100

        self.maxEntropy = round((1.0 + flat) * (1 + increased), 4)
        self.addEntropy(0)

    def calculateEntropyResistance(self):
        flat = 0
        for affix in self.prefixes + self.suffixes:
            if affix.stat == 'entropy_resistance':
                if affix.isFlat:
                    flat += affix.value / 100

        self.entropyResistance = min(round(self.baseEntropyResistance + flat, 2), 0.75)
        if self.soulbound:
            self.entropyResistance -= 0.15 #15% resistance reduction from soulbound
        if self.numPreserved > 0:
            self.entropyResistance -= 0.1 * self.numPreserved #10% resistance reduction per preservation rune used

    @staticmethod
    def _generateEquipmentPiece(level: int, slot: str, rarity: ItemRarity, className: str = None, playerName: str = None) -> 'Equipment':
        def getAffixCounts(level, rarity):
            bases = {
                ItemRarity.COMMON: ([1], [1]),
                ItemRarity.UNCOMMON: ([1, 2], [1, 2]),
                ItemRarity.RARE: ([2], [2]),
                ItemRarity.EPIC: ([2, 3], [2, 3]),
                ItemRarity.LEGENDARY: ([3], [3]),
                ItemRarity.MYTHIC: ([3, 3, 4], [3, 3, 4]) # 3 twice for a higher chance of 3, smaller chance of 4
            }
            basePrefixes, baseSuffixes = bases.get(rarity, (1, 1))
            extra = level // 34 # +1 both affix slots every 34 levels
            prefixes = random.choice(basePrefixes) + extra
            suffixes = random.choice(baseSuffixes) + extra
            return prefixes, suffixes

        def calculateTierBias(level, rarity):
            levelBias = min(0.5, level / 200)
            rarityBias = {
                ItemRarity.COMMON: 0.0,
                ItemRarity.UNCOMMON: 0.05,
                ItemRarity.RARE: 0.15,
                ItemRarity.EPIC: 0.25,
                ItemRarity.LEGENDARY: 0.40,
                ItemRarity.MYTHIC: 0.5
            }
            totalBias = levelBias + rarityBias.get(rarity, 0.0)
            return min(1.0, totalBias)

        if slot == 'any':
            slot = random.choice(['weapon', 'head', 'chest', 'legs', 'feet', 'ring', 'amulet'])

        equipment = {
            'slot': slot,
            'rarity': rarity,
            'level': level,
            'durability': 100,
            'maxDurability': 100,
            'prefixes': [],
            'suffixes': [],
            'implicits': {},
            'baseTypeName': None,
            'twoHanded': False,
        }

        defenseType, defenseValue = None, 0
        damageType, baseDamage = None, 0

        if slot in ARMOUR_SLOTS:

            defenseType, defenseValue, implicits, tierName = Equipment._calculateDefenseRoll(slot, level, rarity, className=className)

            equipment['defenseType'] = defenseType
            equipment['defenseValue'] = defenseValue
            equipment['baseDefenseValue'] = defenseValue
            equipment['implicits'] = implicits
            equipment['baseTypeName'] = tierName

        elif slot == 'weapon':
            baseDamage, damageType, implicits, twoHanded, weaponType, tierName = Equipment._calculateDamageRoll(slot, level, rarity, className=className)
            baseDamage += implicits.get('damage', 0)  # fold weapon 'damage' implicit into baseDamage once, here only

            equipment['damage'] = baseDamage
            equipment['baseDamage'] = baseDamage
            equipment['damageType'] = damageType
            equipment['implicits'] = implicits
            equipment['baseTypeName'] = tierName
            equipment['twoHanded'] = twoHanded

        elif slot in ('ring', 'amulet'):
            tierName, implicits = Equipment._pickAccessoryImplicit(slot, level, className)
            equipment['implicits'] = implicits
            equipment['baseTypeName'] = tierName

        elif slot == 'sigil':
            tierName, implicits, sigilType = Equipment._pickSigilImplicit(level, className)
            equipment['implicits'] = implicits
            equipment['baseTypeName'] = tierName
            equipment['sigilType'] = sigilType

        numPrefixes, numSuffixes = getAffixCounts(level, rarity)

        prefixes = []
        suffixes = []
        excludedPrefixIds = set()
        excludedSuffixIds = set()

        equipment['mythicAffix'] = None
        if rarity == ItemRarity.MYTHIC:
            if slot == 'offhand':
                mythicBucket = 'shield'
            elif slot == 'sigil':
                mythicBucket = f"sigil_{equipment['sigilType']}"
            else:
                mythicBucket = slot  # weapon/head/chest/legs/feet/ring/amulet all match their mythic bucket directly
            equipment['mythicAffix'] = rollMythicAffix(mythicBucket, level, rarity)
            if equipment['mythicAffix']:
                for line in equipment['mythicAffix'].lines:
                    if line.effect == 'affix_slot_bonus':
                        bonus = int(line.values.get('x', 0))
                        if line.meta.get('kind') == 'prefix':
                            numPrefixes += bonus
                        else:
                            numSuffixes += bonus
                    elif line.effect == 'damage_type_double':
                        forcedType = line.meta.get('damage_type')
                        if forcedType:
                            equipment['damageType'] = forcedType

        tierBias = calculateTierBias(level, rarity)

        defenseType = equipment.get('defenseType', None)
        if slot == 'weapon':
            affixPoolKey = 'one_handed' if not equipment.get('twoHanded', False) else slot
        elif slot == 'sigil':
            affixPoolKey = f"sigil_{equipment['sigilType']}"
        else:
            affixPoolKey = slot

        for _ in range(numPrefixes):
            affix = rollAffix(affixPoolKey, 'prefixes', level, rarity, excludedPrefixIds, tierBias, defenseType)
            if affix:
                prefixes.append(affix)
                excludedPrefixIds.add(affix.id.split('_t')[0])

        for _ in range(numSuffixes):
            affix = rollAffix(affixPoolKey, 'suffix', level, rarity, excludedSuffixIds, tierBias, defenseType)
            if affix:
                suffixes.append(affix)
                excludedSuffixIds.add(affix.id.split('_t')[0])

        equipment['prefixes'] = prefixes
        equipment['suffixes'] = suffixes

        if 'defenseType' in equipment and equipment.get('defenseValue', 0) > 0:
            currentDefenseType = equipment['defenseType']
            flatBonus = 0
            increasedBonus = 0

            for affix in prefixes: #only prefixes can increase defenses
                if affix.stat == currentDefenseType:
                    if affix.isFlat:
                        flatBonus += affix.value
                    elif affix.isIncreased:
                        increasedBonus += affix.value / 100
            
            baseDefense = equipment['defenseValue']
            equipment['defenseValue'] = int((baseDefense + flatBonus) * (1 + increasedBonus))

        elif 'damage' in equipment and equipment.get('damage', 0) > 0:
            currentDamge = equipment['damage']
            flatBonus = 0
            increasedBonus = 0

            for affix in prefixes: #only prefixes increase damage
                if affix.stat == 'damage':
                    if affix.isFlat:
                        flatBonus += affix.value
                    elif affix.isIncreased:
                        increasedBonus += affix.value / 100

            equipment['damage'] = round((currentDamge + flatBonus) * (1 + increasedBonus))

        if equipment['slot'] in ARMOUR_SLOTS:
            e = Equipment(
                equipment['slot'],
                equipment['rarity'],
                {'defenseType': equipment['defenseType'], 'baseDefenseValue': equipment['baseDefenseValue'], 'defenseValue': equipment['defenseValue']},
                {},
                equipment['implicits'],
                equipment['prefixes'],
                equipment['suffixes'],
                numPrefixes,
                numSuffixes,
                equipment['level'],
                baseTypeName=equipment['baseTypeName']
            )
        elif equipment['slot'] == 'weapon':
            e = Equipment(
                equipment['slot'],
                equipment['rarity'],
                {},
                {'damage': equipment['damage'], 'baseDamage': equipment['baseDamage'], 'damageType': equipment['damageType'], 'twoHanded': equipment['twoHanded']},
                equipment['implicits'],
                equipment['prefixes'],
                equipment['suffixes'],
                numPrefixes,
                numSuffixes,
                equipment['level'],
                baseTypeName=equipment['baseTypeName']
            )
        else:
            e = Equipment(
                equipment['slot'],
                equipment['rarity'],
                {},
                {},
                equipment['implicits'],
                equipment['prefixes'],
                equipment['suffixes'],
                numPrefixes,
                numSuffixes,
                equipment['level'],
                baseTypeName=equipment['baseTypeName']
            )

        e.mythicAffix = equipment.get('mythicAffix')
        if e.mythicAffix:
            e._generateName()  # __init__ generated the name before mythicAffix was assigned

        e.update()
        e.durability = e.maxDurability

        if playerName is not None:
            reportItem(e, playerName)

        return e

    @staticmethod
    def _generateBlankEquipmentPiece(level: int, slot: str, className: str = None, playerName: str = None) -> 'Equipment':
        if slot == 'any':
            slot = random.choice(['weapon', 'head', 'chest', 'legs', 'feet', 'ring', 'amulet'])

        baseTypeName = None
        twoHanded = False
        defenseType, defenseValue = None, 0
        damageType, baseDamage = None, 0
        implicits = {}

        if slot in ARMOUR_SLOTS:
            defenseType, defenseValue, implicits, baseTypeName = Equipment._calculateDefenseRoll(slot, level, ItemRarity.BLANK, className=className)
        elif slot == 'weapon':
            baseDamage, damageType, implicits, twoHanded, _, baseTypeName = Equipment._calculateDamageRoll(slot, level, ItemRarity.BLANK, className=className)
            baseDamage += implicits.get('damage', 0)  # fold weapon 'damage' implicit into baseDamage once, here only - matches _generateEquipmentPiece
        elif slot in ('ring', 'amulet'):
            baseTypeName, implicits = Equipment._pickAccessoryImplicit(slot, level, className)
        elif slot == 'sigil':
            baseTypeName, implicits, _ = Equipment._pickSigilImplicit(level, className)

        e = Equipment(
            slot,
            ItemRarity.BLANK,
            {'defenseType': defenseType, 'defenseValue': defenseValue, 'baseDefenseValue': defenseValue},
            {'damage': baseDamage, 'baseDamage': baseDamage, 'damageType': damageType, 'twoHanded': twoHanded},
            implicits,
            [], [],
            4, 4,
            level,
            maxEntropy=float('inf'),
            baseTypeName=baseTypeName,
        )
        e.update()
        e.durability = e.maxDurability

        if playerName is not None:
            reportItem(e, playerName)

        return e

    def _generateName(self):
        if self.rarity == ItemRarity.BLANK and getattr(self, 'blankCuratedHand', None) is None:
            # unrevealed - just the base item name (e.g. "Axe"), no rarity/affix naming yet
            self.name = f"[blank]{self.baseTypeName or self.slot.title()}[/blank]"
            return

        typePrefixes = {
            'physical': 'Brutal',
            'fire': 'Blazing',
            'cold': 'Frozen',
            'lightning': 'Storming',
            'dark': 'Corrupt',
            'holy': 'Radiant',
            'arcane': 'Mystic',
            'earth': 'Stone',
            'chaos': 'Chaotic',
            'ethereal': 'Phasing',
            'psychic': 'Imaginary'
        }

        prefixAffixes: List[Affix] = []
        for slot in self.prefixSlots:
            if slot.affix:
                prefixAffixes.append(slot.affix)
        suffixAffixes: List[Affix] = []
        for slot in self.suffixSlots:
            if slot.affix:
                suffixAffixes.append(slot.affix)

        prefix = ""
        if len(prefixAffixes) > 0:
            highestPrefixAffix = max(prefixAffixes, key=lambda a: a.tier)
            prefix = f"{highestPrefixAffix.name} "
        suffix = ""
        if len(suffixAffixes) > 0:
            highestSuffixAffix = max(suffixAffixes, key=lambda a: a.tier)
            suffix = f" {highestSuffixAffix.name}"

        if hasattr(self, 'destabilisedAffixes') and len(self.destabilisedAffixes) > 0:
            affix = random.choice(self.destabilisedAffixes)
            afName = affix.name
            if 'of' in afName:
                suffix = f' {afName}'
            else:
                prefix = f'{afName} '

        if self.soulbound:
            affix = [s.affix for s in self.prefixSlots + self.suffixSlots if s.soulbound][0]
            afName = f'[gold3 bold]{affix.name}[/gold3 bold]'
            if affix.kind == 'prefix':
                prefix = f'{afName} '
            else:
                suffix = afName

        if getattr(self, 'mythicAffix', None):
            afName = f'[plum4 bold]{self.mythicAffix.name}[/plum4 bold]'
            if self.mythicAffix.kind == 'prefix':
                prefix = f'{afName} '
            else:
                suffix = f' {afName}'

        damage = ""
        if hasattr(self, 'damageType'):
            if self.damageType:
                damage = f"{typePrefixes[self.damageType]} "
        
        rarity = self.rarity.value.title()
        slot = f" {self.baseTypeName}" if getattr(self, 'baseTypeName', None) else f" {self.slot.title()}"

        name = f"[{self.rarity.value}]{prefix}{damage}{rarity}{slot}{suffix}[/{self.rarity.value}]"
        self.name = name

    def compareTo(self, other: Optional['Equipment']) -> str:
        """'Other' is the new equipment piece, self is the current equipment piece"""
        if self.slot != other.slot:
            return f"[error][bold]ERROR:[/bold] Selected items do not have the same base types.[/error]"

        def diff(newStat, oldStat) -> tuple[int, str, str]:
            change = round(newStat - oldStat, 2)
            symbol = "[+]" if change > 0 else "[-]"
            colour = "success" if change > 0 else "error"
            return change, symbol, colour

        if not other:
            return f"\nNEW: {self.name}\n"
        comparison = ""
        comparison += f"\n [cyan bold]Current:[/cyan bold] {other.name}\n"
        comparison += f"\n [gold1 bold]New:[/gold1 bold] {self.name}\n"
        comparison += "\n[bold yellow3]Changes:[/bold yellow3]" if self.slot not in ['ring', 'amulet'] else ""
        # compare each stat
        oldStats = other.stats.copy()
        newStats = self.stats.copy()

        if self.slot in ARMOUR_SLOTS:
            newDef = self.defenseValue
            oldDef = other.defenseValue
            change, symbol, colour = diff(newDef, oldDef)
            if other.defenseType == self.defenseType:
                dType = self.defenseType.replace('_', ' ').title()
                comparison += f"\n[{colour}]{symbol} {change} {dType}[/{colour}]"
            else: # different defense types
                nType = self.defenseType.replace('_', ' ').title()
                oType = other.defenseType.replace('_', ' ').title()
                comparison += f"\n[success] [+] {self.defenseValue} {nType}[/success] | [error] [-] {other.defenseValue} {oType}[/error]"

        if self.slot == 'weapon':
            newDtype = self.damageType
            oldDtype = other.damageType
            change, symbol, colour = diff(self.damage, other.damage)
            if newDtype != oldDtype:
                comparison += f"\n[{colour}] {symbol} {change} Damage[/{colour}]"
                if newDtype is not None and oldDtype is not None:
                    comparison += f"\n[success] [+] Damage Type: {newDtype}[/success] | [error] [-] Damage Type: {oldDtype}[/error]"
                elif newDtype is None and oldDtype is not None:
                    comparison += f"\n[error] [-] Damage Type: {oldDtype}[/error]"
                elif newDtype is not None and oldDtype is None:
                    comparison += f"\n[success] [+] Damage Type: {newDtype}[/success]"

        newStats = [a for a in newStats if a.stat not in ['damage', 'armour', 'energy_shield', 'evasion']]
        oldStats = [a for a in oldStats if a.stat not in ['damage', 'armour', 'energy_shield', 'evasion']]

        if len(newStats) > 0:
            comparison += "\n[bold green3 underline]Gains:[/bold green3 underline]"
            newStats = {a.stat.replace('_', ' ').title(): a.value for a in newStats
                        if not ((self.slot == 'weapon' and a.stat == 'damage')
                        or (self.slot in ARMOUR_SLOTS and a.stat in ['armour', 'evasion', 'energy_shield'] and not a.stat.isGlobal))
                        }
            for k, v in newStats.items(): # k = stat, v = value
                comparison += f"\n[success] [+] {v} {k}[/success]"
        console.print()
        if len(oldStats) > 0:
            comparison += "\n[bold red3 underline]Losses:[/bold red3 underline]"
            oldStats = {a.stat.replace('_', ' ').title(): a.value for a in oldStats
                        if not ((self.slot == 'weapon' and a.stat == 'damage')
                        or (self.slot in ARMOUR_SLOTS and a.stat in ['armour', 'evasion', 'energy_shield'] and not a.stat.isGlobal))
                        }
            for k, v in oldStats.items():
                comparison += f"\n[error] [-] {v} {k}[/error]"

        return comparison

    def takeDamage(self, amount: int):
        durabilityLoss = max(1, amount // 10) #1 durability loss per 10 damage
        self.durability = max(0, self.durability - durabilityLoss)
        if self.durability <= 0:
            console.print(f"  - {self.name} is broken and needs repair.")

    def repair(self, amount: int = None):
        if amount is None:
            self.durability = self.maxDurability
        else:
            self.durability = min(self.durability + amount, self.maxDurability)
        self.maxDurability = int(self.maxDurability)
        self.durability = int(self.durability)

    def getStatBonuses(self, stat: str) -> Tuple[int, float, float]:
        totalBonus = self.implicits.get(stat, 0)
        totalIncrease = 0
        globalIncrease = 0

        for affix in self.stats:
            if affix.stat == stat:
                if affix.isGlobal and affix.isPercent and affix.stat in (stat, 'defenses'):
                    globalIncrease += affix.value / 100
                elif affix.stat and affix.isFlat:
                    totalBonus += affix.value
                elif affix.stat and affix.isPercent:
                    totalIncrease += affix.value / 100

        # damage/defenseType are handled in recalculateDamage/recalculateDefenses instead,
        # since those stats aren't read back out through getStatBonuses by the aggregation loop
        if stat not in ('damage', self.defenseType):
            totalBonus += self._mythicScalingBonus(stat)

        return totalBonus, totalIncrease, globalIncrease

    def getDamageType(self) -> str | bool:
        return self.damageType

    def addEntropy(self, amount: float = 0.0):
        if self.entropyPreserved and amount > 0:
            console.print('[green1]Your Preservation Rune prevents your item from gaining entropy![/green1]')
            self.entropyPreserved = False
            amount = 0
        amount = round(amount, 4)
        self.calculateEntropyResistance()
        resistance = self.entropyResistance
        effective = amount * (1 - resistance)
        self.entropy = min(self.maxEntropy, round(self.entropy + effective, 4))
        if effective > 0:
            printError(f"\n{self.name} gained {effective} entropy! Current Entropy: {self.entropy} / {self.maxEntropy}\n")
        if self.entropyLocked:
            printError(f"\n{self.name} has become too unstable! It is no longer modifiable. (Entropy Locked)\n")
