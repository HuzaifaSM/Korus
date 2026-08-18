from .base import Player
from scripts.styles import console, pause
import random

MARAUDER_DESCRIPTIONS = {
    "Marauder": "[class_marauder]A ruthless hunter, pillaging its foes whilst fighting and forcing their hand.[/class_marauder]\n"
        "- If you attack an enemy who has already acted, apply Echo to them, dealing damage equal to 35% of the damage dealt. Echo activates at the start of your turn and deals Cold damage.\n"
        "- If you attack an enemy before they have acted, Siphon 1-3 of their base Damage. You cannot steal Damage equal to more than your 1.5x level, rounded up. You cannot reduce an enemy's base damage below 5.\n"
        "- If an enemy attacks you before you have acted, they steal 1 Siphoned Damage back if possible.\n"
        "- If an enemy fails to steal Siphoned Damage from you, gain +1 Damage Reduction for the rest of combat, up to a maximum equal to 2x your level.\n"
        "- If an enemy attacks you after you have acted, they deal 10% Less Damage to you. At the end of combat, heal 1% Max HP per Siphoned Damage, to a maximum heal of 30%.\n"
        "[bold]Starting Stats:[/bold] 60 HP | 4 Damage | 4% Crit Chance | 130% Crit Damage | Cold Damage | 0.8 Speed.",
    # ascendancies
    "Colossus": "[lore]Dodge? Their hits do nothing. Stand your ground, and trample over theirs. Every strike is a statement of dominance.[/lore]\n"
        "- Convert 50% of your Evasion into Armour, and 10% of your Evasion as Energy Shield. You have no Evasion.\n"
        "- The first time your Energy Shield is broken in combat, gain 1% Increased Damage per 5 Maximum Energy Shield you have for the rest of combat. Elemental damage against you treats your armour as 130% of its value.\n"
        "- If an enemy attacks you before you have acted, your next attack gains damage equal to damage prevented by Armour and Energy Shield by that hit.\n"
        "- If you attack an enemy after they have acted, apply stack of 1 Crush, to a maximum of 3 stacks. Crush: 15% Reduced Armour.\n"
        "- Damage dealt from Echo is reduced to 15% of the damage dealt, but is applied as True damage instead of Cold.\n"
        "- Upon killing an enemy, for the rest of combat: Gain 20% of their Armour as Added Armour, Regenerate Energy Shield equal to 10% of their Armour or Max Energy Shield, whichever is higher.\n"
        "[bold]Stat Changes:[/bold] -15 HP. +4 Damage. -0.2 Speed. +100 Armour. +20 Energy Shield.",
    "Dreadnought": "[lore]Might. That's all that matters on the battlefield. Each wound heals before it opens. Each scar amplifies your strength. Each hit, another reason to decimate them.[/lore]\n"
        "- 20% Increased Maximum Life. Convert 10% of your Armour and Evasion, and 20% of your Maximum Energy Shield into Max Health.\n"
        "- When an attack reduces your health, 50% of the damage is Deferred. Deferred damage is dealt to you 1 turn later as Cold Damage.\n"
        "- Gain 20% of Deferred damage as bonus damage for the rest of combat, to a maximum equal to 30% of your Max HP.\n"
        "- If an enemy attacks you before you have acted, if their current Health is less than your current Health, the damage is reduced by 15% and they automatically fail to steal Siphoned Damage.\n"
        "- If an enemy attacks you after you have acted, they take True Damage equal to 5% of your Max HP, and you heal for the same amount.\n"
        "- Healing has a 30% chance to Echo, applying its heal again at the start of your next turn at 50% value.\n"
        "- If you attack an enemy after before have acted, heal for 10% of the damage dealt, and Siphon up to twice as much damage if possible.\n"
        "[bold]Stat Changes:[/bold] +30 Health. -5 Damage. -0.1 Speed. +50% Healing Magnitude. +15% Cold Resistance. +5% Maximum Cold Resistance.",
    "Sovereign": "[lore]You sit atop the throne of war. Each move flawless and unforgiving. Their pride will be their end.[/lore]\n"
        "- If you attack an enemy after they have acted, deal 25% Increased Cold Damage, heal for 10% of the damage dealt to them, and reduce their base speed by 1% of your speed.\n"
        "- If you attack an enemy before they have acted, gain +25% Crit Chance and +75% Crit Damage against them.\n"
        "- If an enemy attacks you before you have acted, apply Shame to them for 2 turns. Shame: Deal 10% Less Damage, -0.1 Speed.\n"
        "- If an enemy attacks you after you have acted, they deal 20% Less Damage to you, increased to 30% Less Damage if the damage is Divine.\n"
        "[bold]Stat Changes:[/bold] +15 HP. +4 Damage. -0.1 Speed. +5 Stamina Regen. +10% Holy Resistance.",
    "Harrower": "[lore]Their strength is useless. Cripple them instead. Rain blows upon them. Steal even their ability to flee.[/lore]\n"
        "- Siphon Speed instead of Damage. You can Siphon up to 0.5 Speed total. Siphon 0.02 Speed per 1 Damage that would have been Siphoned. Enemies cannot steal Siphoned Speed.\n"
        "- If you have Siphoned more than 0.25 Speed, gain 40% Increased Damage, 10% Elemental Resistance and 20% Physical Resistance.\n"
        "- If you attack an enemy before they have acted, they are executed if they have less than 8% Max HP remaining. Executing an enemy grants you Empowerment for the rest of combat.\n"
        "- Empowerment: +30% Increased Cold Damage, +20 HP Regen, -0.2 Speed.\n"
        "- If an enemy attacks you after you have acted, their Speed is reduced by 5%, and they take Cold Damage equal to their base damage.\n"
        "- If an enemy attacks you before you have acted, their hit treats your Evasion as 150% of its actual value.\n"
        "[bold]Stat Changes:[/bold] -15 HP. +6 Damage. +0.1 Speed. +5% Crit Chance. +25% Crit Damage.",
    "Butcher": "[lore]Their fear tastes so sweet. Revel in delight as you carve them up, one by one. Watch as they cower in fear.[/lore]\n"
        "- At the start of combat, apply Marked to a random enemy. Marked: 25% Increased Damage Taken, 10% Increased Damage Dealt.\n"
        "- When you kill a Marked enemy, Siphon all of its base damage, ignoring your cap, and deal Cold Damage to all enemies equal to 500% of the killed enemy's base damage.\n"
        "- Mark a new random enemy when the current Marked enemy dies.\n"
        "- Upon dealing a critical hit, gain 1 Slaughter, to a maximum of 5. Slaughter: 10% Increased Cold Damage, +15% Crit Damage.\n"
        "- If an enemy attacks you after you have acted, deal Cold Damage to them equal to your Siphoned damage.\n"
        "- If you attack an enemy after they have acted, apply Carved to them, up to 3 times. Carved: -5% Crit Chance, 5% Less Defenses.\n"
        "[bold]Stat Changes:[/bold] +10 HP. +6 Damage. +0.15 Speed. +5% Crit Chance. -25% Crit Multi. -10% Fire Resistance."
}

