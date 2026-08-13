from typing import List, Optional, Tuple
from enum import Enum
from copy import deepcopy
import random
from .entities import Entity
from .enemy import Enemy
from .player import Player
from .abilities import Effects, StatusEffect, resolveEffects
from .styles import (
    console, printSuccess, printWarning, printError, printInfo, formatDamageType, pause
)
from .enemyAi import EnemyAI
#from expansions.bosses.bosses import Boss

class TurnPhase(Enum):
    PLAYER_TURN = "player"
    ENEMY_TURN = "enemy"
    TURN_END = "turn_end"

class EntropyTracker:
    def __init__(self):
        self.entropy = 0
    
    def rollEvasion(self, evasionRating):
        if evasionRating == 0:
            return False
        
        baseChance = min(0.75, evasionRating / 50 / 100)

        self.entropy += baseChance * 100

        if self.entropy >= 100:
            self.entropy -= 100
            return True
        else:
            roll = random.random()
            if roll < baseChance:
                self.entropy = max(0, self.entropy - 20)
                return True
            else:
                return False

class CombatUnit:
    def __init__(self, entity: Entity, team: str = "player", initiative: int = 0):
        self.entity = entity
        self.team = team
        self.initiative = initiative
        self._baseInitiative = initiative
        self.isActive = True
        self.statusEffects: list[StatusEffect] = []
        self.entropyTracker = EntropyTracker()

    def resetTurn(self):
        if not self.statusEffects:
            return

        expiredEffects = []
        for effect in self.statusEffects:
            if effect.tick():
                expiredEffects.append(effect)
        
        # Remove expired effects
        for effect in expiredEffects:
            self.statusEffects.remove(effect)
            console.print(f"  [dim]- {effect.name.capitalize()} has worn off![/dim]")

        self._recalculateInitiative()
        
        pause()

    def rollStunAvoidance(self) -> bool:
        avoidance = self.entity._stats['Bonuses']['stunAvoidance']
        if avoidance <= 0:
            return False
        
        if random.random() * 100 < avoidance:
            console.print(f"  [buff]- {self.entity._name} avoided being stunned! ({avoidance}% chance)[/buff]")
            return True
        return False

    @property
    def canAct(self) -> bool:
        if not self.isActive:
            return False
        stunned = False
        for effect in self.statusEffects:
            if effect.effectType == 'cc' and effect.name in ['stun', 'freeze']:
                if not self.rollStunAvoidance():
                    stunned = True
                    break
                else:
                    self.statusEffects.remove(effect)
        return not stunned

    @property
    def isStunned(self) -> bool:
        return any(effect.effectType == "cc" and effect.name in ['stun', 'immobilize', 'freeze']
                   for effect in self.statusEffects)

    @property
    def isSlowed(self) -> bool:
        return any(effect.name == "slow" for effect in self.statusEffects)

    def _recalculateInitiative(self):
        multiplier = 1.0

        for effect in self.statusEffects:
            if effect.name in ['freeze', 'slow']:
                amount = effect.data.get('amount', 0)
                multiplier *= (1 - amount)

        multiplier = round(multiplier, 2)
        self.initiative = round(self._baseInitiative, )

    def getDamageModifier(self) -> float:
        """Modifies the unit's own OUTGOING damage (e.g. Weaken). Damage TAKEN modifiers
        (Vulnerable/Shock/Brittle) live in getVulnerabilityModifier instead."""
        modifier = 1.0
        for effect in self.statusEffects:
            if effect.name == 'weaken':
                modifier *= (1 - effect.data.get('damageDealtReduction', 0))

        return modifier

    def getResistanceModifier(self, damageType: str) -> float:
        baseResist = self.entity._stats['Resistances'].get(damageType, 0)

        baseResist += self.entity._stats['Resistances'].get('all', 0)

        ELEMENTAL_TYPES = ['fire', 'cold', 'lightning', 'earth']
        if damageType in ELEMENTAL_TYPES:
            baseResist += self.entity._stats['Resistances'].get('elemental', 0)

        DIVINE_TYPES = ['holy', 'dark', 'arcane']
        if damageType in DIVINE_TYPES:
            baseResist += self.entity._stats['Resistances'].get('divine', 0)

        OTHERWORLD_TYPES = ['chaos', 'ethereal', 'psychic']
        if damageType in OTHERWORLD_TYPES:
            baseResist += self.entity._stats['Resistances'].get('otherworld', 0)

        for effect in self.statusEffects:
            if effect.effectType != "debuff":
                continue

            if effect.name == "exposed":
                baseResist -= effect.data.get('allResistanceReduction', 0)
            elif effect.name == "elemental_exposure" and damageType in ELEMENTAL_TYPES:
                baseResist -= effect.data.get('elementalResistanceReduction', 0)
            elif effect.name == "divine_exposure" and damageType in DIVINE_TYPES:
                baseResist -= effect.data.get('divineResistanceReduction', 0)
            elif effect.name == "otherworld_exposure" and damageType in OTHERWORLD_TYPES:
                baseResist -= effect.data.get('otherworldResistanceReduction', 0)
            elif effect.name == "physical_exposure" and damageType == 'physical':
                baseResist -= effect.data.get('physicalResistanceReduction', 0)

        return min(baseResist, 75)

    def calculateArmourReduction(self, incomingDamage: int, armourIgnorePercent: float = 0.0) -> float:
        armour = self.entity.armour * (1 - armourIgnorePercent)
        if armour <= 0:
            return 0
        reduction = armour / (armour + (10 * incomingDamage))
        return min(0.9, reduction)

    def checkEvade(self):
        return self.entropyTracker.rollEvasion(self.entity.evasion)

    def getVulnerabilityModifier(self) -> float:
        multiplier = 1.0
        for effect in self.statusEffects:
            if effect.name in ('vulnerable', 'shock', 'brittle'):
                multiplier += effect.data.get('damageTakenMultiplier', effect.data.get('amount', 0))
        return multiplier

