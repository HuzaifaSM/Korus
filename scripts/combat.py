from typing import List, Optional, Tuple
from enum import Enum
from copy import deepcopy
import random
from rich.text import Text
from .entities import Entity
from .enemies.enemy import Enemy
from .abilities import StatusEffect, resolveEffects
from .styles import (
    console, printWarning, formatDamageBreakdown, pause
)
from .enemies.enemyAi import EnemyAI

_TRUE_ORIGINAL_PRINT = console.print

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
        self.initiative = round(self._baseInitiative * multiplier)

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

        ELEMENTAL_TYPES = ['fire', 'cold', 'lightning', 'earth']
        DIVINE_TYPES = ['holy', 'dark', 'arcane']
        OTHERWORLD_TYPES = ['chaos', 'ethereal', 'psychic']

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
        self.battleLog: list[str] = []

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
        self.battleLog = []
        self.combatLog: List[str] = []
        self._originalPrint = _TRUE_ORIGINAL_PRINT
        console.print = self._capturePrint

        self.player = self.registerUnit(player, "player")
        enemyUnits = [self.registerUnit(enemy, "enemy") for enemy in enemies]

        self.player.entity.onCombatStart(self, self.player)
        self.player.entity._mythicDispatch('onCombatStart', self, self.player)
        for enemy, e in zip(enemies, enemyUnits):
            enemy.onCombatStart(self, e)
            enemy._mythicDispatch('onCombatStart', self, e)

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
            currentUnit.entity._mythicDispatch('onTurnEnd')
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
                nextEntity._mythicDispatch('onTurnStart', self)
                if nextEntity.hasLiveConditionalModifiers():
                    nextEntity._recalculateStats(False, True)  # refreshes mythic conditional_modifier state each turn - some class onTurnStart overrides skip super(), so this can't rely on Entity.onTurnStart's own recalc call

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
            self.endBattle()
            return "enemy"
        elif self.isTeamDefeated("enemy"):
            self.endBattle()
            return "player"
        return None

    def _capturePrint(self, *args, **kwargs):
        parts = []
        for arg in args:
            plain = Text.from_markup(arg).plain if isinstance(arg, str) else str(arg)
            if plain.strip():
                parts.append(plain.strip())
        if parts:
            self.combatLog.append(f"[Turn {self.turnNumber}] {' '.join(parts)}")
        self._originalPrint(*args, **kwargs)

    def endBattle(self):
        self.battleActive = False
        console.print = _TRUE_ORIGINAL_PRINT
        if hasattr(self, '_originalPrint'):
            del self._originalPrint

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
        if type(target) is list:
            target = target[0]
        if target._isDead:
            for unit in self.units:
                if unit.entity == target:
                    self.unregisterUnit(unit)
            return True
        return False

    def applyDamageWithDefenses(self, target: Entity, damage: int, damageType: str, combatUnit: CombatUnit=None, armourIgnorePercent: float = 0.0) -> Tuple[int, int, int, bool, bool]:
        finalDamage = damage

        energyShield = target.energyShield

        didEvade = False
        didBlock = False
        armourDamagePrevented = 0
        esDamagePrevented = 0

        if damageType != 'ethereal': # blocking negates all damage apart from ethereal - even 'true' damage
            blockChance = target._stats['Bonuses']['chance_to_block']
            if blockChance > 0 and random.random() * 100 < blockChance:
                didBlock = True
                target.onBlock(self)
                target._mythicDispatch('onBlock', self)
                return 0, armourDamagePrevented, esDamagePrevented, didEvade, didBlock

        if damageType != 'true': # true damage ignores all other defenses
            if damageType != 'psychic': # psychic ignores evasion
                effectiveEvasion = target.getEffectiveEvasion(damageType, combatUnit)
                rollCount = max(1, target.getEvasionRollCount(damageType))
                didEvade = any(combatUnit.checkEvade(effectiveEvasion) for _ in range(rollCount))

                if didEvade:
                    target.onEvade(self)
                    target._mythicDispatch('onEvade', self)
                    return 0, armourDamagePrevented, esDamagePrevented, True, didBlock

            if damageType != 'ethereal': # ethereal ignores armour
                effectiveArmour = target.getEffectiveArmour(damageType, combatUnit)
                reduction = combatUnit.calculateArmourReduction(finalDamage, armourIgnorePercent, effectiveArmour)
                armourDamagePrevented = int(finalDamage * reduction)
                finalDamage -= armourDamagePrevented

            if damageType != 'chaos': # chaos ignores energy shield
                if energyShield > 0:
                    if finalDamage >= energyShield:
                        esDamagePrevented = energyShield
                        finalDamage -= energyShield
                        target._stats['energy_shield'] = 0
                        console.print(f"    [warning]{target._name}'s energy shield was broken![/warning]")
                        target.onEnergyShieldBroken(self)
                        target._mythicDispatch('onEnergyShieldBroken', self)
                    else:
                        esDamagePrevented = finalDamage
                        target._stats['energy_shield'] -= finalDamage
                        console.print(f"    [cyan]{target._name}'s energy shield absorbed {finalDamage:.0f} damage![/cyan]")
                        return 0, armourDamagePrevented, esDamagePrevented, False, didBlock

        return finalDamage, armourDamagePrevented, esDamagePrevented, didEvade, didBlock

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
            ability.cooldown = ability.maxCooldown  # set here (not just in onAttack) so heal/buff-category abilities go on cooldown too

            if attackerUnit.team == 'player':
                ability.applyResourceCosts(attacker)
            else:
                attacker._stamina = max(0, attacker._stamina - ability.staminaCost)

            selfEffects = ability.effects.get('self', {})
            attackerAscendancy = getattr(attacker, '_ascendancy', None)
            ascendancyValue = getattr(attackerAscendancy, 'value', attackerAscendancy)  # enum for enemies, plain string for players
            selfPreservingSubclass = ascendancyValue in ('tank', 'healer')
            isSupportSelfBuff = (
                ability.targets == 'self' and attackerUnit.team != 'player' and
                getattr(getattr(attacker, 'className', None), 'value', None) == 'support' and
                not selfPreservingSubclass
            )
            if ability.targets == 'all_allies':
                effectRecipients = list(self.allAlive)
            elif ability.targets == 'ally':
                effectRecipients = [target]
            elif isSupportSelfBuff:
                allies = [a for a in self.allAlive if a is not attacker and not a._isDead]
                effectRecipients = [random.choice(allies)] if allies else [attacker]
            else:
                effectRecipients = [attacker]

            for recipient in effectRecipients:
                if 'taunt' in selfEffects and hasattr(recipient, 'applyTaunt'):
                    recipient.applyTaunt(selfEffects['taunt'].get('turns', 1))
                if selfEffects:
                    for effect in resolveEffects(selfEffects):
                        self.addStatusEffect(recipient, effect, attacker)

            attacker.onAbilityCast(ability, self)  # fires once per use regardless of category - the only hook heal/buff abilities reach
            attacker._mythicDispatch('onAbilityCast', ability, self)

            targetEffectsDict = ability.effects.get('target', {})
            effectsBeforeTargeting: List[StatusEffect] = []

            targets = []
            if ability.targets == "all":
                if attackerUnit.team == "player":
                    targets = self.allAlive
                else:
                    targets = [u.entity for u in self.getUnitsInTeam("player")]
            elif ability.targets == "all_allies":
                targets = list(self.allAlive)  # 0-damage, no target-side effects on these - just needs a non-empty list
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
            for _mResult in attacker._mythicDispatch('onBeforeDamage', ability, damage, damageType, targets, self):
                if isinstance(_mResult, dict):
                    damage = _mResult.get('damage', damage)
                    damageType = _mResult.get('damageType', damageType)
                    targets = _mResult.get('targets', targets)
            effectsBeforeTargeting.extend(attacker._pendingEffects)
            attacker._pendingEffects = []

            if targets is None:
                return True

            # CRITICAL

            attacker.onBeforeCritRoll(targetUnit, targets, self)
            attacker._mythicDispatch('onBeforeCritRoll', targetUnit, targets, self)
            isCrit, critMult = attacker.rollCritical(targetUnit, damage)
            attacker.onAfterCritRoll(targetUnit, targets, self)
            attacker._mythicDispatch('onAfterCritRoll', targetUnit, targets, self)

            if isCrit:
                damage = int(damage * critMult)
                console.print(f"[bold gold1]✨ CRITICAL {'HIT' if damageType != 'heal' else 'HEAL'}! ✨[/bold gold1] [damage]{critMult*100:.0f}%[/damage] {'damage' if damageType != 'heal' else 'healing'}!")

                damage = attacker.onCrit(targets, self, damage)
                for _mResult in attacker._mythicDispatch('onCrit', targets, self, damage):
                    damage = _mResult
                damage = target.onCriticallyHit(attacker, self, damage, damageType)
                for _mResult in target._mythicDispatch('onCriticallyHit', attacker, self, damage, damageType):
                    damage = _mResult

            # in case either died through extra mechanics
            if self.checkDead(target) and len(targets) == 1:
                return
            if self.checkDead(attacker):
                return

            if damageType == 'heal':
                heal = int(ability.healBase + (attacker._maxHealth * ability.healPercent))
                attacker.heal(heal, reason=abilityName)
            else:
                # DAMAGE
                attacks = 1
                if random.random() < attacker.chanceToMultihit:
                    attacks = attacker.numMultihits
                    attacker.onMultihitActivated()
                    attacker._mythicDispatch('onMultihitActivated')
                    console.print(f"[multihit]Multihit activated! Attacking {attacks} times.[/multihit]")

                starterDamage = damage * (0.75 if attacks > 1 else 1)

                for _ in range(attacks):
                    for t in targets:
                        if t._isDead: # a prior multihit repetition already killed this target (and unregistered it)
                            continue
                        finalDamage = starterDamage
                        baseDamageForBreakdown = int(finalDamage)
                        attacker._damageLog = []

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
                                finalDamage = int(finalDamage * vulnMult)
                                attacker._logDamage(f"{t._name} Vulnerable", percent=vulnMult - 1.0)

                        if len(targets) > 1:
                            finalDamage = int(finalDamage * 0.8)
                            attacker._logDamage("Multiple Targets", percent=-0.2)
                            console.print(f"  [dim]|- Hitting {t._name}[/dim]")

                        finalDamage = attacker.onPrepareHit(t, targetUnit, finalDamage, damageType, self)
                        for _mResult in attacker._mythicDispatch('onPrepareHit', t, targetUnit, finalDamage, damageType, self):
                            finalDamage = _mResult
                        mechanics.extend(attacker._pendingEffects)
                        attacker._pendingEffects = []

                        finalDamage = t.onBeforeHit(finalDamage, damageType, attacker, self)
                        for _mResult in t._mythicDispatch('onBeforeHit', finalDamage, damageType, attacker, self):
                            finalDamage = _mResult

                        finalDamage, damageType = attacker.onAttack(finalDamage, damageType, targetUnit, self, ability, isCrit)
                        for _mResult in attacker._mythicDispatch('onAttack', finalDamage, damageType, targetUnit, self, ability, isCrit):
                            if isinstance(_mResult, dict):
                                finalDamage = _mResult.get('damageDealt', finalDamage)
                                damageType = _mResult.get('damageType', damageType)
                        mechanics.extend(attacker._pendingEffects)
                        attacker._pendingEffects = []

                        armourIgnorePercent = attacker.getArmourIgnorePercent()

                        preMitigationDamage = finalDamage

                        finalDamage, armourDamagePrevented, esDamagePrevented, evaded, blocked = self.applyDamageWithDefenses(t, finalDamage, damageType, targetUnit, armourIgnorePercent)
                        if armourDamagePrevented > 0:
                            attacker._logDamage("Armour Mitigation", flat=-armourDamagePrevented)
                        if esDamagePrevented > 0:
                            attacker._logDamage(f"{t._name}'s Energy Shield", flat=-esDamagePrevented)
                        finalDamage, damageType = t.onHit(finalDamage, damageType, isCrit, attacker, self)
                        for _mResult in t._mythicDispatch('onHit', finalDamage, damageType, isCrit, attacker, self):
                            if isinstance(_mResult, dict):
                                finalDamage = _mResult.get('damageTaken', finalDamage)
                                damageType = _mResult.get('damageType', damageType)

                        finalDamage = attacker.onDealDamage(t, targetUnit, finalDamage, damageType, evaded or blocked, armourDamagePrevented, esDamagePrevented, self)
                        for _mResult in attacker._mythicDispatch('onDealDamage', t, targetUnit, finalDamage, damageType, evaded or blocked, armourDamagePrevented, esDamagePrevented, self):
                            finalDamage = _mResult

                        finalDamage = t.onAfterMitigation(attacker, finalDamage, damageType, evaded or blocked, armourDamagePrevented, esDamagePrevented, preMitigationDamage, self)
                        for _mResult in t._mythicDispatch('onAfterMitigation', attacker, finalDamage, damageType, evaded or blocked, armourDamagePrevented, esDamagePrevented, preMitigationDamage, self):
                            finalDamage = _mResult

                        if attacker._stats['Bonuses']['lifesteal'] > 0:
                            heal = int(finalDamage * (attacker._stats['Bonuses']['lifesteal'] / 100))
                            attacker.heal(heal, reason=f"{attacker._stats['Bonuses']['lifesteal']:.0f}% Lifesteal")

                        damageReductionValue = 0
                        if evaded:
                            console.print(f'[evasion bold]{t._name} evaded the attack![/evasion bold]')
                            t.onEvade(self)
                            t._mythicDispatch('onEvade', self)
                        elif blocked:
                            console.print(f'[cyan bold]{t._name} blocked the attack![/cyan bold]')
                            t.onBlock(self)
                            t._mythicDispatch('onBlock', self)
                        else:
                            if attacker._damageLog:
                                for line in formatDamageBreakdown(baseDamageForBreakdown, attacker._damageLog, finalDamage, damageType):
                                    console.print(line)
                            damageReductionValue = t.damage(finalDamage, damageType, targetUnit, attacker=attacker)
                            t.onDamaged(attacker, damageReductionValue, armourDamagePrevented, self)
                            t._mythicDispatch('onDamaged', attacker, damageReductionValue, armourDamagePrevented, self)

                            thorns = t._stats['Bonuses']['thorns']
                            if thorns > 0:
                                console.print(f"- {attacker._name} takes {thorns} Thorns Damage!")
                            attacker.damage(thorns, 'physical')

                            attacker.onAfterAttack(t, targetUnit, finalDamage, self)
                            attacker._mythicDispatch('onAfterAttack', t, targetUnit, finalDamage, self)

                        if not evaded and not blocked:
                            if mechanics and not t._isDead:
                                for mechanic in mechanics:
                                    mechanic = t.onStatusApplied(mechanic, attacker)
                                    for _mResult in t._mythicDispatch('onStatusApplied', mechanic, attacker):
                                        mechanic = _mResult
                                    if mechanic:
                                        self.addStatusEffect(t, mechanic, attacker)
                                        if mechanic.effectType == 'cc':
                                            t.onCC(attacker, self)
                                            t._mythicDispatch('onCC', attacker, self)
                            death = self.checkDead(t)
                            if death:
                                killData = {'damage': finalDamage, 'damageType': damageType, 'mechanics': mechanics, 'ability': ability}
                                attacker.onKill(t, killData, self)
                                attacker._mythicDispatch('onKill', t, killData, self)
                            else:
                                if attacker.onExecuteCheck(t, self):
                                    t.damage(t._health, 'true', targetUnit, attacker=attacker)
                                    self.checkDead(t)
                                attacker._mythicDispatch('onExecuteCheck', t, self)

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

        if not self._enemyDecisions: # build snapshot for all enemies this round, cache it
            enemyUnits = self.getUnitsInTeam('enemy')
            allies = [u.entity for u in enemyUnits]
            actionLists = [e.ai.buildActionList(allies) for e in allies]
            buffStates = [any(effect.effectType == 'buff' for effect in u.statusEffects) for u in enemyUnits]
            ignoresDangerStates = [random.random() < getattr(e, 'aggression', 0.3) for e in allies]
            actsDefensivelyStates = [random.random() < getattr(e, 'cautious', 0.3) for e in allies]
            self._enemyDecisions = EnemyAI.decideTurn(
                allies, aliveTargets[0], actionLists, buffStates, ignoresDangerStates, actsDefensivelyStates
            )
            self._enemyIndexMap = {e: i for i, e in enumerate(allies)}

        idx = self._enemyIndexMap.get(enemy, 0)
        decision = self._enemyDecisions.get(idx)
        enemy.ai.applyDecision(decision, aliveTargets[0], self)

    def _setPhaseForUnit(self, unit: CombatUnit):
        if unit.team == "player":
            self.currentPhase = TurnPhase.PLAYER_TURN
        elif unit.team == "enemy":
            self.currentPhase = TurnPhase.ENEMY_TURN

...