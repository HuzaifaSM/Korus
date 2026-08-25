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
        "[bold]Stat Changes:[/bold] +15 HP. +8 Damage. -0.05 Speed. +10% Ethereal Resistance.",
    "Reaper": "[lore]You have seen the end. You have felt its embrace. You turned it into your power. Now, watch as they fall, weak and helpless. Each target, another feast.[/lore]"
        "- Ghostly grants 5% of ignored Armour Rating gained as Shield.\n"
        "- Deal 15% Increased Damage to enemies below 30% Max HP. Execute Enemies under 10% Max HP on hit. Execute immediately kills the targeted enemy.\n"
        "- When Executing enemies, heal for 10% of their Max HP and gain 1% of their Damage as your own permanently per stack of Vengeance you currently have. Lose all Vengeance when you execute an enemy.\n"
        "- Whenever you critically hit an enemy, gain added Crit Damage equal to 5% of your Damage.\n"
        "- If your attack is Evaded, consume all Vengeance to heal 2% Max HP per stack consumed. If your armour mitigates more than half of an enemy's attack, double your Vengeance.\n"
        "[bold]Stat Changes:[/bold] -5 HP. -2 Damage. +0.05 Speed. +2% Crit Chance. +100 Armour.",
    "Phantasm": "[lore]They strike at you, yet you remain. They reach for you, yet you slip away. Reality itself cannot grasp you. Drink their fear as you flow through them.[/lore]"
        "- 30% Less Physical Damage Taken. Ghostly heals for 5% of ignored Armour Rating. Ethereal Damage has a 25% chance to apply Phased for 3 turns.\n"
        "- You have an additional 5% chance to apply Phased per stack of Vengeance. Vengeance has a maximum of 20 stacks.\n"
        "- Phased: -10% Damage Dealt, -0.2 Speed. When a Phased enemy attacks you, you gain Shifting: 10% Increased Armour, Evasion, and Energy Shield for 2 turns.\n"
        "- Vengeance can no longer be consumed upon dealing critical hits. Gain no Vengeance from being critically hit. Lose 2 Vengeance whenever you gain Shifting."
        "- Upon attacking a Phased enemy, heal for 1% of their Max HP per Vengeance you have.\n"
        "- Whenever you are Stunned, the enemy who stunned you loses 1% HP per stack of Vengeance you have.\n"
        "[bold]Stat Changes:[/bold] +25 HP. +8 Damage. -0.1 Speed. -10% Stun Avoidance. +25% Crit Damage.",
    "Revenant": "[lore]Death claimed you once. You became its master. Let it come again, only to be denied. Then, face your enemies, unable to touch you. Tear them asunder, then drift on to the next.[/lore]"
        "- Once per combat, upon taking lethal damage, survive at 1 HP and gain Intangible until the end of your turn. Intangible: Immune to Damage, +30% Increased Ethereal Damage.\n"
        "- If you take a hit larger than 30% of your Max HP whilst Intangible, you will die. Upon losing Intangible, heal equal to damage prevented whilst Intangible.\n"
        "- Gain 2% Added Intangibility Damage threshold per Vengeance you have.\n"
        "- If you deal a critical hit whilst Intangible, heal for 50% of the damage dealt.\n"
        "- Whilst you are above 50% Health: 20% Reduced Defenses, +10% Crit Chance, +25% Crit Damage.\n"
        "- Upon killing an enemy, the next amount of damage you take heals you instead. The healing is doubled if the damage was Ethereal.\n"
        "[bold]Stat Changes:[/bold] -5 HP. +8 Damage. +0.1 Speed. +30% Healing Magnitude. -10% Physical Resistance.",
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
        for _ in range(mult):
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
            self.heal(heal, reason="Vengeance Consumed (Wraith)")

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
            threshold = 0.1 + getattr(target, 'reaperExecuteBonus', 0)
            if getattr(target, 'reaperExecuteBonus', 0):
                target.reaperExecuteBonus = 0  # one-shot: consumed on the next check regardless of outcome
            if target._health <= (target._maxHealth * threshold):
                console.print("  [asc_reaper]Reaper: EXECUTE![/asc_reaper]")
                target.damage(target._health, 'true')
                combatManager.checkDead(target)
                heal = int(target._maxHealth * 0.1)
                dmgBuff = int(target._damage * 0.01 * self.vengeance)
                self.heal(heal, reason="Executing an Enemy (Reaper)")
                self.reaperDamage += dmgBuff
                self.loseAllVengeance()
                console.print(f"  [asc_reaper]Reaper: Executed {target._name}! Healed for {heal} HP and gained {dmgBuff} Damage permanently. Vengeance set to 0.[/asc_reaper]")
                self.onKill(target, {'executed': True}, combatManager)

    def onBeforeDamage(self, ability, damage, damageType, targets, combatManager):
        if self._ascendancy == 'Phantasm' and damageType == 'ethereal':
            if random.random() < (0.25 + (0.05 * self.vengeance)):
                phased = Effects.createCustom(name='phased', effectType='special', turns=3, speedBonus=-0.2, damageMultiplier=0.9)
                for enemy in targets:
                    combatManager.addStatusEffect(enemy, phased, self)
                    console.print(f"  [ethereal]Phantasm: Applied Phased to {enemy._name}![/ethereal]")

        return damage, damageType, targets

    def onCrit(self, targets, combatManager, critDamage):
        if self._ascendancy != 'Phantasm':
            if self.vengeance:
                console.print(f"[class_spectre]Vengeance: Consumed {self.vengeance} stack(s) for +{int(0.15 * self.vengeance * 100)}% Critical Damage![/class_spectre]")
            critDamage = int(critDamage * (1 + (0.15 * self.vengeance)))

        if self._ascendancy == 'Wraith':
            self.heal(self.wraithFading, reason="Fading (Wraith)")
            console.print(f"[asc_wraith]Wraith: Healed {self.wraithFading} HP from Fading. Fading reset to 0.[/asc_wraith]")
            self.wraithFading = 0

        elif self._ascendancy == 'Reaper':
            bonus = int(self._damage * 0.05)
            if bonus:
                console.print(f"[asc_reaper]Reaper: +{bonus} Critical Damage (5% of Damage)![/asc_reaper]")
            critDamage += bonus

        elif self._ascendancy == 'Revenant' and self.intangibleTurns > 0:
            heal = critDamage // 2
            self.heal(heal, reason="Critical Hit while Intangible (Revenant)")

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

    def onAbilityCast(self, ability, combatManager):
        if not ability:
            return
        tags = ability.tags
        selfFx = ability.effects.get('self', {})

        if 'forces_fading_reset' in tags and self._ascendancy == 'Wraith':
            self.heal(self.wraithFading, reason="Fading (Wraith)")
            console.print(f"[asc_wraith]{ability.name}: Healed {self.wraithFading} HP from Fading. Fading reset to 0.[/asc_wraith]")
            self.wraithFading = 0

        if 'grants_intangible_on_cast' in tags and self._ascendancy == 'Revenant':
            turns = selfFx.get('grant_intangible', {}).get('turns', 0)
            if turns:
                self.intangibleTurns = max(self.intangibleTurns, turns)
                console.print(f"[asc_revenant]{ability.name}: Intangible for {turns} turn(s).[/asc_revenant]")

        if 'converts_hp_to_es' in tags and self._ascendancy == 'Lich':
            fx = selfFx.get('convert_hp', {})
            amount = fx.get('hp_amount', 0)
            multiplier = fx.get('es_multiplier', 100) / 100
            if amount and self._health > amount:
                self.damage(amount, 'true', lethal=False)
                gain = int(amount * multiplier)
                self._stats['energy_shield'] = min(self.maxEnergyShield, self.energyShield + gain)
                console.print(f"[asc_lich]{ability.name}: Converted {amount} HP into {gain} Energy Shield.[/asc_lich]")

    def onAttack(self, damageDealt, damageType, target, combatManager, ability, crit):
        damageDealt, damageType = super().onAttack(damageDealt, damageType, target, combatManager, ability, crit)
        target = target.entity

        if self.damageGain:
            self._logDamage("Stored Damage from being Hit", flat=self.damageGain)
        damageDealt += self.damageGain
        self.damageGain = 0

        if ability and self._ascendancy == 'Reaper' and 'raises_execute_threshold' in ability.tags:
            amount = ability.effects.get('target', {}).get('execute_threshold_boost', {}).get('amount', 0)
            if amount:
                target.reaperExecuteBonus = getattr(target, 'reaperExecuteBonus', 0) + amount

        if ability and self._ascendancy == 'Phantasm' and 'applies_phased_directly' in ability.tags:
            target.applyPhased()

        if ability and self._ascendancy == 'Phantasm' and 'phased_vengeance_finisher' in ability.tags:
            if target.phasedTurns > 0 and self.vengeance > 0:
                fx = ability.effects.get('self', {}).get('phased_vengeance', {})
                stacksConsumed = self.vengeance
                dmgPerStack = fx.get('damage_per_stack', 0) / 100
                healPerStack = fx.get('heal_percent_per_stack', 0) / 100
                self._logDamage(f"{ability.name} ({stacksConsumed} Vengeance Consumed)", percent=dmgPerStack * stacksConsumed)
                damageDealt = int(damageDealt * (1 + (dmgPerStack * stacksConsumed)))
                heal = int(self._maxHealth * healPerStack * stacksConsumed)
                self.loseAllVengeance()
                if heal:
                    self.heal(heal, reason=f"{ability.name} (Vengeance Consumed)")
                console.print(f"[asc_phantasm]{ability.name}: Consumes {stacksConsumed} Vengeance against a Phased target for +{int(dmgPerStack * stacksConsumed * 100)}% Damage.[/asc_phantasm]")
            else:
                target.applyPhased()

        if ability and self._ascendancy == 'Revenant' and 'consumes_intangible_absorbed' in ability.tags and self.intangibleAbsorbed > 0:
            fx = ability.effects.get('self', {}).get('consume_intangible_absorbed', {})
            bonus = int(self.intangibleAbsorbed * (fx.get('damage_percent', 0) / 100))
            if bonus:
                self._logDamage(f"{ability.name} (Intangible Damage Absorbed)", flat=bonus)
            damageDealt += bonus
            console.print(f"[asc_revenant]{ability.name}: Cashes in {self.intangibleAbsorbed} absorbed damage for +{bonus} Damage.[/asc_revenant]")
            self.intangibleAbsorbed = 0

        if ability and self._ascendancy == 'Wraith' and 'consumes_fading_finisher' in ability.tags and self.wraithFading > 0:
            fx = ability.effects.get('self', {}).get('consume_fading', {})
            dmgPercent = fx.get('damage_percent_per_100', 0) / 100
            redeemAmount = fx.get('redeem_max_hp', 0)
            stacksConsumed = self.wraithFading
            self._logDamage(f"{ability.name} ({stacksConsumed} Fading Consumed)", percent=dmgPercent * (stacksConsumed / 100))
            damageDealt = int(damageDealt * (1 + dmgPercent * (stacksConsumed / 100)))
            self.wraithFading = 0
            if redeemAmount and self.wraithLostMaxHp > 0:
                redeemed = min(redeemAmount, self.wraithLostMaxHp)
                self.wraithLostMaxHp -= redeemed
                self._recalculateStats(False, True)
                console.print(f"[asc_wraith]{ability.name}: Consumes {stacksConsumed} Fading for +{int(dmgPercent * (stacksConsumed / 100) * 100)}% Damage and redeems {redeemed}% of your lost Max HP.[/asc_wraith]")
            else:
                console.print(f"[asc_wraith]{ability.name}: Consumes {stacksConsumed} Fading for +{int(dmgPercent * (stacksConsumed / 100) * 100)}% Damage.[/asc_wraith]")

        if ability and self._ascendancy == 'Lich' and 'consumes_energy_shield_finisher' in ability.tags and self.energyShield > 0:
            fx = ability.effects.get('self', {}).get('consume_es', {})
            spent = int(self.energyShield * (fx.get('percent_spent', 0) / 100))
            if spent > 0:
                self._stats['energy_shield'] -= spent
                multiplier = fx.get('damage_multiplier', 100) / 100
                if multiplier != 1:
                    self._logDamage(f"{ability.name} (Energy Shield Spent)", percent=multiplier - 1)
                damageDealt = int(damageDealt * multiplier)
                heal = int(spent * (fx.get('heal_percent_of_spent', 0) / 100))
                if heal:
                    self.heal(heal, reason=f"{ability.name} (Energy Shield Spent)")
                console.print(f"[asc_lich]{ability.name}: Spends {spent} Energy Shield for a devastating blow.[/asc_lich]")

        if damageType == 'ethereal':
            if self.vengeance:
                self._logDamage(f"Vengeance ({self.vengeance} stacks)", percent=0.1 * self.vengeance)
            damageDealt = int(damageDealt * (1 + (0.1 * self.vengeance)))
            ignoredArmour = target._stats['armour']
            healAmount = int(ignoredArmour * self.ghostlyAmount)

            if healAmount > 0:
                self.heal(healAmount, reason="Ghostly (Ignored Armour)")
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
                    self._logDamage("Unarmoured Target (Wraith)", percent=0.5)
                    damageDealt = int(damageDealt * 1.5)
                    console.print(f"[asc_wraith]Wraith: Unarmored target! +50% damage![/asc_wraith]")

        if self._ascendancy == 'Wraith' and self.wraithDamage:
            self._logDamage("Added Damage from Evasion (Wraith)", flat=self.wraithDamage)
            damageDealt += self.wraithDamage
            self.wraithDamage = 0

        if self._ascendancy == 'Reaper':
            if self.reaperDamage:
                self._logDamage("Bonus Damage from Executes (Reaper)", flat=self.reaperDamage)
            damageDealt += self.reaperDamage
            if target and target._health < (target._maxHealth * 0.3):
                self._logDamage("Low HP Target (Reaper)", percent=0.15)
                damageDealt = int(damageDealt * 1.15)
                console.print(f"  [buff]Reaper: Low HP target! +15% damage![/buff]")

        if self._ascendancy == 'Phantasm' and damageType == 'ethereal':
            if target.phasedTurns > 0:
                heal = int(target._maxHealth * 0.01 * self.vengeance)
                self.heal(heal, reason="Attacking a Phased Target (Phantasm)")
            if random.random() < 0.25 + (0.05 * self.vengeance):
                target.applyPhased()

        if self._ascendancy == 'Revenant' and self.intangibleTurns > 0 and damageType == 'ethereal':
            self._logDamage("Intangible (Revenant)", percent=0.3)
            damageDealt = int(damageDealt * 1.3)

        if self._ascendancy == 'Lich':
            if self.lichBuffsActive:
                self._logDamage("Energy Shield above 50% (Lich)", percent=0.1)
                damageDealt = int(damageDealt * 1.1)
            esBonus = int(self.energyShield * 0.05)
            if esBonus:
                self._logDamage("5% of Energy Shield (Lich)", flat=esBonus)
            damageDealt += esBonus
            if self.maxEnergyShield > target._maxHealth:
                self._logDamage("Max Energy Shield exceeds Target's Max HP (Lich)", percent=0.2)
                damageDealt = int(damageDealt * 1.2)

        return damageDealt, damageType

    def onKill(self, entity, attackData, combatManager=None):
        super().onKill()
        if self._ascendancy == 'Revenant':
            self.revenantReverseDamage = True

        # generic ability.effects.on_kill processing - available to any ascendancy ability
        ability = attackData.get('ability') if attackData else None
        healPct = ability.effects.get('on_kill', {}).get('heal_percent_max_hp', 0) if ability else 0
        if healPct:
            heal = int(self._maxHealth * healPct / 100)
            self.heal(heal, reason=ability.name)
            console.print(f"[class_spectre]{ability.name} claims its due! Healed {heal} HP.[/class_spectre]")

        return {}

    def onCC(self, attacker, combatManager):
        if self._ascendancy == 'Phantasm':
            dmg = int(attacker._maxHealth * 0.01 * self.vengeance)
            attacker.damage(dmg, 'true')

    def onStatusApplied(self, status, attacker):
        if self._ascendancy == 'Lich' and status.name == 'bleed':
            return None

        return status

    def heal(self, amount, doPrint: bool = True, reason: str = None):
        if self._ascendancy == 'Lich':
            magnitude = self._stats['Bonuses']['healing_magnitude'] / 100
            modifiedAmount = int(amount * magnitude)
            reasonStr = f" due to {reason}" if reason else ""
            if modifiedAmount > 0:
                self._stats['energy_shield'] = min(
                    self.maxEnergyShield,
                    self.energyShield + modifiedAmount
                )
                console.print(f"[success]{self._name} gained {modifiedAmount} Energy Shield from healing{reasonStr}![/success] [dim]Energy Shield: {self._stats['energy_shield']} / {self._stats['max_energy_shield']}[/dim]")
        else:
            super().heal(amount, doPrint, reason)

    def onEvade(self, combatManager):
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
                attacker._logDamage(f"{self._name}'s Post-Kill Damage Reversal (Revenant)", percent=-1.0)
                self.heal(heal, reason="Post-Kill Damage Reversal (Revenant)")
                console.print(f"  [heal]Revenant: The attack heals you instead! +{heal} HP.[/heal]")
                damageTaken = 0
            if self.intangibleTurns > 0:
                if damageTaken > self._maxHealth * (0.3 + (0.02 * self.vengeance)):
                    self._health = 0
                    console.print(f"  [warning]Revenant: Massive hit while intangible! Your intangibility fades![/warning]")
                else:
                    attacker._logDamage(f"{self._name}'s Intangible (Revenant)", percent=-1.0)
                    self.intangibleAbsorbed += damageTaken
                    damageTaken = 0
                    return super().onHit(0, damageType, crit, attacker, combatManager)
            if self._health - damageTaken <= 0 and not self.intangibilityUsed:
                self._health = 1
                self.intangibilityUsed = True
                self.intangibleTurns = 1
                attacker._logDamage(f"{self._name}'s Death Denied (Revenant)", percent=-1.0)
                console.print(f"\n[gold1]Revenant: Death denied! Intangible for 1 turn![/gold1]")
                return super().onHit(0, damageType, crit, attacker, combatManager)

        elif self._ascendancy == 'Phantasm':
            if attacker.phasedTurns > 0:
                self.phantasmGainShifting()
            if damageType == 'physical':
                attacker._logDamage(f"{self._name}'s Reduced Physical Damage Taken (Phantasm)", percent=-0.3)
                damageTaken = int(damageTaken * 0.7)

        elif self._ascendancy == 'Lich':
            if attacker._health < self.energyShield:
                attacker._logDamage(f"{self._name}'s Energy Shield exceeds Attacker's HP (Lich)", percent=-0.1)
                damageTaken = int(damageTaken * 0.9)
            if damageType == 'chaos':
                shieldHit = int(damageTaken * 0.25)
                if self.energyShield > 0 and shieldHit > 0:
                    shieldDmg = min(shieldHit, self.energyShield)
                    attacker._logDamage(f"{self._name}'s Energy Shield absorption (Lich)", flat=-shieldDmg)
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
                    self.heal(heal, reason="Damage Absorbed while Intangible (Revenant)")
                    self.intangibleAbsorbed = 0
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

    ASCENDANCY_DELTAS = {
        'Wraith': {
            '_baseHealth': 15,
            '_baseDamage': 8,
            '_baseSpeed': -0.05,
            '_stats.Permanent.ethereal': 10,
        },
        'Reaper': {
            '_baseHealth': -5,
            '_baseDamage': -2,
            '_baseSpeed': 0.05,
            '_stats.baseCritChance': 0.02,
            '_stats.Permanent.added_armour': 100,
        },
        'Phantasm': {
            '_baseHealth': 25,
            '_baseDamage': 8,
            '_baseSpeed': -0.1,
            '_stats.Permanent.stun_avoidance': -10,
            '_stats.baseCritMulti': 0.25,
        },
        'Revenant': {
            '_baseHealth': -5,
            '_baseDamage': 8,
            '_baseSpeed': 0.1,
            '_stats.Permanent.healing_magnitude': 30,
            '_stats.Permanent.physical': -10,
        },
        'Lich': {
            '_baseHealth': -25,
            '_baseDamage': -4,
            '_baseSpeed': 0.1,
            '_stats.baseCritChance': 0.05,
            '_stats.Permanent.added_energy_shield': 50,
            '_stats.Permanent.increased_energy_shield': 10,
        },
    }

    def _removeOldAscendancy(self) -> bool:
        self.maxVengeance = 15
        if self._ascendancy == 'Wraith':
            self.ghostlyAmount = 0.1
        elif self._ascendancy == 'Phantasm':
            self.ghostlyAmount = 0.1
        delta = self.ASCENDANCY_DELTAS.get(self._ascendancy)
        if delta:
            self._applyStatDelta(delta, sign=-1)
        return True

    def updateAscendancy(self, ascendancy):
        if not super().updateAscendancy(ascendancy):
            return
        self._ascendancy = ascendancy
        self.ascendancyDescription = SPECTRE_DESCRIPTIONS[ascendancy]
        self._applyStatDelta(self.ASCENDANCY_DELTAS[ascendancy], sign=1)
        if ascendancy == 'Wraith':
            self.ghostlyAmount = 0.2
            self.maxVengeance = 5
        elif ascendancy == 'Phantasm':
            self.ghostlyAmount = 0.05
        self._recalculateStats()
        self.gainClassAbilities(True)
        return True
