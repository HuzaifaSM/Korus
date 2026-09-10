from enum import Enum
from typing import Dict, List
import random
from scripts.styles import console

class ItemRarity(Enum):
    COMMON = "common"
    UNCOMMON = "uncommon"
    RARE = "rare"
    EPIC = "epic"
    LEGENDARY = "legendary"
    MYTHIC = "mythic"
    BLANK = "blank"
    QUEST = "quest"

    def __lt__(self, other: ItemRarity) -> bool:
        if self.value == 'common' and other.value != 'common':
            return True
        elif self.value ==  'uncommon':
            if other.value in ['common', 'uncommon']:
                return False
            return True
        elif self.value == 'rare':
            if other.value in ['common', 'uncommon', 'rare']:
                return False
            return True
        elif self.value == 'epic':
            if other.value in ['common', 'uncommon', 'rare', 'epic']:
                return False
            return True
        elif self.value == 'legendary':
            if other.value not in ['mythic', 'blank']:
                return False
            return True
        elif self.value in ['mythic', 'blank']: # nothing greater than mythic/blank
            return False
        elif self.value == 'quest': # quest, all greater
            return True

    def __le__(self, other: ItemRarity) -> bool:
        if self.value == other.value:
            return True
        return self < other

    def __gt__(self, other: ItemRarity) -> bool:
        if self.value == 'common' and other.value != 'common':
            return False
        elif self.value ==  'uncommon':
            if other.value in ['common', 'uncommon']:
                return True
            return False
        elif self.value == 'rare':
            if other.value in ['common', 'uncommon', 'rare']:
                return True
            return False
        elif self.value == 'epic':
            if other.value in ['common', 'uncommon', 'rare', 'epic']:
                return True
            return False
        elif self.value in ['legendary', 'mythic', 'blank']: # legendary, mythic, blank > all but mythic/blank
            if other.value not in ['mythic', 'blank']:
                return True
            return False
        elif self.value == 'quest': # quest, all greater
            return False

    def __ge__(self, other: ItemRarity) -> bool:
        if self.value == other.value:
            return True
        return self > other

    def __add__(self, value: int) -> ItemRarity:
        if value < 0:
            return self - value
        if self.value == 'quest':
            return [ItemRarity.QUEST]
        if value == 0:
            return RARITY_SERIALS[self.value]
        if self.value in ['mythic', 'blank']:
            return RARITY_SERIALS[self.value]

        if self.value == 'common':
            if value == 1:
                return ItemRarity.UNCOMMON
            elif value == 2:
                return ItemRarity.RARE
            elif value == 3:
                return ItemRarity.EPIC
            elif value == 4:
                return ItemRarity.LEGENDARY
        
        elif self.value == 'uncommon':
            if value == 1:
                return ItemRarity.RARE
            elif value == 2:
                return ItemRarity.EPIC
            elif value == 3:
                return ItemRarity.LEGENDARY

        elif self.value == 'rare':
            if value == 1:
                return ItemRarity.EPIC
            elif value == 2:
                return ItemRarity.LEGENDARY

        elif self.value == 'epic':
            if value == 1:
                return ItemRarity.LEGENDARY

        return ItemRarity.MYTHIC

    def __sub__(self, value: int) -> ItemRarity:
        if value < 0:
            return self + value
        if self.value == 'quest':
            return [ItemRarity.QUEST]
        elif self.value == 'common':
            return RARITY_SERIALS[self.value]
        if value == 0:
            return RARITY_SERIALS[self.value]

        if self.value == 'rare':
            if value == 1:
                return ItemRarity.UNCOMMON

        elif self.value == 'epic':
            if value == 1:
                return ItemRarity.RARE
            elif value == 2:
                return ItemRarity.UNCOMMON

        elif self.value == 'legendary':
            if value == 1:
                return ItemRarity.EPIC
            elif value == 2:
                return ItemRarity.RARE
            elif value == 3:
                return ItemRarity.UNCOMMON

        elif self.value in ['mythic', 'blank']:
            if value == 1:
                return ItemRarity.LEGENDARY
            elif value == 2:
                return ItemRarity.EPIC
            elif value == 3:
                return ItemRarity.RARE
            elif value == 4:
                return ItemRarity.UNCOMMON

        return ItemRarity.COMMON

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
    ItemRarity.UNCOMMON: 1.5,
    ItemRarity.RARE: 2,
    ItemRarity.EPIC: 3.5,
    ItemRarity.LEGENDARY: 4.5,
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

class Item:
    def __init__(self, name: str, itemType: ItemType, rarity: ItemRarity = ItemRarity.COMMON,
                 value: int = 1, stackable: bool = False, maxStack: int = 1):
        self.name = name
        self.itemType = itemType
        self.rarity = rarity
        self.value = value
        self.stackable = stackable
        self.maxStack = maxStack

    def __rich__(self):
        return self.__str__()

    def __str__(self):
        return f"[rarity]{self.name}[/rarity] [dim]Max Stack:[/dim] {self.maxStack}"

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
    def __init__(self, name: str, use: str):
        super().__init__(name, ItemType.RESOURCE, ItemRarity.QUEST, value=10, stackable=True, maxStack=999)
        self.use = use
        """the location this item is used in, i.e. 'campfire', 'forge', 'market', 'player'"""

