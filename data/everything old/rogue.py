from .base import Player, Entity
from scripts.styles import console

ROGUE_DESCRIPTIONS = {
    "Rogue": "A swift assassin who thrives on speed and precision.\n"
        "Gain Siphon when hitting an enemy, up to 10 Stacks of Siphon. Each stack of Siphon grants +3% Lifesteal for the rest of combat.\n"
        "Starting Stats: 35 Health | 6 Damage | 10% Crit Chance | 150% Crit Damage | Dark Damage | 1.05 Speed.",
    #ascendancies
    "Assassin": "Attacks with First Strike now deal 3x damage instead. If a First Strike kills an enemy, heal for 10% of their Max HP.\n"
        "When a First Strike deals more than 500 damage, all enemies gain Exposed and Withered.\n"
        "-20 HP. -2 Damage. +10% Crit Chance. +50% Crit Multiplier.",
    "Shadow": "Poison and Venom deals 200% More Damage to enemies. Apply twice as many stacks of Poison and Venom to enemies.\n"
        "You are unable to apply Damage over Time effects apart from Poison and Venom. Take 50% Less Damage from Poison and Venom.\n"
        "+5 HP. -2 Damage. +0.1 Speed. -10% Holy Resistance. +10% DoT Resistance.",
    "Trickster": "Siphon also grants 5% More Evasion per 2% Siphon. Whenever you avoid an ailment, it is reflected onto the attacker.\n"
        "Upon Evading an attack, gain Haste: +0.2 Speed, 10% More Damage dealt for 2 turns.\n"
        "-10 HP. +1 Damage. +0.1 Speed. +10% Ailment Avoidance. -15% DoT Resistance.",
    "Nightblade": "All attacks instead attack twice for 75% damage each. Siphon has a maximum of 15 Stacks.\n"
        "Upon taking lethal damage, remove all Siphon stacks and heal 2% of Max HP per Siphon Stack used. This effect can only occur once per combat. Healing is applied before damage is taken.\n"
        "-15 HP. +2 Damage. +0.05 Speed. +25% Crit Damage.",
    "Voidwalker": "Each stack of Siphon also grants 3% More Dark Damage dealt. Upon reaching Max Siphon, lose all stacks to gain Planewalker for the rest of combat.\n"
        "Planewalker: 50% of Dark Damage dealt is applied as Shield to you. Holy Damage will bypass your shield and set it to 0.\n"
        "-10 HP. -2 Damage. +0.1 Speed. +5% Crit Chance.",
    #subtypes
    "Duelist": "Siphon no longer grants lifesteal. Gain Riposte: 25% Chance to Retaliate on getting hit and deal 50% of your damage to the attacker.\n"
        "Upon attacking, gain Primed: The next enemy you Retaliate against will be afflicted by Weaken.\n"
        "+5 HP. +2 Damage. +0.15 Speed. +50% Crit Damage.",
    "Vanguard": "Each stack of Siphon also grants +1% All Res. First Strike skills now also grant you Guardian.\n"
        "If you lose more than 30% of your Max HP in a single combat, deal 50% of your remaining health as Dark Damage to all enemies. This damage does not trigger on-hit or on-attack effects.\n"
        "+15 HP. -1 Damage. -0.15 Speed. +3% Crit Chance. +75% Crit Damage.",
    "Shade": "Each stack of Siphon causes you to take 2% More Damage. Upon killing an enemy, lose up to 3 stacks of Siphon to heal for 3% of your Max HP per stack.\n"
        "Max Siphon stacks is 15. Whilst you have more than 10 Siphon Stacks, gain 15% More Damage dealt.\n"
        "-10 HP. +1 Damage. +5% Crit Chance. +25% Crit Damage. +10% Dark Resistance.",
}

