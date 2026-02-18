from .base import Player
from scripts.styles import console, clearScreen, printHeader
from scripts.abilities import Effects
import random
from typing import Dict

CULTIST_DESCRIPTIONS = {
    "Cultist": "A manic worshipper of demonic powers.\n"
        "Insanity: At the start of combat, Insanity is randomly set between your minimum and maximum. Base minimum = -50, Base maximum = 50\n"
        "Positive Insanity (Manic): +2% Increased Chaos Damage per Insanity, -0.02 Speed per Insanity, +1% Crit Chance per 2 Insanity.\n"
        "Negative Insanity (Stable): +1% Damage Reduction per 5 Insanity, +1% Max HP gained as Shield at turn start per 10 Insanity.\n"
        "0 Insanity: +50% Increased Damage, +25% Damage Reduction. When attacking or attacked, Insanity is randomly set between your minimum and maximum.\n"
        "At maximum Insanity: 75% Increased Damage, take 10% of damage dealt as Chaos damage. Insanity is randomly set between -1 and your minimum.\n"
        "At minimum Insanity: 25% of damage taken from next hit is gained as damage. Take no damage from the next hit. Insanity is randomly set between 1 and your maximum.\n"
        "At the start of every turn, Insanity is randomly: Halved, Doubled, Inverted, or shifted by ±10.\n"
        "Starting Stats: 35 Health | 7 Damage | 5% Crit Chance | 160% Crit Damage | Chaos Damage | 0.9 Speed.",
    #ascendancies
    "Umbralist": "Minimum Insanity is lowered by 20. Maximum Insanity lowered by 15. At the start of your turn, if you have negative Insanity, gain 1 Shadow per 10 negative Insanity.\n"
        "Max 10 Shadow Stacks. Shadow: +1% Damage Reduction, +3% Increased Chaos Damage.\n"
        "At 10 stacks of Shadow, your next attack ignores all resistances and defenses, has +10% Lifesteal and consumes all Shadow.\n"
        "Negative Insanity grants +2% Max HP gained as Shield at turn start per 10 Insanity rather than +1%. At minimum Insanity, absorb 50% of damage taken.\n"
        "+20 HP. -1 Damage. -0.1 Speed. +10% Chaos Resistance.",
    "Harbinger": "Minimum Insanity is increased by 10. Maximum Insanity is increased by 10. Chaos damage has a 20% chance to apply Corruption, to a maximum of 10.\n"
        "Corruption: +2% Chaos Damage Taken, -1% Damage dealt. When an enemy with 5+ Corruption dies, it deals 10% of its Max HP as chaos damage to all enemies.\n"
        "Enemies have a 10% chance per Corruption to apply 1 Corruption to another enemy at the start of their turn.\n"
        "At positive Insanity: +1% Corruption chance per 5 Insanity. At negative Insanity: Enemies lose 1 Corruption when attacking you.\n"
        "At maximum Insanity, your next attack applies 2 stacks of Curse to all enemies.\n"
        "At minimum Insanity, the absorbed damage is regained as health as well as being applied as damage.\n"
        "-10 HP. +2 Damage. +0.05 Speed. +10% Dark Resistance. +15% Ailment Avoidance.",
    "Doomsayer": "At the start of your turn, you may choose to skew how your Insanity is affected, You may choose to skew towards positive or negative Insanity.\n"
        "Upon skewing your Insanity, gain 1 stack of Omen per 10 Insanity gained or lost, to a maximum of 5. If you do not skew your Insanity, gain 1 stack of Heresy, to a maximum of 10.\n"
        "Omen: +2% Damage Taken, +2% Increased Chaos Damage. Heresy: +2% Crit Chance, +10% Crit Damage, +1% Damage Taken.\n"
        "Upon dealing a critical hit, consume all Omen to gain +20% Crit Damage per Omen consumed, and consume all Heresy to gain +2% Lifesteal and +10% Crit Damage per Heresy consumed.\n"
        "At maximum Insanity, only take 5% of damage dealt as Chaos Damage.\n"
        "+15 HP. -1 Damage. -0.1 Speed. +25% Crit Damage.",
    "Ritualist": "Minimum Insanity is decreased by 15. Maximum Insanity is increased by 15. At the start of your turn, 20% chance to gain 1 stack of Bleed.\n"
        "At the start of your turn, you may sacrifice 5% of your Max HP to gain or lose 20 Insanity. Gain Elevated until the start of your next turn if you sacrifice health.\n"
        "Elevated: +20% Increased Chaos Damage, +5% Damage Reduction, +40% Ailment Avoidance.\n"
        "Gain 1 Devotion when attacking if you have at least 50 Insanity, to a maximum of 5. Gain 1 Faithless when taking damage if Insanity is at or below -50, to a maximum of 10.\n"
        "Devotion: +5% Lifesteal, +8% Increased Chaos Damage. At maximum Devotion: +10% Crit Chance. Faithless: +2% Damage Reduction, +10 HP Regen. At maximum Faithless: +80% Crit Damage.\n"
        "-10 HP. +2 Damage. +0.1 Speed. +5% Lifesteal. -10% Physical Resistance. +10% Dark Resistance.",
    "Anarchist": "Minimum Insanity is increased by 10. Maximum Insanity is increased by 20. Gain 1 Volatility per 10 damage dealt, or 15 damage taken.\n"
        "Maximum Volatility is 100. Gain 15 Volatility on kill and 10 Volatility on Critical Hit. At maximum Volatility, your next attack triggers Discharge. Discharge is based on your Insanity state.\n"
        "Positive Discharge: Deal 1% of your Max HP as Chaos Damage to all enemies per 5 Insanity. Insanity is set between -10 and 30 afterwards.\n"
        "Negative Discharge: Heal for 1% of your damage per negative Insanity. Gain Shield equal to the amount healed. Insanity is set between -30 and 10 afterwards.\n"
        "Neutral Discharge: Insanity is set to either your maximum or your minimum. Lose 5% Max Health. Your attack deals 75% Increased Chaos Damage.\n"
        "After Discharging, Volatility is set to 0. Per 25 Volatility: 10% Increased Damage, +5% Damage Taken.\n"
        "-15 HP. -2 Damage. +0.2 Speed. +15% Chaos Resistance. +5% Crit Chance. +25% Crit Damage.",
    "Desecrator": "Minimum Insanity is increased by 10. Maximum Insanity is increased by 20. Apply Ruin to enemies per 40 damage dealt. Ruin has no maximum stack limit.\n"
        "Ruin: -1% All Resistance, -1% Crit Chance. At 5+ Ruin, the affected enemy becomes Tainted. At 10+ Ruin, the affected enemy becomes Desecrated instead.\n"
        "Tainted: +10% Damage Taken, apply 1 Ruin to one random enemy on turn start. Desecrated: +20% Damage Taken, apply 3 Ruin to all other enemies on death.\n"
        "Upon killing an enemy, per Ruin stack affecting the enemy: Heal 0.5% Max HP, Gain +1 Insanity.\n"
        "Positive Insanity: Apply Ruin to enemies per 30 damage dealt instead. No longer gain Crit Chance from positive Insanity.\n"
        "Negative Insanity: Absorb 1% of damage taken per 5 Insanity if the enemy is Tainted or Desecrated. This absorbed damage is gained as damage on your next attack.\n"
        "Neutral Insanity: When attacked, your attacker loses 3% HP per Ruin affecting them.\n"
        "-10 HP. +2 Damage. -0.05 Speed. -5% Otherworldly Resistance. +15% Dark Resistance, +10% Chaos Resistance.",
    #subtypes
    "Acolyte": "Insanity effects attempt to shift towards 0. Whenever Insanity is randomised, the range is always between -20 and 20.\n"
        "At 0 Insanity: +75% Increased Damage, +35% Damage Reduction.\n"
        "Whenever the effects of 0 Insanity are triggered, gain 1 Zeal, to a maximum of 5.\n"
        "Zeal: 5% Increased Chaos Damage, +0.05 Speed. At 5 Zeal: +10% Crit Chance, +30% Crit Damage.\n"
        "+5 HP. -1 Damage. -0.05 Speed. +15% Crit Resistance.",
    "Conduit": "At maximum Insanity: 100% Increased Damage instead of 75%. At minimum Insanity: 40% of damage taken is gained as damage instead of 25%.\n"
        "Whenever a change in Insanity would cause Insanity to surpass your boundaries, gain 1 Overflow, to a maximum of 8.\n"
        "Overflow: 6% Increased Chaos Damage, -0.05 Speed, +2% Damage Taken, +10% Crit Damage.\n"
        "-10 HP. +1 Damage. +0.05 Speed. +5% Crit Chance.",
    "Preacher": "Minimum Insanity is increased by 10. Maximum Insanity is lowered by 10.\n"
        "Whenever you critically hit, gain 1 Madness, to a maximum of 20 stacks.\n"
        "Madness: +1% Crit Chance, +5% Crit Damage, -1% Damage Dealt. Upon killing an enemy, heal 1% HP per Madness.\n"
        "At Maximum Insanity, the downside of Madness is ignored. At minimum Insanity, you negate 10% of damage taken from the next 2 hits.\n"
        "+5 HP. -1 Damage. +0.1 Speed. +10% Chaos Resistance.",
}

