from .base import Player
from scripts.styles import console
from scripts.abilities import Effects

DRUID_DESCRIPTIONS = {
    "Druid": "[class_druid]A warden of nature, shifting forms as combat demands in order to bring peace to the Surface.[/class_druid]"
        "- The Druid has two Forms they can swap between: Human and Beast. On level up, gain +5% Form Effect. Abilities will transform based on the Form they are used in.\n"
        "- Human Form: +2 HP Regen. +2 Stamina Regen. 5% Increased Defenses.\n"
        "- Beast Form: 10% Increased Earth Damage. +0.02 Speed.\n"
        "- Gain Verdance when attacking in Human Form. Gain Verdance when taking damage in Beast Form. Verdance has a maximum of 20 Stacks\n"
        "- Verdance: 10% Increased Form Effect. 5% Increased Earth Damage. +1 HP Regen.\n"
        "[bold]Starting Stats:[/bold] 55 HP | 5 Damage | 7.5% Crit Chance| 150% Crit Damage | Earth Damage| 0.95 Speed",
    #ascendanies
    "Heartwood": "[lore]Feel the embrace of the earth around you. Let it shelter you from all. Let your primal urges hasten their end. Feel your roots ground you. Making you immovable. Eternal.[/lore]"
        "- Upon switching to Human Form, gain 3 Root. Lose 1 Root at the start of your turn. If you lose all Root, evolve into Elderbark: Gain Thorns equal to your Level + Verdance at time of evolution and +3% Max HP Regeneration.\n"
        "- Elderbark lasts for 3 turns unless you switch to Beast Form. Elderbark counts as Human Form for abilities. Whilst Rootbound, Verdance grants 5% Increased Armour and +2 Damage Reduction, but no longer grants +1 HP Regen.\n"
        "- For every turn you start in Beast Form, gain 1 Loam. Gain Loam when attacked in Beast Form based on damage taken. Loam has a maximum of 10 Stacks.\n"
        "- Switching back into Human Form consumes all Loam. For every 5 Loam consumed, gain 1 less Root. For every Loam consumed: 5% Increased Earth Damage, +1% Crit Chance until you lose Elderbark Form.\n"
        "[bold]Stat Changes:[/bold] +15 HP. -2 Damage. -0.1 Speed. +50 Armour. +15% Elemental Resistance.",
    "Skinwalker": "[lore]Restraint. Patience. Reason. Virtues to others. To you, they are shackles. Break free of them, for they never held you. Tear them to ribbons, then protect your sanctity.[/lore]"
        "- For every turn you begin in Beast Form, gain 1 Ferocity, to a maximum of 10. Ferocity: +3% Crit Chance, +10% Crit Damage.\n"
        "- Verdance grants 5% Increased Ferocity Effect. At Maximum Ferocity, attacking an enemy below 30% Max HP is a guaranteed critical hit.\n"
        "- Upon dealing a critical hit, gain 1 Ferocity. Upon killing an enemy, consume up to 5 Ferocity to heal for 2% Max HP per stack consumed.\n"
        "- For every turn you begin in Human Form, gain Instinct. In Human Form, gain 1 Instinct per 2% cumulative Max HP Regenerated, and per Verdance generated. Instinct has a maximum of 10 Stacks.\n"
        "- Switching to Beast Form consumes all Instinct. For every 3 Instinct consumed, gain 1 Ferocity. For every Instinct consumed: +3 Damage Reduction, +2 HP Regen until you leave Beast Form.\n"
        "- Lose all Ferocity when switching to Human Form. Heal 2% Max HP per Ferocity consumed.\n"
        "[bold]Stat Changes:[/bold] -15 HP. +4 Damage. +0.1 Speed. +25% Crit Damage. +5% Crit Chance.",
    "Confluence": "[lore]Once, you were split in two. Through strength, and help from the wilds, you have become whole. March upon the ground, sundering those who distrupt the Surface. It is yours. It will not fall to corruption.[/lore]"
        "- Switch Form's cooldown is reduced by 1. Using Switch Form grants 1 Flux for the rest of combat.\n"
        "- Flux: 10% Increased Form Effect, +0.05 Speed.\n"
        "- Upon reaching 5 Flux, Switch Form is disabled for the rest of combat and you evolve into Confluence.\n"
        "- Confluence: +5% Max HP Regen, 25% Increased Defenses, 50% Increased Earth Damage, 15% Increased Damage Taken.\n"
        "- Confluence lasts for the rest of combat. 50% Increased Verdance Generation whilst in Confluence Form.\n"
        "- Upon being critically hit whilst in Confluence, the attacker loses 0.5% Max HP per Verdance you have.\n"
        "[bold]Stat Changes:[/bold] +10 HP. +1 Damage. +0.05 Speed. +5 Max Verdance. +10% Elemental Resistance.",
    "Wellspring": "[lore]Life shall never diminish. As long as the Surface exists, all shall heal with time. Give to it freely. It will feed you. As it blooms, your enemies shall be consumed and crushed.[/lore]"
        "- +15 to Max Verdance. Verdance grants +2 Damage Reduction instead of +1 HP Regen.\n"
        "- Gain Verdance equal to 10% of Health gained. Gain 2 Verdance at the start of your turn.\n"
        "- Whilst in Human Form, gain +50% Healing Magnitude. Whilst in Beast Form, gain -75% Healing Magnitude.\n"
        "- Whenever you gain Health in Beast Form, gain Damage for the rest of combat equal to Health gained. This Damage bonus only applies in Beast Form.\n"
        "- Using Switch Form whilst at 50% or more Verdance consumes all Verdance and evolves you into a Blooming version of your Form.\n"
        "- Blooming Forms have 50% Increased Effect and last until you swap Forms. Upon Evolving into a Blooming Form, all enemies take Earth Damage equal to 10% of your Max HP.\n"
        "- Convert 100% of your Energy Shield into Max Health. Whenever you break an enemy's Energy Shield, gain 1% Increased Form Effect per 5 Maximum Energy Shield they have.\n"
        "[bold]Stat Changes:[/bold] +15 HP. -0.05 Speed. +25% Healing Magnitude. +10 HP Regeneration.",
    "Numen": "[lore]They cannot comprehend the earth. They cannot percieve life. They cannot fathom the Plane of Truth. Within all things, peace awaits. Underneath everything, lies something that none will witness.[/lore]"
        "- Beast Form has 1% Increased Form Effect per 10 Armour you have. Human Form has 1% Increased Form Effect per 8 Maximum Energy Shield you have.\n"
        "- Whilst in Human Form, gain 10% of Armour as Maximum Energy Shield. Damage Prevented by Armour is Regenerated as Energy Shield.\n"
        "- Whilst in Beast Form, gain 20% of Maximum Energy Shield as Armour. Damage Mitigated by Energy Shield is gained as Damage until you leave Beast Form.\n"
        "- If you Prevent more than 50% of an incoming hit due to Armour and Energy Shield, gain Damage equal to 20% of the hit's Pre-Mitigation value.\n"
        "[bold]Stat Changes:[/bold] +15 HP. -0.1 Speed. +40 Armour. +40 Energy Shield.",
}

