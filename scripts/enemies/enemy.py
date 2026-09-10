import random
from typing import Dict, Optional
from ..entities import Entity, SIGIL_SLOTS
from ..items.items import ItemRarity, LootTable, RESOURCES, rollRarity
from ..items.equipment import Equipment
from ..runeDrops import rollRuneDrops
from ..abilities import ENEMY_ABILITIES, EnemyAbility, BasicAttack
from ..styles import console
from .enemyAi import EnemyAI
from enum import Enum

class EnemyRarity(Enum):
    COMMON = "common"
    RARE = "rare"
    EPIC = "epic"
    LEGENDARY = "legendary"

class EnemyClass(Enum):
    ATTACKER = "attacker"
    SUPPORT = "support"

class EnemySubclass(Enum):
    # attacker
    BRUISER = "bruiser" # mostly basic attacks, high base damage
    DEBILITATOR = "debilitator" # mostly debuff-heavy attacks
    CHAMPION = "champion" # smarter AI, uses buffs then big hits
    FANATIC = "fanatic" # ability spam, no basic attacks
    # support
    HEALER = "healer" # focuses on healing
    STANDARD_BEARER = "standard_bearer" # focuses on buffing
    TANK = "tank" # taunts player to force single-target to attack it, high health

ATTACKER_SUBCLASSES = [EnemySubclass.BRUISER, EnemySubclass.DEBILITATOR, EnemySubclass.CHAMPION, EnemySubclass.FANATIC]
SUPPORT_SUBCLASSES = [EnemySubclass.HEALER, EnemySubclass.STANDARD_BEARER, EnemySubclass.TANK]

SUBCLASS_WEIGHTS = {
    EnemySubclass.BRUISER: 10, EnemySubclass.DEBILITATOR: 8, EnemySubclass.CHAMPION: 4, EnemySubclass.FANATIC: 10,
    EnemySubclass.HEALER: 10, EnemySubclass.STANDARD_BEARER: 10, EnemySubclass.TANK: 6
}

def rollEnemyClass() -> EnemyClass:
    return EnemyClass.SUPPORT if random.random() < 0.3 else EnemyClass.ATTACKER

def rollEnemySubclass(enemyClass: EnemyClass, rarity: EnemyRarity) -> Optional[EnemySubclass]:
    if rarity == EnemyRarity.COMMON:
        return None
    if random.random() < 0.3: # 70% chance for subclass
        return None
    pool = ATTACKER_SUBCLASSES if enemyClass == EnemyClass.ATTACKER else SUPPORT_SUBCLASSES
    weights = [SUBCLASS_WEIGHTS[s] for s in pool]
    return random.choices(pool, weights, k=1)[0]

ENEMY_RARITY_WEIGHTS = {
    EnemyRarity.COMMON: 70,
    EnemyRarity.RARE: 22,
    EnemyRarity.EPIC: 7,
    EnemyRarity.LEGENDARY: 1,
}

ENEMY_RARITY_AI_DIFFICULTY = {
    EnemyRarity.COMMON: 0.3,
    EnemyRarity.RARE: 0.55,
    EnemyRarity.EPIC: 0.75,
    EnemyRarity.LEGENDARY: 0.95
}

ENEMY_RARITY_STAT_MULT = {
    EnemyRarity.COMMON: 1.0,
    EnemyRarity.RARE: 1.25,
    EnemyRarity.EPIC: 1.6,
    EnemyRarity.LEGENDARY: 2.2,
}

def rollEnemyRarity() -> EnemyRarity:
    totalWeight = sum(ENEMY_RARITY_WEIGHTS.values())
    roll = random.uniform(0, totalWeight)
    currentWeight = 0.0
    for rarity, weight in ENEMY_RARITY_WEIGHTS.items():
        currentWeight += weight
        if roll <= currentWeight:
            return rarity
    return EnemyRarity.COMMON

NAMES = [
    "Beast",
    "Wraith",
    "Hunter",
    "Brute",
    "Mage",
    "Sentinel",
    "Stalker",
    "Construct",
    "Spirit"
]

ELEMENTAL_NAME = {
    'physical': 'Titanic', 'fire': 'Flaming', 'lightning': 'Charged', 'earth': 'Grounded',
    'dark': 'Vile', 'holy': 'Divine', 'arcane': 'Magic', 'cold': 'Glacial'
}

