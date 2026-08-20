from .base import Player
from scripts.styles import console
from scripts.abilities import Effects
import random

"""
to implement:
all vengeance related things
wraith health cut should apply in _recalculateStats (self._maxHealth -= 0.01 * fadingStacks)
"""

SPECTRE_DESCRIPTIONS = {
    "Spectre": "[class_spectre]A vengeful ghost brimming with malice.[/class_spectre]\n"
        "- Ghostly: When dealing Ethereal Damage, heal equal to 10% of ignored Armour Rating on the target.\n"
        "- Whenever you are attacked by Physical or Otherworldly Damage, gain 15% of Damage Taken as Damage on your next attack.\n"
        "- Whenever an attack deals damage equal to or more than your base damage, gain 1 Vengeance. Whenever you are critically hit, gain 1 Vengeance. These two effects can occur from the same attack.\n"
        "- If there is more than one living enemy, Vengeance gain is doubled.\n"
        "- Vengeance: 10% Increased Ethereal Damage, +1% Crit Chance, +0.05 Speed. Vengeance has a maximum of 15 Stacks.\n"
        "- Whenever you critically hit an enemy, consume all Vengeance to gain +15% Crit Damage per stack consumed.\n"
        "[bold]Starting Stats:[/bold] 40 HP | 6 Damage | 3% Crit Chance | 180% Crit Damage | Ethereal Damage | 1.15 Speed.",
    #ascendancies
    "Wraith": "[lore]You were not meant to remain. Your soul fades every moment it stays. Still, let them strike you. Let them feed you. When they fall, take their souls as your own.[/lore]\n"
        "- Ghostly now heals for 20% of ignored Armour Rating. If the target has no Armour Rating, they take 50% Increased Damage.\n"
        "- Fading: For every 300 HP healed in combat through Ghostly, lose 1% Max HP permanently. Fading transfers between combats. This cannot reduce your Health below 1.\n"
        "- Vengeance has a maximum of 5 stacks. Vengeance also grants +1% Lifesteal per stack.\n"
        "- Whenever you critically hit an enemy, reset your Fading value back to 0, and heal HP equal to the progress lost.\n"
        "- Whenever Vengeance is consumed, heal equal to 5% of your Evasion Rating per Vengeance Consumed.\n"
        "- Whenever you Evade an attack, gain Added Damage equal to 50% of your Fading value on your next attack.\n"
        "[bold]Stat Changes:[/bold] +10 HP. +4 Damage. -0.05 Speed. +10% Ethereal Resistance.",
    "Reaper": "[lore]You have seen the end. You have felt its embrace. You turned it into your power. Now, watch as they fall, weak and helpless. Each target, another feast.[/lore]\n"
        "- Ghostly grants 5% of ignored Armour Rating gained as Shield.\n"
        "- Deal 15% Increased Damage to enemies below 30% Max HP. Execute Enemies under 10% Max HP on hit. Execute immediately kills the targeted enemy.\n"
        "- When Executing enemies, heal for 10% of their Max HP and gain 1% of their Damage as your own permanently per stack of Vengeance you currently have. Lose all Vengeance when you execute an enemy.\n"
        "- Whenever you critically hit an enemy, gain added Crit Damage equal to 2% of your Damage.\n"
        "- If your attack is Evaded, consume all Vengeance to heal 2% Max HP per stack consumed. If your armour mitigates more than half of an enemy's attack, double your Vengeance.\n"
        "[bold]Stat Changes:[/bold] -15 HP. -4 Damage. +0.05 Speed. +2% Crit Chance. +100 Armour.",
    "Phantasm": "[lore]They strike at you, yet you remain. They reach for you, yet you slip away. Reality itself cannot grasp you. Drink their fear as you flow through them.[/lore]\n"
        "- 30% Less Physical Damage Taken. Ghostly heals for 5% of ignored Armour Rating. Ethereal Damage has a 25% chance to apply Phased for 3 turns.\n"
        "- You have an additional 5% chance to apply Phased per stack of Vengeance. Vengeance has a maximum of 20 stacks.\n"
        "- Phased: -10% Damage Dealt, -0.2 Speed. When a Phased enemy hits you, you gain Shifting: 10% Increased Armour, Evasion, and Energy Shield for 2 turns.\n"
        "- Vengeance can no longer be consumed upon dealing critical hits. Lose 1 Vengeance when you are critically hit. Lose 2 Vengeance whenever you gain Phasing."
        "- Upon attacking a Phased enemy, heal for 1% of their Max HP per Vengeance you have.\n"
        "- Whenever you are Stunned, the enemy who stunned you loses 1% HP per stack of Vengeance you have.\n"
        "[bold]Stat Changes:[/bold] +20 HP. +6 Damage. -0.1 Speed. -10% Stun Avoidance. +25% Crit Damage.",
    "Revenant": "[lore]Death claimed you once. You became its master. Let it come again, only to be denied. Then, face your enemies, unable to touch you. Tear them asunder, then drift on to the next.[/lore]\n"
        "- Once per combat, upon taking lethal damage, survive at 1 HP and gain Intangible until the end of your turn. Intangible: Immune to Damage, +30% Increased Ethereal Damage.\n"
        "- If you take a hit larger than 30% of your Max HP whilst Intangible, you will die. Upon losing Intangible, heal equal to damage prevented whilst Intangible.\n"
        "- Gain 1% More Intangibility Damage threshold per Vengeance you have at the time of gaining Intangibility.\n"
        "- If you deal a critical hit whilst Intangible, heal for 50% of the damage dealt.\n"
        "- Whilst you are above 50% Health: 20% Reduced Defenses, +10% Crit Chance, +25% Crit Damage.\n"
        "- Upon killing an enemy, the next amount of damage you take heals you instead. The healing is doubled if the damage was Ethereal.\n"
        "[bold]Stat Changes:[/bold] -10 HP. +5 Damage. +0.1 Speed. +30% Healing Magnitude. -10% Physical Resistance.",
    "Lich": "[lore]Flesh decays. Blood dries. Bones crumble. Such trivialities mean nothing. You are free of the fetters of life. What remains cannot bleed, or die.[/lore]\n"
        "- All sources of healing are applied to Energy Shield. Ghostly heals you for 15% of ignored Armour Rating. You are immune to Bleeding.\n"
        "- While your Energy Shield is above 50%: +10% Damage Dealt, +0.2 Speed, +10% Crit Chance. +30% Crit Damage.\n"
        "- 10% of your Max Health is converted to Energy Shield. Convert 10% of your Armour and Evasion into Energy Shield. 50% Less Armour and Evasion. 25% of Chaos damage does not bypass Energy Shield.\n"
        "- Attacks deal bonus damage equal to 5% of your current Energy Shield\n"
        "- When an enemy attacks you, if they have less Health than your current Energy Shield, their attack deals 10% Less Damage.\n"
        "- When you attack an enemy, if your Maximum Energy Shield is more than their Max HP, deal 20% Increased Damage.\n"
        "- Whenever your Energy Shield is broken, gain 3 Vengeance. Upon dealing a critical hit, restore 2% Max Energy Shield per Vengeance consumed.\n"
        "[bold]Stat Changes:[/bold] -25 HP. -4 Damage. +0.1 Speed. +5% Crit Chance. +50 Energy Shield. +10% Increased Energy Shield.",
}

