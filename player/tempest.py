from .base import Player
from scripts.styles import console
import random

TEMPEST_DESCRIPTIONS = {
    "Tempest": "[class_tempest]A flurry of energy, striking before its prey can react.[/class_tempest]\n"
        "If you have more Speed than an enemy, gain +0.25% Crit Chance and +1% Crit Damage per 0.01 Speed you have more than them.\n"
        "If you have less Speed than an enemy, gain +0.25 Damage and +1% Increased Damage per 0.01 Speed you have less than them.\n"
        "Abilities that damage multiple enemies will factor speed based off the first enemy only.\n"
        "When an enemy with less Speed than you attacks you, gain 1 Static. When an enemy with more Speed than you attacks you, gain 1 Flow. Gain twice as much Static and Flow when only 1 enemy is alive.\n"
        "Static: +2 Damage Reduction, -0.02 Speed. Max 10 Static stacks. Flow: +5% Increased Damage, +0.02 Speed. Max 10 Flow stacks.\n"
        "If you have 10 or more combined Static and Flow stacks, your next attack Unleashes: 100% Increased Lightning Damage, +5% Lifesteal, and evenly consumes a total of 10 Static and Flow stacks.\n"
        "At the end of combat, heal 1% Max HP for every critical hit you dealt, to a maximum heal of 30%.\n"
        "Starting Stats: 40 HP | 5 Damage | 8% Crit Chance | 140% Crit Damage | Lightning Damage | 1 Speed.",
    # ascendancies
    "Alternator": "At the start of your turn, the bonuses for speed differences are flipped.\n"
        "For each consecutive critical hit, gain 1 stack of Positive, to a maximum of 5. For each consecutive non-critical hit, gain 1 stack of Negative, to a maximum of 5.\n"
        "Positive: +2% Crit Chance, +20% Crit Damage, 4% Less Defences. Negative: +15% Increased Damage, +1% Lifesteal, 2% Increased Defences.\n"
        "Whenever you lose Positive, you next attack gains 40% Increased Lightning Damage. Whenever you lose Negative, your next attack gains +10% Lifesteal and +20 Damage.\n"
        "+20 HP. +6 Damage. +50% Crit Multi. +20% Lightning Resistance. -10% Earth Resistance.",
    "Dervish": "[evasion stacking ascendancy]"
}

"""
Ravager: bonuses from having more speed than the opponent are doubled. whenever you critically hit an opponent, gain +flat% chance to multihit. whenever you trigger a multihit attack, gain 1 [buff stack]: increased lightning damage, increased speed, reduced defenses. when you have 3 stacks of Flow, Unleash. Static can no longer be used to Unleash. Unleash now gives +75% crit damage, +10% lifesteal, +10% resistance penetration rather than the standard buffs. Static also grants +2% increased defenses per stack. - basically the 'assassination/one-shot/glass cannon' ascendancy

Archon: upon gaining static or flow, gain 1 Current, to a maximum of 10. Current grants +5% increased lightning damage, -2% earth resistance, +1% crit chance. bonuses from having less speed than the enemy are doubled. whenever you critically hit an enemy that has more speed than you, gain 1 Spark, up to a maximum of 5. Spark: +5% Crit Chance, +10% Crit Damage, -0.05 Speed. enemies that have more speed than you also grant 1 Flow when attacking you. enemies that have more speed than you remove 1 stack of Static from you when attacking you. whenever you Unleash, deal 10% of damage dealt to all enemies and consume up to 5 Current stacks and heal 2% max hp per stack consumed

Mirage: evasion/energy shield focused ascendancy: whenever you dodge an attack due to evasion, gain 10% of your energy shield as bonus damage on the next hit, and recover 10% of your maximum energy shield. if your energy shield is equal to more than half your evasion, lose 0.3 speed. if your evasion is more than 2.5x your energy shield, gain 0.3 speed. gain crit chance equal to 1% of your evasion, to a maximum of 25%. gain crit damage equal to 2% of your energy shield, equal to a maximum of 100%. 75% of armour converted to evasion, 5% of armour converted to energy shield. whilst you have no energy shield: +10% crit chance, +0.2 speed, 10% increased evasion. each stack of static grants +3% increased evasion. each stack of flow grants +2% maximum energy shield regeneration. whenever you evade an attack, gain 1 flow. whenever your energy shield fully absorbs an attack, gain 1 static.
"""

class Tempest(Player):
    def __init__(self, name, health=40, damage=5, damageType="lightning", speed=1):
        super().__init__(name, health, damage, 0.08, 1.4, damageType, speed, className="Tempest", classDescription=TEMPEST_DESCRIPTIONS["Tempest"])
        self.static = 0
        self.flow = 0
        self.staticFlowActivatedLastTurn = False
        self.critHits = 0

    def gainStatic(self):
        if self.static < 10:
            self.static += 1
            self._stats['Temporary']['speed'] -= 0.02
            self._stats['Temporary']['damage_reduction'] += 2

    def loseStatic(self):
        if self.static > 0:
            self.static -= 1
            self._stats['Temporary']['speed'] += 0.02
            self._stats['Temporary']['damage_reduction'] -= 2

    def gainFlow(self):
        if self.flow < 10:
            self.flow += 1
            self._stats['Temporary']['speed'] += 0.02

    def loseFlow(self):
        if self.flow > 0:
            self.flow -= 1
            self._stats['Temporary']['speed'] -= 0.02

    def onAttack(self, damageDealt, damageType, target=None, combatManager=None):
        damageDealt, damageType = super().onAttack(damageDealt, damageType)

        if self.static + self.flow >= 10:
            if damageType == 'lightning':
                damageDealt *= 2
            self._stats['Temporary']['lifesteal'] += 5
            self.staticFlowActivatedLastTurn = True
            removedStacks = 0
            while removedStacks < 10:
                if self.static > 0:
                    self.loseStatic()
                    removedStacks += 1
                if self.flow > 0:
                    self.loseFlow()
                    removedStacks += 1

        if target:
            targetEnemy = target.entity
            if targetEnemy._speed > self._speed: # more speed handled in combat manager due to crit changes
                difference = targetEnemy._speed - self._speed
                damageDealt = int((damageDealt + ((difference * 100) // 4)) * (1 + difference / 100))

        if self.flow > 0:
            damageDealt = int(damageDealt * (1 + (0.05 * self.flow)))

        return damageDealt, damageType

    def onTurnStart(self, combatManager=None):
        if self.staticFlowActivatedLastTurn:
            self._stats['Temporary']['lifesteal'] -= 5

        super().onTurnStart(combatManager)

    def onBattleEnd(self):
        critHeal = min(30, self.critHits) / 100
        heal = int(self._maxHealth * critHeal)
        self.heal(heal, False)
        console.print(f"[class_tempest]Tempest: You landed {self.critHits} critical hits this combat. Healed for {critHeal * 100:.0f}% Max HP ({heal})[/class_tempest]")

        super().onBattleEnd()

...