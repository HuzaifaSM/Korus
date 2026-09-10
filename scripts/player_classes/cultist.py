from .base import Player
from scripts.styles import console, clearScreen, printHeader
from scripts.abilities import Effects
import random
from typing import Dict

CULTIST_DESCRIPTIONS = {
    "Cultist": "[class_cultist]A manic worshipper of demonic powers.[/class_cultist]\n"
        "- Insanity: At the start of combat, Insanity is randomly set between your minimum and maximum. Base minimum = -50, Base maximum = 50\n"
        "- Positive Insanity (Manic): +2% Increased Chaos Damage per Insanity, -0.02 Speed per Insanity, +1% Crit Chance per 2 Insanity.\n"
        "- Negative Insanity (Stable): +1% Damage Reduction per 5 Insanity, +1% Max HP gained as Shield at turn start per 10 Insanity.\n"
        "- 0 Insanity: +50% Increased Damage, +25% Damage Reduction. When attacking or attacked, Insanity is randomly set between your minimum and maximum.\n"
        "- At maximum Insanity: 75% Increased Damage, take 10% of damage dealt as Chaos damage. Insanity is randomly set between -1 and your minimum.\n"
        "- At minimum Insanity: 25% of the damage taken from the next hit is gained as damage. Take no damage from the next hit. Insanity is randomly set between 1 and your maximum.\n"
        "- At the start of every turn, Insanity is randomly: Halved, Doubled, Inverted, or shifted by ±10.\n"
        "[bold]Starting Stats:[/bold] 40 Health | 7 Damage | 5% Crit Chance | 160% Crit Damage | Chaos Damage | 0.9 Speed.",
    #ascendancies
    "Umbralist": "[lore]Embrace the darkness. Let it swallow you whole. Once the shadows fall, consume them. Only you will remain.[/lore]"
        "- Minimum Insanity is lowered by 20. Maximum Insanity lowered by 15. At the start of your turn, if you have negative Insanity, gain 1 Shadow per 10 negative Insanity.\n"
        "- Max 10 Shadow Stacks. Shadow: +1% Damage Reduction, +3% Increased Chaos Damage.\n"
        "- At 10 stacks of Shadow, your next attack ignores all resistances and defenses, has +10% Lifesteal and consumes all Shadow.\n"
        "- Negative Insanity grants +2% Max HP gained as Shield at turn start per 10 Insanity rather than +1%. At minimum Insanity, 50% of the damage taken from the next hit is gained as damage.\n"
        "[bold]Stat Changes:[/bold] +40 HP. -0.1 Speed. +10% Chaos Resistance. +5% Damage Reduction.",
    "Harbinger": "[lore]Become the herald of ruin. Show them the depths of your mind, until all becomes one. You are the beginning, and the end.[/lore]"
        "- Minimum Insanity is increased by 10. Maximum Insanity is increased by 10. Chaos damage has a 20% chance to apply Corruption, to a maximum of 10.\n"
        "- Corruption: +2% Chaos Damage Taken, -1% Damage dealt. When an enemy with 5+ Corruption dies, it deals 10% of its Max HP as Chaos damage to all enemies.\n"
        "- Enemies have a 10% chance per Corruption to apply 1 Corruption to another enemy at the start of their turn.\n"
        "- At positive Insanity: +1% Corruption chance per 5 Insanity. At negative Insanity: Enemies lose 1 Corruption when attacking you.\n"
        "- At maximum Insanity, your next attack applies 2 stacks of Curse to all enemies.\n"
        "- At minimum Insanity, the absorbed damage is regained as health as well as being applied as damage.\n"
        "[bold]Stat Changes:[/bold] -5 HP. +10 Damage. +0.05 Speed. +10% Dark Resistance. +15% Ailment Avoidance.",
    "Doomsayer": "[lore]The end is here. You know, for it is you. The madness was tamed, curated into a beast of punishment, but not just for your enemies...[/lore]"
        "- At the start of your turn, you may choose to skew how your Insanity is affected, You may choose to skew towards positive or negative Insanity.\n"
        "- Upon skewing your Insanity, gain 1 stack of Omen per 10 Insanity gained or lost, to a maximum of 5. If you do not skew your Insanity, gain 1 stack of Heresy, to a maximum of 10.\n"
        "- Omen: +2% Damage Taken, +2% Increased Chaos Damage. Heresy: +2% Crit Chance, +10% Crit Damage, +1% Damage Taken.\n"
        "- Upon dealing a critical hit, consume all Omen to gain +20% Crit Damage per Omen consumed, and consume all Heresy to gain +2% Lifesteal and +10% Crit Damage per Heresy consumed.\n"
        "- At maximum Insanity, only take 5% of damage dealt as Chaos Damage.\n"
        "[bold]Stat Changes:[/bold] +40 HP. +2 Damage. -0.1 Speed. +25% Crit Damage.",
    "Ritualist": "[lore][dim]'Offer your flesh.'... 'To a god?'... 'No. To yourself.'[/dim] ...Divinity is dead. In suffering, find hate. In death, find faith.[/lore]"
        "- Minimum Insanity is decreased by 15. Maximum Insanity is increased by 15. At the start of your turn, 20% chance to gain 1 stack of Bleed.\n"
        "- At the start of your turn, you may sacrifice 5% of your Max HP to gain or lose 20 Insanity. Gain Elevated until the start of your next turn if you sacrifice health.\n"
        "- Elevated: +20% Increased Chaos Damage, +5% Damage Reduction, +40% Ailment Avoidance.\n"
        "- Gain 1 Devotion when attacking if you have at least 50 Insanity, to a maximum of 5. Gain 1 Faithless when taking damage if Insanity is at or below -50, to a maximum of 10.\n"
        "- Devotion: +5% Lifesteal, +8% Increased Chaos Damage. At maximum Devotion: +10% Crit Chance. Faithless: +2% Damage Reduction, +10 HP Regen. At maximum Faithless: +80% Crit Damage.\n"
        "[bold]Stat Changes:[/bold] -10 HP. +10 Damage. +0.1 Speed. +5% Lifesteal. -10% Physical Resistance. +10% Dark Resistance.",
    "Anarchist": "[lore]Break everything. Your sanity. Your limits. Reality. Let nothing remain, for you are Death Incarnate.[/lore]"
        "- Minimum Insanity is increased by 10. Maximum Insanity is increased by 20. Gain 1 Volatility per 10 damage dealt, or 15 damage taken.\n"
        "- Maximum Volatility is 100. Gain 15 Volatility on kill and 10 Volatility on Critical Hit. At maximum Volatility, your next attack triggers Discharge. Discharge is based on your Insanity state.\n"
        "- Positive Discharge: Deal 1% of your Max HP as Chaos Damage to all enemies per 5 Insanity. Insanity is set between -10 and 30 afterwards.\n"
        "- Negative Discharge: Heal for 1% of your damage per negative Insanity. Gain Shield equal to the amount healed. Insanity is set between -30 and 10 afterwards.\n"
        "- Neutral Discharge: Insanity is set to either your maximum or your minimum. Lose 5% Max Health. Your attack deals 75% Increased Chaos Damage.\n"
        "- After Discharging, Volatility is set to 0. Per 25 Volatility: 10% Increased Damage, +5% Damage Taken.\n"
        "[bold]Stat Changes:[/bold] -10 HP. -6 Damage. +0.25 Speed. +15% Chaos Resistance. +8% Crit Chance. +40% Crit Damage. +5% Lifesteal.",
    "Desecrator": "[lore]There is no peace. No safety. No salvation. Defile everything, living and dead. Leave this world a field of corpses.[/lore]"
        "- Minimum Insanity is increased by 10. Maximum Insanity is increased by 20. Apply Ruin to enemies per 40 damage dealt. Ruin has no maximum stack limit.\n"
        "- Ruin: -1% All Resistance, -1% Crit Chance. At 5+ Ruin, the affected enemy becomes Tainted. At 10+ Ruin, the affected enemy becomes Desecrated instead.\n"
        "- Tainted: +10% Damage Taken, apply 1 Ruin to one random enemy on turn start. Desecrated: +20% Damage Taken, apply 3 Ruin to all other enemies on death.\n"
        "- Upon killing an enemy, per Ruin stack affecting the enemy: Heal 0.5% Max HP, Gain +1 Insanity.\n"
        "- Positive Insanity: Apply Ruin to enemies per 30 damage dealt instead. No longer gain Crit Chance from positive Insanity.\n"
        "- Negative Insanity: Absorb 1% of damage taken per 5 Insanity if the enemy is Tainted or Desecrated. This absorbed damage is gained as damage on your next attack.\n"
        "- Neutral Insanity: When attacked, your attacker loses 3% HP per Ruin affecting them.\n"
        "[bold]Stat Changes:[/bold] -10 HP. +10 Damage. -0.05 Speed. -5% Otherworldly Resistance. +15% Dark Resistance, +10% Chaos Resistance. +15% Resistance Penetration.",
}

