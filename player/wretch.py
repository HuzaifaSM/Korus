from .base import Player, DIVINE_RES, OTHERWORLD_RES
from scripts.styles import console
from copy import deepcopy
import random

WRETCH_DESCRIPTIONS = {
    "Wretch": "[class_wretch]An outcast mage, revelling in the torture of flesh and blood.[/class_wretch]\n"
        "- You have no Stamina. All abilities cost Health to use. Gain +1% Lifesteal per 5% Missing Health.\n"
        "- Upon attacking an enemy with an ability, apply 1 stack of Blood Spike, up to 10 stacks.\n"
        "- Each stack of Blood Spike increases the execution threshold on an enemy by 2%. If an enemy's health drops below the execution threshold, they are immediately killed.\n"
        "- When an enemy is executed by Blood Spike, heal for 1% Max HP per stack of Blood Spike on the executed enemy.\n"
        "- Whilst below 40% Health: Gain +0.3 Speed, 20% Increased Dark Damage.\n"
        "[bold]Starting Stats:[/bold] 65 HP | 4 Damage | 5% Crit Chance | 150% Crit Damage | [dark]Dark Damage[/dark] | 0.95 Speed.",
    # ascendancies
    "Exsanguinator": "[lore]The blood remembers. Drain it from them, consume their suffering. Let every drop be the reason the next falls.[/lore]"
        "- You can apply up to 15 stacks of Blood Spike on an enemy.\n"
        "- Upon critically striking an enemy with Blood Spike stacks, consume all stacks to deal 5% Increased damage per stack.\n"
        "- Whenever an enemy dies to a critical hit, a random enemy takes Dark damage equal to 20% of the killed enemy's Max HP. If there are no more enemies, instead heal for 10% Max HP.\n"
        "- Abilities will consume Energy Shield before Health if it is available. Abilities which use Energy Shield ignore 15% of the target's Armour.\n"
        "[bold]Stat Changes:[/bold] +10 HP. +4 Damage. +5% Crit Chance. -25% Crit Damage. +50 Energy Shield.",
    "Bloodletter": "[lore]They called your suffering a weakness. Prove them wrong. Bleed. Grow. Your scars only make you stronger.[/lore]"
        "- Abilities have 50% Increased Health cost. While below 20% Health: Deal 30% Increased Dark Damage, gain +10% Lifesteal.\n"
        "- While above 60% Health: -20% Divine Resistance, +10% Otherworld Resistance. Store all Divine and Otherworld damage taken.\n"
        "- Whenever you are attacked by an enemy, deal Dark Damage to them equal to 5% of Health lost in combat. At the end of combat, heal for 33% of all Divine and Otherworld damage taken.\n"
        "- When an enemy is executed by Blood Spike, all remaining enemies take True damage equal to 1% of their Max HP per stack of Blood Spike on the executed enemy.\n"
        "[bold]Stat Changes:[/bold] +25 HP. -3 Damage. -0.1 Speed. +15% Dark Resistance. +5% Otherworld Resistance.",
    "Plaguebearer": "[lore]They made a mockery of your ways. Now make a mockery of their corpses. Let them fester and rot. Each battle is just another experiment.[/lore]"
        "- You can apply up to 7 stacks of Blood Spike on an enemy. Enemies with 7 stacks of Blood Spike deal 20% Less Damage.\n"
        "- Whenever an enemy is executed by Blood Spike, all remaining enemies gain Blood Spike stacks equal to 50% of the stacks on the executed enemy.\n"
        "- Whenever you are critically hit, or an enemy is killed, you gain 1 stack of Blood Scent, up to a maximum of 5.\n"
        "- Blood Scent: +10% Increased Damage, +2% Lifesteal, +0.05 Speed. At the end of combat, heal 2% Max HP per stack of Blood Scent.\n"
        "[bold]Stat Changes:[/bold] +5 HP. +4 Damage. +0.1 Speed. +25% Crit Damage.",
    "Necrose": "[lore]Everything decays. You are the catalyst. Watch them bleed and waste away. Their end simply quickens the next.[/lore]"
        "- Whenever an enemy attacks, they gain 1 stack of Necrosis, up to a maximum of 10 stacks. Necrosis: +3% Damage Taken, -0.02 Speed.\n"
        "- You can apply up to 5 stacks of Blood Spike on an enemy. Deal 2% Increased damage per Blood Spike and Necrosis applied in combat.\n"
        "- Whenever an enemy critically hits you, consume all stacks of Necrosis on them and reflect 5% of the damage taken per Necrosis consumed.\n"
        "- Whenever an enemy is executed by Blood Spike, heal for 5% Max HP and gain Rot for 3 turns: +25% Increased Damage, +0.2 Speed, -50% Crit Damage.\n"
        "- While above 60% Health: +10% Crit Chance, +50% Crit Damage. While below 40% Health: +5% Damage Reduction, +5% Lifesteal, -5% [all]All[/all] Resistance.\n"
        "[bold]Stat Changes:[/bold] -15 HP. +5 Damage. +0.1 Speed. +15% Dark Resistance. +10% Resistance Penetration",
    "Necromancer": "[lore]Living or dead, neither matters. All will serve, for a time. Show them loyalty means nothing. Watch as they rip each other to shreds.[/lore]"
        "- Upon killing an enemy, you may choose to convert them into a skeleton for 3 turns.\n"
        "- Skeletons are allies created from the killed enemy, keeping a portion of their stats and items, scaling off of your level.\n"
        "- You can only convert one enemy per battle. If the converted enemy is the final enemy in combat, it will join you for the first 3 turns of your next combat.\n"
        "- Whenever an enemy is executed by Blood Spike, they will use a basic attack on another living enemy before dying.\n"
        "- If an enemy is executed by Blood Spike and converted, it will retain more of its stats and items.\n"
        "[bold]Stat Changes:[/bold] +20 HP. -4 Damage. -0.1 Speed. +5 HP Regen. +10% Otherworld Resistance."
}