class Rogue(Player): # higher speed + damage, lower health, dark damage
    def __init__(self, name, health = 35, damage = 6, damageType = "dark", speed = 1.05):
        super().__init__(name, health, damage, 0.1, 1.5, damageType, speed, className="Rogue", classDescription=ROGUE_DESCRIPTIONS['Rogue'])
        self.siphon = 0
        self.maxSiphon = 10

        self.planewalkerActive = False
        self.hasteTurns = 0
        self.primed = False
        self.nightbladeReviveUsed = False
        self.combatHealthLost = 0
        self.vanguardUsed = False

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

    def onEvade(self):
        if self._ascendancy == 'Trickster':
            self.hasteTurns = 2
            console.print(f"\n    [buff]- Trickster: Gained 2 turns of haste for dodging! +0.2 Speed, +10% Damage.[/buff]")

    def onAttack(self, damageDealt, damageType):
        super().onAttack(damageDealt, damageType)
        if self._subType != 'Duelist':
            if self._health < self._maxHealth and self.siphon:
                heal = round(damageDealt * (self._stats['Temporary']['lifesteal'] * 3))
                self.heal(heal)

        self.siphon = min(self.siphon + 1, self.maxSiphon)
        self._stats['Temporary']['lifesteal'] = self.siphon * 3

        if self._subType != 'Duelist':
            console.print(f"\n[buff]Siphon: {self.siphon} / {self.maxSiphon} stacks. +{self.siphon * 3}% Lifesteal.[/buff]")
        else:
            self.primed = True
            console.print(f"  [buff]Duelist primed for Riposte.[/buff]")
            console.print(f"\n[buff]Sihpon: {self.siphon} / {self.maxSiphon} stacks.")

        if self._ascendancy == 'Trickster':
            evasionBonus = int((self.siphon * 3) / 2) * 0.05
            self._stats['Temporary']['increased_evasion'] += evasionBonus
            console.print(f"\n[buff]Trickster: +{int(evasionBonus * 100)}% Evasion from Siphon.[/buff]")
            if self.hasteTurns > 0:
                damageDealt = int(damageDealt * 1.1)

        elif self._ascendancy == 'Voidwalker':
            darkBonus = self.siphon * 0.03
            if damageType == 'dark':
                console.print(f"\n[buff]Planewalker: Dealt {darkBonus * 100}% increased damage for dark damage.[/buff]")
                damageDealt = int(damageDealt * 1 + darkBonus)

            if self.siphon >= self.maxSiphon and not self.planewalkerActive:
                self.planewalkerActive = True
                self.siphon = 0
                console.print(f"\n[gold1]Voidwalker: Max Siphon reached! Planewalker activated, siphon set to 0.[/gold1]")
                console.print(f"  [gold1]- 50% of Dark damage dealt is gained as Shield. Holy damage sets shield to 0.[/gold1]")
            
            if damageType == 'dark' and self.planewalkerActive:
                shieldGain = int(damageDealt * 0.5)
                self._shield += shieldGain
                console.print(f"  [buff]Planewalker: Gained {shieldGain} Shield from Dark damage![/buff]")

        if self._subType == 'Vanguard':
            allRes = self.siphon
            self._stats['Temporary']['all'] = allRes
        elif self._subType == 'Shade' and self.siphon > 10:
            damageDealt = int(damageDealt * 1.15)
            console.print(f"  [buff]Shade: High Siphon! +15% Damage dealt.[/buff]")

        return damageDealt, damageType

    def onHit(self, damageTaken, damageType):
        super().onHit(damageTaken, damageType)
        if self._subType == 'Duelist' and self.primed:
            self.primed = False
        
        elif self._subType == 'Vanguard':
            self.combatHealthLost += damageTaken

        elif self._subType == 'Shade' and self.siphon > 0:
            moreModifier = self.siphon * 0.02
            damageTaken = int(damageTaken * (1 + moreModifier))
            console.print(f"  [warning]Shade: Taking {int(moreModifier * 100)}% More damage from siphon stacks.[/warning]")

        if self._ascendancy == 'Voidwalker' and self.planewalkerActive and damageType == 'holy':
            self._shield = 0
            console.print(f"\n[warning]Voidwalker: Holy Damage bypassed and removed all shield![/warning]")

    def onBattleEnd(self):
        super().onBattleEnd()
        self.siphon = 0
        self.planewalkerActive = False
        self.nightbladeReviveUsed = False
        self.hasteTurns = 0

        self._stats['Temporary']['lifesteal'] = 0
        self._stats['Temporary']['increased_evasion'] = 0
        self._stats['Temporary']['speed'] = 0
        self._stats['Temporary']['all'] = 0

    def onTurnStart(self):
        if self._ascendancy == 'Trickster' and self.hasteTurns > 0:
            self._stats['Temporary']['speed'] = 0.2
            self.hasteTurns -= 1
            if self.hasteTurns == 0:
                self._stats['Temporary']['speed'] = 0
                console.print(f"\n[dim]Haste has expired.[/dim]")

    def onKill(self, entity: Entity, attackData):
        if self._ascendancy == 'Assassin' and 'first_strike' in attackData['mechanics']:
            heal = int(entity._maxHealth * 0.1)
            console.print('  [heal]- Asssassin: First Strike killed enemy! Healed for 10% of their Max HP.[/heal]')
            self.heal(heal)
        if self._subType == 'Shade' and self.siphon > 0:
            consume = min(3 , self.siphon)
            self.siphon -= consume
            heal = int(self._maxHealth * consume * 0.03)
            console.print(f'  [heal]- Shade: Consumed {consume} stacks of Siphon to heal for {heal} HP.[/heal]')
            self.heal(heal)
        return None

    def damage(self, damage, damageType, combatUnit=None):
        if self._ascendancy == 'Nightblade' and self.siphon > 0:
            if self._health - damage <= 0:
                healAmount = int(self._maxHealth * 0.02 * self.siphon)
                siphonUsed = self.siphon
                self.siphon = 0
                console.print(f"\n[success]Nightblade: Lethal damage taken! Consumed {siphonUsed} Siphon stacks to heal {healAmount} HP.[/success]")
                self.heal(healAmount)

        return super().damage(damage, damageType, combatUnit)

    def updateAscendancy(self, ascendancy):
        if ascendancy == 'Assassin':
            self._baseHealth -= 20
            self._baseDamage -= 2
            self._stats['baseCritChance'] += 0.1
            self._stats['baseCritMulti'] += 0.5
            self._ascendancy = 'Assassin'
            self.ascendancyDescription = ROGUE_DESCRIPTIONS['Assassin']
        elif ascendancy == 'Shadow':
            self._baseHealth += 5
            self._baseDamage -= 2
            self._baseSpeed += 0.1
            self._stats['Permanent']['holy'] -= 10
            self._stats['Permanent']['dotResistance'] += 10
            self._ascendancy = 'Shadow'
            self.ascendancyDescription = ROGUE_DESCRIPTIONS['Shadow']
        elif ascendancy == 'Trickster':
            self._baseHealth -= 10
            self._baseDamage += 1
            self._baseSpeed += 0.1
            self._stats['Permanent']['ailmentAvoidance'] += 10
            self._stats['Permanent']['dotResistance'] -= 15
            self._ascendancy = 'Trickster'
            self.ascendancyDescription = ROGUE_DESCRIPTIONS['Trickster']
        elif ascendancy == 'Nightblade':
            self._baseHealth -= 15
            self._baseDamage += 2
            self._baseSpeed += 0.05
            self._stats['baseCritMulti'] += 0.25
            self._ascendancy = 'Nightblade'
            self.ascendancyDescription = ROGUE_DESCRIPTIONS['Nightblade']
        elif ascendancy == 'Voidwalker':
            self._baseHealth -= 10
            self._baseDamage -= 2
            self._baseSpeed += 0.1
            self._stats['baseCritChance'] += 0.1
            self._ascendancy = 'Voidwalker'
            self.ascendancyDescription = ROGUE_DESCRIPTIONS['Voidwalker']
        self._recalculateStats(False)

    def updateSubType(self, subType):
        if subType == 'Duelist':
            self._baseHealth += 5
            self._baseDamage += 2
            self._baseSpeed += 0.15
            self._stats['baseCritMulti'] += 0.5
            self._subType = 'Duelist'
            self.subTypeDescription = ROGUE_DESCRIPTIONS['Duelist']
        elif subType == 'Vanguard':
            self._baseHealth += 15
            self._baseDamage -= 1
            self._baseSpeed -= 0.15
            self._stats['baseCritChance'] += 0.03
            self._stats['baseCritMulti'] += 0.75
            self._subType = 'Vanguard'
            self.subTypeDescription = ROGUE_DESCRIPTIONS['Vanguard']
        elif subType == 'Shade':
            self._baseHealth -= 10
            self._baseDamage += 1
            self._stats['baseCritChance'] += 0.05
            self._stats['baseCritMulti'] += 0.25
            self._stats['Permanent']['dark'] += 10
            self._subType = 'Shade'
            self.subTypeDescription = ROGUE_DESCRIPTIONS['Shade']
        self._recalculateStats(False)

# Assassin = 1-shot 10 enemies from full hp to 0
# Shadow = have 20+ DoT on a single enemy at once
# Trickster = avoid 25 total ailments
# Nightblade: use multi-target skills 10 times in 1 combat
# Voidwalker = use 20 dark-type abilities in a single combat
# Duelist = don't use a consumable or healing item in 3 consecutive combats
# Vanguard = end 5 battles at max hp
# Shade = lifesteal to max hp 10 times