DAMAGE_TYPES = ['physical', 'fire', 'cold', 'lightning', 'dark', 'holy', 'arcane', 'earth']

class Enemy(Entity):
    def __init__(self, name: str, level: int = 1, health: int = 20, damage: int = 3, critChance: float = 0.05, critMulti: float = 1.5, damageType: str = "physical",
                 speed: float = 0.8, lootTable: LootTable = None, rarityModifier: float = 1.0, quantityModifier: float = 1.0, playerClass: str = None, playerName: str = None,
                 rarity: EnemyRarity = None, enemyClass: EnemyClass = None, enemySubclass: EnemySubclass = None):
        self.rarity = rarity or rollEnemyRarity()
        self.aiDifficulty = ENEMY_RARITY_AI_DIFFICULTY[self.rarity]
        statMult = ENEMY_RARITY_STAT_MULT[self.rarity]

        resolvedClass = enemyClass or rollEnemyClass()
        resolvedSubclass = enemySubclass or rollEnemySubclass(resolvedClass, self.rarity)

        scaledHealth = round((health + (level - 1) * random.randint(2, 5)) * statMult)
        scaledDamage = round((damage + ((level - 1) / 2.5) * random.uniform(1, 2.2)) * statMult)
        scaledSpeed = round(speed + ((level + random.randint(-10, 10)) / 100), 2)
        scaledCritChance = round(critChance + (random.randint(0, 5) + level / 10) / 100, 2)
        scaledCritMulti = round(critMulti + (random.randint(5, 15) + level / 5) / 100, 2)

        super().__init__(scaledHealth, scaledDamage, scaledCritChance, scaledCritMulti, damageType, scaledSpeed, name)
        # must be set AFTER super().__init__() - Entity.__init__ unconditionally resets
        # self.className/self._ascendancy (to None, since Enemy doesn't pass them through)
        self.className = resolvedClass
        self._ascendancy = resolvedSubclass
        self._abilities: Dict[str, EnemyAbility] = {"Basic Attack": BasicAttack()}
        self._level = level
        self._experienceReward = max(level * 10, level * (level // 3 + random.randint(5, 15 + level // 5)))
        self._lootTable = lootTable or LootTable()

        self.rarityModifer = rarityModifier
        self.quantityModifier = quantityModifier

        self.consumable.updateValue(max(1, min(55, level) - 15)) # cannot have better than healing flasks

        self.ai = EnemyAI(self)

        self.tortureStacks = 0
        self.phasedTurns = 0
        self.cursedTurns = 0
        self.cursedLastTurn = False
        self.earthboundTurns = 0
        self.earthboundLastTurn = False
        self.corruption = 0
        self.ruin = 0
        self.bloodSpike = 0
        self.necrosis = 0
        self.crush = 0
        self.shameTurns = 0
        self.marked = False
        self.carved = 0
        self.taunting = False
        self.tauntTurns = 0

        self._generateEquipment(playerClass, playerName)
        self._generateInventory()
        self._recalculateStats(False)

    @property
    def tainted(self):
        return (not self.desecrated and self.ruin >= 5)

    @property
    def desecrated(self):
        return self.ruin >= 10

    def applyNecrosis(self):
        if self.necrosis < 10:
            self.necrosis += 1
            self._stats['Temporary']['speed'] -= 0.02
            console.print(f"[asc_necrose]{self._name} has gained 1 Necrosis![/asc_necrose]")

    def removeNecrosis(self, stacks: int = None) -> int:
        """Removes up to `stacks` Necrosis (all of it if omitted), reverting its speed debuff. Returns stacks removed."""
        stacks = self.necrosis if stacks is None else min(stacks, self.necrosis)
        if stacks > 0:
            self.necrosis -= stacks
            self._stats['Temporary']['speed'] += 0.02 * stacks
        return stacks

    def applyCrush(self):
        if self.crush < 3:
            self.crush += 1
            self._stats['Temporary']['increased_armour'] -= 15
            console.print(f"[asc_colossus]{self._name} has gained 1 Crush![/asc_colossus]")

    def removeCrush(self, stacks: int = None) -> int:
        """Removes up to `stacks` Crush (all of it if omitted), reverting its armour debuff. Returns stacks removed."""
        stacks = self.crush if stacks is None else min(stacks, self.crush)
        if stacks > 0:
            self.crush -= stacks
            self._stats['Temporary']['increased_armour'] += 15 * stacks
        return stacks

    def applyShame(self):
        if self.shameTurns == 0:
            self._stats['Temporary']['speed'] -= 0.1
        console.print(f"[asc_sovereign]{self._name} has been afflicted with 2 turns of Shame![/asc_sovereign]")
        self.shameTurns = 2

    def unmark(self):
        self.marked = False

    def applyCarved(self):
        if self.carved < 3:
            self.carved += 1
            self._stats['Temporary']['crit_chance'] -= 0.05
            self._stats['Temporary']['increased_defenses'] -= 5
            console.print(f"[asc_butcher]{self._name} has gained 1 Carved![/asc_butcher]")

    def applyPhased(self):
        if self.phasedTurns == 0:
            self._stats['Temporary']['speed'] -= 0.2
        self.phasedTurns = 3

    def applyTaunt(self, turns: int = 1):
        self.taunting = True
        self.tauntTurns = max(self.tauntTurns, turns)
        console.print(f"[warning]{self._name} demands your attention - single-target abilities will be forced onto it![/warning]")

    def _recalculateStats(self, doPrint = True, inCombat = False):
        super()._recalculateStats(doPrint, inCombat)
        if self.ruin > 0:
            self._stats['Temporary']['crit_chance'] -= self.ruin * 0.01
            self._stats['Temporary']['all'] -= self.ruin

    def onAttack(self, damageDealt, damageType, target, combatManager, ability, crit):
        damageDealt, damageType = super().onAttack(damageDealt, damageType, target, combatManager, ability, crit)

        damageDealt = int(damageDealt * (1 - (self.tortureStacks * 0.02)))

        if self.shameTurns > 0:
            damageDealt = int(damageDealt * 0.9)

        if self.marked:
            damageDealt = int(damageDealt * 1.1)

        if self.phasedTurns > 0:
            damageDealt = int(damageDealt * 0.9)

        return damageDealt, damageType

    def onHit(self, damageTaken, damageType, crit, attacker , combatManager):
        damageTaken, damageType = super().onHit(damageTaken, damageType, crit, attacker, combatManager)

        damageTaken = int(damageTaken * (1 + (self.tortureStacks * 0.02)))

        if damageType == 'chaos':
            damageTaken = int(damageTaken * (1 + (self.corruption * 0.02)))

        if self.ruin > 0:
            if self.tainted:
                damageTaken = int(damageTaken * 1.1)
            elif self.desecrated:
                damageTaken = int(damageTaken * 1.2)

        damageTaken = int(damageTaken * 1 + (self.necrosis * 0.03))

        if self.marked:
            damageTaken = int(damageTaken * 1.25)

        return damageTaken, damageType

    def onCrit(self, targets, combatManager, critDamage):
        if self.tortureStacks > 0:
            t = targets[0]
            if not t.radiance:
                devasStr = ""
                if t.devastation:
                    hpLoss = int(self._maxHealth * 0.01 * self.tortureStacks)
                    self.damage(hpLoss, 'true')
                    devasStr = f" Your Devastation caused them to lose {hpLoss} Health!"
                self.tortureStacks = 0
                console.print(f"[asc_mindbreaker]{self._name} has removed all their Torture stacks!{devasStr}[/asc_mindbreaker]")

        return critDamage

    def onTurnStart(self, combatManager=None):
        if self.tauntTurns > 0:
            self.tauntTurns -= 1
            if self.tauntTurns == 0:
                self.taunting = False

        if self.phasedTurns > 0:
            self.phasedTurns -= 1
            if self.phasedTurns == 0:
                self._stats['Temporary']['speed'] += 0.2
        
        if self.cursedTurns > 0:
            if not self.cursedLastTurn:
                self._stats['Temporary']['all'] -= 15
                self.cursedLastTurn = True
            self.cursedTurns -= 1
            if self.cursedTurns == 0:
                self._stats['Temporary']['all'] += 15
        else:
            self.cursedLastTurn = False
        
        if self.earthboundTurns > 0:
            if not self.earthboundLastTurn:
                self._stats['Temporary']['speed'] -= 0.2
                self.earthboundLastTurn = True
            self.earthboundTurns -= 1
            if self.earthboundTurns == 0:
                self._stats['Temporary']['speed'] += 0.2

        if self.corruption > 0:
            allEnemies = [u.entity for u in combatManager.getUnitsInTeam('enemy') if u.entity.corruption < 10]
            if allEnemies and random.random() < (self.corruption * 0.1):
                enemy = random.choice(allEnemies)
                enemy.corruption += 1

        if self.shameTurns > 0:
            self.shameTurns -= 1
            if self.shameTurns == 0:
                self._stats['Temporary']['speed'] += 0.1

        super().onTurnStart(combatManager)

    def displayLoot(self):
        console.print(self._lootTable)

    def _slotIsFull(self, slot: str) -> bool:
        if slot == 'sigil':
            return all(self._equipment[s] is not None for s in SIGIL_SLOTS[:self.unlockedSigilSlots])
        return self._equipment[slot] is not None

    def _generateEquipment(self, playerClass: str = None, playerName: str = None):
        slots = ['head', 'chest', 'legs', 'feet', 'weapon', 'amulet', 'ring', 'offhand', 'sigil']
        maxEquipment = max(1, min(4, self._level // 15)) if self._level < 100 else 5
        maxEquipment = min(len(slots), max(1, round(maxEquipment * self.quantityModifier)))
        numEquipped = 0
        dropChance = {
            ItemRarity.COMMON: 0.3 + round(self._level / 500, 4),
            ItemRarity.UNCOMMON: 0.2 + round(self._level / 600, 4),
            ItemRarity.RARE: 0.125 + round(self._level / 700, 4),
            ItemRarity.EPIC: 0.05 + round(self._level / 900, 4),
            ItemRarity.LEGENDARY: 0.015 + round(self._level / 1200, 4)
        }
        if self._level >= 60:
            dropChance[ItemRarity.MYTHIC] = 0.003 + round(self._level / 1500, 4)

        if self._level > 20:
            for slot in slots:
                if numEquipped >= maxEquipment:
                    break

                equipChance = min(0.75, 0.15 + (self._level / 40))

                if random.random() < equipChance:
                    rarity = rollRarity(self._level, self.rarityModifer) # rarity bonus based on level
                    equipment = Equipment._generateEquipmentPiece(self._level, slot, rarity, playerClass, playerName)
                    self.equip(equipment, False)

                    finalDropChance = min(0.95, dropChance.get(rarity, 0.3))
                    self._lootTable.addEquipment(equipment, finalDropChance)
                    numEquipped += 1

        elif self._level > 10: # rules for enemies level 11-20: guaranteed 1-2 equipment pieces, unable to roll legendary equipment
            numEq = random.choices([1, 2], weights=[2, 1], k=1)[0]
            numEq = min(len(slots), max(1, round(numEq * self.quantityModifier)))
            for _ in range(numEq):
                slot = random.choice(slots)
                while self._slotIsFull(slot):
                    slot = random.choice(slots)
                rarity = None
                while rarity in [None, ItemRarity.LEGENDARY, ItemRarity.MYTHIC]:
                    rarity = rollRarity(self._level, self.rarityModifer)
                equipment = Equipment._generateEquipmentPiece(self._level, slot, rarity, playerClass, playerName)
                self.equip(equipment, False)

                finalDropChance = min(0.9, dropChance.get(rarity, 0.3) + 0.25)
                self._lootTable.addEquipment(equipment, finalDropChance)

        else: # rules for enemies level 1-10: guaranteed 1 equipment piece (quantity bonus rolls a chance at a 2nd). unable to roll epic/legendary equipment, 50% chance to reroll rares
            numEq = 1
            if self.quantityModifier > 1.0 and random.random() < min(0.9, self.quantityModifier - 1.0):
                numEq = 2
            for _ in range(numEq):
                slot = random.choice(slots)
                while self._slotIsFull(slot):
                    slot = random.choice(slots)
                rarity = None
                while rarity in [None, ItemRarity.EPIC, ItemRarity.LEGENDARY, ItemRarity.MYTHIC] or (rarity == ItemRarity.RARE and random.random() < 0.5):
                    rarity = rollRarity(self._level, self.rarityModifer)
                equipment = Equipment._generateEquipmentPiece(self._level, slot, rarity, playerClass, playerName)
                self.equip(equipment, False)

                finalDropChance = min(0.8, dropChance.get(rarity, 0.3) + 0.3)
                self._lootTable.addEquipment(equipment, finalDropChance)

        self._recalculateStats(False)

    def _generateInventory(self):
        numResources = random.randint(1, max(4, 2 + self._level // 15))

        chosenResources = random.sample(list(RESOURCES.keys()), min(numResources, len(RESOURCES)))

        for resourceName in chosenResources:
            baseAmount = 1 + self._level // 15
            maxAmount = 2 + self._level // 10

            amount = random.randint(baseAmount, maxAmount)
            self.addItem(resourceName, amount, False)

            dropChance = min(0.8, 0.6 + (self._level / 500))
            self._lootTable.addResource(resourceName, baseAmount, maxAmount, dropChance)

        runeDrops = rollRuneDrops(self._level, quantityModifier=self.quantityModifier)
        for category, runeType in runeDrops:
            dropChance = min(0.85, 0.5 + (self._level / 150))
            self._lootTable.addRune(category, runeType, dropChance)

    def dropLoot(self) -> tuple:
        resources, equipment = self._lootTable.resources, self._lootTable.equipmentPool
        runes = [(cat, rtype) for cat, rtype, _ in self._lootTable.runeDrops]
        return resources, equipment, runes
    
    def getExperienceReward(self) -> int:
        return self._experienceReward
    
    def death(self):
        console.print(f"\n[success]{self._name} has been defeated![/success]")
        return True

    def rollDungeonMap(self):
        from dungeons.dungeons import generateDungeonMap
        key = generateDungeonMap(self._level)
        if key:
            return key
        return None

def createEnemy(level: int = 1, difficulty: float = 1.0, rarity: float = 0, quantity: float = 0, playerClassName: str = None, playerName: str = None) -> Enemy:
    rarity += 1
    quantity += 1

    element = random.choice(DAMAGE_TYPES)
    baseHealth = random.randint(10, 20) + (level * (random.randint(1, 5))) // 2
    baseDamage = random.randint(2, 5) + level // 6
    baseSpeed = round(random.uniform(0.6, 1.1), 2)
    baseCritChance = round(random.uniform(0.01 + level / 500, 0.05 + level / 400), 2)
    baseCritMulti = round(random.uniform(1.1 + level / 300, 1.5 + level / 200), 2)

    baseHealth = round(baseHealth * difficulty)
    baseDamage = min(level + (level // 3), round(baseDamage * difficulty))

    loot = LootTable()
    numDrops = int(random.randint(1, max(2, 2 + level // 6)) * quantity)
    chosenResources = []
    for _ in range(numDrops):
        chosenResources.append(random.choice(list(RESOURCES.keys())))
    for res in chosenResources: # add resource drops
        minAmt = random.randint(1, 3 + level // 3) * quantity
        maxAmt = minAmt + random.randint(2, 3 + level // 5) * quantity
        dropChance = round(random.uniform(0.4, 1), 2)
        loot.addResource(res, minAmt, maxAmt, dropChance)

    name = f"{ELEMENTAL_NAME[element]} {random.choice(NAMES)}"
    enemy = Enemy(name, level, baseHealth, baseDamage, baseCritChance, baseCritMulti, element, baseSpeed, loot, rarity, quantity, playerClassName, playerName)
    enemy._health = enemy._maxHealth

    key = enemy.rollDungeonMap()
    if key:
        enemy._lootTable.addExtra(key.name, key.description)

    for _ in range(random.randint(1, 3)): #pick enemy resistances
        res = random.choice(DAMAGE_TYPES)
        amount = min(random.randint(-10+(level//3), 15+(level//4)), 35)
        enemy._addResistance(res, amount)
    enemy._recalculateStats(False)

    classPools = ENEMY_ABILITIES.get(enemy.className.value, {})
    pool = dict(classPools.get('base', {}))
    if enemy._ascendancy is not None:
        pool.update(classPools.get(enemy._ascendancy.value, {}))

    possibleAbilities = [name for name, ability in pool.items() if level >= ability.levelReq]
    if possibleAbilities:
        for abilityName in random.sample(possibleAbilities, k=min(len(possibleAbilities)-1, random.randint(level//10, 3+level//8))):
            enemy.gainAbility(abilityName, False)

    return enemy

...