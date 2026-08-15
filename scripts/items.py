from enum import Enum
from typing import Dict, Optional, List, Any, Tuple
import random
from .styles import console, printError
from .affixes import rollAffix, Affix
from .mythicAffixes import rollMythicAffix

class ItemRarity(Enum):
    COMMON = "common"
    UNCOMMON = "uncommon"
    RARE = "rare"
    EPIC = "epic"
    LEGENDARY = "legendary"
    MYTHIC = "mythic"
    BLANK = "blank"
    QUEST = "quest"

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

    def ___str__(self):
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

ARMOUR_SLOTS = ['head', 'chest', 'legs', 'feet']

RARITY_VALUES = {
    "common": 1,
    "uncommon": 2,
    "rare": 3,
    "epic": 4,
    "legendary": 5,
    "mythic": 10,
    "quest": 1
}

RARITY_SERIALS = {
    "common": ItemRarity.COMMON,
    "uncommon": ItemRarity.UNCOMMON,
    "rare": ItemRarity.RARE,
    "epic": ItemRarity.EPIC,
    "legendary": ItemRarity.LEGENDARY,
    "mythic": ItemRarity.MYTHIC,
    "blank": ItemRarity.BLANK,
    "quest": ItemRarity.QUEST
}

VALUE_MULTIPLIER = {
    ItemRarity.COMMON: 1,
    ItemRarity.UNCOMMON: 2,
    ItemRarity.RARE: 3,
    ItemRarity.EPIC: 4,
    ItemRarity.LEGENDARY: 5,
    ItemRarity.MYTHIC: 10,
}

ENTROPY_RESISTANCE = {
    ItemRarity.COMMON: 0.0,
    ItemRarity.UNCOMMON: 0.05,
    ItemRarity.RARE: 0.125,
    ItemRarity.EPIC: 0.20,
    ItemRarity.LEGENDARY: 0.35,
    ItemRarity.MYTHIC: 0.5,
}

MAX_PRESERVATIONS = {
    ItemRarity.COMMON: 1,
    ItemRarity.UNCOMMON: 1,
    ItemRarity.RARE: 2,
    ItemRarity.EPIC: 2,
    ItemRarity.LEGENDARY: 3,
    ItemRarity.MYTHIC: 4,
}

class ItemType(Enum):
    RESOURCE = "resource"
    CONSUMABLE = "consumable"
    EQUIPMENT = "equipment"
    QUEST = "quest"
    DUNGEON = "dungeon"

TYPE_SERIALS = {
    "resource": ItemType.RESOURCE,
    "consumable": ItemType.CONSUMABLE,
    "equipment": ItemType.EQUIPMENT,
    "quest": ItemType.QUEST
}

CONSUMABLES = {
    "Small Health Potion": 20,
    "Medium Health Potion": 40,
    "Large Health Potion": 80,
    "Superior Health Potion": 180,
    "Godly Health Potion": 400
}

DAMAGE_TYPES = [
    'physical',
    'fire', 'cold', 'lightning', 'earth',
    'dark', 'holy', 'arcane',
    'ethereal', 'psychic', 'chaos'
]

class Item:
    def __init__(self, name: str, itemType: ItemType, rarity: ItemRarity = ItemRarity.COMMON,
                 value: int = 1, stackable: bool = False, maxStack: int = 1):
        self.name = name
        self.itemType = itemType
        self.rarity = rarity
        self.value = value * VALUE_MULTIPLIER[rarity]
        self.stackable = stackable
        self.maxStack = maxStack

    def __rich__(self):
        return self.__str__()

    def __str__(self):
        return f"{self.name} ({self.rarity.value})"
    
    def serialise(self):
        return {
            "name": self.name,
            "itemType": self.itemType.value,
            "rarity": self.rarity.value,
            "value": self.value,
            "stackable": self.stackable,
            "maxStack": self.maxStack,
        }
    
    @classmethod
    def deserialise(cls, data: Dict):
        cls = Item(
            data.get('name', 'Item'),
            data.get('itemType'),
            RARITY_SERIALS[data.get('rarity', 'common')],
            data.get('value', 0),
            data.get('stackable', False),
            data.get('maxStack', 1)
        )
        cls.itemType = TYPE_SERIALS[data.get('itemType')]
        return cls