class Marauder(Player):
    def __init__(self, name, health=60, damage=4, damageType="cold", speed=0.8):
        super().__init__(name,health, damage, 0.04, 1.3, damageType, speed, className="Marauder", classDescription=MARAUDER_DESCRIPTIONS["Marauder"])
        self.siphonedDamage = 0
        self.echoDamage = {} # entity: echoDamage

        self.colossusEsBroken = False
        self.colossusDamage = 0
        self.dreadnoughtDeferredDamage = {2: 0, 1: 0}
        self.dreadnoughtDamage = 0
        self.dreadnoughtEchoHeal = 0
        self.harrowerSiphonedSpeed = 0
        self.harrowerSpeedBuffGained = False
        self.harrowerEmpowered = False
        self.butcherMarkedTarget = None
        self.butcherDamage = 0
        self.butcherSlaughter = 0

    @property
    def maxSiphon(self):
        return round(self._level * 1.5)

    def gainDamageReduction(self):
        if self._stats['Temporary']['damage_reduction'] < self._level * 2:
            self._stats['Temporary']['damage_reduction'] += 1

    def checkHarrowerBuff(self):
        if self._stats['Temporary']['speed'] >= 0.25 and not self.harrowerSpeedBuffGained:
            self.harrowerSpeedBuffGained = True
            self._stats['Temporary']['elemental'] += 10
            self._stats['Temporary']['physical'] += 20

    def empowerHarrower(self):
        if not self.harrowerEmpowered:
            self.harrowerEmpowered = True
            self._stats['Temporary']['speed'] -= 0.2
            self._stats['Temporary']['hp_regen'] += 20

    def applyButcherMark(self, allEnemies):
        if self.butcherMarkedTarget is None:
            target = random.choice(allEnemies)
            self.butcherMarkedTarget = target
            target.marked = True
            console.print(f"[asc_butcher]Butcher: Marked {target._name}. 25% Increased Damage dealt to them. They deal 10% Increased Damage[/asc_butcher]")
            pause()

    def _recalculateStats(self, doPrint = True, inCombat = False):
        super()._recalculateStats(doPrint, inCombat)

        if self._ascendancy == 'Colossus':
            evToArmour = int(self.evasion * 0.5)
            evToEs = int(self.evasion * 0.1)
            self._stats['armour'] += evToArmour
            self._stats['energy_shield'] += evToEs
            self._stats['evasion'] = 0

            if doPrint:
                console.print(f"[asc_colossus]Colossus: Converted 50% of Evasion ({evToArmour}) to Armour. Converted 10% of Evasion ({evToEs}) to Energy Shield. Evasion set to 0.[/asc_colossus]")

        elif self._ascendancy == 'Dreadnought':
            armourToHP = int(self.armour * 0.1)
            evToHP = int(self.evasion * 0.1)
            esToHp = int(self.maxEnergyShield * 0.2)
            self._stats['armour'] -= armourToHP
            self._stats['evasion'] -= evToHP
            self._stats['energy_shield'] -= esToHp

            self._maxHealth += armourToHP + evToHP + esToHp

            if doPrint:
                console.print(f"[asc_dreadnought]Dreadnought: Converted 10% of Armour ({armourToHP}), 10% of Evasion ({evToHP}), and 20% of Energy Shield ({esToHp}) to Max Health. Total Health Gained: {armourToHP + evToHP + esToHp}[/asc_dreadnought]")

    def onHeal(self, healAmount):
        if self._ascendancy == 'Dreadnought' and random.random() < 0.3:
            self.dreadnoughtEchoHeal += healAmount // 2

    def onAttack(self, damageDealt, damageType, target=None, combatManager=None):
        damageDealt, damageType = super().onAttack(damageDealt, damageType, target, combatManager)

        damageDealt += self.siphonedDamage

        if self._ascendancy == 'Colossus':
            damageDealt += self.colossusDamage
            if self.colossusEsBroken:
                damageDealt = int(damageDealt * (1 + ((self.maxEnergyShield // 5) / 100)))

        if self._ascendancy == 'Dreadnought':
            damageDealt += self.dreadnoughtDamage

        elif self._ascendancy == 'Harrower':
            if self.harrowerSpeedBuffGained:
                damageDealt = int(damageDealt * 1.4)
            if self.harrowerEmpowered and damageType == 'cold':
                damageDealt = int(damageDealt * 1.3)

        elif self._ascendancy == 'Butcher' and damageType == 'cold':
            damageDealt = int(damageDealt * (1 + (0.1 * self.butcherSlaughter)))

        return damageDealt, damageType

    def onTurnStart(self, combatManager=None):
        dType = 'cold'
        if self._ascendancy == 'Colossus':
            dType = 'true'
        for e, damage in self.echoDamage.items():
            if not e._isDead:
                e.damage(damage, dType)
                combatManager.checkDead(e)
                console.print(f"[class_marauder]Marauder: Echo activated. Dealt {damage} {dType} Damage to {e._name}.[/class_marauder]")
        if self.echoDamage != {}:
            pause()
            self.echoDamage = {}

        if self._ascendancy == 'Dreadnought':
            self.heal(self.dreadnoughtEchoHeal, False)
            self.dreadnoughtEchoHeal = 0

            self.damage(self.dreadnoughtDeferredDamage[1], 'cold')
            self.dreadnoughtDamage = int(max(self._maxHealth * 0.3, self.dreadnoughtDamage + (self.dreadnoughtDeferredDamage[1] * 0.2)))
            self.dreadnoughtDeferredDamage[1] = self.dreadnoughtDeferredDamage[2]
            self.dreadnoughtDeferredDamage[2] = 0

        super().onTurnStart(combatManager)

    def onCrit(self, targets, combatManager, critDamage):
        if self._ascendancy == 'Butcher':
            if self.butcherSlaughter < 5:
                self.butcherSlaughter += 1
                self._stats['Temporary']['crit_multi'] += 0.15

        return critDamage

    def onKill(self, entity, attackData, combatManager=None):
        if self._ascendancy == 'Colossus':
            gainedArmour = int(entity.armour * 0.2)
            esGain = int(max(entity.maxEnergyShield * 0.1, entity.armour * 0.1))
            self._stats['Temporary']['added_armour'] += gainedArmour
            self._stats['energy_shield'] = min(self.maxEnergyShield, self.energyShield + esGain)
            console.print(f"[asc_colossus]Colossus: Gained 20% of {entity._name}'s Armour as Added Armour for the rest of combat! +{gainedArmour} Armour. Regenerated {esGain} Energy Shield.[/asc_colossus]")
        elif self._ascendancy == 'Butcher':
            if entity.marked:
                self.butcherDamage += entity._baseDamage
                console.print(f"[asc_butcher]Butcher: Killed your Marked target! +{entity._baseDamage} Damage for the rest of combat.[/asc_butcher]")
                self.applyButcherMark(combatManager.allAlive)

    def onBattleEnd(self):
        heal = int(self._maxHealth * (max(30, self.siphonedDamage) / 100))
        self.heal(heal)

        self.siphonedDamage = 0
        self.echoDamage = {}

        self.colossusEsBroken = False
        self.colossusDamage = 0
        self.dreadnoughtDeferredDamage = {2: 0, 1: 0}
        self.dreadnoughtDamage = 0
        self.dreadnoughtEchoHeal = 0
        self.harrowerSiphonedSpeed = 0
        self.harrowerSpeedBuffGained = False
        self.harrowerEmpowered = False
        self.butcherMarkedTarget = None
        self.butcherDamage = 0
        self.butcherSlaughter = 0

        super().onBattleEnd()

    def _removeOldAscendancy(self):
        if self._ascendancy == 'Colossus':
            self._baseHealth += 15
            self._baseDamage -= 4
            self._baseSpeed += 0.2
            self._stats['Permanent']['added_armour'] -= 100
            self._stats['Permanent']['added_energy_shield'] -= 20
        elif self._ascendancy == 'Dreadnought':
            self._baseHealth -= 30
            self._baseDamage -= 5
            self._baseSpeed -= 0.1
            self._stats['Permanent']['increased_health'] -= 20
            self._stats['Permanent']['healing_magnitude'] -= 50
            self._stats['Permanent']['cold'] -= 15
            # self._stats['Max_Resistances']['cold'] -= 5
        elif self._ascendancy == 'Sovereign':
            self._baseHealth -= 15
            self._baseDamage -= 4
            self._baseSpeed += 0.1
            self._stats['Permanent']['stamina_regen'] -= 5
            self._stats['Permanent']['holy'] -= 10
        elif self._ascendancy == 'Harrower':
            self._baseHealth += 15
            self._baseDamage -= 6
            self._baseSpeed -= 0.1
            self._stats['baseCritChance'] -= 0.05
            self._stats['baseCritMulti'] -= 0.25
        elif self._ascendancy == 'Butcher':
            self._baseHealth -= 10
            self._damage -= 6
            self._baseSpeed -= 0.15
            self._stats['baseCritChance'] -= 0.05
            self._stats['baseCritMulti'] += 0.25
            self._stats['Permanent']['fire'] += 10
        return True

    def updateAscendancy(self, ascendancy):
        super().updateAscendancy(ascendancy)
        self._ascendancy = ascendancy
        self.ascendancyDescription = MARAUDER_DESCRIPTIONS[ascendancy]
        if ascendancy == 'Colossus':
            self._baseHealth -= 15
            self._baseDamage += 4
            self._baseSpeed -= 0.2
            self._stats['Permanent']['added_armour'] += 100
            self._stats['Permanent']['added_energy_shield'] += 20
        elif ascendancy == 'Dreadnought':
            self._baseHealth += 30
            self._baseDamage -= 5
            self._baseSpeed -= 0.1
            self._stats['Permanent']['increased_health'] += 20
            self._stats['Permanent']['healing_magnitude'] += 50
            self._stats['Permanent']['cold'] += 15
            # self._stats['Max_Resistances']['cold'] += 5
        elif ascendancy == 'Sovereign':
            self._baseHealth += 15
            self._baseDamage += 4
            self._baseSpeed -= 0.1
            self._stats['Permanent']['stamina_regen'] += 5
            self._stats['Permanent']['holy'] += 10
        elif ascendancy == 'Harrower':
            self._baseHealth -= 15
            self._baseDamage += 6
            self._baseSpeed += 0.1
            self._stats['baseCritChance'] += 0.05
            self._stats['baseCritMulti'] += 0.25
        elif ascendancy == 'Butcher':
            self._baseHealth += 10
            self._damage += 6
            self._baseSpeed += 0.15
            self._stats['baseCritChance'] += 0.05
            self._stats['baseCritMulti'] -= 0.25
            self._stats['Permanent']['fire'] -= 10

...