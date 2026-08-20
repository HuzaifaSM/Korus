from .base import Player
from scripts.styles import console, pause
from scripts.abilities import Effects
import random

"""
to implement:
hope/Hopeless, hollow/radiance for all ascendancies
"""

WANDERER_DESCRIPTIONS = {
    "Wanderer": "[class_wanderer]The lost soul of a greater power, eternally searching for peace.[/class_wanderer]\n"
        "- Lost: If a single hit deals more than 10% of your Max HP, your next attack will deal 50% More Damage and target all enemies.\n"
        "- Whenever Lost is triggered, randomly gain 1 Hope or 1 Hopeless. Hope and Hopeless both have a maximum of 5 stacks.\n"
        "- If you have more than 50% Max HP remaining, you are more likely to gain Hope. If you have less than 50% Max HP remaining, you are more likely to gain Hopeless.\n"
        "- Hope: 10% Increased Psychic Damage, +2% Crit Chance. Hopeless: +2 Damage Reduction, +10% Crit Damage.\n"
        "- Upon reaching 5 Hope, gain Radiance, and you can no longer gain Hopeless. Upon reaching 5 Hopeless, gain Devastation, and you can no longer gain Hope.\n"
        "- Radiance: +25% Crit Chance, +75% Crit Damage. Upon killing or critically hitting an enemy, heal for 10% of your Max HP. Excess healing is gained as Shield.\n"
        "- Devastation: 100% Increased Damage Dealt, 20% More Damage Taken. Whenever Lost is triggered, gain Damage equal to 1% of your Max HP for the rest of combat.\n"
        "Starting Stats: 40 HP | 6 Damage | 10% Crit Chance | 160% Crit Damage | Psychic Damage | 1.1 Speed.",
    #ascdenancies
    "Fractured": "[lore]You were never whole. Every wound reveals another piece. Every drop of their blood, another reason to continue. Among the fragments lies the truth.[/lore]\n"
        "- Upon triggering Lost, gain Fracture, up to 5 stacks. Fracture: +5% Psychic Damage. +3% Crit Chance. At 5 Fracture, your next attack deals 150% Damage to all enemies, and Fracture is set to 0.\n"
        "- If you trigger Lost and Fracture at the same time, double your Hope and Hopeless. Hope and Hopeless have 50% Reduced Effect.\n"
        "- If you have Radiance, gain 2 Fracture upon triggering Lost. If you have Devastation, Fracture grants +10% Crit Damage instead of +3% Crit Chance.\n"
        "- Whilst you have more Hopeless than Hope, your Crit Chance is 0, but Lost attacks deal 50% Increased Damage.\n"
        "- Whilst you have more Hope than Hopeless, your Crit Damage is doubled, Non-critical hits do 40% Less Damage.\n"
        "- Upon critically hitting an enemy, take Psychic damage equal to 2% of your Max HP and gain 1 Hope.\n"
        "- When an enemy critically hits you, heal 1% Max HP per stack of Hope and Hopeless you have, and gain 1 Hopeless.\n"
        "[bold]Stat Changes:[/bold] -10 HP. +1 Damage. +0.05 Speed. +3% Crit Chance. +20% Crit Damage.",
    "Manifestation": "[lore]Your search was fruitless. A meaningless excuse. No longer. The truth shall rewrite reality. Become as you were, and unmake them.[/lore]\n"
        "- Lost triggers upon taking more than 5% of your Max HP. Lost attacks have a 20% Chance to miss. Upon missing a Lost attack, apply Otherworld Exposure to all enemies, and lose 3 Hope.\n"
        "- When gaining Hope or Hopeless, gain twice as much and lose 1 of the alternate resource. Hope and Hopeless have a maximum of 8 stacks.\n"
        "- You are able to have Radiance and Devastation at the same time. If you have Radiance and Devastation, gain Transcendence.\n"
        "- Transcendence: All attacks are Critical Hits, 20% Increased Defenses, 25% Increased Psychic Damage, 75% Less Evasion.\n"
        "- If you are hit whilst you have Transcendence, your attacker takes True damage equal to 5% of their Max HP.\n"
        "- Whenever an enemy dies, randomly consume all your Hope or Hopeless. Consuming Hope heals you for 3% Max HP per stack consumed. Consuming Hopeless grants 20% Increased damage on your next attack per stack consumed.\n"
        "[bold]Stat Changes:[/bold] +10 HP. -1 Damage. -0.05 Speed.",
    "Weaver": "[lore]Peace, a dull concept. Harmony, a beautiful one. Unfurl the tapestry of fate. Recreate them in your image. Then cut them down, until threads remain.[/lore]\n"
        "- 20% Increased Psychic Damage dealt. 30% Less Non-Psychic Damage dealt. Upon taking Divine Damage, gain 2 Hopeless.\n"
        "- Devastation now also grants +10% Crit Chance, -0.2 Speed, and 10% Reduced Defenses.\n"
        "- Whenever you are critically hit, gain 2 Hope or Hopeless, depending on which resource you have more of. Hope and Hopeless have a maximum of 10 stacks.\n"
        "- If your Hope and Hopeless are equal, gain Harmony: 30% Increased Damage Dealt, +50% Crit Damage, +0.2 Speed.\n"
        "- If you trigger Lost whilst you have Harmony, heal for 10% of the Damage Dealt per enemy.\n"
        "- When Lost is triggered, apply Weaken and Exposed to all enemies and gain +10 Damage for the rest of combat.\n"
        "- Upon killing an enemy, overkill damage is dealt evenly split to all living enemies.\n"
        "[bold]Stat Changes:[/bold] +15 HP. -4 Damage. +20% Crit Damage. +10% Psychic Resistance.",
    "Abyssal": "[lore]Peace? Salvation? These words have no meaning. The darkness is your home. Your vitality, your army. The Abyss calls you by name, and it is ravenous for their corpses.[/lore]\n"
        "- You are always Lost. Lost has no damage bonus. 10% Less Damage Dealt. 10% Increased Max HP. 25% of Energy Shield converted to Max HP.\n"
        "- Hope and Hopeless have a maximum of 10 stacks. Radiance and Devastation have 50% Increased Effect.\n"
        "- Cumulative through combats, whenever you deal damage equal to 250% of your Max HP, gain +3% Psychic Damage permanently.\n"
        "- Upon critically hitting an enemy, gain 2 Hope and gain 1 Hunted, to a maximum of 3 Hunted. Hunted: 25% Increased Damage Dealt, -0.1 Speed, 5% Increased Damage Taken.\n"
        "- At 3 Hunted, your next attack is guaranteed to critically hit, but also hits you for 30% of the total damage. This attack cannot kill you. If a hunted attack kills an enemy, heal for 10% of your Max HP.\n"
        "- If you attack with 3 Hunted whilst you have Radiance, the healing always applies at double value. If you attack with 3 Hunted whilst you have Devastation, the Damage Dealt is doubled, and only hits you for 5% of the total damage.\n"
        "- Whenever you are critically hit, gain 2 Hopeless and 1 Hunted, and lose Max HP equal to your Crit Chance.\n"
        "[bold]Stat Changes:[/bold] +30 HP. -4 Damage. +0.1 Speed. -3% Crit Chance. -10% Crit Damage. +5% [all]All[/all] Res.",
    "Warper": "[lore]Something is wrong. Twisted. Unreal. Impossible. This world fails to comprehend you. It cannot contain you. It cannot release you. You: the shackle of reality.[/lore]\n"
        "- Lost now triggers if a hit deals less than 5% of your Max HP or a hit deals more than 20% of your Max HP.\n"
        "- Gain Warped on triggering Lost. Warped grants +20% Lifesteal to your next attack and +10% Crit Chance.\n"
        "- Triggering Warped grants 2 Hope or Hopeless, following the same rules as Lost.\n"
        "- At the start of your turn, if you are not Lost or Warped, take Psychic damage equal to 5% of your Max HP. This damage cannot kill you.\n"
        "- If you have Radiance, you are Immune to Psychic Damage. If you have Devastation, 20% Increased Defenses, +2% Max HP Regen.\n"
        "- If your attack is fully blocked by Energy Shield, gain Lost and Warped, and deal True damage to the enemy equal to 3% of your Current HP.\n"
        "[bold]Stat Changes:[/bold] +10 HP. +2 Damage. -0.1 Speed. +25% Crit Damage.",
    "Mindbreaker": "[lore]Embrace the suffering. Pull them in with you. Their minds are weak, and you are the whisper of doom. Feel their sanity decay, then dismantle them swiftly.[/lore]\n"
        "- Non-critical hits against you deal 20% Less Damage. All Psychic Damage permanently applies Torture on targets. Torture: +2% Damage Taken, -2% Damage Dealt.\n"
        "- When Lost triggers, 1% Chance per Torture for Damage Dealt to each individual target to be doubled and apply Otherworld Exposure.\n"
        "- Enemies lose all Torture upon critically hitting you. Upon being critically hit, double how much Hope or Hopeless you have, based on whichever resource has more stacks.\n"
        "- If you have Radiance or Devastation, apply twice as much Torture. If you have Radiance, enemies are unable to lose Torture. If you have Devastation, enemies lose 1% Max HP per Torture upon losing Torture.\n"
        "- If you have Radiance, take 30% Less Damage from Otherworld Damage. If you have Devastation, chance to deal double damage per Torture is doubled.\n"
        "[bold]Stat Changes:[/bold] -10 HP. +2 Damage. -0.1 Speed. +3% Crit Chance. +10% Psychic Resistance.",
}

