from .base import Player, OTHERWORLD_RES
from scripts.styles import console
from scripts.abilities import Effects
import random

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
    "Wraith": "[lore]You were not meant to remain. Your soul fades every moment it stays. Still, let them strike you. Let them feed you. When they fall, take their souls as your own.[/lore]"
        "- Ghostly now heals for 20% of ignored Armour Rating. If the target has no Armour Rating, they take 50% Increased Damage.\n"
        "- Fading: For every 300 HP healed in combat through Ghostly, lose 1% Max HP permanently. Fading transfers between combats. This cannot reduce your Health below 1.\n"
        "- Vengeance has a maximum of 5 stacks. Vengeance also grants +1% Lifesteal per stack.\n"
        "- Whenever you critically hit an enemy, reset your Fading value back to 0, and heal HP equal to the progress lost.\n"
        "- Whenever Vengeance is consumed, heal equal to 3% of your Evasion Rating per Vengeance Consumed.\n"
        "- Whenever you Evade an attack, gain Added Damage equal to 50% of your Fading value on your next attack.\n"
        "[bold]Stat Changes:[/bold] +10 HP. +4 Damage. -0.05 Speed. +10% Ethereal Resistance.",
    "Reaper": "[lore]You have seen the end. You have felt its embrace. You turned it into your power. Now, watch as they fall, weak and helpless. Each target, another feast.[/lore]"
        "- Ghostly grants 5% of ignored Armour Rating gained as Shield.\n"
        "- Deal 15% Increased Damage to enemies below 30% Max HP. Execute Enemies under 10% Max HP on hit. Execute immediately kills the targeted enemy.\n"
        "- When Executing enemies, heal for 10% of their Max HP and gain 1% of their Damage as your own permanently per stack of Vengeance you currently have. Lose all Vengeance when you execute an enemy.\n"
        "- Whenever you critically hit an enemy, gain added Crit Damage equal to 5% of your Damage.\n"
        "- If your attack is Evaded, consume all Vengeance to heal 2% Max HP per stack consumed. If your armour mitigates more than half of an enemy's attack, double your Vengeance.\n"
        "[bold]Stat Changes:[/bold] -15 HP. -4 Damage. +0.05 Speed. +2% Crit Chance. +100 Armour.",
    "Phantasm": "[lore]They strike at you, yet you remain. They reach for you, yet you slip away. Reality itself cannot grasp you. Drink their fear as you flow through them.[/lore]"
        "- 30% Less Physical Damage Taken. Ghostly heals for 5% of ignored Armour Rating. Ethereal Damage has a 25% chance to apply Phased for 3 turns.\n"
        "- You have an additional 5% chance to apply Phased per stack of Vengeance. Vengeance has a maximum of 20 stacks.\n"
        "- Phased: -10% Damage Dealt, -0.2 Speed. When a Phased enemy attacks you, you gain Shifting: 10% Increased Armour, Evasion, and Energy Shield for 2 turns.\n"
        "- Vengeance can no longer be consumed upon dealing critical hits. Gain no Vengeance from being critically hit. Lose 2 Vengeance whenever you gain Shifting."
        "- Upon attacking a Phased enemy, heal for 1% of their Max HP per Vengeance you have.\n"
        "- Whenever you are Stunned, the enemy who stunned you loses 1% HP per stack of Vengeance you have.\n"
        "[bold]Stat Changes:[/bold] +20 HP. +6 Damage. -0.1 Speed. -10% Stun Avoidance. +25% Crit Damage.",
    "Revenant": "[lore]Death claimed you once. You became its master. Let it come again, only to be denied. Then, face your enemies, unable to touch you. Tear them asunder, then drift on to the next.[/lore]"
        "- Once per combat, upon taking lethal damage, survive at 1 HP and gain Intangible until the end of your turn. Intangible: Immune to Damage, +30% Increased Ethereal Damage.\n"
        "- If you take a hit larger than 30% of your Max HP whilst Intangible, you will die. Upon losing Intangible, heal equal to damage prevented whilst Intangible.\n"
        "- Gain 2% Added Intangibility Damage threshold per Vengeance you have.\n"
        "- If you deal a critical hit whilst Intangible, heal for 50% of the damage dealt.\n"
        "- Whilst you are above 50% Health: 20% Reduced Defenses, +10% Crit Chance, +25% Crit Damage.\n"
        "- Upon killing an enemy, the next amount of damage you take heals you instead. The healing is doubled if the damage was Ethereal.\n"
        "[bold]Stat Changes:[/bold] -10 HP. +5 Damage. +0.1 Speed. +30% Healing Magnitude. -10% Physical Resistance.",
    "Lich": "[lore]Flesh decays. Blood dries. Bones crumble. Such trivialities mean nothing. You are free of the fetters of life. What remains cannot bleed, or die.[/lore]"
        "- All sources of healing are applied to Energy Shield. Ghostly heals you for 15% of ignored Armour Rating. You are immune to Bleeding.\n"
        "- While your Energy Shield is above 50%: +10% Damage Dealt, +0.2 Speed, +10% Crit Chance. +30% Crit Damage.\n"
        "- 10% of your Max Health is converted to Energy Shield. Convert 10% of your Armour and Evasion into Energy Shield. 50% Less Armour and Evasion. 25% of Chaos damage does not bypass Energy Shield.\n"
        "- Attacks deal bonus damage equal to 5% of your current Energy Shield.\n"
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
        self.damageGain = 0

        self.wraithFading = 0
        self.wraithLostMaxHp = 0
        self.wraithDamage = 0
        self.reaperDamage = 0
        self.shiftingTurns = 0
        self.intangibilityUsed = False
        self.intangibleTurns = 0
        self.intangibleAbsorbed = 0
        self.revenantAbove50LastTurn = False
        self.revenantReverseDamage = False
        self.lichBuffsActive = False

    def gainVengeance(self, combatManager=None):
        """intentionally leave combatManager empty if only giving 1 vengeance"""
        if combatManager:
            mult = 2 if len(combatManager.allAlive) > 1 else 1
        else:
            mult = 1
        for _ in mult:
            if self.vengeance < self.maxVengeance:
                self.vengeance += 1
                self._stats['Temporary']['crit_chance'] += 0.01
                self._stats['Temporary']['speed'] += 0.05
                if self._ascendancy == 'Wraith':
                    self._stats['Temporary']['lifesteal'] += 1

    def loseAllVengeance(self):
        for _ in range(self.vengeance):
            self._stats['Temporary']['crit_chance'] -= 0.01
            self._stats['Temporary']['speed'] -= 0.05
            if self._ascendancy == 'Wraith':
                self._stats['Temporary']['lifesteal'] -= 1

        if self._ascendancy == 'Wraith':
            heal = int(self.vengeance * 0.03 * self.evasion)
            self.heal(heal)

        self.vengeance = 0

    def loseVengeance(self, amount: int=1):
        for _ in range(amount):
            if self.vengeance > 0:
                self._stats['Temporary']['crit_chance'] -= 0.01
                self._stats['Temporary']['speed'] -= 0.05
                self.vengeance -= 2

    def phantasmGainShifting(self):
        if self.shiftingTurns == 0:
            self._stats['Temporary']['increased_defenses'] += 10
            self.loseVengeance(2)
        self.shiftingTurns = 2

    def _recalculateStats(self, doPrint: bool = True, inCombat: bool = False):
        super()._recalculateStats(doPrint, inCombat)

        if self._ascendancy == 'Wraith':
            self._maxHealth = max(1, int(self._maxHealth * (1 - (0.01 * self.wraithLostMaxHp))))

        elif self._ascendancy == 'Lich':
            conversion = int(self._maxHealth * 0.1)
            self._maxHealth -= conversion
            armourToES = int(self.armour * 0.1)
            evToES = int(self.evasion * 0.1)
            self._stats['armour'] -= armourToES
            self._stats['armour'] //= 2
            self._stats['evasion'] -= evToES
            self._stats['evasion'] //= 2
            self._stats['max_energy_shield'] += conversion + armourToES + evToES
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

    def onCrit(self, targets, combatManager, critDamage):
        if self._ascendancy != 'Phantasm':
            critDamage = int(critDamage * (1 + (0.15 * self.vengeance)))

        if self._ascendancy == 'Wraith':
            self.heal(self.wraithFading)
            console.print(f"[asc_wraith]Wraith: Healed {self.wraithFading} HP from Fading. Fading reset to 0.[/asc_wraith]")
            self.wraithFading = 0

        elif self._ascendancy == 'Reaper':
            critDamage += int(self._damage * 0.05)

        elif self._ascendancy == 'Revenant' and self.intangibleTurns > 0:
            heal = critDamage // 2
            self.heal(heal)

        elif self._ascendancy == 'Lich':
            esRestore = int(self.maxEnergyShield * 0.02 * self.vengeance)
            self._stats['energy_shield'] = min(self.maxEnergyShield, self.energyShield + esRestore)
            console.print(f"[asc_lich]Lich: Restored {esRestore} Energy Shield from dealing a critical hit![/asc_lich]")

        self.vengeance = 0

        return critDamage

    def onDealDamage(self, target, targetUnit, finalDamage, damageType, evaded, armourDamagePrevented, esDamagePrevented, combatManager):
        if self._ascendancy == 'Reaper':
            heal = int(self._maxHealth * 0.02 * self.vengeance)
            self.heal(heal, False)
            self.vengeance = 0
            console.print(f"[asc_reaper]Reaper: Your attack was Evaded! Consumed all Vengeance to heal for a total of {heal} HP.[/asc_reaper]")

        return finalDamage

    def onAttack(self, damageDealt, damageType, target, combatManager, ability, crit):
        damageDealt, damageType = super().onAttack(damageDealt, damageType, target, combatManager, ability, crit)
        target = target.entity

        damageDealt += self.damageGain
        self.damageGain = 0

        if damageType == 'ethereal':
            damageDealt = int(damageDealt * (1 + (0.1 * self.vengeance)))
            ignoredArmour = target._stats['armour']
            healAmount = int(ignoredArmour * self.ghostlyAmount)

            if healAmount > 0:
                self.heal(healAmount)
                console.print(f"  [heal]Ghostly: Healed {healAmount} HP from ignored armor![/heal]")

                if self._ascendancy == 'Wraith':
                    self.wraithFading += healAmount
                    while self.wraithFading >= 300:
                        self.wraithFading -= 300
                        self.wraithLostMaxHp += 1

                elif self._ascendancy == 'Reaper':
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
            if target.phasedTurns > 0:
                heal = int(target._maxHealth * 0.01 * self.vengeance)
                self.heal(heal)
            if random.random() < 0.25 + (0.05 * self.vengeance):
                target.applyPhased()

        if self._ascendancy == 'Revenant' and self.intangibleTurns > 0 and damageType == 'ethereal':
            damageDealt = int(damageDealt * 1.3)

        if self._ascendancy == 'Lich':
            if self.lichBuffsActive:
                damageDealt = int(damageDealt * 1.1)
            damageDealt += int(self.energyShield * 0.05)
            if self.maxEnergyShield > target._maxHealth:
                damageDealt = int(damageDealt * 1.2)

        return damageDealt, damageType

    def onKill(self, entity, attackData, combatManager=None):
        super().onKill()
        if self._ascendancy == 'Revenant':
            self.revenantReverseDamage = True

        return {}

    def onCC(self, attacker, combatManager):
        if self._ascendancy == 'Phantasm':
            dmg = int(attacker._maxHealth * 0.01 * self.vengeance)
            attacker.damage(dmg, 'true')

    def onStatusApplied(self, status, attacker):
        if self._ascendancy == 'Lich' and status.name == 'bleed':
            return None

        return status

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

    def onEvade(self):
        if self._ascendancy == 'Wraith':
            self.wraithDamage += self.wraithFading // 2

    def onEnergyShieldBroken(self, combatManager):
        if self._ascendancy == 'Lich':
            for _ in range(3):
                self.gainVengeance()

    def onAfterMitigation(self, attacker, finalDamage, damageType, evaded, armourDamagePrevented, esDamagePrevented, preMitigationDamage, combatManager):
        if self._ascendancy == 'Reaper':
            if armourDamagePrevented > preMitigationDamage // 2:
                for _ in range(self.vengeance):
                    self.gainVengeance()

        return finalDamage

    def onHit(self, damageTaken, damageType, crit, attacker, combatManager):
        damageTaken, damageType = super().onHit(damageTaken, damageType, crit, attacker, combatManager)
        if damageType in OTHERWORLD_RES or damageType == 'physical':
            self.damageGain += int(damageTaken * 0.15)

        if damageTaken >= self._baseDamage:
            self.gainVengeance(combatManager)

        if self._ascendancy == 'Revenant':
            if self.revenantReverseDamage:
                self.revenantReverseDamage = False
                heal = damageTaken * 2 if damageType == 'ethereal' else damageTaken
                self.heal(heal)
                console.print(f"  [heal]Revenant: The attack heals you instead! +{heal} HP.[/heal]")
                damageTaken = 0
            if self.intangibleTurns > 0:
                if damageTaken > self._maxHealth * (0.3 + (0.02 * self.vengeance)):
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
                self.phantasmGainShifting()
            if damageType == 'physical':
                damageTaken = int(damageTaken * 0.7)

        elif self._ascendancy == 'Lich':
            if attacker._health < self.energyShield:
                damageTaken = int(damageTaken * 0.9)
            if damageType == 'chaos':
                shieldHit = int(damageTaken * 0.25)
                if self.energyShield > 0 and shieldHit > 0:
                    shieldDmg = min(shieldHit, self.energyShield)
                    self._stats['energy_shield'] -= shieldDmg
                    damageTaken -= shieldDmg
                    console.print(f"[asc_lich]Lich: Energy Shield absorbed {shieldDmg} chaos damage![/asc_lich]")

        return damageTaken, damageType

    def onCriticallyHit(self, attacker, combatManager, critDamage, damageType):
        critDamage = super().onCriticallyHit(attacker, combatManager, critDamage, damageType)
        if self._ascendancy != 'Phantasm':
            self.gainVengeance(combatManager)

        return critDamage

    def onTurnStart(self, combatManager=None):
        if self._ascendancy == 'Phantasm' and self.shiftingTurns > 0:
            self.shiftingTurns -= 1
            if self.shiftingTurns == 0:
                self._stats['Temporary']['increased_defenses'] -= 10

        elif self._ascendancy == 'Revenant':
            if self.intangibleTurns > 0:
                self.intangibleTurns -= 1
                if self.intangibleTurns == 0:
                    heal = self.intangibleAbsorbed
                    self.heal(heal)
            if self.revenantAbove50LastTurn and self._health < self._maxHealth // 2:
                self.revenantAbove50LastTurn = False
                self._stats['Temporary']['increased_defenses'] += 20
                self._stats['Temporary']['crit_chance'] -= 0.1
                self._stats['Temporary']['crit_multi'] -= 0.25
            elif not self.revenantAbove50LastTurn and self._health > self._maxHealth // 2:
                self.revenantAbove50LastTurn = True
                self._stats['Temporary']['increased_defenses'] -= 20
                self._stats['Temporary']['crit_chance'] += 0.1
                self._stats['Temporary']['crit_multi'] += 0.25

        elif self._ascendancy == 'Lich':
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
        self.maxVengeance = 15
        if self._ascendancy == 'Wraith':
            self._baseHealth -= 10
            self._baseDamage -= 4
            self._baseSpeed += 0.05
            self.ghostlyAmount = 0.1
            self._stats['Permanent']['ethereal'] -= 10
        elif self._ascendancy == 'Reaper':
            self._baseHealth += 15
            self._baseDamage += 4
            self._baseSpeed -= 0.05
            self._stats['baseCritChance'] -= 0.02
            self._stats['Permanent']['added_armour'] -= 100
        elif self._ascendancy == 'Phantasm':
            self._baseHealth -= 20
            self._baseDamage -= 6
            self._baseSpeed += 0.1
            self.ghostlyAmount = 0.1
            self.maxVengeance = 20
            self._stats['Permanent']['stun_avoidance'] += 10
            self._stats['baseCritMulti'] -= 0.25
        elif self._ascendancy == 'Revenant':
            self._baseHealth += 10
            self._baseDamage -= 5
            self._baseSpeed -= 0.1
            self._stats['Permanent']['healing_magnitude'] -= 30
            self._stats['Permanent']['physical'] += 10
        elif self._ascendancy == 'Lich':
            self._baseHealth += 25
            self._baseDamage += 4
            self._baseSpeed -= 0.1
            self._stats['baseCritChance'] -= 0.05
            self._stats['Permanent']['added_energy_shield'] -= 50
            self._stats['Permanent']['increased_energy_shield'] -= 10
        return True

    def updateAscendancy(self, ascendancy):
        if not super().updateAscendancy(ascendancy):
            return
        self._ascendancy = ascendancy
        self.ascendancyDescription = SPECTRE_DESCRIPTIONS[ascendancy]
        if ascendancy == 'Wraith':
            self._baseHealth += 10
            self._baseDamage += 4
            self._baseSpeed -= 0.05
            self.ghostlyAmount = 0.2
            self.maxVengeance = 5
            self._stats['Permanent']['ethereal'] += 10
        elif ascendancy == 'Reaper':
            self._baseHealth -= 15
            self._baseDamage -= 4
            self._baseSpeed += 0.05
            self._stats['baseCritChance'] += 0.02
            self._stats['Permanent']['added_armour'] += 100
        elif ascendancy == 'Phantasm':
            self._baseHealth += 20
            self._baseDamage += 6
            self._baseSpeed -= 0.1
            self.ghostlyAmount = 0.05
            self._stats['Permanent']['stun_avoidance'] -= 10
            self._stats['baseCritMulti'] += 0.25
        elif ascendancy == 'Revenant':
            self._baseHealth -= 10
            self._baseDamage += 5
            self._baseSpeed += 0.1
            self._stats['Permanent']['healing_magnitude'] += 30
            self._stats['Permanent']['physical'] -= 10
        elif ascendancy == 'Lich':
            self._baseHealth -= 25
            self._baseDamage -= 4
            self._baseSpeed += 0.1
            self._stats['baseCritChance'] += 0.05
            self._stats['Permanent']['added_energy_shield'] += 50
            self._stats['Permanent']['increased_energy_shield'] += 10
        self._recalculateStats()
