from typing import Dict, Optional, List
import random
from copy import deepcopy
from .items import Equipment, Consumable
from .abilities import CLASS_ABILITIES, Ability, ENEMY_ABILITIES, BasicAttack
from .runeDrops import getRuneObject
from .styles import (
    console, printSuccess, printWarning, printError, printInfo,
    formatDamageType, formatRarity, createHealthBar,
    formatEffectsDetailed, formatAbilityCost
)

ELEMENTAL_RES = ['fire', 'earth', 'cold', 'lightning']
DIVINE_RES = ['holy', 'dark', 'arcane']
OTHERWORLD_RES = ['chaos', 'ethereal', 'psychic']

class Entity:
    def __init__(self, health: int, damage: int, baseCritChance: float, baseCritMulti: float,
                 damageType: str, speed: float,
                 name: str, className: str = None, isPlayer: bool = False):
        self._maxHealth = health
        self._health = health
        self._shield = 0
        self._damage = damage
        self._damageType = damageType or "physical"
        self._speed = speed
        self._stats = {
            'Resistances': {
                'physical': 0,
                'fire': 0,
                'cold': 0,
                'lightning': 0,
                'dark': 0,
                'holy': 0,
                'arcane': 0,
                'earth': 0,
                'psychic': 0,
                'ethereal': 0,
                'chaos': 0,
                'all': 0,
                'elemental': 0,
                'otherworld': 0,
                'divine': 0
            },
            'Bonuses': {
                'itemRarity': 0,
                'itemQuantity': 0,
                'enemyQuantity': 0,
                'xpGain': 0,
                'goldGain': 0,
                'stunAvoidance': 0,
                'dotResistance': 0,
                'ailmentAvoidance': 0,
                'healingMagnitude': 100,
                'critChance': 0,
                'critMulti': 0,
                'critResistance': 0,
                'resistancePenetration': 0,
                'chance_to_multihit': 0,
                'lifesteal': 0,
                'added_multihits': 0,
                'hpRegen': 0,
                'increased_defenses': 0,
            },
            'Permanent': {
                'physical': 0,
                'fire': 0,
                'earth': 0,
                'lightning': 0,
                'cold': 0,
                'holy': 0,
                'dark': 0,
                'psychic': 0,
                'arcane': 0,
                'divine': 0,
                'otherworld': 0,
                'all': 0,
                'resistancePenetration': 0,
                'stunAvoidance': 0,
                'dotResistance': 0,
                'ailmentAvoidance': 0,
                'critResistance': 0,
                'lifesteal': 0,
                'hpRegen': 0,
                'added_multihits': 0,
                'increased_defenses': 0,
                'added_armour': 0,
                'added_evasion': 0,
                'added_energy_shield': 0,
                'increased_armour': 0,
                'increased_evasion': 0,
                'increased_energy_shield': 0,
                # for everything that needs to be permanent and doesn't get affected by recalculated stats
                # e.g. all resistances, all base types that could be modified by classes/ascendancies
            },
            'Temporary': {
                'elemental': 0,
                'divine': 0,
                'otherworld': 0,
                'all': 0,
                'healingMagnitude': 0,
                'stunAvoidance': 0,
                'dotResistance': 0,
                'speed': 0,
                'critChance': 0,
                'critMulti': 0,
                'resistancePeneration': 0,
                'lifesteal': 0,
                'hpRegen': 0,
                'added_multihits': 0,
                'increased_defenses': 0,
                'added_armour': 0,
                'added_evasion': 0,
                'added_energy_shield': 0,
                'increased_armour': 0,
                'increased_evasion': 0,
                'increased_energy_shield': 0,
                'increased_dark_damage': 0,
            },
            'baseCritChance': baseCritChance or 0.05,
            'baseCritMulti': baseCritMulti or 1.5,
            'armour': 0,
            'evasion': 0,
            'energyShield': 0,
            'maxEnergyShield': 0
        }
        self._abilities: Dict[str, Ability] = {"Basic Attack": BasicAttack()}
        self._inventory: Dict[str, int] = {}  # {item_name: quantity}
        self._craftingInventory: Dict[str, int] = {} # {f'{category}_{runeType}': quantity}
        self._equipmentStorage: List[Equipment] = [] # store equipment objects
        self._equipment: Dict[str, Optional[Equipment]] = {
            'weapon': None,
            'head': None,
            'chest': None,
            'legs': None,
            'feet': None,
            'ring': None,
            'amulet': None
        }
        # stats before equipment
        self._baseHealth = health
        self._baseDamage = damage
        self._baseSpeed = speed
        self._baseStamina = 100
        self._stamina = 100
        self._maxStamina = 100
        self._gold = 0
        self._level = 1
        self._xp = 0
        self.calcXpRequirement()
        self._name = name
        self.className = className
        self.classDescription = None
        self._ascendancy = None
        self.ascendancyDescription = None
        self.isPlayer = isPlayer

    @property
    def _isDead(self) -> bool:
        return self._health <= 0

    @property
    def armour(self) -> int:
        return self._stats['armour']
    
    @property
    def evasion(self) -> int:
        return self._stats['evasion']
    
    @property
    def energyShield(self) -> int:
        return self._stats['energyShield']
    
    @property
    def maxEnergyShield(self) -> int:
        return self._stats['maxEnergyShield']

    @property
    def critChance(self) -> float:
        return self._stats['baseCritChance'] + self._getExtraBonuses('critChance')

    @property
    def critMulti(self) -> float:
        return self._stats['baseCritMulti'] + (self._stats['Bonuses']['critMulti']) + self._getExtraBonuses('critMulti')

    @property
    def numMultihits(self) -> int:
        return 2 + self._getExtraBonuses('added_multihits')

    def __rich__(self):
        return self.__str__()

    def __str__(self):
        healthBar = createHealthBar(self._health, self._maxHealth)
        baseStr =  f"[health]Health:[/health] {healthBar} | [damage]Damage:[/damage] {self._damage} [dim]({formatDamageType(self._damageType, self._damageType)})[/dim] | [speed]Speed:[/speed] {self._speed}"

        if self._stats.get('armour', 0) > 0:
            baseStr += f"\n[cyan]Armour:[/cyan] {self._stats['armour']}"
        if self._stats.get('evasion', 0) > 0:
            baseStr += f"\n[cyan]Evasion:[/cyan] {self._stats['evasion']}"
        if self._stats.get('maxEnergyShield', 0) > 0:
            es = self._stats.get('energyShield', 0)
            maxEs = self.stats['maxEnergyShield']
            baseStr += f"\n[cyan]Energy Shield:[/cyan] {es} / {maxEs}"

        return baseStr

    def __repr__(self):
        return f"{self.serialise()}"

    def serialise(self):
        equipped = {}
        for slot, equip in self._equipment.items():
            if equip:
                equipped[slot] = equip.serialise()

        equipmentStorage = []
        for equipment in self._equipmentStorage:
            if equipment:
                equipmentStorage.append(equipment.serialise())

        return {'maxHealth': self._maxHealth,
                'baseHealth': self._baseHealth,
                'health': self._health,
                'baseDamage': self._baseDamage,
                'damageType': self._damageType,
                'baseSpeed': self._baseSpeed,
                'stats': self._stats,
                'name': self._name,
                'level': self._level,
                'xp': self._xp,
                'xpToNextLevel': self._xpToNextLevel,
                'gold': self._gold,
                'equipped': equipped,
                'equipmentStorage': equipmentStorage,
                'craftingInventory': self._craftingInventory,
                'inventory': self._inventory,
                'className': self.className,
                'classDescription': self.classDescription,
                'ascendancy': self._ascendancy,
                'ascendancyDescription': self.ascendancyDescription,
        }

    def deserialise(self, data: Dict):
        self._maxHealth = data.get('maxHealth', 50)
        self._baseHealth = data.get('baseHealth', 50)
        self._health = data.get('health', 50)
        self._baseDamage = data.get('baseDamage', 3)
        self._damageType = data.get('damageType', 'physical')
        self._baseSpeed = data.get('baseSpeed', 1.0)
        self._name = data.get('name', 'Entity')
        self._level = data.get('level', 0)
        self._xp = data.get('xp', 0)
        self._xpToNextLevel = data.get('xpToNextLevel', 50)
        self._gold = data.get('gold', 0)
        self.className = data.get('className')
        self.classDescription = data.get('classDescription', 'Basic Player')
        self._ascendancy = data.get('ascendancy', None)
        self.ascendancyDescription = data.get('ascendancyDescription', None)
        equipment = data.get('equipped')

        if equipment:
            for slot, eqData in equipment.items():
                e = Equipment.deserialise(eqData)
                self._equipment[slot] = e

        equipmentStorage = data.get('equipmentStorage')
        if equipmentStorage:
            for eqData in equipmentStorage:
                e = Equipment.deserialise(eqData)
                self._equipmentStorage.append(e)
        
        self._inventory = data.get('inventory', {})
        self._craftingInventory = data.get('craftingInventory', {})
        self._abilities = {"Basic Attack": BasicAttack()}

        self._recalculateStats()

    def _addResistance(self, resistance: str, amount: int):
        """Amount can be negative or positive (no lower limit for resistances)"""
        if resistance in self._stats['Resistances']:
            self._stats['Resistances'][resistance] = min(
                self._stats['Resistances'][resistance] + amount,
                75
            )

    def calcXpRequirement(self):
        self._xpToNextLevel = max(int((self._level * 25) ** 0.717), (3 * self._level) ** 2)

    def damage(self, damage: int, damageType: str, combatUnit = None, *, lethal: bool = True):
        """'true' damageType means no resistances apply"""
        if combatUnit:
            resistMod = combatUnit.getResistanceModifier(damageType)
        else:
            resistMod = self._stats['Resistances'].get(damageType, 0) / 100
            if damageType in ELEMENTAL_RES:
                resistMod += self._stats['Resistances']['elemental'] / 100
            elif damageType in DIVINE_RES:
                resistMod += self._stats['Resistances']['divine'] / 100
            elif damageType in OTHERWORLD_RES:
                resistMod += self._stats['Resistances']['otherworld'] / 100
            resistMod += self._stats['Resistances']['all'] / 100
            resistMod = min(0.75, resistMod)
        if damageType == 'true':
            resistMod = 0
        damage = int(round(damage * (1 - resistMod)))
        trueDamage = max(0, damage - self._shield)
        damagePrevented = damage - trueDamage
        self._shield -= damagePrevented
        if damage > 0:
            self._health -= damage
            if not lethal and self._health <= 0:
                self._health = 1
                console.print(f"  [warning]Non-lethal damage dealt![/warning]")
            damageTypeFormatted = formatDamageType(damageType, damageType)
            console.print(f"  [damage]- {self._name} took {damage} {damageTypeFormatted} damage.[/damage] [dim buff]({damagePrevented} damage prevented with shield)[/dim buff] [dim]HP remaining: {self._health} / {self._maxHealth}[/dim]")
            if  self._isDead: # dies
                self.death()
        else:
            console.print("[success]Your Shield prevented any damage being taken![/success]")

    def heal(self, amount: int, doPrint: bool = True) -> int:
        """returns true healed amount"""
        magnitude = self._stats['Bonuses']['healingMagnitude'] / 100
        modifiedAmount = int(amount * magnitude)
        if modifiedAmount > 0:
            self._health = min(self._health + modifiedAmount, self._maxHealth)
            if doPrint:
                console.print(f"[success]{self._name} healed for {modifiedAmount} HP.[/success] [dim]HP Remaining: {self._health} / {self._maxHealth}[/dim]")
        elif modifiedAmount < 0:
            damageTaken = abs(modifiedAmount)
            self._health -= damageTaken
            if doPrint:
                console.print(f"[error]{self._name}'s negative healing dealt {damageTaken} damage![/error] [dim]HP Remaining: {self._health} / {self._maxHealth}[/dim]")
            if  self._isDead:
                self.death()
        else:
            if doPrint:
                console.print(f"[warning]{self._name}'s healing was nullified![/warning]")
        return modifiedAmount

    def death(self):
        console.print(f"[error]{self._name} has been defeated[/error]")
        return True 

    def rollCritical(self, target: Entity, damageDealt: int=None) -> tuple[bool, float]:
        """target is combatUnit"""
        target = target.entity
        if random.random() < self.critChance:
            return True, self.critMulti
        return False, 1.0

    def gainGold(self, amount: int):
        self._gold += amount
        console.print(f"[gold]{self._name} got +{amount}g.[/gold] [dim]Total gold: {self._gold}[/dim]")

    def gainAbility(self, ability: str, doPrint: bool = True):
        if self.isPlayer:
            tree = CLASS_ABILITIES.get(self.className, {}).get('base', {}).get(ability)
            if not tree:
                return
            overlay = CLASS_ABILITIES.get(self.className, {}).get(self._ascendancy, {}).get(ability)
            resolved = tree.getCurrentAbility(self._level, overlay)
            if not resolved:
                return
        else:
            if ability not in ENEMY_ABILITIES:
                return
            resolved = deepcopy(ENEMY_ABILITIES[ability]) # used to separate references

        self._abilities[ability] = resolved
        if doPrint:
            console.print(f"[success]{self._name} Learnt {ability}![/success]")
            if resolved.damageType:
                damageTypeFormatted = formatDamageType(resolved.damageType, resolved.damageType)
                console.print(f"[dim]Base Damage: {resolved.baseDamage} + {resolved.damageScaling*100:.0f}% of damage | Type: {damageTypeFormatted}[/dim]")
            costStr = formatAbilityCost(getattr(resolved, 'resources', {}))
            if costStr != "-":
                console.print(f"[dim]Cost: {costStr}[/dim]")
            for line in formatEffectsDetailed(resolved.effects):
                console.print(f"  [buff]- {line}[/buff]")

    def removeAbility(self, ability: str, doPrint: bool = True):
        if ability in self._abilities:
            del self._abilities[ability]
            if doPrint:
                console.print(f"[warning]{self._name} no longer has the ability: {ability}[/warning]")

    def canUseAbility(self, ability: Ability) -> bool:
        if self._stamina < ability.staminaCost:
            return False
        self._stamina -= ability.staminaCost
        return True

    def spendHealthForAbility(self, amount: int):
        """Default: abilities that cost Health draw straight from Health. Rewrite per class for alternate payment sources."""
        self._health = max(0, self._health - amount)
        if self._isDead:
            self.death()

    def displayAbilities(self):
        console.print("\n[bold cyan]=== Abilities ===[/bold cyan]")
        for name, ability in self._abilities.items():
            console.print(f"  [cyan]- {name}[/cyan]")
            if ability.damageType:
                damageTypeFormatted = formatDamageType(ability.damageType, ability.damageType)
                console.print(f"    [dim]Base Damage: {ability.baseDamage} + {ability.damageScaling*100:.0f}% of damage | Type: {damageTypeFormatted}[/dim]")
            if ability.healBase or ability.healPercent:
                console.print(f"    [heal]Heal: {ability.healBase} + {ability.healPercent*100:.0f}% Max HP[/heal]")
            costStr = formatAbilityCost(getattr(ability, 'resources', {}))
            if costStr != "-":
                console.print(f"    [dim]Cost: {costStr}[/dim]")
            for line in formatEffectsDetailed(ability.effects):
                console.print(f"    [buff]- {line}[/buff]")

    def addRune(self, category: str, runeType: str, quantity: int = 1):
        key = f'{category}_{runeType}'
        if key in self._craftingInventory:
            self._craftingInventory[key] += quantity
        else:
            self._craftingInventory[key] = quantity
        rune = getRuneObject(category, runeType)
        runeName = rune.name if rune else runeType
        console.print(f'[success]  - Gained {quantity}x {runeName}[/success]')

    def removeRune(self, category: str, runeType: str, quantity: int = 1) -> bool:
        key = f'{category}_{runeType}'
        if key not in self._craftingInventory:
            return False
        if self._craftingInventory[key] < quantity:
            return False
        self._craftingInventory[key] -= quantity
        if self._craftingInventory[key] <= 0:
            del self._craftingInventory[key]
        return True
    
    def getRune(self, category: str, runeType: str) -> int:
        key = f'{category}_{runeType}'
        return self._craftingInventory.get(key, 0)

    def hasRune(self, category: str, runeType: str) -> bool:
        return self.getRune(category, runeType) > 0

    def addItem(self, itemName: str, quantity: int = 1, doPrint: bool = True):
        self._inventory[itemName] = self._inventory.get(itemName, 0) + quantity
        if doPrint:
            console.print(f"[success]  - Gained {quantity}x {itemName}[/success]")

    def removeItem(self, itemName: str, quantity: int = 1) -> bool:
        if self._inventory.get(itemName) >= quantity:
            self._inventory[itemName] -= quantity
            if self._inventory[itemName] <= 0:
                del self._inventory[itemName]
            return True
        return False

    def hasItem(self, itemName: str, quantity: int = 1) -> bool:
        return self._inventory.get(itemName, 0) >= quantity

    def getItem(self, itemName: str) -> int:
        return self._inventory.get(itemName, 0)

    def addEquipmentToStorage(self, equipment: Equipment):
        self._equipmentStorage.append(equipment)
        equipName = formatRarity(equipment.name, equipment.rarity.value)
        console.print(f"[info]Stored {equipName} in equipment storage.[/info]")

    def removeEquipmentFromStorage(self, index: int) -> Optional[Equipment]:
        if 0 <= index < len(self._equipmentStorage):
            return self._equipmentStorage.pop(index)
        return None
    
    def showEquipmentStorage(self):
        console.print("\n[bold cyan]=== Equipment Storage ===[/bold cyan]")
        if not self._equipmentStorage:
            console.print("  [dim]Empty[/dim]")
        else:
            for i, equipment in enumerate(self._equipmentStorage, 1):
                equipName = formatRarity(equipment.name, equipment.rarity.value)
                console.print(f"  [cyan]{i}.[/cyan] {equipName}")
                console.print(f"    [dim]Durability: {equipment.durability} / {equipment.maxDurability}[/dim]")

    def equip(self, equipment: Equipment) -> bool:
        slot = equipment.slot

        if slot not in self._equipment:
            printError(f"Invalid equipment slot: {slot}")
            return False
        
        if self._equipment[slot]:
            self.unequip(slot)

        self._equipment[slot] = equipment
        self._recalculateStats()
        equipName = formatRarity(equipment.name, equipment.rarity.value)
        printSuccess(f"Equipped {equipName} in {slot} slot.")
        return True
    
    def unequip(self, slot: str) -> Optional[Equipment]:
        if slot in self._equipment and self._equipment[slot]:
            item = self._equipment[slot]
            self._equipment[slot] = None
            self._recalculateStats()
            printInfo(f"Unequipped {item.name}")
            return item
        return None
    
    def _getExtraBonuses(self, stat: str) -> int: # gets temporary + permanent buffs for a stat
        perm = self._stats['Permanent'].get(stat, 0)
        temp = self._stats['Temporary'].get(stat, 0)
        if 'increased_' in stat or stat in ['critChance', 'critMulti']:
            return (perm + temp / 100)
        return perm + temp

    def _recalculateStats(self, doPrint: bool = True, inCombat: bool = False):
        self._maxHealth = self._baseHealth
        self._damage = self._baseDamage
        self._speed = self._baseSpeed

        # reset bonuses
        for bonus in self._stats['Bonuses']:
            if bonus == 'healingMagnitude':
                self._stats['Bonuses'][bonus] = 100
            else:
                self._stats['Bonuses'][bonus] = 0

        # reset resistances
        for res in self._stats['Resistances']:
            self._stats['Resistances'][res] = 0

        armour = 0
        evasion = 0
        es = 0
        globalArmourInc = 0
        globalEvasionInc = 0
        globalEsInc = 0

        healthFlat = 0
        healthInc = 0
        dmgFlat = 0
        dmgInc = 0
        spdFlat = 0
        spdInc = 0

        for slot, equipment in self._equipment.items():
            if equipment:
                hFlat, hInc, _ = equipment.getStatBonuses('health')
                healthFlat += hFlat
                extra = self._getExtraBonuses('increased_health')
                healthInc += hInc + extra

                dFlat, dInc, _ = equipment.getStatBonuses('damage')
                dmgFlat += dFlat
                dmgInc += dInc

                sFlat, sInc, _ = equipment.getStatBonuses('speed')
                spdFlat += sFlat
                spdInc += sInc
                
                if slot == "weapon":
                    self._damageType = equipment.getDamageType() if equipment.getDamageType() else self._damageType

                for damageType in self._stats['Resistances'].keys():
                    resFlat, _, _ = equipment.getStatBonuses(damageType)
                    extra = self._getExtraBonuses(damageType)
                    self._stats['Resistances'][damageType] = min(
                        self._stats['Resistances'][damageType] + resFlat + extra,
                        75
                    )
                
                for bonus in self._stats['Bonuses'].keys():
                    bonusFlat, bonusInc, _ = equipment.getStatBonuses(bonus)
                    extra = self._getExtraBonuses(bonus)
                    self._stats['Bonuses'][bonus] = round((bonusFlat + extra) * (1 + bonusInc))

                if hasattr(equipment, 'defenseType') and equipment.defenseType:
                    if equipment.defenseType == 'armour':
                        armour += equipment.defenseValue + self._getExtraBonuses('added_armour')
                    elif equipment.defenseType == 'evasion':
                        evasion += equipment.defenseValue + self._getExtraBonuses('added_evasion')
                    elif equipment.defenseType == 'energyShield':
                        es += equipment.defenseValue + self._getExtraBonuses('added_energy_shield')

                if equipment.slot == 'amulet':
                    _, _, gIncArm = equipment.getStatBonuses('armour')
                    globalArmourInc += gIncArm + self._getExtraBonuses('increased_armour')
                    _, _, gIncEva = equipment.getStatBonuses('evasion')
                    globalEvasionInc += gIncEva + self._getExtraBonuses('increased_evasion')
                    _, _, gIncEs = equipment.getStatBonuses('energy_shield')
                    globalEsInc += gIncEs + self._getExtraBonuses('increased_energy_shield')

        self._maxHealth = int((self._maxHealth + healthFlat) * (1 + healthInc))

        # cap bonuses
        self._stats['Bonuses']['enemyQuantity'] = min(self._stats['Bonuses']['enemyQuantity'], 100)
        self._stats['Bonuses']['stunAvoidance'] = min(self._stats['Bonuses']['stunAvoidance'], 100)
        self._stats['Bonuses']['dotResistance'] = min(self._stats['Bonuses']['dotResistance'], 100)

        globalIncDef = self._getExtraBonuses('increased_defenses')
        armour += self._getExtraBonuses('added_armour')
        evasion += self._getExtraBonuses('added_evasion')
        es += self._getExtraBonuses('added_energy_shield')
        finalArmour = int(armour * (1 + globalArmourInc + globalIncDef))
        finalEvasion = int(evasion * (1 + globalEvasionInc + globalIncDef))
        finalEs = int(es * (1 + globalEsInc + globalIncDef))

        self._stats['armour'] = finalArmour
        self._stats['evasion'] = finalEvasion
        if not inCombat:
            self._stats['energyShield'] = finalEs
        self._stats['maxEnergyShield'] = finalEs

        if not inCombat:
            self._health = min(self._health, self._maxHealth)
        self._speed = round(self._speed, 2)

        if doPrint:
            console.print("\n[bold cyan]Stats updated:[/bold cyan]")
            console.print(f"[health]HP:[/health] {self._health} / {self._maxHealth}")
            console.print(f"[damage]DMG:[/damage] {self._damage} |[{self._damageType}] Type: {self._damageType}[/{self._damageType}]")
            console.print(f"[speed]Speed:[/speed] {self._speed:.2f}")
            
            console.print("\n[bold]Resistances:[/bold]")
            for res, val in self._stats['Resistances'].items():
                if val != 0:
                    console.print(f"  {res}: [cyan]{val}%[/cyan]")

            activeBonuses = {k: v for k, v in self._stats['Bonuses'].items() if v > 0}
            if activeBonuses.get('healingMagnitude', 100) == 100:
                activeBonuses.pop('healingMagnitude')
            if activeBonuses:
                console.print("\n[bold]Bonuses:[/bold]")
                for bonus, val in activeBonuses.items():
                    console.print(f"  [buff]{bonus.replace('_', ' ').title()}: {val}%[/buff]")

    def useConsumable(self, consumable: Consumable) -> bool:
        if consumable.use(self):
            self.removeItem(consumable.name, 1)
            return True
        return False
    
    def showInventory(self):
        console.print("\n[bold cyan]=== INVENTORY ===[/bold cyan]")
        if not self._inventory:
            console.print(" [dim]- Empty[/dim]")
        else:
            for item, quantity in sorted(self._inventory.items()):
                console.print(f" [cyan]- {item}:[/cyan] [gold]{quantity}[/gold]")

    def showEquipment(self):
        console.print("\n[bold cyan]=== EQUIPMENT ===[/bold cyan]")
        for slot, equipment in self._equipment.items():
            if equipment:
                equipName = formatRarity(equipment.name, equipment.rarity.value)
                console.print(f"  [cyan]{slot.capitalize()}:[/cyan] {equipName}")
            else:
                console.print(f"  [cyan]{slot.capitalize()}:[/cyan] [dim]Empty[/dim]")

    def showAbilities(self):
        console.print("\n[bold cyan]=== abilities ===[/bold cyan]")
        if not self._abilities:
            printWarning("No abilities learnt yet!")
            return
        for name, ability in self._abilities.items():
            console.print(f" [bold]= {name} =[/bold]")
            if ability.damageType:
                damageTypeFormatted = formatDamageType(ability.damageType, ability.damageType)
                console.print(f"  [dim]- Base Damage: {ability.baseDamage} + {ability.damageScaling*100:.0f}% of damage | Type: {damageTypeFormatted}[/dim]")
            if ability.healBase or ability.healPercent:
                console.print(f"  [heal]- Heal: {ability.healBase} + {ability.healPercent*100:.0f}% Max HP[/heal]")
            console.print(f"  [dim]- Cooldown: {ability.maxCooldown} turns[/dim]")
            costStr = formatAbilityCost(getattr(ability, 'resources', {}))
            if costStr != "-":
                console.print(f"  [dim]- Cost: {costStr}[/dim]")
            for line in formatEffectsDetailed(ability.effects):
                console.print(f"  [buff]- {line}[/buff]")

    def showCraftingInventory(self):
        console.print('\n[cyan bold]=== Crafting Inventory ===[/cyan bold]')
        if not self._craftingInventory:
            console.print("[dim]No runes in crafting inventory[/dim]")
            return
        
        for key, quantity in sorted(self._craftingInventory.items()):
            cat, rtype = key.split('_', 1)
            rune = getRuneObject(cat, rtype)
            console.print(rune)
            console.print(f'[dim]Quantity: {quantity}[/dim]')

    def onAttack(self, damageDealt: int, damageType: str, target=None, combatManager=None):
        """Target should be combatUnit"""
        durabilityLoss = max(1, damageDealt // 25)
        if self._equipment.get('weapon'):
            weapon = self._equipment.get('weapon')
            weapon.durability = max(0, weapon.durability - durabilityLoss)
            if weapon.durability == 0:
                printWarning(f"{weapon.name} has broken!")
                self.unequip('weapon')
        accessoryLoss = durabilityLoss // 2
        for slot in ['ring', 'amulet']:
            if self._equipment.get(slot):
                accessory = self._equipment.get(slot)
                accessory.durability = max(0, accessory.durability - accessoryLoss)
                if accessory.durability == 0:
                    printWarning(f"{accessory.name} has broken!")
                    self.unequip(slot)

        incStr = f'increased_{damageType}_damage'
        if self._stats['Temporary'].get(incStr, 0) > 0:
            damageDealt += int(damageDealt * self._stats['Temporary'][incStr])

        return damageDealt, damageType

    def onHit(self, damageTaken: int, damageType: str, crit: bool=False, attacker: Entity=None, combatManager=None):
        durabilityLoss = max(1, damageTaken // 30)
        for slot in ['head', 'chest', 'legs', 'feet']:
            if self._equipment.get(slot):
                armour = self._equipment.get(slot)
                armour.durability = max(0, armour.durability - durabilityLoss)
                if armour.durability == 0:
                    printWarning(f"{armour.name} has broken!")
                    self.unequip(slot)
        return damageTaken, damageType

    def onKill(self, entity: Entity, attackData: Dict, combatManager=None) -> Optional[Dict]:
        """Rewrite per class, always return None/dict\n
        attackData should include: final attack damage, damage type, mechanics of ability used"""
        return {}

    def onHeal(self, healAmout: int):
        """Rewrite per class"""
        pass

    def onTurnStart(self, combatManager=None):
        """Recalculates stats for temp + permanent additions, use at end of onTurnStart methods"""
        self._recalculateStats(False, True)
        heal = self._stats['Bonuses']['hpRegen']
        self.heal(heal, False)

    def onTurnEnd(self):
        """Rewrite per class"""
        pass

    def onTurnEnd(self):
        """Rewrite per class"""
        pass

    def onEvade(self):
        """Rewrite per class"""
        pass

    def onBlock(self):
        """Rewrite per class"""
        pass

    def onBattleEnd(self):
        """Sets all temporary stats to 0, use at end of onBattleEnd methods."""
        for stat in self._stats['Temporary'].keys():
            self._stats['Temporary'][stat] = 0

...