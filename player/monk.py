from .base import Player
from scripts.styles import console, formatDamageType
import random

MONK_DESCRIPTIONS = {
    "Monk": "An enlightened martial artist.\n"
        "In combat, if your damage type is Lightning or Cold, switch to the other at the beginning of your turn.\n"
        "Prowess: When dealing Lightning or Cold damage, Gain 1 Prowess per 12 damage dealt. Prowess buffs: +2 Damage, +0.03 Speed. Prowess has no limit.\n"
        "Starting Stats: 55 HP | 3 Damage | 10% Crit Chance | 130% Crit Damage | Lightning Damage | 1.05 Speed.",
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
    #subtypes
    "Pugilist": "Gain +20% Resistance to your current Elemental Damage type. On critical hit, apply Exposed to the target.\n"
        "Focus: Deal 12% More damage per consecutive hit on the same enemy, to a maximum of 120%.\n"
        "Enemies afflicted with any of the following grant +3 prowess when hit: Chill, Shock, Freeze, Elemental Exposure.\n"
        "-10 HP. +1 Damage. +0.05 Speed.",
    "Manafist": "No longer gain bonuses from prowess. Lightning Damage applies Chilled. Cold Damage applies Shocked.\n"
        "Conflux: Upon dealing Cold or Lightning damage, gain 15% Increased Elemental damage and +0.1 speed for 3 turns.\n"
        "Enemies afflicted by both Chill and Shock take 30% more damage from you and deal 15% less damage to you.\n"
        "+15 HP. +4 Damage. +0.05 Speed. +10% Arcane Resistance. +25% Crit Damage.",
    "Dualist": "50% Chance to gain an additional Prowess stack on being hit. 100% Chance if the damage taken was Lightning or Cold.\n"
        "Ending combat with Cold damage grants +1 Damage permanently. Ending combat with Lightning damage grants +0.01 Speed permanently.\n"
        "+10 HP. -1 Damage. -0.05 Speed. +10% Lifesteal.",
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

        self.focusTarget = None
        self.focusStacks = 0
        self.pugilistResType = None

        self.confluxTurns = 0

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

    def onAttack(self, damageDealt, damageType, target=None):
        super().onAttack(damageDealt, damageType)
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

            if self._subType == 'Manafist':
                if self.confluxTurns == 0:
                    self._stats['Temporary']['speed'] += 0.1
                self.confluxTurns = 3
                print(f'\n[gold]Conflux: +15% Increased Elemental damage, +0.1 speed for 3 turns![/gold]')

            if self._ascendancy != 'Psychopath' or self._subType != 'Manafist':
                self.prowess += prowess
                damageDealt += int(prowess * self.prowessEffect)
                self._stats['Temporary']['speed'] += 0.03 * self.prowessEffect

            self._recalculateStats(False)
            if prowess > 0 and self._ascendancy != 'Psychopath':
                console.print(f"\n[buff]Your Prowess grows! +{self.prowess*2} Damage, +{round(self.prowess / 100 * 3, 2)} Speed for the rest of combat.[/buff]")
            if self._ascendancy == 'Psychopath' and self.apathy > 0:
                console.print(f"\n[dark_red]You currently have {self.apathy} Apathy. +{self.apathy * 10} Damage, +{self.apathy * 0.1:.2f} Speed, +{self.apathy * 10}% Crit Damage.[/dark_red]")

            if self._subType == 'Pugilist':
                if target:
                    hasAilment = any(e.name in ['chill', 'shock', 'freeze', 'elemental_exposure'] for e in target.statusEffects)
                    if hasAilment:
                        bonusProwess = 3
                        self.prowess += bonusProwess
                        self._stats['Temporary']['speed'] += 0.03 * self.prowessEffect
                        console.print(f"  [buff]Pugilist: Hit afflicted enemy! +3 Prowess![/buff]")

                if target and self.focusTarget == target:
                    self.focusStacks = min(10, self.focusStacks + 1)
                    focusMult = 1 + (0.12 * self.focusStacks)
                    damageDealt = int(damageDealt * focusMult)
                    console.print(f"\n[buff]Focus: {self.focusStacks}/5 stacks on {target._name}. Dealing {int((focusMult - 1) * 100)}% more damage[/buff]")
                else:
                    self.focusTarget = target
                    self.focusStacks = 1
                    console.print(f"\n[buff]Focus: New target. Focus stacks: {self.focusStacks}/5[/buff]")
                
                if self._damageType in ELEMENTAL:
                    if hasattr(self, 'pugilistResType'):
                        self._stats['Temporary'][self.pugilistResType] -= 20
                    self._stats['Temporary'][damageType] += 20
                    self.pugilistResType = self._damageType

            if self._subType == 'Dualist':
                self.lastDamageType = damageType

            if self._subType == 'Manafist' and damageType in ELEMENTAL:
                damageDealt = int(damageDealt * 1.1)
            if self._ascendancy == 'Enlightened':
                damageDealt = int(damageDealt * 1.15)
            elif self._ascendancy == 'Stormwalker' and damageType == 'lightning':
                damageDealt = int(damageDealt * 1.2)
            elif self._ascendancy == 'Glacierfist' and damageType == 'cold':
                damageDealt = int(damageDealt * 1.2)

        return damageDealt, damageType

    def onHit(self, damageTaken, damageType):
        super().onHit(damageTaken, damageType)
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

        if self._subType == 'Dualist':
            prowess = 0
            if random.random() < 0.5:
                prowess = 1
            if damageType in ['lightning', 'cold']:
                prowess = 1
            if prowess == 1:
                self.prowess += prowess
                self._baseDamage += prowess * self.prowessEffect
                self._baseSpeed += (prowess / 100) * self.prowessEffect
                self._recalculateStats(False)
                console.print(f'\n[buff]Dualist: Gained 1 prowess from being hit.[/buff]')

    def rollCritical(self, target, damageDealt):
        crit, multi = super().rollCritical(target)

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
        if self._subType == 'Manafist' and self.confluxTurns > 0:
            self.confluxTurns -= 1
            if self.confluxTurns == 0:
                console.print(f'\n[dim]Conflux has expired.[/dim]')
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

        if self._subType == 'Pugilist':
            self.focusTarget = None
            self.focusStacks = 0
            self.pugilistResType = None
        elif self._subType == 'Manafist':
            self.confluxTurns = 0
        elif self._subType == 'Dualist':
            if self.lastDamageType == 'cold':
                self._baseDamage += 1
                console.print(f'\n[gold]Dualist: Ended combat with cold damage. Permanently gained +1 damage.[/gold]')
            elif self.lastDamageType == 'lightning':
                self._baseSpeed += 0.01
                console.print(f'\n[gold]Dualist: Ended combat with lightning damage. Permanently gained +0.01 speed.[/gold]')
            self.lastDamageType = None

        self.enlightenedElement = None
        self.enlightenedProwessGen = 1.0

        super().onBattleEnd()

    def updateAscendancy(self, ascendancy):
        if ascendancy == 'Enlightened':
            self._baseHealth += 10
            self._baseDamage += 2
            self._baseSpeed -= 0.1
            self._stats['baseCritChance'] += 0.05
            self._ascendancy = 'Enlightened'
            self.ascendancyDescription = MONK_DESCRIPTIONS['Enlightened']
        elif ascendancy == 'Stormwalker':
            self._baseHealth -= 5
            self._baseDamage += 1
            self._baseSpeed += 0.15
            self._stats['Permanent']['lightning'] += 20
            self._stats['baseCritChance'] += 0.03
            self._ascendancy = 'Stormwalker'
            self.ascendancyDescription = MONK_DESCRIPTIONS['Stormwalker']
        elif ascendancy == 'Glacierfist':
            self._baseHealth += 15
            self._baseDamage += 2
            self._baseSpeed -= 0.1
            self._stats['Permanent']['cold'] += 20
            self._stats['baseCritMulti'] += 0.2
            self._ascendancy = 'Glacierfist'
            self.ascendancyDescription = MONK_DESCRIPTIONS['Glacierfist']
        elif ascendancy == 'Ascetic':
            self._baseHealth += 10
            self._baseDamage -= 1
            self._baseSpeed += 0.05
            self.prowessEffect = 2
            self._stats['baseCritChance'] += 0.05
            self._ascendancy = 'Ascetic'
            self.ascendancyDescription = MONK_DESCRIPTIONS['Ascetic']
        elif ascendancy == 'Psychopath':
            self._baseHealth -= 15
            self._baseDamage += 3
            self._baseSpeed -= 0.05
            self._stats['baseCritChance'] += 0.05
            self._stats['baseCritMulti'] += 0.25
            self._stats['Permanent']['lightning'] -= 10
            self._stats['Permanent']['cold'] -= 10
            self._ascendancy = 'Psychopath'
            self.ascendancyDescription = MONK_DESCRIPTIONS['Psychopath']
        elif ascendancy == 'Avatar':
            self._baseHealth -= 15
            self._baseDamage += 2
            self._baseSpeed += 0.05
            self.prowessEffect = 2
            self._stats['Permanent']['divine'] += 10
            self._ascendancy = 'Avatar'
            self.ascendancyDescription = MONK_DESCRIPTIONS['Avatar']
        self._recalculateStats(False)

    def updateSubType(self, subType):
        if subType == 'Pugilist':
            self._baseHealth -= 10
            self._baseDamage += 1
            self._baseSpeed += 0.05
            self._subType = 'Pugilist'
            self.subTypeDescription = MONK_DESCRIPTIONS['Pugilist']
        elif subType == 'Manafist':
            self._baseHealth += 15
            self._baseDamage += 4
            self._baseSpeed += 0.05
            self._stats['Permanent']['arcane'] += 10
            self._stats['baseCritMulti'] += 0.25
            self._subType = 'Manafist'
            self.subTypeDescription = MONK_DESCRIPTIONS['Manafist']
        elif subType == 'Dualist':
            self._baseHealth += 10
            self._baseDamage -= 1
            self._baseSpeed -= 0.05
            self._stats['Permanent']['lifesteal'] += 10
            self._subType = 'Dualist'
            self.subTypeDescription = MONK_DESCRIPTIONS['Dualist']
        self._recalculateStats(False)

# Enlightened = switch element 30 times in a single combat
# Stormwalker = kill 50 enemies with lightning skills
# Glacierfist = stack 5 slows on a single enemy 5 times
# Ascetic = reach prowess buffs: +100 damage, +1 speed simultaneously
# Psychopath = kill 30 enemies with critical hits
# Pugilist = kill 50 enemies with lightning or cold damage
# Manafist = use 5 different elemental abilities in one combat
# Dualist = swap elements a total of 50 times
