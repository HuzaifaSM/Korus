from .base import Player, Entity
from scripts.styles import console
from scripts.abilities import StatusEffect, Effects
from copy import deepcopy
from typing import List
import random

MUTANT_DESCRIPTIONS = {
    "Mutant": "A freak of nature.\n"
        "Any damage over time ailments inflicted on you are reflected onto your attacker. 20% Increased Damage Taken.\n"
        "Starting Stats: 60 HP | 4 Damage | 6% Crit Chance | 130% Crit Damage | Chaos Damage | 1.05 Speed.",
    #ascendancies
    "Plaguebearer": "All Enemies take 20% Increased Damage from Damage over Time Ailments.\n"
        "Gain 2% Increased Damage per DoT reflected in combat to a maximum of 100%.\n"
        "When reflecting or applying DoT ailments, apply two stacks of that ailment to all enemies.\n"
        "+15 HP. -1 Damage. -0.05 Speed.",
    "Catalyst": "Damage over Time ailments are instead reflected with a duration of 1 turn, and deal 60% of the damage they would have dealt normally.\n"
        "When an enemy dies to a DoT, all enemies take Chaos Damage equal to 15% of the killed enemy's Max HP.\n"
        "Take 25% Increased Damage instead of 20% Increased. You only reflect DoTs 50% of the time.\n"
        "-15HP. +2 Damage. +0.1 Speed.",
    "Parasite": "Whenever an enemy takes damage from Damage over Time ailments, heal for 20% of the damage they take.\n"
        "Upon killing an enemy, gain Parasitic: +15% Lifesteal, +10 Damage, 5% Increased Damage for 2 turns.\n"
        "Take 25% Increased Damage instead of 20% Increased.\n"
        "-20 HP. +4 Damage. +0.05 Speed. +2.5% Crit Chance.",
    "Aberration": "Take 30% Increased Damage instead of 20% Increased. When hitting a target, apply a random Damage over Time ailment out of Bleed, Burn, and Poison.\n"
        "Upon reflecting Damage over Time ailments, gain +1% All Resistance and +1% Damage Reduction, both to a maximum of 15%.\n"
        "Upon successful duplication, restore either 100 Energy Shield or 10% of your Maximum Energy Shield, whichever is higher.\n"
        "-10 HP. +2 Damage. -0.1 Speed. +80 Energy Shield. +100 Armour. -300 Evasion",
    "Voidborn": "Consume Damage over Time ailments instead of reflecting them.\n"
        "Upon consuming DoTs, deal 50 Chaos Damage to all enemies and heal 1% of your Max HP.\n"
        "Gain one stack of Hunger for the rest of combat on consuming a DoT. Hunger: +4 Damage. +0.5% Lifesteal. Max 50 Hunger Stacks.\n"
        "-15 HP. +2 Damage. +0.05 Speed. +10% Chaos Resistance.",
    "Symbiote": "No longer take 20% Increased Damage. All Damage over Time ailments deal 50% less damage.\n"
        "Instead of reflecting DoTs, they are applied to both you and the attacker. At the start of your turn, all combatants with DoT ailments lose 1% max HP per ailment affecting them.\n"
        "Upon landing a critical hit, cleanse up to 3 DoTs from yourself.\n"
        "Upon killing an enemy, heal 3% Max HP per DoT affecting them. This healing can exceed your Max Health by up to 50%.\n"
        "+20 HP. -1 Damage. -0.2 Speed. +5% Crit Chance. +25% Crit Damage. +10% Chaos Resistance. +10% DoT Resistance.",
    #subtypes
    "Inverter": "No longer reflect Damage over Time ailments. No longer take 20% Increased Damage.\n"
        "Instead, deal 20% Increased Damage. All DoT ailments you apply are applied to you and your target.\n"
        "Gain +3% Elemental Resistance and 1% Increased Damage Dealt per 4 DoTs affecting you.\n"
        "-10 HP. +3 Damage. -0.05 Speed. +10% DoT Resistance.",
    "Regenerator": "No longer take 20% Increased Damage. Upon reflecting Damage over Time ailments, heal for 10% damage taken from the hit that applied the ailment. Once per hit.\n"
        "At the start of your turn, regenerate 0.2% Max HP per DoT affecting all enemies.\n"
        "-5 HP. +1 Damage. -0.1 Speed. +5% Physical Resistance.",
    "Irradiated": "Upon reflecting Damage over Time ailments, 20% chance to duplicate the reflected ailment with the highest tick damage.\n"
        "Upon successful duplication, the duplicated DoT is applied to all combatants. When a DoT is applied to you this way, gain 3% Increased Damage for the rest of combat.\n"
        "-10 HP. +1 Damage. +0.05 Speed. +5% Chaos Resistance."
}

class Mutant(Player):
    def __init__(self, name, health = 60, damage = 4, damageType = "chaos", speed = 1.05):
        super().__init__(name, health, damage, 0.06, 1.3, damageType, speed,
                         className="Mutant", classDescription=MUTANT_DESCRIPTIONS['Mutant'])
        self.damageTakenModifier = 1.2
        self.reflectChance = 1.0
        self.dotMultiplier = 1.0
        self.dotsReflected = 0

        self.parasiticTurns = 0
        self.aberrationAllRes = 0
        self.aberrationDR = 0
        self.hungerStacks = 0

        self.inverterDamage = 0
        self.irradiationDamage = 0

    def reflectDoTs(self, enemy: Entity, dot: StatusEffect, combatManager=None, enemies: List[Entity]=[]):
        if combatManager and enemy:
            dot.data['damage'] = int(dot.data['damage'] * self.dotMultiplier)

            if self._ascendancy == 'Catalyst':
                damage = int(dot.turns * dot.data['damage'] * 0.6)
                dot.turns = 1
                dot.data['damage'] = damage

            if random.random() < self.reflectChance:

                if self._ascendancy == 'Plaguebearer':
                    for e in enemies:
                        for _ in range(2):
                            combatManager.addStatusEffect(e, dot, self)

                else:
                    combatManager.addStatusEffect(enemy, dot, self)

            self.dotsReflected += 1

    def onAttack(self, damageDealt, damageType, target=None, combatManager=None):
        super().onAttack(damageDealt, damageType, target, combatManager)

        if self._ascendancy == 'Plaguebearer':
            bonus = 1 + (min(50, self.dotsReflected) * 0.02)
            damageDealt = int(damageDealt * bonus)

        return damageDealt, damageType

    def onHit(self, damageTaken, damageType):
        super().onHit(damageTaken, damageType)
        damageTaken = round(damageTaken * self.damageTakenModifier)

    def updateAscendancy(self, ascendancy):
        if ascendancy == 'Plaguebearer':
            self._baseHealth += 15
            self._baseDamage -= 1
            self._baseSpeed -= 0.05
            self.dotMultiplier += 0.2
            self._ascendancy = 'Plaguebearer'
            self.ascendancyDescription = MUTANT_DESCRIPTIONS["Plaguebearer"]
        elif ascendancy == 'Catalyst':
            




