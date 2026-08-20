from typing import Dict, Optional, List
import random
from copy import deepcopy
from .items import Equipment, Consumable
from .abilities import CLASS_ABILITIES, Ability, ENEMY_ABILITIES, BasicAttack
from .runeDrops import getRuneObject
from .styles import (
    console, printSuccess, printWarning, printError, printInfo,
    formatDamageType, formatDamageValue, formatRarity, createHealthBar,
    formatEffectsDetailed, formatAbilityCost, pause
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
            'Max_Resistances': {
                'physical': 75,
                'fire': 75,
                'cold': 75,
                'lightning': 75,
                'dark': 75,
                'holy': 75,
                'arcane': 75,
                'earth': 75,
                'psychic': 75,
                'ethereal': 75,
                'chaos': 75,
                'all': 75,
                'elemental': 75,
                'otherworld': 75,
                'divine': 75,
            },
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
                'item_rarity': 0,
                'item_quantity': 0,
                'enemy_quantity': 0,
                'xp_gain': 0,
                'gold_gain': 0,
                'stun_avoidance': 0,
                'dot_resistance': 0,
                'ailment_avoidance': 0,
                'healing_magnitude': 100,
                'crit_chance': 0,
                'crit_multi': 0,
                'crit_resistance': 0,
                'resistance_penetration': 0,
                'chance_to_multihit': 0,
                'lifesteal': 0,
                'damage_reduction': 0,
                'added_multihits': 0,
                'hp_regen': 0,
                'stamina_regen': 0,
                'increased_defenses': 0,
                'increased_health': 0,
                'health_on_hit': 0,
                'health_on_kill': 0,
                'stamina_on_hit': 0,
                'stamina_on_kill': 0,
                'thorns': 0,
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
                'chaos': 0,
                'ethereal': 0,
                'arcane': 0,
                'divine': 0,
                'elemental': 0,
                'otherworld': 0,
                'all': 0,
                'resistance_penetration': 0,
                'stun_avoidance': 0,
                'dot_resistance': 0,
                'ailment_avoidance': 0,
                'healing_magnitude': 0,
                'crit_resistance': 0,
                'lifesteal': 0,
                'damage_reduction': 0,
                'increased_damage_reduction': 0,
                'hp_regen': 0,
                'stamina_regen': 0,
                'enemy_quantity': 0,
                'added_multihits': 0,
                'increased_defenses': 0,
                'added_armour': 0,
                'added_evasion': 0,
                'added_energy_shield': 0,
                'increased_armour': 0,
                'increased_evasion': 0,
                'increased_energy_shield': 0,
                'increased_health': 0,
                # for everything that needs to be permanent and doesn't get affected by recalculated stats
                # e.g. all resistances, all base types that could be modified by classes/ascendancies
            },
            'Temporary': {
                'elemental': 0,
                'divine': 0,
                'otherworld': 0,
                'physical': 0,
                'all': 0,
                'healing_magnitude': 0,
                'stun_avoidance': 0,
                'dot_resistance': 0,
                'ailment_avoidance': 0,
                'crit_avoidance': 0,
                'speed': 0,
                'crit_chance': 0,
                'crit_multi': 0,
                'resistance_peneration': 0,
                'lifesteal': 0,
                'damage_reduction': 0,
                'increased_damage_reduction': 0,
                'hp_regen': 0,
                'stamina_regen': 0,
                'chance_to_multihit': 0,
                'added_multihits': 0,
                'increased_defenses': 0,
                'added_armour': 0,
                'added_evasion': 0,
                'added_energy_shield': 0,
                'increased_armour': 0,
                'increased_evasion': 0,
                'increased_energy_shield': 0,
                'increased_health': 0,
            },
            'baseCritChance': baseCritChance or 0.05,
            'baseCritMulti': baseCritMulti or 1.5,
            'armour': 0,
            'evasion': 0,
            'energy_shield': 0,
            'max_energy_shield': 0
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
        self.combatUnit = None
        self._pendingEffects = []

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
        return self._stats['energy_shield']

    @property
    def maxEnergyShield(self) -> int:
        return self._stats['max_energy_shield']

    @property
    def critChance(self) -> float:
        return self._stats['baseCritChance'] + self._stats['Bonuses']['crit_chance'] + self._getExtraBonuses('crit_chance')

    @property
    def critMulti(self) -> float:
        return self._stats['baseCritMulti'] + self._stats['Bonuses']['crit_multi'] + self._getExtraBonuses('crit_multi')

    @property
    def numMultihits(self) -> int:
        return 2 + self._getExtraBonuses('added_multihits') + self._stats['Bonuses']['added_multihits']

    @property
    def hasConsumables(self) -> bool:
        return 'Potion' in [i for i in self._inventory.keys()]

    def __rich__(self):
        return self.__str__()

    def __str__(self):
        healthBar = createHealthBar(self._health, self._maxHealth)
        baseStr =  f"[health]Health:[/health] {healthBar} | [damage]Damage:[/damage] {self._damage} [dim]({formatDamageType(self._damageType, self._damageType)})[/dim] | [speed]Speed:[/speed] {self._speed}"

        if self._stats.get('armour', 0) > 0:
            baseStr += f"\n[armour]Armour:[/armour] {self.armour}"
        if self._stats.get('evasion', 0) > 0:
            baseStr += f"\n[evasion]Evasion:[/evasion] {self.evasion}"
        if self._stats.get('max_energy_shield', 0) > 0:
            es = self.energyShield
            maxEs = self.maxEnergyShield
            baseStr += f"\n[energy_shield]Energy Shield:[/energy_shield] {es} / {maxEs}"

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

    def damage(self, damage: int, damageType: str='physical', combatUnit = None, *, lethal: bool = True, attacker: Entity = None) -> int:
        """'true' damageType means no resistances apply"""
        if combatUnit:
            resistMod = combatUnit.getResistanceModifier(damageType, attacker)
            stoneskinMod = combatUnit.getStoneskinModifier()
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
            stoneskinMod = 0
        if damageType == 'true':
            resistMod = 0
            stoneskinMod = 0

        damageReductionValue = min(damage, max(0, self._stats['Bonuses']['damage_reduction'] - damage))
        damage = max(0, damage - self._stats['Bonuses']['damage_reduction'])

        damage = int(round(damage * (1 - resistMod) * (1 - stoneskinMod)))
        trueDamage = max(0, damage - self._shield)
        damagePrevented = damage - trueDamage
        self._shield -= damagePrevented
        
        if trueDamage > 0:
            self._health -= trueDamage
            if not lethal and self._health <= 0:
                self._health = 1
                console.print(f"  [warning]Non-lethal damage dealt![/warning]")
            damageTypeFormatted = formatDamageType(damageType, damageType)
            dmgColour = formatDamageValue(trueDamage)
            console.print(f"  [damage]- {self._name} took[/damage] [{dmgColour}]{trueDamage}[/{dmgColour}] [damage]{damageTypeFormatted} damage.[/damage] [dim buff]({damagePrevented} damage prevented with shield)[/dim buff] [dim]HP remaining: {self._health} / {self._maxHealth}[/dim]")
            if self._isDead:
                self.death()

        return damageReductionValue

    def heal(self, amount: int, doPrint: bool = True) -> int:
        """returns true healed amount"""
        magnitude = self._stats['Bonuses']['healing_magnitude'] / 100
        modifiedAmount = int(amount * magnitude)
        if modifiedAmount > 0:
            self._health = min(self._health + modifiedAmount, self._maxHealth)
            self.onHeal(modifiedAmount)
            if doPrint:
                console.print(f"[success]{self._name} healed for {modifiedAmount} HP.[/success] [dim]HP Remaining: {self._health} / {self._maxHealth}[/dim]")
        elif modifiedAmount < 0:
            damageTaken = abs(modifiedAmount)
            self._health -= damageTaken
            if doPrint:
                printError(f"{self._name}'s negative Healing Magnitude dealt {damageTaken} damage! [dim]HP Remaining: {self._health} / {self._maxHealth}[/dim]")
            if  self._isDead:
                self.death()
        else:
            if doPrint:
                printWarning(f"[warning]{self._name}'s healing was nullified![/warning]")
        return modifiedAmount

    def death(self):
        console.print(f"[error]{self._name} has been defeated[/error]")
        return True 

    def rollCritical(self, target: Entity, damageDealt: int=None) -> tuple[bool, float]:
        """target is combatUnit"""
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
            resolved = deepcopy(ENEMY_ABILITIES[ability]) # used to sefate references

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
        if quantity > 0:
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

    def equip(self, equipment: Equipment, doPrint: bool = True) -> bool:
        slot = equipment.slot

        if slot not in self._equipment:
            if doPrint:
                printError(f"Invalid equipment slot: {slot}")
            return False
        
        if self._equipment[slot]:
            self.unequip(slot)

        self._equipment[slot] = equipment
        self._recalculateStats(doPrint)
        if equipment.slot != 'weapon':
            hGain, hInc, _ = equipment.getStatBonuses('health')
            self._health = min(
                self._maxHealth,
                (self._health + hGain) * (1 + hInc)
            )
        equipName = formatRarity(equipment.name, equipment.rarity.value)
        if doPrint:
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
        if 'increased_' in stat:
            return ((perm + temp) / 100)
        return perm + temp

    def _recalculateStats(self, doPrint: bool = True, inCombat: bool = False):
        self._maxHealth = self._baseHealth
        self._damage = self._baseDamage
        self._speed = self._baseSpeed

        for bonus in self._stats['Bonuses']:
            if bonus == 'healing_magnitude':
                self._stats['Bonuses'][bonus] = 100
            else:
                self._stats['Bonuses'][bonus] = 0

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
        staminaFlat = 0
        dmgFlat = 0
        dmgInc = 0
        spdFlat = 0
        spdInc = 0

        for slot, equipment in self._equipment.items():
            if equipment:
                hFlat, hInc, _ = equipment.getStatBonuses('health')
                healthFlat += hFlat
                healthInc += hInc

                stFlat, _, _ = equipment.getStatBonuses('added_stamina')
                staminaFlat += stFlat

                if equipment.slot == 'weapon':
                    dmgFlat += equipment.damage
                else:
                    dFlat, dInc, _ = equipment.getStatBonuses('damage')
                    dmgFlat += dFlat
                    dmgInc += dInc

                sFlat, sInc, _ = equipment.getStatBonuses('speed')
                spdFlat += sFlat
                spdInc += sInc

                if slot == "weapon":
                    self._damageType = equipment.getDamageType() if equipment.getDamageType() else self._damageType

                for damageType in self._stats['Resistances'].keys():
                    resFlat, _, _ = equipment.getStatBonuses(f'{damageType}_resistance')
                    self._stats['Resistances'][damageType] = min(
                        self._stats['Resistances'][damageType] + resFlat,
                        self._stats['Max_Resistances'][damageType], 90
                    )

                for bonus in self._stats['Bonuses'].keys():
                    bonusFlat, bonusInc, _ = equipment.getStatBonuses(bonus)
                    if bonus in ('crit_chance', 'crit_multi'):
                        self._stats['Bonuses'][bonus] += (bonusFlat / 100) * (1 + bonusInc)
                    else:
                        self._stats['Bonuses'][bonus] += round(bonusFlat * (1 + bonusInc))

                if hasattr(equipment, 'defenseType') and equipment.defenseType:
                    if equipment.defenseType == 'armour':
                        armour += equipment.defenseValue
                    elif equipment.defenseType == 'evasion':
                        evasion += equipment.defenseValue
                    elif equipment.defenseType == 'energy_shield':
                        es += equipment.defenseValue

                if equipment.slot == 'amulet':
                    _, _, gIncArm = equipment.getStatBonuses('armour')
                    globalArmourInc += gIncArm
                    _, _, gIncEva = equipment.getStatBonuses('evasion')
                    globalEvasionInc += gIncEva
                    _, _, gIncEs = equipment.getStatBonuses('energy_shield')
                    globalEsInc += gIncEs

        for damageType in self._stats['Resistances'].keys():
            extra = self._getExtraBonuses(damageType)
            self._stats['Resistances'][damageType] = min(
                self._stats['Resistances'][damageType] + extra,
                75
            )

        for bonus in self._stats['Bonuses'].keys():
            if bonus in ('crit_chance', 'crit_multi'):
                continue
            self._stats['Bonuses'][bonus] += round(self._getExtraBonuses(bonus))

        healthInc += self._getExtraBonuses('increased_health')
        globalArmourInc += self._getExtraBonuses('increased_armour')
        globalEvasionInc += self._getExtraBonuses('increased_evasion')
        globalEsInc += self._getExtraBonuses('increased_energy_shield')
        armour += self._getExtraBonuses('added_armour')
        evasion += self._getExtraBonuses('added_evasion')
        es += self._getExtraBonuses('added_energy_shield')

        self._damage = int((self._baseDamage + dmgFlat) * (1 + dmgInc))
        self._maxHealth = int((self._maxHealth + healthFlat) * (1 + healthInc))
        self._maxStamina = self._maxStamina + staminaFlat
        self._speed = (self._speed + spdFlat) * (1 + spdInc)
        self._speed += self._getExtraBonuses('speed')
        self._speed = round(self._speed, 2)

        # cap bonuses
        self._stats['Bonuses']['enemy_quantity'] = min(self._stats['Bonuses']['enemy_quantity'], 100)
        self._stats['Bonuses']['stun_avoidance'] = min(self._stats['Bonuses']['stun_avoidance'], 100)
        self._stats['Bonuses']['dot_resistance'] = min(self._stats['Bonuses']['dot_resistance'], 100)

        globalIncDef = self._getExtraBonuses('increased_defenses')
        finalArmour = int(armour * (1 + globalArmourInc + globalIncDef))
        finalEvasion = int(evasion * (1 + globalEvasionInc + globalIncDef))
        finalEs = int(es * (1 + globalEsInc + globalIncDef))

        self._stats['armour'] = finalArmour
        self._stats['evasion'] = finalEvasion
        if not inCombat:
            self._stats['energy_shield'] = finalEs
        self._stats['max_energy_shield'] = finalEs

        if not inCombat:
            self._health = min(self._health, self._maxHealth)
        self._speed = round(self._speed, 2)

        if doPrint:
            console.print("\n[bold cyan]Stats updated:[/bold cyan]")
            console.print(f"[health]HP:[/health] {self._health} / {self._maxHealth}")
            console.print(f"[damage]DMG:[/damage] {self._damage} |[{self._damageType}] Type: {self._damageType.title()}[/{self._damageType}]")
            console.print(f"[speed]Speed:[/speed] {self._speed:.2f}")

            resistances = {}
            for res, val in self._stats['Resistances'].items():
                if val != 0:
                    resistances[res] = val
            if resistances:
                console.print("\n[bold]Resistances:[/bold]")
                for r, v in resistances.items():
                    console.print(f"-  [{r}]{r.title()}[/{r}]: [cyan]{v}%[/cyan]")

            console.print()
            pause()

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
                item = item.replace('_', ' ').title()
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
            costStr = formatAbilityCost(ability.resources, ability.staminaCost)
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
    
    # ===================================================================================== #
    # COMBAT HOOKS
    # Called by CombatManager.performAttack/applyDamageWithDefenses in this order, per attack:
    #   1. onBeforeDamage    (attacker) -> retarget/reroll before anything is finalised
    #   1.5. onMultihitActivated (Attacher) -> only called if a multihit is activated
    #   2. onBeforeCritRoll  (attacker) -> rollCritical() -> onAfterCritRoll (attacker)
    #   3. onCrit (attacker) / onCriticallyHit (target)      - only if the roll crit
    #   4. per target, once per multihit:
    #        onPrepareHit (attacker)     - attacker adjusts the hit for this specific target
    #        onBeforeHit (target)        - target reacts before mitigation is applied
    #        getArmourIgnorePercent (attacker)
    #        onAttack (attacker)
    #        getEffectiveEvasion / getEffectiveArmour (target) / onEnergyShieldBroken (target)
    #          - used inside applyDamageWithDefenses while rolling evasion/armour/energy shield
    #        onHit (target)              - target reacts to the mitigated damage number
    #        onDealDamage (attacker)     - attacker reacts, before damage is actually applied
    #        onAfterMitigation (target)  - target's last chance to change finalDamage
    #        onEvade (target)            - called if the hit was evaded, rendering further functions irrelevant
    #        damage is applied to target
    #        onDamaged (target)          - target reacts to the damage that just landed
    #   5. once per target, after all multihits: mechanics/status effects applied, death checked
    #   6. onKill (attacker) if the target died, else onExecuteCheck (attacker)
    # Any hook may queue a StatusEffect via self._queueEffect() instead of returning one -
    # CombatManager drains _pendingEffects after the hook call and applies it to the
    # relevant target(s) once evasion has been resolved.
    # Every hook default here is a no-op/pass-through; rewrite per class as needed.
    # ===================================================================================== #

    def _queueEffect(self, effect):
        """Queues a StatusEffect (or list of them) to be applied once the current hit resolves.
        Use from any combat hook instead of calling combatManager.addStatusEffect directly when the
        effect should only land if the attack isn't evaded."""
        if isinstance(effect, list):
            self._pendingEffects.extend(effect)
        else:
            self._pendingEffects.append(effect)

    def onBeforeDamage(self, ability: Ability, damage: int, damageType: str, targets: list[Entity], combatManager):
        """Rewrite per class. Returns: damage, damageType, targets"""
        return damage, damageType, targets

    def onBeforeCritRoll(self, targetUnit, targets: list[Entity], combatManager):
        """Rewrite per class"""
        pass

    def onAfterCritRoll(self, targetUnit, targets: list, combatManager):
        """Rewrite per class. Undo whatever onBeforeCritRoll applied. No return value."""
        pass

    def getArmourIgnorePercent(self) -> float:
        """Rewrite per class. Returns the fraction (0-1) of the target's armour this attack ignores."""
        return 0.0

    def getEffectiveEvasion(self, damageType: str, combatUnit) -> float:
        """Rewrite per class. Returns the evasion value to roll against for this hit."""
        return self.evasion

    def getEffectiveArmour(self, damageType: str, combatUnit) -> float:
        """Rewrite per class. Returns the armour value to mitigate this hit with."""
        return self.armour

    def onEnergyShieldBroken(self, combatManager):
        """Rewrite per class. Called the moment this entity's energy shield is reduced to 0."""
        pass

    def onBeforeHit(self, finalDamage: int, damageType: str, attacker: Entity, combatManager) -> int:
        """Rewrite per class. return finalDamage"""
        return finalDamage

    def onAfterMitigation(self, attacker: Entity, finalDamage: int, damageType: str, evaded: bool,
                           armourDamagePrevented: int, esDamagePrevented: int, preMitigationDamage: int,
                           combatManager) -> int:
        """Rewrite per class. return finalDamage"""
        return finalDamage

    def onPrepareHit(self, target: Entity, targetUnit, finalDamage: int, damageType: str, combatManager) -> int:
        """Rewrite per class. return finalDamage"""
        return finalDamage

    def onDamaged(self, attacker: Entity, damageReductionValue: int, armourDamagePrevented: int, combatManager):
        """Rewrite per class"""
        pass

    def onDealDamage(self, target: Entity, targetUnit, finalDamage: int, damageType: str, evaded: bool,
                      armourDamagePrevented: int, esDamagePrevented: int, combatManager) -> int:
        """Rewrite per class. return finalDamage"""
        return finalDamage

    def onExecuteCheck(self, target: Entity, combatManager):
        """Rewrite per class"""
        pass

    def onEvade(self, combatManager):
        """Rewrite per class"""
        return

    def onMultihitActivated(self):
        """Rewrite per class"""
        return

    def onAttack(self, damageDealt: int, damageType: str, target, combatManager, ability: Ability):
        """Target should be combatUnit. Fires once per target before mitigation (once per multihit)."""
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

        ability.cooldown = ability.maxCooldown

        return damageDealt, damageType

    def onHit(self, damageTaken: int, damageType: str, crit: bool, attacker: Entity, combatManager):
        durabilityLoss = max(1, damageTaken // 30)
        for slot in ['head', 'chest', 'legs', 'feet']:
            if self._equipment.get(slot):
                armour = self._equipment.get(slot)
                armour.durability = max(0, armour.durability - durabilityLoss)
                if armour.durability == 0:
                    printWarning(f"{armour.name} has broken!")
                    self.unequip(slot)

        self.heal(self._stats['Bonuses']['health_on_hit'])
        self._stamina = min(self._maxStamina, self._stamina + self._stats['Bonuses']['stamina_on_hit'])

        return damageTaken, damageType

    def onKill(self, entity: Entity=None, attackData: Dict=None, combatManager=None) -> Optional[Dict]:
        """Rewrite per class. Call super() first (applies health/stamina on kill), always return None/dict\n
        attackData should include: final attack damage, damage type, mechanics of ability used"""
        self.heal(self._stats['Bonuses']['health_on_kill'])
        self._stamina = min(self._maxStamina, self._stamina + self._stats['Bonuses']['stamina_on_kill'])
        return {}

    def onHeal(self, healAmount: int):
        """Rewrite per class"""
        pass

    def onCrit(self, targets: list[Entity], combatManager, critDamage: int) -> int:
        """Rewrite per class, called when dealing a critical hit. Returns critDamage"""
        return critDamage

    def onCriticallyHit(self, attacker: Entity, combatManager, critDamage: int, damageType: str) -> int:
        """Rewrite per class, called when being critically hit. Returns critDamage"""
        return critDamage

    def onTurnStart(self, combatManager):
        """Recalculates stats for temp + permanent additions, use at end of onTurnStart methods"""
        self._recalculateStats(False, True)
        heal = self._stats['Bonuses']['hp_regen']
        self.heal(heal, False)
        self._stamina = min(self._maxStamina, self._stamina + 3 + self._stats['Bonuses']['stamina_regen'])
        if self._speed < 0.2: # minimum speed is 0.2
            self._speed = 0.2

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

    def onCombatStart(self, combatManager, combatUnit):
        """Assigns given combatUnit to self. run at the start of each onCombatStart"""
        self.combatUnit = combatUnit

    def onCombatEnd(self):
        """Sets all temporary stats to 0 and sets self.combatUnit to None, use at end of onCombatEnd methods."""
        for stat in self._stats['Temporary'].keys():
            self._stats['Temporary'][stat] = 0
        self.combatUnit = None

...