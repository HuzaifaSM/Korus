from .base import Player, DIVINE_RES, OTHERWORLD_RES
from scripts.styles import console, pause
from scripts.abilities import Effects
import random

WANDERER_DESCRIPTIONS = {
    "Wanderer": "[class_wanderer]The lost soul of a greater power, eternally searching for peace.[/class_wanderer]\n"
        "- Lost: If a single hit deals more than 10% of your Max HP, your next attack will deal 50% More Damage and target all enemies.\n"
        "- Whenever Lost is triggered, randomly gain 1 Hope or 1 Hopeless. Hope and Hopeless both have a maximum of 5 stacks.\n"
        "- If you have more than 50% Max HP remaining, you are more likely to gain Hope. If you have less than 50% Max HP remaining, you are more likely to gain Hopeless.\n"
        "- Hope: 10% Increased Psychic Damage, +2% Crit Chance. Hopeless: +2 Damage Reduction, +10% Crit Damage.\n"
        "- Upon reaching Max Hope, gain Radiance. Upon reaching Max Hopeless, gain Devastation. If you have Radiance or Devastation, you cannot gain Hope or Hopeless.\n"
        "- Radiance: +25% Crit Chance, +75% Crit Damage. Upon killing or critically hitting an enemy, heal for 10% of your Max HP. Excess healing is gained as Shield.\n"
        "- Devastation: 100% Increased Damage Dealt, 20% Increased Damage Taken. Whenever Lost is triggered, gain Damage equal to 3% of your Max HP for the rest of combat.\n"
        "Starting Stats: 40 HP | 6 Damage | 10% Crit Chance | 160% Crit Damage | Psychic Damage | 1.1 Speed.",
    #ascdenancies
    "Fractured": "[lore]You were never whole. Every wound reveals another piece. Every drop of their blood, another reason to continue. Among the fragments lies the truth.[/lore]"
        "- Upon triggering Lost, gain Fracture, up to 5 stacks. Fracture: +5% Psychic Damage. +3% Crit Chance. At 5 Fracture, your next attack deals 150% Damage to all enemies, and Fracture is set to 0.\n"
        "- If you trigger Lost and Fracture at the same time, double your Hope and Hopeless. Hope and Hopeless have 50% Reduced Effect.\n"
        "- If you have Radiance, gain 2 Fracture upon triggering Lost. If you have Devastation, Fracture grants +10% Crit Damage instead of +3% Crit Chance.\n"
        "- Whilst you have more Hope than Hopeless, your Crit Damage is doubled, but Non-critical hits do 40% Less Damage.\n"
        "- Whilst you have more Hopeless than Hope, you cannot Critically Hit, but Lost attacks deal 60% Increased Damage.\n"
        "- Upon critically hitting an enemy, take Psychic damage equal to 2% of your Max HP and gain 1 Hope.\n"
        "- When an enemy critically hits you, heal 1% Max HP per stack of Hope and Hopeless you have, and gain 1 Hopeless.\n"
        "[bold]Stat Changes:[/bold] -10 HP. +4 Damage. +0.05 Speed. +3% Crit Chance. +20% Crit Damage.",
    "Manifestation": "[lore]Your search was fruitless. A meaningless excuse. No longer. The truth shall rewrite reality. Become as you were, and unmake them.[/lore]"
        "- Lost triggers upon taking more than 5% of your Max HP as damage. Lost attacks have a 20% Chance to miss. Upon missing a Lost attack, apply Otherworld Exposure to all enemies, and lose 3 Hope.\n"
        "- When gaining Hope or Hopeless, gain twice as much. Hope and Hopeless have a maximum of 8 stacks.\n"
        "- You are able to have Radiance and Devastation at the same time. If you have Radiance and Devastation, gain Transcendence.\n"
        "- Transcendence: All attacks are Critical Hits, 20% Increased Defenses, 25% Increased Psychic Damage, 75% Less Evasion.\n"
        "- If you are hit whilst you have Transcendence, your attacker takes True damage equal to 5% of their Max HP.\n"
        "- Whenever an enemy dies, randomly consume all your Hope or Hopeless. Consuming Hope heals you for 3% Max HP per stack consumed. Consuming Hopeless grants 20% Increased damage on your next attack per stack consumed.\n"
        "[bold]Stat Changes:[/bold] +25 HP. -4 Damage. -0.05 Speed. +25% Crit Damage.",
    "Weaver": "[lore]Peace, a dull concept. Harmony, a beautiful one. Unfurl the tapestry of fate. Recreate them in your image. Then cut them down, until threads remain.[/lore]"
        "- 20% Increased Psychic Damage dealt. 30% Less Non-Psychic Damage dealt. Upon taking Divine Damage, gain 2 Hopeless.\n"
        "- Devastation now also grants +10% Crit Chance, -0.2 Speed, and 10% Reduced Defenses.\n"
        "- Lost triggers upon taking more than 15% of of your Max HP as damage.\n"
        "- Whenever you are critically hit, gain 2 Hope or Hopeless, depending on which resource you have more of. Hope and Hopeless have a maximum of 10 stacks.\n"
        "- If your Hope and Hopeless are equal, gain Harmony: 30% Increased Damage Dealt, +50% Crit Damage, +0.2 Speed.\n"
        "- If you trigger Lost whilst you have Harmony, heal for 10% of the Damage Dealt.\n"
        "- When Lost is triggered, apply Weaken and Exposed to all enemies and gain +10 Damage for the rest of combat.\n"
        "- Upon killing an enemy, overkill damage is dealt evenly split to all living enemies.\n"
        "[bold]Stat Changes:[/bold] +20 HP. -4 Damage. +0.05 Speed. +20% Crit Damage. +10% Psychic Resistance.",
    "Abyssal": "[lore]Peace? Salvation? These words have no meaning. The darkness is your home. Your vitality, your army. The Abyss calls you by name, and it is ravenous for their corpses.[/lore]"
        "- You are always Lost. Lost has no damage bonus. 15% Less Damage Dealt. 10% Increased Max HP. 25% of Energy Shield converted to Max HP.\n"
        "- Hope and Hopeless have a maximum of 10 stacks. Radiance and Devastation have 50% Increased Effect.\n"
        "- Cumulative through combats, whenever you deal damage equal to 250% of your Max HP, gain +3% Psychic Damage permanently.\n"
        "- Upon critically hitting an enemy, gain 2 Hope and gain 1 Hunted, to a maximum of 3 Hunted. Hunted: 25% Increased Damage Dealt, -0.1 Speed, 5% Increased Damage Taken.\n"
        "- At 3 Hunted, your next attack is guaranteed to critically hit and consume all Hunted. You take 30% of the damage from a Hunted attack as Psychic Damage. This attack cannot kill you.\n"
        "- If a hunted attack kills an enemy, heal for 10% of your Max HP.\n"
        "- If you attack with 3 Hunted whilst you have Radiance, the healing always applies at double value. If you attack with 3 Hunted whilst you have Devastation, you take no damage from the attack.\n"
        "- Whenever you are critically hit, gain 2 Hopeless and 1 Hunted, and permanently lose Max HP equal to your Crit Chance.\n"
        "[bold]Stat Changes:[/bold] +30 HP. -4 Damage. +0.1 Speed. -3% Crit Chance. -10% Crit Damage. +10% Otherworld Resistance.",
    "Warper": "[lore]Something is wrong. Twisted. Unreal. Impossible. This world fails to comprehend you. It cannot contain you. It cannot release you. You: the shackle of reality.[/lore]"
        "- Lost now triggers if a hit deals less than 5% of your Max HP or a hit deals more than 20% of your Max HP.\n"
        "- Gain Warped on triggering Lost. Warped grants +20% Lifesteal to your next attack and +10% Crit Chance.\n"
        "- Triggering Warped grants 2 Hope or Hopeless, following the same rules as Lost.\n"
        "- At the start of your turn, if you are not Lost or Warped, take Psychic damage equal to 5% of your Max HP. This damage cannot kill you.\n"
        "- If you have Radiance, you are Immune to Psychic Damage. If you have Devastation, 20% Increased Defenses, +2% Max HP Regen.\n"
        "- If your attack is fully blocked by Energy Shield, gain Lost and Warped, and deal True damage to the enemy equal to 3% of your Current HP.\n"
        "[bold]Stat Changes:[/bold] +15 HP. +4 Damage. -0.1 Speed. +10% Physical Resistance. +25% Crit Damage.",
    "Mindbreaker": "[lore]Embrace the suffering. Pull them in with you. Their minds are weak, and you are the whisper of doom. Feel their sanity decay, then dismantle them swiftly.[/lore]"
        "- Non-critical hits against you deal 20% Less Damage. All Psychic Damage permanently applies Torture on targets. Torture: +2% Damage Taken, -2% Damage Dealt.\n"
        "- When Lost triggers, 1% Chance per Torture for Damage Dealt to each individual target to be doubled and apply Otherworld Exposure.\n"
        "- Enemies lose all Torture upon critically hitting you. Upon being critically hit, double how much Hope or Hopeless you have, based on whichever resource has more stacks.\n"
        "- If you have Radiance or Devastation, apply twice as much Torture. If you have Radiance, enemies are unable to lose Torture. If you have Devastation, enemies lose 1% Max HP per Torture upon losing Torture.\n"
        "- If you have Radiance, take 30% Less Damage from Otherworld Damage. If you have Devastation, chance to deal double damage per Torture is doubled.\n"
        "[bold]Stat Changes:[/bold] -20 HP. +5 Damage. -0.1 Speed. +2% Crit Chance. +20% Crit Damage. +10% Psychic Resistance.",
}