INSANITY_EFFECTS = {
    'flat': [10, -10],
    'inverse': [-1],
    'multiply': [0.5, 2]
}

class Cultist(Player):
    def __init__(self, name, health = 40, damage = 7, baseCritChance = 0.05, baseCritMulti = 1.6, damageType = "chaos", speed = 0.9):
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

    def serialise(self):
        temp = super().serialise()
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

    def _doomsayerSkew(self, effect: str, val: int):
        if self._ascendancy == 'Doomsayer':
            skew = False
            old = self.insanity
            while True:
                clearScreen()
                printHeader("Doomsayer")
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
                    self._stats['Temporary']['crit_chance'] += 0.02
                    self._stats['Temporary']['crit_multi'] += 0.1

        return skew

    def _ritualSacrifice(self):
        if self._ascendancy == 'Ritualist' and self._health > self._maxHealth * 0.05:
            printHeader("Ritualist")
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
                            self._stats['Temporary']['ailment_avoidance'] += 40
                            break
                    except ValueError:
                        console.print("[warning]Invalid Input![/warning]")

    def gainDevotion(self):
        if self.devotion < 5:
            self.devotion += 1
            self._stats['Temporary']['lifesteal'] += 8
            if self.devotion == 5:
                self._stats['Temporary']['crit_chance'] += 0.1

    def gainFaithless(self):
        if self.faithless < 10:
            self.faithless += 1
            self._stats['Temporary']['hp_regen'] += 10
            if self.faithless == 10:
                self._stats['Temporary']['crit_multi'] += 0.8

    def rollCritical(self, target, damageDealt = None):
        crit, multi = super().rollCritical(target, damageDealt)

        if crit:
            if self._ascendancy == 'Doomsayer':
                bonus = (0.2 * self.omen) + (0.1 * self.heresy)
                if bonus:
                    console.print(f"[asc_doomsayer]Doomsayer: Critical Hit consumes {self.omen} Omen and {self.heresy} Heresy for +{int(bonus * 100)}% Crit Damage![/asc_doomsayer]")
                multi += bonus
                if self.heresy > 0:
                    dmg = int(damageDealt * multi)
                    heal = int(dmg * (self.heresy * 0.02))
                    self.heal(heal, reason="Doomsayer (Heresy Lifesteal on Crit)")
                self.omen = 0
                self.heresy = 0

            elif self._ascendancy == 'Anarchist':
                self.volatility = min(self.maxVolatility, self.volatility + 10)

        return crit, multi

    def onAbilityCast(self, ability, combatManager):
        super().onAbilityCast(ability, combatManager)
        if not ability:
            return

        insanityShift = ability.effects.get('self', {}).get('insanity_shift', {}).get('amount', 0)
        if insanityShift:
            self._shiftInsanity('flat', insanityShift)
            console.print(f"[chaos]Cultist: {ability.name} shifts Insanity by {insanityShift:+}. Current Insanity: {self.insanity}[/chaos]")

        if self._ascendancy == 'Umbralist' and 'gain_shadow_on_cast' in ability.tags:
            fx = ability.effects.get('self', {}).get('gain_shadow', {})
            stacks = fx.get('stacks', 0)
            self.shadow = min(10, self.shadow + stacks)

        if self._ascendancy == 'Doomsayer' and 'gain_omen_heresy_on_cast' in ability.tags:
            fx = ability.effects.get('self', {}).get('gain_omen_heresy', {})
            stacks = fx.get('stacks', 0)
            self.omen = min(5, self.omen + stacks)
            self.heresy = min(10, self.heresy + stacks)

        if self._ascendancy == 'Ritualist' and 'gain_devotion_faithless_on_cast' in ability.tags:
            fx = ability.effects.get('self', {}).get('gain_devotion_faithless', {})
            for _ in range(fx.get('stacks', 0)):
                self.gainDevotion()
                self.gainFaithless()

        if self._ascendancy == 'Anarchist' and 'gain_volatility_on_cast' in ability.tags:
            fx = ability.effects.get('self', {}).get('gain_volatility', {})
            self.volatility = min(self.maxVolatility, self.volatility + fx.get('amount', 0))

    def onKill(self, entity, attackData, combatManager=None):
        super().onKill()
        if self._ascendancy == 'Anarchist':
            self.volatility = min(self.maxVolatility, self.volatility + 15)

        elif self._ascendancy == 'Desecrator' and entity:
            heal = int(self._maxHealth * (0.005 * entity.ruin))
            iGain = entity.ruin
            self.heal(heal, reason="Desecrator (Ruin stacks on Kill)")
            self.insanity = min(self.maxInsanity, self.insanity + iGain)

        elif self._ascendancy == 'Harbinger' and combatManager:
            if entity.corruption >= 5 and len(combatManager.allAlive) > 0:
                aoeDamage = int(entity._maxHealth * 0.1)
                for e in combatManager.allAlive:
                    e.damage(aoeDamage, 'chaos')

        # generic ability.effects.onKill processing - available to any Cultist ability
        ability = attackData.get('ability') if attackData else None
        onKillFx = ability.effects.get('onKill', {}) if ability else {}
        if onKillFx:
            healPct = onKillFx.get('heal', {}).get('percent', 0)
            if healPct:
                heal = int(self._maxHealth * healPct)
                self.heal(heal, reason=ability.name)
                console.print(f"[class_cultist]{ability.name} claims its due! Healed {heal} HP.[/class_cultist]")

            shiftAmount = onKillFx.get('insanity_shift', {}).get('amount', 0)
            if shiftAmount:
                self._shiftInsanity('flat', shiftAmount)
                console.print(f"[class_cultist]{ability.name} shifts Insanity by {shiftAmount:+}. Current Insanity: {self.insanity}[/class_cultist]")

        return {}

    def onBeforeDamage(self, ability, damage, damageType, targets, combatManager):
        if self._ascendancy == 'Harbinger' and self.insanity >= self.maxInsanity - 2:
            self._queueEffect(Effects.createCurse(2))

        elif self._ascendancy == 'Anarchist':
            if self.volatility == self.maxVolatility and self.insanity > 0:
                if combatManager.allAlive:
                    aoeDamage = int(self._maxHealth * (0.01 * (self.insanity // 5)))
                    for e in combatManager.allAlive:
                        e.damage(aoeDamage, 'chaos')
                        combatManager.checkDead(e)
                self.volatility = 0
                self._randomiseInsanity(min=-10, max=30)

        return damage, damageType, targets

    def onAfterMitigation(self, attacker, finalDamage, damageType, evaded, armourDamagePrevented, esDamagePrevented, preMitigationDamage, combatManager):
        finalDamage = super().onAfterMitigation(attacker, finalDamage, damageType, evaded, armourDamagePrevented, esDamagePrevented, preMitigationDamage, combatManager)
        if self._ascendancy == 'Harbinger':
            if attacker.corruption > 0 and self.insanity < 0:
                attacker.corruption -= 1
                console.print(f"  [chaos]You were attacked while your Insanity is negative! {attacker._name} is cleansed of 1 Corruption.[/chaos]")
        return finalDamage

    def onAttack(self, damageDealt, damageType, target, combatManager, ability, crit):
        damageDealt, damageType = super().onAttack(damageDealt, damageType, target, combatManager, ability, crit)

        targetEntity = target.entity if target else None

        if ability and targetEntity:
            if self._ascendancy == 'Umbralist' and 'consumes_shadow_early' in ability.tags and self.shadow > 0:
                fx = ability.effects.get('self', {}).get('consume_shadow', {})
                dmgPerStack = fx.get('damage_per_stack', 0) / 100
                stacksConsumed = self.shadow
                self.shadow = 0
                self._logDamage(f"{ability.name} consumes {stacksConsumed} Shadow (Umbralist)", percent=dmgPerStack * stacksConsumed)
                damageDealt = int(damageDealt * (1 + (dmgPerStack * stacksConsumed)))
                console.print(f"[asc_umbralist]Umbralist: {ability.name} consumes {stacksConsumed} Shadow for +{int(dmgPerStack * stacksConsumed * 100)}% Damage.[/asc_umbralist]")

            if self._ascendancy == 'Harbinger':
                if 'bonus_corruption_on_hit' in ability.tags:
                    fx = ability.effects.get('target', {}).get('corruption', {})
                    stacks = fx.get('stacks', 0)
                    if stacks > 0:
                        gained = min(stacks, 10 - targetEntity.corruption)
                        targetEntity.corruption += gained
                        console.print(f"[asc_harbinger]Harbinger: {ability.name} applies {gained} Corruption to {targetEntity._name}.[/asc_harbinger]")

                if 'consumes_target_corruption' in ability.tags and targetEntity.corruption > 0:
                    fx = ability.effects.get('self', {}).get('consume_target_corruption', {})
                    dmgPerStack = fx.get('damage_per_stack', 0)
                    stacksConsumed = targetEntity.corruption
                    targetEntity.corruption = 0
                    bonus = dmgPerStack * stacksConsumed
                    self._logDamage(f"{ability.name} consumes {stacksConsumed} Corruption (Harbinger)", flat=bonus)
                    damageDealt += bonus
                    console.print(f"[asc_harbinger]Harbinger: {ability.name} consumes {stacksConsumed} Corruption for +{bonus} Damage.[/asc_harbinger]")

            if self._ascendancy == 'Doomsayer' and 'consumes_omen_heresy_for_damage' in ability.tags and (self.omen > 0 or self.heresy > 0):
                fx = ability.effects.get('self', {}).get('consume_omen_heresy', {})
                dmgPerStack = fx.get('damage_per_stack', 0) / 100
                stacksConsumed = self.omen + self.heresy
                self.omen = 0
                self.heresy = 0
                self._logDamage(f"{ability.name} consumes {stacksConsumed} Omen/Heresy (Doomsayer)", percent=dmgPerStack * stacksConsumed)
                damageDealt = int(damageDealt * (1 + (dmgPerStack * stacksConsumed)))
                console.print(f"[asc_doomsayer]Doomsayer: {ability.name} consumes {stacksConsumed} Omen/Heresy for +{int(dmgPerStack * stacksConsumed * 100)}% Damage.[/asc_doomsayer]")

            if self._ascendancy == 'Ritualist' and 'consumes_devotion_faithless_for_damage' in ability.tags and (self.devotion > 0 or self.faithless > 0):
                fx = ability.effects.get('self', {}).get('consume_devotion_faithless', {})
                dmgPerStack = fx.get('damage_per_stack', 0) / 100
                stacksConsumed = self.devotion + self.faithless
                if self.devotion == 5:
                    self._stats['Temporary']['crit_chance'] -= 0.1
                if self.faithless == 10:
                    self._stats['Temporary']['crit_multi'] -= 0.8
                self._stats['Temporary']['lifesteal'] -= 8 * self.devotion
                self._stats['Temporary']['hp_regen'] -= 10 * self.faithless
                self.devotion = 0
                self.faithless = 0
                self._logDamage(f"{ability.name} consumes {stacksConsumed} Devotion/Faithless (Ritualist)", percent=dmgPerStack * stacksConsumed)
                damageDealt = int(damageDealt * (1 + (dmgPerStack * stacksConsumed)))
                console.print(f"[asc_ritualist]Ritualist: {ability.name} consumes {stacksConsumed} Devotion/Faithless for +{int(dmgPerStack * stacksConsumed * 100)}% Damage.[/asc_ritualist]")

            if self._ascendancy == 'Anarchist' and 'consumes_volatility_for_damage' in ability.tags and self.volatility > 0:
                fx = ability.effects.get('self', {}).get('consume_volatility', {})
                dmgPerPoint = fx.get('damage_per_point', 0) / 100
                stacksConsumed = self.volatility
                self.volatility = 0
                self._logDamage(f"{ability.name} consumes {stacksConsumed} Volatility (Anarchist)", percent=dmgPerPoint * stacksConsumed)
                damageDealt = int(damageDealt * (1 + (dmgPerPoint * stacksConsumed)))
                console.print(f"[asc_anarchist]Anarchist: {ability.name} consumes {stacksConsumed} Volatility for +{int(dmgPerPoint * stacksConsumed * 100)}% Damage.[/asc_anarchist]")

            if self._ascendancy == 'Desecrator':
                if 'bonus_ruin_on_hit' in ability.tags:
                    fx = ability.effects.get('target', {}).get('ruin', {})
                    stacks = fx.get('stacks', 0)
                    if stacks > 0:
                        targetEntity.ruin += stacks
                        console.print(f"[asc_desecrator]Desecrator: {ability.name} applies {stacks} Ruin to {targetEntity._name}.[/asc_desecrator]")

                if 'consumes_target_ruin' in ability.tags and targetEntity.ruin > 0:
                    fx = ability.effects.get('self', {}).get('consume_target_ruin', {})
                    dmgPerStack = fx.get('damage_per_stack', 0)
                    stacksConsumed = targetEntity.ruin
                    targetEntity.ruin = 0
                    bonus = dmgPerStack * stacksConsumed
                    self._logDamage(f"{ability.name} consumes {stacksConsumed} Ruin (Desecrator)", flat=bonus)
                    damageDealt += bonus
                    console.print(f"[asc_desecrator]Desecrator: {ability.name} consumes {stacksConsumed} Ruin for +{bonus} Damage.[/asc_desecrator]")

        if self.absorbedToAdd > 0:
            self._logDamage("Absorbed Damage retained from previous hit", flat=self.absorbedToAdd)
            damageDealt += self.absorbedToAdd
            self.absorbedToAdd = 0

        if self.insanity >= self.maxInsanity - 2:
            extremeBonus = self._stats['Bonuses'].get('insanity_extreme_effect_increased', 0) / 100
            extremeMulti = 2 + extremeBonus
            self._logDamage("Insanity at Maximum", percent=extremeMulti - 1)
            damageDealt = int(damageDealt * extremeMulti)
            selfDamagePercent = 0.1 * (1 - self._stats['Bonuses'].get('insanity_penalty_reduction', 0) / 100)
            selfDamage = int(damageDealt * selfDamagePercent)

            if self._ascendancy == 'Doomsayer':
                selfDamage //= 2 #5%

            self.damage(selfDamage, 'chaos', lethal=False)
            self._randomiseInsanity(max = -1)

        elif -1 <= self.insanity <= 1:
            self._logDamage("Insanity at 0", percent=0.75)
            damageDealt = int(damageDealt * 1.75)
            self._randomiseInsanity()

        elif self.insanity > 0:
            bonus = 1 + (0.02 * self.insanity)
            self._logDamage(f"Positive Insanity ({self.insanity})", percent=0.02 * self.insanity)
            damageDealt = int(damageDealt * bonus)

        if self._ascendancy == 'Umbralist' and self.shadow > 0 and damageType == 'chaos':
            self._logDamage(f"Shadow ({self.shadow} stacks) (Umbralist)", percent=self.shadow * 0.03)
            damageDealt = int(damageDealt * (1 + (self.shadow * 0.03)))
            if self.shadow == 10:
                damageType = 'true'
                self.shadow = 0
                heal = int(damageDealt * 0.1)
                self.heal(heal, reason="Umbralist (Max Shadow Lifesteal)")

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
                self._logDamage(f"Omen ({self.omen} stacks) (Doomsayer)", percent=self.omen * 0.02)
                damageDealt = int(damageDealt * bonus)

        elif self._ascendancy == 'Ritualist':
            if damageType == 'chaos':
                bonus = 1 + (self.devotion * 0.08)
                self._logDamage(f"Devotion ({self.devotion} stacks) (Ritualist)", percent=self.devotion * 0.08)
                damageDealt = int(damageDealt * bonus)

            if self.insanity >= 50:
                self.gainDevotion()

        elif self._ascendancy == 'Anarchist':
            volatilityStacks = self.volatility // 25
            if volatilityStacks:
                self._logDamage(f"Volatility ({self.volatility}) (Anarchist)", percent=0.1 * volatilityStacks)
                damageDealt = int(damageDealt * (1 + (0.1 * volatilityStacks)))

            if self.volatility < self.maxVolatility:
                vGain = damageDealt // 10
                self.volatility = min(self.maxVolatility, self.volatility + vGain)

            elif self.volatility == self.maxVolatility:
                if -1 <= self.insanity <= 1:
                    self.insanity = random.choice([self.minInsanity, self.maxInsanity])
                    damage = int(self._maxHealth * 0.05)
                    self.damage(damage, 'true', lethal=False)
                    if damageType == 'chaos':
                        self._logDamage("Neutral Discharge (Anarchist)", percent=0.75)
                        damageDealt = int(damageDealt * 1.75)
                elif self.insanity > 0:
                    pass # > 0 handled in combat
                elif self.insanity < 0:
                    heal = int(self._damage * abs(self.insanity) * 0.01)
                    self.heal(heal, reason="Anarchist (Negative Discharge)")
                    self._shield += heal
                    self._randomiseInsanity(min=-30, max=10)
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
        damageTaken, damageType = super().onHit(damageTaken, damageType, isCrit, attacker, combatManager)

        if self.combatStart: # dont apply insanity effects before player's first turn
            return damageTaken, damageType

        if self.insanity <= self.minInsanity + 2:
            extremeBonus = self._stats['Bonuses'].get('insanity_extreme_effect_increased', 0) / 100
            self.absorbedToAdd += int(damageTaken * (0.25 + extremeBonus))

            if self._ascendancy == 'Umbralist':
                self.absorbedToAdd *= 2

            elif self._ascendancy == 'Harbinger':
                self.heal(int(damageTaken * 0.25), reason="Harbinger (25% of Damage Taken at Minimum Insanity)")

            if attacker:
                attacker._logDamage(f"{self._name}'s Insanity at Minimum", percent=-1.0)
            self._randomiseInsanity(min = 1)
            damageTaken = 0

        elif -1 <= self.insanity <= 1:
            if attacker:
                attacker._logDamage(f"{self._name}'s Insanity at 0", percent=-0.35)
            damageTaken = int(damageTaken * 0.65)

            if self._ascendancy == 'Desecrator' and attacker and attacker.ruin > 0:
                damage = int(attacker._maxHealth * (0.03 * attacker.ruin))
                attacker.damage(damage, 'true')

        elif self.insanity < 0:
            dr = abs(self.insanity) // 5 * 0.01
            if attacker and dr:
                attacker._logDamage(f"{self._name}'s Insanity below 0 (Stable)", percent=-dr)
            damageTaken = int(damageTaken * (1 - dr))

            if self._ascendancy == 'Desecrator' and attacker:
                if attacker.tainted or attacker.desecrated:
                    absorb = int(0.01 * damageTaken * (abs(self.insanity) // 5))
                    if absorb:
                        attacker._logDamage(f"{self._name}'s Desecrator Absorb (Tainted/Desecrated attacker)", flat=-absorb)
                    self.absorbedToAdd += absorb
                    damageTaken -= absorb

        if self._ascendancy == 'Umbralist' and self.shadow > 0:
            if attacker:
                attacker._logDamage(f"{self._name}'s Shadow ({self.shadow} stacks) (Umbralist)", percent=-(self.shadow * 0.01))
            damageTaken = int(damageTaken * (1 - (self.shadow * 0.01)))

        elif self._ascendancy == 'Doomsayer':
            bonus = 1 + (self.omen * 0.02) + (self.heresy * 0.01)
            if attacker:
                attacker._logDamage(f"{self._name}'s Omen/Heresy (Doomsayer)", percent=bonus - 1)
            damageTaken = int(damageTaken * bonus)

        elif self._ascendancy == 'Ritualist':
            dr = self.faithless * 0.02
            if attacker and dr:
                attacker._logDamage(f"{self._name}'s Faithless ({self.faithless} stacks) (Ritualist)", percent=-dr)
            damageTaken = int(damageTaken * (1 - dr))

            if self.insanity <= -50:
                self.gainFaithless()

        elif self._ascendancy == 'Anarchist':
            volatilityStacks = self.volatility // 25
            if volatilityStacks:
                if attacker:
                    attacker._logDamage(f"{self._name}'s Volatility ({self.volatility}) (Anarchist)", percent=0.05 * volatilityStacks)
                damageTaken = int(damageTaken * (1 + (0.05 * volatilityStacks)))

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
            swingBonus = self._stats['Bonuses'].get('insanity_swing_increased', 0) / 100
            if swingBonus:
                if effect == 'flat':
                    val = int(val * (1 + swingBonus))
                elif effect == 'multiply':
                    val = val * (1 - swingBonus) if val < 1 else val * (1 + swingBonus)
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
                self._stats['Temporary']['ailment_avoidance'] -= 40
            self.elevated = False
            if random.random() < 0.2 and combatManager:
                bleed = Effects.createBleed()[0]
                combatManager.addStatusEffect(self, bleed, self)
            self._ritualSacrifice()

        super().onTurnStart(combatManager)

    def onCombatEnd(self):
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

        super().onCombatEnd()

    ASCENDANCY_DELTAS = {
        'Umbralist': {
            '_baseHealth': 40,
            '_baseDamage': 0,
            '_baseSpeed': -0.1,
            'minInsanity': -20,
            'maxInsanity': -15,
            '_stats.Permanent.chaos': 10,
            '_stats.Permanent.damage_reduction': 5,
        },
        'Harbinger': {
            '_baseHealth': -5,
            '_baseDamage': 10,
            '_baseSpeed': 0.05,
            'minInsanity': 10,
            'maxInsanity': 10,
            '_stats.Permanent.dark': 10,
            '_stats.Permanent.ailment_avoidance': 15,
        },
        'Doomsayer': {
            '_baseHealth': 40,
            '_baseDamage': 2,
            '_baseSpeed': -0.1,
            '_stats.Permanent.crit_multi': 0.25,
        },
        'Ritualist': {
            '_baseHealth': -10,
            '_baseDamage': 10,
            '_baseSpeed': 0.1,
            'minInsanity': -15,
            'maxInsanity': 15,
            '_stats.Permanent.lifesteal': 5,
            '_stats.Permanent.physical': -10,
            '_stats.Permanent.dark': 10,
        },
        'Anarchist': {
            '_baseHealth': -10,
            '_baseDamage': -6,
            '_baseSpeed': 0.25,
            'minInsanity': 10,
            'maxInsanity': 20,
            '_stats.Permanent.chaos': 15,
            '_stats.Permanent.crit_chance': 0.08,
            '_stats.Permanent.crit_multi': 0.4,
            '_stats.Permanent.lifesteal': 5,
        },
        'Desecrator': {
            '_baseHealth': -10,
            '_baseDamage': 10,
            '_baseSpeed': -0.05,
            '_stats.Permanent.otherworld': -5,
            '_stats.Permanent.dark': 15,
            '_stats.Permanent.resistance_penetration': 15,
            '_stats.Permanent.chaos': 10,
        },
    }

    def _removeOldAscendancy(self) -> bool:
        delta = self.ASCENDANCY_DELTAS.get(self._ascendancy)
        if delta:
            self._applyStatDelta(delta, sign=-1)
        return True

    def updateAscendancy(self, ascendancy):
        if not super().updateAscendancy(ascendancy):
            return
        self._ascendancy = ascendancy
        self.ascendancyDescription = CULTIST_DESCRIPTIONS[ascendancy]
        self._applyStatDelta(self.ASCENDANCY_DELTAS[ascendancy], sign=1)
        self._recalculateStats()
        self.gainClassAbilities(True)
        return True
