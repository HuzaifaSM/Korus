from .base import Player
from scripts.styles import console, pause, printHeader, clearScreen
from typing import Dict
import random

DRUID_DESCRIPTIONS = {
    "Druid": "A nature mystic who channels the primal forces.\n"
        "Shapeshifting: Deal Earth damage to swap forms. Your forms grow in power with each level.\n"
        "Per Level Buffs: Human: +1 Damage, +1% Elemental Resistance, +0.01 Speed | Beast: +1.5% Crit Damage, +2% Increased Earth Damage, -0.02 Speed, +0.4% Damage Taken.\n"
        "Gain 1 stack of Verdance per 10 damage dealt, to a max of 30 stacks. Verdance: 0.5% Damage Reduction, 1% Increased Earth Damage. Heal 1% Max HP per Verdance at the end of combat.\n"
        "Starting Stats: 55 HP | 5 Damage | 7.5% Crit Chance | 150% Crit Damage | Earth Damage | 1 Speed.",
    #ascendancy
    "Primalist": "Form bonuses have 50% Increased Magnitude. Human Form gains 0.25% Damage Reduction per level. Beast Form gains +1 Damage per level.\n"
        "Upon shapeshifting, gain Residual for 2 turns from your previous form. Human Residual: +30% Crit Damage, +20% Increased Earth Damage. Beast Residual: +15% Elemental Resistance, +5% Lifesteal.\n"
        "When in Human Form, -15% Damage over Time Resistance. When in Beast Form, -20% Stun Avoidance.\n"
        "+10 HP. +1 Damage. -0.05 Speed. +10% Earth Resistance.",
    "Arbiter": "At the start of combat, choose your starting form. You cannot shapeshift unless you kill an enemy.\n"
        "Upon killing an enemy, you may choose to shapeshift. If you do, gain Adaptation for 3 turns based on your new form.\n"
        "Human Adaptation: +15% Damage Reduction, +50% Healing Magnitude. Beast Adaptation: +20% Increased Damage, +10% Crit Chance.\n"
        "Verdance generation increased by 50%.\n"
        "+15 HP. +1 Damage. -0.1 Speed. +10% Physical Resistance.\n",
    "Moonkin": "Gain a new form, Moonkin Form. You are permanently in Moonkin form and cannot shapeshift.\n"
        "Moonkin Form per level: +1 Damage, +0.02 Speed, +0.5% Crit Chance, +2% Crit Damage.\n"
        "Verdance no longer increases Earth Damage. Verdance grants 1.5% Damage Reduction per stack. -10 to Max Verdance.\n"
        "Whilst at or above 15 Verdance, gain Lunar Empowerment: 20% Increased Damage, +5% Crit Chance, +25% Crit Damage, +10% Lifesteal.\n"
        "The first time you drop below 25% Max HP each combat, gain Lunar Fury for 3 turns: 30% Increased Damage, +0.3 Speed.\n"
        "+10 HP. -2 Damage. -0.1 Speed. +15% Arcane Resistance. +10% Stun Avoidance.",
    "Chimera": "+10 to Max Verdance. Whilst at or above 25 Verdance, you are in Chimera Form and are unable to shapeshift.\n"
        "Chimera Form per level: +1 Damage, +0.01 Speed, +1% Crit Damage, +1% Increased Earth Damage.\n"
        "While in Chimera Form, Verdance buffs have 100% Increased Effect.\n"
        "-10 HP. +1 Damage. -0.05 Speed. +10% Elemental Resistance.",
    "Earthshaper": "+20 to Max Verdance. Verdance instead grants +2% Increased Earth Damage and +2% Increased Armour per stack.\n"
        "Earth Damage you deal has a 25% to apply Earthbound for 2 turns: -0.2 Speed, -10% Damage Dealt.\n"
        "Whilst at or above 30 Verdance, regenerate 5% of your Energy Shield at the start of your turn.\n"
        "Form bonuses have 50% less Magnitude.\n"
        "-10 HP. +2 Damage. -0.15 Speed. +25% Earth Resistance. +10% Stun Avoidance. +50 Armour. +25 Energy Shield.",
}