class CombatManager:
    def __init__(self):
        self.units: List[CombatUnit] = []
        self.turnOrder: List[CombatUnit] = []
        self.currentTurnIndex = 0
        self.currentPhase = TurnPhase.PLAYER_TURN
        self.turnNumber = 0
        self.battleActive = False
        self._enemyDecisions = {}
        self._enemyIndexMap = {}

    def registerUnit(self, entity: Entity, team: str = "player") -> CombatUnit:
        initiative = int(entity._speed * 10) + random.randint(0, 5)
        unit = CombatUnit(entity, team, initiative)
        self.units.append(unit)
        return unit
    
    def unregisterUnit(self, unit: CombatUnit):
        unit.isActive = False
        if unit in self.units:
            self.units.remove(unit)
        if unit in self.turnOrder:
            self.turnOrder.remove(unit)

    def startBattle(self, player: Entity, enemies: List[Entity]):
        self.battleActive = True
        self.turnNumber = 1
        self.currentTurnIndex = 0
        self.units = []

        self.player = self.registerUnit(player, "player")

        for enemy in enemies:
            self.registerUnit(enemy, "enemy")

        self.turnOrder = sorted(
            [u for u in self.units if u.isActive],
            key=lambda u: u.initiative,
            reverse=True
        )

        console.print("\n[bold cyan]=== Turn Order ===[/bold cyan]")
        for i, unit in enumerate(self.turnOrder, 1):
            teamColour = "green" if unit.team == "player" else "red"
            console.print(f"  [dim]{i}.[/dim] [{teamColour}]{unit.entity._name}[/{teamColour}] [dim]({unit.team}) - Initiative: {unit.initiative}[/dim]")
        pause()

        if self.turnOrder:
            self._setPhaseForUnit(self.turnOrder[0])
       
    def nextTurn(self):
        if not self.battleActive or not self.turnOrder:
            return
        
        currentUnit = self.getCurrentUnit()
        if currentUnit: #reduce all ability cooldowns by 1 turn
            currentUnit.entity.onTurnEnd()
            for ability in currentUnit.entity._abilities.values():
                if ability.cooldown > 0:
                    ability.cooldown -= 1
        
        self.currentTurnIndex += 1

        if self.currentTurnIndex >= len(self.turnOrder): #start next round if at end of list
            self.currentTurnIndex = 0
            self.turnNumber += 1
            self._enemyDecisions = {}

            for unit in self.turnOrder: #reset all units for new round
                if unit.isActive:
                    unit.resetTurn()
        
        self.turnOrder = sorted(
            [u for u in self.units if u.isActive],
            key=lambda u: u.initiative,
            reverse=True
        )

        nextUnit = self.getCurrentUnit() #get next unit, skip if stunned
        if nextUnit:
            attempts = 0
            while not nextUnit.canAct and attempts < len(self.turnOrder):
                console.print(f"[warning]{nextUnit.entity._name} is stunned and cannot act![/warning]")
                nextUnit.resetTurn()
                self.currentTurnIndex += 1
                if self.currentTurnIndex >= len(self.turnOrder):
                    self.currentTurnIndex = 0
                    self.turnNumber += 1
                    self._enemyDecisions = {}
                    for unit in self.turnOrder:
                        if unit.isActive:
                            unit.resetTurn()
                nextUnit = self.getCurrentUnit()
                attempts += 1

            self._setPhaseForUnit(nextUnit)
            nextEntity = nextUnit.entity
            if not nextEntity.isPlayer:
                nextEntity.onTurnStart(self)

    def getCurrentUnit(self) -> Optional[CombatUnit]:
        if 0 <= self.currentTurnIndex < len(self.turnOrder):
            return self.turnOrder[self.currentTurnIndex]
        return None
    
    def getUnitsInTeam(self, team: str) -> List[CombatUnit]:
        return [u for u in self.units if u.team == team and u.isActive]
    
    def isTeamDefeated(self, team: str) -> bool:
        teamUnits = self.getUnitsInTeam(team)
        return len(teamUnits) == 0 or all(u.entity._isDead for u in teamUnits)
    
    def checkBattleEnd(self) -> Optional[str]:
        if self.isTeamDefeated("player"):
            self.battleActive = False
            return "enemy"
        elif self.isTeamDefeated("enemy"):
            self.battleActive = False
            return "player"
        return None

    def addStatusEffect(self, target: Entity, statusEffect: StatusEffect, attacker: Entity):
        statusEffect.target = target
        statusEffect.attacker = attacker
        targetUnit = None
        for unit in self.units:
            if unit.entity == target:
                targetUnit = unit
                break
        if targetUnit:
            targetUnit.statusEffects.append(statusEffect)
            console.print(f"  [debuff]- {target._name} is afflicted with {statusEffect.name.capitalize()}![/debuff]")

    def checkDead(self, target: Entity):
        if target._isDead:
            for unit in self.units:
                if unit.entity == target:
                    self.unregisterUnit(unit)
            return True
        return False

    def applyDamageWithDefenses(self, target: Entity, damage: int, damageType: str, combatUnit: CombatUnit=None, armourIgnorePercent: float = 0.0) -> Tuple[int, bool]:
        finalDamage = damage

        didEvade = False
        if damageType != 'true': # true damage ignores all defenses
            if damageType != 'psychic': # psychic ignores evasion
                didEvade = combatUnit.checkEvade()
                if didEvade:
                    target.onEvade()
                    console.print(f"    [buff]{target._name} dodged the attack![/buff]")
                    return 0, True

            if damageType != 'ethereal': # ethereal ignores armour
                reduction = combatUnit.calculateArmourReduction(finalDamage, armourIgnorePercent)
                reducedAmount = int(finalDamage * reduction)
                finalDamage -= reducedAmount

                if reducedAmount > 0:
                    console.print(f"    [cyan]{target._name}'s armour reduced damage by {reducedAmount}![/cyan]")

            if damageType != 'chaos': # chaos ignores energy shield
                currentES = target.energyShield
                if currentES > 0:
                    if finalDamage >= currentES:
                        finalDamage -= currentES
                        target._stats['energy_shield'] = 0
                        console.print(f"    [warning]{target._name}'s energy shield was broken![/warning]")
                    else:
                        target._stats['energy_shield'] -= finalDamage
                        console.print(f"    [cyan]{target._name}'s energy shield absorbed {finalDamage} damage![/cyan]")
                        return 0, False

        return finalDamage, didEvade

    def performAttack(self, attacker: Entity, target: Entity, abilityName: str = None):
        attackerUnit = None
        targetUnit = None
        for unit in self.units:
            if unit.entity == attacker:
                attackerUnit = unit
            elif unit.entity == target:
                targetUnit = unit

        if not attackerUnit:
            return False

        if abilityName and abilityName in attacker._abilities:
            ability = attacker._abilities[abilityName]
            console.print(f"\n[cyan]{attacker._name}[/cyan] uses [bold]{abilityName}[/bold]")

            if attackerUnit.team == 'player':
                canUse, reason = ability.canUse(attacker)
                if not canUse:
                    printWarning(f"  - {abilityName} cannot be used: {reason}")
                    return False
                ability.applyResourceCosts(attacker)
            else:
                if ability.cooldown > 0:
                    printWarning(f"  - {abilityName} is on cooldown for {ability.cooldown} more turn(s).")
                    return False

            selfEffects = ability.effects.get('self', {})
            if selfEffects:
                for effect in resolveEffects(selfEffects):
                    self.addStatusEffect(attacker, effect, attacker)

            targetEffectsDict = ability.effects.get('target', {})
            effectsBeforeTargeting: List[StatusEffect] = []

            targets = []
            if ability.targets == "all":
                if attackerUnit.team == "player":
                    targets = [u.entity for u in self.getUnitsInTeam("enemy")]
                else:
                    targets = [u.entity for u in self.getUnitsInTeam("player")]
            elif ability.targets == "multiple":
                numTargets = 2
                if attackerUnit.team == "player":
                    available = [u.entity for u in self.getUnitsInTeam("enemy")]
                else:
                    available = [u.entity for u in self.getUnitsInTeam("player")]
                targets = random.sample(available, min(numTargets, len(available)))
            else:
                targets = [target]

            damage = ability.calculateDamage(attacker._damage)
            damageType = ability.damageType if ability.damageType else attacker._damageType
            if attackerUnit:
                damage = int(damage * attackerUnit.getDamageModifier())

            if attacker.className == 'Wretch' and 'execute_bonus' in ability.tags:
                if target._health <= target._maxHealth * 0.5:
                    damage = int(damage * 1.5)
                    console.print(f"  [dark_red]Crimson Ritual: {target._name} is below 50% Health - damage increased![/dark_red]")

            # EXTRA TARGETING + MECHANICS

            if attacker.className == 'Monk':
                if attacker._ascendancy == 'Stormwalker' and damageType == 'lightning':
                    available = [u.entity for u in self.getUnitsInTeam('enemy')]
                    for _ in range(2):
                        targets.append(random.choice(available))
                        console.print(f"  [lightning]- Stormwalker: Lightning damage forks to {target._name}![/lightning]")
                    if random.random() < 0.4:
                        effectsBeforeTargeting.append(Effects.createShock())
                        console.print(f"  [lightning]- Stormwalker: Lightning damage applied Shock to {target._name}![/lightning]")

                elif attacker._ascendancy == 'Glacierfist':
                    if random.random() < 0.25:
                        chill = Effects.createChill()
                        effectsBeforeTargeting.extend(chill)
                    if random.random() < 0.2:
                        freeze = Effects.createFreeze()
                        effectsBeforeTargeting.append(freeze)

                elif attacker._ascendancy == 'Enlightened':
                    if damageType != attacker._damageType:
                        aoeDamage = int(attacker._baseDamage * 1.3)
                        console.print(f'  [gold1]- Enlightened: Element mismatch! {aoeDamage} {attacker._damageType} damage to all enemies![/gold1]')
                        for enemy in self.allAlive:
                            enemy.damage(aoeDamage, attacker._damageType)

            elif attacker.className == 'Wanderer':
                if random.random() < attacker.lostHitChance:
                    if attacker._ascendancy == 'Manifestation':
                        console.print('  [warning]- Manifestation: Lost attack missed! Applied Otherworld Exposure to all enemies.[/warning]')
                        exposure = Effects.createOtherworldExposure()
                        for unit in [u.entity for u in self.getUnitsInTeam('enemy')]:
                            self.addStatusEffect(unit, exposure, attacker)
                        return True
                if attacker.lostTrigger and damageType != 'heal':
                    console.print(f'  [buff]- Wanderer: Lost triggered. Attacking all enemies for 150% damage.[/buff]')
                    targets = [u.entity for u in self.getUnitsInTeam('enemy')]

                    if attacker._ascendancy == 'Weaver':
                        attacker.wovenDamage += 10
                        weaken = Effects.createWeaken()
                        effectsBeforeTargeting.append(weaken)
                        exposed = Effects.createExposed()
                        effectsBeforeTargeting.append(exposed)
                        console.print('  [buff]- Weaver: Lost Triggered! Applied Weaken and Lost to all enemies! +10 Damage for the rest of combat.[/buff]')

                if attacker._ascendancy == 'Fractured':
                    if attacker.fracture >= 5 and damageType != 'heal':
                        console.print(f"  [buff]- Fractured: Fracture stacks have reached 5. Attacking all enemies for 150% damage. Fracture stacks set to 0.[/buff]")
                        targets = [u.entity for u in self.getUnitsInTeam('enemy')]

            elif attacker.className == 'Mage':
                if attacker._ascendancy == 'Elementalist' and damageType in ['arcane', 'cold', 'earth', 'fire', 'lightning']:
                    if attacker.elementalistAttackCount % 3 == 0:
                        if len(self.allAlive) == 1:
                            damage *= 2
                            targets = self.allAlive
                            console.print(f'[gold1]Elementalist: 3rd elemental attack! Single target: 200% damage![/gold1]')
                        else:
                            damage = int(damage * 0.6)
                            targets = self.allAlive
                            console.print(f'[gold1]Elementalist: 3rd elemental attack! Hitting all enemies for 60% damage![/gold1]')

                elif attacker._ascendancy == 'Fluxweaver' and damageType in ['arcane', 'cold', 'earth', 'fire', 'lightning']:
                    if random.random() < 0.3:
                        exposure = Effects.createElementalExposure()
                        effectsBeforeTargeting.append(exposure)
                        console.print(f'[wind]Fluxweaver: Applied Elemental Exposure![/wind]')

            elif attacker.className == 'Fighter':
                if attacker._ascendancy == 'Brawler' and attacker.brawlerFury == 15:
                    damage = int(damage * 1.1)
                    targets = [u.entity for u in self.getUnitsInTeam('enemy')]
                    attacker.brawlerFury = 0
                    console.print("[fire]Brawler: Max Brawler's Fury reached! Expended all stacks to deal 90% damage to all enemies. Brawler's Fury set to 0.[/fire]")

            elif attacker.className == 'Warrior':
                if attacker._ascendancy == 'Warlord':
                    if attacker._fury == attacker._maxFury:
                        damage *= 3
                        targets = [u.entity for u in self.getUnitsInTeam('enemy')]
                        attacker._fury = 0
                        console.print(f'[gold1]Warlord: Max Fury! 200% More Damage to all enemies! Fury reset to 0.[/gold1]')
                elif attacker._ascendancy == 'Pyromancer':
                    if attacker.pyromancerAttacks % 3 == 0:
                        enemyEntities = [u.entity for u in self.getUnitsInTeam('enemy')]
                        for enemy in enemyEntities:
                            burn = Effects.createBurn()
                            self.addStatusEffect(enemy, burn, attacker)
                    if random.random() < 0.4:
                        burn = Effects.createBurn()
                        for b in burn:
                            effectsBeforeTargeting.append(b)
                elif attacker._ascendancy == 'Juggernaut' and attacker._fortify >= attacker._maxFortify and attacker._rage >= 100:
                    targets = [u.entity for u in self.getUnitsInTeam('enemy')]
                    stun = Effects.createStun()
                    effectsBeforeTargeting.append(stun)
                    console.print(f'[gold1]Juggernaut: Max Fortify - Stunning all enemies! -100 Rage.[/gold1]')
                    attacker._rage -= 100

                if attacker._ascendancy == 'Phantasm' and damageType == 'ethereal':
                    if random.random() < 0.3:
                        phased = Effects.createCustom(name='phased', effectType='special', duration=3, speedBonus=-0.2, damageMultiplier=0.9)
                        for enemy in self.allAlive:
                            self.addStatusEffect(enemy, phased, attacker)
                            console.print(f"  [ethereal]Phantasm: Applied Phased to {enemy._name}![/ethereal]")

            elif attacker.className == 'Cultist':
                if attacker._ascendancy == 'Harbinger' and attacker.insanity == attacker.maxInsanity:
                    curse = Effects.createCurse(2)
                    for c in curse:
                        effectsBeforeTargeting.append(c)

                elif attacker._ascendancy == 'Anarchist':
                    if attacker.volatility == attacker.maxVolatility and attacker.insanity > 0:
                        if self.allAlive:
                            aoeDamage = int(attacker._maxHealth * (0.01 * (attacker.insanity // 5)))
                            for e in self.allAlive:
                                e.damage(aoeDamage, 'chaos')
                        attacker.volatility = 0
                        attacker._randomiseInsanity(min=-10, max=30)

            # CRITICAL

            isCrit, critMult = attacker.rollCritical(targetUnit, damage)
            if damageType != 'heal':
                if isCrit:
                    damage = int(damage * critMult)
                    console.print(f"[bold gold1]✨ CRITICAL HIT! ✨[/bold gold1] [damage]{critMult*100:.0f}%[/damage] damage!")

                    if attacker.className == 'Paladin':
                        if attacker._ascendancy == 'Justicar':
                            living = len([u for u in self.getUnitsInTeam('enemy') if u.isActive])
                            attacker.favour = min(attacker.maxFavour,
                                                  attacker.favour + living * 5)

                    elif attacker.className == 'Wretch':
                        if attacker._ascendancy == 'Exsanguinator':
                            target.bloodSpike = 0

                    if target.className == 'Wanderer':
                        if target._ascendancy == 'Mindbreaker' and attacker.tortureStacks > 0:
                            attacker.tortureStacks = 0
                            console.print(f"  [warning]- Mindbreaker: {attacker._name} has removed all their torture stacks![/warning]")

                    elif target.className == 'Wretch':
                        if target._ascendancy == 'Plaguebearer':
                            target.gainBloodScent()

                        elif target._ascendancy == 'Necrose':
                            perc = 0.05 * attacker.necrosis
                            reflect = int(damage * perc)
                            console.print(f"[dark_olive_green3]Necrose: Reflected [/dark_olive_green3]{int(perc*100)}[dark_olive_green3]% of the damage to the enemy![/dark_olive_green3]")
                            damage -= reflect
                            attacker.damage(reflect, damageType)

            if damageType == 'heal':
                heal = int(ability.healBase + (attacker._maxHealth * ability.healPercent))
                attacker.heal(heal)
            else:
                # DAMAGE
                for t in targets:
                    mechanics: List[StatusEffect] = [deepcopy(m) for m in effectsBeforeTargeting]
                    mechanics.extend(resolveEffects(targetEffectsDict))

                    targetUnit = None
                    for unit in self.units:
                        if unit.entity == t:
                            targetUnit = unit
                            break

                    attacks = 1
                    if random.random() < attacker._stats['Bonuses']['chance_to_multihit']:
                        attacks = attacker.numMultihits

                    for _ in range(attacks):

                        finalDamage = damage * (0.75 if attacks > 1 else 1)
                        if targetUnit:
                            vulnMult = targetUnit.getVulnerabilityModifier()
                            if vulnMult > 1.0:
                                finalDamage = int(damage * vulnMult)
                                console.print(f"  [debuff]- {t._name} is vulnerable. Damage increased to {finalDamage}[/debuff]")

                        if len(targets) > 1:
                            finalDamage = int(finalDamage * 0.8)
                            console.print(f"  [dim]|- Hitting {t._name}[/dim]")
                            
                        if attacker.className == 'Monk':
                            if attacker._ascendancy == 'Stormwalker':
                                if any(e.name == 'shock' for e in targetUnit.statusEffects):
                                    attacker._prowess += 1
                                    console.print(f"  [buff]Stormwalker: Hit shocked enemy! +1 Prowess![/buff]")

                                    targetShockValue = [s.amount for s in targetUnit.statusEffects if s.name == 'shock'][0]
                                    otherEnemies = [e for e in self.allAlive if e != targetUnit]
                                    if otherEnemies:
                                        spread = random.choice(otherEnemies)
                                        shock = Effects.createShock(amount=targetShockValue)
                                        self.addStatusEffect(t, shock, attacker)
                                        console.print(f"  [lightning]Stormwalker: Shock spread to {spread._name}![/lightning]")

                        # BONUS MECHANICS

                        if attacker.className == 'Wanderer':
                            if attacker._ascendancy == 'Mindbreaker':
                                if damageType == 'psychic':
                                    t.tortureStacks += 1
                                if attacker.lostTrigger and random.random() <= (t.tortureStacks / 100):
                                    finalDamage *= 2
                                    exposure = Effects.createOtherworldExposure()
                                    mechanics.append(exposure)

                        elif attacker.className == 'Wretch':
                            if t.bloodSpike < attacker.maxBloodSpikeStacks:
                                t.bloodSpike += 1
                                if attacker._ascendancy == 'Necrose':
                                    attacker.bloodSpikeApplied += 1

                        finalDamage, damageType = attacker.onAttack(finalDamage, damageType, targetUnit, self)

                        armourIgnorePercent = 0.0
                        if attacker.className == 'Wretch' and attacker._ascendancy == 'Exsanguinator' and getattr(attacker, 'abilityUsedEnergyShield', False):
                            armourIgnorePercent = 0.15

                        finalDamage, evaded = self.applyDamageWithDefenses(target, finalDamage, damageType, targetUnit, armourIgnorePercent)
                        finalDamage, damageType = t.onHit(finalDamage, damageType, isCrit, attacker, self)

                        if t.className == 'Cultist' and t._ascendancy == 'Harbinger':
                            if attacker.corruption > 0 and t.insanity < 0:
                                attacker.corruption -= 1
                                console.print(f"  [chaos]You were attacked while your Insanity is negative! {attacker._name} is cleansed of 1 Corruption.[/chaos]")

                        elif t.className == 'Wretch':
                            if t._ascendancy == 'Bloodletter':
                                reflect = int(t.healthLost * 0.05)
                                attacker.damage(reflect, 'dark', attackerUnit)
                            elif t._ascendancy == 'Plaguebearer' and attacker.bloodSpike == 7:
                                finalDamage = int(finalDamage * 0.8)
                            elif t._ascendancy == 'Necrose':
                                attacker.gainNecrosis()
                                t.necrosisApplied += 1

                        if attacker._stats['Bonuses']['lifesteal'] > 0:
                            heal = int(finalDamage * (attacker._stats['Bonuses']['lifesteal'] / 100))
                            attacker.heal(heal)

                        if not evaded:
                            t.damage(finalDamage, damageType)
                        else:
                            console.print(f'[wind bold]{t._name} dodged the attack![/wind bold]')

                    # AFTER-HIT EFFECTS

                    if mechanics and not t._isDead:
                        for mechanic in mechanics:
                            self.addStatusEffect(t, mechanic, attacker)
                    death = self.checkDead(t)
                    if death:
                        # DEATH EFFECTS

                        killData = {'damage': finalDamage, 'damageType': damageType, 'mechanics': mechanics}
                        data = attacker.onKill(t, killData, self)

                        if attacker.className == 'Wanderer' and attacker._ascendancy == 'Weaver':
                            overkill = t._health
                            remainingEnemies = [u.entity for u in self.getUnitsInTeam('enemy')]
                            numEnemies = len(remainingEnemies)
                            if numEnemies > 0:
                                damageToAll = int(overkill / numEnemies)
                                console.print(f"  [buff]- Weaver: Overkill! {damageToAll} damage dealt to all living enemies")
                                for e in remainingEnemies:
                                    e.damage(damageToAll, damageType)
                        
                        elif attacker.className == 'Cultist' and attacker._ascendancy == 'Harbinger':
                            if t.corruption >= 5:
                                if len(self.allAlive) > 0:
                                    aoeDamage = int(t._maxHealth * 0.1)
                                    for e in self.allAlive:
                                        e.damage(aoeDamage, 'chaos')

                        elif attacker.className == 'Wretch':
                            if attacker._ascendancy == 'Exsanguinator':
                                if len(self.allAlive) > 0:
                                    dmg = int(t._maxHealth * 0.2)
                                    pick = random.choice(self.allAlive)
                                    pick.damage(dmg, 'dark')
                                else:
                                    heal = int(attacker._maxHealth * 0.1)
                                    attacker.heal(heal)
                            if attacker._ascendancy == 'Plaguebearer':
                                attacker.gainBloodScent()

                    else:

                        if attacker.className == 'Spectre' and attacker._ascendancy == 'Reaper':
                            if t._health <= (t._maxHealth * 0.05):
                                console.print(f"  [gold1 bold]Reaper: EXECUTE![/gold1 bold]")
                                t.damage(t._health, 'true')
                                self.checkDead(t)
                                heal = int(t._maxHealth * 0.1)
                                dmgBuff = int(target._damage * 0.05)
                                attacker.heal(heal)
                                attacker.reaperDamage += dmgBuff
                                console.print(f"  [gold1]Reaper: Executed {t._name}! Healed for {heal} HP and gained {dmgBuff} Damage permanently.[/gold1]")
                                attacker.onKill(t, {'executed': True}, self)

                        elif attacker.className == 'Wretch':
                            if target.bloodSpike > 0:
                                if t._health <= (t._maxHealth * (0.02 * t.bloodSpike)):
                                    console.print(f"[dark_red bold]Wretch: {t._name} Executed from Blood Spike![/dark_red bold]")

                                    if attacker._ascendancy == 'Necromancer':
                                        otherEnemies = [e for e in self.allAlive if e != t]
                                        if otherEnemies:
                                            victim = random.choice(otherEnemies)
                                            console.print(f"[dark_red]Necromancer: {t._name} lashes out at {victim._name} before dying![/dark_red]")
                                            victim.damage(t._damage, t._damageType)
                                            self.checkDead(victim)

                                    t.damage(t._health, 'true')
                                    self.checkDead(t)
                                    heal = attacker._maxHealth * (0.01 * target.bloodSpike)
                                    attacker.heal(heal)

                                    if attacker._ascendancy == 'Bloodletter':
                                        dmgMult = 0.01 * target.bloodSpike
                                        console.print(f'[dim red1]Bloodletter: All enemies take {int(dmgMult*100)}% of their Max HP as True Damage![/dim red1]')
                                        for e in self.allAlive:
                                            dmg = int(e._maxHealth * dmgMult)
                                            e.damage(dmg, 'true')

                                    elif attacker._ascendancy == 'Plaguebearer':
                                        spread = t.bloodSpike // 2
                                        numEnemies = len(self.getUnitsInTeam('enemy'))
                                        per = int(spread / numEnemies)
                                        if per > 0:
                                            for e in self.allAlive:
                                                e.bloodSpike = min(attacker.maxBloodSpikeStacks, e.bloodSpike + per)

                                    elif attacker._ascendancy == 'Necrose':
                                        heal = int(attacker._maxHealth * 0.05)
                                        attacker.heal(heal)
                                        attacker.gainRot()

                                    attacker.onKill(t, {'executed': True}, self)

            ability.cooldown = ability.maxCooldown
            return True

    @property
    def allAlive(self) -> List[Entity]:
        """returns all living enemies"""
        return [u.entity for u in self.getUnitsInTeam('enemy')]

    def resolveSkeletonAttack(self, wretch: Entity):
        """Necromancer: has the current skeleton ally attack alongside the player's turn"""
        skeleton = getattr(wretch, 'currentSkeleton', None)
        if not skeleton or getattr(wretch, 'skeletonTurns', 0) <= 0:
            return

        targets = self.allAlive
        if not targets:
            return

        target = random.choice(targets)
        console.print(f"\n[dark_red]{skeleton._name}[/dark_red] attacks {target._name}!")
        target.damage(skeleton._damage, skeleton._damageType)
        self.checkDead(target)

    def enemyTurn(self, enemy: Enemy, targets: List[Entity]):
        self.checkDead(enemy)
        if not targets or enemy._isDead:
            return
        aliveTargets = [t for t in targets if not t._isDead]
        if not aliveTargets:
            return

        # if isinstance(enemy, Boss):
        #     self.performAttack(enemy, random.choice(aliveTargets), enemy.chooseAbility(aliveTargets[0]))
        #     return
        
        if not self._enemyDecisions: # build snapshot for all enemies this round, cache it
            actionLists = [e.ai.buildActionList() for e in self.allAlive]
            self._enemyDecisions = EnemyAI.decideTurn(self.allAlive, aliveTargets[0], actionLists)
            self._enemyIndexMap = {e: i for i, e in enumerate(self.allAlive)}

        idx = self._enemyIndexMap.get(enemy, 0)
        decision = self._enemyDecisions.get(idx)
        enemy.ai.applyDecision(decision, aliveTargets[0], self)

    def _setPhaseForUnit(self, unit: CombatUnit):
        if unit.team == "player":
            self.currentPhase = TurnPhase.PLAYER_TURN
        elif unit.team == "enemy":
            self.currentPhase = TurnPhase.ENEMY_TURN

...