class Resource(Item):
    def __init__(self, name: str, rarity: ItemRarity = ItemRarity.COMMON, value: int = 1):
        super().__init__(name, ItemType.RESOURCE, rarity, value, stackable=True, maxStack=999)

class Equipment(Item):
    def __init__(self, slot: str, rarity: ItemRarity = ItemRarity.COMMON,
                 defenses: dict[str, int] = {}, damages: dict[str, Any] = {},
                 prefixes: List[Affix] = None, suffixes: List[Affix] = None, numPrefixes: int = 1, numSuffixes: int = 1,
                 level: int = 1, maxEntropy: float | None = None):

        itemType = ItemType.EQUIPMENT

        if not hasattr(self, 'value'):
            value = 500 * RARITY_VALUES[rarity.value]
        else:
            value = self.value

        super().__init__("", itemType, rarity, value)
        self.slot = slot  # weapon, head, chest, legs, feet, ring, amulet
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
        self._generateName()

        self.entropy = 0
        self.entropyPreserved = False
        self.numPreserved = 0
        self.maxPreservations = MAX_PRESERVATIONS[rarity]
        self.maxEntropy = maxEntropy if maxEntropy is not None else 1.0
        self.baseEntropyResistance = ENTROPY_RESISTANCE[rarity]
        self.destabilised = False
        self.destabilisedAffixes = []

        self.mastery = 0

        self.update()
        self.baseMaxDurability = self.maxDurability
        self.durability = self.maxDurability

    @property
    def prefixes(self) -> List[Affix]:
        return [s.affix for s in self.prefixSlots if s.affix]
    
    @property
    def suffixes(self) -> List[Affix]:
        return [s.affix for s in self.suffixSlots if s.affix]

    @property
    def stats(self) -> List[Affix]:
        return self.prefixes + self.suffixes

    @property
    def locked(self) -> bool:
        for affix in self.suffixes + self.prefixes:
            if affix.locked:
                return True
        return False

    @property
    def entropyLocked(self) -> bool:
        return self.entropy >= self.maxEntropy

    @property
    def soulbound(self) -> bool:
        for slot in self.prefixSlots + self.suffixSlots:
            if slot.soulbound:
                return True
        return False

    @property
    def preservable(self) -> bool:
        if self.numPreserved >= self.maxPreservations:
            return False
        return True

    def serialise(self):
        temp = super().serialise()
        temp['slot'] = self.slot
        temp['prefixSlots'] = [s.serialise() for s in self.prefixSlots]
        temp['suffixSlots'] = [s.serialise() for s in self.suffixSlots]
        temp['level'] = self.level

        temp['durability'] = self.durability
        temp['maxDurability'] = self.maxDurability
        temp['baseMaxDurability'] = self.baseMaxDurability

        temp['defenseType'] = self.defenseType
        temp['defenseValue'] = self.defenseValue
        temp['baseDefenseValue'] = self.baseDefenseValue

        temp['damage'] = self.damage
        temp['baseDamage'] = self.baseDamage
        temp['damageType'] = self.damageType

        temp['entropy'] = self.entropy
        temp['entropyPreserved'] = self.entropyPreserved
        temp['maxEntropy'] = self.maxEntropy
        temp['baseEntropyResistance'] = self.baseEntropyResistance
        temp['entropyResistance'] = self.entropyResistance
        temp['entropyLocked'] = self.entropyLocked
        temp['destabilised'] = self.destabilised
        temp['destabilisedAffixes'] = [
            {
                'name': da.name,
                'stat': da.stat,
                'value': da.value,
                'isPercent': da.isPercent
            } for da in getattr(self, 'destabilisedAffixes', [])
        ]

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
                'damageType': data.get('damageType', None)
            },
            prefixes,
            suffixes,
            len(prefixSlots), len(suffixSlots),
            data.get('level', 1)
        )
        i = super().deserialise(data)

        e.prefixSlots = prefixSlots
        e.suffixSlots = suffixSlots

        e.name = i.name
        e.itemType = i.itemType
        e.value = i.value
        e.rarity = i.rarity
        e.stackable = i.stackable or False
        e.maxStack  = i.maxStack or 1

        e.entropy = data.get('entropy', 0)
        e.entropyPreserved = data.get('entropyPreserved', False)
        e.maxEntropy = data.get('maxEntropy', 1.0)
        e.baseEntropyResistance = data.get('baseEntropyResistance', ENTROPY_RESISTANCE[e.rarity])
        e.entropyResistance = data.get('entropyResistance', e.baseEntropyResistance)
        e.destabilised = data.get('destabilised', False)
        from crafting.destabilisationRune import DestabilisedAffix
        e.destabilisedAffixes = []
        for daData in data.get('destabilisedAffixes', []):
            da = DestabilisedAffix(
                name=daData['name'],
                stat=daData['stat'],
                value=daData['value'],
                isPercent=daData['isPercent']
            )
            e.destabilisedAffixes.append(da)

        e.update()
        e.baseMaxDurability = data.get('baseMaxDurability', e.maxDurability)
        e.durability = data.get('durability', e.maxDurability)

        return e

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
        masteryString = f" | [gold1]Mastery:[/gold1] {self.mastery}%"
        return f"{destabilisedString}{self.name} | [bold]Durability:[/bold] {self.durability} / {self.maxDurability}{masteryString}{entropyString}{damageString}{defenseString}\n{stat_string}{corruptedString}"

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

    def gainMastery(self, amount: int):
        if self.mastery >= 20: # max mastery is 20
            return
        maxGain = 20 - self.mastery
        gained = amount
        if amount > maxGain:
            gained = maxGain
        if gained > 0:
            self.mastery += gained
            console.print(f"[bold]Gained [gold1]{gained}% Mastery[/gold1] on {self.name}. New Amount: [gold1]{self.mastery} / 20[/gold1][/bold]")
            self.update()

    def applyMastery(self):
        for slot in self.prefixSlots + self.suffixSlots:
            if slot.affix is not None:
                slot.affix.mastery  = self.mastery

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

        return excludedPre, excludedSuf

    @staticmethod
    def _calculateDefenseRoll(slot: str, level: int, rarity: ItemRarity) -> List[str, int]:
        if slot not in ARMOUR_SLOTS:
            return None, 0
        
        defenseTypes = ['armour', 'evasion', 'energy_shield']
        selectedType = random.choice(defenseTypes)

        defenseRanges = {
            'head': {
            'armour': (8, 15),
            'evasion': (11, 18),
            'energy_shield': (5, 10)
            },
            'chest': {
                'armour': (16, 30),
                'evasion': (19, 33),
                'energy_shield': (9, 19)
            },
            'legs': {
                'armour': (16, 30),
                'evasion': (19, 33),
                'energy_shield': (9, 19)
            },
            'feet': {
                'armour': (8, 15),
                'evasion': (11, 18),
                'energy_shield': (5, 10)
            }
        }

        baseMin, baseMax = defenseRanges[slot][selectedType]
        baseMin += level // 3
        baseMax += level

        rarityMultipliers = {
            ItemRarity.COMMON: 1,
            ItemRarity.UNCOMMON: 1.2,
            ItemRarity.RARE: 1.5,
            ItemRarity.EPIC: 1.8,
            ItemRarity.LEGENDARY: 2.2,
        }
        multiplier = rarityMultipliers.get(rarity, 1) + level / 100

        minVal = int(baseMin * multiplier)
        maxVal = int(baseMax * multiplier)
        defenseValue = random.randint(minVal, maxVal)

        return selectedType, defenseValue

    @staticmethod
    def _calculateDamageRoll(slot: str, level: int, rarity: ItemRarity) -> List[int, str | None]:
        if slot != 'weapon':
            return 0, None

        baseMin = random.randint(2, 4) + int(level * 2 / 3) - (1 if level < 3 else 0)
        baseMax = random.randint(6, 8) + int(level * 4 / 3) - (random.randint(1, 2) if level < 5 else 0)

        rarityMultipliers = {
            ItemRarity.COMMON: 1,
            ItemRarity.UNCOMMON: 1.2,
            ItemRarity.RARE: 1.5,
            ItemRarity.EPIC: 1.8,
            ItemRarity.LEGENDARY: 2.2,
        }
        multiplier = rarityMultipliers.get(rarity, 1) + level / 100

        minVal = int(baseMin * multiplier)
        maxVal = int(baseMax * multiplier)
        damage = random.randint(minVal, maxVal)

        if random.random() <= 0.3:
            damageType = random.choice(DAMAGE_TYPES)
        else:
            damageType = None
        
        return damage, damageType

    def update(self):
        self.applyMastery()
        self.recalculateDamage()
        self.recalculateDefenses()
        self.calculateMaxDurability()
        self.calculateEntropyResistance()
        self.calculateTotalEntropy()

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

        self.damage = int(((self.baseDamage + flat) * (1 + increased)) * mastery)

    def calculateTotalEntropy(self):
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
    def _generateEquipmentPiece(level: int, slot: str, rarity: ItemRarity, className: str = None) -> 'Equipment':
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
            'suffixes': []
        }

        defenseType, defenseValue = None, 0
        damageType, baseDamage = None, 0

        if slot in ARMOUR_SLOTS:

            defenseType, defenseValue = Equipment._calculateDefenseRoll(slot, level, rarity)

            equipment['defenseType'] = defenseType
            equipment['defenseValue'] = defenseValue
            equipment['baseDefenseValue'] = defenseValue

        elif slot == 'weapon':
            baseDamage, damageType = Equipment._calculateDamageRoll(slot, level, rarity)

            equipment['damage'] = baseDamage
            equipment['baseDamage'] = baseDamage
            equipment['damageType'] = damageType

        numPrefixes, numSuffixes = getAffixCounts(level, rarity) 

        prefixes = []
        suffixes = []
        excludedPrefixIds = set()
        excludedSuffixIds = set()

        mythicPre = 0
        mythicSuf = 0
        if rarity == ItemRarity.MYTHIC:
            mythicType = random.choice(['prefix', 'suffix'])
            mythicAffix = rollMythicAffix(slot, mythicType, level, rarity, set(), defenseType)
            if mythicType == 'prefix':
                mythicPre = 1
                prefixes.append(mythicAffix)
                excludedPrefixIds.add(mythicAffix.id.split('_t')[0])
            else:
                mythicSuf = 1
                suffixes.append(mythicAffix)
                excludedSuffixIds.add(mythicAffix.id.split('_t')[0])

        tierBias = calculateTierBias(level, rarity)

        defenseType = equipment.get('defenseType', None)

        for _ in range(numPrefixes - mythicPre):
            affix = rollAffix(slot, 'prefixes', level, rarity, excludedPrefixIds, tierBias, defenseType)
            if affix:
                prefixes.append(affix)
                excludedPrefixIds.add(affix.id.split('_t')[0])
        
        for _ in range(numSuffixes - mythicSuf):
            affix = rollAffix(slot, 'suffix', level, rarity, excludedSuffixIds, tierBias, defenseType)
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

        if 'defenseType' in equipment and equipment.get('defenseValue', 0) > 0:
            e = Equipment(
                equipment['slot'],
                equipment['rarity'],
                {'defenseType': equipment['defenseType'], 'baseDefenseValue': equipment['baseDefenseValue'], 'defenseValue': equipment['defenseValue']},
                {},
                equipment['prefixes'],
                equipment['suffixes'],
                numPrefixes,
                numSuffixes,
                equipment['level']
            )
        elif 'damageType' in equipment and equipment.get('damage', 0) > 0:
            e = Equipment(
                equipment['slot'],
                equipment['rarity'],
                {},
                {'damage': equipment['damage'], 'baseDamage': equipment['baseDamage'], 'damageType': equipment['damageType']},
                equipment['prefixes'],
                equipment['suffixes'],
                numPrefixes,
                numSuffixes,
                equipment['level'],
            )
        else:
            e = Equipment(
                equipment['slot'],
                equipment['rarity'],
                {},
                {},
                equipment['prefixes'],
                equipment['suffixes'],
                numPrefixes,
                numSuffixes,
                equipment['level']
            )

        e.update()
        e.durability = e.maxDurability

        return e

    def _generateName(self):
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
            if self.rarity == ItemRarity.MYTHIC:
                for a in prefixAffixes:
                    if a.isMythic:
                        prefix = f"{a.name} "
                        break
            if prefix == "":
                highestPrefixAffix = max(prefixAffixes, key=lambda a: a.tier)
                prefix = f"{highestPrefixAffix.name} "
        suffix = ""
        if len(suffixAffixes) > 0:
            if self.rarity == ItemRarity.MYTHIC:
                for a in suffixAffixes:
                    if a.isMythic:
                        suffix = f" {a.name}"
                        break
            if suffix == "":
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

        damage = ""
        if hasattr(self, 'damageType'):
            if self.damageType:
                damage = f"{typePrefixes[self.damageType]} "
        
        rarity = self.rarity.value.title()
        slot = f" {self.slot.title()}"

        name = f"[{self.rarity.value}]{prefix}{damage}{rarity}{slot}{suffix}[/{self.rarity.value}]"
        self.name = name

    def compareTo(self, other: Optional['Equipment']) -> str:
        """'Other' is the current equipment piece, self is the new equipment piece"""
        if self.slot != other.slot:
            return f"[error][bold]ERROR:[/bold] Selected items do not have the same base types.[/error]"

        def diff(newStat, oldStat) -> tuple[int, str, str]:
            change = round(newStat - oldStat, 2)
            symbol = "[+]" if change > 0 else "[-]"
            colour = "success" if change > 0 else "error"
            return change, symbol, colour

        if not other:
            return f"\nNEW: {self.name}\n    {self._formatStats()}"
        comparison = ""
        comparison += f"\n [cyan]Current:[/cyan] {other.name}"
        comparison += f"\n   {other._formatStats()}"
        comparison += f"\n [cyan]New:[/cyan] {self.name}"
        comparison += f"\n   {self._formatStats()}"
        comparison += "\n[bold yellow3]Changes:[/bold yellow3]" if self.slot not in ['ring', 'amulet'] else ""
        # compare each stat
        oldStats = other.stats.copy()
        newStats = self.stats.copy()

        if self.slot in ARMOUR_SLOTS:
            newDef = self.defenseValue
            oldDef = other.defenseValue
            change, symbol, colour = diff(newDef, oldDef)
            if other.defenseType == self.defenseType:
                comparison += f"\n[{colour}]{symbol} {change} {self.defenseType}[/{colour}]"
            else: # different defense types
                nType = self.defenseType.replace('_', ' ').title()
                oType = other.defenseType.replace('_', ' ').title()
                comparison += f"\n[success] [+] {self.defenseValue} {nType}[/success] | [error] [-] {other.defenseValue} {oType}[/error]"

        if self.slot == 'weapon':
            newDtype = self.damageType
            oldDtype = other.damageType
            change, symbol, colour = diff(self.damage, other.damage)
            comparison += f"\n[{colour}] {symbol} {change} Damage[/{colour}]"
            if newDtype is not None and oldDtype is not None:
                comparison += f"\n[success] [+] Damage Type: {newDtype}[/success] | [error] [-] Damage Type: {oldDtype}[/error]"
            elif newDtype is None and oldDtype is not None:
                comparison += f"\n[error] [-] Damage Type: {oldDtype}[/error]"
            elif newDtype is not None and oldDtype is None:
                comparison += f"\n[success] [+] Damage Type: {newDtype}[/success]"

        if len(newStats) > 0:
            comparison += "\n[bold green3 underline]Gains:[/bold green3 underline]"
            newStats = {a.stat.replace('_', ' ').title(): a.value for a in newStats
                        if not ((self.slot == 'weapon' and a.stat == 'damage')
                        or (self.slot in ARMOUR_SLOTS and a.stat in ['armour', 'evasion', 'energy_shield']))
                        }
            for k, v in newStats.items(): # k = stat, v = value
                comparison += f"\n[success] [+] {v} {k}[/success]"
        if len(oldStats) > 0:
            comparison += "\n[bold red3 underline]Losses:[/bold red3 underline]"
            oldStats = {a.stat.replace('_', ' ').title(): a.value for a in oldStats
                        if not ((self.slot == 'weapon' and a.stat == 'damage')
                        or (self.slot in ARMOUR_SLOTS and a.stat in ['armour', 'evasion', 'energy_shield']))
                        }
            for k, v in oldStats.items():
                comparison += f"\n[error] [-] {v} {k}[/error]"

        return comparison

    def _formatStats(self) -> str:
        statStrings = []
        for stat in self.stats:
            statStrings.append(f"{stat}")
        return "\n- ".join(statStrings)

    def takeDamage(self, amount: int):
        durabilityLoss = max(1, amount // 10) #1 durability loss per 10 damage
        self.durability = max(0, self.durability - durabilityLoss)
        if self.durability == 0:
            console.print(f"  - {self.name} is broken and needs repair.")

    def repair(self, amount: int = None):
        if amount is None:
            self.durability = self.maxDurability
        else:
            self.durability = min(self.durability + amount, self.maxDurability)

    def getStatBonuses(self, stat: str) -> Tuple[int, float, float]:
        totalBonus = 0
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

class Consumable(Item):
    def __init__(self, name: str, rarity: ItemRarity = ItemRarity.COMMON, value: int = 1,
                 effect: Dict = None):
        super().__init__(name, "consumable", rarity, value, stackable=True, maxStack=999)
        self.effect = effect or {}
        self.value = effect.get('heal', 20) * 50

    def use(self, target):
        if "heal" in self.effect:
            oldHealth = target._health
            target._health = min(target._health + self.effect['heal'], target._maxHealth)
            actualHeal = target._health - oldHealth
            console.print(f"Healed for {actualHeal} HP")
            return True
        return False

    def serialise(self):
        current = super().serialise()
        current['effect'] = self.effect
        return current

    @classmethod
    def deserialise(cls, data):
        cls = Consumable(
            data.get('name', 'Consumable'),
            data.get('rarity', ItemRarity.COMMON),
            data.get('value', 0)
        )
        i = super().deserialise(data)

        cls.itemType = i.itemType
        cls.stackable = i.stackable
        cls.maxStack  = i.maxStack

        cls.effect = data.get('effect', {})

        return cls

class QuestItem(Item):
    def __init__(self, name: str, value: int = 1):
        super().__init__(name, "quest", ItemRarity.QUEST, value, stackable=False, maxStack=1)

DUNGEON_RARITY_MULTIPLIERS = {
    ItemRarity.COMMON: {'difficulty': 1.0, 'rewards': 1.0},
    ItemRarity.UNCOMMON: {'difficulty': 1.2, 'rewards': 1.5},
    ItemRarity.RARE: {'difficulty': 1.5, 'rewards': 2.0},
    ItemRarity.EPIC: {'difficulty': 2.0, 'rewards': 3.0},
    ItemRarity.LEGENDARY: {'difficulty': 3, 'rewards': 5.0}
}

class DungeonMap(Item):
    def __init__(self, name: str, level: int, waves: int, tier: int,
                 rarity: ItemRarity = ItemRarity.COMMON, description: str = ""):
        super().__init__(name, ItemType.DUNGEON, rarity, 1, False, 1)
        self.level = level
        self.waves = waves
        self.tier = tier
        self.description = description

    def serialise(self):
        temp = super().serialise()
        temp['level'] = self.level
        temp['waves'] = self.waves
        temp['tier'] = self.tier
        temp['description'] = self.description

        return temp
    
    @classmethod
    def deserialise(cls, data):
        cls = DungeonMap(
            data.get('name', 'Dungeon Map'),
            data.get('level', 1),
            data.get('waves', 1),
            data.get('tier', 1),
            data.get('rarity', ItemRarity.COMMON),
            data.get('description', "")
        )

        i = super().deserialise(data)

        cls.itemType = i.itemType
        cls.value = i.value
        cls.stackable = i.stackable or False
        cls.maxStack  = i.maxStack or 1

        return cls
    
    def getDifficultyMultiplier(self):
        return DUNGEON_RARITY_MULTIPLIERS[self.rarity]['difficulty']
    
    def getRewardMultiplier(self):
        return DUNGEON_RARITY_MULTIPLIERS[self.rarity]['rewards']

RESOURCES = {
    "wood": Resource("Wood", ItemRarity.COMMON, 1),
    "stone": Resource("Stone", ItemRarity.COMMON, 1),
    "cloth": Resource("Cloth", ItemRarity.COMMON, 2),
    "herbs": Resource("Herbs", ItemRarity.COMMON, 2),
    "leather": Resource("Leather", ItemRarity.UNCOMMON, 2),
    "iron_ore": Resource("Iron Ore", ItemRarity.UNCOMMON, 3),
    "bone": Resource("Bone", ItemRarity.UNCOMMON, 5),
    "crystal": Resource("Crystal", ItemRarity.RARE, 10),
    "soul": Resource("Soul", ItemRarity.RARE, 10),
    "mana_essence": Resource("Mana Essence", ItemRarity.EPIC, 15),
    "ancient_wood" : Resource("Ancient Wood", ItemRarity.EPIC, 30),
    "diamond": Resource("Diamond", ItemRarity.EPIC, 30),
    "dragon_scale": Resource("Dragon Scale", ItemRarity.LEGENDARY, 50),
    "ascended_essence": Resource("Ascended Essence", ItemRarity.LEGENDARY, 75)
}

RARITY_WEIGHTS = {
    ItemRarity.COMMON: 75,
    ItemRarity.UNCOMMON: 20,
    ItemRarity.RARE: 10,
    ItemRarity.EPIC: 4,
    ItemRarity.LEGENDARY: 1,
    ItemRarity.MYTHIC: 0.2,
}

def rollRarity(level: int = 0) -> ItemRarity:
    weights = RARITY_WEIGHTS.copy()
    if level > 0:
        shiftAmount = level / 100
        commonReduction = RARITY_WEIGHTS[ItemRarity.COMMON] * shiftAmount * 0.5
        weights[ItemRarity.COMMON] = max(10, RARITY_WEIGHTS[ItemRarity.COMMON] - commonReduction)
        weights[ItemRarity.UNCOMMON] += commonReduction * 0.3
        weights[ItemRarity.RARE] += commonReduction * 0.3
        weights[ItemRarity.EPIC] += commonReduction * 0.25
        weights[ItemRarity.LEGENDARY] += commonReduction * 0.15
        if level >= 60:
            weights[ItemRarity.MYTHIC] += commonReduction * 0.03
        else:
            weights[ItemRarity.MYTHIC] = 0

    totalWeight = round(sum(weights.values()))
    roll = random.randint(1, totalWeight)
    currentWeight = 0
    
    for rarity, weight in weights.items():
        currentWeight += weight
        if roll <= currentWeight:
            return rarity
        
    return ItemRarity.COMMON

class LootTable:
    def __init__(self):
        self.resources: Dict[str, tuple] = {}  # {resource_name: (min_amount, max_amount, drop_chance)}
        self.equipmentPool: list = []  # List of possible equipment
        self.runeDrops = []
        self.extras = {}

    def __rich__(self):
        return self.__str__()

    def __str__(self):
        output = ""
        
        if self.resources:
            output += "\n === Resources ==="
            for resource, (minAmt, maxAmt, dropChance) in self.resources.items():
                output += f"\n  - {resource}: {minAmt}-{maxAmt} | {dropChance * 100:.0f}% chance"
        
        if self.equipmentPool:
            output += "\n\n === Equipment ==="
            for equipment, dropChance in self.equipmentPool:
                output += f"\n  - {equipment.name} (Lv.{equipment.level}) | {dropChance * 100:.0f}% chance"

        if self.runeDrops:
            output += "\n\n === Runes ==="

        if self.extras:
            output += "\n\n === Extras ==="
            for name, data in self.extras.items():
                output += f"\n  - {name} : {data}"
        
        return output if output else "\n  No loot available"
        
    def addResource(self, resourceName: str, minAmount: int, maxAmount: int, dropChance: float = 1.0):
        self.resources[resourceName] = (minAmount, maxAmount, min(1.0, dropChance))
    
    def addEquipment(self, equipment: Equipment, dropChance: float = 0.1):
        self.equipmentPool.append((equipment, min(1.0, dropChance)))

    def addRune(self, category: str, runeType: str, dropChance: float = 0.8):
        self.runeDrops.append((category, runeType, dropChance))

    def addExtra(self, name, data, dictVersion=None):
        """Use dict version to send multiple otherwise use name/data"""
        if dictVersion:
            for k, v in dictVersion:
                self.extras[k] = v
        else:
            self.extras[name] = data

    def rollLoot(self) -> tuple[Dict[str, int], List[Equipment], List[str, str]]:
        droppedResources = {}
        droppedEquipment = []
        droppedRunes = []

        for resourceName, (minAmt, maxAmt, dropChance) in self.resources.items():
            if random.random() <= dropChance:
                amount = random.randint(minAmt, maxAmt)
                droppedResources[resourceName] = amount

        for equipment, dropChance in self.equipmentPool:
            if random.random() <= dropChance:
                droppedEquipment.append(equipment)

        for category, runeType, runeChance in self.runeDrops:
            if random.random() <= dropChance:
                droppedRunes.append((category, runeType))

        return droppedResources, droppedEquipment, droppedRunes

...