class Druid(Player): # balanced damage and speed, earth damage
    def __init__(self, name, health = 55, damage = 5, damageType = "earth", speed = 1.0):
        super().__init__(name, health, damage, 0.075, 1.5, damageType, speed, className = "Druid", classDescription=DRUID_DESCRIPTIONS['Druid'])
        self.verdance = 0
        self.maxVerdance = 30
        self.verdanceEffect = 1
        self.form = 'human'
        self.formBonuses = {
            'damage': 0,
            'speed': 0,
            'critMulti': 0,
            'earthDamage': 0,
            'elemental': 0,
            'damageTaken': 0
        }
        self.humanPerLevel = {
            'damage': 1,
            'elemental': 1,
            'speed': 0.01
        }
        self.beastPerLevel = {
            'critMulti': 0.015,
            'earthDamage': 2,
            'speed': -0.02,
            'damageTaken': 0.4
        }
        self.moonkinPerLevel = {
            'damage': 1,
            'speed': 0.02,
            'critChance': 0.005,
            'critMulti': 0.02
        }
        self.chimeraPerLevel = {
            'damage': 1,
            'speed': 0.01,
            'critMulti': 0.01,
            'earthDamage': 1
        }
        self.formEffect = 1
        self.residualTurns = 0
        self.residualType = None
        self.arbiterFormChosen = False
        self.adaptationTurns = 0
        self.adaptationType = None
        self.lunarEmpowered = False
        self.lunarFuryTurns = 0
        self.lunarFuryTriggered = False
        self.chimeraActive = False

    def __str__(self):
        formDisplay = "[green]Human[/green]" if self.form == 'human' else "[yellow]Beast[/yellow]"
        return f"{super().__str__()}\n[earth]Verdance:[/earth] {self.verdance}/{self.maxVerdance} | Form: {formDisplay}"

    def _serialise(self):
        temp = super()._serialise()
        temp['verdance'] = self.verdance
        temp['maxVerdance'] = self.maxVerdance
        temp['form'] = self.form
        return temp

    def deserialise(self, data):
        super().deserialise(data)
        self.verdance = data.get('verdance', 0)
        self.maxVerdance = data.get('maxVerdance', 30)
        self.form = data.get('form', 'human')

    def _applyFormBonuses(self):
        self._stats['Temporary']['speed'] -= self.formBonuses['speed']
        for k, v in self.formBonuses.items():
            if k in self._stats['Temporary']:
                self._stats['Temporary'][k] -= v
            self.formBonuses[k] = 0

        if self.form == 'human':
            self.formBonuses['damage'] = self.humanPerLevel['damage'] * self._level
            self.formBonuses['elemental'] = self.humanPerLevel['elemental'] * self._level
            self.formBonuses['speed'] = self.humanPerLevel['speed'] * self._level
            
            if self._ascendancy == 'Primalist':
                self.formBonuses['damageReduction'] = 0.25 * self._level
                self._stats['Temporary']['dotResistance'] -= 15

        elif self.form == 'beast':
            self.formBonuses['critMulti'] = self.beastPerLevel['critMulti'] * self._level
            self.formBonuses['earthDamage'] = self.beastPerLevel['earthDamage'] * self._level
            self.formBonuses['speed'] = self.beastPerLevel['speed'] * self._level
            self.formBonuses['damageTaken'] = self.beastPerLevel['damageTaken'] * self._level

            if self._ascendancy == 'Primalist':
                self.formBonuses['damage'] = self._level
                self._stats['Temporary']['stunAvoidance'] -= 20

        elif self.form == 'moonkin':
            self.formBonuses['damage'] = self.moonkinPerLevel['damage'] * self._level
            self.formBonuses['speed'] = self.moonkinPerLevel['speed'] * self._level
            self.formBonuses['critChance'] = self.moonkinPerLevel['critChance'] * self._level
            self.formBonuses['critMulti'] = self.moonkinPerLevel['critMulti'] * self._level

        elif self.form == 'chimera':
            self.formBonuses['damage'] = self.chimeraPerLevel['damage'] * self._level
            self.formBonuses['speed'] = self.chimeraPerLevel['speed'] * self._level
            self.formBonuses['critMulti'] = self.chimeraPerLevel['critMulti'] * self._level
            self.formBonuses['earthDamage'] = self.chimeraPerLevel['earthDamage'] * self._level

        for k, v in self.formBonuses.items():
            self.formBonuses[k] = int(v * self.formEffect)

        for k, v in self.formBonuses.items():
            if k in self._stats['Temporary']:
                self._stats['Temporary'][k] += v

    def _shapeShift(self, *, form: str = None):
        oldForm = self.form

        if self._ascendancy == 'Primalist':
            self.residualType = oldForm
            if oldForm == 'human':
                self._stats['Temporary']['dotResistance'] += 15
                console.print("  [green]Gained Human Residual: +30% Crit Multi, +20% Earth Damage[/green]")
                if self.residualTurns == 0:
                    self._stats['Temporary']['critMulti'] += 0.3
                else:
                    self._stats['Temporary']['elemental'] -= 15
                    self._stats['Temporary']['lifesteal'] -= 5
            else:
                self._stats['Temporary']['stunAvoidance'] += 20
                console.print("  [yellow]Gained Beast Residual: +15% Elemental Res, +5% Lifesteal[/yellow]")
                if self.residualTurns == 0:
                    self._stats['Temporary']['elemental'] += 15
                    self._stats['Temporary']['lifesteal'] += 5
                else:
                    self._stats['Temporary']['critMulti'] -= 0.3
            self.residualTurns = 2

        if form is not None:
            self.form = form
        else:
            if self.form == 'human':
                self.form = 'beast'
            elif self.form == 'beast':
                self.form = 'human'

        self._applyFormBonuses()
        self._recalculateStats(False)

        if self.form == 'human':
            console.print(f"  [green]+{self.formBonuses['damage']} Damage, +{self.formBonuses['elemental']*100:.1f}% Elemental Res, +{self.formBonuses['speed']:.2f} Speed[/green]")
        elif self.form == 'beast':
            console.print(f"  [yellow]+{self.formBonuses['critMulti']*100:.1f}% Crit Damage, +{self.formBonuses['earthDamage']*100:.0f}% Earth Damage, {self.formBonuses['speed']:.2f} Speed, +{self.formBonuses['damageTaken']*100:.1f}% Damage Taken[/yellow]")
        elif self.form == 'moonkin':
            console.print(f"  [cyan]+{self.formBonuses['damage']} Damage, +{self.formBonuses['speed']} Speed, +{self.formBonuses['critChance']}% Crit Chance, +{self.formBonuses['critMulti']*100:.1f}% Crit Damage.[/cyan]")

    def onTurnEnd(self, combatManager=None):
        if self._ascendancy == 'Primalist' and self.residualTurns > 0:
            self.residualTurns -= 1
            if self.residualTurns == 0:
                if self.residualType == 'human':
                    self._stats['Temporary']['critMulti'] -= 0.3
                else:
                    self._stats['Temporary']['elemental'] -= 15
                    self._stats['Temporary']['lifesteal'] -= 5

        elif self._ascendancy == 'Arbiter' and self.adaptationTurns > 0:
                self.adaptationTurns -= 1
                if self.adaptationTurns == 0:
                    if self.adaptationType == 'human':
                        self._stats['Temporary']['healingMagnitude'] -= 50
                        self._stats['Temporary']['critChance'] += 0.1
                    elif self.adaptationType == 'beast':
                        self._stats['Temporary']['critChance'] -= 0.1
                        self._stats['Temporary']['healingMagnitude'] -= 50
                    console.print("[earth]Arbiter: Adaptation has faded.[/earth]")

        elif self._ascendancy == 'Moonkin' and self.lunarFuryTurns > 0:
            self.lunarFuryTurns -= 1
            if self.lunarFuryTurns == 0:
                self._stats['Temporary']['speed'] -= 0.3
                console.print("[earth]Moonkin: Lunar Fury has ended.[/earth]")

    def _chooseArbiterForm(self) -> bool:
        if self._ascendancy == 'Arbiter':
            switch = False
            current = self.form
            while True:
                clearScreen()
                printHeader()
                console.print("[earth]Arbiter: Choose your form:[/earth]\n  [dim]1.[/dim] Human\n  [dim]2.[/dim] Beast")
                choice = console.input("[cyan]> [/cyan]").strip()
                try:
                    form = int(choice)
                    if form in [1, 2]:
                        if form == 1:
                            self._shapeShift(form='human')
                        elif form == 2:
                            self._shapeShift(form='beast')
                        break
                except ValueError:
                    console.print("[warning]Invalid Input![/warning]")
            if current != self.form:
                switch = True
            return switch

    def onTurnStart(self, combatManager=None):
        if self._ascendancy == 'Arbiter' and not self.arbiterFormChosen:
            self._chooseArbiterForm()
        
        if self._ascendancy == 'Moonkin':
            self._shapeShift(form='moonkin')
            if self.verdance >= 15 and not self.lunarEmpowered:
                self.lunarEmpowered = True
                self._stats['Temporary']['critChance'] += 0.05
                self._stats['Temporary']['critMulti'] += 0.25
                self._stats['Temporary']['lifesteal'] += 10
            elif self.verdance < 15 and self.lunarEmpowered:
                self.lunarEmpowered = False
                self._stats['Temporary']['critChance'] -= 0.05
                self._stats['Temporary']['critMulti'] -= 0.25
                self._stats['Temporary']['lifesteal'] -= 10
        
        elif self._ascendancy == 'Chimera':
            if self.verdance >= 25 and not self.chimeraActive:
                self.chimeraActive = True
                self._shapeShift(form='chimera')
                self.verdanceEffect = 2
                console.print("[earth]Chimera: Transformed into Chimera form.[/earth]")
            elif self.verdance < 25 and self.chimeraActive:
                self.chimeraActive = False
                self._shapeShift(form='human')
                self.verdanceEffect = 1
                console.print("[warning]Chimera: Chimera Form has faded![/warning]")

        elif self._ascendancy == 'Earthshaper':
            if self.verdance >= 30 and self.maxEnergyShield > 0:
                esGain = int(self.maxEnergyShield * 0.05)
                self._stats['energyShield'] = min(self.maxEnergyShield, self.energyShield + esGain)
                console.print(f"[earth]Earthshaper: Regenerated 5% of Energy Shield! +{esGain} Energy Shield. Current Shield: {self.maxEnergyShield} / {self.energyShield}[/earth]")

        super().onTurnStart(combatManager)

    def onAttack(self, damageDealt, damageType, target=None, combatManager=None):
        super().onAttack(damageDealt, damageType, target, combatManager)

        verdanceGained = damageDealt // 10
        if self._ascendancy == 'Arbiter':
            verdanceGained = int(verdanceGained * 1.5)
        realGain = min(verdanceGained, self.maxVerdance - self.verdance)
        self.verdance = min(self.maxVerdance, self.verdance + verdanceGained)
        console.print(f"[earth]Gained {realGain} Verdance. Current: {self.verdance}/{self.maxVerdance}[/earth]")

        if self._ascendancy == 'Earthshaper' and realGain > 0:
            self._stats['Temporary']['increased_armour'] += 2 * realGain

        if (damageType == 'earth' and
            self._ascendancy not in ['Arbiter', 'Moonkin'] and
            not self.chimeraActive):
            self._shapeShift()

        if self.verdance > 0 and self._ascendancy != 'Moonkin':
            earthBonus = 1 + (0.01 * self.verdance * self.verdanceEffect)
            if damageType == 'earth':
                damageDealt = int(damageDealt * earthBonus)
        
        if 'earthDamage' in self.formBonuses and self.formBonuses['earthDamage'] > 0 and damageType == 'earth':
            bonus = 1 + (0.01 * self.formBonuses['earthDamage'])
            damageDealt = int(damageDealt * bonus)
        if 'damage' in self.formBonuses and self.formBonuses['damage'] > 0:
            damageDealt += self.formBonuses['damage']

        if self._ascendancy == 'Arbiter' and self.form == 'beast' and self.adaptationTurns > 0:
            damageDealt = int(damageDealt * 1.2)

        elif self._ascendancy == 'Moonkin':
            if self.lunarEmpowered:
                damageDealt = int(damageDealt * 1.2)
            if self.lunarFuryTurns > 0:
                damageDealt = int(damageDealt * 1.3)

        elif self._ascendancy == 'Earthshaper' and target and damageType == 'earth':
            if random.random() < 0.25:
                target.entity.earthboundTurns = 2

        return damageDealt, damageType
    
    def onHit(self, damageTaken, damageType, attacker = None, combatManager=None):
        if self._ascendancy == 'Arbiter' and self.form == 'human' and self.adaptationTurns > 0:
            damageTaken = int(damageTaken * 0.85)

        if self._ascendancy == 'Moonkin' and (self._health - damageTaken < self._maxHealth * 0.25) and not self.lunarFuryTriggered:
            self.lunarFuryTriggered = True
            self.lunarFuryTurns = 3
            self._stats['Temporary']['speed'] += 0.3

        dr = 0
        if self.verdance > 0:
            if self._ascendancy == 'Earthshaper' and attacker:
                if attacker.earthboundTurns > 0:
                    dr += 0.1
            
            elif self._ascendancy == 'Moonkin':
                dr += 0.015 * self.verdance * self.verdanceEffect
            
            else:
                dr += 0.005 * self.verdance * self.verdanceEffect
            damageTaken = int(damageTaken * (1 - dr))

        return super().onHit(damageTaken, damageType, attacker, combatManager)
    
    def onKill(self, entity, attackData, combatManager=None):
        if self._ascendancy == 'Arbiter':
            old = self.form
            switch = self._chooseArbiterForm()
            if switch and old != self.form:
                self.adaptationTurns = 3
                self.adaptationType = self.form
                if self.form == 'human':
                    if self.adaptationTurns != 0: #previously adapted, remove alternate effects
                        self._stats['Temporary']['healingMagnitude'] += 50
                        self._stats['Temporary']['critChance'] -= 0.1
                    self._stats['Temporary']['healingMagnitude'] += 50
                elif self.form == 'beast':
                    if self.adaptationTurns != 0:
                        self._stats['Temporary']['critChance'] += 0.1
                        self._stats['Temporary']['healingMagnitude'] -= 10
                    self._stats['Temporary']['critChance'] += 0.1

        return {}

    def onBattleEnd(self):
        heal = int(self._maxHealth * 0.01 * self.verdance)
        self.heal(heal)
        console.print(f"[earth]Healed {heal} HP from {self.verdance} Verdance.[/earth]")
        
        if self.form != 'human':
            self.form = 'human'
            self._applyFormBonuses()
            self._recalculateStats(False)

        self.verdance = 0

        super().onBattleEnd()

    def _levelUp(self):
        super()._levelUp()
        self._applyFormBonuses()
        self._recalculateStats(False)

    def updateAscendancy(self, ascendancy):
        if ascendancy == 'Primalist':
            self._baseHealth += 10
            self._baseDamage += 1
            self._baseSpeed -= 0.05
            self.formEffect = 1.5
            self._stats['Permanent']['earth'] += 10
            self._ascendancy = 'Primalist'
            self.ascendancyDescription = DRUID_DESCRIPTIONS["Primalist"]
        elif ascendancy == 'Arbiter':
            self._baseHealth += 15
            self._baseDamage += 1
            self._baseSpeed -= 0.1
            self._stats['Permanent']['physical'] += 10
            self._ascendancy = 'Arbiter'
            self.ascendancyDescription = DRUID_DESCRIPTIONS["Arbiter"]
        elif ascendancy == 'Moonkin':
            self._baseHealth += 10
            self._baseDamage -= 2
            self._baseSpeed -= 0.1
            self.maxVerdance -= 10
            self.form = 'moonkin'
            self._stats['Permanent']['arcane'] += 15
            self._stats['Permanent']['stunAvoidance'] += 10
            self._ascendancy = 'Moonkin'
            self.ascendancyDescription = DRUID_DESCRIPTIONS["Moonkin"]
        elif ascendancy == 'Chimera':
            self._baseHealth -= 10
            self._baseDamage += 1
            self._baseSpeed -= 0.05
            self.maxVerdance += 10
            self._stats['Permanent']['elemental'] += 10
            self._ascendancy = 'Chimera'
            self.ascendancyDescription = DRUID_DESCRIPTIONS["Chimera"]
        elif ascendancy == 'Earthshaper':
            self._baseHealth -= 10
            self._baseDamage += 2
            self._baseSpeed -= 0.15
            self.maxVerdance += 20
            self.formEffect = 0.5
            self._stats['Permanent']['earth'] += 25
            self._stats['Permanent']['stunAvoidance'] += 10
            self._stats['added_armour'] += 50
            self._stats['added_energy_shield'] += 25
            self._ascendancy = 'Earthshaper'
            self.ascendancyDescription = DRUID_DESCRIPTIONS["Earthshaper"]
