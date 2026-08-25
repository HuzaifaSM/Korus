from .base import Player, OTHERWORLD_RES
from scripts.styles import console
from enum import Enum
import random

class Threshold(Enum):
    COMPLACENT = "complacent"
    NEUTRAL = "neutral"
    TRAINED = "trained"
    DEDICATED = "dedicated"
    ALL_IN = "all-in"

def getThresholdFromValue(value: int) -> Threshold:
    if value < 0:
        return Threshold.COMPLACENT
    elif value < 35:
        return Threshold.NEUTRAL
    elif value < 70:
        return Threshold.TRAINED
    elif value < 110:
        return Threshold.DEDICATED
    else:
        return Threshold.ALL_IN

def GetThresholdFromStr(threshold: str) -> Threshold:
    threshold = threshold.lower()
    if threshold == 'complacent':
        return Threshold.COMPLACENT
    elif threshold == 'neutral':
        return Threshold.NEUTRAL
    elif threshold == 'trained':
        return Threshold.TRAINED
    elif threshold == 'dedicated':
        return Threshold.DEDICATED
    elif threshold == 'all-in':
        return Threshold.ALL_IN

FIGHTER_DESCRIPTIONS = {
    "Fighter": "[class_fighter]An expert of combat, balancing precision and recklessness to dismantle their foes.[/class_fighter]\n"
        "- You have two Stances: Aggression and Discipline. At the start of your turn, gain 5 Aggression and Discipline.\n"
        "- Start combat with 25 Aggression and Discipline. Gain 3 Aggression when you attack, and bonus Aggression based on Damage Dealt. Gain 3 Discipline when you use a non-damaging ability, and bonus Discipline based on Damage Taken.\n"
        "- Aggression and Discipline share a combined maximum of 100. Aggression and Discipline have no maximum, but have a minimum of -30.\n"
        "- You cannot fall below 0 Aggression or Discipline without using an ability.\n"
        "- There are 5 thresholds for Aggression and Discipline: Complacent (-30 to -1), Neutral (0 to 34), Trained (35 to 69), Dedicated (70 to 109), All-In (110)+. Neutral has no stat changes. Only the current threshold applies its buffs.\n\n"
        "Aggression Threshold Changes:\n"
        "   > Complacent: -0.3 Speed, 30% Less Physical Damage Dealt, -10% Crit Chance.\n"
        "   > Trained: 20% Increased Physical Damage, +5% Lifesteal, +25% Crit Multi.\n"
        "   > Dedicated: 50% Increased Physical Damage, +15% Lifesteal, +60% Crit Multi, +5% Crit Chance.\n"
        "   > All-In: 100% Increased Physical Damage, +30% Lifesteal, Upon landing a critical hit: heal for 10% of the damage dealt, gain Bonus Damage equal to your Base Damage for the rest of combat, 40% Reduced Defenses.\n\n"
        "Discipline Threshold Changes:\n"
        "   > Complacent: 30% More Damage Taken, 25% Reduced Defenses, -25% Stun Avoidance.\n"
        "   > Trained: Gain Damage Reduction equal to your level, 10% Increased Defenses, +1% Max HP Regen.\n"
        "   > Dedicated: 15% Less Damage Taken, Gain Thorns equal to your base damage, 25% Increased Defenses, +3% Max HP Regen.\n"
        "   > All-In: You are unable to critically hit. Gain Thorns equal to 3x your Damage, Upon killing an enemy: gain their Damage as Added Damage for the rest of combat and heal equal to 10% of their Max HP. 40% Less Damage Taken.\n\n"
        "[bold]Starting Stats:[/bold] 45 HP | 6 Damage | 5% Crit Chance | 160% Crit Damage | Physical Damage | 1.05 Speed",
    # ascendancies
    "Dissenter": "[lore]They call it complacency. Degeneracy. Lunacy. Why should you fight to their standards? Why lower yourself to such boring duels? Reject their ignorance. Show them their training means nothing. Eradicate them.[/lore]"
        "- Complacent Aggression now grants Damage Reduction equal to 2x your level, and Thorns equal to half your level.\n"
        "- Complacent Discipline grants +10% Crit Chance and +50% Crit Damage.\n"
        "- For every turn you begin without a Stance in All-In, gain 1 Impatience. Impatience: +2 Stance Progress to the stronger Stance at the start of your turn.\n"
        "- Impatience has no stack limits. Whenever a Stance reaches All-In, consume all Impatience to gain buffs.\n"
        "- Upon reaching All-In Aggression, for each stack of Impatience, gain +1% Crit Chance and +1 Damage until you lose All-In Aggression.\n"
        "- Upon reaching All-In Discipline, for each stack of Impatience, gain +2 HP Regen, +1 Damage Reduction until you lose All-In Discipline.\n"
        "[bold]Stat Changes:[/bold] -5 HP. +10 Damage. +0.05 Speed. +25% Crit Damage. +5% Increased Defenses.",
    "Arbiter": "[lore]There is no strength in excess. No wisdom in weakness. Hesitation and recklessness have no place here. To master yourself, you must rid the whispers of grandeur. Only then, this world shall bow to you.[/lore]"
        "- Trained Aggression has 50% Increased Effect. Trained Discipline grants 5% Less Damage Taken.\n"
        "- For every turn you have Trained Aggression and Trained Discipline, gain 1 stack of Balance. Balance has no stack limit.\n"
        "- Balance: 5% Increased Damage, 1% Less Damage Taken. Whenever a Stance reaches Dedicated, consume all Balance to gain buffs.\n"
        "- Upon reaching Dedicated Aggression, for each stack of Balance, gain 5% Increased Damage and +1% Lifesteal until you lose Dedicated Aggression.\n"
        "- Upon reaching Dedicated Discipline, for each stack of Balance, gain 1% Less Damage Taken and Thorns equal to half your level.\n"
        "[bold]Stat Changes:[/bold] +25 HP. +8 Damage. -0.1 Speed. +15% Physical Resistance.",
    "Transgressor": "[lore]Their training fell short. They could not exceed the body. They could not fathom the mind. But you could. So go, and walk through the boundaries of mortality. When their heads roll, only then will they understand.[/lore]"
        "- Every turn, the combined cap of Aggression and Discipline is increased by 10. Upon dealing critical hits or being critically hit, raise your combined cap by 5.\n"
        "- The combined cap of Aggression and Discipline cannot exceed 150. Complacent debuffs have 50% Increased Effects.\n"
        "- If you have Dedicated Aggression and Trained Discipline simultaneously, gain 30% Increased Physical Damage, 10% Less Damage Taken, +5% Crit Chance.\n"
        "- If you have Dedicated Discipline and Trained Aggression simultaneously, gain 20% Increased Defenses, Thorns equal to 2% of your highest Defense, 20% Increased Physical Damage.\n"
        "- If you have Dedicated Aggression and Dedicated Discipline simultaneously, gain +10% Crit Chance, +50% Crit Damage, 25% Increased Defenses, 25% Increased Physical Damage.\n"
        "[bold]Stat Changes:[/bold] +5 HP. +2 Damage. +0.15 Speed. +5% Crit Chance. +25% Ailment Avoidance.",
    "Triarch": "[lore]Endure, evade, absorb. Their feeble minds could never comprehend. They fail to see the threads between them. Why pick, when all is yours? Why sacrifice, if all returns to you? Become unbreakable as The Sky itself, then collapse upon them with unspeakable might.[/lore]"
        "- If you have Armour, Evasion, and Energy Shield: Gain 10% of Armour as Evasion and Energy Shield, Gain 10% of Evasion as Armour and Energy Shield, Gain 20% of Energy Shield as Armour and Evasion.\n"
        "- Gain 2% Increased Physical Damage per 25 Armour. Gain +0.2% Crit Chance and +1% Crit Damage per 30 Evasion. Gain +1 HP Regen per 25 Current Energy Shield.\n"
        "- For every 50 Max Energy Shield, gain +1 to the combined cap of Aggression and Discipline, to a maximum of +25.\n"
        "- Whenever you kill an enemy, Regenerate Energy Shield equal to the value of your stronger Stance. If you have more Armour than Evasion, this Regeneration is doubled. If you have more Evasion than Armour, this Regeneration applies to Health as well.\n"
        "- When attacked by Otherworld Damage, if you have all three Defenses: your Armour is treated as 150% of its real value, your Evasion is rolled twice, heal Health equal to Damage absorbed by Energy Shield.\n"
        "[bold]Stat Changes:[/bold] +5 HP. +10 Damage. 10% Increased Defenses.",
    "Autarch": "[lore]You were trained to succumb to limits. You broke through, and ruled over them instead. Their laws cannot bind you. Their strength cannot stop you. Walk atop their corpses, frail and bound. Claim their empire as yours.[/lore]"
        "- At the start of your turn, choose a Pact: Pact of Aggression, Pact of Discipline. If you have a Dedicated Stance, you can choose Pact of Balance. If you have an All-In Stance, you can choose Pact of Purging.\n"
        "- Pacts last until the start of your next turn.\n"
        "- Pact of Aggression: The effect of your current Aggression Stance is doubled. The effect of your current Discipline Stance is inverted. All Stance changes count as Aggression progress.\n"
        "- Pact of Discipline: The effect of your current Dscipline Stance is doubled. The effect of your current Aggression Stance is inverted. All Stance changes count as Discipline progress.\n"
        "- Pact of Balance: Gain the bonuses of Trained Aggression and Trained Discipline alongside your current Stance effects. All Stance changes will aim to balance Stance progress towards 50/50.\n"
        "- Pact of Purging: Gain the All-In buffs of the alternate Stance. Both Stances have no All-In debuffs until the start of your next turn. If you do not kill an enemy this turn, take Physical Damage equal to 25% of your Max HP. This Damage cannot kill you.\n"
        "- Upon killing an enemy, heal equal to 10% of their Max HP and gain Damage equal to their Base Damage for the rest of combat.\n"
        "[bold]Stat Changes:[/bold] +25 HP. +7 Damage. -0.1 Speed. +10% Physical Resistance. +5% Divine Resistance."
}

