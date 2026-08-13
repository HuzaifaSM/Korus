from .base import Player
from scripts.styles import console, formatDamageType
import random

MONK_DESCRIPTIONS = {
    "Monk": "[class_monk]An enlightened martial artist.[/class_monk]\n"
        "In combat, if your damage type is [lightning]Lightning[/lightning] or [cold]Cold[/cold], switch to the other at the beginning of your turn.\n"
        "[resource]Prowess[/resource]: When dealing [lightning]Lightning[/lightning] or [cold]Cold[/cold] damage, Gain 1 [resource]Prowess[/resource] per 12 damage dealt. [resource]Prowess[/resource] buffs: +2 Damage, +0.03 Speed. [resource]Prowess[/resource] has no limit.\n"
        "Starting Stats: 55 [health]HP[/health] | 3 [damage]Damage[/damage] | 10% [critical]Crit Chance[/critical] | 130% [critical]Crit Damage[/critical] | [lightning]Lightning Damage[/lightning] | 1.05 [speed]Speed[/speed].",
    #ascendancies
    "Enlightened": "25% Increased Cold and Lightning Damage Dealt. At the start of combat, your damage type switches to the first type you use.\n"
        "If the first damage type was lightning or cold, 100% more Prowess generation for the rest of combat.\n"
        "Upon attacking with a damage type that differs to your own, deal 130% of your base damage as damage of your damage type to all enemies.\n"
        "+10 HP. +2 Damage. -0.1 Speed. +5% Crit Chance.",
    "Stormwalker": "You no longer switch elements from lightning to cold. 40% Increased Lightning damage.\n"
        "Lightning attacks hit 2 additional random targets for 60% damage. Lightning damage has a 40% chance to apply Shock.\n"
        "Shocked enemies you hit grant +1 Prowess and spread Shock to 1 random enemy.\n"
        "-5 HP. +1 Damage. +0.15 Speed. +20% Lightning Resistance. +3% Crit Chance.",
    "Glacierfist": "You no longer switch elements from cold to lightning. 40% Increased Cold damage.\n"
        "All enemies permanently have 20% Less Speed. All sources of Cold damage you deal have a 25% chance to apply Chilled or a 20% chance to apply Freeze to their target.\n"
        "Attacking frozen enemies increases your prowess by 10% and heals you for 5% of damage dealt.\n"
        "+15 HP. +2 Damage. -0.1 Speed. +20% Cold Resistance. +20% Crit Damage.",
    "Ascetic": "Prowess has 100% increased effect on you. 10% Damage Reduction.\n"
        "On crit, heal 1% Max HP per 60 damage dealt. Upon taking Psychic Damage, Prowess is halved.\n"
        "+10 HP. -1 Damage. +0.05 Speed. +5% Crit Chance.",
    "Psychopath": "Prowess has no effect on you. Prowess is replaced by Apathy. Apathy has a maximum of 20 stacks.\n"
        "Upon Critical Strike, gain 1 Apathy. Apathy: +10 Damage, +0.1 Speed, +15% Crit Damage.\n"
        "-15 HP. +3 Damage. -0.05 Speed. +5% Crit Chance. +25% Crit Damage. -10% Lightning Resistance. -10% Cold Resistance.",
    "Avatar": "You no longer switch damage type at the start of your turn. 100% increased Prowess effect.\n"
        "Upon hitting an enemy, your damage type will immediately switch to the damage type the target has the least resistance to.\n"
        "Upon killing an enemy, gain Resistance Penetration and damage equal to 10% of their total resistances for the rest of combat.\n"
        "-15 HP. +2 Damage. +0.05 Speed. +10% Divine Resistance.",
}

ELEMENTAL = ['fire', 'cold', 'lightning', 'wind', 'earth']