class Druid(Player): # balanced damage and speed, earth damage
    def __init__(self, name, health = 55, damage = 5, damageType = "earth", speed = 1.0):
        super().__init__(name, health, damage, 0.075, 1.5, damageType, speed, className = "Druid", classDescription=DRUID_DESCRIPTIONS['Druid'])
        self.verdance = 0
        self.maxVerdance = 20
        self.form = 'human'
        self.formEffect = 1.0

        # tracked so exactly what was applied can be removed again on the next recompute
        self.formBonuses = {
            'hp_regen': 0,
            'stamina_regen': 0,
            'increased_defenses': 0,
            'speed': 0,
            'healing_magnitude': 0,
        }
        self.formEarthDamage = 0 # % increased earth damage from Beast Form - applied manually in onAttack, not a generic stat
        self.verdanceHpRegen = 0
        self.verdanceArmour = 0
        self.verdanceDR = 0
        self.verdanceEarthDamage = 0 # % increased earth damage from Verdance - applied manually in onAttack

        # Heartwood
        self.root = 0
        self.elderbarkActive = False
        self.elderbarkTurns = 0
        self.elderbarkThorns = 0
        self.loam = 0
        self.maxLoam = 10
        self.heartwoodLoamEarthDamage = 0
        self.heartwoodLoamCritChance = 0

        # Skinwalker
        self.ferocity = 0
        self.maxFerocity = 10
        self.ferocityCritChance = 0
        self.ferocityCritMulti = 0
        self.instinct = 0
        self.maxInstinct = 10
        self.instinctHealAccum = 0
        self.skinwalkerInstinctDR = 0
        self.skinwalkerInstinctRegen = 0

        # Confluence
        self.flux = 0
        self.confluenceActive = False

        # Wellspring
        self.wellspringBeastDamage = 0
        self.bloomActive = False
        self.wellspringFormEffectBonus = 0

        # Numen
        self.numenBeastDamage = 0
        self.numenThresholdDamage = 0

        self._applyFormBonuses()

    def bypassesFormRequirement(self) -> bool:
        return self._ascendancy == 'Confluence' and self.confluenceActive

    def __str__(self):
        formDisplay = "[green]Human[/green]" if self.form == 'human' else "[yellow]Beast[/yellow]"
        base = f"{super().__str__()}\n[earth]Verdance:[/earth] {self.verdance}/{self.maxVerdance} | Form: {formDisplay}"

        if self._ascendancy == 'Heartwood':
            if self.elderbarkActive:
                base += f" | [buff]Elderbark: {self.elderbarkTurns} turn(s) left[/buff]"
            elif self.root > 0:
                base += f" | [dim]Root: {self.root}[/dim]"
            base += f" | Loam: {self.loam}/{self.maxLoam}"
        elif self._ascendancy == 'Skinwalker':
            base += f" | Ferocity: {self.ferocity}/{self.maxFerocity} | Instinct: {self.instinct}/{self.maxInstinct}"
        elif self._ascendancy == 'Confluence':
            base += f" | Flux: {self.flux}"
            if self.confluenceActive:
                base += " | [gold1]Confluence Active[/gold1]"
        elif self._ascendancy == 'Wellspring' and self.bloomActive:
            base += " | [gold1]Blooming[/gold1]"

        return base

    def serialise(self):
        temp = super().serialise()
        temp['verdance'] = self.verdance
        temp['maxVerdance'] = self.maxVerdance
        temp['form'] = self.form
        return temp

    def deserialise(self, data):
        super().deserialise(data)
        self.verdance = data.get('verdance', 0)
        self.maxVerdance = data.get('maxVerdance', 20)
        self.form = data.get('form', 'human')
        self._applyFormBonuses()

    # ----------------------------------------------------------------------------------- #
    # form + verdance bonus application
    # ----------------------------------------------------------------------------------- #

    def _currentFormEffect(self) -> float:
        if self._ascendancy == 'Numen':
            if self.form == 'beast':
                return 1 + (self.armour * 0.001)
            return 1 + (self.energyShield * 0.00125)

        effect = 1 + (0.05 * (self._level - 1)) + (0.10 * self.verdance)
        if self._ascendancy == 'Confluence':
            effect += 0.10 * self.flux
        if self._ascendancy == 'Wellspring':
            if self.bloomActive:
                effect *= 1.5
            effect += self.wellspringFormEffectBonus
        return effect

    def _applyFormBonuses(self):
        for k, v in self.formBonuses.items():
            if k in self._stats['Temporary']:
                self._stats['Temporary'][k] -= v
            self.formBonuses[k] = 0
        self.formEarthDamage = 0

        self._stats['Temporary']['hp_regen'] -= self.verdanceHpRegen
        self._stats['Temporary']['increased_armour'] -= self.verdanceArmour
        self._stats['Temporary']['damage_reduction'] -= self.verdanceDR
        self.verdanceHpRegen = 0
        self.verdanceArmour = 0
        self.verdanceDR = 0
        self.verdanceEarthDamage = 0

        self.formEffect = self._currentFormEffect()

        if self.form == 'human':
            self.formBonuses['hp_regen'] = round(2 * self.formEffect, 1)
            self.formBonuses['stamina_regen'] = round(2 * self.formEffect, 1)
            self.formBonuses['increased_defenses'] = 5 * self.formEffect
        elif self.form == 'beast':
            self.formEarthDamage = 10 * self.formEffect
            self.formBonuses['speed'] = round(0.02 * self.formEffect, 3)

        rootbound = self._ascendancy == 'Heartwood' and self.form == 'human' and (self.root > 0 or self.elderbarkActive)
        if rootbound:
            self.verdanceArmour = 5 * self.verdance
            self.verdanceDR = 2 * self.verdance
        elif self._ascendancy == 'Wellspring':
            self.verdanceDR = 2 * self.verdance
            self.verdanceEarthDamage = 5 * self.verdance
        else:
            self.verdanceEarthDamage = 5 * self.verdance
            self.verdanceHpRegen = 1 * self.verdance

        if self._ascendancy == 'Confluence' and self.confluenceActive:
            self.formBonuses['hp_regen'] += int(self._maxHealth * 0.05)
            self.formBonuses['increased_defenses'] += 25

        if self._ascendancy == 'Wellspring':
            self.formBonuses['healing_magnitude'] = 50 if self.form == 'human' else -75

        for k, v in self.formBonuses.items():
            if k in self._stats['Temporary']:
                self._stats['Temporary'][k] += v
        self._stats['Temporary']['hp_regen'] += self.verdanceHpRegen
        self._stats['Temporary']['increased_armour'] += self.verdanceArmour
        self._stats['Temporary']['damage_reduction'] += self.verdanceDR

    def _gainVerdance(self, amount: int) -> int:
        if amount <= 0 or self.verdance >= self.maxVerdance:
            return 0
        if self._ascendancy == 'Confluence' and self.confluenceActive:
            amount = int(amount * 1.5)
        gained = min(amount, self.maxVerdance - self.verdance)
        if gained > 0:
            self.verdance += gained
            self._applyFormBonuses()
            if self._ascendancy == 'Skinwalker' and self.form == 'human':
                self.instinct = min(self.maxInstinct, self.instinct + gained)
            console.print(f"[earth]Gained {gained} Verdance. Current: {self.verdance}/{self.maxVerdance}[/earth]")
        return gained

    def _applyFerocityBonus(self):
        self._stats['Temporary']['crit_chance'] -= self.ferocityCritChance
        self._stats['Temporary']['crit_multi'] -= self.ferocityCritMulti
        effect = 1 + (0.05 * self.verdance)
        self.ferocityCritChance = 0.03 * self.ferocity * effect
        self.ferocityCritMulti = 0.10 * self.ferocity * effect
        self._stats['Temporary']['crit_chance'] += self.ferocityCritChance
        self._stats['Temporary']['crit_multi'] += self.ferocityCritMulti

    def _heartwoodEvolveElderbark(self):
        self.elderbarkActive = True
        self.elderbarkTurns = 3
        self.elderbarkThorns = self._level + self.verdance
        self._stats['Temporary']['thorns'] += self.elderbarkThorns
        console.print(f"[earth]Heartwood: Rootbound blossoms into Elderbark! +{self.elderbarkThorns} Thorns, +3% Max HP Regeneration for 3 turns.[/earth]")

    def _heartwoodEndRootedState(self):
        if self.elderbarkActive:
            self._stats['Temporary']['thorns'] -= self.elderbarkThorns
            self.elderbarkThorns = 0
            self.elderbarkActive = False
            self.elderbarkTurns = 0
            console.print("[warning]Heartwood: Elderbark has faded.[/warning]")
        if self.heartwoodLoamCritChance:
            self._stats['Temporary']['crit_chance'] -= self.heartwoodLoamCritChance
        self.heartwoodLoamCritChance = 0
        self.heartwoodLoamEarthDamage = 0
        self.root = 0

    def _wellspringTriggerBloom(self, combatManager):
        consumed = self.verdance
        self.verdance = 0
        self.bloomActive = True
        console.print(f"[earth]Wellspring: Blooming {self.form.title()} Form erupts! Consumed {consumed} Verdance.[/earth]")
        dmg = int(self._maxHealth * 0.10)
        if combatManager:
            for e in combatManager.allAlive:
                e.damage(dmg, 'earth')
        self._applyFormBonuses()

    def _confluenceTriggerEvolution(self):
        self.confluenceActive = True
        if 'Switch Form' in self._abilities:
            self._abilities['Switch Form'].cooldown = 999
        console.print("[gold1]Confluence: You have fused into a true Human/Beast hybrid![/gold1]")

    def _onFormSwitched(self, oldForm: str, newForm: str):
        if self._ascendancy == 'Heartwood':
            if newForm == 'human':
                self.root = 3
                loamConsumed = self.loam
                self.loam = 0
                console.print("[earth]Heartwood: Rootbound begins - 3 turns until Elderbark.[/earth]")
                if loamConsumed > 0:
                    self.root = max(1, self.root - (loamConsumed // 5))
                    self.heartwoodLoamEarthDamage = 5 * loamConsumed
                    self.heartwoodLoamCritChance = 0.01 * loamConsumed
                    self._stats['Temporary']['crit_chance'] += self.heartwoodLoamCritChance
                    console.print(f"[earth]Heartwood: Consumed {loamConsumed} Loam! Root reduced to {self.root} turn(s). +{self.heartwoodLoamEarthDamage:.0f}% Earth Damage, +{self.heartwoodLoamCritChance*100:.0f}% Crit Chance until Elderbark fades.[/earth]")
            else:
                self._heartwoodEndRootedState()

        elif self._ascendancy == 'Skinwalker':
            if newForm == 'beast':
                consumed = self.instinct
                self.instinct = 0
                self.instinctHealAccum = 0
                if consumed > 0:
                    ferocityGain = consumed // 3
                    if ferocityGain > 0:
                        self.ferocity = min(self.maxFerocity, self.ferocity + ferocityGain)
                        self._applyFerocityBonus()
                    self.skinwalkerInstinctDR = 3 * consumed
                    self.skinwalkerInstinctRegen = 2 * consumed
                    self._stats['Temporary']['damage_reduction'] += self.skinwalkerInstinctDR
                    self._stats['Temporary']['hp_regen'] += self.skinwalkerInstinctRegen
                    console.print(f"[yellow]Skinwalker: Consumed {consumed} Instinct! +{ferocityGain} Ferocity, +{self.skinwalkerInstinctDR} Damage Reduction, +{self.skinwalkerInstinctRegen} HP Regen until you leave Beast Form.[/yellow]")
            else:
                if self.skinwalkerInstinctDR or self.skinwalkerInstinctRegen:
                    self._stats['Temporary']['damage_reduction'] -= self.skinwalkerInstinctDR
                    self._stats['Temporary']['hp_regen'] -= self.skinwalkerInstinctRegen
                    self.skinwalkerInstinctDR = 0
                    self.skinwalkerInstinctRegen = 0
                if self.ferocity > 0:
                    heal = int(self._maxHealth * 0.02 * self.ferocity)
                    self.heal(heal, reason=f"Skinwalker ({self.ferocity} Ferocity)")
                    self.ferocity = 0
                    self._applyFerocityBonus()

        elif self._ascendancy == 'Wellspring':
            if self.bloomActive:
                self.bloomActive = False
                console.print("[warning]Wellspring: Blooming Form has faded.[/warning]")

        elif self._ascendancy == 'Numen' and newForm == 'human':
            self.numenBeastDamage = 0

    def _shapeShift(self, *, form: str = None):
        oldForm = self.form
        if form is not None:
            self.form = form
        else:
            self.form = 'beast' if self.form == 'human' else 'human'

        if self.form != oldForm:
            self._onFormSwitched(oldForm, self.form)

        self._applyFormBonuses()
        self._recalculateStats(False)

        if self.form == 'human':
            console.print(f"  [green]Shifted into Human Form. +{self.formBonuses['hp_regen']:.0f} HP Regen, +{self.formBonuses['stamina_regen']:.0f} Stamina Regen, +{self.formBonuses['increased_defenses']:.0f}% Increased Defenses.[/green]")
        else:
            console.print(f"  [yellow]Shifted into Beast Form. +{self.formEarthDamage:.0f}% Earth Damage, +{self.formBonuses['speed']:.2f} Speed.[/yellow]")

    # ----------------------------------------------------------------------------------- #
    # combat hooks
    # ----------------------------------------------------------------------------------- #

    def _gainFlux(self, amount: int):
        if self._ascendancy != 'Confluence' or self.confluenceActive or amount <= 0:
            return
        self.flux += amount
        self._stats['Temporary']['speed'] += 0.05 * amount
        console.print(f"[earth]Confluence: Gained {amount} Flux. Current Flux: {self.flux}.[/earth]")
        if self.flux >= 5:
            self._confluenceTriggerEvolution()
        self._applyFormBonuses()

    def onAbilityCast(self, ability, combatManager):
        super().onAbilityCast(ability, combatManager)
        if not ability:
            return

        if 'switch_form' in ability.tags:
            bloomThresholdMet = self._ascendancy == 'Wellspring' and self.verdance >= self.maxVerdance * 0.5

            self._shapeShift()

            if bloomThresholdMet:
                self._wellspringTriggerBloom(combatManager)

            self._gainFlux(1)
            return

        if self._ascendancy == 'Heartwood' and 'gain_loam_on_cast' in ability.tags:
            fx = ability.effects.get('self', {}).get('gain_loam', {})
            stacks = fx.get('stacks', 0)
            gained = min(stacks, self.maxLoam - self.loam)
            if gained > 0:
                self.loam += gained
                console.print(f"[earth]Heartwood: {ability.name} grants {gained} Loam. Current: {self.loam}/{self.maxLoam}.[/earth]")

        if self._ascendancy == 'Skinwalker' and 'gain_ferocity_on_cast' in ability.tags:
            fx = ability.effects.get('self', {}).get('gain_ferocity', {})
            for _ in range(fx.get('stacks', 0)):
                if self.ferocity < self.maxFerocity:
                    self.ferocity += 1
                    self._applyFerocityBonus()

        if self._ascendancy == 'Confluence' and 'gain_flux_on_cast' in ability.tags:
            fx = ability.effects.get('self', {}).get('gain_flux', {})
            self._gainFlux(fx.get('stacks', 0))

        if self._ascendancy == 'Wellspring' and 'gain_verdance_on_cast' in ability.tags:
            fx = ability.effects.get('self', {}).get('gain_verdance', {})
            self._gainVerdance(fx.get('amount', 0))

        if self._ascendancy == 'Numen' and 'gain_numen_pool_on_cast' in ability.tags:
            fx = ability.effects.get('self', {}).get('gain_numen_pool', {})
            amount = fx.get('amount', 0)
            if amount > 0:
                self.numenThresholdDamage += amount
                console.print(f"[earth]Numen: {ability.name} adds {amount} to your stored bonus damage.[/earth]")

    def onTurnStart(self, combatManager=None):
        if self._ascendancy == 'Heartwood':
            if self.form == 'beast' and self.loam < self.maxLoam:
                self.loam = min(self.maxLoam, self.loam + 1)
            elif self.form == 'human':
                if self.elderbarkActive:
                    self.heal(int(self._maxHealth * 0.03), reason="Elderbark")
                    self.elderbarkTurns -= 1
                    if self.elderbarkTurns <= 0:
                        self._heartwoodEndRootedState()
                        self.root = 3
                        self._applyFormBonuses()
                elif self.root > 0:
                    self.root -= 1
                    if self.root <= 0:
                        self._heartwoodEvolveElderbark()
                        self._applyFormBonuses()

        elif self._ascendancy == 'Skinwalker':
            if self.form == 'beast' and self.ferocity < self.maxFerocity:
                self.ferocity += 1
                self._applyFerocityBonus()
            elif self.form == 'human' and self.instinct < self.maxInstinct:
                self.instinct = min(self.maxInstinct, self.instinct + 1)

        elif self._ascendancy == 'Wellspring':
            self._gainVerdance(2)

        super().onTurnStart(combatManager)

    def onAttack(self, damageDealt, damageType, target, combatManager, ability, crit):
        damageDealt, damageType = super().onAttack(damageDealt, damageType, target, combatManager, ability, crit)
        if ability and 'switch_form' in ability.tags:
            return damageDealt, damageType

        if ability and 'form_adaptive' in ability.tags:
            fx = ability.effects.get('beast_bonus' if self.form == 'beast' else 'human_bonus', {})
            dmgPct = fx.get('damage_percent', 0) / 100
            if dmgPct:
                damageDealt = int(damageDealt * (1 + dmgPct))
            healPct = fx.get('heal_percent_of_damage', 0) / 100
            if healPct:
                heal = int(damageDealt * healPct)
                self.heal(heal, reason=ability.name)
            verdanceGain = fx.get('gain_verdance', 0)
            if verdanceGain:
                self._gainVerdance(verdanceGain)

        if ability:
            if self._ascendancy == 'Heartwood' and 'consumes_loam_for_damage' in ability.tags and self.loam > 0:
                fx = ability.effects.get('self', {}).get('consume_loam', {})
                earthPerStack = fx.get('earth_damage_per_stack', 0)
                critPerStack = fx.get('crit_chance_per_stack', 0) / 100
                stacksConsumed = self.loam
                self.loam = 0
                self.heartwoodLoamEarthDamage += earthPerStack * stacksConsumed
                gainedCrit = critPerStack * stacksConsumed
                self.heartwoodLoamCritChance += gainedCrit
                self._stats['Temporary']['crit_chance'] += gainedCrit
                console.print(f"[earth]Heartwood: {ability.name} consumes {stacksConsumed} Loam! +{earthPerStack * stacksConsumed:.0f}% Earth Damage, +{gainedCrit*100:.0f}% Crit Chance until Elderbark fades.[/earth]")

            if self._ascendancy == 'Skinwalker' and 'consumes_ferocity_for_damage' in ability.tags and self.ferocity > 0:
                fx = ability.effects.get('self', {}).get('consume_ferocity', {})
                dmgPerStack = fx.get('damage_per_stack', 0) / 100
                stacksConsumed = self.ferocity
                self.ferocity = 0
                self._applyFerocityBonus()
                damageDealt = int(damageDealt * (1 + (dmgPerStack * stacksConsumed)))
                console.print(f"[yellow]Skinwalker: {ability.name} consumes {stacksConsumed} Ferocity for +{int(dmgPerStack * stacksConsumed * 100)}% Damage.[/yellow]")

            if self._ascendancy == 'Confluence' and 'consumes_verdance_for_damage' in ability.tags and self.verdance > 0:
                fx = ability.effects.get('self', {}).get('consume_verdance', {})
                dmgPerStack = fx.get('damage_per_stack', 0)
                stacksConsumed = self.verdance
                self.verdance = 0
                self._applyFormBonuses()
                bonus = dmgPerStack * stacksConsumed
                damageDealt += bonus
                console.print(f"[earth]Confluence: {ability.name} consumes {stacksConsumed} Verdance for +{bonus} Damage.[/earth]")

            if self._ascendancy == 'Confluence' and self.confluenceActive and 'form_adaptive' in ability.tags:
                fx = ability.effects.get('self', {}).get('confluence_bonus', {})
                confluencePct = fx.get('damage_percent', 0) / 100
                if confluencePct:
                    damageDealt = int(damageDealt * (1 + confluencePct))
                    console.print(f"[gold1]Confluence: {ability.name} draws on your fused nature for +{int(confluencePct * 100)}% Damage![/gold1]")

            if self._ascendancy == 'Wellspring' and 'consumes_beast_damage_pool' in ability.tags and self.wellspringBeastDamage > 0:
                fx = ability.effects.get('self', {}).get('consume_beast_pool', {})
                mult = fx.get('multiplier_percent', 100) / 100
                pooled = self.wellspringBeastDamage
                self.wellspringBeastDamage = 0
                bonus = int(pooled * mult)
                damageDealt += bonus
                console.print(f"[earth]Wellspring: {ability.name} overflows {pooled} stored Damage for +{bonus}![/earth]")

            if self._ascendancy == 'Numen' and 'consumes_numen_pools' in ability.tags and (self.numenBeastDamage > 0 or self.numenThresholdDamage > 0):
                fx = ability.effects.get('self', {}).get('consume_numen_pools', {})
                mult = fx.get('multiplier_percent', 100) / 100
                pooled = self.numenBeastDamage + self.numenThresholdDamage
                self.numenBeastDamage = 0
                self.numenThresholdDamage = 0
                bonus = int(pooled * mult)
                damageDealt += bonus
                console.print(f"[earth]Numen: {ability.name} overloads {pooled} stored Damage for +{bonus}![/earth]")

        if self.form == 'human':
            self._gainVerdance(2)

        totalEarthBonus = self.formEarthDamage + self.verdanceEarthDamage + self.heartwoodLoamEarthDamage
        if self._ascendancy == 'Confluence' and self.confluenceActive:
            totalEarthBonus += 50
        if damageType == 'earth' and totalEarthBonus > 0:
            damageDealt = int(damageDealt * (1 + (totalEarthBonus / 100)))

        if self._ascendancy == 'Wellspring' and self.form == 'beast' and self.wellspringBeastDamage > 0:
            damageDealt += self.wellspringBeastDamage

        if self._ascendancy == 'Numen':
            if self.form == 'beast' and self.numenBeastDamage > 0:
                damageDealt += self.numenBeastDamage
            if self.numenThresholdDamage > 0:
                damageDealt += self.numenThresholdDamage

        return damageDealt, damageType

    def onHit(self, damageTaken, damageType, crit=False, attacker=None, combatManager=None):
        if self.form == 'beast':
            self._gainVerdance(2)
            if self._ascendancy == 'Heartwood' and self.loam < self.maxLoam:
                self.loam = min(self.maxLoam, self.loam + max(1, damageTaken // 15))

        if self._ascendancy == 'Confluence' and self.confluenceActive:
            damageTaken = int(damageTaken * 1.15)

        return super().onHit(damageTaken, damageType, crit, attacker, combatManager)

    def onHeal(self, healAmount):
        if self._ascendancy == 'Skinwalker' and self.form == 'human' and self.instinct < self.maxInstinct:
            self.instinctHealAccum += healAmount
            threshold = max(1, int(self._maxHealth * 0.02))
            while self.instinctHealAccum >= threshold and self.instinct < self.maxInstinct:
                self.instinctHealAccum -= threshold
                self.instinct += 1

        elif self._ascendancy == 'Wellspring':
            self._gainVerdance(int(healAmount * 0.10))
            if self.form == 'beast':
                self.wellspringBeastDamage += healAmount
                console.print(f"[earth]Wellspring: +{healAmount} Damage whilst in Beast Form (from Health gained).[/earth]")

    def onCrit(self, targets, combatManager, critDamage):
        if self._ascendancy == 'Skinwalker' and self.ferocity < self.maxFerocity:
            self.ferocity += 1
            self._applyFerocityBonus()
        return critDamage

    def onCriticallyHit(self, attacker, combatManager, critDamage, damageType):
        critDamage = super().onCriticallyHit(attacker, combatManager, critDamage, damageType)
        if self._ascendancy == 'Confluence' and self.confluenceActive and self.verdance > 0:
            retaliation = int(attacker._maxHealth * 0.005 * self.verdance)
            if retaliation > 0:
                console.print(f"[earth]Confluence: {attacker._name} takes {retaliation} Earth damage for critically striking you![/earth]")
                attacker.damage(retaliation, 'earth')
        return critDamage

    def rollCritical(self, target, damageDealt=None):
        if (self._ascendancy == 'Skinwalker' and self.ferocity >= self.maxFerocity
                and target and target.entity._health < target.entity._maxHealth * 0.3):
            return True, self.critMulti
        return super().rollCritical(target, damageDealt)

    def onDealDamage(self, target, targetUnit, finalDamage, damageType, evaded, armourDamagePrevented, esDamagePrevented, combatManager):
        finalDamage = super().onDealDamage(target, targetUnit, finalDamage, damageType, evaded, armourDamagePrevented, esDamagePrevented, combatManager)
        if self._ascendancy == 'Wellspring' and esDamagePrevented > 0 and target.energyShield <= 0 and target.maxEnergyShield > 0:
            gain = 0.01 * (target.maxEnergyShield / 5)
            self.wellspringFormEffectBonus += gain
            self._applyFormBonuses()
            console.print(f"[earth]Wellspring: Shattered {target._name}'s Energy Shield! +{gain*100:.1f}% Form Effect for the rest of combat.[/earth]")
        return finalDamage

    def onAfterMitigation(self, attacker, finalDamage, damageType, evaded, armourDamagePrevented, esDamagePrevented, preMitigationDamage, combatManager):
        finalDamage = super().onAfterMitigation(attacker, finalDamage, damageType, evaded, armourDamagePrevented, esDamagePrevented, preMitigationDamage, combatManager)
        if self._ascendancy == 'Numen' and not evaded:
            if self.form == 'human' and armourDamagePrevented > 0:
                gain = min(self.maxEnergyShield - self.energyShield, armourDamagePrevented)
                if gain > 0:
                    self._stats['energy_shield'] += gain
                    console.print(f"[earth]Numen: {armourDamagePrevented} damage prevented by Armour regenerates {gain} Energy Shield.[/earth]")
            elif self.form == 'beast' and esDamagePrevented > 0:
                self.numenBeastDamage += esDamagePrevented
                console.print(f"[earth]Numen: {esDamagePrevented} damage mitigated by Energy Shield becomes bonus Damage whilst in Beast Form.[/earth]")

            totalPrevented = armourDamagePrevented + esDamagePrevented
            if preMitigationDamage > 0 and (totalPrevented / preMitigationDamage) > 0.5:
                bonus = int(preMitigationDamage * 0.2)
                self.numenThresholdDamage += bonus
                console.print(f"[earth]Numen: Prevented over 50% of an incoming hit! +{bonus} Damage for the rest of combat.[/earth]")
        return finalDamage

    def onKill(self, entity=None, attackData=None, combatManager=None):
        super().onKill()
        if self._ascendancy == 'Skinwalker' and self.ferocity > 0:
            consumed = min(5, self.ferocity)
            self.ferocity -= consumed
            self._applyFerocityBonus()
            heal = int(self._maxHealth * 0.02 * consumed)
            self.heal(heal, reason=f"Skinwalker ({consumed} Ferocity consumed)")

        # generic ability.effects.onKill processing - available to any Druid ability
        ability = attackData.get('ability') if attackData else None
        onKillFx = ability.effects.get('onKill', {}) if ability else {}
        if onKillFx:
            healPct = onKillFx.get('heal', {}).get('percent', 0)
            if healPct:
                heal = int(self._maxHealth * healPct)
                self.heal(heal, reason=ability.name)
                console.print(f"[class_druid]{ability.name} claims its due! Healed {heal} HP.[/class_druid]")

            regenFx = onKillFx.get('regeneration')
            if regenFx and combatManager:
                pct = regenFx.get('amount_percent', 0)
                pct = pct / 100 if pct > 1 else pct
                effect = Effects.createRegeneration(regenFx.get('turns', 2), pct, regenFx.get('amount_flat', 0))
                combatManager.addStatusEffect(self, effect, self)

        return {}

    def onCombatEnd(self):
        self.form = 'human'
        self.verdance = 0
        self.formEffect = 1.0
        for k in self.formBonuses:
            self.formBonuses[k] = 0
        self.formEarthDamage = 0
        self.verdanceHpRegen = 0
        self.verdanceArmour = 0
        self.verdanceDR = 0
        self.verdanceEarthDamage = 0

        self.root = 0
        self.elderbarkActive = False
        self.elderbarkTurns = 0
        self.elderbarkThorns = 0
        self.loam = 0
        self.heartwoodLoamEarthDamage = 0
        self.heartwoodLoamCritChance = 0

        self.ferocity = 0
        self.ferocityCritChance = 0
        self.ferocityCritMulti = 0
        self.instinct = 0
        self.instinctHealAccum = 0
        self.skinwalkerInstinctDR = 0
        self.skinwalkerInstinctRegen = 0

        self.flux = 0
        self.confluenceActive = False
        if 'Switch Form' in self._abilities:
            self._abilities['Switch Form'].cooldown = 0

        self.wellspringBeastDamage = 0
        self.bloomActive = False
        self.wellspringFormEffectBonus = 0

        self.numenBeastDamage = 0
        self.numenThresholdDamage = 0

        super().onCombatEnd() # zeroes every Temporary stat, must run after the resets above

    def _recalculateStats(self, doPrint=True, inCombat=False):
        super()._recalculateStats(doPrint, inCombat)

        if self._ascendancy == 'Wellspring':
            esToHp = self.maxEnergyShield
            if esToHp > 0:
                self._maxHealth += esToHp
                self._stats['max_energy_shield'] = 0
                self._stats['energy_shield'] = 0
                if doPrint:
                    console.print(f"[earth]Wellspring: Converted {esToHp} Energy Shield into Max Health.[/earth]")

        elif self._ascendancy == 'Numen':
            if self.form == 'human':
                gain = int(self.armour * 0.10)
                if gain > 0:
                    self._stats['max_energy_shield'] += gain
                    if not inCombat:
                        self._stats['energy_shield'] += gain
            elif self.form == 'beast':
                gain = int(self.maxEnergyShield * 0.20)
                if gain > 0:
                    self._stats['armour'] += gain

    def _levelUp(self):
        super()._levelUp()
        self._applyFormBonuses()
        self._recalculateStats(False)

    ASCENDANCY_DELTAS = {
        'Heartwood': {
            '_baseHealth': 15,
            '_baseDamage': -2,
            '_baseSpeed': -0.1,
            '_stats.Permanent.elemental': 15,
            '_stats.Permanent.added_armour': 50,
        },
        'Skinwalker': {
            '_baseHealth': -15,
            '_baseDamage': 4,
            '_baseSpeed': 0.1,
            '_stats.baseCritMulti': 0.25,
            '_stats.baseCritChance': 0.05,
        },
        'Confluence': {
            '_baseHealth': 10,
            '_baseDamage': 1,
            '_baseSpeed': 0.05,
            'maxVerdance': 5,
            '_stats.Permanent.elemental': 10,
        },
        'Wellspring': {
            '_baseHealth': 15,
            '_baseSpeed': -0.05,
            'maxVerdance': 15,
            '_stats.Permanent.healing_magnitude': 25,
            '_stats.Permanent.hp_regen': 10,
        },
        'Numen': {
            '_baseHealth': 15,
            '_baseSpeed': -0.1,
            '_stats.Permanent.added_armour': 40,
            '_stats.Permanent.added_energy_shield': 40,
        },
    }

    def _removeOldAscendancy(self) -> bool:
        delta = self.ASCENDANCY_DELTAS.get(self._ascendancy)
        if delta:
            self._applyStatDelta(delta, sign=-1)
        if self._ascendancy == 'Confluence' and 'Switch Form' in self._abilities:
            self._abilities['Switch Form'].cooldown = 0
        return True

    def updateAscendancy(self, ascendancy):
        if not super().updateAscendancy(ascendancy):
            return
        self._ascendancy = ascendancy
        self.ascendancyDescription = DRUID_DESCRIPTIONS[ascendancy]
        self._applyStatDelta(self.ASCENDANCY_DELTAS[ascendancy], sign=1)
        self.gainClassAbilities(True)
        self._applyFormBonuses()
        self._recalculateStats()
        return True