class Fighter(Player): # higher speed, lower damage, physical damage
    def __init__(self, name, health = 45, damage = 6, damageType = "physical", speed = 1.05):
        super().__init__(name, health, damage, 0.05, 1.6, damageType, speed, className="Fighter", classDescription=FIGHTER_DESCRIPTIONS['Fighter'])
        self.aggression = 0
        self.currentAggressionTreshold = Threshold.NEUTRAL
        self.aggressionDamage = 0
        self.discipline = 0
        self.currentDisciplineThreshold = Threshold.NEUTRAL
        self.disciplineDamage = 0
        self._appliedAggressionDelta = {}
        self._appliedDisciplineDelta = {}
        self.stanceCap = 100

        self.impatience = 0
        self.impatienceAggroBuff = {}
        self.impatienceAggroDamage = 0
        self.impatienceDiscBuff = {}

        self.balance = 0
        self.balanceAggroStacks = 0
        self.balanceAggroBuff = {}
        self.balanceDiscStacks = 0
        self.balanceDiscBuff = {}

        self.transgressorSyncTier = None
        self.transgressorSyncStats = {}
        self.transgressorSyncThorns = 0

        self.triarchCapBonus = 0
        self.triarchHpRegenBonus = 0

        self.autarchPact = None
        self.autarchKilledThisTurn = False
        self.autarchBonusDamage = 0

    @property
    def availableStanceSpace(self):
        return self.stanceCap - (self.aggression + self.discipline)

    def getMaxStanceChange(self, stance: str, change: int) -> int:
        """finds out how much cost can be subtracted from the other, floor at 0."""
        if stance == 'aggression': # comapare gain in one to change in other
            return min(change, max(0, self.discipline))
        else:
            return min(change, max(0, self.aggression))

    def _autarchGainTarget(self, requestedStance: str) -> str:
        if self.autarchPact == 'aggression':
            return 'aggression'
        elif self.autarchPact == 'discipline':
            return 'discipline'
        elif self.autarchPact == 'balance':
            return 'aggression' if self.aggression <= self.discipline else 'discipline'
        return requestedStance

    def gainAggression(self, amount):
        if self._ascendancy == 'Autarch' and self._autarchGainTarget('aggression') == 'discipline':
            self._rawGainDiscipline(amount)
            return
        self._rawGainAggression(amount)

    def _rawGainAggression(self, amount):
        freeGain = min(self.availableStanceSpace, amount)
        costGain = self.getMaxStanceChange('aggression', amount - freeGain)
        self.discipline -= costGain
        self.aggression += freeGain + costGain
        self.checkAggressionChange()
        self.checkDisciplineChange()

    def loseAggression(self, amount: int, floorBreak: bool = False):
        if floorBreak:
            self.aggression = max(-30, self.aggression - amount)
        else:
            self.aggression = max(0, self.aggression - amount)
        self.checkAggressionChange()

    def gainDiscipline(self, amount):
        if self._ascendancy == 'Autarch' and self._autarchGainTarget('discipline') == 'aggression':
            self._rawGainAggression(amount)
            return
        self._rawGainDiscipline(amount)

    def _rawGainDiscipline(self, amount):
        freeGain = min(self.availableStanceSpace, amount)
        costGain = self.getMaxStanceChange('discipline', amount - freeGain)
        self.aggression -= costGain
        self.discipline += freeGain + costGain
        self.checkDisciplineChange()
        self.checkAggressionChange()

    def loseDiscipline(self, amount: int, floorBreak: bool = False):
        if floorBreak:
            self.discipline = max(-30, self.discipline - amount)
        else:
            self.discipline = max(0, self.discipline - amount)
        self.checkDisciplineChange()

    def _thresholdEffects(self, stance: str, threshold: Threshold) -> dict:
        if stance == 'aggression':
            if threshold == Threshold.COMPLACENT:
                delta = {'speed': -0.3, 'crit_chance': -0.1}
                if self._ascendancy == 'Dissenter':
                    delta['damage_reduction'] = delta.get('damage_reduction', 0) + self._level * 2
                    delta['thorns'] = delta.get('thorns', 0) + self._level // 2
            elif threshold == Threshold.TRAINED:
                delta = {'lifesteal': 5, 'crit_multi': 0.25}
                if self._ascendancy == 'Arbiter':
                    delta = {k: v * 1.5 for k, v in delta.items()}
            elif threshold == Threshold.DEDICATED:
                delta = {'lifesteal': 15, 'crit_multi': 0.6, 'crit_chance': 0.05}
            elif threshold == Threshold.ALL_IN:
                delta = {'lifesteal': 30, 'increased_defenses': -40}
            else:
                delta = {}
        else:
            if threshold == Threshold.COMPLACENT:
                delta = {'increased_defenses': -25, 'stun_avoidance': -25}
                if self._ascendancy == 'Dissenter':
                    delta['crit_chance'] = delta.get('crit_chance', 0) + 0.1
                    delta['crit_multi'] = delta.get('crit_multi', 0) + 0.5
            elif threshold == Threshold.TRAINED:
                delta = {'damage_reduction': self._level, 'increased_defenses': 10, 'hp_regen': int(self._maxHealth * 0.01)}
            elif threshold == Threshold.DEDICATED:
                delta = {'thorns': self._baseDamage, 'increased_defenses': 25, 'hp_regen': int(self._maxHealth * 0.03)}
            elif threshold == Threshold.ALL_IN:
                delta = {'crit_chance': -100, 'thorns': self._damage * 3}
            else:
                delta = {}

        if self._ascendancy == 'Transgressor' and threshold == Threshold.COMPLACENT:
            delta = {k: v * 1.5 for k, v in delta.items()}
        return delta

    def _transformStanceDelta(self, stance: str, delta: dict) -> dict:
        if self._ascendancy != 'Autarch' or not self.autarchPact:
            return delta

        def merge(a: dict, b: dict) -> dict:
            merged = dict(a)
            for k, v in b.items():
                merged[k] = merged.get(k, 0) + v
            return merged

        if self.autarchPact == 'aggression':
            if stance == 'aggression':
                return {k: v * 2 for k, v in delta.items()}
            return {k: -v for k, v in delta.items()}

        elif self.autarchPact == 'discipline':
            if stance == 'discipline':
                return {k: v * 2 for k, v in delta.items()}
            return {k: -v for k, v in delta.items()}

        elif self.autarchPact == 'balance':
            trained = self._thresholdEffects(stance, Threshold.TRAINED)
            return merge(delta, trained)

        elif self.autarchPact == 'purging':
            aggAllIn = self.currentAggressionTreshold == Threshold.ALL_IN
            discAllIn = self.currentDisciplineThreshold == Threshold.ALL_IN
            isCurrentAllIn = (stance == 'aggression' and aggAllIn) or (stance == 'discipline' and discAllIn)
            if isCurrentAllIn:
                return {k: v for k, v in delta.items() if v > 0}  # strip All-In debuff components

            isAlternate = (stance == 'aggression' and discAllIn) or (stance == 'discipline' and aggAllIn)
            if isAlternate:
                allInBuffs = {k: v for k, v in self._thresholdEffects(stance, Threshold.ALL_IN).items() if v > 0}
                return merge(delta, allInBuffs)

        return delta

    def _applyStanceDelta(self, delta: dict, sign: int = 1):
        for stat, amount in delta.items():
            self._stats['Temporary'][stat] += amount * sign

    def _checkStanceChange(self, stance: str):
        if stance == 'aggression':
            oldThreshold = self.currentAggressionTreshold
            newThreshold = getThresholdFromValue(self.aggression)
            appliedAttr = '_appliedAggressionDelta'
        else:
            oldThreshold = self.currentDisciplineThreshold
            newThreshold = getThresholdFromValue(self.discipline)
            appliedAttr = '_appliedDisciplineDelta'

        if oldThreshold == newThreshold:
            return

        self._applyStanceDelta(getattr(self, appliedAttr), sign=-1)
        newDelta = self._transformStanceDelta(stance, self._thresholdEffects(stance, newThreshold))
        self._applyStanceDelta(newDelta, sign=1)
        setattr(self, appliedAttr, newDelta)

        if stance == 'aggression':
            self.currentAggressionTreshold = newThreshold
        else:
            self.currentDisciplineThreshold = newThreshold

        self._onStanceThresholdChanged(stance, oldThreshold, newThreshold)

    def checkAggressionChange(self):
        self._checkStanceChange('aggression')

    def checkDisciplineChange(self):
        self._checkStanceChange('discipline')

    def _refreshStanceEffects(self):
        for stance, appliedAttr, currentThreshold in (
            ('aggression', '_appliedAggressionDelta', self.currentAggressionTreshold),
            ('discipline', '_appliedDisciplineDelta', self.currentDisciplineThreshold),
        ):
            self._applyStanceDelta(getattr(self, appliedAttr), sign=-1)
            newDelta = self._transformStanceDelta(stance, self._thresholdEffects(stance, currentThreshold))
            self._applyStanceDelta(newDelta, sign=1)
            setattr(self, appliedAttr, newDelta)

    def _onStanceThresholdChanged(self, stance: str, old: Threshold, new: Threshold):
        if self._ascendancy == 'Dissenter':
            self._dissenterOnThresholdChanged(stance, old, new)
        elif self._ascendancy == 'Arbiter':
            self._arbiterOnThresholdChanged(stance, old, new)
        elif self._ascendancy == 'Transgressor':
            self._transgressorRefreshSync()

    def _dissenterOnThresholdChanged(self, stance: str, old: Threshold, new: Threshold):
        if new == Threshold.ALL_IN:
            stacks = self.impatience
            self.impatience = 0
            if stacks <= 0:
                return
            if stance == 'aggression':
                self.impatienceAggroBuff = {'crit_chance': stacks * 0.01}
                self._applyStanceDelta(self.impatienceAggroBuff, sign=1)
                self.impatienceAggroDamage = stacks
                console.print(f"[asc_dissenter]Dissenter: Consumed {stacks} Impatience! +{stacks}% Crit Chance, +{stacks} Damage while All-In Aggression.[/asc_dissenter]")
            else:
                self.impatienceDiscBuff = {'hp_regen': stacks * 2, 'damage_reduction': stacks}
                self._applyStanceDelta(self.impatienceDiscBuff, sign=1)
                console.print(f"[asc_dissenter]Dissenter: Consumed {stacks} Impatience! +{stacks * 2} HP Regen, +{stacks} Damage Reduction while All-In Discipline.[/asc_dissenter]")
        elif old == Threshold.ALL_IN:
            if stance == 'aggression':
                self._applyStanceDelta(self.impatienceAggroBuff, sign=-1)
                self.impatienceAggroBuff = {}
                self.impatienceAggroDamage = 0
            else:
                self._applyStanceDelta(self.impatienceDiscBuff, sign=-1)
                self.impatienceDiscBuff = {}

    def _arbiterOnThresholdChanged(self, stance: str, old: Threshold, new: Threshold):
        if new == Threshold.DEDICATED:
            stacks = self.balance
            self.balance = 0
            if stacks <= 0:
                return
            if stance == 'aggression':
                self.balanceAggroStacks = stacks
                self.balanceAggroBuff = {'lifesteal': stacks}
                self._applyStanceDelta(self.balanceAggroBuff, sign=1)
                console.print(f"[asc_arbiter]Arbiter: Consumed {stacks} Balance! +{stacks * 5}% Increased Damage, +{stacks}% Lifesteal while Dedicated Aggression.[/asc_arbiter]")
            else:
                self.balanceDiscStacks = stacks
                self.balanceDiscBuff = {'thorns': (self._level // 2) * stacks}
                self._applyStanceDelta(self.balanceDiscBuff, sign=1)
                console.print(f"[asc_arbiter]Arbiter: Consumed {stacks} Balance! +{stacks}% Less Damage Taken, +{self.balanceDiscBuff['thorns']} Thorns while Dedicated Discipline.[/asc_arbiter]")
        elif old == Threshold.DEDICATED:
            if stance == 'aggression':
                self._applyStanceDelta(self.balanceAggroBuff, sign=-1)
                self.balanceAggroBuff = {}
                self.balanceAggroStacks = 0
            else:
                self._applyStanceDelta(self.balanceDiscBuff, sign=-1)
                self.balanceDiscBuff = {}
                self.balanceDiscStacks = 0

    TRANSGRESSOR_SYNC_TIERS = {
        'agg': {'increasedDamage': 0.30, 'lessDamageTaken': 0.10, 'stats': {'crit_chance': 0.05}},
        'disc': {'increasedDamage': 0.20, 'lessDamageTaken': 0.0, 'stats': {'increased_defenses': 20}},
        'both': {'increasedDamage': 0.25, 'lessDamageTaken': 0.0, 'stats': {'crit_chance': 0.10, 'crit_multi': 0.5, 'increased_defenses': 25}},
    }

    def _transgressorCurrentTier(self):
        agg, disc = self.currentAggressionTreshold, self.currentDisciplineThreshold
        if agg == Threshold.DEDICATED and disc == Threshold.DEDICATED:
            return 'both'
        elif agg == Threshold.DEDICATED and disc == Threshold.TRAINED:
            return 'agg'
        elif disc == Threshold.DEDICATED and agg == Threshold.TRAINED:
            return 'disc'
        return None

    def _transgressorRefreshSync(self):
        tier = self._transgressorCurrentTier()
        if tier != self.transgressorSyncTier:
            self._applyStanceDelta(self.transgressorSyncStats, sign=-1)
            newStats = dict(self.TRANSGRESSOR_SYNC_TIERS[tier]['stats']) if tier else {}
            self._applyStanceDelta(newStats, sign=1)
            self.transgressorSyncStats = newStats
            self.transgressorSyncTier = tier
            if tier:
                console.print(f"[asc_transgressor]Transgressor: Dual-Stance synergy active ({tier}).[/asc_transgressor]")

        newThorns = int(0.02 * max(self.armour, self.evasion, self.energyShield)) if tier == 'disc' else 0
        if newThorns != self.transgressorSyncThorns:
            self._stats['Temporary']['thorns'] += (newThorns - self.transgressorSyncThorns)
            self.transgressorSyncThorns = newThorns

    def onCrit(self, targets, combatManager, critDamage):
        if self.currentAggressionTreshold == Threshold.ALL_IN:
            heal = int(critDamage * 0.1)
            self.heal(heal, reason="All-In Aggression (Critical Hit)")
            self.aggressionDamage += self._baseDamage

        if self._ascendancy == 'Transgressor':
            self.stanceCap = min(150, self.stanceCap + 5)

        return critDamage

    def onCriticallyHit(self, attacker, combatManager, critDamage, damageType):
        critDamage = super().onCriticallyHit(attacker, combatManager, critDamage, damageType)
        if self._ascendancy == 'Transgressor':
            self.stanceCap = min(150, self.stanceCap + 5)
        return critDamage

    def onKill(self, entity, attackData, combatManager):
        if self.currentDisciplineThreshold == Threshold.ALL_IN:
            self.disciplineDamage += entity._damage
            heal = int(entity._maxHealth * 0.1)
            self.heal(heal, reason="All-In Discipline (Enemy Killed)")
            console.print(f"[class_fighter]All-In Discipline: Healed {heal} HP and gained +{entity._damage} Damage for the rest of combat.[/class_fighter]")

        if self._ascendancy == 'Triarch':
            base = max(0, max(self.aggression, self.discipline))
            esGain = base * 2 if self.armour > self.evasion else base
            before = self._stats['energy_shield']
            self._stats['energy_shield'] = min(self.maxEnergyShield, before + esGain)
            if self.evasion > self.armour:
                self.heal(base, reason="Triarch (Stronger Stance, Evasion > Armour)")
            console.print(f"[asc_triarch]Triarch: Regenerated {self._stats['energy_shield'] - before} Energy Shield from your stronger Stance.[/asc_triarch]")

        elif self._ascendancy == 'Autarch':
            self.autarchKilledThisTurn = True
            heal = int(entity._maxHealth * 0.1)
            self.heal(heal, reason="Autarch (Enemy Killed)")
            self.autarchBonusDamage += entity._damage
            console.print(f"[asc_autarch]Autarch: Healed {heal} HP and gained +{entity._damage} Damage for the rest of combat.[/asc_autarch]")

        # generic ability.effects.on_kill processing - available to any ascendancy ability
        ability = attackData.get('ability') if attackData else None
        healPct = ability.effects.get('on_kill', {}).get('heal_percent_max_hp', 0) if ability else 0
        if healPct:
            heal = int(self._maxHealth * healPct / 100)
            self.heal(heal, reason=f"{ability.name} (On-Kill Effect)")
            console.print(f"[class_fighter]{ability.name} claims its due! Healed {heal} HP.[/class_fighter]")

        return {}

    def _higherStance(self) -> str:
        if self.aggression > self.discipline:
            return 'aggression'
        elif self.discipline > self.aggression:
            return 'discipline'
        return random.choice(['aggression', 'discipline'])

    def onAbilityCast(self, ability, combatManager):
        if not ability:
            return
        tags = ability.tags
        selfFx = ability.effects.get('self', {})

        if 'gain_higher_stance' in tags:
            amount = selfFx.get('gain_higher_stance', {}).get('amount', 0)
            if amount:
                stance = self._higherStance()
                if stance == 'aggression':
                    self.gainAggression(amount)
                else:
                    self.gainDiscipline(amount)
                console.print(f"[class_fighter]{ability.name}: +{amount} {stance.title()} (your higher stance).[/class_fighter]")

        if 'grants_discipline_on_cast' in tags:
            amount = selfFx.get('grant_discipline', {}).get('amount', 0)
            if amount:
                self.gainDiscipline(amount)

        if 'grants_aggression_on_cast' in tags:
            amount = selfFx.get('grant_aggression', {}).get('amount', 0)
            if amount:
                self.gainAggression(amount)

        if 'commits_to_dominant_stance' in tags:
            fx = selfFx.get('commit_to_dominant', {})
            sacrifice = fx.get('sacrifice_amount', 0)
            gain = fx.get('gain_amount', 0)
            dominant = self._higherStance()
            if dominant == 'aggression':
                self.loseDiscipline(sacrifice, floorBreak=True)
                self.gainAggression(gain)
                console.print(f"[class_fighter]{ability.name}: Sacrificed {sacrifice} Discipline (can go negative) to gain {gain} Aggression.[/class_fighter]")
            else:
                self.loseAggression(sacrifice, floorBreak=True)
                self.gainDiscipline(gain)
                console.print(f"[class_fighter]{ability.name}: Sacrificed {sacrifice} Aggression (can go negative) to gain {gain} Discipline.[/class_fighter]")

        # -- Dissenter -- #
        if 'grants_impatience_on_cast' in tags:
            amount = selfFx.get('grant_impatience', {}).get('amount', 0)
            if amount:
                self.impatience += amount
                console.print(f"[asc_dissenter]{ability.name}: +{amount} Impatience.[/asc_dissenter]")

        # -- Arbiter -- #
        if 'gains_both_stances' in tags:
            amount = selfFx.get('gain_both_stances', {}).get('amount', 0)
            if amount:
                self.gainAggression(amount)
                self.gainDiscipline(amount)

        if 'grants_balance_on_cast' in tags:
            amount = selfFx.get('grant_balance', {}).get('amount', 0)
            if amount:
                self.balance += amount
                console.print(f"[asc_arbiter]{ability.name}: +{amount} Balance.[/asc_arbiter]")

        # -- Transgressor -- #
        if 'expands_stance_cap' in tags:
            amount = selfFx.get('expand_cap', {}).get('amount', 0)
            if amount:
                self.stanceCap = min(150, self.stanceCap + amount)
                console.print(f"[asc_transgressor]{ability.name}: Stance cap raised to {self.stanceCap}.[/asc_transgressor]")

        # -- Autarch -- #
        if 'pact_aligned_gain' in tags:
            amount = selfFx.get('pact_gain', {}).get('amount', 0)
            if amount:
                self.gainAggression(amount)  # Autarch's own gainAggression() already redirects per the active Pact

    def onAttack(self, damageDealt, damageType, target, combatManager, ability, crit):
        damageDealt, damageType = super().onAttack(damageDealt, damageType, target, combatManager, ability, crit)

        if ability and 'rewards_stance_commitment' in ability.tags:
            fx = ability.effects.get('self', {}).get('stance_commitment_bonus', {})
            bonus = 0
            for threshold in (self.currentAggressionTreshold, self.currentDisciplineThreshold):
                if threshold == Threshold.ALL_IN:
                    bonus = max(bonus, fx.get('all_in_percent', 0))
                elif threshold == Threshold.DEDICATED:
                    bonus = max(bonus, fx.get('dedicated_percent', 0))
            if bonus:
                self._logDamage(f"{ability.name} (Stance Commitment Bonus)", percent=bonus / 100)
                damageDealt = int(damageDealt * (1 + (bonus / 100)))

        if ability and self._ascendancy == 'Dissenter' and 'consumes_impatience_finisher' in ability.tags and self.impatience > 0:
            stacksConsumed = self.impatience
            dmgPerStack = ability.effects.get('self', {}).get('consume_impatience', {}).get('damage_per_stack', 0) / 100
            self.impatience = 0
            self._logDamage(f"{ability.name} (Consumed {stacksConsumed} Impatience)", percent=dmgPerStack * stacksConsumed)
            damageDealt = int(damageDealt * (1 + (dmgPerStack * stacksConsumed)))
            console.print(f"[asc_dissenter]{ability.name}: Consumes {stacksConsumed} Impatience for +{int(dmgPerStack * stacksConsumed * 100)}% Damage.[/asc_dissenter]")

        if ability and self._ascendancy == 'Arbiter' and 'consumes_balance_finisher' in ability.tags and self.balance > 0:
            stacksConsumed = self.balance
            dmgPerStack = ability.effects.get('self', {}).get('consume_balance', {}).get('damage_per_stack', 0) / 100
            self.balance = 0
            self._logDamage(f"{ability.name} (Consumed {stacksConsumed} Balance)", percent=dmgPerStack * stacksConsumed)
            damageDealt = int(damageDealt * (1 + (dmgPerStack * stacksConsumed)))
            console.print(f"[asc_arbiter]{ability.name}: Consumes {stacksConsumed} Balance for +{int(dmgPerStack * stacksConsumed * 100)}% Damage.[/asc_arbiter]")

        if ability and self._ascendancy == 'Transgressor' and 'rewards_sync_tier' in ability.tags:
            fx = ability.effects.get('self', {}).get('sync_tier_bonus', {})
            tier = self._transgressorCurrentTier()
            bonusMap = {'agg': 'agg_percent', 'disc': 'disc_percent', 'both': 'both_percent'}
            if tier and fx.get(bonusMap[tier]):
                self._logDamage(f"{ability.name} (Sync Tier: {tier}, Transgressor)", percent=fx[bonusMap[tier]] / 100)
                damageDealt = int(damageDealt * (1 + (fx[bonusMap[tier]] / 100)))

        if ability and self._ascendancy == 'Triarch' and 'defense_scaling_damage' in ability.tags:
            fx = ability.effects.get('self', {}).get('defense_scaling', {})
            perHundred = fx.get('percent_per_100', 0)
            totalDefense = self.armour + self.evasion + self.energyShield
            if perHundred and totalDefense:
                self._logDamage(f"{ability.name} (Defense Scaling, Triarch)", percent=(perHundred / 100) * (totalDefense / 100))
                damageDealt = int(damageDealt * (1 + (perHundred / 100) * (totalDefense / 100)))

        if ability and self._ascendancy == 'Triarch' and 'consumes_energy_shield_finisher' in ability.tags and self.energyShield > 0:
            fx = ability.effects.get('self', {}).get('consume_es', {})
            spent = int(self.energyShield * (fx.get('percent_spent', 0) / 100))
            if spent > 0:
                self._stats['energy_shield'] -= spent
                self._logDamage(f"{ability.name} (Energy Shield Consumed, Triarch)", percent=(fx.get('damage_multiplier', 100) / 100) - 1)
                damageDealt = int(damageDealt * (fx.get('damage_multiplier', 100) / 100))
                heal = int(spent * (fx.get('heal_percent_of_spent', 0) / 100))
                if heal:
                    self.heal(heal, reason=f"{ability.name} (Energy Shield Consumed)")
                console.print(f"[asc_triarch]{ability.name}: Spends {spent} Energy Shield for a devastating blow.[/asc_triarch]")

        if ability and self._ascendancy == 'Autarch' and 'rewards_current_pact' in ability.tags and self.autarchPact:
            fx = ability.effects.get('self', {}).get('pact_bonus', {})
            bonus = fx.get(f'{self.autarchPact}_percent', 0)
            if bonus:
                self._logDamage(f"{ability.name} (Pact of {self.autarchPact.title()}, Autarch)", percent=bonus / 100)
                damageDealt = int(damageDealt * (1 + (bonus / 100)))

        aggGain = 3 + (damageDealt // (10 * (1 + self._level // 10)))
        self.gainAggression(aggGain)

        if self.currentAggressionTreshold != Threshold.NEUTRAL and damageType == 'physical':
            if self.currentAggressionTreshold == Threshold.COMPLACENT:
                self._logDamage("Complacent Aggression", percent=-0.3)
                damageDealt = int(damageDealt * 0.7)
            elif self.currentAggressionTreshold == Threshold.TRAINED:
                self._logDamage("Trained Aggression", percent=0.2)
                damageDealt = int(damageDealt * 1.2)
            elif self.currentAggressionTreshold == Threshold.DEDICATED:
                self._logDamage("Dedicated Aggression", percent=0.5)
                damageDealt = int(damageDealt * 1.5)
            elif self.currentAggressionTreshold == Threshold.ALL_IN:
                if self.aggressionDamage:
                    self._logDamage("All-In Aggression (Bonus Damage from Crits)", flat=self.aggressionDamage)
                damageDealt += self.aggressionDamage
                if self._ascendancy == 'Dissenter':
                    if self.impatienceAggroDamage:
                        self._logDamage("All-In Aggression (Impatience, Dissenter)", flat=self.impatienceAggroDamage)
                    damageDealt += self.impatienceAggroDamage
                self._logDamage("All-In Aggression (Doubled Damage)", percent=1.0)
                damageDealt *= 2

        if self.currentDisciplineThreshold == Threshold.ALL_IN:
            if self.disciplineDamage:
                self._logDamage("All-In Discipline (Bonus Damage from Kills)", flat=self.disciplineDamage)
            damageDealt += self.disciplineDamage

        if damageType == 'physical':
            if self._ascendancy == 'Arbiter' and (self.balance or self.balanceAggroStacks):
                self._logDamage(f"Balance ({self.balance + self.balanceAggroStacks} stacks, Arbiter)", percent=0.05 * (self.balance + self.balanceAggroStacks))
                damageDealt = int(damageDealt * (1 + 0.05 * (self.balance + self.balanceAggroStacks)))
            elif self._ascendancy == 'Transgressor' and self.transgressorSyncTier:
                self._logDamage(f"Dual-Stance Synergy ({self.transgressorSyncTier}, Transgressor)", percent=self.TRANSGRESSOR_SYNC_TIERS[self.transgressorSyncTier]['increasedDamage'])
                damageDealt = int(damageDealt * (1 + self.TRANSGRESSOR_SYNC_TIERS[self.transgressorSyncTier]['increasedDamage']))
            elif self._ascendancy == 'Triarch' and self.armour >= 25:
                self._logDamage("Armour (Triarch)", percent=0.02 * (self.armour // 25))
                damageDealt = int(damageDealt * (1 + 0.02 * (self.armour // 25)))

        if self._ascendancy == 'Autarch' and self.autarchBonusDamage:
            self._logDamage("Bonus Damage from Kills (Autarch)", flat=self.autarchBonusDamage)
            damageDealt += self.autarchBonusDamage

        return damageDealt, damageType

    def onHit(self, damageTaken, damageType, crit=False, attacker=None, combatManager=None):
        damageTaken, damageType = super().onHit(damageTaken, damageType, crit, attacker, combatManager)

        disGain = damageTaken // (8 * (1 + self._level // 11))
        self.gainDiscipline(disGain)

        if self.currentDisciplineThreshold != Threshold.NEUTRAL:
            if self.currentDisciplineThreshold == Threshold.DEDICATED:
                attacker._logDamage(f"{self._name}'s Dedicated Discipline", percent=-0.15)
                damageTaken = int(damageTaken * 0.85)
            elif self.currentDisciplineThreshold == Threshold.ALL_IN:
                attacker._logDamage(f"{self._name}'s All-In Discipline", percent=-0.4)
                damageTaken = int(damageTaken * 0.6)

        if self._ascendancy == 'Arbiter':
            if self.currentDisciplineThreshold == Threshold.TRAINED:
                attacker._logDamage(f"{self._name}'s Trained Discipline (Arbiter)", percent=-0.05)
                damageTaken = int(damageTaken * 0.95)
            if self.balance or self.balanceDiscStacks:
                attacker._logDamage(f"{self._name}'s Balance ({self.balance + self.balanceDiscStacks} stacks, Arbiter)", percent=-(0.01 * (self.balance + self.balanceDiscStacks)))
                damageTaken = int(damageTaken * (1 - 0.01 * (self.balance + self.balanceDiscStacks)))
        elif self._ascendancy == 'Transgressor' and self.transgressorSyncTier == 'agg':
            attacker._logDamage(f"{self._name}'s Dual-Stance Synergy (Transgressor)", percent=-self.TRANSGRESSOR_SYNC_TIERS['agg']['lessDamageTaken'])
            damageTaken = int(damageTaken * (1 - self.TRANSGRESSOR_SYNC_TIERS['agg']['lessDamageTaken']))

        return damageTaken, damageType

    def _autarchChoosePact(self) -> str:
        options = ['aggression', 'discipline']
        if self.currentAggressionTreshold == Threshold.DEDICATED or self.currentDisciplineThreshold == Threshold.DEDICATED:
            options.append('balance')
        if self.currentAggressionTreshold == Threshold.ALL_IN or self.currentDisciplineThreshold == Threshold.ALL_IN:
            options.append('purging')

        labels = {'aggression': 'Pact of Aggression', 'discipline': 'Pact of Discipline', 'balance': 'Pact of Balance', 'purging': 'Pact of Purging'}
        console.print("[asc_autarch]Autarch: Choose a Pact for this turn:[/asc_autarch]")
        for i, opt in enumerate(options, 1):
            console.print(f"  {i}. {labels[opt]}")
        choice = console.input("[cyan]> [/cyan]").strip()
        try:
            idx = int(choice) - 1
            if 0 <= idx < len(options):
                return options[idx]
        except ValueError:
            pass
        return options[0]

    def onTurnStart(self, combatManager=None):
        if self._ascendancy == 'Dissenter':
            if self.currentAggressionTreshold != Threshold.ALL_IN and self.currentDisciplineThreshold != Threshold.ALL_IN:
                self.impatience += 1
                console.print(f"[asc_dissenter]Dissenter: Gained 1 Impatience! ({self.impatience})[/asc_dissenter]")

            if self.impatience > 0:
                gain = self.impatience * 2
                if self.aggression >= self.discipline:
                    console.print(f"  [asc_dissenter]Impatience: +{gain} Aggression progress.[/asc_dissenter]")
                    self.gainAggression(gain)
                else:
                    console.print(f"  [asc_dissenter]Impatience: +{gain} Discipline progress.[/asc_dissenter]")
                    self.gainDiscipline(gain)

        elif self._ascendancy == 'Arbiter':
            if self.currentAggressionTreshold == Threshold.TRAINED and self.currentDisciplineThreshold == Threshold.TRAINED:
                self.balance += 1
                console.print(f"[asc_arbiter]Arbiter: Gained 1 Balance! ({self.balance})[/asc_arbiter]")

        elif self._ascendancy == 'Transgressor':
            self.stanceCap = min(150, self.stanceCap + 10)
            self._transgressorRefreshSync()

        elif self._ascendancy == 'Triarch':
            newHpRegen = self.energyShield // 25
            self._stats['Temporary']['hp_regen'] += (newHpRegen - self.triarchHpRegenBonus)
            self.triarchHpRegenBonus = newHpRegen

            newCapBonus = min(25, self.maxEnergyShield // 50)
            self.stanceCap += (newCapBonus - self.triarchCapBonus)
            self.triarchCapBonus = newCapBonus

        elif self._ascendancy == 'Autarch':
            if self.autarchPact == 'purging' and not self.autarchKilledThisTurn:
                penalty = int(self._maxHealth * 0.25)
                console.print(f"[asc_autarch]Autarch: Pact of Purging unfulfilled - no kill last turn! Taking {penalty} Physical Damage.[/asc_autarch]")
                self.damage(penalty, 'physical', lethal=False)
            self.autarchKilledThisTurn = False
            self.autarchPact = self._autarchChoosePact()
            console.print(f"[asc_autarch]Autarch: {self.autarchPact.title()} Pact is now active.[/asc_autarch]")
            self._refreshStanceEffects()

        self.gainAggression(5)
        self.gainDiscipline(5)

        super().onTurnStart(combatManager)

    def onCombatStart(self, combatManager, combatUnit):
        super().onCombatStart(combatManager, combatUnit)
        if self._ascendancy == 'Triarch':
            self.triarchCapBonus = min(25, self.maxEnergyShield // 50)
            self.stanceCap += self.triarchCapBonus
        self.gainAggression(25)
        self.gainDiscipline(25)

    def onCombatEnd(self):
        self._applyStanceDelta(self._appliedAggressionDelta, sign=-1)
        self._applyStanceDelta(self._appliedDisciplineDelta, sign=-1)
        self._appliedAggressionDelta = {}
        self._appliedDisciplineDelta = {}
        self.aggression = 0
        self.currentAggressionTreshold = Threshold.NEUTRAL
        self.aggressionDamage = 0
        self.discipline = 0
        self.currentDisciplineThreshold = Threshold.NEUTRAL
        self.disciplineDamage = 0
        self.stanceCap = 100

        if self._ascendancy == 'Dissenter':
            self._applyStanceDelta(self.impatienceAggroBuff, sign=-1)
            self._applyStanceDelta(self.impatienceDiscBuff, sign=-1)
            self.impatience = 0
            self.impatienceAggroBuff = {}
            self.impatienceAggroDamage = 0
            self.impatienceDiscBuff = {}

        elif self._ascendancy == 'Arbiter':
            self._applyStanceDelta(self.balanceAggroBuff, sign=-1)
            self._applyStanceDelta(self.balanceDiscBuff, sign=-1)
            self.balance = 0
            self.balanceAggroStacks = 0
            self.balanceAggroBuff = {}
            self.balanceDiscStacks = 0
            self.balanceDiscBuff = {}

        elif self._ascendancy == 'Transgressor':
            self._applyStanceDelta(self.transgressorSyncStats, sign=-1)
            self._stats['Temporary']['thorns'] -= self.transgressorSyncThorns
            self.transgressorSyncTier = None
            self.transgressorSyncStats = {}
            self.transgressorSyncThorns = 0

        elif self._ascendancy == 'Triarch':
            self._stats['Temporary']['hp_regen'] -= self.triarchHpRegenBonus
            self.triarchHpRegenBonus = 0
            self.triarchCapBonus = 0

        elif self._ascendancy == 'Autarch':
            self.autarchPact = None
            self.autarchKilledThisTurn = False
            self.autarchBonusDamage = 0

        super().onCombatEnd()

    def _recalculateStats(self, doPrint=True, inCombat=False):
        super()._recalculateStats(doPrint, inCombat)
        if self._ascendancy == 'Triarch':
            armour0 = self._stats['armour']
            evasion0 = self._stats['evasion']
            es0 = self._stats['max_energy_shield']
            if armour0 > 0 and evasion0 > 0 and es0 > 0:
                fromArmour = int(0.1 * armour0)
                fromEvasion = int(0.1 * evasion0)
                fromEs = int(0.2 * es0)
                self._stats['armour'] += fromEvasion + fromEs
                self._stats['evasion'] += fromArmour + fromEs
                self._stats['max_energy_shield'] += fromArmour + fromEvasion
                if not inCombat:
                    self._stats['energy_shield'] = self._stats['max_energy_shield']
                if doPrint:
                    console.print(f"[asc_triarch]Triarch: Converted defenses - +{fromEvasion + fromEs} Armour, +{fromArmour + fromEs} Evasion, +{fromArmour + fromEvasion} Energy Shield.[/asc_triarch]")

    def rollCritical(self, target, damageDealt=None):
        if self._ascendancy == 'Triarch':
            critChance = self.critChance + 0.002 * (self.evasion // 30)
            critMulti = self.critMulti + 0.01 * (self.evasion // 30)
            if random.random() < critChance:
                return True, critMulti
            return False, 1.0
        return super().rollCritical(target, damageDealt)

    def _triarchHasAllDefenses(self) -> bool:
        return self.armour > 0 and self.evasion > 0 and self.maxEnergyShield > 0

    def getEffectiveArmour(self, damageType, combatUnit):
        if self._ascendancy == 'Triarch' and damageType in OTHERWORLD_RES and self._triarchHasAllDefenses():
            return self.armour * 1.5
        return super().getEffectiveArmour(damageType, combatUnit)

    def getEvasionRollCount(self, damageType) -> int:
        if self._ascendancy == 'Triarch' and damageType in OTHERWORLD_RES and self._triarchHasAllDefenses():
            return 2
        return super().getEvasionRollCount(damageType)

    def onAfterMitigation(self, attacker, finalDamage, damageType, evaded, armourDamagePrevented, esDamagePrevented, preMitigationDamage, combatManager):
        finalDamage = super().onAfterMitigation(attacker, finalDamage, damageType, evaded, armourDamagePrevented, esDamagePrevented, preMitigationDamage, combatManager)
        if self._ascendancy == 'Triarch' and damageType in OTHERWORLD_RES and self._triarchHasAllDefenses() and esDamagePrevented > 0:
            self.heal(esDamagePrevented, reason="Triarch (Energy Shield Absorption)")
            console.print(f"[asc_triarch]Triarch: Healed {esDamagePrevented} HP from Energy Shield absorption.[/asc_triarch]")
        return finalDamage

    ASCENDANCY_DELTAS = {
        'Dissenter': {
            '_baseHealth': -5,
            '_baseDamage': 10,
            '_baseSpeed': 0.05,
            '_stats.baseCritMulti': 0.25,
            '_stats.Permanent.increased_defenses': 5,
        },
        'Arbiter': {
            '_baseHealth': 25,
            '_baseDamage': 8,
            '_baseSpeed': -0.1,
            '_stats.Permanent.physical': 15,
        },
        'Transgressor': {
            '_baseHealth': 5,
            '_baseDamage': 2,
            '_baseSpeed': 0.15,
            '_stats.baseCritChance': 0.05,
            '_stats.Permanent.ailment_avoidance': 25,
        },
        'Triarch': {
            '_baseHealth': 5,
            '_baseDamage': 10,
            '_stats.Permanent.increased_defenses': 10,
        },
        'Autarch': {
            '_baseHealth': 25,
            '_baseDamage': 7,
            '_baseSpeed': -0.1,
            '_stats.Permanent.physical': 10,
            '_stats.Permanent.divine': 5,
        },
    }

    def _removeOldAscendancy(self):
        delta = self.ASCENDANCY_DELTAS.get(self._ascendancy)
        if delta:
            self._applyStatDelta(delta, sign=-1)
        return True

    def updateAscendancy(self, ascendancy):
        if not super().updateAscendancy(ascendancy):
            return
        self._ascendancy = ascendancy
        self.ascendancyDescription = FIGHTER_DESCRIPTIONS[ascendancy]
        self._applyStatDelta(self.ASCENDANCY_DELTAS[ascendancy], sign=1)
        self._recalculateStats()
        self.gainClassAbilities()
        return True

...