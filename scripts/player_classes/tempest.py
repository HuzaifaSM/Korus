from .base import Player
from scripts.styles import console

TEMPEST_DESCRIPTIONS = {
    "Tempest": "[class_tempest]A flurry of energy, striking before its prey can react.[/class_tempest]\n"
        "- If you have more Speed than an enemy, gain +0.25% Crit Chance and +1% Crit Damage per 0.01 Speed you have more than them.\n"
        "- If you have less Speed than an enemy, gain +0.25 Damage and +1% Increased Damage per 0.01 Speed you have less than them.\n"
        "- Abilities that damage multiple enemies will factor speed based off the first enemy only.\n"
        "- When an enemy with less Speed than you attacks you, gain 1 Static. When an enemy with more Speed than you attacks you, gain 1 Flow. Gain twice as much Static and Flow when only 1 enemy is alive.\n"
        "- Static: +2 Damage Reduction, -0.02 Speed. Max 10 Static stacks. Flow: +5% Increased Damage, +0.02 Speed. Max 10 Flow stacks.\n"
        "- If you have 10 or more combined Static and Flow stacks, your next attack Unleashes: 100% Increased Lightning Damage, +5% Lifesteal, and evenly consumes a total of 10 Static and Flow stacks.\n"
        "- At the end of combat, heal 1% Max HP for every critical hit you dealt, to a maximum heal of 30%.\n"
        "[bold]Starting Stats:[/bold] 40 HP | 5 Damage | 8% Crit Chance | 140% Crit Damage | Lightning Damage | 1 Speed.",
    # ascendancies
    "Alternator": "[lore]Everything changes. The storm has no favourites. Lethal or devastating, it matters not.[/lore]"
        "- At the start of your turn, the bonuses for speed differences are flipped.\n"
        "- For each consecutive critical hit, gain 1 stack of Positive, to a maximum of 5. For each consecutive non-critical hit, gain 1 stack of Negative, to a maximum of 5.\n"
        "- Positive: +2% Crit Chance, +20% Crit Damage, 4% Less Defenses. Negative: +15% Increased Damage, +1% Lifesteal, 2% Increased Defenses.\n"
        "- Whenever you lose Positive, you next attack gains 40% Increased Lightning Damage. Whenever you lose Negative, your next attack gains +20 Damage and heals for 10% of the damage dealt.\n"
        "[bold]Stat Changes:[/bold] +20 HP. +6 Damage. +50% Crit Multi. +20% Lightning Resistance. -10% Earth Resistance.",
    "Dervish": "[lore]You cannot strike what never stays still. You cannot corner the wind. Flow through them. Lure them into the dance of death.[/lore]"
        "- Convert 100% of your Armour into Evasion. Whenever you Evade an attack, gain 1 stack of Fleeting, to a maximum of 10.\n"
        "- Fleeting: +0.1 Speed, 10% Increased Lightning Damage. Whenever you deal a critical hit, consume all Fleeting to: Heal 3% Max HP and gain +10% Crit Damage per Fleeting consumed.\n"
        "- Static no longer grants Damage Reduction, and instead grants +2% Evasion per stack. Flow no longer grants Speed, and instead grants +1% Crit Chance per stack.\n"
        "- Unleash only deals 50% Increased Lightning Damage, but only needs 5 combined Static and Flow stacks to activate. Whenever you Unleash, gain 30% Increased Evasion until the start of your next turn.\n"
        "[bold]Stat Changes:[/bold] -20 HP. +5 Damage. +0.1 Speed. +75 Evasion. +15% Psychic Resistance.",
    "Ravager": "[lore]Faster. Again. Again. Never strike twice, they die too fast for that. Tear it all down, then continue on.[/lore]"
        "- Bonuses for having more Speed than your target are doubled. Whenever you critically hit an opponent, gain 1 Flurry, to a maximum of 5.\n"
        "- Flurry: +3% Multihit Chance, +3% Crit Chance. Whenever you trigger a Multihit, gain 1 Relentless, to a maximum of 3.\n"
        "- Relentless: 25% Increased Lightning Damage, +0.1 Speed, 10% Reduced Defenses.\n"
        "- Static can no longer be used to Unleash. Unleash when you have 3 stacks of Flow. Unleash now grants: +75% Crit Damage, +10% Lifesteal, +10% Resistance Penetration.\n"
        "- Static also grants 2% Increased Defenses per stack. Static no longer reduces Speed per stack.\n"
        "[bold]Stat Changes:[/bold] -5 HP. +3 Damage. +0.2 Speed. +10% Crit Chance. +50% Crit Damage.",
    "Archon": "[lore]The storm gathers. Evolves. Currents become sparks. Sparks become thunder. Thunder becomes the end.[/lore]"
        "- Upon gaining Static or Flow, gain 1 Current, to a maximum of 10. Current: 5% Increased Lightning Damage, -2% Earth Resistance, +1% Crit Chance.\n"
        "- Bonuses for having less Speed than your target are doubled. Whenever you critically hit an enemy that has more speed than you, gain 1 Spark, to a maximum of 5.\n"
        "- Spark: +5% Crit Chance, +10% Crit Damage, -0.05 Speed. Gain 1 more Flow whenever you gain Flow.\n"
        "- When you are attacked by an enemy with more Speed than you, lose 1 Static.\n"
        "- Whenever you Unleash, deal 10% of the damage dealt to all enemies as Lightning Damage and consume up to 5 Current Stacks to heal 2% Max HP per stack consumed.\n"
        "[bold]Stat Changes:[/bold] +25 HP. +4 Damage. -0.05 Speed. +20% Lightning Resistance. +30% Crit Damage.",
    "Mirage": "[lore]Shapeless. Senseless. Ruthless. They strike, only to find nothing but air. The flickering hastens, then all goes still.[/lore]"
        "- 75% of your Armour is converted to Evasion. 5% of your Armour is converted to Energy Shield.\n"
        "- Whenever you Evade an attack, gain 10% of your Maximum Energy Shield as bonus damage on your next attack.\n"
        "- If your Maximum Energy Shield is equal to more than half your Evasion, lose 0.3 Speed. If your Evasion is equal to more than 2.5x your Maximum Energy Shield, gain 0.3 Speed.\n"
        "- Gain Crit Chance equal to 1% of your Evasion, to a maximum of +25%. Gain Crit Damage equal to 2% of your Energy Shield, up to a maximum of +50%.\n"
        "- Whilst you have no Energy Shield: +10% Crit Chance, +0.2 Speed, 10% Increased Evasion for the rest of combat.\n"
        "- Static also grants 3% Increased Evasion per stack. Flow also grants 2% Maximum Energy Shield Regeneration.\n"
        "- Whenever you Evade an attack, gain 1 Flow. Whenever your Energy Shield fully blocks an attack, gain 1 Static.\n"
        "[bold]Stat Changes:[/bold] -20 HP. +7 Damage. +0.1 Speed. +75 Evasion. +20 Energy Shield. +5% Otherworld Resistance."
}

