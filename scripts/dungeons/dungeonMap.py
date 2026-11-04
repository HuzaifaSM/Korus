import random
from typing import Optional

from ..items.items import Item, ItemType, ItemRarity, RARITY_SERIALS, rollRarity

DUNGEON_RARITY_MULTIPLIERS = {
    ItemRarity.COMMON: {'difficulty': 1.0, 'rewards': 1.0},
    ItemRarity.UNCOMMON: {'difficulty': 1.2, 'rewards': 1.5},
    ItemRarity.RARE: {'difficulty': 1.5, 'rewards': 2.0},
    ItemRarity.EPIC: {'difficulty': 2.0, 'rewards': 3.0},
    ItemRarity.LEGENDARY: {'difficulty': 3.0, 'rewards': 5.0},
}

class DungeonMap(Item):
    def __init__(self, name: str, level: int, floorCount: int, tier: int,
                 rarity: ItemRarity = ItemRarity.COMMON, description: str = ""):
        super().__init__(name, ItemType.DUNGEON, rarity, 1, False, 1)
        self.level = level
        self.floorCount = floorCount
        self.tier = tier
        self.description = description

    def serialise(self):
        temp = super().serialise()
        temp['level'] = self.level
        temp['floorCount'] = self.floorCount
        temp['tier'] = self.tier
        temp['description'] = self.description
        return temp

    @classmethod
    def deserialise(cls, data):
        return DungeonMap(
            data.get('name', 'Dungeon Map'),
            data.get('level', 1),
            data.get('floorCount', data.get('waves', 6)),  # 'waves' kept as a fallback for saves made before the rework
            data.get('tier', 1),
            RARITY_SERIALS.get(data.get('rarity', 'common'), ItemRarity.COMMON),
            data.get('description', "")
        )

    def getDifficultyMultiplier(self) -> float:
        return DUNGEON_RARITY_MULTIPLIERS[self.rarity]['difficulty']

    def getRewardMultiplier(self) -> float:
        return DUNGEON_RARITY_MULTIPLIERS[self.rarity]['rewards']

FIRST_NAMES = [
    'Cursed', 'Forgotten', 'Twisted', 'Corrupted', 'Abyssal',
    'Forsaken', 'Voiden', 'Shattered', 'Dark', 'Winding',
    'Tormenting', 'Lifeless', 'Malicious', 'Vile', 'Ominous'
]

SECOND_NAMES = [
    'Catacombs', 'Temple', 'Depths', 'Ruins', 'Sanctuary',
    'Shrine', 'Chambers', 'Halls', 'Monastery', 'Crypt',
    'Manor', 'Estate', 'Bastion', 'Warren', 'Maze'
]

DUNGEON_MIN_ENEMY_LEVEL = 10  # nothing below this level can ever drop a map

def _rollDungeonMapRarity(enemyLevel: int) -> ItemRarity:
    rarity = rollRarity(enemyLevel)
    if rarity not in DUNGEON_RARITY_MULTIPLIERS:  # MYTHIC/BLANK aren't meaningful dungeon tiers - clamp down
        rarity = ItemRarity.LEGENDARY
    return rarity

def generateDungeonMap(enemyLevel: int, playerLevel: int) -> Optional[DungeonMap]:
    """Rolled off the enemy that dropped it (rarity/chance), but scaled to fit the player when it's eventually run."""
    if enemyLevel < DUNGEON_MIN_ENEMY_LEVEL:
        return None

    dropChance = min(0.08, 0.015 + enemyLevel * 0.0005)
    if random.random() > dropChance:
        return None

    rarity = _rollDungeonMapRarity(enemyLevel)
    tier = rarity.num  # COMMON..LEGENDARY -> 1..5, conveniently already the tier scale we want

    level = max(DUNGEON_MIN_ENEMY_LEVEL, playerLevel + random.randint(-1, 3))
    floorCount = 5 + tier  # 6 floors at tier 1, up to 10 floors at tier 5

    name = f"{random.choice(FIRST_NAMES)} {random.choice(SECOND_NAMES)}"

    return DungeonMap(
        name=name,
        level=level,
        floorCount=floorCount,
        tier=tier,
        rarity=rarity,
        description=f"Level {level} | {floorCount} Floors | Tier {tier}",
    )
