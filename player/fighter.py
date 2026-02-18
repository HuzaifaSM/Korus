from .base import Player
from scripts.styles import console
import random

FIGHTER_DESCRIPTIONS = {
    "Fighter": "A combo-focused brawler."
        "\nEach hit grants +1 Combo for the rest of combat. +2 Damage per combo. No combo maximum."
        "\n Starting Stats: 40 HP | 3 Damage | 7.5% Crit Chance | 175% Crit Damage | Physical Damage | 1.15 Speed.",
    #ascendancies
    "Bladedancer": "Combo is capped at 5. At maximum combo, deal 60% increased damage with your next hit and heal for 3% of damage dealt. Reset combo after this attack.\n"
        "Upon dealing a critical hit, gain Flurry for 3 turns. Flurry: 15% Increased Physical Damage, +0.1 Speed, +20% Crit Damage."
        "-5 HP. +1 Damage. +0.1 Speed. +3% Crit Chance.",
    "Champion": "Every 5 combo generated, gain 1 Aegis up to 3. Aegis reduces the damage taken from the next to 0.\n"
        "When you block a hit with Aegis, your next attack deals 70% Increased damage."
        "At the end of combat, Heal 5 HP per stack of combo. Heal 5% Max HP per Aegis remaining.\n"
        "+10 HP. +2 Damage. -0.1 Speed. +10% Physical Resistance. +10% Block Chance", # block chance not yet available until shields are added!
    "Barbarian": "Combo grants +5 damage instead of +2. Gain 3% more damage per combo, up to a maximum of 30% at 10 combo.\n"
        "For every turn you begin above 10 combo, gain: +3% Crit Chance and +10% Crit Damage.\n"
        "Take 10% Increased Damage. Whenever you are hit, gain +5% Increased damage for the rest of combat, up to a maximum of +50%.\n"
        "-10 HP. +3 Damage. -0.05 Speed.",
    "Brawler": "Attacks grant 1 stack of Brawler's Fury, up to a maximum of 15 stacks. Brawler's Fury: +2 Damage, +2% Increased Damage.\n"
        "At max Brawler's Fury, your next attack hits all enemies for 110% damage and resets Brawler's Fury to 0.\n"
        "Gain 1 Combo when hit. Attacking the same target consecutively grants 1 additional combo.\n"
        "-5 HP. +1 Damage. +0.15 Speed. +20% Crit Damage. -10% Physical Resistance.",
    "Marshal": "Every 5 Combo generated, gain: +3% All Resistance, +3% Increased Damage, +2% Crit Chance.\n"
        "Every 5th attack is a guaranteed critical hit. Upon landing a critical hit, gain Momentum for 2 turns. Momentum: +0.15 Speed, +15% Increased Damage.\n"
        "Upon landing a critical hit, reduce all ability cooldowns by 1. On kill, your next ability costs 50% less stamina.\n"
        "+5 HP. +1 Damage. -0.05 Speed. +3% Crit Chance.",
    #subtypes
    "Bruiser": "Combo no longer affects damage directly. Instead, combo grants +0.03 speed uncapped and 1% increased damage.\n"
        "Attacks apply Overwhelmed to targets, up to 10 stacks. Overwhelm: -3% damage dealt and 1% more damage taken.\n"
        "+10 HP. +5 Damage. -0.05 Speed.",
    "Samurai": "50% Chance to generate an additional combo. Gain +0.02 speed per combo to a maximum of +0.5.\n"
        "Attacks have a 15% chance to apply Physical Exposure and Vulernable.\n"
        "If a single attack deals more than 15% of the target's Max HP, gain 1 stack of Honour, up to a maximum of 10 Honour.\n"
        "Honour: +2.5% Crit Chance, +10% Crit Damage, -0.05 Speed per Honour."
        "-5 Health. -1 Damage. +0.1 Speed. +10% Crit Damage.",
    "Veteran": "Combo is capped at 20. Upon reaching max combo, lose all combo and gain Fatigue for 2 turns. Fatigue: -10% Damage Dealt, -0.2 Speed, +5% Damage Taken.\n"
        "While you are at or below 10 Combo, you have +10% All Resistance and -0.15 Speed. While you are above 10 Combo, you have -15% All Resistance, +0.1 Speed, +15% Increased Damage.\n"
        "For each damage type you are attacked by, gain 1 stack of Versatility: +1% Damage Reduction, +2% Increased Damage, for the rest of combat. Versatility has no cap.\n"
        "+10 HP. +1 Damage. -0.1 Speed. -5% Crit Chance. -25% Crit Damage. +10% Physical Resistance."
}

