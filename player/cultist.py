from .base import Player
from scripts.styles import console, clearScreen, printHeader
from scripts.abilities import Effects
import random
from typing import Dict

CULTIST_DESCRIPTIONS = {
    "Cultist": "[class_cultist]A manic worshipper of demonic powers.[/class_cultist]\n"
        "[resource]Insanity[/resource]: At the start of combat, [resource]Insanity[/resource] is randomly set between your minimum and maximum. Base minimum = -50, Base maximum = 50\n"
        "Positive [resource]Insanity[/resource] ([resource]Manic[/resource]): +2% Increased [chaos]Chaos[/chaos] Damage per [resource]Insanity[/resource], -0.02 [speed]Speed[/speed] per [resource]Insanity[/resource], +1% [critical]Crit Chance[/critical] per 2 [resource]Insanity[/resource].\n"
        "Negative [resource]Insanity[/resource] ([resource]Stable[/resource]): +1% [resistance]Damage Reduction[/resistance] per 5 [resource]Insanity[/resource], +1% Max HP gained as [buff]Shield[/buff] at turn start per 10 [resource]Insanity[/resource].\n"
        "0 [resource]Insanity[/resource]: +50% Increased Damage, +25% [resistance]Damage Reduction[/resistance]. When attacking or attacked, [resource]Insanity[/resource] is randomly set between your minimum and maximum.\n"
        "At maximum [resource]Insanity[/resource]: 75% Increased Damage, take 10% of damage dealt as [chaos]Chaos[/chaos] damage. [resource]Insanity[/resource] is randomly set between -1 and your minimum.\n"
        "At minimum [resource]Insanity[/resource]: 25% of damage taken from next hit is gained as damage. Take no damage from the next hit. [resource]Insanity[/resource] is randomly set between 1 and your maximum.\n"
        "At the start of every turn, [resource]Insanity[/resource] is randomly: Halved, Doubled, Inverted, or shifted by ±10.\n"
        "Starting Stats: 35 [health]Health[/health] | 7 [damage]Damage[/damage] | 5% [critical]Crit Chance[/critical] | 160% [critical]Crit Damage[/critical] | [chaos]Chaos Damage[/chaos] | 0.9 [speed]Speed[/speed].",
    #ascendancies
    "Umbralist": "Minimum [resource]Insanity[/resource] is lowered by 20. Maximum [resource]Insanity[/resource] lowered by 15. At the start of your turn, if you have negative [resource]Insanity[/resource], gain 1 [asc_umbralist]Shadow[/asc_umbralist] per 10 negative [resource]Insanity[/resource].\n"
        "Max 10 [asc_umbralist]Shadow[/asc_umbralist] Stacks. [asc_umbralist]Shadow[/asc_umbralist]: +1% [resistance]Damage Reduction[/resistance], +3% Increased [chaos]Chaos[/chaos] Damage.\n"
        "At 10 stacks of [asc_umbralist]Shadow[/asc_umbralist], your next attack ignores all resistances and defenses, has +10% [lifesteal]Lifesteal[/lifesteal] and consumes all [asc_umbralist]Shadow[/asc_umbralist].\n"
        "Negative [resource]Insanity[/resource] grants +2% Max HP gained as [buff]Shield[/buff] at turn start per 10 [resource]Insanity[/resource] rather than +1%. At minimum [resource]Insanity[/resource], absorb 50% of damage taken.\n"
        "+20 [health]HP[/health]. -1 [damage]Damage[/damage]. -0.1 [speed]Speed[/speed]. +10% [chaos]Chaos[/chaos] Resistance.",
    "Harbinger": "Minimum [resource]Insanity[/resource] is increased by 10. Maximum [resource]Insanity[/resource] is increased by 10. [chaos]Chaos[/chaos] damage has a 20% chance to apply [asc_harbinger]Corruption[/asc_harbinger], to a maximum of 10.\n"
        "[asc_harbinger]Corruption[/asc_harbinger]: +2% [chaos]Chaos[/chaos] Damage Taken, -1% Damage dealt. When an enemy with 5+ [asc_harbinger]Corruption[/asc_harbinger] dies, it deals 10% of its Max HP as [chaos]chaos[/chaos] damage to all enemies.\n"
        "Enemies have a 10% chance per [asc_harbinger]Corruption[/asc_harbinger] to apply 1 [asc_harbinger]Corruption[/asc_harbinger] to another enemy at the start of their turn.\n"
        "At positive [resource]Insanity[/resource]: +1% [asc_harbinger]Corruption[/asc_harbinger] chance per 5 [resource]Insanity[/resource]. At negative [resource]Insanity[/resource]: Enemies lose 1 [asc_harbinger]Corruption[/asc_harbinger] when attacking you.\n"
        "At maximum [resource]Insanity[/resource], your next attack applies 2 stacks of Curse to all enemies.\n"
        "At minimum [resource]Insanity[/resource], the absorbed damage is regained as health as well as being applied as damage.\n"
        "-10 [health]HP[/health]. +2 [damage]Damage[/damage]. +0.05 [speed]Speed[/speed]. +10% [dark]Dark[/dark] Resistance. +15% Ailment Avoidance.",
    "Doomsayer": "At the start of your turn, you may choose to skew how your [resource]Insanity[/resource] is affected, You may choose to skew towards positive or negative [resource]Insanity[/resource].\n"
        "Upon skewing your [resource]Insanity[/resource], gain 1 stack of [asc_doomsayer]Omen[/asc_doomsayer] per 10 [resource]Insanity[/resource] gained or lost, to a maximum of 5. If you do not skew your [resource]Insanity[/resource], gain 1 stack of [asc_doomsayer]Heresy[/asc_doomsayer], to a maximum of 10.\n"
        "[asc_doomsayer]Omen[/asc_doomsayer]: +2% Damage Taken, +2% Increased [chaos]Chaos[/chaos] Damage. [asc_doomsayer]Heresy[/asc_doomsayer]: +2% [critical]Crit Chance[/critical], +10% [critical]Crit Damage[/critical], +1% Damage Taken.\n"
        "Upon dealing a critical hit, consume all [asc_doomsayer]Omen[/asc_doomsayer] to gain +20% [critical]Crit Damage[/critical] per [asc_doomsayer]Omen[/asc_doomsayer] consumed, and consume all [asc_doomsayer]Heresy[/asc_doomsayer] to gain +2% [lifesteal]Lifesteal[/lifesteal] and +10% [critical]Crit Damage[/critical] per [asc_doomsayer]Heresy[/asc_doomsayer] consumed.\n"
        "At maximum [resource]Insanity[/resource], only take 5% of damage dealt as [chaos]Chaos[/chaos] Damage.\n"
        "+15 [health]HP[/health]. -1 [damage]Damage[/damage]. -0.1 [speed]Speed[/speed]. +25% [critical]Crit Damage[/critical].",
    "Ritualist": "Minimum [resource]Insanity[/resource] is decreased by 15. Maximum [resource]Insanity[/resource] is increased by 15. At the start of your turn, 20% chance to gain 1 stack of Bleed.\n"
        "At the start of your turn, you may sacrifice 5% of your Max HP to gain or lose 20 [resource]Insanity[/resource]. Gain [asc_ritualist]Elevated[/asc_ritualist] until the start of your next turn if you sacrifice health.\n"
        "[asc_ritualist]Elevated[/asc_ritualist]: +20% Increased [chaos]Chaos[/chaos] Damage, +5% [resistance]Damage Reduction[/resistance], +40% Ailment Avoidance.\n"
        "Gain 1 [asc_ritualist]Devotion[/asc_ritualist] when attacking if you have at least 50 [resource]Insanity[/resource], to a maximum of 5. Gain 1 [asc_ritualist]Faithless[/asc_ritualist] when taking damage if [resource]Insanity[/resource] is at or below -50, to a maximum of 10.\n"
        "[asc_ritualist]Devotion[/asc_ritualist]: +5% [lifesteal]Lifesteal[/lifesteal], +8% Increased [chaos]Chaos[/chaos] Damage. At maximum [asc_ritualist]Devotion[/asc_ritualist]: +10% [critical]Crit Chance[/critical]. [asc_ritualist]Faithless[/asc_ritualist]: +2% [resistance]Damage Reduction[/resistance], +10 HP [regen]Regen[/regen]. At maximum [asc_ritualist]Faithless[/asc_ritualist]: +80% [critical]Crit Damage[/critical].\n"
        "-10 [health]HP[/health]. +2 [damage]Damage[/damage]. +0.1 [speed]Speed[/speed]. +5% [lifesteal]Lifesteal[/lifesteal]. -10% Physical Resistance. +10% [dark]Dark[/dark] Resistance.",
    "Anarchist": "Minimum [resource]Insanity[/resource] is increased by 10. Maximum [resource]Insanity[/resource] is increased by 20. Gain 1 [asc_anarchist]Volatility[/asc_anarchist] per 10 damage dealt, or 15 damage taken.\n"
        "Maximum [asc_anarchist]Volatility[/asc_anarchist] is 100. Gain 15 [asc_anarchist]Volatility[/asc_anarchist] on kill and 10 [asc_anarchist]Volatility[/asc_anarchist] on Critical Hit. At maximum [asc_anarchist]Volatility[/asc_anarchist], your next attack triggers [asc_anarchist]Discharge[/asc_anarchist]. [asc_anarchist]Discharge[/asc_anarchist] is based on your [resource]Insanity[/resource] state.\n"
        "Positive [asc_anarchist]Discharge[/asc_anarchist]: Deal 1% of your Max HP as [chaos]Chaos[/chaos] Damage to all enemies per 5 [resource]Insanity[/resource]. [resource]Insanity[/resource] is set between -10 and 30 afterwards.\n"
        "Negative [asc_anarchist]Discharge[/asc_anarchist]: Heal for 1% of your damage per negative [resource]Insanity[/resource]. Gain [buff]Shield[/buff] equal to the amount healed. [resource]Insanity[/resource] is set between -30 and 10 afterwards.\n"
        "Neutral [asc_anarchist]Discharge[/asc_anarchist]: [resource]Insanity[/resource] is set to either your maximum or your minimum. Lose 5% Max Health. Your attack deals 75% Increased [chaos]Chaos[/chaos] Damage.\n"
        "After Discharging, [asc_anarchist]Volatility[/asc_anarchist] is set to 0. Per 25 [asc_anarchist]Volatility[/asc_anarchist]: 10% Increased Damage, +5% Damage Taken.\n"
        "-15 [health]HP[/health]. -2 [damage]Damage[/damage]. +0.2 [speed]Speed[/speed]. +15% [chaos]Chaos[/chaos] Resistance. +5% [critical]Crit Chance[/critical]. +25% [critical]Crit Damage[/critical].",
    "Desecrator": "Minimum [resource]Insanity[/resource] is increased by 10. Maximum [resource]Insanity[/resource] is increased by 20. Apply [asc_desecrator]Ruin[/asc_desecrator] to enemies per 40 damage dealt. [asc_desecrator]Ruin[/asc_desecrator] has no maximum stack limit.\n"
        "[asc_desecrator]Ruin[/asc_desecrator]: -1% All Resistance, -1% [critical]Crit Chance[/critical]. At 5+ [asc_desecrator]Ruin[/asc_desecrator], the affected enemy becomes [asc_desecrator]Tainted[/asc_desecrator]. At 10+ [asc_desecrator]Ruin[/asc_desecrator], the affected enemy becomes [asc_desecrator]Desecrated[/asc_desecrator] instead.\n"
        "[asc_desecrator]Tainted[/asc_desecrator]: +10% Damage Taken, apply 1 [asc_desecrator]Ruin[/asc_desecrator] to one random enemy on turn start. [asc_desecrator]Desecrated[/asc_desecrator]: +20% Damage Taken, apply 3 [asc_desecrator]Ruin[/asc_desecrator] to all other enemies on death.\n"
        "Upon killing an enemy, per [asc_desecrator]Ruin[/asc_desecrator] stack affecting the enemy: Heal 0.5% Max HP, Gain +1 [resource]Insanity[/resource].\n"
        "Positive [resource]Insanity[/resource]: Apply [asc_desecrator]Ruin[/asc_desecrator] to enemies per 30 damage dealt instead. No longer gain [critical]Crit Chance[/critical] from positive [resource]Insanity[/resource].\n"
        "Negative [resource]Insanity[/resource]: Absorb 1% of damage taken per 5 [resource]Insanity[/resource] if the enemy is [asc_desecrator]Tainted[/asc_desecrator] or [asc_desecrator]Desecrated[/asc_desecrator]. This absorbed damage is gained as damage on your next attack.\n"
        "Neutral [resource]Insanity[/resource]: When attacked, your attacker loses 3% HP per [asc_desecrator]Ruin[/asc_desecrator] affecting them.\n"
        "-10 [health]HP[/health]. +2 [damage]Damage[/damage]. -0.05 [speed]Speed[/speed]. -5% Otherworldly Resistance. +15% [dark]Dark[/dark] Resistance, +10% [chaos]Chaos[/chaos] Resistance.",
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

        self.insanity = random.randint(min, max)
        console.print(f"[chaos]Cultist: Insanity randomised! New Insanity: {self.insanity}[/chaos]")
        for k, v in self.insanityBuffs.items():
            if k in self._stats['Temporary']:
                self._stats['Temporary'][k] += v

    def _shiftInsanity(self, effect: str, val: int):
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

        if self.absorbedToAdd > 0:
            damageDealt += self.absorbedToAdd
            self.absorbedToAdd = 0

        if self.insanity == self.maxInsanity:
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
            damageDealt = int(damageDealt * 1.75)
            self._randomiseInsanity()

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

    def onHit(self, damageTaken, damageType, isCrit: bool, attacker = None, combatManager=None):
        super().onHit(damageTaken, damageType, isCrit, attacker, combatManager)

        if self.insanity == self.minInsanity:
            self.absorbedToAdd += int(damageTaken * 0.25)

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
            damageTaken = int(damageTaken * 0.65)

            if self._ascendancy == 'Desecrator' and attacker and attacker.ruin > 0:
                damage = int(attacker._maxHealth * (0.03 * attacker.ruin))
                attacker.damage(damage, 'true')

            self._randomiseInsanity()

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

