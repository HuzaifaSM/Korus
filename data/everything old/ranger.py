from .base import Player
from scripts.styles import console
from random import random
from collections import deque

RANGER_DESCRIPTIONS = {
    "Ranger": "An agile marksman.\n"
        "Gain 1 Tailwind on attack, 2 on critical hit, up to a maximum of 20 stacks. Tailwind: 5% Increased Evasion, +1% Crit Chance, +0.025 Speed.\n"
        "Upon dodging an attack, lose up to 3 Tailwind and gain Momentum for 1 turn. Momentum: +0.2 Speed, 15% Increased Damage, +5% Crit Chance.\n"
        "Starting Stats: 40 HP | 6 Damage | 15% Crit Chance | 150% Crit Damage | Wind Damage | 1.05 Speed.",
    #ascendancies
    "Sniper": "-10 Max Tailwind. Tailwind instead grants +3% Increased Evasion, +2% Crit Chance and +10% Crit Damage per stack.\n"
        "At 10 Tailwind, your next attack deals 100% Increased damage and consumes all Tailwind. If this attack kills the enemy, regain 6 Tailwind.\n"
        "Critical hits dealt whilst at 7 or more Tailwind apply Vulnerable to the target.\n"
        "-5 HP. +2 Damage. -0.1 Speed. +5% Crit Chance. +50% Crit Damage. -15% Physical Resistance.",
    "Windwalker": "Tailwind's Speed buff is increased to +0.05 per stack instead of +0.025. +10 Max Tailwind.\n"
        "Momentum lasts 2 turns instead of 1. While you have Momentum, gain 20% Increased Evasion. Upon killing an enemy gain Gust for 3 turns.\n"
        "Gust: 15% Increased Wind Damage, 10% Damage Reduction, +0.2 Speed. Upon losing Gust, heal for 10% of your Max HP.\n"
        "-10 HP. +1 Damage. +0.15 Speed. -5% Crit Chance. +10% Wind Resistance. 10% Increased Evasion.",
    "Hunter": "Attacking the same enemy grants you 1 stack of Predator, to a max of 10. Predator: 3% Increased Damage, +1% Crit Chance, +5% Crit Damage.\n"
        "Upon switching targets whilst your current target is alive, lose all stacks of Predator.\n"
        "Gaining Momentum does not consume Tailwind. Instead, upon dealing a critical hit, consume up to 5 Tailwind to gain +10% Crit Damage per stack consumed.\n"
        "Killing an enemy whilst you have 4+ stacks of Predator heals you for 5% Max HP per stack of Predator, and consumes all Predator stacks.\n"
        "+10 HP. +1 Damage. -0.15 Speed. +10% Physical Resistance.",
    "Skirmisher": "Momentum has 100% Increased effect. Tailwind no longer grants additional Crit Chance or Speed, and instead grants 3% Increased Damage per stack.\n"
        "Upon gaining Momentum, your next 2 attacks deal 30% of their damage as Wind damage to up to 2 random additional enemies.\n"
        "Whenever you consume Tailwind, gain Shield equal to 1% of your Evasion Rating per stack of Tailwind consumed.\n"
        "-10 HP. +4 Damage. +0.1 Speed. -5% Crit Chance. -15% Crit Damage.",
    "Tempest": "Wind damage has a 40% chance to deal 50% of damage as additional damage of a random elemental damage type - Wind, Earth, Fire, Cold, Lightning.\n"
        "Every time this bonus damage triggers, gain 1 stack of Mysticism for the rest of combat. Mysticism has no maximum stacks.\n"
        "Mysticism: 5% Increased Elemental Damage, 2% Increased Evasion, +1% Elemental Resistance.\n"
        "Whilst at or above 12 Tailwind, your attacks have a 30% chance to apply an elemental ailment on hit: Shock, Chill, Burn, Elemental Exposure.\n"
        "+10 HP. -2 Damage. -0.1 Speed. +10% Elemental Resistance.",
    "Pathfinder": "Upon taking damage, gain Adaptation to that damage type. Adaptation: -10% Damage from that type. You can have up to 3 Adaptations at any time.\n"
        "Deal 10% Increased damage per unique Adaptation. You can have multiple of the same Adaptations. Your Adaptations are always based on the last 3 damage types you've been hit by.\n"
        "Tailwind no longer grants Speed bonuses, and instead grants +1% All Resistance per stack. -5 Max Tailwind.\n"
        "Whilst at max Tailwind, restore 3% Max HP at the start of your turn. Upon dodging an attack, cleanse a random ailment.\n"
        "+15 HP. -1 Damage. -0.05 Speed. +15% DoT Resistance.",
    #subtypes
    "Sharpshooter": "Critical hits grant +2 Tailwind rather than +1. Tailwind grants +2% Crit Chance per stack rather than +1%. Take 10% Increased Damage.\n"
        "Critical Hits apply Elemental Exposure for 3 turns. When an enemy dodges your attack, gain 1 stack of Tailwind.\n"
        "-5 HP. +2 Damage. -0.1 Speed. +10% Crit Chance. +50% Crit Damage. 15% Less Armour.",
    "Scout": "Tailwind grants +10% Increased Evasion per stack rather than +5%. Upon dodging 3 attacks in a row, heal 10% Max HP and gain 3 Tailwind.\n"
        "Dodging an attack grants Opening for your next hit. Opening: 15% Increased Damage, +10 Damage.\n"
        "+5 HP. -2 Damage. +0.05 Speed. 10% Increased Evasion.",
    "Warden": "10% Increased Wind Damage. Tailwind no longer grants a Speed Buff. Instead, it grants +2 Damage per stack of Tailwind.\n"
        "Upon killing an enemy, gain Protector for 2 turns. Protector: 15% Increased Evasion, 10% Increased Wind Damage.\n"
        "+10 HP. +1 Damage. -0.15 Speed. +5% Wind Resistance. +5% Physical Resistance."
}

