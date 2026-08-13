from .base import Player
from scripts.styles import console
import random

SPECTRE_DESCRIPTIONS = {
    "Spectre": "[class_spectre]A vengeful ghost brimming with malice.[/class_spectre]\n"
        "[resource]Ghostly[/resource]: When dealing [ethereal]Ethereal[/ethereal] Damage, heal equal to 10% of ignored Armour Rating on the target.\n"
        "Starting Stats: 40 [health]HP[/health] | 6 [damage]Damage[/damage] | 3% [critical]Crit Chance[/critical] | 180% [critical]Crit Damage[/critical] | [ethereal]Ethereal Damage[/ethereal] | 1.15 [speed]Speed[/speed].",
    #ascendancies
    "Wraith": "Ghostly now heals for 20% of ignored Armour Rating. If the target has no Armour Rating, they take 50% Increased Damage.\n"
        "For every 300 HP healed in combat through Ghostly, lose 1% Max HP permanently.\n"
        "+10 HP. -1 Damage. -0.05 Speed. +10% Ethereal Resistance.",
    "Reaper": "Deal 15% Increased Damage to enemies below 30% Max HP. Execute Enemies under 5% Max HP on hit. Execute immediately kills the targeted enemy.\n"
        "When Executing enemies, heal for 10% of their Max HP and gain 5% of their damage as your own permanently.\n"
        "Ghostly also grants 5% of ignored Armour Rating gained as Shield.\n"
        "-15 HP. +2 Damage. +0.05 Speed. +2% Crit Chance. +100 Armour.",
    "Phantasm": "30% Less Physical Damage Taken. Ghostly heals for 5% of ignored Armour Rating. Ethereal Damage has a 30% chance to apply Phased to a random enemy for 3 turns.\n"
        "Phased: -10% Damage Dealt, -0.2 Speed. When a Phased enemy hits you, you gain Shifting: 10% Increased Armour, Evasion, and Energy Shield for 2 turns.\n"
        "+20 HP. +1 Damage. -0.1 Speed. -10% Stun Avoidance. +25% Crit Damage.",
    "Revenant": "Once per combat, upon taking lethal damage, survive at 1 HP and gain Intangible for 1 turn. Intangible: Immune to Damage, +30% Increased Ethereal Damage.\n"
        "If you take a hit larger than 30% of your Max HP whilst Intangible, you will die. Upon losing Intangible, heal equal to damage prevented whilst intangible.\n"
        "Upon killing an enemy, the next amount of damage you take heals you instead. The healing is doubled if the damage was Ethereal.\n"
        "-10 HP. +3 Damage. +0.1 Speed. -10% Physical Resistance.",
    "Lich": "All sources of healing are applied to Energy Shield. Ghostly heals you for 15% of ignored Armour Rating.\n"
        "While your Energy Shield is above 50%: +10% Damage Dealt, +0.2 Speed, +10% Crit Chance. +30% Crit Damage.\n"
        "10% of your Max Health is converted to Energy Shield. 25% of Chaos damage does not bypass Energy Shield."
        "-25 HP. -2 Damage. +0.1 Speed. +5% Crit Chance. +50 Energy Shield. +10% Increased Energy Shield. -250 Armour. -250 Evasion.",
}