INSANITY_EFFECTS = {
    'flat': [10, -10],
    'inverse': [-1],
    'multiply': [0.5, 2]
}

class Cultist(Player):
    def __init__(self, name, health = 35, damage = 7, baseCritChance = 0.05, baseCritMulti = 1.6, damageType = "chaos", speed = 0.9):
        super().__init__(name, health, damage, baseCritChance, baseCritMulti, damageType, speed, className='Cultist', classDescription=CULTIST_DESCRIPTIONS["Cultist"])
        self.combatStart = True
        self.insanity = 0
        self.minInsanity = -50
        self.maxInsanity = 50
        self.absorbedToAdd = 0

        self.shadow = 0
        self.omen = 0
        self.heresy = 0
        self.elevated = False
        self.devotion = 0
        self.faithless = 0
        self.volatility = 0
        self.maxVolatility = 100
        self.zeal = 0
        self.overflow = 0
        self.madness = 0
        self.preacherProtectedHits = 0

    def __str__(self):
        baseStr = super().__str__()
        
        state = "Neutral"
        maxInsanity = 0
        if self.insanity > 0:
            state = "Manic"
            maxInsanity = self.maxInsanity
        elif self.insanity < 0:
            state = "Stable"
            maxInsanity = -self.minInsanity

        baseStr += f"\n[chaos]Insanity:[/chaos] {self.insanity:+d} / {maxInsanity} ({state})"
        
        return baseStr

    def _serialise(self):
        temp = super()._serialise()
        temp['insanity'] = self.insanity
        temp['minInsanity'] = self.minInsanity
        temp['maxInsanity'] = self.maxInsanity
        return temp

    def deserialise(self, data):
        super().deserialise(data)
        self.insanity = data.get('insanity', 0)
        self.minInsanity = data.get('minInsanity', -50)
        self.maxInsanity = data.get('maxInsanity', 50)

    @property
    def insanityBuffs(self) -> Dict:
        buffs = {
            'speed': 0 if self.insanity < 0 else -0.02 * self.insanity,
            'critChance': 0 if (self.insanity < 0 or self._ascendancy == 'Desecrator') else 0.01 * (self.insanity // 2)
        }
        return buffs

    def _randomiseInsanity(self, *, min: int=None, max: int=None):
        for k, v in self.insanityBuffs.items():
            if k in self._stats['Temporary']:
                self._stats['Temporary'][k] -= v
        min = min if min is not None else self.minInsanity
        max = max if max is not None else self.maxInsanity

        if self._subType == 'Acolyte':
            min = -20
            max = 20

        self.insanity = random.randint(min, max)
        console.print(f"[chaos]Cultist: Insanity randomised! New Insanity: {self.insanity}[/chaos]")
        for k, v in self.insanityBuffs.items():
            if k in self._stats['Temporary']:
                self._stats['Temporary'][k] += v

    def _shiftInsanity(self, effect: str, val: int):
        if self._subType == 'Conduit':
            self._conduitCheckOverflow(effect, val)
        if self._subType == 'Acolyte':
            self._acolyteShiftInsanity(effect, val)
        else:
            if effect == 'flat':
                self.insanity = min(
                    self.maxInsanity,
                    max(self.minInsanity, self.insanity + val)
                )
            else:
                self.insanity = min(
                    self.maxInsanity,
                    max(self.minInsanity, int(self.insanity * val))
                )
            console.print(f"[chaos]Cultist: Insanity affected by effect: {effect.title()}. Insanity: {self.insanity}[/chaos]")

    def _acolyteShiftInsanity(self, effect: str, val: int):
        if effect == 'flat':
            if self.insanity > 0:
                val = -10
            elif self.insanity < 0:
                val = 10
            self.insanity = min(
                self.maxInsanity,
                max(self.minInsanity, self.insanity + val)
            )
        else:
            if effect == 'multiply':
                if val == 2:
                    val = 0.75
            self.insanity = min(
                self.maxInsanity,
                max(self.minInsanity, int(self.insanity * val))
            )

    def _addZeal(self):
        if self._subType == 'Acolyte' and self.zeal < 5:
            self.zeal += 1
            self._stats['Temporary']['speed'] += 0.05
            if self.zeal == 5:
                self._stats['Temporary']['critChance'] += 0.1
                self._stats['Temporary']['critMulti'] += 0.3

    def _conduitCheckOverflow(self, effect: str, val: int):
        if self._subType == 'Conduit' and self.overflow < 8:
            if effect == 'flat':
                outcome = self.insanity + val
            else:
                outcome = self.insanity * val
            if outcome < self.minInsanity or outcome > self.maxInsanity:
                self.overflow += 1
                self._stats['Temporary']['speed'] -= 0.05
                self._stats['Temporary']['critMulti'] += 0.1

    def _doomsayerSkew(self, effect: str, val: int):
        if self._ascendancy == 'Doomsayer':
            skew = False
            old = self.insanity
            while True:
                clearScreen()
                printHeader()
                console.print("[chaos]Doomsayer: Do you want to skew your Insanity? (y/n)[/chaos]")
                choice = console.input("[cyan]> [/cyan]").strip().lower()
                skew = (choice == 'y')
                if skew:
                    console.print("[chaos]Do you want to skew your Insanity positively or negatively?[/chaos]\n  [dim]1.[/dim] Positively\n  [dim]2.[/dim] Negatively")
                    choice = console.input("[cyan]> [/cyan]").strip()
                    try:
                        direction = int(choice)
                        if direction in [1, 2]:
                            if direction == 1:
                                direction = 'positive'
                            elif direction == 2:
                                direction = 'negative'
                            break
                    except ValueError:
                        console.print("[warning]Invalid Input![/warning]")
                else:
                    direction = None
                    break

            if skew and direction is not None:
                if direction == 'positive':
                    if effect == 'inverse' and self.insanity > 0:
                        effect = 'flat'
                        val = 10
                    elif effect == 'multiply' and val == 0.5 and self.insanity > 0:
                        val = 1.5
                    val = abs(val)
                else:
                    if effect == 'inverse' and self.insanity < 0:
                        effect = 'flat'
                        val = -10
                    elif effect == 'multiply' and val == 0.5 and self.insanity < 0:
                        val = 1.5
                    val = -abs(val)
                self._shiftInsanity(effect, val)
                difference = abs(old - self.insanity)
                if self.omen < 5:
                    oGain = difference // 10
                    self.omen = min(5, self.omen + oGain)
            else: # no skew, direction is none
                if self.heresy < 10:
                    self.heresy += 1
                    self._stats['Temporary']['critChance'] += 0.02
                    self._stats['Temporary']['critMulti'] += 0.1

        return skew

    def _ritualSacrifice(self):
        if self._ascendancy == 'Ritualist' and self._health > self._maxHealth * 0.05:
            printHeader()
            console.print("[dark_red]Ritualist: Sacrifice 5% HP to gain Elevated? (y/n)[/dark_red]")
            choice = console.input("[cyan]> [/cyan]").strip().lower()
            if choice == 'y':
                health = int(self._maxHealth * 0.05)
                self.damage(health, 'true', lethal=False)
                while True:
                    console.print("[dark_red]Do you want to:[/dark_red]\n  [dim]1.[/dim] Gain 20 Insanity\n  [dim]2.[/dim]Lose 20 Insanity")
                    choice = console.input("[cyan]> [/cyan]").strip()
                    try:
                        choice = int(choice)
                        if choice in [1, 2]:
                            if choice == 1:
                                self.insanity = max(self.minInsanity, self.insanity + 20)
                            elif choice == 2:
                                self.insanity = min(self.maxInsanity, self.insanity - 20)
                            self.elevated = True
                            self._stats['Temporary']['ailmentAvoidance'] += 40
                            break
                    except ValueError:
                        console.print("[warning]Invalid Input![/warning]")

    def rollCritical(self, target, damageDealt = None):
        crit, multi = super().rollCritical(target, damageDealt)

        if crit:
            if self._subType == 'Preacher' and self.madness < 20:
                self.madness += 1
                self._stats['Temporary']['critChance'] += 0.01
                self._stats['Temporary']['critMulti'] += 0.05

            if self._ascendancy == 'Doomsayer':
                multi += (0.2 * self.omen) + (0.1 * self.heresy)
                if self.heresy > 0:
                    dmg = int(damageDealt * multi)
                    heal = int(dmg * (self.heresy * 0.02))
                    self.heal(heal)
            
            elif self._ascendancy == 'Anarchist':
                self.volatility = min(self.maxVolatility, self.volatility + 10)

        return crit, multi

    def onKill(self, entity, attackData, combatManager=None):
        if self._subType == 'Preacher' and self.madness > 0:
            heal = int(self._maxHealth * (self.madness * 0.01))
            self.heal(heal)

        if self._ascendancy == 'Anarchist':
            self.volatility = min(self.maxVolatility, self.volatility + 15)

        elif self._ascendancy == 'Desecrator' and entity:
            heal = int(self._maxHealth * (0.005 * entity.ruin))
            iGain = entity.ruin
            self.heal(heal)
            self.insanity = min(self.maxInsanity, self.insanity + iGain)

        return {}

    def onAttack(self, damageDealt, damageType, target=None, combatManager=None):
        super().onAttack(damageDealt, damageType, target, combatManager)
        if self._subType == 'Preacher':
            preachIgnore = (self.insanity == self.maxInsanity)

        if self.absorbedToAdd > 0:
            damageDealt += self.absorbedToAdd
            self.absorbedToAdd = 0

        if self.insanity == self.maxInsanity:
            if self._subType != 'Conduit':
                damageDealt = int(damageDealt * 1.75)
            else:
                damageDealt *= 2
            selfDamage = int(damageDealt * 0.1)

            if self._ascendancy == 'Doomsayer':
                selfDamage //= 2 #5%

            self.damage(selfDamage, 'chaos', lethal=False)
            self._randomiseInsanity(max = -1)

        elif self.insanity > 0:
            bonus = 1 + (0.02 * self.insanity)
            damageDealt = int(damageDealt * bonus)

        elif self.insanity == 0:
            if self._subType != 'Acolyte':
                damageDealt = int(damageDealt * 1.5)
            else:
                damageDealt = int(damageDealt * 1.75)
                self._addZeal()
            self._randomiseInsanity()

        if self._subType == 'Acolyte' and self.zeal > 0:
            bonus = 1 + (0.05 * self.zeal)
            damageDealt = int(damageDealt * bonus)

        elif self._subType == 'Conduit' and self.overflow > 0 and damageType == 'chaos':
            bonus = 1 + (0.06 * self.overflow)
            damageDealt = int(damageDealt * bonus)

        elif self._subType == 'Preacher':
            if self.madness > 0 and not preachIgnore:
                reduction = 0.01 * self.madness
                damageDealt = int(damageDealt * (1 - reduction))

        if self._ascendancy == 'Umbralist' and self.shadow > 0 and damageType == 'chaos':
            damageDealt = int(damageDealt * (1 + (self.shadow * 0.03)))
            if self.shadow == 10:
                damageType = 'true'
                self.shadow = 0
                heal = int(damageDealt * 0.1)
                self.heal(heal)

        elif self._ascendancy == 'Harbinger':
            if damageType == 'chaos' and target:
                target = target.entity
                bonusChance = 0
                if self.insanity > 0:
                    bonusChance = 0.01 * (self.insanity // 5)
                if random.random() < (0.2 + bonusChance) and target.corruption < 10:
                    target.corruption += 1

        elif self._ascendancy == 'Doomsayer':
            if self.omen > 0 and damageType == 'chaos':
                bonus = 1 + (self.omen * 0.02)
                damageDealt = int(damageDealt * bonus)

        elif self._ascendancy == 'Ritualist':
            if damageType == 'chaos':
                bonus = 1 + (self.devotion * 0.08)
                damageDealt = int(damageDealt * bonus)

            if self.insanity >= 50 and self.devotion < 5:
                self.devotion += 1
                self._stats['Temporary']['lifesteal'] += 8
                if self.devotion == 5:
                    self._stats['Temporary']['critChance'] += 0.1

        elif self._ascendancy == 'Anarchist':
            bonus = 1 + (0.1 * (self.volatility // 25))
            if self.volatility < self.maxVolatility:
                vGain = damageDealt // 10
                self.volatility = min(self.maxVolatility, self.volatility + vGain)

            elif self.volatility == self.maxVolatility:
                if self.insanity > 0:
                    pass # > 0 handled in combat
                elif self.insanity < 0: 
                    heal = int(self._damage * abs(self.insanity))
                    self.heal(heal)
                    self._shield += heal
                    self._randomiseInsanity(min=-30, max=10)
                elif self.insanity == 0:
                    self.insanity = random.choice([self.minInsanity, self.maxInsanity])
                    damage = int(self._maxHealth * 0.05)
                    self.damage(damage, 'true', lethal=False)
                    if damageType == 'chaos':
                        damageDealt = int(damageDealt * 1.75)
                self.volatility = 0

        elif self._ascendancy == 'Desecrator':
            if self.insanity > 0:
                ruin = damageDealt // 30
            else:
                ruin = damageDealt // 40
            if target:
                target = target.entity
                target.ruin += ruin

        return damageDealt, damageType

    def onHit(self, damageTaken, damageType, attacker = None, combatManager=None):
        super().onHit(damageTaken, damageType, attacker, combatManager)

        if self.insanity == self.minInsanity:
            self.absorbedToAdd += int(damageTaken * 0.25)

            if self._subType == 'Conduit':
                self.absorbedToAdd += int(damageTaken * 0.15)

            elif self._subType == 'Preacher':
                self.preacherProtectedHits = 2

            if self._ascendancy == 'Umbralist':
                self.absorbedToAdd *= 2

            elif self._ascendancy == 'Harbinger':
                self.heal(int(damageTaken * 0.25))

            self._randomiseInsanity(min = 1)
            damageTaken = 0

        elif self.insanity < 0:
            dr = abs(self.insanity) // 5 * 0.01
            damageTaken = int(damageTaken * (1 - dr))

            if self._ascendancy == 'Desecrator' and attacker:
                if attacker.tainted or attacker.desecrated:
                    absorb = int(0.01 * damageTaken * (abs(self.insanity) // 5))
                    self.absorbedToAdd += absorb
                    damageTaken -= absorb

        elif self.insanity == 0:
            if self._subType != 'Acolyte':
                damageTaken = int(damageTaken * 0.75)
            else:
                damageTaken = int(damageTaken * 0.65)
                self._addZeal()

            if self._ascendancy == 'Desecrator' and attacker and attacker.ruin > 0:
                damage = int(attacker._maxHealth * (0.03 * attacker.ruin))
                attacker.damage(damage, 'true')

            self._randomiseInsanity()

        if self._subType == 'Preacher' and self.preacherProtectedHits > 0:
            damageTaken = int(damageTaken * 0.9)
            self.preacherProtectedHits -= 1

        if self._ascendancy == 'Umbralist' and self.shadow > 0:
            damageTaken = int(damageTaken * (1 - (self.shadow * 0.01)))

        elif self._ascendancy == 'Doomsayer':
            bonus = 1 + (self.omen * 0.02) + (self.heresy * 0.01)
            damageTaken = int(damageTaken * bonus)

        elif self._ascendancy == 'Ritualist':
            dr = self.faithless * 0.02
            damageTaken = int(damageTaken * (1 - dr))

            if self.insanity <= -50 and self.faithless < 10:
                self.faithless += 1
                self._stats['Temporary']['hpRegen'] += 10
                if self.faithless == 10:
                    self._stats['Temporary']['critMulti'] += 0.8

        elif self._ascendancy == 'Anarchist':
            if self.volatility < self.maxVolatility:
                vGain = damageTaken // 15
                self.volatility = min(self.maxVolatility, self.volatility + vGain)

        return damageTaken, damageType

    def onTurnStart(self, combatManager=None):
        if self.combatStart:
            self._randomiseInsanity()
            self.combatStart = False
        else:
            effect = random.choice(list(INSANITY_EFFECTS.keys()))
            val = random.choice(INSANITY_EFFECTS[effect])
            proceed = True
            if self._ascendancy == 'Doomsayer':
                if self._doomsayerSkew(effect, val):
                    proceed = False
            if proceed:
                self._shiftInsanity(effect, val)

        if self.insanity < 0:
            sGainPercent = abs(self.insanity) // 10 * 0.01
            if self._ascendancy == 'Umbralist':
                sGainPercent *= 2
            if sGainPercent > 0:
                sGain = int(self._maxHealth * sGainPercent)
                self._shield += sGain

        if self._ascendancy == 'Umbralist' and self.insanity < 0:
            if self.shadow < 10:
                gain = abs(self.insanity) // 10
                self.shadow = min(10, self.shadow + gain)

        if self._ascendancy == 'Ritualist':
            if self.elevated:
                self._stats['Temporary']['ailmentAvoidance'] += 40
            self.elevated = False
            if random.random() < 0.2 and combatManager:
                bleed = Effects.createBleed()[0]
                combatManager.addStatusEffect(self, bleed, self)
            self._ritualSacrifice()

        super().onTurnStart(combatManager)

    def onBattleEnd(self):
        self.insanity = 0
        self.combatStart = True
        self.absorbedToAdd = 0
        self.shadow = 0
        self.omen = 0
        self.heresy = 0
        self.elevated = False
        self.devotion = 0
        self.faithless = 0
        self.volatility = 0
        self.zeal = 0
        self.overflow = 0
        self.madness = 0
        self.preacherProtectedHits = 0

        super().onBattleEnd()

    def updateAscendancy(self, ascendancy):
        if ascendancy == 'Umbralist':
            self._baseHealth += 20
            self._baseDamage -= 1
            self._baseSpeed -= 0.1
            self.minInsanity -= 20
            self.maxInsanity -= 15
            self._stats['Permanent']['chaos'] += 10
            self._ascendancy = 'Umbralist'
            self.ascendancyDescription = CULTIST_DESCRIPTIONS["Umbralist"]
        elif ascendancy == 'Harbinger':
            self._baseHealth -= 10
            self._baseDamage += 2
            self._baseSpeed += 0.05
            self.minInsanity += 10
            self.maxInsanity += 10
            self._stats['Permanent']['dark'] += 10
            self._stats['Permanent']['ailmentAvoidance'] += 15
            self._ascendancy = 'Harbinger'
            self.ascendancyDescription = CULTIST_DESCRIPTIONS["Harbinger"]
        elif ascendancy == 'Doomsayer':
            self._baseHealth += 15
            self._baseDamage -= 1
            self._baseSpeed -= 0.1
            self._stats['baseCritMulti'] += 0.25
            self._ascendancy = 'Doomsayer'
            self.ascendancyDescription = CULTIST_DESCRIPTIONS["Doomsayer"]
        elif ascendancy == 'Ritualist':
            self._baseHealth -= 10
            self._baseDamage += 2
            self._baseSpeed += 0.1
            self.minInsanity -= 15
            self.maxInsanity += 15
            self._stats['Permanent']['lifesteal'] += 5
            self._stats['Permanent']['physical'] -= 10
            self._stats['Permanent']['dark'] += 10
            self._ascendancy = 'Ritualist'
            self.ascendancyDescription = CULTIST_DESCRIPTIONS["Ritualist"]
        elif ascendancy == 'Anarchist':
            self._baseHealth -= 15
            self._baseDamage -= 2
            self._baseSpeed += 0.1
            self.minInsanity += 10
            self.maxInsanity += 20
            self._stats['Permanent']['chaos'] += 15
            self._stats['baseCritChance'] += 0.05
            self._stats['baseCritMulti'] += 0.25
            self._ascendancy = 'Anarchist'
            self.ascendancyDescription = CULTIST_DESCRIPTIONS["Anarchist"]
        elif ascendancy == 'Desecrator':
            self._baseHealth -= 10
            self._baseDamage += 2
            self._baseSpeed -= 0.05
            self._stats['Permanent']['otherworldly'] -= 5
            self._stats['Permanent']['dark'] += 15
            self._stats['Permanent']['chaos'] += 10
            self._ascendancy = 'Desecrator'
            self.ascendancyDescription = CULTIST_DESCRIPTIONS["Desecrator"]

    def updateSubType(self, subType):
        if subType == 'Acolyte':
            self._baseHealth += 5
            self._baseDamage -= 1
            self._baseSpeed -= 0.05
            self._stats['Permanent']['critResistance'] += 15
            self._subType = 'Acolyte'
            self.subTypeDescription = CULTIST_DESCRIPTIONS["Acolyte"]
        elif subType == 'Conduit':
            self._baseHealth -= 10
            self._baseDamage += 1
            self._baseSpeed += 0.05
            self._stats['baseCritChance'] += 0.05
            self._subType = 'Conduit'
            self.subTypeDescription = CULTIST_DESCRIPTIONS["Conduit"]
        elif subType == 'Preacher':
            self._baseHealth += 5
            self._baseDamage -= 1
            self._baseSpeed += 0.1
            self.minInsanity += 10
            self.maxInsanity -= 10
            self._stats['Permanent']['chaos'] += 10
            self._subType == 'Preacher'
            self.subTypeDescription = CULTIST_DESCRIPTIONS["Preacher"]

