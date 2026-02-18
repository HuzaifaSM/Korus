from .base import Player
from scripts.styles import console, formatDamageType
import random

DESCRIPTIONS = {
    "Mage": "A master of the arcane arts.\n"
        "Mana: Starts with a mana pool that increases with level. Regenerate a base of 5 mana per turn.\n"
        "Upon attacking with Elemental or Arcane damage, spend mana equal to 20% of damage dealt.\n Gain damage equal to mana spent on attacks.\n"
        "Starting Stats: 40 HP | 7 Damage | 5% Crit Chance | 175% Crit Damage | Arcane Damage | 1 Speed.",
    #ascendancies
    "Elementalist": "For every elemental attack used consecutively, gain 1 stack of Symphony. Max 10 stacks of Symphony. Symphony: 5% more Elemental damage per Symphony stack.\n"
        "Every 3rd elemental attack instead attacks all enemies for 60% damage. If only one enemy is alive, deal 200% damage to it instead.\n"
        "+5 HP. +1 Damage. -0.05 Speed. +15 Mana.",
    "Arcanist": "For every enemy you kill with Arcane damage, permanently gain 1% increased Arcane damage.\n"
        "Skills have 15% Reduced Mana cost. Upon killing an enemy with non-arcane damage, regain 60% of your missing mana.\n"
        "-10 HP. +1 Damage. +0.05 Speed. -10 Mana. +10% Arcane Resistance",
    "Battlemage": "Physical attacks also cost mana. 30% Increased Physical damage. Upon killing an enemy with non-elemental damage, gain Combat Focus.\n"
        "Combat Focus: +10 Mana Regen, +15% Elemental Damage. Combat Focus lasts 3 turns and refreshes on non-elemental kills.\n"
        "+5 HP. +3 Damage. -0.2 Speed. +3% Crit Chance. +5% Physical Resistance.",
    "Fluxweaver": "Elemental damage has a 30% chance to apply Elemental Exposure to the enemy for 3 turns. Upon killing an enemy afflicted by Elemental Exposure, gain 1 stack of Flux.\n"
        "Flux: +10 Damage, +0.1 Speed, +5% Elemental Resistance for the rest of combat. Flux has no maximum stacks.\n"
        "Whenever you use mana to attack, deal damage to all enemies equal to 50% of mana spent.\n"
        "-15 HP. +2 Damage. +0.05 Speed. +5% Crit Chance. +50% Crit Damage. +10% Arcane Resistance.",
    "Calamity": "Deal 20% Increased Elemental Damage. Take 10% Increased Elemental Damage.\n"
        "Upon being hit by non-elemental damage, 20% chance to apply Elemental Exposure to the enemy and deal 50% of the damage taken back to the enemy.\n"
        "Upon killing an enemy with elemental damage, all living enemies take Arcane damage equal to 25% of your base damage.\n"
        "Upon killing an enemy with non-elemental damage, gain Mana Sickness: -40% Elemental Damage, -15% Elemental Resistance, for 3 turns.\n"
        "-20 HP. +4 Damage. +0.1 Speed. +50% Crit Damage.",
    "Archon": "Upon dealing a critical hit with Arcane damage, deal 50-100% of your base damage as Arcane damage to all enemies, and gain 1 stack of Archon.\n"
        "Archon: 5% Increased Arcane damage, +5 Damage, for the rest of combat. Archon has no max stacks.\n"
        "Upon being hit by elemental damage, 10% chance to nullify the damage and instead deal 50% of damage taken back to the attacker as Arcane damage.\n"
        "+10 HP. -2 Damage. +0.05 Speed. +5% Crit Chance. +10% Arcane Resistance",
    #subtypes
    "Sage": "Mana costs of attacks reduced by 20%. For every 20% of your Maximum Mana you spend in combat, gain Shield equal to that amount.\n"
        "For every unique damage type used in combat, gain 5% increased damage for the rest of combat.\n"
        "-10 HP. +2 Damage. +20 Mana. -10% Physical Resistance.",
    "Warlock": "30% less Maximum Mana. Health can be used in place of Mana if you do not have enough Mana. 1 Health = 3 Mana.\n"
        "20% Increased Elemental Damage. If any health was used in place of mana to attack, heal for 10% of elemental damage dealt.\n"
        "+15 HP. -2 Damage. +0.1 Speed. +10% Dark Resistance.",
    "Chronicler": "40% Reduced Mana Regeneration rate. At the start of combat, for every enemy present, gain 10% Increased Elemental Damage and -2% All Resistance.\n"
        "Gain Knowledge on elemental skill use. Knowledge: +2% Increased Elemental Damage, +5 Max Mana. Knowledge persists between combats. Lose all Knowledge upon using a non-elemental skill.\n"
        "Upon killing an enemy, lose 20% of your Knowledge and heal for Max HP equal to the amount lost.\n"
        "+10 HP. -1 Damage. +0.05 Speed. +20 Mana. +5% Crit Chance. -5% Elemental Resistance."
}

