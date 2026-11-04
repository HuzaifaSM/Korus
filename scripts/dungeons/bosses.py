import random
from typing import Dict, List, Tuple

from ..enemies.enemy import createEnemy, rollEncounterClasses, EnemyClass, EnemyRarity
from .modifiers import applyEnemyModifiers

BOSS_TEMPLATES = [
    {"name": "The Hollow King", "title": "a husk of a ruler, still crowned in rust and rot"},
    {"name": "Vessel of the Deep", "title": "something that was drowned, and did not stay that way"},
    {"name": "The Gravekeeper", "title": "tends a garden of bones no one else can see"},
    {"name": "Ashen Warden", "title": "burned once, and decided it liked the feeling"},
    {"name": "The Unbound", "title": "wears the chains it broke as trophies"},
    {"name": "Matriarch of Thorns", "title": "every step she takes, something else starts growing"},
]

MAX_ADDS_BY_TIER = {1: 1, 2: 2, 3: 2, 4: 3, 5: 3}
BOSS_BASE_MULTIPLIER = 1.5  # flat toughness a boss has over a normal LEGENDARY-rarity enemy of the same level

def rollAddCount(tier: int) -> int:
    maxAdds = MAX_ADDS_BY_TIER[min(5, max(1, tier))]
    return random.randint(0, maxAdds)

def bossMultiplierFor(numAdds: int) -> float:
    """The boss itself gets proportionally weaker as more adds join, so total encounter threat
    stays roughly constant regardless of how many adds were rolled."""
    return max(1.15, 1.6 - (numAdds * 0.15))

def createBossEncounter(level: int, tier: int, difficulty: float, rarity: float, quantity: float,
                         playerClassName: str = None, playerName: str = None,
                         effects: Dict = None, currentFloor: int = 0) -> Tuple[List, Dict]:
    """Returns (enemies, template) - enemies[0] is always the boss, the rest are its adds."""
    effects = effects or {}
    numAdds = rollAddCount(tier)
    groupSize = numAdds + 1

    template = random.choice(BOSS_TEMPLATES)
    boss = createEnemy(level, difficulty, rarity, quantity, playerClassName, playerName,
                        enemyClass=EnemyClass.ATTACKER, groupSize=1, forcedRarity=EnemyRarity.LEGENDARY)
    boss._name = template['name']
    boss.isBoss = True

    multiplier = bossMultiplierFor(numAdds) * BOSS_BASE_MULTIPLIER
    boss._baseHealth = int(boss._baseHealth * multiplier)
    boss._baseDamage = int(boss._baseDamage * multiplier)
    applyEnemyModifiers(boss, effects, currentFloor)
    boss._recalculateStats(False)
    boss._health = boss._maxHealth

    enemies = [boss]
    if numAdds > 0:
        addLevel = max(1, level - random.randint(2, 5))
        for addClass in rollEncounterClasses(numAdds):
            add = createEnemy(addLevel, difficulty, rarity, quantity, playerClassName, playerName,
                               enemyClass=addClass, groupSize=groupSize)
            applyEnemyModifiers(add, effects, currentFloor)
            add._health = add._maxHealth
            enemies.append(add)

    return enemies, template