class Wanderer(Player):
    def __init__(self, name, health = 45, damage = 6, damageType = "psychic", speed = 1.1):
        super().__init__(name, health, damage, 0.1, 1.6, damageType, speed, className='Wanderer', classDescription=WANDERER_DESCRIPTIONS['Wanderer'])
        self.lostTrigger = False
        self.lostPercent = 0.1
        
        self.fracture = 0
        self.lostHitChance = 1.0
        self.wovenDamage = 0
        self.abyssalDamageDealt = 0
        self.abyssalDamageThreshold = self._maxHealth * 2
        self.abyssalPsychicBuff = 0
        self.warped = False

    def _recalculateStats(self, doPrint = True):
        super()._recalculateStats(doPrint)
        self.abyssalHealThreshold = self._maxHealth * 2

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
                console.print("  [buff]- Fractured: Fracture stacks have reached 5. Attacking all enemies for 150% damage. Fracture stacks set to 0.[/buff]")
                targets = combatManager.allAlive

        return damage, damageType, targets

    def onPrepareHit(self, target, targetUnit, finalDamage, damageType, combatManager):
        finalDamage = super().onPrepareHit(target, targetUnit, finalDamage, damageType, combatManager)
        if self._ascendancy == 'Mindbreaker':
            if damageType == 'psychic':
                target.tortureStacks += 1
            if self.lostTrigger and random.random() <= (target.tortureStacks / 100):
                finalDamage *= 2
                self._queueEffect(Effects.createOtherworldExposure())
        return finalDamage

    def onKill(self, entity, attackData, combatManager=None):
        super().onKill()
        if self._ascendancy == 'Weaver' and combatManager:
            overkill = max(0, -entity._health)
            remainingEnemies = combatManager.allAlive
            numEnemies = len(remainingEnemies)
            if numEnemies > 0:
                damageToAll = int(overkill / numEnemies)
                console.print(f"  [buff]- Weaver: Overkill! {damageToAll} Damage Dealt to all living enemies")
                for e in remainingEnemies:
                    e.damage(damageToAll, attackData.get('damageType', self._damageType))
        return {}

    def onAttack(self, damageDealt, damageType, target, combatManager, ability):
        damageDealt, damageType = super().onAttack(damageDealt, damageType, target, combatManager, ability)
        if self.lostTrigger and self._ascendancy != 'Abyssal':
            damageDealt = int(damageDealt * 1.5)
            self.lostTrigger = False

        if self._ascendancy == 'Fractured' and self.fracture > 0:
            if damageType == 'psychic':
                damageDealt = int(damageDealt * (1 + 0.05 * self.fracture))
            if self.fracture >= 5:
                damageDealt = int(damageDealt * 1.5)
                self.fracture = 0
            
        elif self._ascendancy == 'Weaver':
            damageDealt += self.wovenDamage

        elif self._ascendancy == 'Abyssal':
            if damageType == 'psychic':
                damageDealt = int(damageDealt * (1 + self.abyssalPsychicBuff))
            damageDealt = int(damageDealt * 0.9)
            self.abyssalDamageDealt += damageDealt

        elif self._ascendancy == 'Warper' and self.warped:
            self.warped = False
            self._stats['Temporary']['lifesteal'] -= 20
            self._stats['Temporary']['crit_chance'] -= 0.1

        return damageDealt, damageType

    def onHit(self, damageTaken, damageType, crit, attacker, combatManager):
        damageTaken, damageType = super().onHit(damageTaken, damageType, crit, attacker, combatManager)
        if damageTaken >= round(self._maxHealth * self.lostPercent):
            self.lostTrigger = True
            console.print(f"\n[buff]Wanderer: Took more than 10% of max health as damage! Lost has been activated.[/buff]")

            if self._ascendancy == 'Fractured':
                self.fracture = min(5, self.fracture + 1)
                self._stats['Temporary']['crit_chance'] = self.fracture * 0.03
                console.print(f"\n  [buff]Fractured: Gained 1 stack of Fracture. Current Fracture stacks: {self.fracture} / 5[/buff]")

        if self._ascendancy == 'Warper':
            if damageTaken <= int(self._maxHealth * 0.05):
                self.lostTrigger = True
            if self.lostTrigger and not self.warped:
                self.warped = True
                self._stats['Temporary']['lifesteal'] += 20
                self._stats['Temporary']['crit_chance'] += 0.1

        return damageTaken, damageType

    def rollCritical(self, target, damageDealt=None):
        crit, critMulti = super().rollCritical(target, damageDealt)
        if self._ascendancy == 'Fractured':
            damageTaken = int(self._maxHealth * 0.02)
            console.print(f"  [warning]- Fractured: Dealt a critical strike. 2% of Max HP lost. -{damageTaken} HP.[/warning]")
            self.damage(damageTaken, 'psychic')

        return crit, critMulti

    def onTurnStart(self, combatManager=None):
        if self._ascendancy == 'Abyssal' and not self.lostTrigger:
            self.lostTrigger = True
        if self._ascendancy == 'Warper':
            if not self.lostTrigger and not self.warped:
                damage = int(self._maxHealth * 0.02)
                console.print(f"\n [warning]Warper: Not Warped or Lost! {damage} Damage taken.[/warning]")
                self.damage(damage, 'psychic')

    def onCombatEnd(self):
        if self._ascendancy == 'Abyssal':
            if self.abyssalDamageDealt >= self.abyssalDamageThreshold:
                self.abyssalDamageDealt -= self.abyssalDamageThreshold
                self.abyssalPsychicBuff += 0.03
                console.print(f"  [buff]Abyssal: 200% of Max HP dealt as damage! +3% Psychic Damage permanently. +{int(self.abyssalPsychicBuff*100)}% Total Psychic Damage.[/buff]")

        self.lostTrigger = False
        self.wovenDamage = 0
        self.abyssalPsychicBuff = 0
        self.warped = False
        super().onCombatEnd()

    def _removeOldAscendancy(self) -> bool:
        if self._ascendancy == 'Fractured':
            self._baseHealth += 10
            self._baseDamage -= 1
            self._baseSpeed -= 0.05
            self._stats['baseCritChance'] -= 0.02
            self._stats['baseCritMulti'] -= 0.2
        elif self._ascendancy == 'Manifestation':
            self._baseHealth -= 10
            self._baseDamage += 1
            self._baseSpeed += 0.05
            self.lostPercent = 0.1
            self.lostHitChance = 1.0
        elif self._ascendancy == 'Weaver':
            self._baseHealth -= 15
            self._baseDamage += 4
            self._stats['baseCritMulti'] -= 0.2
            self._stats['Permanent']['psychic'] -= 10
        elif self._ascendancy == 'Abyssal':
            self._baseHealth -= 30
            self._baseDamage += 4
            self._baseSpeed -= 0.1
            self._stats['baseCritChance'] += 0.03
            self._stats['baseCritMulti'] += 0.1
            self._stats['Permanent']['all'] -= 5
        elif self._ascendancy == 'Warper':
            self._baseHealth -= 10
            self._baseDamage -= 2
            self._baseSpeed += 0.1
            self._stats['baseCritMulti'] -= 0.25
        elif self._ascendancy == 'Mindbreaker':
            self._baseHealth += 10
            self._baseDamage -= 2
            self._baseSpeed += 0.1
            self._stats['baseCritChance'] -= 0.03
            self._stats['Permanent']['psychic'] -= 10
        return True

    def updateAscendancy(self, ascendancy):
        super().updateAscendancy(ascendancy)
        if ascendancy == 'Fractured':
            self._baseHealth -= 10
            self._baseDamage += 1
            self._baseSpeed += 0.05
            self._stats['baseCritChance'] += 0.02
            self._stats['baseCritMulti'] += 0.2
            self._ascendancy = 'Fractured'
            self.ascendancyDescription = WANDERER_DESCRIPTIONS['Fractured']
        elif ascendancy == 'Manifestation':
            self._baseHealth += 10
            self._baseDamage -= 1
            self._baseSpeed -= 0.05
            self.lostPercent = 0.05
            self.lostHitChance = 0.8
            self._ascendancy = 'Manifestation'
            self.ascendancyDescription = WANDERER_DESCRIPTIONS['Manifestation']
        elif ascendancy == 'Weaver':
            self._baseHealth += 15
            self._baseDamage -= 4
            self._stats['baseCritMulti'] += 0.2
            self._stats['Permanent']['psychic'] += 10
            self._ascendancy = 'Weaver'
            self.ascendancyDescription = WANDERER_DESCRIPTIONS["Weaver"]
        elif ascendancy == 'Abyssal':
            self._baseHealth += 30
            self._baseDamage -= 4
            self._baseSpeed += 0.1
            self.lostTrigger = True
            self._stats['baseCritChance'] -= 0.03
            self._stats['baseCritMulti'] -= 0.1
            self._stats['Permanent']['all'] += 5
            self._ascendancy = 'Abyssal'
            self.ascendancyDescription = WANDERER_DESCRIPTIONS["Abyssal"]
        elif ascendancy == 'Warper':
            self._baseHealth += 10
            self._baseDamage += 2
            self._baseSpeed -= 0.1
            self.lostTrigger = 0.2
            self._stats['baseCritMulti'] += 0.25
            self._ascendancy = 'Warper'
            self.ascendancyDescription = WANDERER_DESCRIPTIONS["Warper"]
        elif ascendancy == 'Mindbreaker':
            self._baseHealth -= 10
            self._baseDamage += 2
            self._baseSpeed -= 0.1
            self._stats['baseCritChance'] += 0.03
            self._stats['Permanent']['psychic'] += 10
            self._ascendancy = 'Mindbreaker'
            self.ascendancyDescription = WANDERER_DESCRIPTIONS['Mindbreaker']
        self._recalculateStats()