class Spectre(Player):
    def __init__(self, name, health = 40, damage = 6, damageType = "ethereal", speed = 1.15):
        super().__init__(name, health, damage, 0.03, 1.8, damageType, speed, className="Spectre", classDescription=SPECTRE_DESCRIPTIONS['Spectre'])
        self.ghostlyAmount = 0.1
        
        self.hollow = False
        self.reaperDamage = 0
        self.intangibilityUsed = False
        self.intangibleTurns = 0
        self.intangibleAbsorbed = 0
        self.revenantReverseDamage = False
        self.wraithHealingTotal = 0
        self.lichBuffsActive = False
        self.shiftingTurns = 0

    def _recalculateStats(self, doPrint: bool = True, inCombat: bool = False):
        super()._recalculateStats(doPrint, inCombat)

        if self._ascendancy == 'Lich':
            conversion = int(self._maxHealth * 0.1)
            self._maxHealth -= conversion
            self._stats['maxEnergyShield'] += conversion
            if not inCombat:
                self._stats['energyShield'] += conversion
            if doPrint:
                console.print(f"  [ethereal]Lich: Converted {conversion} HP to Energy Shield![/ethereal]")

    def onAttack(self, damageDealt, damageType, target=None, combatManager=None):
        super().onAttack(damageDealt, damageType, target, combatManager)
        if target:
            target = target.entity

        if damageType == 'ethereal' and target:
            ignoredArmour = target._stats['armour']
            healAmount = int(ignoredArmour * self.ghostlyAmount)

            if healAmount > 0:
                self.heal(healAmount)
                console.print(f"  [heal]Ghostly: Healed {healAmount} HP from ignored armor![/heal]")
                
                if self._ascendancy == 'Reaper':
                    shieldGain = int(ignoredArmour * 0.05)
                    self._shield += shieldGain
                    console.print(f"  [buff]Reaper: +{shieldGain} Shield![/buff]")
        
            if self._ascendancy == 'Wraith':
                self.wraithHealingTotal += healAmount
                if self.wraithHealingTotal >= 300:
                    hpLoss = self.wraithHealingTotal // 300
                    self._baseHealth = int(self._baseHealth * (1 - hpLoss * 0.01))
                    self.wraithHealingTotal = self.wraithHealingTotal % 300
                    console.print(f"  [warning]Wraith: Lost {hpLoss}% Max HP from excessive healing![/warning]")
                if target and target._stats['armour'] == 0:
                    damageDealt = int(damageDealt * 1.5)
                    console.print(f"  [buff]Wraith: Unarmored target! +50% damage![/buff]")
        
        if self._ascendancy == 'Reaper':
            damageDealt += self.reaperDamage
            if target and target._health < (target._maxHealth * 0.3):
                damageDealt = int(damageDealt * 1.15)
                console.print(f"  [buff]Reaper: Low HP target! +15% damage![/buff]")
    
        if self._ascendancy == 'Phantasm' and damageType == 'ethereal':
            if random.random() < 0.3:
                if target.phasedTurns == 0:
                    target._stats['Temporary']['speed'] -= 0.2
                target.phasedTurns = 3

        if self._ascendancy == 'Revenant' and self.intangibleTurns > 0 and damageType == 'ethereal':
            damageDealt = int(damageDealt * 1.3)

        if self._ascendancy == 'Lich' and self.lichBuffsActive:
            damageDealt = int(damageDealt * 1.1)

        return damageDealt, damageType

    def onKill(self, entity, attackData, combatManager=None):
        if self._ascendancy == 'Revenant' and not self.revenantReverseDamage:
            self.revenantReverseDamage = True

        return {}

    def heal(self, amount, doPrint: bool = True):
        if self._ascendancy == 'Lich':
            magnitude = self._stats['Bonuses']['healingMagnitude'] / 100
            modifiedAmount = int(amount * magnitude)
            if modifiedAmount > 0:
                self._stats['energyShield'] = min(
                    self.maxEnergyShield,
                    self.energyShield + modifiedAmount
                )
                console.print(f"[success]{self._name} gained {modifiedAmount} Energy Shield from healing![/success] [dim]Energy Shield: {self._stats['energyShield']} / {self._stats['maxEnergyShield']}[/dim]")
        else:
            super().heal(amount, doPrint)

    def onHit(self, damageTaken, damageType, crit=False, attacker=None, combatManager=None):
        if self._ascendancy == 'Revenant':
            if self.revenantReverseDamage:
                self.revenantReverseDamage = False
                heal = damageTaken * 2 if damageType == 'ethereal' else damageTaken
                self.heal(heal)
                console.print(f"  [heal]Revenant: The attack heals you instead! +{heal} HP.[/heal]")
                damageTaken = 0
            if self.intangibleTurns > 0:
                if damageTaken > self._maxHealth * 0.3:
                    self._health = 0
                    console.print(f"  [warning]Revenant: Massive hit while intangible! Your intangibility fades![/warning]")
                else:
                    self.intangibleAbsorbed += damageTaken
                    damageTaken = 0
                    return super().onHit(0, damageType, crit, attacker, combatManager)
            if self._health - damageTaken <= 0 and not self.intangibilityUsed:
                self._health = 1
                self.intangibilityUsed = True
                self.intangibleTurns = 1
                console.print(f"\n[gold1]Revenant: Death denied! Intangible for 1 turn![/gold1]")
                return super().onHit(0, damageType, crit, attacker, combatManager)
        
        elif self._ascendancy == 'Phantasm':
            if attacker.phasedTurns > 0:
                damageTaken = int(damageTaken * 0.9)
                if self.shiftingTurns == 0:
                    self._stats['Temporary']['increased_defenses'] += 10
                self.shiftingTurns = 2
            if damageType == 'physical':
                damageTaken = int(damageTaken * 0.7)

        elif self._ascendancy == 'Lich' and damageType == 'chaos':
            shieldHit = int(damageTaken * 0.25)
            if self.energyShield > 0 and shieldHit > 0:
                shieldDmg = min(shieldHit, self.energyShield)
                self._stats['energyShield'] -= shieldDmg
                damageTaken -= shieldDmg
                console.print(f"  [ethereal]Lich: Energy Shield absorbed {shieldDmg} chaos damage![/ethereal]")

        return super().onHit(damageTaken, damageType, crit, attacker, combatManager)

    def onTurnStart(self, combatManager=None):
        if self._ascendancy == 'Phantasm' and self.shiftingTurns > 0:
            self.shiftingTurns -= 1
            if self.shiftingTurns == 0:
                self._stats['Temporary']['increased_defenses'] -= 10

        if self._ascendancy == 'Revenant' and self.intangibleTurns > 0:
            self.intangibleTurns -= 1
            if self.intangibleTurns == 0:
                heal = self.intangibleAbsorbed
                self.heal(heal)

        if self._ascendancy == 'Lich':
            if self._stats['energyShield'] > (self._stats['maxEnergyShield'] * 0.5) and not self.lichBuffsActive:
                self._stats['Temporary']['speed'] += 0.2
                self._stats['Temporary']['critChance'] += 0.1
                self._stats['Temporary']['critMulti'] += 0.3
                self.lichBuffsActive = True
            if self._stats['energyShield'] < (self._stats['maxEnergyShield'] * 0.5):
                self._stats['Temporary']['speed'] -= 0.2
                self._stats['Temporary']['critChance'] -= 0.1
                self._stats['Temporary']['critMulti'] -= 0.3
                self.lichBuffsActive = False

        super().onTurnStart(combatManager)

    def onBattleEnd(self):
        self.hollow = False
        self.intangibilityUsed = False
        self.intangibleTurns = 0
        self.intangibleAbsorbed = 0
        self.revenantReverseDamage = False
        self.wraithHealingTotal = 0
        self.lichBuffsActive = False
        self.shiftingTurns = 0

        super().onBattleEnd()

    def updateAscendancy(self, ascendancy):
        if ascendancy == 'Wraith':
            self._baseHealth += 10
            self._baseDamage -= 1
            self._baseSpeed -= 0.05
            self.ghostlyAmount = 0.2
            self._stats['Permanent']['ethereal'] += 10
            self._ascendancy = 'Wraith'
            self.ascendancyDescription = SPECTRE_DESCRIPTIONS["Wraith"]
        elif ascendancy == 'Reaper':
            self._baseHealth -= 15
            self._baseDamage += 2
            self._baseSpeed += 0.05
            self._stats['baseCritChance'] += 0.02
            self._stats['Permanent']['added_armour'] += 100
            self._ascendancy = 'Reaper'
            self.ascendancyDescription = SPECTRE_DESCRIPTIONS["Reaper"]
        elif ascendancy == 'Phantasm':
            self._baseHealth += 20
            self._baseDamage += 1
            self._baseSpeed -= 0.1
            self.ghostlyAmount = 0.05
            self._stats['Permanent']['stunAvoidance'] -= 10
            self._stats['baseCritMulti'] += 0.25
            self._ascendancy = 'Phantasm'
            self.ascendancyDescription = SPECTRE_DESCRIPTIONS["Phantasm"]
        elif ascendancy == 'Revenant':
            self._baseHealth -= 10
            self._baseDamage += 3
            self._baseSpeed += 0.1
            self._stats['Permanent']['physical'] -= 10
            self._ascendancy = 'Revenant'
            self.ascendancyDescription = SPECTRE_DESCRIPTIONS["Revenant"]
        elif ascendancy == 'Lich':
            self._baseHealth -= 25
            self._baseDamage -= 2
            self._baseSpeed += 0.1
            self._stats['baseCritChance'] += 0.05
            self._stats['Permanent']['added_energy_shield'] += 50
            self._stats['Permanent']['increased_energy_shield'] += 10
            self._stats['Permanent']['added_armour'] -= 250
            self._stats['Permanent']['added_evasion'] -= 250
            self._ascendancy = 'Lich'
            self.ascendancyDescription = SPECTRE_DESCRIPTIONS["Lich"]
        self._recalculateStats(False)