ELEMENTAL = ['arcane', 'cold', 'earth', 'fire', 'lightning', 'wind']

class Mage(Player): # higher damage, lower health, arcane damage
    def __init__(self, name, health = 40, damage = 7, damageType = "arcane", speed = 1):
        super().__init__(name, health, damage, 0.05, 1.75, damageType, speed, className="Mage", classDescription=DESCRIPTIONS['Mage'])
        self._maxMana = self._maxHealth
        self._mana = self._maxMana
        self._lastElementUsed = None
        self.manaEfficiency = 1.0
        self.manaRegenBonus = 0

        self.lastSymphonyElement = None
        self.symphony = 0
        self.elementalistAttackCount = 0

        self.arcanistKills = 0

        self.combatFocusTurns = 0
        
        self.flux = 0
        self.fluxweaverManaSpent = 0

        self.manaSicknessTurns = 0

        self.archon = 0
        
        self.sageTypesUsed = []
        self.sageManaSpent = 0
        
        self.warlockUsedHP = False

        self.chroniclerEnemies = 0
        self.knowledgeStacks = 0

    def __str__(self):
        baseStr = super().__str__()
        baseStr += f"\n[cyan]Mana:[/cyan] {self._mana} / {self._maxMana}"
        
        if self._ascendancy == "Elementalist" and self.symphony > 0:
            baseStr += f"\n[gold1]Symphony:[/gold1] {self.symphony} / 10"
        elif self._ascendancy == "Battlemage" and self.combatFocusTurns > 0:
            baseStr += f"\n[buff]Combat Focus:[/buff] {self.combatFocusTurns} turns"
        elif self._ascendancy == "Fluxweaver" and self.flux > 0:
            baseStr += f"\n[wind]Flux:[/wind] {self.flux} stacks"
        elif self._ascendancy == "Archon" and self.archon > 0:
            baseStr += f"\n[arcane]Archon:[/arcane] {self.archon} stacks"
        
        if self._subType == "Chronicler" and self.knowledgeStacks > 0:
            baseStr += f"\n[info]Knowledge:[/info] {self.knowledgeStacks} stacks"
        
        return baseStr

    def _serialise(self):
        temp = super()._serialise()
        temp['maxMana'] = self._maxMana
        temp['mana'] = self._mana
        temp['arcanistKills'] = self.arcanistKills
        temp['knowledgeStacks'] = self.knowledgeStacks
        return temp

    def deserialise(self, data):
        super().deserialise(data)
        if hasattr(self, '_rage'):
            delattr(self, '_rage')
        if hasattr(self, '_maxRage'):
            delattr(self, '_maxRage')
        if hasattr(self, '_maxThorns'):
            delattr(self, '_maxThorns')
        if hasattr(self, '_form'):
            delattr(self, '_form')
        
        self.arcanistKills = data.get('arcanistKills', 0)
        self.knowledgeStacks = data.get('knowledgeStacks', 0)

    def onAttack(self, damageDealt, damageType, target=None, combatManager=None):
        super().onAttack(damageDealt, damageType)

        manaSpent = 0

        if damageType in ELEMENTAL or damageType == 'arcane':
            baseCost = damageDealt // 5 + 5
            manaCost = int(min(self._mana, baseCost) / self.manaEfficiency)

            if self._subType == 'Warlock' and self._mana < manaCost:
                manaDeficit = manaCost - self._mana
                hpNeeded = (manaDeficit + 2) // 3

                if self._health > hpNeeded:
                    self._health -= hpNeeded
                    self._mana = 0
                    manaCost = baseCost
                    self.warlockUsedHP = True
                    console.print(f"[warning]Warlock: Used {hpNeeded} HP to cover mana cost![/warning]")
                else:
                    manaCost = self._mana
                    self._mana = 0
            else:
                self._mana = max(0, self._mana - manaCost)

            manaSpent = manaCost
            damageDealt += manaCost
            console.print(f"[cyan]Used {manaCost} mana to empower attack with +{manaCost} damage.[/cyan]")
        
        elif self._ascendancy == 'Battlemage' and damageType == 'physical':
            baseCost = damageDealt // 5 + 5
            manaCost = int(min(self._mana, baseCost) / self.manaEfficiency)
            self._mana -= manaCost
            manaSpent = manaCost
            damageDealt = int(damageDealt * 1.3)
            console.print(f"[cyan]Battlemage: Used {manaCost} mana! +30% Physical damage.[/cyan]")
        
        if self._subType == 'Sage':
            self.sageManaSpent += manaSpent
            shieldThreshold = self._maxMana * 0.2
            if self.sageManaSpent >= shieldThreshold:
                shieldGain = int(shieldThreshold)
                self._shield += shieldGain
                self.sageManaSpent -= shieldThreshold
                console.print(f"[buff]Sage: Gained {shieldThreshold} Shield! Total Shield: {self._shield}[/buff]")

        if self._ascendancy == 'Fluxweaver' and manaSpent > 0 and combatManager:
            aoeDamage = int(manaSpent * 0.5)
            enemies = combatManager.getUnitsInTeam('enemy')
            console.print(f"[wind]Fluxweaver: Mana flux deals {aoeDamage} damage to all enemies![/wind]")
            for enemy in enemies:
                enemy.entity.damage(aoeDamage, 'arcane')

        if self._lastElementUsed == damageType:
            damageDealt = round(damageDealt * 1.2)
            console.print(f"\n[buff]Damage type affinity: +20% damage![/buff]")
        else:
            self._lastElementUsed = damageType
            console.print(f"\n[info]New damage type affinity: {formatDamageType(self._lastElementUsed, self._lastElementUsed)}[/info]")
        
        if self._subType == 'Sage' and damageType not in self.sageTypesUsed:
            self.sageTypesUsed.append(damageType)
            console.print(f"[buff]New damage type! +5% Damage. Total: +{int(damageBonus*100)}% Damage.[/buff]")
        if self._subType == 'Sage' and len(self.sageTypesUsed) > 0:
            damageBonus = int(len(self.sageTypesUsed) * 0.05)
            damageDealt = int(damageDealt * (1 + damageBonus))

        if self._ascendancy == 'Arcanist' and self.arcanistKills > 0 and damageType == 'arcane':
            damageDealt = int(damageDealt * (1 + self.arcanistKills * 0.01))

        elif self._ascendancy == 'Elementalist':
            if damageType in ELEMENTAL:
                if self.lastSymphonyElement == damageType and self.symphony < 10:
                    self.symphony += 1
                    console.print(f"[gold1]Elementalist: Symphony +1! ({self.symphony} / 10)[/gold1]")
                else:
                    self.lastSymphonyElement = damageType

                if self.symphony > 0:
                    symphonyBonus = 1 + (self.symphony * 0.05)
                    damageDealt = int(damageDealt * symphonyBonus)
                    console.print(f"[gold1]Symphony: +{int((symphonyBonus-1)*100)}% elemental damage![/gold1]")
                self.elementalistAttackCount += 1

            else:
                if self.symphony > 0:
                    console.print(f"[warning]Non-elemental attack! Symphony reset.[/warning]")
                self.symphony = 0
                self.lastSymphonyElement = None

        elif self._ascendancy == 'Battlemage' and self.combatFocusTurns > 0:
            if damageType in ELEMENTAL:
                damageDealt = int(damageDealt * 1.15)
                console.print('[buff]Combat Focus: +15% Elemental Damage dealt![/buff]')

        elif self._ascendancy == 'Fluxweaver' and self.flux > 0:
            damageDealt += self.flux * 10
            console.print(f"[wind]Flux: +{self.flux * 10} damage![/wind]")

        elif self._ascendancy == 'Calamity':
            if damageType in ELEMENTAL:
                damageDealt = int(damageDealt * 1.2)
                console.print(f"[fire]Calamity: +20% elemental damage![/fire]")
            if self.manaSicknessTurns > 0:
                damageDealt = int(damageDealt * 0.6)
                console.print(f"[warning]Mana Sickness: -40% elemental damage![/warning]")

        elif self._ascendancy == 'Archon' and self.archon > 0:
            if damageType == 'arcane':
                damageDealt += self.archon * 5
                damageDealt = int(damageDealt * (1 + self.archon * 0.05))
                console.print(f"[arcane]Archon: +{int(self.archon * 0.05 * 100)}% arcane damage, +{self.archon * 5} flat![/arcane]")

        if self._subType == 'Warlock':
            if damageType in ELEMENTAL:
                damageDealt = int(damageDealt * 1.2)
                console.print(f"[buff]Warlock: +20% elemental damage![/buff]")
            if self.warlockUsedHP and damageType in ELEMENTAL:
                heal = int(damageDealt * 0.1)
                self.heal(heal)
                console.print(f"[buff]Warlock: Healed {heal} HP from blood magic![/buff]")
                self.warlockUsedHP = False
        
        if self._subType == 'Chronicler' and damageType in ELEMENTAL:
            self.knowledgeStacks += 1
            console.print(f"[info]Chronicler: Knowledge +1! ({self.knowledgeStacks} total)[/info]")
            damageDealt = int(damageDealt * (1 + self.chroniclerEnemies * 0.1))
        elif self._subType == 'Chronicler' and damageType not in ELEMENTAL and self.knowledgeStacks > 0:
            lostKnowledge = self.knowledgeStacks
            self.knowledgeStacks = 0
            console.print(f"[warning]Chronicler: Non-elemental attack! Lost all {lostKnowledge} Knowledge![/warning]")
        
        if self._subType == 'Chronicler' and self.knowledgeStacks > 0:
            knowledgeBonus = 1 + (self.knowledgeStacks * 0.02)
            if damageType in ELEMENTAL:
                damageDealt = int(damageDealt * knowledgeBonus)
                console.print(f"[info]Knowledge: +{int((knowledgeBonus-1)*100)}% elemental damage![/info]")

        return damageDealt, damageType

    def onHit(self, damageTaken, damageType, attacker=None, combatManager=None):
        super().onHit(damageTaken, damageType)

        if self._ascendancy == 'Calamity' and damageType not in ELEMENTAL and random.random() < 0.2:
            if attacker and combatManager:
                reflectDamage = int(damageType * 0.5)
                attacker.damage(reflectDamage, damageType)
                console.print(f"[fire]Calamity: Reflected {reflectDamage} damage![/fire]")

                from scripts.abilities import createElementalExposure
                exposureEffect = createElementalExposure(3)
                combatManager.addStatusEffect(attacker, exposureEffect.toDict(), self)
                console.print(f"[debuff]Applied Elemental Exposure![/debuff]")

        if self._ascendancy == 'Archon' and damageType in ELEMENTAL and random.random() < 0.1:
            if attacker:
                reflectDamage = int(damageTaken * 0.5)
                attacker.damage(reflectDamage, 'arcane')
                console.print(f"[arcane]Archon: Nullified damage and reflected {reflectDamage} damage as Arcane damage![/arcane]")
                self._health += damageTaken
                return

        if self._ascendancy == 'Calamity' and damageType in ELEMENTAL:
            extraDamage = int(damageTaken * 0.1)
            self._health -= extraDamage
            console.print(f"[warning]Calamity: Took {extraDamage} extra elemental damage![/warning]")

    def onKill(self, entity, attackData, combatManager=None):
        if self._ascendancy == 'Arcanist' and attackData['damageType'] == 'arcane':
            self.arcanistKills += 1
            console.print(f"[arcane]Arcanist: +1% Increased Arcane Damage permanently! ({int(self.arcanistKills)}% total)[/arcane]")

        elif self._ascendancy == 'Arcanist' and attackData['damageType'] != 'arcane':
            missingMana = self._maxMana - self._mana
            gain = int(missingMana * 0.6)
            self._mana = min(self._maxMana, self._mana + gain)
            console.print(f"[cyan]Arcanist: Regained {gain} mana![/cyan]")

        if self._ascendancy == 'Battlemage' and attackData['damageType'] not in ELEMENTAL:
            self.combatFocusTurns = 3
            console.print(f"[buff]Battlemage: Combat Focus gained! (+10 mana regen, +15% elemental damage)[/buff]")

        if self._ascendancy == 'Fluxweaver' and combatManager:
            for enemy in combatManager.getUnitsInTeam('enemy'):
                if enemy.entity == entity:
                    target = enemy
                    break
            hasExposure = any(e.name == 'elemental_exposure' for e in target.statusEffects)
            if hasExposure:
                self.flux += 1
                self._stats['Temporary']['speed'] = self._stats['Temporary'].get('speed', 0) + 0.1
                self._stats['Temporary']['elemental'] = self._stats['Temporary'].get('elemental', 0) + 5
                console.print(f"[wind]Fluxweaver: Flux +1! ({self.flux} stacks)[/wind]")

        if self._ascendancy == 'Calamity' and attackData['damageType'] in ELEMENTAL and combatManager:
            aoeDamage = int(self._baseDamage * 0.25)
            enemies = combatManager.getUnitsInTeam('enemy')
            if enemies:
                console.print(f"[fire]Calamity: Elemental kill! {aoeDamage} arcane damage to all enemies![/fire]")
                for enemyUnit in enemies:
                    enemyUnit.entity.damage(aoeDamage, 'arcane')
        
        elif self._ascendancy == 'Calamity' and attackData['damageType'] not in ELEMENTAL:
            self.manaSicknessTurns = 3
            self._stats['Temporary']['elemental'] = self._stats['Temporary'].get('elemental', 0) - 15
            console.print(f"[warning]Calamity: Mana Sickness! (-40% elemental damage, -15% elemental res for 3 turns)[/warning]")
        
        if self._subType == 'Chronicler' and self.knowledgeStacks > 0:
            knowledgeLost = int(self.knowledgeStacks * 0.2)
            healPercent = knowledgeLost / 100
            healAmount = int(self._maxHealth * healPercent)
            self.knowledgeStacks -= knowledgeLost
            self.heal(healAmount)
            console.print(f"[info]Chronicler: Lost {knowledgeLost} Knowledge, healed {healAmount} HP![/info]")

        return None

    def onTurnStart(self, combatManager=None):
        super().onTurnStart(combatManager)

        baseRegen = 5
        
        if self.combatFocusTurns > 0:
            baseRegen += 10

        if self._subType == 'Chronicler':
            baseRegen = int(baseRegen * 0.6)

        totalRegen = baseRegen + self.manaRegenBonus
        self._mana = min(self._maxMana, self._mana + totalRegen)
        console.print(f"[cyan]+{totalRegen} mana regenerated. ({self._mana} / {self._maxMana})[/cyan]")
        
        if self._subType == 'Chronicler' and combatManager and self.chroniclerEnemies == 0:
            enemies = combatManager.getUnitsInTeam('enemy')
            self.chroniclerEnemies = len(enemies)
            if self.chroniclerEnemies > 0:
                damageBonus = self.chroniclerEnemies * 0.1
                resReduction = self.chroniclerEnemies * 2
                self._stats['Temporary']['all'] = self._stats['Temporary'].get('all', 0) - resReduction
                console.print(f"[info]Chronicler: {self.chroniclerEnemies} enemies! +{int(damageBonus*100)}% elemental damage, -{resReduction}% all res[/info]")

    def onTurnEnd(self):
        super().onTurnEnd()

        if self.combatFocusTurns > 0:
            self.combatFocusTurns -= 1
            if self.combatFocusTurns == 0:
                console.print(f"[warning]Combat Focus expired![/warning]")

        if self.manaSicknessTurns > 0:
            self.manaSicknessTurns -= 1
            if self.manaSicknessTurns == 0:
                self._stats['Temporary']['elemental'] = self._stats['Temporary'].get('elemental', 0) + 15
                console.print(f"[buff]Mana Sickness expired![/buff]")
        
    def onBattleEnd(self):
        self._lastElementUsed = None
        self._mana = self._maxMana
        self.symphony = 0
        self.lastSymphonyElement = None
        self.elementalistAttackCount = 0
        self.combatFocusTurns = 0
        self.flux = 0
        self.manaSicknessTurns = 0
        self.archon = 0
        self.sageTypesUsed = []
        self.sageManaSpent = 0
        self.warlockUsedHP = False
        self.chroniclerEnemies = 0
        super().onBattleEnd()

    def _recalculateStats(self, doPrint=True):
        super()._recalculateStats(doPrint)
        self._maxMana = self._maxHealth
        
        if self._subType == 'Warlock':
            self._maxMana = int(self._maxMana * 0.7)

        elif self._subType == 'Chronicler':
            self._maxMana += self.knowledgeStacks * 5

    def updateAscendancy(self, ascendancy):
        if ascendancy == 'Elementalist':
            self._baseHealth += 5
            self._baseDamage += 1
            self._baseSpeed -= 0.05
            self._ascendancy = 'Elementalist'
            self.ascendancyDescription = DESCRIPTIONS['Elementalist']
        elif ascendancy == 'Arcanist':
            self._baseHealth -= 10
            self._baseDamage += 1
            self._baseSpeed += 0.05
            self.manaEfficiency = 1.15  # 15% reduced mana cost
            self._stats['Permanent']['arcane'] = self._stats['Permanent'].get('arcane', 0) + 10
            self._ascendancy = 'Arcanist'
            self.ascendancyDescription = DESCRIPTIONS['Arcanist']
        elif ascendancy == 'Battlemage':
            self._baseHealth += 5
            self._baseDamage += 3
            self._baseSpeed -= 0.2
            self._stats['baseCritChance'] += 0.03
            self._stats['Permanent']['physical'] = self._stats['Permanent'].get('physical', 0) + 5
            self._ascendancy = 'Battlemage'
            self.ascendancyDescription = DESCRIPTIONS['Battlemage']
        elif ascendancy == 'Fluxweaver':
            self._baseHealth -= 15
            self._baseDamage += 2
            self._baseSpeed += 0.05
            self._stats['baseCritChance'] += 0.05
            self._stats['baseCritMulti'] += 0.5
            self._stats['Permanent']['arcane'] = self._stats['Permanent'].get('arcane', 0) + 10
            self._ascendancy = 'Fluxweaver'
            self.ascendancyDescription = DESCRIPTIONS['Fluxweaver']
        elif ascendancy == 'Calamity':
            self._baseHealth -= 20
            self._baseDamage += 4
            self._baseSpeed += 0.1
            self._stats['baseCritMulti'] += 0.5
            self._ascendancy = 'Calamity'
            self.ascendancyDescription = DESCRIPTIONS['Calamity']
        elif ascendancy == 'Archon':
            self._baseHealth += 10
            self._baseDamage -= 2
            self._baseSpeed += 0.05
            self._stats['baseCritChance'] += 0.05
            self._stats['Permanent']['arcane'] = self._stats['Permanent'].get('arcane', 0) + 10
            self._ascendancy = 'Archon'
            self.ascendancyDescription = DESCRIPTIONS['Archon']
        self._recalculateStats(False)

    def updateSubType(self, subType):
        if subType == 'Sage':
            self._baseHealth -= 10
            self._baseDamage += 2
            self.manaEfficiency = 1.2  # 20% reduced mana cost
            self._stats['Permanent']['physical'] = self._stats['Permanent'].get('physical', 0) - 10
            self._subType = 'Sage'
            self.subTypeDescription = DESCRIPTIONS['Sage']
        elif subType == 'Warlock':
            self._baseHealth += 15
            self._baseDamage -= 2
            self._baseSpeed += 0.1
            self._stats['Permanent']['dark'] = self._stats['Permanent'].get('dark', 0) + 10
            self._subType = 'Warlock'
            self.subTypeDescription = DESCRIPTIONS['Warlock']
        elif subType == 'Chronicler':
            self._baseHealth += 10
            self._baseDamage -= 1
            self._baseSpeed += 0.05
            self._stats['baseCritChance'] += 0.05
            self._stats['Permanent']['elemental'] = self._stats['Permanent'].get('elemental', 0) - 5
            self._subType = 'Chronicler'
            self.subTypeDescription = DESCRIPTIONS['Chronicler']
        self._recalculateStats(False)

# elementalist = kill 50 enemies with elemental damage
# arcanist = cast only arcane-type skills in 5 combats
# battlemage = deal 1000 total physical damage as a mage (or any mage variant)
# fluxweaver = kill 20 enemies afflicted with elemental exposure
# calamity = -20 HP. +1 Damage. +0.1 Speed. +3% Crit Chance. +20% Crit Multi
# archon = deal 50 critical hits as a mage

# sage = use each elemental-type skill in a single combat
#warlock = use 20 arcane-type skills whilst under 50% hp
# chronicler = win 10 combats without reaching 0 mana
