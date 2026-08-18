from .base import Player
from scripts.styles import console
import random

"""
FIGHTER REWORK — planned base mechanic (not yet implemented):

[class_fighter]An expert of combat, balancing precision and recklessness to dismantle their foes.[/class_fighter]
Start combat with 25 Aggression and Discipline. Gain 3 Aggression when you attack, and 1 Aggression per 10 Damage Dealt. Gain 3 Discipline when you use a non-damaging ability, and 1 Discipline per 15 Damage Taken.
At the start of your turn, gain 2 Aggression and 2 Discipline.
The combined total of your Aggression and Discipline cannot exceed 100. Aggression and Discipline have no maximum, but have a minimum of -50.
You cannot fall below 0 Aggression or Discipline unless an Ability puts you under the threshold.
There are 5 thresholds for Aggression and Discipline: Complacent (-50 to -1), Neutral (0 to 34), Trained (35 to 74), Dedicated (75 to 120), All-In (120+). Neutral has no stat changes.

Aggression Threshold Changes:
  - Complacent: -0.3 Speed, 30% Less Damage Dealt, -10% Crit Chance.
  - Trained: 20% Increased Physical Damage, +5% Lifesteal, +25% Crit Multi.
  - Dedicated: 50% Increased Physical Damage, +15% Lifesteal, +60% Crit Multi.
  - All-In: 100% Increased Physical Damage, +30% Lifesteal, upon landing a critical hit: heal for 10% of the damage dealt, and deal damage to all other enemies equal to your base damage. 40% Reduced Defenses.

  Discipline Threshold Changes:
  - Complacent: 30% More Damage taken, 25% Reduced Defenses, -20% Stun Avoidance.
  - Trained: +10% Damage Reduction, 5% Increased Defenses, +1% of Max HP regenerated as HP per turn.
  - Dedicated: +15% Less Damage Taken, Gain Thorns equal to your base damage, 10% Increased Defenses, +3% of Max HP regenerated as HP per turn
  - All-In: You are unable to critically hit. Gain Thorns equal to 5x your base damage, upon killing an enemy: gain their base damage as damage for the rest of combat, heal equal to 10% of their Max HP. Take 30% Less Damage from all hits. Damage prevented is gained as damage on your next attack.

Starting Stats: 40 HP | 6 Damage | 5% Crit Chance | 175% Crit Damage | Physical Damage | 1.05 Speed.
"""

FIGHTER_DESCRIPTIONS = {
    "Fighter": "[class_fighter]A combo-focused brawler.[/class_fighter]"
        "\nEach hit grants +1 [resource]Combo[/resource] for the rest of combat. +2 Damage per [resource]combo[/resource]. No [resource]combo[/resource] maximum."
        "\n Starting Stats: 40 [health]HP[/health] | 3 [damage]Damage[/damage] | 7.5% [critical]Crit Chance[/critical] | 175% [critical]Crit Damage[/critical] | [physical]Physical Damage[/physical] | 1.15 [speed]Speed[/speed].",
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

    def rollCritical(self, target, damageDealt=None):
        crit, critMulti = super().rollCritical(target, damageDealt)
        if self._ascendancy == 'Bladedancer':
            if crit:
                if self.flurryTurns == 0:
                    self._stats['Temporary']['speed'] += 0.1
                    self._stats['Temporary']['crit_multi'] += 0.25
                self.flurryTurns = 3
        if self._ascendancy == 'Marshal':
            if self.marshalAttackCount % 5 == 0:
                crit = True
            if crit:
                if self.marshalMomentumTurns == 0:
                    self._stats['Temporary']['speed'] += 0.15
                self.marshalMomentumTurns = 2
                for _, ability in self._abilities.items():
                    ability.cooldown = max(0, ability.cooldown - 1)
                console.print('[gold1]Marshal: Critical Hit! Gained 2 turns of Momentum and all ability cooldowns reduced by 1.[/gold1]')
        return crit, critMulti

    def onAttack(self, damageDealt, damageType, target=None, combatManager=None):
        damageDealt, damageType = super().onAttack(damageDealt, damageType, target, combatManager)
        comboGained = False
        bonus = 0
        damageDealt = int(damageDealt * (self._combo / 100) * self.comboEffect)

        if self._ascendancy == 'Bladedancer' and self.flurryTurns > 0 and damageType == 'physical':
            damageDealt = int(damageDealt * 1.15)

        if self._ascendancy == 'Barbarian':
            bonus = 1 + (min(10, self._combo) * 0.03 + (self.barbarianHits * 0.05))
            damageDealt = int(damageDealt * bonus)

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
                self._stats['Temporary']['crit_chance'] += 0.02
                self.marshalDamageStacks += 1
            damageDealt = int(damageDealt * (1 + 0.03 * self.marshalDamageStacks))
            self.marshalAttackCount += 1

        return damageDealt, damageType
    
    def onHit(self, damageTaken, damageType, crit=False, attacker=None, combatManager=None):
        if self._ascendancy == 'Barbarian':
            damageTaken = round(damageTaken * 1.1)
            self.barbarianHits += 1

        if self._ascendancy == 'Champion' and self.aegis:
            damageTaken = damageTaken = 0
            self.aegisDamage = True
            self.aegis -= 1

        return super().onHit(damageTaken, damageType, crit, attacker, combatManager)

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
                self._stats['Temporary']['crit_multi'] -= 0.25

        elif self._ascendancy == 'Barbarian' and self._combo > 10:
            self._stats['Temporary']['crit_chance'] += 0.03
            self._stats['Temporary']['crit_multi'] += 0.25

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