ELEMENTAL = ['wind', 'earth', 'fire', 'cold', 'lightning']

class Ranger(Player): # higher speed, lower health, wind damage
    def __init__(self, name, health = 40, damage = 6, damageType = "wind", speed = 1.05):
        super().__init__(name, health, damage, 0.15, 1.5, damageType, speed, className="Ranger", classDescription=RANGER_DESCRIPTIONS['Ranger'])
        self.tailwind = 0
        self.maxTailwind = 20
        self.tailwindBuffs = {
            'increased_evasion': 5,
            'critChance': 0.01,
            'speed': 0.025
        }
        self.momentumTurns = 0
        self.momentumTurnsGained = 1
        self.momentumBuffs = {
            'speed': 0.15,
            'damage': 15,
            'critChance': 0.05
        }
        self.sniperHit = False
        self.momentumEffect = 1
        self.gustTurns = 0
        self.predator = 0
        self.currentTarget = None
        self.skirmisherHits = 0
        self.mysticism = 0
        self.adaptations = deque(maxlen=3) # max size of 3 list, automatically deletes 0 index at len > 3
        self.scoutDodges = 0
        self.opening = False
        self.protectorTurns = 0

    def _serialise(self):
        temp = super()._serialise()
        temp['maxTailwind'] = self.maxTailwind
        temp['tailwindBuffs'] = self.tailwindBuffs
        temp['momentumTurnsGained'] = self.momentumTurnsGained
        temp['momentumBuffs'] = self.momentumBuffs

    def deserialise(self, data):
        super().deserialise(data)
        self.maxTailwind = data.get('maxTailwind', 20)
        self.tailwindBuffs = data.get('tailwindBuffs', {
            'increased_evasion': 5,
            'critChance': 0.01,
            'speed': 0.025
        })
        self.momentumTurnsGained = data.get('momentumTurnsGained', 1)
        self.momentumBuffs = data.get('momentumBuffs', {
            'speed': 0.15,
            'damage': 15,
            'critChance': 0.05
        })

    def onEvade(self):
        lostTailwind = min(3, self.tailwind)
        if self._subType == 'Scout':
            self.scoutDodges += 1
            if self.scoutDodges % 3 == 0:
                heal = int(self._maxHealth * 0.1)
                self.heal(heal)
                console.print(f"  [wind]Scout: Dodged 3 attacks in a row! Healed 10% Max HP and gained 3 Tailwind.[/wind]")
                self.tailwind = min(self.maxTailwind, self.tailwind + 3)
            self.opening = True

        if self._ascendancy == 'Hunter':
            lostTailwind = 0
        
        if lostTailwind > 0 or self._ascendancy == 'Hunter':
            self.tailwind -= lostTailwind
            self.momentumTurns = self.momentumTurnsGained
            for stat, val in self.momentumBuffs.items():
                if stat in self._stats['Temporary']:
                    self._stats['Temporary'][stat] += val * self.momentumEffect
            console.print(f"  [wind]Ranger: Lost {lostTailwind} Tailwind to gain Momentum.[/wind]")
            for  _ in range(lostTailwind):
                for stat, val in self.tailwindBuffs.items():
                    if stat in self._stats['Temporary']:
                        self._stats['Temporary'][stat] -= val
            if self._ascendancy == 'Skirmisher':
                self.skirmisherHits += 2
                shieldGain = int(0.01 * lostTailwind * self.evasion)
                self._shield += shieldGain
                console.print(f"  [wind]Skirmisher: Lost {lostTailwind} Tailwind. Healed {lostTailwind}% of Evasion as Shield. +{shieldGain} Shield.[/wind]")

    def onAttack(self, damageDealt, damageType, target=None, combatManager=None):
        super().onAttack(damageDealt, damageType, target, combatManager)

        if self.tailwind < self.maxTailwind:
            self.tailwind += 1
            console.print(f"[wind]Ranger: Gained 1 Tailwind. Current Tailwind: {self.tailwind} / {self.maxTailwind}[/wind]")
            for stat, val in self.tailwindBuffs.items():
                if stat in self._stats['Temporary']:
                    self._stats['Temporary'][stat] += val

        if 'damage' in self.tailwindBuffs:
            bonus = 1 + (self.tailwindBuffs['damage'] / 100 * self.tailwind)
            damageDealt = int(damageDealt * bonus)
        if self.momentumTurns > 0:
            if 'damage' in self.momentumBuffs:
                bonus = 1 + (self.momentumBuffs['damage'] / 100)
                damageDealt = int(damageDealt * bonus)

        if self._subType == 'Scout' and self.opening:
            damageDealt += 10
            damageDealt = int(damageDealt * 1.15)
            self.opening = False

        elif self._subType == 'Warden' and damageType == 'wind':
            damageDealt += self.tailwindBuffs['added_damage'] * self.tailwind
            damageDealt = int(damageDealt * 1.1)
            if self.protectorTurns > 0:
                damageDealt = int(damageDealt * 1.1)

        if self._ascendancy == 'Sniper':
            if self.tailwind == 10:
                damageDealt *= 2
                self.tailwind = 0
                self.sniperHit = True

        elif self._ascendancy == 'Windwalker':
            if self.gustTurns > 0 and damageType == 'wind':
                damageDealt = int(damageDealt * 1.15)

        elif self._ascendancy == 'Hunter':
            if target:
                if self.currentTarget == target:
                    self.predator += 1
                    self._stats['Temporary']['critChance'] += 0.01
                    self._stats['Temporary']['critMulti'] += 0.05
                else: # different target
                    if not target.entity._isDead: # willingly switched
                        self._stats['Temporary']['critChance'] -= 0.01 * self.predator
                        self._stats['Temporary']['critMulti'] -= 0.05 * self.predator
                        self.predator = 0
            bonus = 1 + (0.03 * self.predator)
            damageDealt = int(damageDealt * bonus)

        elif self._ascendancy == 'Skirmisher':
            bonus = 1 + (self.tailwindBuffs.get('increased_damage', 3) * self.tailwind / 100)
            damageDealt = int(damageDealt * bonus)
            if self.skirmisherHits > 0:
                self.skirmisherHits -= 1

        elif self._ascendancy == 'Tempest' and self.mysticism > 0 and damageType in ELEMENTAL:
            bonus = 1 + (0.05 * self.mysticism)
            damageDealt = int(damageDealt * bonus)

        elif self._ascendancy == 'Pathfinder':
            bonus = 1 + (0.1 * len(set(self.adaptations))) # make set since only unique adaptations count
            damageDealt = int(damageDealt * bonus)

        return damageDealt, damageType

    def onHit(self, damageTaken, damageType, attacker=None, combatManager=None):
        if self._subType == 'Sharpshooter':
            damageTaken = int(damageTaken * 1.1)

        if self._ascendancy == 'Windwalker' and self.gustTurns > 0:
            damageTaken = int(damageTaken * 0.9)

        elif self._ascendancy == 'Pathfinder':
            self.adaptations.append(damageType)
            if len(self.adaptations) > 0:
                adaptationStacks = len([a for a in self.adaptations if a == damageType])
                reduction = 1 - (adaptationStacks * 0.1)
                damageTaken = int(damageTaken * reduction)
        
        return super().onHit(damageTaken, damageType, attacker, combatManager)

    def rollCritical(self, target, damageDealt=None):
        crit, multi = super().rollCritical(target, damageDealt)
        if self.tailwind < self.maxTailwind:
            self.tailwind += 1
            tg = 1
            if self._subType == 'Sharpshooter' and self.tailwind < self.maxTailwind:
                self.tailwind += 1
                tg += 1
            console.print(f"[wind]Ranger: Critical Hit! Gained {tg} Tailwind. Current Tailwind: {self.tailwind} / {self.maxTailwind}[/wind]")
            for stat, val in self.tailwindBuffs.items():
                if stat in self._stats['Temporary']:
                    self._stats['Temporary'][stat] += val

        if self._ascendancy == 'Hunter' and crit:
            consumed = min(5, self.tailwind)
            self.tailwind -= consumed
            critMulti += consumed * 0.1
            console.print(f"  [wind]Hunter: Critical hit! Consumed {consumed} Tailwind to gain +{int(consumed*10)}% Crit Damage.[/wind]")

        return crit, multi
    
    def onKill(self, entity, attackData, combatManager=None):
        if self._subType == 'Warden':
            if self.protectorTurns == 0:
                self._stats['Temporary']['increased_evasion'] += 15
            self.protectorTurns = 2

        if self._ascendancy == 'Sniper' and self.sniperHit:
            self.tailwind += 6
            console.print("[wind]Sniper: Killed an enemy with empowered attack! Regained 6 Tailwind.[/wind]")
        
        if self._ascendancy == 'Windwalker':
            self.gustTurns = 3
            self._stats['Temporary']['speed'] += 0.2
            console.print("[wind]Windwalker: Killed an enemy! Gained Gust for 3 turns. +15% Wind Damage, +10% Damage Reduction, +0.2 Speed.[/wind]")
        
        if self._ascendancy == 'Hunter' and self.predator >= 4:
            heal = int(self._maxHealth * 0.05 * self.predator)
            consumed = self.predator
            self.heal(heal)
            self.predator = 0
            console.print(f"  [wind]Hunter: Killed an enemy! Consumed {consumed} stacks of Predator to heal for {heal} total HP.[/wind]")

        return {}

    def onTurnEnd(self):
        if self.momentumTurns > 0:
            self.momentumTurns -= 1
            if self.momentumTurns == 0:
                for stat, val in self.momentumBuffs.items():
                    if stat in self._stats['Temporary']:
                        self._stats['Temporary'][stat] -= val * self.momentumEffect

    def onTurnStart(self, combatManager=None):
        if self._subType == 'Warden' and self.protectorTurns > 0:
            self.protectorTurns -= 1
            if self.protectorTurns == 0:
                self._stats['Temporary']['increaed_evasion'] -= 15

        if self._ascendancy == 'Sniper':
            self.sniperHit = False
        
        elif self._ascendancy == 'Windwalker' and self.gustTurns > 0:
            self.gustTurns -= 1
            if self.gustTurns == 0:
                self._stats['Temporary']['speed'] -= 0.2
                heal = int(self._maxHealth * 0.1)
                self.heal(heal)
                console.print(f"[wind]Windwalker: Gust has worn off! Healed for 10% Max HP. Healed for {heal} HP total.[/wind]")
        
        elif self._ascendancy == 'Pathfinder':
            if self.tailwind == self.maxTailwind:
                heal = int(self._maxHealth * 0.03)
                self.heal(heal)
                console.print(f"[wind]Pathfinder: Began turn at Max Tailwind, 3% Max HP healed. +{heal} HP.[/wind]")

        super().onTurnStart(combatManager)

    def onBattleEnd(self):
        self.tailwind = 0
        self.momentumTurns = 0
        self.sniperHit = False
        self.gustTurns = 0
        self.predator = 0
        self.currentTarget = None
        self.skirmisherHits = 0
        self.mysticism = 0
        self.adaptations = deque(maxlen=3)
        self.scoutDodges = 0
        self.opening = False
        self.protectorTurns = 0

        super().onBattleEnd()

    def updateAscendancy(self, ascendancy):
        if ascendancy == 'Sniper':
            self._baseHealth -= 5
            self._baseDamage += 2
            self._baseSpeed -= 0.1
            self.maxTailwind -= 10
            self.tailwindBuffs = {
                'increased_evasion': 3,
                'critChance': 0.02,
                'critMulti': 0.1
            }
            self._stats['baseCritChance'] += 0.05
            self._stats['baseCritMulti'] += 0.5
            self._stats['Permanent']['physical'] -= 15
            self._ascendancy = 'Sniper'
            self.ascendancyDescription = RANGER_DESCRIPTIONS["Sniper"]
        elif ascendancy == 'Windwalker':
            self._baseHealth -= 10
            self._baseDamage += 1
            self._baseSpeed += 0.15
            self.maxTailwind += 10
            self.momentumTurnsGained = 2
            self._stats['baseCritChance'] -= 0.05
            self._stats['Permanent']['wind'] += 10
            self._stats['Permanent']['increased_evasion'] += 10
            self._ascendancy = 'Windwalker'
            self.ascendancyDescription = RANGER_DESCRIPTIONS["Windwalker"]
        elif ascendancy == 'Hunter':
            self._baseHealth += 10
            self._baseDamage += 1
            self._baseSpeed -= 0.15
            self._stats['Permanent']['physical'] += 10
            self._ascendancy = 'Hunter'
            self.ascendancyDescription = RANGER_DESCRIPTIONS["Hunter"]
        elif ascendancy == 'Skirmisher':
            self._baseHealth -= 10
            self._baseDamage += 4
            self._baseSpeed += 0.1
            self._stats['baseCritChance'] -= 0.05
            self._stats['baseCritMulti'] -= 0.15
            self.tailwindBuffs = {
                'increased_evasion': 5,
                'increased_damage': 3
            }
            self.momentumEffect = 2
            self._ascendancy = 'Skirmisher'
            self.ascendancyDescription = RANGER_DESCRIPTIONS["Skirmisher"]
        elif ascendancy == 'Tempest':
            self._baseHealth += 10
            self._baseDamage -= 2
            self._baseSpeed -= 0.1
            self._stats['Permanent']['elemental'] += 10
            self._ascendancy = 'Tempest'
            self.ascendancyDescription = RANGER_DESCRIPTIONS["Tempest"]
        elif ascendancy == 'Pathfinder':
            self._baseHealth += 15
            self._baseDamage -= 1
            self._baseSpeed -= 0.05
            self.maxTailwind -= 5
            self._stats['Permanent']['dotResistance'] += 15
            self.tailwindBuffs = {
                'increased_evasion': 5,
                'critChance': 0.01,
                'all': 1
            }
            self._ascendancy = 'Pathfinder'
            self.ascendancyDescription = RANGER_DESCRIPTIONS["Pathfinder"]
        self._recalculateStats(False)

    def updateSubType(self, subType):
        if subType == 'Sharpshooter':
            self._baseHealth -= 5
            self._baseDamage += 2
            self._baseSpeed -= 0.1
            self._stats['baseCritChance'] += 0.1
            self._stats['baseCritMulti'] += 0.5
            self._stats['Permanent']['increased_armour'] -= 15
            self.tailwindBuffs['critChance'] += 0.01
            self._subType = 'Sharpshooter'
            self.subTypeDescription = RANGER_DESCRIPTIONS["Sharpshooter"]
        elif subType == 'Scout':
            self._baseHealth += 5
            self._baseDamage -= 2
            self._baseSpeed += 0.05
            self._stats['Permanent']['increased_evasion'] += 10
            self.tailwindBuffs['increased_evasion'] += 5
            self._subType = 'Scout'
            self.subTypeDescription = RANGER_DESCRIPTIONS["Scout"]
        elif subType == 'Warden':
            self._baseHealth += 10
            self._baseDamage += 1
            self._baseSpeed -= 0.15
            self._stats['Permanent']['wind'] += 5
            self._stats['Permanent']['physical'] += 5
            self.tailwindBuffs = {
                'increased_evasion': 5,
                'critChance': 0.01,
                'added_damage': 2
            }
            self._subType = 'Warden'
            self.subTypeDescription = RANGER_DESCRIPTIONS["Warden"]
        self._recalculateStats(False)

# Sniper = deal 1500+ damage with a single critical hit
# windwalker = have at least 2.5 speed
# Hunter = kill 100 enemies
# Skirmisher = kill 20 enemies with mutli-targeting attacks
# Tempest = deal 3000 wind damage
# Pathfinder = take 5000 elemental damage
# Sharpshooter = deal 100 critical hits
# Scout = have an evasion rating of 5000+
# Warden = win 50 combats
