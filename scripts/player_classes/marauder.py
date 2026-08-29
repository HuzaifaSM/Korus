from .base import Player, ELEMENTAL_RES, DIVINE_RES
from scripts.styles import console, pause
import random

MARAUDER_DESCRIPTIONS = {
    "Marauder": "[class_marauder]A ruthless hunter, pillaging its foes whilst fighting and forcing their hand.[/class_marauder]\n"
        "- If you attack an enemy who has already acted, apply Echo to them, dealing damage equal to 35% of the damage dealt. Echo activates at the start of your turn and deals Cold damage.\n"
        "- If you attack an enemy before they have acted, Siphon 1-3 of their base Damage. You cannot steal Damage equal to more than your 1.5x level, rounded up. You cannot reduce an enemy's base damage below 5.\n"
        "- If an enemy attacks you before you have acted, they steal 1 Siphoned Damage back if possible.\n"
        "- If an enemy fails to steal Siphoned Damage from you, gain +1 Damage Reduction for the rest of combat, up to a maximum equal to 2x your level.\n"
        "- If an enemy attacks you after you have acted, they deal 10% Less Damage to you. At the end of combat, heal 1% Max HP per Siphoned Damage, to a maximum heal of 30%.\n"
        "[bold]Starting Stats:[/bold] 60 HP | 4 Damage | 4% Crit Chance | 130% Crit Damage | Cold Damage | 0.8 Speed.",
    # ascendancies
    "Colossus": "[lore]Dodge? Their hits do nothing. Stand your ground, and trample over theirs. Every strike is a statement of dominance.[/lore]"
        "- Convert 50% of your Evasion into Armour, and 10% of your Evasion as Energy Shield. You have no Evasion.\n"
        "- The first time your Energy Shield is broken in combat, gain 1% Increased Damage per 5 Maximum Energy Shield you have for the rest of combat. Elemental damage against you treats your armour as 130% of its value.\n"
        "- If an enemy attacks you before you have acted, your next attack gains damage equal to damage prevented by Armour and Energy Shield by that hit.\n"
        "- If you attack an enemy after they have acted, apply stack of 1 Crush, to a maximum of 3 stacks. Crush: 15% Reduced Armour.\n"
        "- Damage dealt from Echo is reduced to 15% of the damage dealt, but is applied as True damage instead of Cold.\n"
        "- Upon killing an enemy, for the rest of combat: Gain 20% of their Armour as Added Armour, Regenerate Energy Shield equal to 10% of their Armour or Max Energy Shield, whichever is higher.\n"
        "[bold]Stat Changes:[/bold] -15 HP. +4 Damage. -0.1 Speed. +100 Armour. +20 Energy Shield.",
    "Dreadnought": "[lore]Might. That's all that matters on the battlefield. Each wound heals before it opens. Each scar amplifies your strength. Each hit, another reason to decimate them.[/lore]"
        "- 20% Increased Maximum Life. Convert 10% of your Armour and Evasion, and 20% of your Maximum Energy Shield into Max Health.\n"
        "- When an attack reduces your health, 50% of the damage is Deferred. Deferred damage is dealt to you 1 turn later as Cold Damage.\n"
        "- Gain 20% of Deferred damage as bonus damage for the rest of combat, to a maximum equal to 30% of your Max HP.\n"
        "- If an enemy attacks you before you have acted, if their current Health is less than your current Health, the damage is reduced by 15% and they automatically fail to steal Siphoned Damage.\n"
        "- If an enemy attacks you after you have acted, they take True Damage equal to 5% of your Max HP, and you heal for the same amount.\n"
        "- Healing has a 30% chance to Echo, applying its heal again at the start of your next turn at 50% value.\n"
        "- If you attack an enemy after before have acted, heal for 10% of the damage dealt, and Siphon up to twice as much damage if possible.\n"
        "[bold]Stat Changes:[/bold] +30 Health. -5 Damage. -0.1 Speed. +50% Healing Magnitude. +15% Cold Resistance. +5% Maximum Cold Resistance.",
    "Sovereign": "[lore]You sit atop the throne of war. Each move flawless and unforgiving. Their pride will be their end.[/lore]"
        "- If you attack an enemy after they have acted, deal 25% Increased Cold Damage, heal for 10% of the damage dealt to them, and reduce their base speed by 1% of your speed.\n"
        "- If you attack an enemy before they have acted, gain +25% Crit Chance and +75% Crit Damage against them.\n"
        "- If an enemy attacks you before you have acted, apply Shame to them for 2 turns. Shame: Deal 10% Less Damage, -0.1 Speed.\n"
        "- If an enemy attacks you after you have acted, they deal 20% Less Damage to you, increased to 30% Less Damage if the damage is Divine.\n"
        "[bold]Stat Changes:[/bold] +30 HP. +6 Damage. -0.1 Speed. +5 Stamina Regen. +10% Holy Resistance.",
    "Harrower": "[lore]Their strength is useless. Cripple them instead. Rain blows upon them. Steal even their ability to flee.[/lore]"
        "- Siphon Speed instead of Damage. You can Siphon up to 0.5 Speed total. Siphon 0.02 Speed per 1 Damage that would have been Siphoned. Enemies cannot steal Siphoned Speed.\n"
        "- If you have Siphoned more than 0.25 Speed, gain 40% Increased Damage, 10% Elemental Resistance and 20% Physical Resistance.\n"
        "- If you attack an enemy before they have acted, they are executed if they have less than 8% Max HP remaining. Executing an enemy grants you Empowerment for the rest of combat.\n"
        "- Empowerment: +30% Increased Cold Damage, +20 HP Regen, -0.2 Speed.\n"
        "- If an enemy attacks you after you have acted, their Speed is reduced by 5%, and they take Cold Damage equal to their base damage.\n"
        "- If an enemy attacks you before you have acted, their hit treats your Evasion as 150% of its actual value.\n"
        "[bold]Stat Changes:[/bold] -10 HP. +10 Damage. +0.1 Speed. +5% Crit Chance. +25% Crit Damage.",
    "Butcher": "[lore]Their fear tastes so sweet. Revel in delight as you carve them up, one by one. Watch as they cower in fear.[/lore]"
        "- At the start of combat, apply Marked to a random enemy. Marked: 25% Increased Damage Taken, 10% Increased Damage Dealt.\n"
        "- When you kill a Marked enemy, Siphon all of its base damage, ignoring your cap, and deal Cold Damage to all enemies equal to 500% of the killed enemy's base damage.\n"
        "- Mark a new random enemy when the current Marked enemy dies.\n"
        "- Upon dealing a critical hit, gain 1 Slaughter, to a maximum of 5. Slaughter: 10% Increased Cold Damage, +15% Crit Damage.\n"
        "- If an enemy attacks you after you have acted, deal Cold Damage to them equal to your Siphoned damage.\n"
        "- If you attack an enemy after they have acted, apply Carved to them, up to 3 times. Carved: -5% Crit Chance, 5% Less Defenses.\n"
        "[bold]Stat Changes:[/bold] +10 HP. +6 Damage. +0.1 Speed. +5% Crit Chance. -25% Crit Multi. -10% Fire Resistance."
}

