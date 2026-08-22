from typing import List, Optional, Tuple
from enum import Enum
from copy import deepcopy
import random
from .entities import Entity
from .enemy import Enemy
from .abilities import StatusEffect, resolveEffects
from .styles import (
    console, printSuccess, printWarning, printError, printInfo, formatDamageType, pause
)
from .enemyAi import EnemyAI

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
        self.hasActed = False
        self.isActive = True
        self.statusEffects: list[StatusEffect] = []
        self.entropyTracker = EntropyTracker()

    def resetTurn(self):
        self.hasActed = False

        self._recalculateInitiative()

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

    def rollStunAvoidance(self) -> bool:
        avoidance = self.entity._stats['Bonuses']['stun_avoidance']
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
        self.initiative = round(self._baseInitiative)

    def getDamageModifier(self) -> float:
        modifier = 1.0
        for effect in self.statusEffects:
            if effect.name == 'weaken':
                modifier *= (1 - effect.data.get('damageDealtReduction', 0))
            elif effect.name == 'haste':
                modifier *= effect.data.get('damageMultiplier', 1.0)
            elif effect.name == 'daze':
                modifier *= effect.data.get('damageMultiplier', 1.0)

        return modifier

    def getStoneskinModifier(self) -> float:
        """Percentage damage reduction from active Stoneskin stacks, capped at 75%."""
        total = 0.0
        for effect in self.statusEffects:
            if effect.name == 'stoneskin':
                total += effect.data.get('damageReduction', 0)
        return min(total, 0.75)

    def getResistanceModifier(self, damageType: str, attacker=None) -> float:
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
            if effect.name == "burn":
                baseResist -= effect.data.get('resistanceReduction', 0)
                continue

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

        baseResist = min(baseResist, 75)

        if attacker is not None and baseResist > 0:
            pen = max(0, min(200, attacker._stats['Bonuses'].get('resistance_penetration', 0)))
            if pen > 0:
                baseResist *= (1 - pen / 100)

        return baseResist / 100

    def calculateArmourReduction(self, incomingDamage: int, armourIgnorePercent: float = 0.0, armourOverride: float = None) -> float:
        armour = armourOverride if armourOverride is not None else self.entity.armour
        armour *= (1 - armourIgnorePercent)
        if armour <= 0:
            return 0
        reduction = armour / (armour + (10 * incomingDamage))
        return min(0.9, reduction)

    def checkEvade(self, evasionOverride: float = None):
        evasion = evasionOverride if evasionOverride is not None else self.entity.evasion
        return self.entropyTracker.rollEvasion(evasion)

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
        enemyUnits = [self.registerUnit(enemy, "enemy") for enemy in enemies]

        self.player.entity.onCombatStart(self, self.player)
        for enemy, e in zip(enemies, enemyUnits):
            enemy.onCombatStart(self, e)

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
        if len(self.allAlive) == 0:
            return
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

    def applyDamageWithDefenses(self, target: Entity, damage: int, damageType: str, combatUnit: CombatUnit=None, armourIgnorePercent: float = 0.0) -> Tuple[int, int, int, bool]:
        finalDamage = damage

        energyShield = target.energyShield

        didEvade = False
        armourDamageReduction = 0
        esDamagePrevented = 0
        if damageType != 'true': # true damage ignores all defenses
            if damageType != 'psychic': # psychic ignores evasion
                effectiveEvasion = target.getEffectiveEvasion(damageType, combatUnit)
                didEvade = combatUnit.checkEvade(effectiveEvasion)

                if didEvade:
                    target.onEvade(self)
                    return 0, armourDamageReduction, esDamagePrevented, True

            if damageType != 'ethereal': # ethereal ignores armour
                effectiveArmour = target.getEffectiveArmour(damageType, combatUnit)
                reduction = combatUnit.calculateArmourReduction(finalDamage, armourIgnorePercent, effectiveArmour)
                reducedAmount = int(finalDamage * reduction)
                armourDamageReduction = finalDamage - reducedAmount
                finalDamage -= reducedAmount

                if reducedAmount > 0:
                    console.print(f"    [cyan]{target._name}'s armour reduced damage by {reducedAmount}![/cyan]")

            if damageType != 'chaos': # chaos ignores energy shield
                if energyShield > 0:
                    if finalDamage >= energyShield:
                        esDamagePrevented = energyShield - finalDamage
                        finalDamage -= energyShield
                        target._stats['energy_shield'] = 0
                        console.print(f"    [warning]{target._name}'s energy shield was broken![/warning]")
                        target.onEnergyShieldBroken(self)
                    else:
                        esDamagePrevented = finalDamage
                        target._stats['energy_shield'] -= finalDamage
                        console.print(f"    [cyan]{target._name}'s energy shield absorbed {finalDamage:.0f} damage![/cyan]")
                        return 0, armourDamageReduction, esDamagePrevented, False

        return finalDamage, armourDamageReduction, esDamagePrevented, didEvade

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

        attackerUnit.hasActed = True

        if abilityName and abilityName in attacker._abilities:
            ability = attacker._abilities[abilityName]
            console.print(f"\n[cyan]{attacker._name}[/cyan] uses [bold]{abilityName}[/bold]")

            if ability.cooldown > 0:
                printWarning(f"  - {abilityName} is on cooldown for {ability.cooldown} more turn(s).")
                return False

            if attackerUnit.team == 'player':
                ability.applyResourceCosts(attacker)

            selfEffects = ability.effects.get('self', {})
            if selfEffects:
                for effect in resolveEffects(selfEffects):
                    self.addStatusEffect(attacker, effect, attacker)

            targetEffectsDict = ability.effects.get('target', {})
            effectsBeforeTargeting: List[StatusEffect] = []

            targets = []
            if ability.targets == "all":
                if attackerUnit.team == "player":
                    targets = self.allAlive
                else:
                    targets = [u.entity for u in self.getUnitsInTeam("player")]
            elif ability.targets == "multiple":
                numTargets = 2
                if attackerUnit.team == "player":
                    available = self.allAlive
                else:
                    available = [u.entity for u in self.getUnitsInTeam("player")]
                targets = random.sample(available, min(numTargets, len(available)))
            else:
                targets = [target]

            damage = ability.calculateDamage(attacker._damage)
            damageType = ability.damageType if ability.damageType else attacker._damageType
            if attackerUnit:
                damage = int(damage * attackerUnit.getDamageModifier())

            if 'execute_bonus' in ability.tags:
                if target._health <= target._maxHealth * 0.5:
                    damage = int(damage * 1.5)
                    console.print(f"  [dark_red]{target._name} is below 50% Health - damage increased![/dark_red]")

            # TARGETING + PRE-DAMAGE MECHANICS

            damage, damageType, targets = attacker.onBeforeDamage(ability, damage, damageType, targets, self)
            effectsBeforeTargeting.extend(attacker._pendingEffects)
            attacker._pendingEffects = []

            if targets is None:
                return True

            # CRITICAL

            attacker.onBeforeCritRoll(targetUnit, targets, self)
            isCrit, critMult = attacker.rollCritical(targetUnit, damage)
            attacker.onAfterCritRoll(targetUnit, targets, self)

            if isCrit:
                damage = int(damage * critMult)
                console.print(f"[bold gold1]✨ CRITICAL {'HIT' if damageType != 'heal' else 'HEAL'}! ✨[/bold gold1] [damage]{critMult*100:.0f}%[/damage] {'damage' if damageType != 'heal' else 'healing'}!")

                damage = attacker.onCrit(targets, self, damage)
                damage = target.onCriticallyHit(attacker, self, damage, damageType)

            # in case either died through extra mechanics
            if self.checkDead(target) and len(targets) == 1:
                return
            if self.checkDead(attacker):
                return

            if damageType == 'heal':
                heal = int(ability.healBase + (attacker._maxHealth * ability.healPercent))
                attacker.heal(heal)
            else:
                # DAMAGE
                attacks = 1
                if random.random() < attacker._stats['Bonuses']['chance_to_multihit']:
                    attacks = attacker.numMultihits
                    attacker.onMultihitActivated()
                    console.print(f"[multihit]Multihit activated! Attacking {attacks} times.[/multihit]")

                finalDamage = damage * (0.75 if attacks > 1 else 1)

                for _ in range(attacks):
                    for t in targets:
                        mechanics: List[StatusEffect] = [deepcopy(m) for m in effectsBeforeTargeting]
                        mechanics.extend(resolveEffects(targetEffectsDict))

                        targetUnit = None
                        for unit in self.units:
                            if unit.entity == t:
                                targetUnit = unit
                                break

                        if targetUnit:
                            vulnMult = targetUnit.getVulnerabilityModifier()
                            if vulnMult > 1.0:
                                finalDamage = int(damage * vulnMult)
                                console.print(f"  [debuff]- {t._name} is vulnerable (+{vulnMult*100:.0f}% Damage Taken). Damage increased to {finalDamage}[/debuff]")

                        if len(targets) > 1:
                            finalDamage = int(finalDamage * 0.8)
                            console.print(f"  [dim]|- Hitting {t._name}[/dim]")

                        finalDamage = attacker.onPrepareHit(t, targetUnit, finalDamage, damageType, self)
                        mechanics.extend(attacker._pendingEffects)
                        attacker._pendingEffects = []

                        finalDamage = t.onBeforeHit(finalDamage, damageType, attacker, self)

                        finalDamage, damageType = attacker.onAttack(finalDamage, damageType, targetUnit, self, ability, isCrit)
                        mechanics.extend(attacker._pendingEffects)
                        attacker._pendingEffects = []

                        armourIgnorePercent = attacker.getArmourIgnorePercent()

                        preMitigationDamage = finalDamage

                        finalDamage, armourDamagePrevented, esDamagePrevented, evaded = self.applyDamageWithDefenses(t, finalDamage, damageType, targetUnit, armourIgnorePercent)
                        finalDamage, damageType = t.onHit(finalDamage, damageType, isCrit, attacker, self)

                        finalDamage = attacker.onDealDamage(t, targetUnit, finalDamage, damageType, evaded, armourDamagePrevented, esDamagePrevented, self)

                        finalDamage = t.onAfterMitigation(attacker, finalDamage, damageType, evaded, armourDamagePrevented, esDamagePrevented, preMitigationDamage, self)

                        if attacker._stats['Bonuses']['lifesteal'] > 0:
                            heal = int(finalDamage * (attacker._stats['Bonuses']['lifesteal'] / 100))
                            attacker.heal(heal)

                        damageReductionValue = 0
                        if evaded:
                            console.print(f'[evasion bold]{t._name} evaded the attack![/evasion bold]')
                            t.onEvade(self)
                        else:
                            damageReductionValue = t.damage(finalDamage, damageType, targetUnit, attacker=attacker)
                            t.onDamaged(attacker, damageReductionValue, armourDamagePrevented, self)

                            thorns = t._stats['Bonuses']['thorns']
                            if thorns > 0:
                                console.print(f"- {attacker._name} takes {thorns} Thorns Damage!")
                            attacker.damage(thorns, 'physical')

                            attacker.onAfterAttack(t, targetUnit, finalDamage, self)

                    if not evaded:
                        if mechanics and not t._isDead:
                            for mechanic in mechanics:
                                mechanic = t.onStatusApplied(mechanic, attacker)
                                if mechanic:
                                    self.addStatusEffect(t, mechanic, attacker)
                                    if mechanic.effectType == 'cc':
                                        t.onCC(attacker, self)
                        death = self.checkDead(t)
                        if death:
                            killData = {'damage': finalDamage, 'damageType': damageType, 'mechanics': mechanics}
                            attacker.onKill(t, killData, self)
                        else:
                            attacker.onExecuteCheck(t, self) # check for any executes (e.g. blood spike or ascendancy-specific)

                        if t._isDead:
                            break # prevent multihit bugs

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