class Consumable(Item):
    def __init__(self):
        super().__init__('Healing Vial', ItemType.CONSUMABLE, ItemRarity.COMMON, 0, False, 1)
        self.healPercent = 0.1
        self.maxUses = 2
        self.usesRemaining = 2

    def updateValue(self, playerLevel: int):
        if playerLevel < 15:
            self.name = 'Healing Vial'
            self.healPercent = 0.1
            self.maxUses = 2
            self.usesRemaining = 2
            self.rarity = ItemRarity.COMMON
        elif playerLevel < 30:
            self.name = 'Healing Potion'
            self.healPercent = 0.16
            self.maxUses = 2
            self.usesRemaining = 2
            self.rarity = ItemRarity.UNCOMMON
        elif playerLevel < 40:
            self.name = 'Healing Flask'
            self.healPercent = 0.25
            self.maxUses = 3
            self.usesRemaining = 3
            self.rarity = ItemRarity.RARE
        elif playerLevel < 60:
            self.name = 'Grand Flask of Healing'
            self.healPercent = 0.35
            self.maxUses = 4
            self.usesRemaining = 4
            self.rarity = ItemRarity.EPIC
        elif playerLevel < 85:
            self.name = 'Renowned Goblet of Healing'
            self.healPercent = 0.5
            self.maxUses = 4
            self.usesRemaining = 4
            self.rarity = ItemRarity.LEGENDARY
        else:
            self.name = 'Elixir of Immortality'
            self.healPercent = 0.75
            self.maxUses = 5
            self.usesRemaining = 5
            self.rarity = ItemRarity.MYTHIC

    def serialise(self):
        temp = super().serialise()
        temp['healPercent'] = self.healPercent
        temp['maxUses'] = self.maxUses
        temp['usesRemaining'] = self.usesRemaining
        return temp

    @classmethod
    def deserialise(cls, data):
        cls = Consumable()
        cls.name = data.get('name', cls.name)
        cls.healPercent = data.get('healPercent', cls.healPercent)
        cls.maxUses = data.get('maxUses', cls.maxUses)
        cls.usesRemaining = data.get('usesRemaining', cls.usesRemaining)
        cls.rarity = RARITY_SERIALS[data.get('rarity', 'common')]
        return cls

    @property
    def useable(self) -> bool:
        return self.usesRemaining > 0

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
    "wood": Resource("Wood", 'Campfire'), "stone": Resource("Stone", 'Campfire'),
    "brick": Resource("Brick", "Forge"), "metal": Resource("Metal", "Forge"),
    "leather": Resource("Leather", "Market"), "cloth": Resource("Cloth", "Market"),
    "soul": Resource("Soul", "Player"), "ascended_essence": Resource("Ascended Essence", "Player"),
}

RARITY_WEIGHTS = {
    ItemRarity.COMMON: 75,
    ItemRarity.UNCOMMON: 20,
    ItemRarity.RARE: 10,
    ItemRarity.EPIC: 4,
    ItemRarity.LEGENDARY: 1,
    ItemRarity.MYTHIC: 0.2,
}

def _shiftRarityWeights(rarity: float, weights: Dict[ItemRarity, float]) -> Dict[ItemRarity, float]:
    if rarity == 1.0:
        return weights # no change

    DISTRIBUTION = {
        ItemRarity.COMMON: -0.2,
        ItemRarity.UNCOMMON: 0.2,
        ItemRarity.RARE: 0.5,
        ItemRarity.EPIC: 0.4,
        ItemRarity.LEGENDARY: 0.1,
        ItemRarity.MYTHIC: 0,
    }
    if weights[ItemRarity.MYTHIC] > 0:
        DISTRIBUTION[ItemRarity.LEGENDARY] -= 0.05
        DISTRIBUTION[ItemRarity.MYTHIC] += 0.05

    shiftAmount = rarity - 1.0 # positive = rarer, negative = more common

    newWeights = dict(weights)
    commonShift = weights[ItemRarity.COMMON] * abs(DISTRIBUTION[ItemRarity.COMMON]) * shiftAmount
    newWeights[ItemRarity.COMMON] = max(weights[ItemRarity.COMMON] * 0.05, weights[ItemRarity.COMMON] - commonShift)
    commonShift = weights[ItemRarity.COMMON] - newWeights[ItemRarity.COMMON] # actual amount moved, after the floor clamp

    giveShares = {r: w for r, w in DISTRIBUTION.items() if r != ItemRarity.COMMON}
    shareTotal = sum(giveShares.values())

    for r, share in giveShares.items():
        newWeights[r] = max(0.0, weights[r] + commonShift * (share / shareTotal))

    return newWeights

def rollRarity(level: int = 0, rarity: float = 1.0) -> ItemRarity:
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

    weights = _shiftRarityWeights(rarity, weights)

    totalWeight = sum(weights.values())
    roll = random.uniform(0, totalWeight)
    currentWeight = 0.0

    for r, weight in weights.items():
        currentWeight += weight
        if roll <= currentWeight:
            return r

    return list(weights.keys())[-1]

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
    
    def addEquipment(self, equipment, dropChance: float = 0.1):
        self.equipmentPool.append((equipment, min(1.0, dropChance)))

    def addRune(self, category: str, runeType: str, dropChance: float = 0.8):
        self.runeDrops.append((category, runeType, min(1.0, dropChance)))

    def addExtra(self, name, data, dictVersion=None):
        """Use dict version to send multiple otherwise use name/data"""
        if dictVersion:
            for k, v in dictVersion:
                self.extras[k] = v
        else:
            self.extras[name] = data

    def rollLoot(self) -> tuple[Dict[str, int], List, List[str, str]]:
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

        for category, runeType, dropChance in self.runeDrops:
            if random.random() <= dropChance:
                droppedRunes.append((category, runeType))

        return droppedResources, droppedEquipment, droppedRunes

...