class Wanderer(Player):
    def __init__(self, name, health = 45, damage = 6, damageType = "psychic", speed = 1.1):
        super().__init__(name, health, damage, 0.1, 1.6, damageType, speed, className='Wanderer', classDescription=WANDERER_DESCRIPTIONS['Wanderer'])
        self.lostTrigger = False
        self.lostPercent = 0.1
        self.hope = 0
        self.maxHope = 5
        self.hopeless = 0
        self.maxHopeless = 5
        self.radiance = True
        self.devastation = False
        self.devastationDamage = 0
        
        self.fracture = 0
        self.fractureNoCritLastTurn = False
        self.lostHitChance = 1.0
        self.transcendence = False
        self.manifestationIncreasedDamagePercent = 0
        self.wovenDamage = 0
        self.harmony = False
        self.abyssalDamageDealt = 0
        self.abyssalDamageThreshold = self._maxHealth * 2.5
        self.abyssalPsychicBuff = 0
        self.hunted = 0
        self.abyssalMaxHPLoss = 0
        self.huntedAttackThisTurn = False
        self.warped = False

    def _recalculateStats(self, doPrint = True, inCombat = False):
        super()._recalculateStats(doPrint, inCombat)

        if self._ascendancy == 'Abyssal':
            hpGain = int(self._maxHealth * 0.1)
            esToHP = int(self.maxEnergyShield * 0.25)
            self._maxHealth = max(1, self._maxHealth  + hpGain + esToHP - self.abyssalMaxHPLoss)
            self._stats['max_energy_shield'] -= esToHP
            self.abyssalHealThreshold = int(self._maxHealth * 2.5)
            if inCombat:
                self._stats['energy_shield'] = min(self.maxEnergyShield, self.energyShield)
            else:
                self._stats['energy_shield'] = self.maxEnergyShield

            if doPrint:
                console.print(f"[asc_abyssal]Abyssal: Converted 25% of Energy Shield ({esToHP}) to Health. 10% Increased Max HP. Total Health Gain: {hpGain + esToHP}")

    def randomGainHopeOrHopeless(self):
        resourceGain = ['hope', 'hopeless']
        if self._health >= self._maxHealth * 0.5:
            resourceGain.append('hope')
        else:
            resourceGain.append('hopeless')
        if not self.radiance and not self.devastation and not self._ascendancy == 'Manifestation':
            gain = random.choice(resourceGain)
            if gain == 'hope':
                self.gainHope()
                if self._ascendancy == 'Manifestation':
                    self.gainHope()
            else:
                self.gainHopeless()
                if self._ascendancy == 'Manifestation':
                    self.gainHopeless()

    def gainHope(self):
        mult = 1
        if self._ascendancy == 'Fractured':
            mult = 0.5
        if self.hope < self.maxHope:
            self.hope += 1
            self._stats['Temporary']['crit_chance'] += 0.02 * mult
            self.gainRadiance()

    def loseHope(self):
        if self.hope > 0:
            self.hope -= 1
            self._stats['Temporary']['crit_chance'] -= 0.02
            self.loseRadiance()

    def gainRadiance(self):
        mult = 1
        if self._ascendancy == 'Abyssal':
            mult = 1.5
        if not self.radiance and self.hope == self.maxHope:
            self._stats['Temporary']['crit_chance'] += 0.25 * mult
            self._stats['Temporary']['crit_multi'] += 0.75 * mult
            self.radiance = True

    def loseRadiance(self):
        mult = 1
        if self._ascendancy == 'Abyssal':
            mult = 1.5
        if self.radiance and self.hope < self.maxHope:
            self._stats['Temporary']['crit_chance'] -= 0.25 * mult
            self._stats['Temporary']['crit_multi'] -= 0.75 * mult
            self.radiance = False

    def radianceHeal(self):
        if self.radiance:
            maxHeal = self._maxHealth - self._health
            heal = min(maxHeal, int(self._maxHealth * (0.1 if self._ascendancy != 'Abyssal' else 0.15)))
            excess = int(self._maxHealth * 0.1) - heal
            self.heal(heal)
            self._shield += excess
            shieldStr = f" and gained {excess} Shield" if excess > 0 else ""
            console.print(f"[class_wanderer]Wanderer: Radiance! Healed for {heal} HP{shieldStr}.[/class_wanderer]")

    def gainHopeless(self):
        mult = 1
        if self._ascendancy == 'Fractured':
            mult = 0.5
        if self.hopeless < self.maxHopeless:
            self.hopeless += 1
            self._stats['Temporary']['damage_reduction'] += 2 * mult
            self._stats['Temporary']['crit_multi'] += 0.1 * mult
            self.gainDevastation()

    def loseHopeless(self):
        if self.hopeless > 0:
            self.hopeless -= 1
            self._stats['Temporary']['damage_reduction'] -= 2
            self._stats['Temporary']['crit_multi'] -= 0.1
            self.loseDevastation()

    def gainDevastation(self):
        if not self.devastation and self.hopeless == self.maxHopeless:
            if self._ascendancy == 'Fractured':
                for _ in range(self.fracture):
                    self._stats['Temporary']['crit_chance'] -= 0.03
                    self._stats['Temporary']['crit_multi'] += 0.1
            elif self._ascendancy == 'Weaver':
                self._stats['Temporary']['crit_chance'] += 0.1
                self._stats['Temporary']['speed'] -= 0.2
                self._stats['Temporary']['increased_defenses'] -= 10
            elif self._ascendancy == 'Warper':
                self._stats['Temporary']['increased_defenses'] += 20

    def loseDevastation(self):
        if self.devastation and self.hopeless < self.maxHopeless:
            self.devastation = False

    def gainFracture(self):
        if self.fracture < 5:
            self.fracture += 1
            if self.devastation:
                self._stats['Temporary']['crit_damage'] += 0.1
            else:
                self._stats['Temporary']['crit_chance'] += 0.03
            console.print(f"[asc_fractured]Fractured: Gained 1 stack of Fracture. Current Fracture stacks: {self.fracture}/5[/asc_fractured]")

    def loseAllFracture(self):
        if self.devastation:
            self._stats['Temporary']['crit_damage'] -= 0.1 * self.fracture
        else:
            self._stats['Temporary']['crit_chance'] -= 0.03 * self.fracture
        self.fracture = 0

    def updateTranscendence(self):
        if self._ascendancy == 'Manifestation':
            if self.radiance and self.devastation and not self.transcendence:
                self._stats['Temporary']['increased_defenses'] += 20
                self._stats['Temporary']['increased_evasion'] -= 75
                self.transcendence = True
            elif self.transcendence and not (self.radiance or self.devastation):
                self._stats['Temporary']['increased_defenses'] -= 20
                self._stats['Temporary']['increased_evasion'] -= 75
                self.transcendence = False

    def updateHarmony(self):
        if self._ascendancy == 'Weaver':
            if self.hope == self.hopeless and not self.harmony:
                self._stats['Temporary']['crit_multi'] += 0.5
                self._stats['Temporary']['speed'] += 0.2
                self.harmony = True
            elif self.hope != self.hopeless and self.harmony:
                self._stats['Temporary']['crit_multi'] -= 0.5
                self._stats['Temporary']['speed'] -= 0.2
                self.harmony = False

    def gainHunted(self):
        if self._ascendancy == 'Abyssal' and self.hunted < 3:
            self.hunted += 1
            self._stats['Temporary']['speed'] -= 0.1
            if self.hunted == 3:
                self._stats['Temporary']['crit_chance'] += 1

    def loseAllHunted(self):
        if self._ascendancy == 'Abyssal':
            self._stats['Temporary']['speed'] += 0.3
            self._stats['Temporary']['crit_chance'] -= 1
            self.hunted = 0
            self.huntedAttackThisTurn = True

    def onBeforeDamage(self, ability, damage, damageType, targets, combatManager):
        if random.random() < self.lostHitChance:
            if self._ascendancy == 'Manifestation':
                console.print('  [warning]- Manifestation: Lost attack missed! Applied Otherworld Exposure to all enemies.[/warning]')
                exposure = Effects.createOtherworldExposure()
                for enemy in combatManager.allAlive:
                    combatManager.addStatusEffect(enemy, exposure, self)
                return damage, damageType, None

        if self.lostTrigger and damageType != 'heal':
            console.print('  [buff]- Wanderer: Lost triggered. Attacking all enemies for 150% damage.[/buff]')
            targets = combatManager.allAlive

            if self._ascendancy == 'Weaver':
                self.wovenDamage += 10
                self._queueEffect(Effects.createWeaken())
                self._queueEffect(Effects.createExposed())
                console.print('  [buff]- Weaver: Lost Triggered! Applied Weaken and Lost to all enemies! +10 Damage for the rest of combat.[/buff]')

        if self._ascendancy == 'Fractured':
            if self.fracture >= 5 and damageType != 'heal':
                console.print("[asc_fractured]- Fractured: Fracture stacks have reached 5. Your next attack with target all enemies for 150% damage and set Fracture to 0.[/asc_fractured]")
                self.loseAllFracture()
                targets = combatManager.allAlive

        return damage, damageType, targets

    def onPrepareHit(self, target, targetUnit, finalDamage, damageType, combatManager):
        finalDamage = super().onPrepareHit(target, targetUnit, finalDamage, damageType, combatManager)
        if self._ascendancy == 'Mindbreaker':
            if damageType == 'psychic':
                target.tortureStacks += 1
                if self.radiance or self.devastation:
                    target.tortureStacks += 1
            doubleDamageChance = target.tortureStacks / (100 if not self.devastation else 50)
            if self.lostTrigger and random.random() <= doubleDamageChance:
                finalDamage *= 2
                self._queueEffect(Effects.createOtherworldExposure())
        return finalDamage

    def onKill(self, entity, attackData, combatManager):
        super().onKill()
        if self.radiance:
            self.radianceHeal()

        if self._ascendancy == 'Manifestation':
            consume = random.choice(['hope', 'hopeless'])
            if consume == 'hope':
                hopeHeal = 0.03 * self.hope
                self.heal(hopeHeal)
                for _ in range(self.hope):
                    self.loseHope()
            else:
                self.manifestationIncreasedDamagePercent += 0.2 * self.hopeless
                for _ in range(self.hopeless):
                    self.loseHopeless()

        elif self._ascendancy == 'Weaver':
            overkill = max(0, -entity._health)
            remainingEnemies = combatManager.allAlive
            numEnemies = len(remainingEnemies)
            if numEnemies > 0:
                damageToAll = int(overkill / numEnemies)
                console.print(f"  [buff]- Weaver: Overkill! {damageToAll} Damage Dealt to all living enemies")
                for e in remainingEnemies:
                    e.damage(damageToAll, attackData.get('damageType', self._damageType))

        elif self._ascendancy == 'Abyssal' and self.huntedAttackThisTurn:
            heal = int(self._maxHealth * 0.1)
            if self.radiance:
                heal *= 2
            self.heal(heal)

        return {}

    def onDealDamage(self, target, targetUnit, finalDamage, damageType, evaded, armourDamagePrevented, esDamagePrevented, combatManager):
        if self._ascendancy == 'Warper':
            if finalDamage == 0 and esDamagePrevented > 0:
                self.lostTrigger = True
                self.warped = True
                dmg = int(self._health * 0.03)
                target.damage(dmg, 'true')

        return finalDamage

    def onAttack(self, damageDealt, damageType, target, combatManager, ability, crit):
        damageDealt, damageType = super().onAttack(damageDealt, damageType, target, combatManager, ability, crit)

        if self._ascendancy == 'Fractured':
            if self.lostTrigger and self.fracture == 5:
                for _ in range(self.hope):
                    self.gainHope()
                for _ in range(self.hopeless):
                    self.gainHopeless()

        if self.lostTrigger:
            if self.devastation:
                self.devastationDamage += int(self._maxHealth * 0.03 * (1.5 if self._ascendancy == 'Abyssal' else 1))

            if self._ascendancy != 'Abyssal':
                damageDealt = int(damageDealt * 1.5)
                self.lostTrigger = False
            if self._ascendancy == 'Fractured':
                self.gainFracture()
                if self.radiance:
                    self.gainFracture()
                if self.hope < self.hopeless:
                    damageDealt = int(damageDealt * 1.6)
            elif self._ascendancy == 'Weaver' and self.harmony:
                heal = int(damageDealt * 0.1)
                self.heal(heal)

            self.randomGainHopeOrHopeless()

        damageDealt = int(damageDealt * (1 + (0.1 * self.hope)))

        if self.devastation:
            damageDealt = int(damageDealt * (2.5 if self._ascendancy == 'Abyssal' else 2))

        if self._ascendancy == 'Fractured' and self.fracture > 0:
            if damageType == 'psychic':
                damageDealt = int(damageDealt * (1 + 0.05 * self.fracture))
            if self.fracture >= 5:
                damageDealt = int(damageDealt * 1.5)
            if self.hope > self.hopeless and not crit:
                damageDealt = int(damageDealt * 0.6)

        elif self._ascendancy == 'Manifestation':
            if self.transcendence and damageType == 'psychic':
                damageDealt = int(damageDealt * 1.25)
            damageDealt = int(damageDealt * (1 + self.manifestationIncreasedDamagePercent))
            self.manifestationIncreasedDamagePercent = 0

        elif self._ascendancy == 'Weaver':
            damageDealt += self.wovenDamage
            if damageType == 'psychic':
                damageDealt = int(damageDealt * 1.2)
            else:
                damageDealt = int(damageDealt * 0.7)
            if self.harmony:
                damageDealt = int(damageDealt * 1.3)

        elif self._ascendancy == 'Abyssal':
            damageDealt = int(damageDealt * 0.85)
            if damageType == 'psychic':
                damageDealt = int(damageDealt * (1 + self.abyssalPsychicBuff))
            damageDealt = int(damageDealt * (1 + (0.25 * self.hunted)))
            self.abyssalDamageDealt += damageDealt

        elif self._ascendancy == 'Warper' and self.warped:
            self.warped = False
            self._stats['Temporary']['lifesteal'] -= 20
            self._stats['Temporary']['crit_chance'] -= 0.1
            self.randomGainHopeOrHopeless()
            self.randomGainHopeOrHopeless()

        return damageDealt, damageType

    def onHit(self, damageTaken, damageType, crit, attacker, combatManager):
        damageTaken, damageType = super().onHit(damageTaken, damageType, crit, attacker, combatManager)

        if self.devastation:
            damageTaken = int(damageTaken * (1.2 if self._ascendancy != 'Abyssal' else 1.3))

        if damageTaken >= round(self._maxHealth * self.lostPercent):
            self.lostTrigger = True
            console.print(f"\n[buff]Wanderer: Took more than 10% of max health as damage! Lost has been activated.[/buff]")

            if self._ascendancy == 'Fractured':
                self.gainFracture()

        if self._ascendancy == 'Manifestation' and self.transcendence:
            dmg = int(attacker._maxHealth * 0.05)
            attacker.damage(dmg, 'true')

        elif self._ascendancy == 'Warper':
            if damageTaken <= int(self._maxHealth * 0.05):
                self.lostTrigger = True
            if self.lostTrigger and not self.warped:
                self.warped = True
                self._stats['Temporary']['lifesteal'] += 20
                self._stats['Temporary']['crit_chance'] += 0.1

        elif self._ascendancy == 'Weaver' and damageType in DIVINE_RES:
            self.gainHopeless()
            self.gainHopeless()

        elif self._ascendancy == 'Abyssal':
            damageTaken = int(damageTaken * (1 + (0.05 * self.hunted)))

        elif self._ascendancy == 'Mindbreaker':
            if not crit:
                damageTaken = int(damageTaken * 0.8)
            if self.radiance and damageType in OTHERWORLD_RES:
                damageTaken = int(damageTaken * 0.7)

        return damageTaken, damageType

    def damage(self, damage, damageType = 'physical', combatUnit=None, *, lethal = True, attacker = None):
        if self._ascendancy == 'Warper' and self.radiance and damageType == 'psychic':
            damage = 0

        damageReductionValue = super().damage(damage, damageType, combatUnit, lethal=lethal, attacker=attacker)

        return damageReductionValue

    def onBeforeCritRoll(self, targetUnit, targets, combatManager):
        if self._ascendancy == 'Manifestation' and self.transcendence:
            self.manifestationCritGained = True
            self._stats['Temporary']['crit_chance'] += 1

    def onAfterCritRoll(self, targetUnit, targets, combatManager):
        if self._ascendancy == 'Manifestation' and (self.transcendence):
            self._stats['Temporary']['crit_chance'] -= 1

    def onCrit(self, targets, combatManager, critDamage):
        if self.radiance:
            self.radianceHeal()

        if self._ascendancy == 'Fractured':
            damageTaken = int(self._maxHealth * 0.02)
            console.print(f"[asc_fractured]- Fractured: Dealt a critical strike. 2% of Max HP taken as Psychic Damage.[/asc_fractured]")
            self.damage(damageTaken, 'psychic')
            self.gainHope()
            if self.hope > self.hopeless:
                critDamage *= 2

        elif self._ascendancy == 'Abyssal':
            self.gainHope()
            self.gainHope()
            if self.hunted == 3:
                if not self.devastation:
                    selfDmg = int(critDamage * 0.3)
                    self.damage(selfDmg, 'psychic', lethal=False)
                self.loseAllHunted()
            self.gainHunted()

        return critDamage

    def onCriticallyHit(self, attacker, combatManager, critDamage, damageType):
        if self._ascendancy == 'Fractured':
            heal = int(self._maxHealth * 0.01 * (self.hope + self.hopeless))
            self.heal(heal)
            self.gainHopeless()

        elif self._ascendancy == 'Weaver':
            if self.hope > self.hopeless:
                self.gainHope()
                self.gainHope()
            else:
                self.gainHopeless()
                self.gainHopeless()

        elif self._ascendancy == 'Abyssal':
            self.gainHopeless()
            self.gainHopeless()
            self.gainHunted()
            hpLoss = int(self.critChance * 100)
            self.abyssalMaxHPLoss += hpLoss

        elif self._ascendancy == 'Mindbreaker':
            if self.hope > self.hopeless:
                for _ in range(self.hope):
                    self.gainHope()
            else:
                for _ in range(self.hopeless):
                    self.gainHopeless()

        return critDamage

    def onTurnStart(self, combatManager):
        if self._ascendancy == 'Fractured':
            if self.hope < self.hopeless and not self.fractureNoCritLastTurn:
                self._stats['Temporary']['crit_chance'] -= 100
            elif self.hope > self.hopeless and self.fractureNoCritLastTurn:
                self._stats['Temporary']['crit_chance'] += 100
        elif self._ascendancy == 'Abyssal' and not self.lostTrigger:
            self.lostTrigger = True
        elif self._ascendancy == 'Warper':
            if not self.lostTrigger and not self.warped:
                damage = int(self._maxHealth * 0.02)
                console.print(f"\n [warning]Warper: Not Warped or Lost! {damage} Damage taken.[/warning]")
                self.damage(damage, 'psychic', lethal=False)
            if self.devastation:
                heal = int(self._maxHealth + 0.02)
                self.heal(heal)

        super().onTurnStart(combatManager)

    def onCombatEnd(self):
        if self._ascendancy == 'Abyssal':
            while self.abyssalDamageDealt >= self.abyssalDamageThreshold:
                self.abyssalDamageDealt -= self.abyssalDamageThreshold
                self.abyssalPsychicBuff += 0.03
                console.print(f"  [buff]Abyssal: 250% of Max HP dealt as damage! +3% Psychic Damage permanently. +{int(self.abyssalPsychicBuff*100)}% Total Psychic Damage.[/buff]")

        if self._ascendancy != 'Abyssal':
            self.lostTrigger = False
        self.lostPercent = 0.1
        self.hope = 0
        self.maxHope = 5
        self.hopeless = 0
        self.maxHopeless = 5
        self.radiance = True
        self.devastation = False
        self.devastationDamage = 0
        
        self.fracture = 0
        self.fractureNoCritLastTurn = False
        self.lostHitChance = 1.0
        self.transcendence = False
        self.manifestationIncreasedDamagePercent = 0
        self.wovenDamage = 0
        self.harmony = False
        self.abyssalDamageDealt = 0
        self.abyssalDamageThreshold = self._maxHealth * 2.5
        self.abyssalPsychicBuff = 0
        self.hunted = 0
        self.abyssalMaxHPLoss = 0
        self.huntedAttackThisTurn = False
        self.warped = False
        super().onCombatEnd()

    def _removeOldAscendancy(self) -> bool:
        self.lostPercent = 0.1
        if self._ascendancy == 'Fractured':
            self._baseHealth += 10
            self._baseDamage -= 4
            self._baseSpeed -= 0.05
            self._stats['baseCritChance'] -= 0.02
            self._stats['baseCritMulti'] -= 0.2
        elif self._ascendancy == 'Manifestation':
            self._baseHealth -= 25
            self._baseDamage += 4
            self._baseSpeed += 0.05
            self._stats['baseCritMulti'] -= 0.25
            self.lostHitChance = 1.0
        elif self._ascendancy == 'Weaver':
            self._baseHealth -= 20
            self._baseDamage += 4
            self._baseSpeed -= 0.05
            self._stats['baseCritMulti'] -= 0.2
            self._stats['Permanent']['psychic'] -= 10
        elif self._ascendancy == 'Abyssal':
            self._baseHealth -= 30
            self._baseDamage += 4
            self._baseSpeed -= 0.1
            self._stats['baseCritChance'] += 0.03
            self._stats['baseCritMulti'] += 0.1
            self._stats['Permanent']['otherworld'] -= 10
        elif self._ascendancy == 'Warper':
            self._baseHealth -= 15
            self._baseDamage -= 4
            self._baseSpeed += 0.1
            self._stats['Permanent']['physical'] -= 10
            self._stats['baseCritMulti'] -= 0.25
        elif self._ascendancy == 'Mindbreaker':
            self._baseHealth += 20
            self._baseDamage -= 5
            self._baseSpeed += 0.1
            self._stats['baseCritChance'] -= 0.02
            self._stats['baseCritMulti'] -= 0.2
            self._stats['Permanent']['psychic'] -= 10
        return True

    def updateAscendancy(self, ascendancy):
        if not super().updateAscendancy(ascendancy):
            return
        self._ascendancy = ascendancy
        self.ascendancyDescription = WANDERER_DESCRIPTIONS[ascendancy]
        if ascendancy == 'Fractured':
            self._baseHealth -= 10
            self._baseDamage += 4
            self._baseSpeed += 0.05
            self._stats['baseCritChance'] += 0.02
            self._stats['baseCritMulti'] += 0.2
        elif ascendancy == 'Manifestation':
            self._baseHealth += 25
            self._baseDamage -= 4
            self._baseSpeed -= 0.05
            self._stats['baseCritMulti'] += 0.25
            self.lostPercent = 0.05
            self.lostHitChance = 0.8
            self.maxHope = 8
            self.maxHopeless = 8
        elif ascendancy == 'Weaver':
            self._baseHealth += 20
            self._baseDamage -= 4
            self._baseSpeed += 0.05
            self._stats['baseCritMulti'] += 0.2
            self._stats['Permanent']['psychic'] += 10
            self.lostPercent = 0.15
        elif ascendancy == 'Abyssal':
            self._baseHealth += 30
            self._baseDamage -= 4
            self._baseSpeed += 0.1
            self.lostTrigger = True
            self.maxHope = 10
            self.maxHopeless = 10
            self._stats['baseCritChance'] -= 0.03
            self._stats['baseCritMulti'] -= 0.1
            self._stats['Permanent']['otherworld'] += 10
        elif ascendancy == 'Warper':
            self._baseHealth += 15
            self._baseDamage += 4
            self._baseSpeed -= 0.1
            self._stats['Permanent']['physical'] += 10
            self._stats['baseCritMulti'] += 0.25
            self.lostTrigger = 0.2
            self.maxHope = 10
            self.maxHopeless = 10
        elif ascendancy == 'Mindbreaker':
            self._baseHealth -= 20
            self._baseDamage += 5
            self._baseSpeed -= 0.1
            self._stats['baseCritChance'] += 0.02
            self._stats['baseCritDamage'] += 0.2
            self._stats['Permanent']['psychic'] += 10
        self._recalculateStats()

...