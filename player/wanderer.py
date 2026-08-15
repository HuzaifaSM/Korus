from .base import Player
from scripts.styles import console, pause
import random

WANDERER_DESCRIPTIONS = {
    "Wanderer": "[class_wanderer]A lost soul searching for peace.[/class_wanderer]\n"
        "[resource]Lost[/resource]: If a single hit deals more than 10% of your Max HP, your next attack will deal 50% More Damage and target all enemies.\n"
        "Starting Stats: 45 [health]HP[/health] | 6 [damage]Damage[/damage] | 10% [critical]Crit Chance[/critical] | 160% [critical]Crit Damage[/critical] | [psychic]Psychic Damage[/psychic] | 1.1 [speed]Speed[/speed].",
    #ascdenancies
    "Fractured": "Upon triggering Lost, gain Fracture, up to 5 stacks.\n"
        "Fracture: +5% Psychic Damage. +3% Crit Chance. At 5 Fracture, your next attack deals 150% Damage to all enemies, and Fracture is set to 0.\n"
        "Upon critically hitting an enemy, take Psychic damage equal to 2% of your Max HP.\n"
        "-10 HP. +1 Damage. +0.05 Speed. +3% Crit Chance. +20% Crit Damage.",
    "Manifestation": "Lost triggers upon taking more than 5% of your Max HP.\n"
        "Lost attacks have a 20% Chance to miss. Upon missing a Lost attack, apply Otherworld Exposure to all enemies.\n"
        "+10 HP. -1 Damage. -0.05 Speed.",
    "Weaver": "Non-psychic attacks deal 10% of Damage as Extra Psychic Damage.\n"
        "When Lost is triggered, apply Weaken and Exposed to all enemies and gain +10 Damage for the rest of combat.\n"
        "Upon killing an enemy, overkill damage is dealt evenly split to all living enemies.\n"
        "+15 HP. -4 Damage. +20% Crit Damage. +10% Psychic Resistance.",
    "Abyssal": "You are always Lost. Lost has no damage bonus. 10% Less Damage Dealt.\n"
        "Cumulative through combats, whenever you deal damage equal to 200% of your Max HP, gain +3% Psychic Damage permanently.\n"
        "+30 HP. -4 Damage. +0.1 Speed. -3% Crit Chance. -10% Crit Damage. +5% All Res.",
    "Warper": "Lost now triggers if a hit deals less than 5% of your Max HP or a hit deals more than 20% of your Max HP.\n"
        "Gain 'Warped' on triggering Lost. Warped grants +20% Lifesteal to your next attack and +10% Crit Chance.\n"
        "For every turn you are not Lost or Warped, take Psychic damage at the start of your turn equal to 2% of your Max HP.\n"
        "+10 HP. +2 Damage. -0.1 Speed. +25% Crit Damage.",
    "Mindbreaker": "All psychic damage permanently applies Torture on targets. Torture: +1% Damage Taken, -1% Damage Dealt.\n"
        "When Lost triggers, 1% Chance per Torture for damage dealt to each individual target to be doubled and apply Otherworld Exposure.\n"
        "Enemies lose all Torture upon critically hitting you.\n"
        "-10 HP. +2 Damage. -0.1 Speed. +3% Crit Chance. +10% Psychic Resistance.",
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

    def onAttack(self, damageDealt, damageType, target=None, combatManager=None):
        super().onAttack(damageDealt, damageType, target, combatManager)
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

    def onHit(self, damageTaken, damageType, crit=False, attacker=None, combatManager=None):
        super().onHit(damageTaken, damageType, crit, attacker, combatManager)
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

    def onBattleEnd(self):
        if self._ascendancy == 'Abyssal':
            if self.abyssalDamageDealt >= self.abyssalDamageThreshold:
                self.abyssalDamageDealt -= self.abyssalDamageThreshold
                self.abyssalPsychicBuff += 0.03
                console.print(f"  [buff]Abyssal: 200% of Max HP dealt as damage! +3% Psychic Damage permanently. +{int(self.abyssalPsychicBuff*100)}% Total Psychic Damage.[/buff]")

        self.lostTrigger = False
        self.wovenDamage = 0
        self.abyssalPsychicBuff = 0
        self.warped = False
        super().onBattleEnd()

    def updateAscendancy(self, ascendancy):
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
        self._recalculateStats(False)