class Tempest(Player):
    def __init__(self, name, health=40, damage=5, damageType="lightning", speed=1):
        super().__init__(name, health, damage, 0.08, 1.4, damageType, speed, className="Tempest", classDescription=TEMPEST_DESCRIPTIONS["Tempest"])
        self.static = 0
        self.staticBuffs = {'damage_reduction': 2, 'speed': -0.02}
        self.flow = 0
        self.flowBuffs = {'increased_damage': 0.05, 'speed': 0.02}
        self.unleashActivatedLastTurn = False
        self.critHits = 0
        self._tempestCritBuff = None

        self.alternatorFlip = False # false = standard, true = inverted
        self.alternatorCrits = 0 # consecutive-hit streak counters, read by onCrit, updated by onAttack
        self.alternatorNonCrits = 0
        self.alternatorPositive = 0
        self.alternatorLostPositive = False
        self.alternatorNegative = 0
        self.alternatorLostNegative = False
        self.dervishFleeting = 0
        self.dervishCritGained = 0
        self.ravagerFlurry = 0
        self.ravagerRelentless = 0
        self.archonCurrent = 0
        self.archonSpark = 0
        self.mirageDamage = 0
        self.mirageEsLastTurn = False

    @property
    def unleashStacksNeeded(self) -> int:
        base = 3 if self._ascendancy == 'Ravager' else (5 if self._ascendancy == 'Dervish' else 10)
        reduction = self._stats['Bonuses'].get('unleash_cost_reduced', 0)
        return max(1, round(base * (1 - reduction / 100)))

    def gainStatic(self, amount: int = 1):
        amount += self._stats['Bonuses'].get('static_flow_gain_flat', 0)
        for _ in range(amount):
            if self.static < 10:
                self.static += 1
                for k, v in self.staticBuffs.items():
                    if k in self._stats['Temporary']:
                        self._stats['Temporary'][k] += v
                if self._ascendancy == 'Archon':
                    self.gainArchonCurrent()

    def loseStatic(self):
        if self.static > 0:
            self.static -= 1
            for k, v in self.staticBuffs.items():
                if k in self._stats['Temporary']:
                    self._stats['Temporary'][k] -= v

    def gainFlow(self, amount: int = 1):
        amount += self._stats['Bonuses'].get('static_flow_gain_flat', 0)
        for _ in range(amount):
            if self.flow < 10:
                self.flow += 1
                for k, v in self.flowBuffs.items():
                    if k in self._stats['Temporary']:
                        self._stats['Temporary'][k] += v
                if self._ascendancy == 'Archon':
                    self.gainArchonCurrent()

    def loseFlow(self):
        if self.flow > 0:
            self.flow -= 1
            for k, v in self.flowBuffs.items():
                if k in self._stats['Temporary']:
                    self._stats['Temporary'][k] -= v

    def _checkUnleash(self) -> bool:
        if self._ascendancy == 'Ravager':
            return self.flow >= self.unleashStacksNeeded
        else:
            return self.static + self.flow >= self.unleashStacksNeeded

    def consumeUnleashStacks(self):
        consumed = 0
        while consumed < self.unleashStacksNeeded and self.flow > 0 and self.static > 0:
            if self.static > 0 and not self._ascendancy == 'Ravager':
                self.static -= 1
                self.loseStatic()
                consumed += 1
            if self.flow > 0:
                self.flow -= 1
                self.loseFlow()
                consumed += 1
        self.unleashActivatedLastTurn = True

    def gainAlternatorPositive(self):
        if self.alternatorPositive < 5:
            self.alternatorPositive += 1
            self._stats['Temporary']['crit_chance'] += 0.02
            self._stats['Temporary']['crit_multi'] += 0.2
            self._stats['Temporary']['increased_defenses'] -= 4

    def loseAllAlternatorPositive(self):
        if self.alternatorPositive > 0:
            self._stats['Temporary']['crit_chance'] -= 0.02 * self.alternatorPositive
            self._stats['Temporary']['crit_multi'] -= 0.2 * self.alternatorPositive
            self._stats['Temporary']['increased_defenses'] += 4 * self.alternatorPositive
            self.alternatorPositive = 0
            self.alternatorLostPositive = True

    def gainAlternatorNegative(self):
        if self.alternatorNegative < 5:
            self.alternatorNegative += 1
            self._stats['Temporary']['lifesteal'] += 1
            self._stats['Temporary']['increased_defenses'] += 2

    def loseAllAlternatorNegative(self):
        if self.alternatorNegative > 0:
            self._stats['Temporary']['lifesteal'] -= 1 * self.alternatorNegative
            self._stats['Temporary']['increased_defenses'] -= 2 * self.alternatorNegative
            self.alternatorNegative = 0
            self.alternatorLostNegative = True

    def gainArchonCurrent(self):
        if self.archonCurrent < 10:
            self.archonCurrent += 1
            self._stats['Temporary']['earth'] -= 2
            self._stats['Temporary']['crit_chance'] += 0.01

    def consumeArchonCurrent(self):
        consumed = 0
        while consumed < 5 and self.archonCurrent > 0:
            self.archonCurrent -= 1
            consumed += 1
            self._stats['Temporary']['earth'] += 2
            self._stats['Temporary']['crit_chance'] -= 0.01
        heal = int(self._maxHealth * 0.02 * consumed)
        self.heal(heal, reason=f"Archon (Consumed {consumed} Current)")

    def gainArchonSpark(self):
        if self.archonSpark < 5:
            self.archonSpark += 1
            self._stats['Temporary']['crit_chance'] += 0.05
            self._stats['Temporary']['crit_multi'] += 0.1
            self._stats['Temporary']['speed'] -= 0.05

    def consumeArchonSpark(self) -> int:
        consumed = self.archonSpark
        if consumed > 0:
            self._stats['Temporary']['crit_chance'] -= 0.05 * consumed
            self._stats['Temporary']['crit_multi'] -= 0.1 * consumed
            self._stats['Temporary']['speed'] += 0.05 * consumed
            self.archonSpark = 0
        return consumed

    def gainRavagerFlurry(self):
        if self.ravagerFlurry < 5:
            self.ravagerFlurry += 1
            self._stats['Temporary']['chance_to_multihit'] += 3
            self._stats['Temporary']['crit_chance'] += 0.03

    def checkMirageEsBuff(self):
        if not self.mirageEsLastTurn and self.energyShield > 0:
            self._stats['Temporary']['crit_chance'] += 0.1
            self._stats['Temporary']['speed'] += 0.2
            self._stats['Temporary']['increased_evasion'] += 10
            self.mirageEsLastTurn = True
        elif self.mirageEsLastTurn and self.energyShield == 0:
            self._stats['Temporary']['crit_chance'] -= 0.1
            self._stats['Temporary']['speed'] -= 0.2
            self._stats['Temporary']['increased_evasion'] -= 10
            self.mirageEsLastTurn = False        

    def _recalculateStats(self, doPrint = True, inCombat = False):
        super()._recalculateStats(doPrint, inCombat)

        if self._ascendancy == 'Dervish':
            armour = self.armour
            self._stats['evasion'] += self.armour
            self._stats['armour'] = 0

            if doPrint:
                console.print(f"[asc_dervish]Dervish:[/asc_dervish] Converted 100% of Armour ({armour}) to Evasion.")

        elif self._ascendancy == 'Mirage':
            armourToEv = int(self.armour * 0.75)
            armourToEs = int(self.armour * 0.05)
            self._stats['armour'] -= (armourToEv + armourToEs)
            self._stats['evasion'] += armourToEv
            self._stats['max_energy_shield'] += armourToEs
            if not inCombat:
                self._stats['energy_shield'] += armourToEs

            if self.maxEnergyShield >= self.evasion / 2:
                self._speed -= 0.3
            elif self.evasion >= 2.5 * self.maxEnergyShield:
                self._speed += 0.3
            critChanceGain = min(0.25, round(self.evasion / 100, 3))
            critMultiGain = min(0.5, round(self.maxEnergyShield / 50, 3))
            self._stats['Bonuses']['crit_chance'] += critChanceGain
            self._stats['Bonuses']['crit_multi'] += critMultiGain

    def onEvade(self, combatManager):
        if self._ascendancy == 'Dervish':
            if self.dervishFleeting < 10:
                self.dervishFleeting += 1
                self._stats['Temporary']['speed'] += 0.1
        elif self._ascendancy == 'Mirage':
            self.mirageDamage += int(0.1 * self.maxEnergyShield)
            self.gainFlow()

    def onBeforeCritRoll(self, targetUnit, targets, combatManager):
        self._tempestCritBuff = None
        if targets and self._speed > targets[0]._speed and not self.alternatorFlip:
            difference = self._speed - targets[0]._speed
            buffChance = round(0.25 * difference, 4) + self._stats['Bonuses'].get('crit_chance_when_faster', 0) / 100
            buffMulti = round(difference, 4)
            if self._ascendancy == 'Ravager':
                buffChance *= 2
                buffMulti *= 2
                if self._checkUnleash():
                    buffMulti += 0.75
                    self._stats['Temporary']['lifesteal'] += 10
                    self._stats['Temporary']['resistance_penetration'] += 10
                    self.consumeUnleashStacks()
            self._stats['Temporary']['crit_chance'] += buffChance
            self._stats['Temporary']['crit_multi'] += buffMulti
            self._tempestCritBuff = (buffChance, buffMulti)

        if self._ascendancy == 'Dervish':
            self.dervishCritGained = 0.01 * self.flow
            self._stats['Temporary']['crit_chance'] += self.dervishCritGained

    def onAfterCritRoll(self, targetUnit, targets, combatManager):
        if self._tempestCritBuff:
            buffChance, buffMulti = self._tempestCritBuff
            self._stats['Temporary']['crit_chance'] -= buffChance
            self._stats['Temporary']['crit_multi'] -= buffMulti
            self._tempestCritBuff = None

        if self._ascendancy == 'Dervish':
            self._stats['Temporary']['crit_chance'] -= self.dervishCritGained

    def onCrit(self, targets, combatManager, critDamage):
        self.critHits += 1

        if self._ascendancy == 'Alternator':
            if self.alternatorCrits > 0:
                self.gainAlternatorPositive()
                self.loseAllAlternatorNegative()
            elif self.alternatorNonCrits > 0:
                self.gainAlternatorNegative()
                self.loseAllAlternatorPositive()
        
        elif self._ascendancy == 'Dervish' and self.dervishFleeting > 0:
            heal = int(self._maxHealth * 0.03 * self.dervishFleeting)
            self.heal(heal, reason=f"Fleeting ({self.dervishFleeting} stacks, Dervish)")
            console.print(f"[asc_dervish]Dervish: Consuming {self.dervishFleeting} Fleeting grants +{10 * self.dervishFleeting}% Critical Damage![/asc_dervish]")
            critDamage = int(critDamage * (1 + (0.1 * self.dervishFleeting)))
            self._stats['Temporary']['speed'] -= 0.1 * self.dervishFleeting
            self.dervishFleeting = 0

        elif self._ascendancy == 'Ravager':
            self.gainRavagerFlurry()

        elif self._ascendancy == 'Archon':
            t = targets[0]
            if self._speed < t._speed:
                self.gainArchonSpark()

        return critDamage

    def onMultihitActivated(self):
        if self._ascendancy == 'Ravager':
            if self.ravagerRelentless < 3:
                self.ravagerRelentless += 1
                self._stats['Temporary']['speed'] += 0.1
                self._stats['Temporary']['increased_defenses'] -= 10

    def onAfterMitigation(self, attacker, finalDamage, damageType, evaded, armourDamagePrevented, esDamagePrevented, preMitigationDamage, combatManager):
        finalDamage = super().onAfterMitigation(attacker, finalDamage, damageType, evaded, armourDamagePrevented, esDamagePrevented, preMitigationDamage, combatManager)
        if attacker._speed < self._speed:
            if len(combatManager.allAlive) == 1:
                self.gainStatic()
            self.gainStatic()
        elif attacker._speed > self._speed:
            if len(combatManager.allAlive) == 1:
                self.gainFlow()
            self.gainFlow()
            if self._ascendancy == 'Archon':
                self.gainFlow()
                self.loseStatic()

        if self._ascendancy == 'Mirage' and esDamagePrevented > 0 and finalDamage == 0:
            self.gainStatic()

        return finalDamage

    def onAbilityCast(self, ability, combatManager):
        super().onAbilityCast(ability, combatManager)
        if not ability:
            return

        if self._ascendancy == 'Alternator' and 'manual_flip' in ability.tags:
            self.alternatorFlip = not self.alternatorFlip
            console.print(f"[asc_alternator]Alternator: {ability.name} flips the storm's favour![/asc_alternator]")

        if self._ascendancy == 'Dervish' and 'gain_fleeting_on_cast' in ability.tags:
            fx = ability.effects.get('self', {}).get('gain_fleeting', {})
            stacks = fx.get('stacks', 0)
            gained = 0
            for _ in range(stacks):
                if self.dervishFleeting < 10:
                    self.dervishFleeting += 1
                    self._stats['Temporary']['speed'] += 0.1
                    gained += 1
            if gained > 0:
                console.print(f"[asc_dervish]Dervish: {ability.name} grants {gained} stack(s) of Fleeting.[/asc_dervish]")

        if self._ascendancy == 'Ravager' and 'gain_flurry_on_cast' in ability.tags:
            fx = ability.effects.get('self', {}).get('gain_flurry', {})
            stacks = fx.get('stacks', 0)
            for _ in range(stacks):
                self.gainRavagerFlurry()
            if stacks > 0:
                console.print(f"[asc_ravager]Ravager: {ability.name} grants {stacks} stack(s) of Flurry.[/asc_ravager]")

        if self._ascendancy == 'Mirage' and 'gain_mirage_damage_on_cast' in ability.tags:
            fx = ability.effects.get('self', {}).get('gain_mirage_damage', {})
            pct = fx.get('percent_max_es', 0) / 100
            gained = int(self.maxEnergyShield * pct)
            if gained > 0:
                self.mirageDamage += gained
                console.print(f"[asc_mirage]Mirage: {ability.name} adds {gained} to your stored damage.[/asc_mirage]")

    def onKill(self, entity, attackData, combatManager=None):
        super().onKill()
        ability = attackData.get('ability') if attackData else None
        onKillFx = ability.effects.get('on_kill', {}) if ability else {}
        if onKillFx:
            healPct = onKillFx.get('heal_percent_max_hp', 0)
            if healPct:
                heal = int(self._maxHealth * healPct / 100)
                self.heal(heal, False)
                console.print(f"[class_tempest]{ability.name} claims its due! Healed {heal} HP.[/class_tempest]")
        return {}

    def onAttack(self, damageDealt, damageType, target, combatManager, ability, crit):
        damageDealt, damageType = super().onAttack(damageDealt, damageType, target, combatManager, ability, crit)

        targetEntity = target.entity if target else None

        if ability and targetEntity:
            if self._ascendancy == 'Alternator' and 'consumes_alternator_stacks' in ability.tags and (self.alternatorPositive > 0 or self.alternatorNegative > 0):
                fx = ability.effects.get('self', {}).get('consume_alternator', {})
                dmgPerStack = fx.get('damage_per_stack', 0)
                stacksConsumed = self.alternatorPositive + self.alternatorNegative
                self.loseAllAlternatorPositive()
                self.loseAllAlternatorNegative()
                bonus = dmgPerStack * stacksConsumed
                self._logDamage(f"Consumed {stacksConsumed} Alternator Stacks", flat=bonus)
                damageDealt += bonus
                console.print(f"[asc_alternator]Alternator: {ability.name} consumes {stacksConsumed} stack(s) for +{bonus} Damage.[/asc_alternator]")

            if self._ascendancy == 'Dervish' and 'consumes_fleeting_bonus_damage' in ability.tags and self.dervishFleeting > 0:
                fx = ability.effects.get('self', {}).get('consume_fleeting', {})
                dmgPerStack = fx.get('damage_per_stack', 0)
                stacksConsumed = self.dervishFleeting
                self._stats['Temporary']['speed'] -= 0.1 * stacksConsumed
                self.dervishFleeting = 0
                bonus = dmgPerStack * stacksConsumed
                self._logDamage(f"Consumed {stacksConsumed} Fleeting (Dervish)", flat=bonus)
                damageDealt += bonus
                console.print(f"[asc_dervish]Dervish: {ability.name} consumes {stacksConsumed} Fleeting for +{bonus} Damage.[/asc_dervish]")

            if self._ascendancy == 'Ravager' and 'consumes_relentless' in ability.tags and self.ravagerRelentless > 0:
                fx = ability.effects.get('self', {}).get('consume_relentless', {})
                dmgPerStack = fx.get('damage_per_stack', 0) / 100
                stacksConsumed = self.ravagerRelentless
                self._stats['Temporary']['speed'] -= 0.1 * stacksConsumed
                self._stats['Temporary']['increased_defenses'] += 10 * stacksConsumed
                self.ravagerRelentless = 0
                self._logDamage(f"Consumed {stacksConsumed} Relentless (Ravager)", percent=dmgPerStack * stacksConsumed)
                damageDealt = int(damageDealt * (1 + (dmgPerStack * stacksConsumed)))
                console.print(f"[asc_ravager]Ravager: {ability.name} consumes {stacksConsumed} Relentless for +{int(dmgPerStack * stacksConsumed * 100)}% Damage.[/asc_ravager]")

            if self._ascendancy == 'Archon' and 'consumes_current_for_damage' in ability.tags and self.archonCurrent > 0:
                fx = ability.effects.get('self', {}).get('consume_current', {})
                dmgPerStack = fx.get('damage_per_stack', 0)
                maxStacks = fx.get('max_stacks', 0)
                stacksConsumed = min(maxStacks, self.archonCurrent)
                self.archonCurrent -= stacksConsumed
                self._stats['Temporary']['earth'] += 2 * stacksConsumed
                self._stats['Temporary']['crit_chance'] -= 0.01 * stacksConsumed
                bonus = dmgPerStack * stacksConsumed
                self._logDamage(f"Consumed {stacksConsumed} Current (Archon)", flat=bonus)
                damageDealt += bonus
                console.print(f"[asc_archon]Archon: {ability.name} consumes {stacksConsumed} Current for +{bonus} Damage.[/asc_archon]")

            if self._ascendancy == 'Archon' and 'consumes_spark_for_damage' in ability.tags and self.archonSpark > 0:
                fx = ability.effects.get('self', {}).get('consume_spark', {})
                dmgPerStack = fx.get('damage_per_stack', 0)
                stacksConsumed = self.consumeArchonSpark()
                bonus = dmgPerStack * stacksConsumed
                self._logDamage(f"Consumed {stacksConsumed} Spark (Archon)", flat=bonus)
                damageDealt += bonus
                console.print(f"[asc_archon]Archon: {ability.name} consumes {stacksConsumed} Spark for +{bonus} Damage.[/asc_archon]")

            if self._ascendancy == 'Mirage' and self.mirageDamage > 0:
                if 'consumes_mirage_damage_amplified' in ability.tags:
                    fx = ability.effects.get('self', {}).get('consume_mirage_damage', {})
                    mult = fx.get('multiplier_percent', 100) / 100
                    bonus = int(self.mirageDamage * mult)
                    self._logDamage("Stored Damage (Mirage, Amplified)", flat=bonus)
                    damageDealt += bonus
                    self.mirageDamage = 0
                    console.print(f"[asc_mirage]Mirage: {ability.name} shatters your stored damage for +{bonus}![/asc_mirage]")
                else:
                    self._logDamage("Stored Damage (Mirage)", flat=self.mirageDamage)
                    damageDealt += self.mirageDamage
                    self.mirageDamage = 0

        if self._ascendancy == 'Alternator':
            if crit:
                self.alternatorCrits += 1
                self.alternatorNonCrits = 0
            else:
                self.alternatorNonCrits += 1
                self.alternatorCrits = 0

        if self._ascendancy != 'Ravager': # unleash handled in crit for ravager
            if self._checkUnleash():
                if damageType == 'lightning':
                    if self._ascendancy == 'Dervish':
                        self._logDamage("Unleash (Dervish)", percent=0.5)
                        damageDealt = int(damageDealt * 1.5)
                        self._stats['Temporary']['increased_evasion'] += 30
                    else:
                        self._logDamage("Unleash", percent=1.0)
                        damageDealt *= 2
                self._stats['Temporary']['lifesteal'] += 5
                self.consumeUnleashStacks()

                if self._ascendancy == 'Archon':
                    aoeDamage = int(damageDealt * 0.1)
                    console.print(f"[asc_archon]Archon: Unleash discharges {aoeDamage} Lightning Damage to all enemies![/asc_archon]")
                    for e in combatManager.allAlive:
                        e.damage(aoeDamage, 'lightning')
                    self.consumeArchonCurrent()

        targetEnemy = target.entity
        if targetEnemy._speed > self._speed or self.alternatorFlip:
            difference = targetEnemy._speed - self._speed
            if self._ascendancy == 'Archon':
                difference *= 2
            flatBonus = (difference * 100) // 4
            percentBonus = difference / 100
            speedReason = "Speed Deficit (Alternator Flip)" if self.alternatorFlip and targetEnemy._speed <= self._speed else "Speed Deficit"
            self._logDamage(speedReason, flat=int(flatBonus), percent=percentBonus)
            damageDealt = int((damageDealt + flatBonus) * (1 + percentBonus))

        if ability:
            if self._speed > targetEnemy._speed and 'gain_flow_if_faster' in ability.tags:
                self.gainFlow()
                console.print(f"[class_tempest]Tempest: {ability.name} outpaces {targetEnemy._name} - gained 1 Flow![/class_tempest]")
            elif self._speed < targetEnemy._speed and 'gain_static_if_slower' in ability.tags:
                self.gainStatic()
                console.print(f"[class_tempest]Tempest: {ability.name} is outpaced by {targetEnemy._name} - gained 1 Static![/class_tempest]")

        if self.flow > 0 and 'increased_damage' in self.flowBuffs:
            self._logDamage("Flow", percent=0.05 * self.flow)
            damageDealt = int(damageDealt * (1 + (0.05 * self.flow)))

        if self._ascendancy == 'Alternator':
            if self.alternatorLostPositive and damageType == 'lightning':
                self._logDamage("Lost Positive (Alternator)", percent=0.4)
                damageDealt = int(damageDealt * 1.4)
                self.alternatorLostPositive = False
            elif self.alternatorLostNegative:
                self._logDamage("Lost Negative (Alternator)", flat=20)
                damageDealt += 20
                heal = int(damageDealt * 0.1)
                self.heal(heal, reason="Lost Negative (Alternator)")
                self.alternatorLostNegative = False
            if self.alternatorNegative > 0:
                self._logDamage(f"Negative ({self.alternatorNegative} stacks, Alternator)", percent=0.15 * self.alternatorNegative)
                damageDealt = int(damageDealt * (1 + (0.15 * self.alternatorNegative)))

        elif self._ascendancy == 'Dervish':
            if self.dervishFleeting > 0:
                self._logDamage(f"Fleeting ({self.dervishFleeting} stacks, Dervish)", percent=0.1 * self.dervishFleeting)
                damageDealt = int(damageDealt * (1 + (0.1 * self.dervishFleeting)))

        elif self._ascendancy == 'Archon' and damageType == 'lightning':
            self._logDamage(f"Current ({self.archonCurrent} stacks, Archon)", percent=0.05 * self.archonCurrent)
            damageDealt = int(damageDealt * (1 + (0.05 * self.archonCurrent)))

        elif self._ascendancy == 'Ravager' and self.ravagerRelentless > 0 and damageType == 'lightning':
            self._logDamage(f"Relentless ({self.ravagerRelentless} stacks, Ravager)", percent=0.25 * self.ravagerRelentless)
            damageDealt = int(damageDealt * (1 + (0.25 * self.ravagerRelentless)))

        return damageDealt, damageType

    def onTurnStart(self, combatManager=None):
        if self._ascendancy == 'Alternator':
            self.alternatorFlip = not self.alternatorFlip

        elif self._ascendancy == 'Mirage':
            self.checkMirageEsBuff()
            self._stats['energy_shield'] = min(self.maxEnergyShield, self.energyShield + int(0.02 * self.maxEnergyShield * self.flow))

        if self.unleashActivatedLastTurn:
            self._stats['Temporary']['lifesteal'] -= 5

            if self._ascendancy == 'Dervish':
                self._stats['Temporary']['increased_evasion'] -= 30

            elif self._ascendancy == 'Ravager':
                self._stats['Temporary']['lifesteal'] -= 5
                self._stats['Temporary']['resistance_penetration'] -= 10

        super().onTurnStart(combatManager)

    def onCombatEnd(self):
        critHeal = min(30, self.critHits) / 100
        heal = int(self._maxHealth * critHeal)
        self.heal(heal, False)
        console.print(f"[class_tempest]Tempest: You landed {self.critHits} critical hits this combat. Healed for {critHeal * 100:.0f}% Max HP ({heal})[/class_tempest]")

        self.static = 0
        self.flow = 0
        self.unleashActivatedLastTurn = False
        self.critHits = 0
        self._tempestCritBuff = None

        self.alternatorFlip = False
        self.alternatorCrits = 0
        self.alternatorNonCrits = 0
        self.alternatorPositive = 0
        self.alternatorLostPositive = False
        self.alternatorNegative = 0
        self.alternatorLostNegative = False
        self.dervishFleeting = 0
        self.dervishCritGained = 0
        self.ravagerFlurry = 0
        self.ravagerRelentless = 0
        self.archonCurrent = 0
        self.archonSpark = 0
        self.mirageDamage = 0
        self.mirageEsLastTurn = False

        super().onCombatEnd()

    ASCENDANCY_DELTAS = {
        'Alternator': {
            '_baseHealth': 20,
            '_baseDamage': 6,
            '_stats.Permanent.crit_multi': 0.5,
            '_stats.Permanent.lightning': 20,
            '_stats.Permanent.earth': -10,
        },
        'Dervish': {
            '_baseHealth': -20,
            '_baseDamage': 5,
            '_baseSpeed': 0.1,
            '_stats.Permanent.added_evasion': 75,
            '_stats.Permanent.psychic': 15,
        },
        'Ravager': {
            '_baseHealth': -5,
            '_baseDamage': 3,
            '_baseSpeed': 0.2,
            '_stats.Permanent.crit_chance': 0.1,
            '_stats.Permanent.crit_multi': 0.5,
        },
        'Archon': {
            '_baseHealth': 25,
            '_baseDamage': 4,
            '_baseSpeed': -0.05,
            '_stats.Permanent.lightning': 20,
            '_stats.Permanent.crit_multi': 0.3,
        },
        'Mirage': {
            '_baseHealth': -20,
            '_baseDamage': 7,
            '_baseSpeed': -0.1,
            '_stats.Permanent.added_evasion': 75,
            '_stats.Permanent.added_energy_shield': 20,
            '_stats.Permanent.otherworld': 5,
        },
    }

    def _removeOldAscendancy(self):
        self.staticBuffs = {'damage_reduction': 2, 'speed': -0.02}
        self.flowBuffs = {'increased_damage': 0.05, 'speed': 0.02}
        delta = self.ASCENDANCY_DELTAS.get(self._ascendancy)
        if delta:
            self._applyStatDelta(delta, sign=-1)
        return True

    def updateAscendancy(self, ascendancy):
        if not super().updateAscendancy(ascendancy):
            return
        self._ascendancy = ascendancy
        self.ascendancyDescription = TEMPEST_DESCRIPTIONS[ascendancy]
        self._applyStatDelta(self.ASCENDANCY_DELTAS[ascendancy], sign=1)
        if ascendancy == 'Dervish':
            self.staticBuffs.pop('damage_reduction')
            self.staticBuffs['increased_evasion'] = 2
            self.flowBuffs.pop('speed')
        elif ascendancy == 'Ravager':
            self.staticBuffs.pop('speed')
            self.staticBuffs['increased_defenses'] = 2
        elif ascendancy == 'Mirage':
            self.staticBuffs['increased_evasion'] = 3
        self._recalculateStats()
        self.gainClassAbilities(True)
        return True

...