class Wretch(Player):
    def __init__(self, name, health = 65, damage = 4, damageType = "dark", speed = 0.95):
        super().__init__(name, health, damage, 0.05, 1.5, damageType, speed, className="Wretch", classDescription=WRETCH_DESCRIPTIONS["Wretch"])
        self.maxBloodSpikeStacks = 10

        self.under40LastTurn = False
        self.under20LastTurn = False
        self.above60LastTurn = True

        self.divineOtherworldDamageTaken = 0
        self.healthLost = 0
        self.bloodScent = 0
        self.bloodSpikeApplied = 0
        self.necrosisApplied = 0
        self.rotTurns = 0
        self.currentSkeleton = None
        self.skeletonTurns = 0
        self.pendingSkeleton = None
        self.skeletonUsedThisBattle = False
        self.abilityUsedEnergyShield = False

    def spendHealthForAbility(self, amount):
        self.abilityUsedEnergyShield = False
        if self._ascendancy == 'Exsanguinator' and self.energyShield > 0:
            fromShield = min(self.energyShield, amount)
            self._stats['energyShield'] -= fromShield
            amount -= fromShield
            if fromShield > 0:
                self.abilityUsedEnergyShield = True
                console.print(f"[cyan]Exsanguinator: {fromShield} of the ability's Health cost was paid with Energy Shield![/cyan]")

        if amount > 0:
            super().spendHealthForAbility(amount)

    def gainBloodScent(self):
        if self._ascendancy == 'Plaguebearer':
            self.bloodScent = min(5, self.bloodScent + 1)
            self._stats['Temporary']['lifesteal'] += 2
            self._stats['Temporary']['speed'] += 0.05

    def gainRot(self):
        if self._ascendancy == 'Necrose':
            if self.rotTurns == 0:
                self._stats['Temporary']['speed'] += 0.2
                self._stats['Temporary']['crit_multi'] -= 0.5
            self.rotTurns = 3

    def _convertToSkeleton(self, enemy, executed=False):
        skeleton = deepcopy(enemy)
        skeleton._name = f"{enemy._name}'s Skeleton"

        statsKeptPercent = min(75, self._level + 5) + min(10, enemy._level // 10)
        itemLossChance = 60 - (self._level // 4) - min(10, enemy._level // 10)
        if executed:
            statsKeptPercent += 15
            itemLossChance -= 20
        statsKeptPercent = min(100, statsKeptPercent)
        itemLossChance = max(0, itemLossChance)

        mult = statsKeptPercent / 100
        skeleton._baseHealth = max(1, int(skeleton._baseHealth * mult))
        skeleton._baseDamage = max(0, int(skeleton._baseDamage * mult))

        for slot, item in list(skeleton._equipment.items()):
            if item and random.randint(1, 100) <= itemLossChance:
                skeleton._equipment[slot] = None

        for itemName in list(skeleton._inventory.keys()):
            if random.randint(1, 100) <= itemLossChance:
                del skeleton._inventory[itemName]

        skeleton._recalculateStats(False)
        skeleton._health = skeleton._maxHealth

        return skeleton

    def onKill(self, entity, attackData, combatManager=None):
        super().onKill()
        if self._ascendancy == 'Necromancer':
            if not self.skeletonUsedThisBattle and self.skeletonTurns <= 0:
                choice = console.input(
                    f"[dark_red]Necromancer: Convert {entity._name} into a skeleton to fight alongside you? [/dark_red][dim](y/n)[/dim]\n> "
                ).strip().lower()
                if choice == 'y':
                    executed = attackData.get('executed', False)
                    skeleton = self._convertToSkeleton(entity, executed)
                    self.skeletonUsedThisBattle = True

                    if combatManager and len(combatManager.allAlive) == 0:
                        self.pendingSkeleton = skeleton
                        console.print(f"[dark_red]{skeleton._name} will join you at the start of your next battle![/dark_red]")
                    else:
                        self.currentSkeleton = skeleton
                        self.skeletonTurns = 3
                        console.print(f"[dark_red]{skeleton._name} rises to fight alongside you for 3 turns![/dark_red]")

        if self._ascendancy == 'Exsanguinator':
            if combatManager and len(combatManager.allAlive) > 0:
                dmg = int(entity._maxHealth * 0.2)
                pick = random.choice(combatManager.allAlive)
                pick.damage(dmg, 'dark')
            else:
                heal = int(self._maxHealth * 0.1)
                self.heal(heal)
        if self._ascendancy == 'Plaguebearer':
            self.gainBloodScent()

        return {}

    def onExecuteCheck(self, target, combatManager):
        if target.bloodSpike > 0 and target._health <= (target._maxHealth * (0.02 * target.bloodSpike)):
            console.print(f"[class_wretch]Wretch: {target._name} has been Executed from Blood Spike![/class_wretch]")

            if self._ascendancy == 'Necromancer':
                otherEnemies = [e for e in combatManager.allAlive if e != target]
                if otherEnemies:
                    victim = random.choice(otherEnemies)
                    console.print(f"[dark_red]Necromancer: {target._name} lashes out at {victim._name} before dying![/dark_red]")
                    victim.damage(target._damage, target._damageType)
                    combatManager.checkDead(victim)

            target.damage(target._health, 'true')
            combatManager.checkDead(target)
            heal = self._maxHealth * (0.01 * target.bloodSpike)
            self.heal(heal)

            if self._ascendancy == 'Bloodletter':
                dmgMult = 0.01 * target.bloodSpike
                console.print(f'[dim red1]Bloodletter: All enemies take {int(dmgMult*100)}% of their Max HP as True Damage![/dim red1]')
                for e in combatManager.allAlive:
                    dmg = int(e._maxHealth * dmgMult)
                    e.damage(dmg, 'true')

            elif self._ascendancy == 'Plaguebearer':
                spread = target.bloodSpike // 2
                numEnemies = len(combatManager.getUnitsInTeam('enemy'))
                per = int(spread / numEnemies) if numEnemies else 0
                if per > 0:
                    for e in combatManager.allAlive:
                        e.bloodSpike = min(self.maxBloodSpikeStacks, e.bloodSpike + per)

            elif self._ascendancy == 'Necrose':
                heal = int(self._maxHealth * 0.05)
                self.heal(heal)
                self.gainRot()

            self.onKill(target, {'executed': True}, combatManager)

    def getArmourIgnorePercent(self) -> float:
        if self._ascendancy == 'Exsanguinator' and self.abilityUsedEnergyShield:
            return 0.15
        return super().getArmourIgnorePercent()

    def onPrepareHit(self, target, targetUnit, finalDamage, damageType, combatManager):
        finalDamage = super().onPrepareHit(target, targetUnit, finalDamage, damageType, combatManager)
        if target.bloodSpike < self.maxBloodSpikeStacks:
            target.bloodSpike += 1
            if self._ascendancy == 'Necrose':
                self.bloodSpikeApplied += 1
        return finalDamage

    def onAfterMitigation(self, attacker, finalDamage, damageType, evaded, armourDamagePrevented, esDamagePrevented, preMitigationDamage, combatManager):
        finalDamage = super().onAfterMitigation(attacker, finalDamage, damageType, evaded, armourDamagePrevented, esDamagePrevented, preMitigationDamage, combatManager)
        if self._ascendancy == 'Bloodletter':
            reflect = int(self.healthLost * 0.05)
            attacker.damage(reflect, 'dark', attacker.combatUnit)
        elif self._ascendancy == 'Plaguebearer' and attacker.bloodSpike == 7:
            finalDamage = int(finalDamage * 0.8)
        elif self._ascendancy == 'Necrose':
            attacker.applyNecrosis()
            self.necrosisApplied += 1
        return finalDamage

    def onAttack(self, damageDealt, damageType, target, combatManager, ability, crit):
        damageDealt, damageType = super().onAttack(damageDealt, damageType, target, combatManager, ability, crit)

        if ability and target:
            bonusSpike = ability.effects.get('target', {}).get('blood_spike', {}).get('stacks', 0)
            if bonusSpike > 0:
                entity = target.entity
                if entity.bloodSpike < self.maxBloodSpikeStacks:
                    gained = min(bonusSpike, self.maxBloodSpikeStacks - entity.bloodSpike)
                    entity.bloodSpike += gained
                    if self._ascendancy == 'Necrose':
                        self.bloodSpikeApplied += gained
                    console.print(f"[class_wretch]Wretch: {ability.name} applies {gained} extra stack(s) of Blood Spike to {entity._name}![/class_wretch]")

        if self._health < (0.4 * self._maxHealth) and damageDealt == 'dark':
            damageDealt = int(damageDealt * 1.2)

        if self._ascendancy == 'Plaguebearer' and self.bloodScent > 0:
            damageDealt = int(damageDealt * (1.1 * self.bloodScent))

        elif self._ascendancy == 'Necrose' and (self.bloodSpikeApplied > 0 or self.necrosisApplied > 0):
            total = self.bloodSpikeApplied + self.necrosisApplied
            damageDealt = int(damageDealt * (1.02 * total))
            if self.rotTurns > 0:
                damageDealt = int(damageDealt * 1.25)

        return damageDealt, damageType

    def onHit(self, damageTaken, damageType, crit = False, attacker = None, combatManager=None):
        damageTaken, damageType = super().onHit(damageTaken, damageType, crit, attacker, combatManager)
        if self._ascendancy == 'Bloodletter':
            self.healthLost += damageTaken
            if damageType in DIVINE_RES or damageType in OTHERWORLD_RES:
                self.divineOtherworldDamageTaken += damageTaken

        if self._ascendancy == 'Necrose' and self.under40LastTurn:
            damageTaken = int(damageTaken * 0.95)

        return damageTaken, damageType

    def onCrit(self, targets, combatManager, critDamage):
        if self._ascendancy == 'Exsanguinator':
            for t in targets:
                t.bloodSpike = 0

        return critDamage

    def onCriticallyHit(self, attacker, combatManager, critDamage, damageType):
        critDamage = super().onCriticallyHit(attacker, combatManager, critDamage, damageType)
        if self._ascendancy == 'Plaguebearer':
            self.gainBloodScent()

        elif self._ascendancy == 'Necrose':
            perc = 0.05 * attacker.necrosis
            reflect = int(critDamage * perc)
            console.print(f"[asc_necrose]Necrose: Reflected [/asc_necrose]{int(perc*100)}[asc_necrose]% of the damage to the enemy![/asc_necrose]")
            critDamage -= reflect
            attacker.damage(reflect, damageType)

        return critDamage

    def onTurnEnd(self):
        if self._ascendancy == 'Necrose' and self.rotTurns > 0:
            self.rotTurns -= 1
            if self.rotTurns == 0:
                self._stats['Temporary']['speed'] -= 0.2
                self._stats['Temporary']['crit_multi'] += 0.5

        if self._ascendancy == 'Necromancer' and self.skeletonTurns > 0:
            self.skeletonTurns -= 1
            if self.skeletonTurns == 0:
                console.print(f"[dim]{self.currentSkeleton._name} crumbles to dust.[/dim]")
                self.currentSkeleton = None

    def onCombatEnd(self):
        if self._ascendancy == 'Bloodletter':
            heal = int(self.divineOtherworldDamageTaken * 0.33)
            self.heal(heal)
        elif self._ascendancy == 'Plaguebearer':
            heal = int(self._maxHealth * 0.02 * self.bloodScent)
            self.heal(heal)

        self.divineOtherworldDamageTaken = 0
        self.healthLost = 0
        self.bloodScent = 0
        self.necrosisApplied = 0
        self.bloodSpikeApplied = 0
        self.bloodScent = 0
        self.rotTurns = 0
        self.abilityUsedEnergyShield = False

        if self._ascendancy == 'Necromancer':
            self.skeletonUsedThisBattle = False
            self.skeletonTurns = 0
            self.currentSkeleton = None

        super().onCombatEnd()

    def onTurnStart(self, combatManager=None):
        if not self.under40LastTurn and self._health <= (self._maxHealth * 0.4):
            self._stats['Temporary']['speed'] += 0.3
            self.under40LastTurn = True
            if self._ascendancy == 'Necrose':
                self._stats['Temporary']['lifesteal'] += 5
                self._stats['Temporary']['all'] -= 5
        elif self.under40LastTurn and self._health > (self._maxHealth * 0.4):
            self._stats['Temporary']['speed'] -= 0.3
            self.under40LastTurn = False
            if self._ascendancy == 'Necrose':
                self._stats['Temporary']['lifesteal'] -= 5
                self._stats['Temporary']['all'] += 5

        if self._ascendancy == 'Bloodletter':
            if not self.under20LastTurn and self._health <= (self._maxHealth * 0.2):
                self._stats['Temporary']['increased_dark_damage'] += 30
                self.under20LastTurn = True
                self._stats['Temporary']['lifesteal'] += 10
            elif self.under20LastTurn and self._health > (self._maxHealth * 0.2):
                self._stats['Temporary']['increased_dark_damage'] -= 30
                self._stats['Temporary']['lifesteal'] -= 10
                self.under20LastTurn = False

            if not self.above60LastTurn and self._health <= (self._maxHealth * 0.6):
                self._stats['Temporary']['divine'] -= 20
                self._stats['Temporary']['otherworld'] += 10
                self.above60LastTurn = True
            elif self.above60LastTurn and self._health > (self._maxHealth * 0.6):
                self._stats['Temporary']['divine'] += 20
                self._stats['Temporary']['otherworld'] -= 10
                self.above60LastTurn = False

        elif self._ascendancy == 'Necrose':
            if not self.above60LastTurn and self._health <= (self._maxHealth * 0.6):
                self._stats['Temporary']['crit_chance'] += 0.1
                self._stats['Temporary']['crit_multi'] += 0.5
                self.above60LastTurn = True
            elif self.above60LastTurn and self._health > (self._maxHealth * 0.6):
                self._stats['Temporary']['crit_chance'] -= 0.1
                self._stats['Temporary']['crit_multi'] -= 0.5
                self.above60LastTurn = False

        super().onTurnStart(combatManager)

    def rollCritical(self, target, damageDealt = None):
        crit, damage = super().rollCritical(target, damageDealt)
        if crit and self._ascendancy == 'Exsanguinator':
            if target and target.entity.bloodSpike > 0:
                damage = int(damage * (1 + (0.05 * target.entity.bloodSpike)))

        return crit, damage

    def _removeOldAscendancy(self) -> bool:
        if self._ascendancy == "Exsanguinator":
            self._baseHealth -= 10
            self._baseDamage -= 1
            self._stats['baseCritChance'] -= 0.05
            self._stats['baseCritMulti'] += 0.25
            self._stats['Permanent']['added_energy_shield'] -= 50
            self.maxBloodSpikeStacks -= 5
        elif self._ascendancy == "Bloodletter":
            self._baseHealth -= 25
            self._baseDamage -= 2
            self._baseSpeed -= 0.1
            self._stats['Permanent']['dark'] -= 15
            self._stats['Permanent']['otherworld'] -= 5
        elif self._ascendancy == "Plaguebearer":
            self._baseHealth -= 5
            self._baseDamage -= 4
            self._baseSpeed -= 0.1
            self._stats['baseCritMulti'] -= 0.25
            self.maxBloodSpikeStacks += 3
        elif self._ascendancy == 'Necrose':
            self._baseHealth += 15
            self._baseDamage -= 3
            self._baseSpeed -= 0.1
            self._stats['Permanent']['dark'] -= 15
            self._stats['Permanent']['resistance_penetration'] -= 10
            self.maxBloodSpikeStacks += 5
        elif self._ascendancy == 'Necromancer':
            self._baseHealth -= 20
            self._baseDamage += 2
            self._baseSpeed += 0.1
            self._stats['Permanent']['hp_regen'] -= 5
            self._stats['Permanent']['otherworld'] -= 10
        return True

    def updateAscendancy(self, ascendancy):
        if not super().updateAscendancy(ascendancy):
            return
        self._ascendancy = ascendancy
        self.ascendancyDescription = WRETCH_DESCRIPTIONS[ascendancy]
        if ascendancy == "Exsanguinator":
            self._baseHealth += 10
            self._baseDamage += 1
            self._stats['baseCritChance'] += 0.05
            self._stats['baseCritMulti'] -= 0.25
            self._stats['Permanent']['added_energy_shield'] += 50
            self.maxBloodSpikeStacks += 5
        elif ascendancy == "Bloodletter":
            self._baseHealth += 25
            self._baseDamage += 2
            self._baseSpeed += 0.1
            self._stats['Permanent']['dark'] += 15
            self._stats['Permanent']['otherworld'] += 5
        elif ascendancy == "Plaguebearer":
            self._baseHealth += 5
            self._baseDamage += 4
            self._baseSpeed += 0.1
            self._stats['baseCritMulti'] += 0.25
            self.maxBloodSpikeStacks -= 3
        elif ascendancy == "Necrose":
            self._baseHealth -= 15
            self._baseDamage += 3
            self._baseSpeed += 0.1
            self._stats['Permanent']['dark'] += 15
            self._stats['Permanent']['resistance_penetration'] += 10
            self.maxBloodSpikeStacks -= 5
        elif ascendancy == "Necromancer":
            self._baseHealth += 20
            self._baseDamage -= 2
            self._baseSpeed -= 0.1
            self._stats['Permanent']['hp_regen'] += 5
            self._stats['Permanent']['otherworld'] += 10
        self._recalculateStats()