class Monk(Player): # higher speed, higher health, lower damage, lightning + cold damage
    def __init__(self, name, health = 55, damage = 3, damageType = "lightning", speed = 1.05):
        super().__init__(name, health, damage, 0.1, 1.3, damageType, speed, className="Monk", classDescription=MONK_DESCRIPTIONS['Monk'])
        self.prowess = 0
        self.prowessEffect = 1
        self.enlightenedElement = None
        self.enlightenedProwessGen = 1.0
        self.apathy = 0
        self.avatarGain = 0
        self.lastDamageType = None

    def deserialise(self, data):
        super().deserialise(data)
        if hasattr(self, '_rage'):
            delattr(self, '_rage')
        if hasattr(self, '_maxRage'):
            delattr(self, '_maxRage')
        if hasattr(self, '_mana'):
            delattr(self, '_mana')
        if hasattr(self, '_maxMana'):
            delattr(self, '_maxMana')
        if hasattr(self, '_maxThorns'):
            delattr(self, '_maxThorns')
        if hasattr(self, '_form'):
            delattr(self, '_form')

    def onAttack(self, damageDealt, damageType, target=None, combatManager=None):
        super().onAttack(damageDealt, damageType, target, combatManager)
        if self.enlightenedElement is None:
            self.enlightenedElement = damageType
            if self._ascendancy == 'Enlightened' and damageType in ['cold', 'lightning']:
                self.enlightenedProwessGen = 2.0
                console.print('\n[gold]Enlightened: 100% more Prowess generation for the rest of combat![/gold]')

        if self._ascendancy == 'Glacierfist':
            gainExtra = any(e.name == 'freeze' for e in target.statusEffects)
            if gainExtra:
                bonusProwess = int(self.prowess * 0.1)
                self.prowess += bonusProwess
                heal = int(damageDealt * 0.05)
                self.heal(heal)
                console.print(f"  [buff]Glacierfist: +{bonusProwess} prowess, healed {heal} HP![/buff]")

        if self._ascendancy == 'Avatar':
            lowestResType = None
            lowestResValue = float('inf')
            
            damageTypes = ['physical', 'fire', 'cold', 'lightning', 'wind', 'earth', 'dark', 'holy', 'arcane', 'ethereal', 'psychic', 'chaos']
            for dType in damageTypes:
                resistance = target._stats['Resistances'].get(dType, 0)
                if resistance < lowestResValue:
                    lowestResValue = resistance
                    lowestResType = dType

            if lowestResType and lowestResType != self._damageType:
                oldType = self._damageType
                self._damageType = lowestResType
                console.print(f'[gold1]Avatar: Damage type switched from {formatDamageType(oldType, oldType)} to {formatDamageType(lowestResType, lowestResType)}[/gold1]')
                damageType = lowestResType

        if damageType in ['lightning', 'cold']:
            prowess = max(0, damageDealt // 12)
            if self._ascendancy == 'Enlightened':
                prowess = int(prowess * self.enlightenedProwessGen)

            if self._ascendancy != 'Psychopath':
                self.prowess += prowess
                damageDealt += int(prowess * self.prowessEffect)
                self._stats['Temporary']['speed'] += 0.03 * self.prowessEffect

            self._recalculateStats(False)
            if prowess > 0 and self._ascendancy != 'Psychopath':
                console.print(f"\n[buff]Your Prowess grows! +{self.prowess*2} Damage, +{round(self.prowess / 100 * 3, 2)} Speed for the rest of combat.[/buff]")
            if self._ascendancy == 'Psychopath' and self.apathy > 0:
                console.print(f"\n[dark_red]You currently have {self.apathy} Apathy. +{self.apathy * 10} Damage, +{self.apathy * 0.1:.2f} Speed, +{self.apathy * 10}% Crit Damage.[/dark_red]")

            if self._ascendancy == 'Enlightened':
                damageDealt = int(damageDealt * 1.15)
            elif self._ascendancy == 'Stormwalker' and damageType == 'lightning':
                damageDealt = int(damageDealt * 1.2)
            elif self._ascendancy == 'Glacierfist' and damageType == 'cold':
                damageDealt = int(damageDealt * 1.2)

        return damageDealt, damageType

    def onHit(self, damageTaken, damageType, crit=False, attacker=None, combatManager=None):
        super().onHit(damageTaken, damageType, crit, attacker, combatManager)
        if self._ascendancy == 'Ascetic':
            damageTaken = int(damageTaken * 0.9)
            if damageType == 'psychic':
                self.prowess //= 2

        if damageType in ['lightning', 'cold'] and self._damageType in ['lightning', 'cold'] \
            and not self._ascendancy == 'Enlightened':
            if damageType == 'lightning':
                self._damageType = 'lightning'
            elif self._damageType == 'cold':
                self._damageType = 'cold'
            console.print(f"\n[info]Your elemental affinity changes your damage type to {formatDamageType(self._damageType, self._damageType)}[/info]")

        return damageTaken, damageType

    def rollCritical(self, target, damageDealt=None):
        crit, multi = super().rollCritical(target, damageDealt)

        if self._ascendancy == 'Ascetic' and crit:
            heal = int((self._maxHealth * 0.01) * (damageDealt // 60))
            self.heal(heal)

        elif self._ascendancy == 'Psychopath' and crit:
            if self.apathy < 20:
                self.apathy += 1
                self._stats['Temporary']['speed'] += 0.1
                self._stats['Temporary']['critMulti'] += 0.15
                console.print(f'  [dark_red]- Psychopath: Gained 1 Apathy! Total: {self.apathy}/15[/dark_red]')

        return crit, multi

    def onKill(self, entity, attackData, combatManager=None):
        if self._ascendancy == 'Avatar':
            totalRes = sum(entity._stats['Resistances'].values())
            bonus = int(totalRes * 0.1)
            if bonus > 0:
                self.avatarGain += bonus
                self._stats['Temporary']['resistancePenetration'] += bonus
                console.print(f"  [gold1]Avatar: Absorbed enemy defenses! +{bonus} damage and penetration![/gold1]")

        return None

    def onTurnStart(self):
        if self._ascendancy in ['Enlightened', 'Stormwalker', 'Glacierfist', 'Avatar']:
            return
        if self._damageType in ['lightning', 'cold']:
            if self._damageType == 'lightning':
                self._damageType = 'cold'
            elif self._damageType == 'cold':
                self._damageType = 'lightning'
            console.print(f"\n[info]Your element shifts! Your damage type has switched to {formatDamageType(self._damageType, self._damageType)}[/info]")
        super().onTurnStart()

    def onBattleEnd(self):
        if self._ascendancy != 'Psychopath' and self.prowess > 0:
            self._baseDamage -= self.prowess * self.prowessEffect
            self._baseSpeed -= (self.prowess / 100) * self.prowessEffect
            self.prowess = 0

        if self._ascendancy == 'Psychopath' and self.apathy > 0:
            self.apathy = 0

        self.enlightenedElement = None
        self.enlightenedProwessGen = 1.0

        super().onBattleEnd()