class Fighter(Player): # higher speed, lower damage, physical damage
    def __init__(self, name, health = 40, damage = 3, damageType = "physical", speed = 1.15):
        super().__init__(name, health, damage, 0.075, 1.75, damageType, speed, className="Fighter", classDescription=FIGHTER_DESCRIPTIONS['Fighter'])
        self._combo = 0
        self.totalComboGenerated = 0

        self.aegis = 0
        self.aegisDamage = False

        self._maxCombo = None
        self.comboEffect = 1

        self.flurryTurns = 0

        self.previousTarget = None
        self.brawlerFury = 0
        self.maxBrawlerFury = 15

        self.barbarianHits = 0

        self.marshalMomentumTurns = 0
        self.marshalAttackCount = 0
        self.marshalDamageStacks = 0
        self.marshalStaminaReduction = False

        self.veteranComboType = None
        self.fatigueTurns = 0
        self.versatilityTypes = []

        self.honour = 0
        self.maxHonour = 10

    def deserialise(self, data):
        super().deserialise(data)
        if hasattr(self, '_rage'):
            delattr(self, '_rage')
        if hasattr(self, '_maxRage'):
            delattr(self, '_maxRage')
        if hasattr(self, '_mana'):
            delattr(self, '_mana')
        if hasattr(self, '_maxMana'):
            delattr(self, '_maxMana')
        if hasattr(self, '_maxThorns'):
            delattr(self, '_maxThorns')
        if hasattr(self, '_form'):
            delattr(self, '_form')

    def rollCritical(self, target):
        crit, critMulti = super().rollCritical(target)
        if self._ascendancy == 'Bladedancer':
            if crit:
                if self.flurryTurns == 0:
                    self._stats['Temporary']['speed'] += 0.1
                    self._stats['Temporary']['critMulti'] += 0.25
                self.flurryTurns = 3
        if self._ascendancy == 'Marshal':
            if self.marshalAttackCount % 5 == 0:
                crit = True
            if crit:
                if self.marshalMomentumTurns == 0:
                    self._stats['Temporary']['speed'] += 0.15
                self.marshalMomentumTurns = 2
                for _, ability in self._abilities.items():
                    ability.currentCooldown = max(0, ability.currentCooldown - 1)
                console.print('[gold1]Marshal: Critical Hit! Gained 2 turns of Momentum and all ability cooldowns reduced by 1.[/gold1]')
        return crit, critMulti

    def onAttack(self, damageDealt, damageType, target=None):
        super().onAttack(damageDealt, damageType)
        comboGained = False
        if self._subType != 'Bruiser':
            damageDealt += int((2 * self._combo) * self.comboEffect)
        else:
            damageDealt = int(damageDealt * (self._combo / 100) * self.comboEffect)

        if self._subType == 'Samurai' and target:
            honourThreshold = target._maxHealth * 0.15
            if damageDealt > honourThreshold and self.honour < self.maxHonour:
                self.honour += 1
                self._stats['Temporary']['critChance'] += 0.025
                self._stats['Temporary']['critMulti'] += 0.1
                self._stats['Temporary']['speed'] -= 0.05

        elif self._subType == 'Veteran':
            if self._combo > 10:
                damageDealt = round(damageDealt * 1.15)
            if self.fatigueTurns > 0:
                damageDealt = int(damageDealt * 0.9)
            if len(self.versatilityTypes) > 0:
                damageDealt = int(damageDealt * (1 + (len(self.versatilityTypes) * 0.02)))

        if self._ascendancy == 'Bladedancer' and self.flurryTurns > 0 and damageType == 'physical':
            damageDealt = int(damageDealt * 1.15)

        if self._ascendancy == 'Barbarian':
            bonus = 1 + (min(10, self._combo) * 0.03 + (self.barbarianHits * 0.05))
            damageDealt = int(damageDealt * bonus)

        bonus = 1 if self._subType == 'Samurai' and random.random() < 0.5 else 0
        if not self._maxCombo:
            self._combo += 1 + bonus
            self.totalComboGenerated += 1 + bonus
            comboGained = True
            console.print(f"\n[buff]Gained 1 Combo! Current Combo: {self._combo}[/buff]")
        elif self._maxCombo and self._combo < self._maxCombo:
            self._combo += 1 + bonus
            self.totalComboGenerated += 1 + bonus
            comboGained = True
            console.print(f"\n[buff]Gained 1 Combo! Current Combo: {self._combo}[/buff]")
        
        if self._ascendancy == 'Bladedancer':
            if self._combo == 5:
                damageDealt = int(damageDealt * 1.6)
                healAmount = int(damageDealt * 0.03)
                console.print(f"    [success]- Bladedancer: Devastating Strike! 2.5x damage multiplier. Healed for 3% of total damage dealt. (Healed for {healAmount} HP.)[/success]")
                self.heal(healAmount)
                self._combo = 0
        
        elif self._ascendancy == 'Champion':
            if self.totalComboGenerated % 5 == 0 and comboGained:
                self.aegis = min(3, self.aegis + 1)
            if self.aegisDamage:
                damageDealt = int(damageDealt * 1.7)
                self.aegisDamage = False

        elif self._ascendancy == 'Brawler':
            self.brawlerFury = min(15, self.brawlerFury + 1)

            if self.previousTarget == target:
                if self._maxCombo:
                    self._combo = min(self._maxCombo, self._combo + 1)
                else:
                    self._combo += 1
                    self.totalComboGenerated += 1
                    comboGained = True
            else:
                self.previousTarget = target
        
        elif self._ascendancy == 'Marshal':
            if self.totalComboGenerated % 5 == 0 and comboGained:
                self._stats['Temporary']['all'] += 3
                self._stats['Temporary']['critChance'] += 0.02
                self.marshalDamageStacks += 1
            damageDealt = int(damageDealt * (1 + 0.03 * self.marshalDamageStacks))
            self.marshalAttackCount += 1

        return damageDealt, damageType
    
    def onHit(self, damageTaken, damageType):
        if self._ascendancy == 'Barbarian':
            damageTaken = round(damageTaken * 1.1)
            self.barbarianHits += 1
        
        if self._ascendancy == 'Champion' and self.aegis:
            damageTaken = damageTaken = 0
            self.aegisDamage = True
            self.aegis -= 1

        if self._subType == 'Veteran' and damageType not in self.versatilityTypes:
            self.versatilityTypes.append(damageType)
        if self._subType == 'Veteran' and len(self.versatilityTypes) > 0:
            damageTaken = int(damageTaken * (1 - (len(self.versatilityTypes) * 0.01)))

        return super().onHit(damageTaken, damageType)

    def onKill(self, entity, attackData):
        if self._ascendancy == 'Marshal':
            self.marshalStaminaReduction = True
            console.print('[fire]Marshal: Killed an enemy! Your next ability will have 50% reduced stamina cost[/fire]')
        return None

    def damage(self, damage, damageType, combatUnit=None):
        if self._ascendancy == 'Barbarian':
            damage = round(damage * 1.1)
        return super().damage(damage, damageType, combatUnit)

    def onTurnStart(self):
        if self._ascendancy == 'Bladedancer' and self.flurryTurns > 0:
            self.flurryTurns -= 1
            if self.flurryTurns == 0:
                self._stats['Temporary']['speed'] -= 0.1
                self._stats['Temporary']['critMulti'] -= 0.25

        elif self._ascendancy == 'Barbarian' and self._combo > 10:
            self._stats['Temporary']['critChance'] += 0.03
            self._stats['Temporary']['critMulti'] += 0.25

        if self._subType == 'Samurai':
            self._stats['Temporary']['speed'] = min(0.5, 0.02 * self._combo)

        elif self._subType == 'Bruiser':
            self._stats['Temporary']['speed'] = 0.03 * self._combo

        elif self._subType == 'Veteran':
            if self._combo <= 10 and self.veteranComboType != 'defense':
                if self.veteranComboType is None:
                    self._stats['Temporary']['all'] += 10
                    self._stats['Temporary']['speed'] -= 0.15
                else: # switching from offense to defense
                    self._stats['Temporary']['all'] += 25
                    self._stats['Temporary']['speed'] -= 0.25
                self.veteranComboType = 'defense'
            elif self._combo > 10 and self.veteranComboType != 'offense':
                if self.veteranComboType is None:
                    self._stats['Temporary']['all'] -= 15
                    self._stats['Temporary']['speed'] += 0.1
                else:
                    self._stats['Temporary']['all'] -= 25
                    self._stats['Temporary']['speed'] += 0.25
                self.veteranComboType = 'offense'

        super().onTurnStart()

    def onBattleEnd(self):
        if self._ascendancy == 'Champion':
            healing = int((5 * self._combo) + (self._maxHealth * 0.05 * self.aegis))
            self.heal(healing)

        self._combo = 0
        self.aegis = False
        self.aegisDamage = False
        self.flurryTurns = 0
        self.brawlerFury = 0
        self.previousTarget = None
        self.marshalAttackCount = 0
        self.marshalDamageStacks = 0
        self.versatilityTypes = []
        super().onBattleEnd()

    def updateAscendancy(self, ascendancy):
        if ascendancy == 'Bladedancer':
            self._baseHealth -= 5
            self._baseDamage += 1
            self._baseSpeed += 0.1
            self._stats['baseCritChance'] += 0.03
            self._maxCombo = 5
            self._ascendancy = 'Bladedancer'
            self.ascendancyDescription = FIGHTER_DESCRIPTIONS['Bladedancer']
        elif ascendancy == 'Champion':
            self._baseHealth += 10
            self._baseDamage += 2
            self._baseSpeed -= 0.1
            self._stats['Permanent']['physical'] += 10
            #self._stats['Permanent']['blockChance'] += 10
            self._ascendancy = 'Champion'
            self.ascendancyDescription = FIGHTER_DESCRIPTIONS['Champion']
        elif ascendancy == 'Barbarian':
            self.comboEffect = 2.5
            self._baseHealth -= 10
            self._baseDamage += 3
            self._baseSpeed -= 0.05
            self._ascendancy = 'Barbarian'
            self.ascendancyDescription = FIGHTER_DESCRIPTIONS['Barbarian']
        elif ascendancy == 'Brawler':
            self._baseHealth -= 5
            self._baseDamage -= 2
            self._baseSpeed += 0.1
            self._stats['baseCritMulti'] += 0.2
            self._stats['Permanent']['physical'] -= 10
            self._ascendancy = 'Brawler'
            self.ascendancyDescription = FIGHTER_DESCRIPTIONS['Brawler']
        elif ascendancy == 'Marshal':
            self._baseHealth += 5
            self._baseDamage += 1
            self._baseSpeed += 0.05
            self._stats['baseCritChance'] += 0.03
            self._ascendancy = 'Marshal'
            self.ascendancyDescription = FIGHTER_DESCRIPTIONS['Marshal']
        self._recalculateStats(False)

    def updateSubType(self, subType):
        if subType == 'Bruiser':
            self._baseHealth += 10
            self._baseDamage += 5
            self._baseSpeed -= 0.05
            self._subType = 'Bruiser'
            self.subTypeDescription = FIGHTER_DESCRIPTIONS['Bruiser']
        elif subType == 'Samurai':
            self._baseHealth -= 5
            self._baseDamage -= 1
            self._baseSpeed += 0.1
            self._stats['baseCritMulti'] += 0.1
            self._subType = 'Samurai'
            self.subTypeDescription = FIGHTER_DESCRIPTIONS['Samurai']
        elif subType == 'Veteran':
            self._baseHealth += 10
            self._baseDamage += 1
            self._baseSpeed -= 0.1
            self._maxCombo = 20
            self._stats['baseCritChance'] -= 0.05
            self._stats['baseCritMulti'] -= 0.25
            self._stats['Permanent']['physical'] += 10
            self._subType = 'Veteran'
            self.subTypeDescription = FIGHTER_DESCRIPTIONS['Veteran']
        self._recalculateStats(False)