class Spectre(Player):
    def __init__(self, name, health = 40, damage = 6, damageType = "ethereal", speed = 1.15):
        super().__init__(name, health, damage, 0.03, 1.8, damageType, speed, className="Spectre", classDescription=SPECTRE_DESCRIPTIONS['Spectre'])
        self.ghostlyAmount = 0.1
        self.vengeance = 0
        self.maxVengeance = 15

        self.wraithFading = 0
        self.reaperDamage = 0
        self.intangibilityUsed = False
        self.intangibleTurns = 0
        self.intangibleAbsorbed = 0
        self.revenantReverseDamage = False
        self.lichBuffsActive = False
        self.shiftingTurns = 0

    def _recalculateStats(self, doPrint: bool = True, inCombat: bool = False):
        super()._recalculateStats(doPrint, inCombat)

        if self._ascendancy == 'Lich':
            conversion = int(self._maxHealth * 0.1)
            self._maxHealth -= conversion
            self._stats['max_energy_shield'] += conversion
            if not inCombat:
                self._stats['energy_shield'] += conversion
            if doPrint:
                console.print(f"  [ethereal]Lich: Converted {conversion} HP to Energy Shield![/ethereal]")

    def onExecuteCheck(self, target, combatManager):
        if self._ascendancy == 'Reaper':
            if target._health <= (target._maxHealth * 0.1):
                console.print("  [asc_reaper]Reaper: EXECUTE![/asc_reaper]")
                target.damage(target._health, 'true')
                combatManager.checkDead(target)
                heal = int(target._maxHealth * 0.1)
                dmgBuff = int(target._damage * 0.01 * self.vengeance)
                self.heal(heal)
                self.reaperDamage += dmgBuff
                self.loseAllVengeance()
                console.print(f"  [asc_reaper]Reaper: Executed {target._name}! Healed for {heal} HP and gained {dmgBuff} Damage permanently. Vengeance set to 0.[/asc_reaper]")
                self.onKill(target, {'executed': True}, combatManager)

    def onBeforeDamage(self, ability, damage, damageType, targets, combatManager):
        if self._ascendancy == 'Phantasm' and damageType == 'ethereal':
            if random.random() < (0.25 + (0.05 * self.vengeance)):
                phased = Effects.createCustom(name='phased', effectType='special', duration=3, speedBonus=-0.2, damageMultiplier=0.9)
                for enemy in targets:
                    combatManager.addStatusEffect(enemy, phased, self)
                    console.print(f"  [ethereal]Phantasm: Applied Phased to {enemy._name}![/ethereal]")

        return damage, damageType, targets

    def onAttack(self, damageDealt, damageType, target, combatManager, ability):
        damageDealt, damageType = super().onAttack(damageDealt, damageType, target, combatManager, ability)
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
                if target and target._stats['armour'] == 0:
                    damageDealt = int(damageDealt * 1.5)
                    console.print(f"[asc_wraith]Wraith: Unarmored target! +50% damage![/asc_wraith]")
        
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
        super().onKill()
        if self._ascendancy == 'Revenant' and not self.revenantReverseDamage:
            self.revenantReverseDamage = True

        return {}

    def heal(self, amount, doPrint: bool = True):
        if self._ascendancy == 'Lich':
            magnitude = self._stats['Bonuses']['healingMagnitude'] / 100
            modifiedAmount = int(amount * magnitude)
            if modifiedAmount > 0:
                self._stats['energy_shield'] = min(
                    self.maxEnergyShield,
                    self.energyShield + modifiedAmount
                )
                console.print(f"[success]{self._name} gained {modifiedAmount} Energy Shield from healing![/success] [dim]Energy Shield: {self._stats['energy_shield']} / {self._stats['max_energy_shield']}[/dim]")
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
                self._stats['energy_shield'] -= shieldDmg
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
            if self._stats['energy_shield'] > (self._stats['max_energy_shield'] * 0.5) and not self.lichBuffsActive:
                self._stats['Temporary']['speed'] += 0.2
                self._stats['Temporary']['crit_chance'] += 0.1
                self._stats['Temporary']['crit_multi'] += 0.3
                self.lichBuffsActive = True
            if self._stats['energy_shield'] < (self._stats['max_energy_shield'] * 0.5):
                self._stats['Temporary']['speed'] -= 0.2
                self._stats['Temporary']['crit_chance'] -= 0.1
                self._stats['Temporary']['crit_multi'] -= 0.3
                self.lichBuffsActive = False

        super().onTurnStart(combatManager)

    def onCombatEnd(self):
        self.intangibilityUsed = False
        self.intangibleTurns = 0
        self.intangibleAbsorbed = 0
        self.revenantReverseDamage = False
        self.lichBuffsActive = False
        self.shiftingTurns = 0

        super().onCombatEnd()

    def _removeOldAscendancy(self) -> bool:
        if self._ascendancy == 'Wraith':
            self._baseHealth -= 10
            self._baseDamage += 1
            self._baseSpeed += 0.05
            self.ghostlyAmount = 0.1
            self._stats['Permanent']['ethereal'] -= 10
        elif self._ascendancy == 'Reaper':
            self._baseHealth += 15
            self._baseDamage -= 2
            self._baseSpeed -= 0.05
            self._stats['baseCritChance'] -= 0.02
            self._stats['Permanent']['added_armour'] -= 100
        elif self._ascendancy == 'Phantasm':
            self._baseHealth -= 20
            self._baseDamage -= 1
            self._baseSpeed += 0.1
            self.ghostlyAmount = 0.1
            self._stats['Permanent']['stun_avoidance'] += 10
            self._stats['baseCritMulti'] -= 0.25
        elif self._ascendancy == 'Revenant':
            self._baseHealth += 10
            self._baseDamage -= 3
            self._baseSpeed -= 0.1
            self._stats['Permanent']['physical'] += 10
        elif self._ascendancy == 'Lich':
            self._baseHealth += 25
            self._baseDamage += 2
            self._baseSpeed -= 0.1
            self._stats['baseCritChance'] -= 0.05
            self._stats['Permanent']['added_energy_shield'] -= 50
            self._stats['Permanent']['increased_energy_shield'] -= 10
            self._stats['Permanent']['added_armour'] += 250
            self._stats['Permanent']['added_evasion'] += 250
        return True

    def updateAscendancy(self, ascendancy):
        super().updateAscendancy(ascendancy)
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
            self._stats['Permanent']['stun_avoidance'] -= 10
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
        self._recalculateStats()