class Marauder(Player):
    def __init__(self, name, health=60, damage=4, damageType="cold", speed=0.8):
        super().__init__(name,health, damage, 0.04, 1.3, damageType, speed, className="Marauder", classDescription=MARAUDER_DESCRIPTIONS["Marauder"])
        self.siphonedDamage = 0
        self.echoDamage = {} # entity: echoDamage
        self._recentlyActedEnemies = set()

        self.colossusEsBroken = False
        self.colossusDamage = 0
        self.colossusRetaliateCharges = 0
        self.dreadnoughtDeferredDamage = {2: 0, 1: 0}
        self.dreadnoughtDamage = 0
        self.dreadnoughtEchoHeal = 0
        self.harrowerSiphonedSpeed = 0
        self.harrowerSpeedBuffGained = False
        self.harrowerEmpowered = False
        self.butcherMarkedTarget = None
        self.butcherDamage = 0
        self.butcherSlaughter = 0
        self._butcherSlaughterfeastLifesteal = 0
        self._harrowerExecuteReady = False
        self._sovereignCritBuffed = False
        self._sovereignForceAmbush = False

    @property
    def maxSiphon(self):
        return round(self._level * 1.5)

    def gainDamageReduction(self):
        if self._stats['Temporary']['damage_reduction'] < self._level * 2:
            self._stats['Temporary']['damage_reduction'] += 1

    def checkHarrowerBuff(self):
        if self._stats['Temporary']['speed'] >= 0.25 and not self.harrowerSpeedBuffGained:
            self.harrowerSpeedBuffGained = True
            self._stats['Temporary']['elemental'] += 10
            self._stats['Temporary']['physical'] += 20

    def empowerHarrower(self):
        if not self.harrowerEmpowered:
            self.harrowerEmpowered = True
            self._stats['Temporary']['speed'] -= 0.2
            self._stats['Temporary']['hp_regen'] += 20

    def _setButcherMark(self, target):
        if self.butcherMarkedTarget is not None and self.butcherMarkedTarget is not target and not self.butcherMarkedTarget._isDead:
            self.butcherMarkedTarget.unmark()
        self.butcherMarkedTarget = target
        target.marked = True

    def applyButcherMark(self, allEnemies):
        if self.butcherMarkedTarget is None and allEnemies:
            target = random.choice(allEnemies)
            self._setButcherMark(target)
            console.print(f"[asc_butcher]Butcher: Marked {target._name}. 25% Increased Damage dealt to them. They deal 10% Increased Damage[/asc_butcher]")
            pause()

    def _recalculateStats(self, doPrint = True, inCombat = False):
        super()._recalculateStats(doPrint, inCombat)

        if self._ascendancy == 'Colossus':
            evToArmour = int(self.evasion * 0.5)
            evToEs = int(self.evasion * 0.1)
            self._stats['armour'] += evToArmour
            self._stats['energy_shield'] += evToEs
            self._stats['evasion'] = 0

            if doPrint:
                console.print(f"[asc_colossus]Colossus: Converted 50% of Evasion ({evToArmour}) to Armour. Converted 10% of Evasion ({evToEs}) to Energy Shield. Evasion set to 0.[/asc_colossus]")

        elif self._ascendancy == 'Dreadnought':
            armourToHP = int(self.armour * 0.1)
            evToHP = int(self.evasion * 0.1)
            esToHp = int(self.maxEnergyShield * 0.2)
            self._stats['armour'] -= armourToHP
            self._stats['evasion'] -= evToHP
            self._stats['energy_shield'] -= esToHp

            self._maxHealth += armourToHP + evToHP + esToHp

            if doPrint:
                console.print(f"[asc_dreadnought]Dreadnought: Converted 10% of Armour ({armourToHP}), 10% of Evasion ({evToHP}), and 20% of Energy Shield ({esToHp}) to Max Health. Total Health Gained: {armourToHP + evToHP + esToHp}[/asc_dreadnought]")

    def onHeal(self, healAmount):
        if self._ascendancy == 'Dreadnought' and random.random() < 0.3:
            self.dreadnoughtEchoHeal += healAmount // 2

    def getEffectiveEvasion(self, damageType, combatUnit):
        if self._ascendancy == 'Harrower' and not combatUnit.hasActed:
            return self.evasion * 1.5
        return super().getEffectiveEvasion(damageType, combatUnit)

    def getEffectiveArmour(self, damageType, combatUnit):
        if self._ascendancy == 'Colossus' and damageType in ELEMENTAL_RES:
            return self.armour * 1.3
        return super().getEffectiveArmour(damageType, combatUnit)

    def onEnergyShieldBroken(self, combatManager):
        if self._ascendancy == 'Colossus' and not self.colossusEsBroken:
            self.colossusEsBroken = True

    def onBeforeDamage(self, ability, damage, damageType, targets, combatManager):
        damage, damageType, targets = super().onBeforeDamage(ability, damage, damageType, targets, combatManager)
        # tracked so later ability-blind hooks (onBeforeCritRoll, onDealDamage) can still tell
        # whether the ability being used this attack should force Sovereign's ambush bonuses
        self._sovereignForceAmbush = bool(ability and self._ascendancy == 'Sovereign' and 'forces_ambush_bonus' in ability.tags)
        return damage, damageType, targets

    def onBeforeCritRoll(self, targetUnit, targets, combatManager):
        self._sovereignCritBuffed = False
        targetHasActed = bool(targetUnit) and targetUnit.entity in self._recentlyActedEnemies
        if self._ascendancy == 'Sovereign' and targetUnit and (not targetHasActed or self._sovereignForceAmbush):
            console.print(f"[asc_sovereign]Sovereign: Ambush against {targetUnit.entity._name}! +25% Crit Chance, +75% Crit Damage.[/asc_sovereign]")
            self._stats['Temporary']['crit_chance'] += 0.25
            self._stats['Temporary']['crit_multi'] += 0.75
            self._sovereignCritBuffed = True

    def onAfterCritRoll(self, targetUnit, targets, combatManager):
        if self._sovereignCritBuffed:
            self._stats['Temporary']['crit_chance'] -= 0.25
            self._stats['Temporary']['crit_multi'] -= 0.75
            self._sovereignCritBuffed = False

    def onHit(self, damageTaken, damageType, crit, attacker, combatManager):
        damageTaken, damageType = super().onHit(damageTaken, damageType, crit, attacker, combatManager)
        if attacker:
            self._recentlyActedEnemies.add(attacker)
        if self._ascendancy == 'Colossus' and self.colossusRetaliateCharges > 0 and attacker:
            attacker.applyCrush()
            self.colossusRetaliateCharges -= 1
        return damageTaken, damageType

    def onBeforeHit(self, finalDamage, damageType, attacker, combatManager):
        finalDamage = super().onBeforeHit(finalDamage, damageType, attacker, combatManager)
        hasActed = self.combatUnit.hasActed if self.combatUnit else False
        if hasActed:
            if self._ascendancy == 'Sovereign':
                if damageType in DIVINE_RES:
                    attacker._logDamage(f"{self._name}'s Sovereign (Acted, Divine Damage)", percent=-0.3)
                    finalDamage = round(finalDamage * 0.7)
                else:
                    attacker._logDamage(f"{self._name}'s Sovereign (Acted)", percent=-0.2)
                    finalDamage = round(finalDamage * 0.8)
            else:
                attacker._logDamage(f"{self._name}'s Marauder (Attacked after acting)", percent=-0.1)
                finalDamage = round(finalDamage * 0.9)
            if self._ascendancy == 'Dreadnought':
                dmg = int(self._maxHealth * 0.05)
                console.print(f"[asc_dreadnought]Dreadnought: {attacker._name} takes 5% of your Max HP as True Damage for attacking you after you acted![/asc_dreadnought]")
                attacker.damage(dmg, 'true')
                self.heal(dmg, reason="Dreadnought (Retaliation)")
        else:
            if self._ascendancy == 'Dreadnought' and attacker._health < self._health:
                attacker._logDamage(f"{self._name}'s Dreadnought (Enemy Health Advantage)", percent=-0.15)
                finalDamage = int(finalDamage * 0.85)
                self.gainDamageReduction()
            else:
                if self.siphonedDamage > 0:
                    self.siphonedDamage -= 1
                    attacker._baseDamage += 1
                    console.print(f"[warning]{attacker._name} stole 1 Siphoned Damage from you![/warning]")
                else:
                    self.gainDamageReduction()
        return finalDamage

    def _applySovereignAmbushBonus(self, finalDamage, damageType, target):
        if damageType == 'cold':
            self._logDamage("Sovereign Ambush (Cold Damage)", percent=0.25)
            finalDamage = int(finalDamage * 1.25)
        heal = int(finalDamage * 0.1)
        self.heal(heal, reason="Sovereign Ambush")
        target._baseSpeed -= round(self._speed * 0.01, 2)
        return finalDamage

    def onDealDamage(self, target, targetUnit, finalDamage, damageType, evaded, armourDamagePrevented, esDamagePrevented, combatManager):
        finalDamage = super().onDealDamage(target, targetUnit, finalDamage, damageType, evaded, armourDamagePrevented, esDamagePrevented, combatManager)

        self._harrowerExecuteReady = False
        targetHasActed = target in self._recentlyActedEnemies
        self._recentlyActedEnemies.discard(target)
        if targetHasActed:
            if self._ascendancy == 'Colossus':
                target.applyCrush()
                self.echoDamage[target] = max(1, int(finalDamage * 0.15))
            else:
                self.echoDamage[target] = max(1, int(finalDamage * 0.35))

            if self._ascendancy == 'Butcher':
                target.applyCarved()

            if self._ascendancy == 'Sovereign':
                finalDamage = self._applySovereignAmbushBonus(finalDamage, damageType, target)

        else:
            if self._ascendancy == 'Dreadnought':
                heal = int(finalDamage * 0.1)
                self.heal(heal, reason="Dreadnought (Damage Dealt)")

            elif self._ascendancy == 'Sovereign' and self._sovereignForceAmbush:
                finalDamage = self._applySovereignAmbushBonus(finalDamage, damageType, target)

            if self.siphonedDamage < self.maxSiphon and target._baseDamage > 5:
                dread = 1 if self._ascendancy != 'Dreadnought' else 2
                maxSiphon = min(
                    3 * dread,
                    (target._baseDamage + 5) - 3,
                    self.maxSiphon - self.siphonedDamage)
                siphon = random.randint(1, maxSiphon)

                if self._ascendancy == 'Harrower':
                    siphon = siphon / 50 # 1 damage = 0.02 speed
                    target._baseSpeed -= siphon
                    self._stats['Temporary']['speed'] = min(0.5, self._stats['Temporary']['speed'] + siphon)
                    console.print(f"[asc_harrower]Harrower: Siphoned {siphon:.2f} speed from {target._name}![/asc_harrower]")
                    self.checkHarrowerBuff()
                    self._harrowerExecuteReady = True
                else:
                    target._baseDamage -= siphon
                    self.siphonedDamage += siphon
                    console.print(f"[class_marauder]Marauder: Siphoned {siphon} damage from {target._name}![/class_marauder]")

        return finalDamage

    def onAfterMitigation(self, attacker, finalDamage, damageType, evaded, armourDamagePrevented, esDamagePrevented, preMitigationDamage, combatManager):
        finalDamage = super().onAfterMitigation(attacker, finalDamage, damageType, evaded, armourDamagePrevented, esDamagePrevented, preMitigationDamage, combatManager)
        hasActed = self.combatUnit.hasActed if self.combatUnit else False
        if hasActed:
            if self._ascendancy == 'Colossus':
                self.colossusDamage += armourDamagePrevented + esDamagePrevented
            elif self._ascendancy == 'Harrower':
                spdReduction = round(attacker._speed * 0.05, 2)
                attacker._speed -= spdReduction
                console.print(f"[asc_harrower]Harrower: {attacker._name} attacked you after you acted - Speed reduced by {spdReduction:.2f} and takes Cold Damage equal to their base damage![/asc_harrower]")
                attacker.damage(attacker._baseDamage, 'cold')
            elif self._ascendancy == 'Butcher' and self.siphonedDamage > 0:
                console.print(f"[asc_butcher]Butcher: {attacker._name} attacked you after you acted - takes Cold Damage equal to your Siphoned Damage![/asc_butcher]")
                attacker.damage(self.siphonedDamage, 'cold')

        if self._ascendancy == 'Dreadnought':
            if finalDamage > 0:
                self.dreadnoughtDeferredDamage[2] += finalDamage // 2
                finalDamage = round(finalDamage / 2)

        return finalDamage

    def onExecuteCheck(self, target, combatManager):
        if self._harrowerExecuteReady and target._health <= (target._maxHealth * 0.08):
            console.print(f"[asc_harrower]Harrower: {target._name} has been Executed![/asc_harrower]")
            target.damage(target._health, 'true')
            combatManager.checkDead(target)
            self.onKill(target, {'executed': True}, combatManager)

    def onAttack(self, damageDealt, damageType, target, combatManager, ability, crit):
        damageDealt, damageType = super().onAttack(damageDealt, damageType, target, combatManager, ability, crit)

        targetEntity = target.entity if target else None

        if self._ascendancy == 'Butcher' and ability and targetEntity:
            if 'marks_target' in ability.tags:
                self._setButcherMark(targetEntity)
                console.print(f"[asc_butcher]Butcher: Marked {targetEntity._name} as your prey![/asc_butcher]")
                for _ in range(ability.effects.get('target', {}).get('grant_carved', {}).get('stacks', 0)):
                    targetEntity.applyCarved()
                for _ in range(ability.effects.get('self', {}).get('grant_slaughter', {}).get('stacks', 0)):
                    if self.butcherSlaughter < 5:
                        self.butcherSlaughter += 1
                        self._stats['Temporary']['crit_multi'] += 0.15

            if 'consumes_slaughter' in ability.tags and self.butcherSlaughter > 0:
                stacksConsumed = self.butcherSlaughter
                consumeFx = ability.effects.get('self', {}).get('consume_slaughter', {})
                dmgPerStack = consumeFx.get('damage_per_stack', 0) / 100
                lsPerStack = consumeFx.get('lifesteal_per_stack', 0)

                self._stats['Temporary']['crit_multi'] -= 0.15 * stacksConsumed
                self.butcherSlaughter = 0

                self._logDamage(f"Slaughterfeast ({stacksConsumed} Slaughter consumed)", percent=dmgPerStack * stacksConsumed)
                damageDealt = int(damageDealt * (1 + (dmgPerStack * stacksConsumed)))
                lsGain = lsPerStack * stacksConsumed
                self._stats['Temporary']['lifesteal'] += lsGain
                self._butcherSlaughterfeastLifesteal += lsGain
                console.print(f"[asc_butcher]Butcher: Slaughterfeast consumes {stacksConsumed} Slaughter! +{int(dmgPerStack * stacksConsumed * 100)}% Damage, +{lsGain}% Lifesteal.[/asc_butcher]")

            if 'marked_bonus_damage' in ability.tags and targetEntity.marked:
                self._logDamage("Marked Target (Butcher)", percent=0.25)
                damageDealt = int(damageDealt * 1.25)

            if 'aoe_carves_marked' in ability.tags and targetEntity.marked:
                targetEntity.applyCarved()

        if self._ascendancy == 'Colossus' and ability and targetEntity:
            if 'grants_crush_retaliation' in ability.tags:
                charges = ability.effects.get('self', {}).get('retaliate_crush', {}).get('charges', 0)
                if charges:
                    self.colossusRetaliateCharges = charges
                    console.print(f"[asc_colossus]Colossus: Braced for retaliation - the next {charges} hit(s) against you Crush your attacker.[/asc_colossus]")

            if 'consumes_target_crush' in ability.tags and targetEntity.crush > 0:
                consumeFx = ability.effects.get('self', {}).get('consume_target_crush', {})
                dmgPerStack = consumeFx.get('damage_per_stack', 0) / 100
                armourPct = consumeFx.get('added_armour_percent', 0) / 100

                stacksConsumed = targetEntity.removeCrush()
                self._logDamage(f"Sunder ({stacksConsumed} Crush consumed)", percent=dmgPerStack * stacksConsumed)
                damageDealt = int(damageDealt * (1 + (dmgPerStack * stacksConsumed)))
                armourGain = int(damageDealt * armourPct)
                self._stats['Temporary']['added_armour'] += armourGain
                console.print(f"[asc_colossus]Colossus: Sunder shatters {stacksConsumed} Crush stack(s)! +{int(dmgPerStack * stacksConsumed * 100)}% Damage, +{armourGain} Added Armour.[/asc_colossus]")

            if 'aoe_applies_crush' in ability.tags:
                targetEntity.applyCrush()

        if self._ascendancy == 'Dreadnought' and ability and targetEntity:
            if 'accelerates_deferred_damage' in ability.tags:
                fx = ability.effects.get('self', {}).get('accelerate_deferred', {})
                pct = fx.get('conversion_percent', 0) / 100
                pending = self.dreadnoughtDeferredDamage.get(1, 0) + self.dreadnoughtDeferredDamage.get(2, 0)
                if pending > 0:
                    gained = int(pending * pct)
                    cap = int(self._maxHealth * 0.3)
                    self.dreadnoughtDamage = min(cap, self.dreadnoughtDamage + gained)
                    self.dreadnoughtDeferredDamage[1] = 0
                    self.dreadnoughtDeferredDamage[2] = 0
                    console.print(f"[asc_dreadnought]Dreadnought: Grim Resolve converts {pending} pending Deferred Damage into +{gained} permanent bonus damage.[/asc_dreadnought]")

            if 'consumes_dreadnought_pool' in ability.tags and self.dreadnoughtDamage > 0:
                fx = ability.effects.get('self', {}).get('consume_dreadnought_pool', {})
                mult = fx.get('multiplier', 100) / 100
                bonus = int(self.dreadnoughtDamage * mult)
                self._logDamage("Reckoning (Dreadnought pool consumed)", flat=bonus)
                damageDealt += bonus
                console.print(f"[asc_dreadnought]Dreadnought: Reckoning consumes your {self.dreadnoughtDamage} bonus damage pool for +{bonus} Damage.[/asc_dreadnought]")
                self.dreadnoughtDamage = 0

        if self._ascendancy == 'Sovereign' and ability and targetEntity:
            if 'applies_shame_directly' in ability.tags:
                targetEntity.applyShame()

            if 'speed_advantage_damage' in ability.tags:
                fx = ability.effects.get('self', {}).get('speed_advantage_bonus', {})
                multiplier = fx.get('multiplier', 0)
                speedAdvantage = max(0, self._speed - targetEntity._speed)
                if speedAdvantage > 0 and multiplier:
                    bonus = int(speedAdvantage * multiplier)
                    self._logDamage(f"Speed Advantage ({speedAdvantage:.2f})", flat=bonus)
                    damageDealt += bonus
                    console.print(f"[asc_sovereign]Sovereign: Outpaced {targetEntity._name} by {speedAdvantage:.2f} Speed - +{bonus} Damage.[/asc_sovereign]")

        if self._ascendancy == 'Harrower' and ability and targetEntity:
            if 'siphons_speed_directly' in ability.tags:
                fx = ability.effects.get('self', {}).get('siphon_speed', {})
                amount = fx.get('amount', 0)
                if amount > 0:
                    targetEntity._baseSpeed -= amount
                    self._stats['Temporary']['speed'] = min(0.5, self._stats['Temporary']['speed'] + amount)
                    console.print(f"[asc_harrower]Harrower: Siphoned {amount:.2f} Speed from {targetEntity._name}![/asc_harrower]")
                    self.checkHarrowerBuff()

            if 'low_hp_finisher' in ability.tags:
                fx = ability.effects.get('self', {}).get('low_hp_bonus', {})
                threshold = fx.get('threshold_percent', 0) / 100
                mult = fx.get('damage_multiplier', 100) / 100
                if threshold and targetEntity._health <= targetEntity._maxHealth * threshold:
                    self._logDamage("Low HP Finisher (Harrower)", percent=mult - 1)
                    damageDealt = int(damageDealt * mult)
                    console.print(f"[asc_harrower]Harrower: {targetEntity._name} is running out of road - damage increased![/asc_harrower]")

            if 'grants_empowerment' in ability.tags:
                self.empowerHarrower()

        if self.siphonedDamage:
            self._logDamage("Siphoned Damage", flat=self.siphonedDamage)
        damageDealt += self.siphonedDamage

        if self._ascendancy == 'Colossus':
            if self.colossusDamage:
                self._logDamage("Stored Damage from Prevented Hits (Colossus)", flat=self.colossusDamage)
            damageDealt += self.colossusDamage
            if self.colossusEsBroken:
                self._logDamage(f"Energy Shield Broken ({self.maxEnergyShield} Max ES, Colossus)", percent=(self.maxEnergyShield // 5) / 100)
                damageDealt = int(damageDealt * (1 + ((self.maxEnergyShield // 5) / 100)))

        if self._ascendancy == 'Dreadnought':
            if self.dreadnoughtDamage:
                self._logDamage("Bonus Damage Pool (Dreadnought)", flat=self.dreadnoughtDamage)
            damageDealt += self.dreadnoughtDamage

        elif self._ascendancy == 'Harrower':
            if self.harrowerSpeedBuffGained:
                self._logDamage("Siphoned Speed above 0.25 (Harrower)", percent=0.4)
                damageDealt = int(damageDealt * 1.4)
            if self.harrowerEmpowered and damageType == 'cold':
                self._logDamage("Empowerment (Harrower)", percent=0.3)
                damageDealt = int(damageDealt * 1.3)

        elif self._ascendancy == 'Butcher' and damageType == 'cold':
            if self.butcherSlaughter:
                self._logDamage(f"Slaughter ({self.butcherSlaughter} stacks)", percent=0.1 * self.butcherSlaughter)
            damageDealt = int(damageDealt * (1 + (0.1 * self.butcherSlaughter)))

        return damageDealt, damageType

    def onTurnStart(self, combatManager):
        if self._ascendancy == 'Butcher' and self._butcherSlaughterfeastLifesteal:
            self._stats['Temporary']['lifesteal'] -= self._butcherSlaughterfeastLifesteal
            self._butcherSlaughterfeastLifesteal = 0

        dType = 'cold'
        if self._ascendancy == 'Colossus':
            dType = 'true'
        for e, damage in self.echoDamage.items():
            if not e._isDead:
                e.damage(damage, dType)
                combatManager.checkDead(e)
                console.print(f"[class_marauder]Marauder: Echo activated. Dealt {damage} {dType} Damage to {e._name}.[/class_marauder]")
        if self.echoDamage != {}:
            pause()
            self.echoDamage = {}

        if self._ascendancy == 'Dreadnought':
            self.heal(self.dreadnoughtEchoHeal, reason="Echoing Heal (Dreadnought)")
            self.dreadnoughtEchoHeal = 0

            if self.dreadnoughtDeferredDamage[1] > 0:
                console.print(f"[asc_dreadnought]Dreadnought: {self.dreadnoughtDeferredDamage[1]} Deferred Damage catches up to you![/asc_dreadnought]")
            self.damage(self.dreadnoughtDeferredDamage[1], 'cold')
            self.dreadnoughtDamage = int(min(self._maxHealth * 0.3, self.dreadnoughtDamage + (self.dreadnoughtDeferredDamage[1] * 0.2)))
            self.dreadnoughtDeferredDamage[1] = self.dreadnoughtDeferredDamage[2]
            self.dreadnoughtDeferredDamage[2] = 0

        super().onTurnStart(combatManager)

    def onCrit(self, targets, combatManager, critDamage):
        if self._ascendancy == 'Butcher':
            if self.butcherSlaughter < 5:
                self.butcherSlaughter += 1
                self._stats['Temporary']['crit_multi'] += 0.15

        return critDamage

    def onKill(self, entity, attackData, combatManager=None):
        super().onKill()
        if self._ascendancy == 'Colossus':
            gainedArmour = int(entity.armour * 0.2)
            esGain = int(max(entity.maxEnergyShield * 0.1, entity.armour * 0.1))
            self._stats['Temporary']['added_armour'] += gainedArmour
            self._stats['energy_shield'] = min(self.maxEnergyShield, self.energyShield + esGain)
            console.print(f"[asc_colossus]Colossus: Gained 20% of {entity._name}'s Armour as Added Armour for the rest of combat! +{gainedArmour} Armour. Regenerated {esGain} Energy Shield.[/asc_colossus]")
        elif self._ascendancy == 'Butcher' and entity.marked:
            self.butcherDamage += entity._baseDamage
            console.print(f"[asc_butcher]Butcher: Killed your Marked target! +{entity._baseDamage} Damage for the rest of combat.[/asc_butcher]")
            self.butcherMarkedTarget = None
            self.applyButcherMark(combatManager.allAlive)

        # generic ability.effects.on_kill processing - available to any Marauder ascendancy ability
        ability = attackData.get('ability')
        onKillFx = ability.effects.get('on_kill', {}) if ability else {}
        if onKillFx:
            healPct = onKillFx.get('heal_percent_max_hp', 0)
            if healPct:
                heal = int(self._maxHealth * healPct / 100)
                self.heal(heal, False)
                console.print(f"[class_marauder]{ability.name} claims its due! Healed {heal} HP.[/class_marauder]")

            refund = onKillFx.get('refund_slaughter', 0)
            if refund and self._ascendancy == 'Butcher':
                for _ in range(refund):
                    if self.butcherSlaughter < 5:
                        self.butcherSlaughter += 1
                        self._stats['Temporary']['crit_multi'] += 0.15
                console.print(f"[asc_butcher]Butcher: {ability.name} grants +{refund} Slaughter.[/asc_butcher]")

    def onCombatStart(self, combatManager, combatUnit):
        super().onCombatStart(combatManager, combatUnit)
        if self._ascendancy == 'Butcher':
            self.applyButcherMark(combatManager.allAlive)

    def onCombatEnd(self):
        heal = int(self._maxHealth * (min(30, self.siphonedDamage) / 100))
        self.heal(heal, reason="Siphoned Damage (End of Combat)")

        self.siphonedDamage = 0
        self.echoDamage = {}
        self._recentlyActedEnemies = set()

        self.colossusEsBroken = False
        self.colossusDamage = 0
        self.colossusRetaliateCharges = 0
        self.dreadnoughtDeferredDamage = {2: 0, 1: 0}
        self.dreadnoughtDamage = 0
        self.dreadnoughtEchoHeal = 0
        self.harrowerSiphonedSpeed = 0
        self.harrowerSpeedBuffGained = False
        self.harrowerEmpowered = False
        self.butcherMarkedTarget = None
        self.butcherDamage = 0
        self.butcherSlaughter = 0
        self._butcherSlaughterfeastLifesteal = 0
        self._sovereignForceAmbush = False

        super().onCombatEnd()

    ASCENDANCY_DELTAS = {
        'Colossus': {
            '_baseHealth': -15,
            '_baseDamage': 4,
            '_baseSpeed': -0.1,
            '_stats.Permanent.added_armour': 100,
            '_stats.Permanent.added_energy_shield': 20,
        },
        'Dreadnought': {
            '_baseHealth': 30,
            '_baseDamage': -5,
            '_baseSpeed': -0.1,
            '_stats.Permanent.increased_health': 20,
            '_stats.Permanent.healing_magnitude': 50,
            '_stats.Permanent.cold': 15,
            '_stats.Permanent.max_cold': 5,
        },
        'Sovereign': {
            '_baseHealth': 30,
            '_baseDamage': 6,
            '_baseSpeed': -0.1,
            '_stats.Permanent.stamina_regen': 5,
            '_stats.Permanent.holy': 10,
        },
        'Harrower': {
            '_baseHealth': -10,
            '_baseDamage': 10,
            '_baseSpeed': 0.1,
            '_stats.baseCritChance': 0.05,
            '_stats.baseCritMulti': 0.25,
        },
        'Butcher': {
            '_baseHealth': 10,
            '_baseDamage': 6,
            '_baseSpeed': 0.1,
            '_stats.baseCritChance': 0.05,
            '_stats.baseCritMulti': -0.25,
            '_stats.Permanent.fire': -10,
        },
    }

    def _removeOldAscendancy(self):
        delta = self.ASCENDANCY_DELTAS.get(self._ascendancy)
        if delta:
            self._applyStatDelta(delta, sign=-1)
        return True

    def updateAscendancy(self, ascendancy):
        if not super().updateAscendancy(ascendancy):
            return
        self._ascendancy = ascendancy
        self.ascendancyDescription = MARAUDER_DESCRIPTIONS[ascendancy]
        self._applyStatDelta(self.ASCENDANCY_DELTAS[ascendancy], sign=1)
        self._recalculateStats()
        self.gainClassAbilities(True)
        return True

...