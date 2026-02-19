from typing import List, Optional, Tuple
from enum import Enum
import random
from .entities import Entity
from .abilities import Effects, StatusEffect
from .styles import (
    console, printSuccess, printWarning, printError, printInfo, formatDamageType, pause
)
from expansions.bosses.bosses import Boss

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

    def canAct(self) -> bool:
        if not self.isActive:
            return False
        stunned = False
        for effect in self.statusEffects:
            if effect.type == 'cc' and effect.data.get('effect') in ['stun', 'freeze']:
                if not self.rollStunAvoidance():
                    stunned = True
                    break
                else:
                    self.statusEffects.remove(effect)
        return not stunned
    
    def isStunned(self) -> bool:
        return any(effect.type == "cc" and effect.data.get('effect') in ['stun', 'immobilize', 'freeze']
                   for effect in self.statusEffects)
    
    def isSlowed(self) -> bool:
        return any(effect.type == "slow" for effect in self.statusEffects)
    
    def _recalculateInitiative(self):
        multiplier = 1.0

        for effect in self.statusEffects:
            if effect.name in ['freeze', 'slow']:
                amount = effect.data['amount']
                multiplier *= (1 - amount)
        
        multiplier = round(multiplier, 2)
        self.initiative = round(self._baseInitiative, )
    
    def getDamageModifier(self) -> float:
        modifier = 1.0
        for effect in self.statusEffects:
            if effect.type == "debuff" and effect.data.get('effect') == 'damage_reduction': #weaken/disarm
                modifier *= (1 - effect.data.get('amount', 0))
            
            if effect.type == "debuff" and effect.data.get('effect') == 'damage_amplification': #vulnerable
                modifier *= (1 + effect.data.get('amount', 0))
        
        return modifier
    
    def getResistanceModifier(self, damageType: str) -> float:
        baseResist = self.entity._stats['Resistances'].get(damageType, 0)

        baseResist += self.entity._stats['Resistances'].get('all', 0)

        ELEMENTAL_TYPES = ['fire', 'cold', 'lightning', 'wind', 'earth']
        if damageType in ELEMENTAL_TYPES:
            baseResist += self.entity._stats['Resistances'].get('elemental', 0)

        DIVINE_TYPES = ['holy', 'dark', 'arcane']
        if damageType in DIVINE_TYPES:
            baseResist += self.entity._stats['Resistances'].get('divine', 0)

        for effect in self.statusEffects:
            if effect.type == "debuff":
                effectName = effect.name

                if effectName == f"{damageType}_reduction":
                    baseResist -= effect.data.get('amount', 0)
                if effectName == "all_reduction":
                    baseResist -= effect.data.get('amount', 0)
        return min(baseResist, 75)

    def calculateArmourReduction(self, incomingDamage: int) -> float:
        armour = self.entity._stats.get('armour', 0)
        if armour == 0:
            return 0
        reduction = armour / (armour + (10 * incomingDamage))
        return min(0.9, reduction)

    def checkEvade(self):
        return self.entropyTracker.rollEvasion(self.entity._stats.get('evasion', 0))

    def getVulnerabilityModifier(self) -> float:
        multiplier = 1.0
        for effect in self.statusEffects:
            if effect.name == 'vulnerable' or effect.name == 'brittle':
                multiplier += effect.data.get('amount', 0)
        return multiplier

class CombatManager:
    def __init__(self):
        self.units: List[CombatUnit] = []
        self.turnOrder: List[CombatUnit] = []
        self.currentTurnIndex = 0
        self.currentPhase = TurnPhase.PLAYER_TURN
        self.turnNumber = 0
        self.battleActive = False

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
            while not nextUnit.canAct() and attempts < len(self.turnOrder):
                console.print(f"[warning]{nextUnit.entity._name} is stunned and cannot act![/warning]")
                nextUnit.resetTurn()
                self.currentTurnIndex += 1
                if self.currentTurnIndex >= len(self.turnOrder):
                    self.currentTurnIndex = 0
                nextUnit = self.getCurrentUnit()
                attempts += 1

            self._setPhaseForUnit(nextUnit)
            nextEntity = nextUnit.entity
            nextEntity.onTurnStart(self)
            if nextEntity.className == 'Rogue':
                if nextEntity._subType == 'Vanguard' and not nextEntity.vanguardUsed:
                    if nextEntity.combatHealthLost >= (nextEntity._maxHealth * 0.3):
                        console.print(f"\n  [buff]- Vanguard: More than 30% health lost this combat! 50% of remaning health dealt as Dark damage to all enemies.[/buff]")
                        targets = [u.entity for u in self.getUnitsInTeam('enemy')]
                        damage = int(nextEntity._health * 0.5)
                        for target in targets:
                            target.damage(damage, 'dark')

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
            if target.className == 'Mutant':
                enemies = [u.entity for u in self.getUnitsInTeam('enemy') if u.isActive]
                target.reflectDoTs(attacker, statusEffect, self, enemies)

            avoidChance = target._stats['Bonuses'].get('ailmentAvoidance', 0)
            if random.random() < avoidChance: # avoided ailment
                console.print(f"\n  [buff]- {target._name} avoided being afflicted by {statusEffect['name']}! ({avoidChance}% Chance.)[/buff]")
                if target.className == 'Rogue' and target._ascendancy == 'Trickster':
                    for unit in self.units: # apply effect back to attacker
                        if unit.entity == attacker:
                            attackerUnit = unit
                            break
                    attackerUnit.statusEffects.append(statusEffect)
                    console.print(f"    [buff]- Trickster: Applied {statusEffect.name} to {attacker._name} instead![/buff]")
            else:
                if statusEffect.name == 'poison' and attacker.className == 'Rogue' and attacker._ascendancy == 'Shadow':
                    statusEffect.data['damage'] *= 2
                targetUnit.statusEffects.append(statusEffect)
                console.print(f"  [debuff]- {statusEffect.name} applied.[/debuff]")

    def checkDead(self, target: Entity):
        if target._isDead:
            for unit in self.units:
                if unit.entity == target:
                    self.unregisterUnit(unit)
            return True
        return False

    def applyDamageWithDefenses(self, target: Entity, damage: int, damageType: str, combatUnit: CombatUnit=None) -> Tuple[int, bool]:
        finalDamage = damage

        didEvade = False
        if damageType != 'true': # true damage ignores all defenses
            if damageType != 'psychic': # psychic ignores evasion
                didEvade = combatUnit.checkEvade()
                if didEvade:
                    target.onEvade()
                    console.print(f"    [buff]{target._name} dodged the attack![/buff]")
                    return 0

            if damageType != 'ethereal': # ethereal ignores armour
                reduction = combatUnit.calculateArmourReduction(finalDamage)
                reducedAmount = round(finalDamage * reduction)
                finalDamage -= reducedAmount

                if reducedAmount > 0:
                    console.print(f"    [cyan]{target._name}'s armour reduced damage by {reducedAmount}![/cyan]")

            if damageType != 'chaos': # chaos ignores energy shield
                currentES = target.energyShield
                if currentES > 0:
                    if finalDamage >= currentES:
                        finalDamage -= currentES
                        target._stats['energyShield'] = 0
                        console.print(f"    [warning]{target._name}'s energy shield was broken![/warning]")
                    else:
                        target._stats['energyShield'] -= finalDamage
                        console.print(f"    [cyan]{target._name}'s energy shield absorbed {finalDamage} damage![/cyan]")
                        return 0
                
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

            if ability.cooldown > 0:
                printWarning(f"  - {abilityName} is on cooldown for {ability.cooldown} more turn(s).")
                return False

            mechanics = ability.effects.copy()

            # Determine targets
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

            damage = ability.damage + attacker._damage
            damageType = ability.damageType
            if attackerUnit:
                damage = int(damage * attackerUnit.getDamageModifier())

            # EXTRA TARGETING + MECHANICS

            if attacker.className == 'Monk':
                if attacker._ascendancy == 'Stormwalker' and damageType == 'lightning':
                    available = [u.entity for u in self.getUnitsInTeam('enemy')]
                    for _ in range(2):
                        targets.append(random.choice(available))
                        console.print(f"  [lightning]- Stormwalker: Lightning damage forks to {target._name}![/lightning]")
                    if random.random() < 0.4:
                        mechanics.append('shock')
                        console.print(f"  [lightning]- Stormwalker: Lightning damage applied Shock to {target._name}![/lightning]")

                elif attacker._ascendancy == 'Glacierfist':
                    if random.random() < 0.25:
                        chill = Effects.createChill()
                        mechanics.append(chill)
                    if random.random() < 0.2:
                        freeze = Effects.createFreeze()
                        mechanics.append(freeze)
                if attacker._subType == 'Manafist':
                    if damageType == 'lightning':
                        console.print(f'  [buff]- Manafist: Lightning damage applied chill![/buff]')
                        chill = Effects.createChill()
                        mechanics.append(chill)
                    elif damageType == 'cold':
                        console.print(f'  [buff]- Manafist: Cold damage applied shock![/buff]')
                        shock = Effects.createShock()
                        mechanics.append(shock)

                elif attacker._ascendancy == 'Enlightened':
                    if damageType != attacker._damageType:
                        allEnemies = [u.entity for u in self.getUnitsInTeam('enemy')]
                        aoeDamage = int(attacker._baseDamage * 1.3)
                        console.print(f'  [gold1]- Enlightened: Element mismatch! {aoeDamage} {attacker._damageType} damage to all enemies![/gold1]')
                        for enemy in allEnemies:
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

                    if attacker._subType == 'Shattered' and random.random() <= 0.1:
                        stun = Effects.createStun()
                        mechanics.append(stun)
                        console.print("  [buff]- Shattered: Lost attack applies stun to all enemies![/buff]")
                        buffs = ['damage', 'speed', 'lifesteal']
                        buff = random.choice(buffs)
                        attacker.shatteredBuffs[buff] = min(2, attacker.shatteredBuffs.get(buff, 0) + 2)
                        buffInfo = ""
                        if buff == 'damage':
                            buffInfo = "+10% Damage Dealt"
                        elif buff == 'speed':
                            buffInfo = "+0.3 Speed"
                        elif buff == 'lifesteal':
                            buffInfo = "+15% Lifesteal"
                        console.print(f'  [buff]- Shattered: Gained Shattered {buff} buff for 2 turns. ({buffInfo})[/buff]')

                    if attacker._ascendancy == 'Weaver':
                        attacker.wovenDamage += 10
                        weaken = Effects.createWeaken()
                        mechanics.append(weaken)
                        exposed = Effects.createExposed()
                        mechanics.append(exposed)
                        console.print('  [buff]- Weaver: Lost Triggered! Applied Weaken and Lost to all enemies! +10 Damage for the rest of combat.[/buff]')

                if attacker._ascendancy == 'Fractured':
                    if attacker.fracture >= 5 and damageType != 'heal':
                        console.print(f"  [buff]- Fractured: Fracture stacks have reached 5. Attacking all enemies for 150% damage. Fracture stacks set to 0.[/buff]")
                        targets = [u.entity for u in self.getUnitsInTeam('enemy')]

            elif attacker.className == 'Mage':
                if attacker._ascendancy == 'Elementalist' and damageType in ['arcane', 'cold', 'earth', 'fire', 'lightning', 'wind']:
                    if attacker.elementalistAttackCount % 3 == 0:
                        allEnemies = [u.entity for u in self.getUnitsInTeam('enemy')]
                        if len(allEnemies) == 1:
                            damage *= 2
                            targets = allEnemies
                            console.print(f'[gold1]Elementalist: 3rd elemental attack! Single target: 200% damage![/gold1]')
                        else:
                            damage = int(damage * 0.6)
                            targets = allEnemies
                            console.print(f'[gold1]Elementalist: 3rd elemental attack! Hitting all enemies for 60% damage![/gold1]')

                elif attacker._ascendancy == 'Fluxweaver' and damageType in ['arcane', 'cold', 'earth', 'fire', 'lightning', 'wind']:
                    if random.random() < 0.3:
                        exposure = Effects.createElementalExposure()
                        mechanics.append(exposure)
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
                            mechanics.append(b)
                elif attacker._ascendancy == 'Juggernaut' and attacker._fortify >= attacker._maxFortify and attacker._rage >= 100:
                    targets = [u.entity for u in self.getUnitsInTeam('enemy')]
                    stun = Effects.createStun()
                    mechanics.append(stun)
                    console.print(f'[gold1]Juggernaut: Max Fortify - Stunning all enemies! -100 Rage.[/gold1]')
                    attacker._rage -= 100

            elif attacker.className == 'Spectre':
                if attacker._subType == 'Incorporeal' and damageType == 'ethereal':
                    allTargets = self.getUnitsInTeam('enemy')
                    allTargets = [t.entity for t in allTargets if t != target]
                    if allTargets:
                        extraTarget = random.choice(allTargets)
                        bonusDamage = int(damage * 0.3)
                        extraTarget.damage(bonusDamage, damageType)
                        console.print(f"  [ethereal]Incorporeal: Ethereal form strikes {extraTarget._name} for {bonusDamage} damage![/ethereal]")

                if attacker._ascendancy == 'Phantasm' and damageType == 'ethereal':
                    if random.random() < 0.3:
                        allEnemies = [u.entity for u in self.getUnitsInTeam('enemy')]
                        phased = Effects.createCustom(name='phased', effectType='special', duration=3, speedBonus=-0.2, damageMultiplier=0.9)
                        for enemy in allEnemies:
                            self.addStatusEffect(enemy, phased, attacker)
                            console.print(f"  [ethereal]Phantasm: Applied Phased to {enemy._name}![/ethereal]")

            elif attacker.className == 'Ranger':
                if attacker._ascendancy == 'Skirmisher' and attacker.skirmisherHits > 0:
                    allTargets = [u.entity for u in self.getUnitsInTeam('enemy')]
                    allTargets = [u for u in allTargets if u != target]
                    if allTargets:
                        extraTargets = random.sample(allTargets, 2)
                        bonusDamage = int(damage * 0.3)
                        for et in extraTargets:
                            et.damage(bonusDamage, 'wind')
                            console.print(f"  [wind]Skirmisher: Skirmisher Momentum buff attacks {et._name} for {bonusDamage} damage![/wind]")
                elif attacker._ascendancy == 'Tempest' and attacker.tailwind >= 12:
                    if random.random() < 0.3:
                        ailment = random.choice(['shock', 'chill', 'burn', 'elemental_exposure'])
                        if ailment == 'shock':
                            ailment = Effects.createShock(3, 0.2)
                        elif ailment == 'chill':
                            ailment = Effects.createChill(1)
                        elif ailment == 'burn':
                            ailment = Effects.createBurn(1)
                        elif ailment == 'elemental_exposure':
                            ailment = Effects.createElementalExposure(3)
                        mechanics.append(ailment)

            elif attacker.className == 'Druid':
                if attacker._subType == 'Feral' and attacker.form == 'beast':
                    bleed = Effects.createBleed()
                    for b in bleed:
                        mechanics.append(b)

            elif attacker.className == 'Cultist':
                if attacker._ascendancy == 'Harbinger' and attacker.insanity == attacker.maxInsanity:
                    curse = Effects.createCurse(2)
                    for c in curse:
                        mechanics.append(c)

                elif attacker._ascendancy == 'Anarchist':
                    if attacker.volatility == attacker.maxVolatility and attacker.insanity > 0:
                        allEnemies = [u.entity for u in self.getUnitsInTeam('enemy')]
                        if allEnemies:
                            aoeDamage = int(attacker._maxHealth * (0.01 * (attacker.insanity // 5)))
                            for e in allEnemies:
                                e.damage(aoeDamage, 'chaos')
                        attacker.volatility = 0
                        attacker._randomiseInsanity(min=-10, max=30)

            # CRITICAL

            if damageType != 'heal':
                isCrit, critMult = attacker.rollCritical(targetUnit, damage)
                if isCrit:
                    damage = int(damage * critMult)
                    console.print(f"[bold gold1]✨ CRITICAL HIT! ✨[/bold gold1] [damage]{critMult*100:.0f}%[/damage] damage!")
                    if attacker.className == 'Monk' and attacker._subType == 'Pugilist':
                        exposed = Effects.createExposed()
                        self.addStatusEffect(target, exposed)
                        console.print(f"  [debuff]- Pugilist: {target._name} is Exposed![/debuff]")
                    
                    elif attacker.className == 'Ranger':
                        if attacker._subType == 'Sharpshooter':
                            exposure = Effects.createElementalExposure(3)
                            mechanics.append(exposure)
                        if attacker._ascendancy == 'Sniper':
                            if attacker.tailwind >= 7:
                                vulnerable = Effects.createVulnerable(2, 0.5)
                                mechanics.append(vulnerable)

                    elif attacker.className == 'Druid':
                        if attacker._subType == 'Feral' and attacker.form == 'beast':
                            bleed = Effects.createBleed()
                            for b in bleed:
                                mechanics.append(b)

                    elif attacker.className == 'Paladin':
                        if attacker._ascendancy == 'Justicar':
                            living = len([u for u in self.getUnitsInTeam('enemy') if u.isActive])
                            attacker.favour = min(attacker.maxFavour,
                                                  attacker.favour + living * 5)

                    if target.className == 'Wanderer':
                        if target._ascendancy == 'Mindbreaker' and attacker.tortureStacks > 0:
                            attacker.tortureStacks = 0
                            console.print(f"  [warning]- Mindbreaker: {attacker._name} has removed all their torture stacks![/warning]")

            if damage < 0:
                healAmount = abs(damage)
                attacker.heal(healAmount)
            else:
                # DAMAGE
                for t in targets:
                    targetUnit = None
                    for unit in self.units:
                        if unit.entity == t:
                            targetUnit = unit
                            break
                    
                    finalDamage = damage
                    if targetUnit:
                        vulnMult = targetUnit.getVulnerabilityModifier()
                        if vulnMult > 1.0:
                            finalDamage = int(damage * vulnMult)
                            console.print(f"  [debuff]- {t._name} is vulnerable. Damage increased to {finalDamage}[/debuff]")

                    if len(targets) > 1:
                        finalDamage = int(damage * 0.8)
                        console.print(f"  [dim]|- Hitting {t._name}[/dim]")
                        
                    if attacker.className == 'Monk':
                        if attacker._ascendancy == 'Stormwalker':
                            if any(e.name == 'shock' for e in targetUnit.statusEffects):
                                attacker._prowess += 1
                                console.print(f"  [buff]Stormwalker: Hit shocked enemy! +1 Prowess![/buff]")

                                allEnemies = [u for u in self.getUnitsInTeam('enemy')]
                                targetShockValue = [s.amount for s in targetUnit.statusEffects if s.name == 'shock'][0]
                                otherEnemies = [e for e in allEnemies if e != targetUnit]
                                if otherEnemies:
                                    spread = random.choice(otherEnemies)
                                    shock = Effects.createShock(amount=targetShockValue)
                                    self.addStatusEffect(t, shock, attacker)
                                    console.print(f"  [lightning]Stormwalker: Shock spread to {spread._name}![/lightning]")

                        if attacker._subType == 'Manafist':
                            hasChill = any(e.name == 'chill' for e in targetUnit.statusEffects)
                            hasShock = any(e.name == 'shock' for e in targetUnit.statusEffects)
                            if hasChill and hasShock:
                                damage = int(damage * 1.3)
                                console.print(f"  [gold1]Manafist: {target._name} has both Shock and Chill! +30% damage![/gold1]")

                    # BONUS MECHANICS

                    if attacker.className == "Fighter":
                        if attacker._subType == 'Bruiser':
                            finalDamage = round(finalDamage * 1 + (0.05 * t.overwhelmStacks))
                            t.overwhelmStacks = min(10, t.overwhelmStacks + 1)

                    elif attacker.className == 'Wanderer':
                        if attacker._ascendancy == 'Mindbreaker':
                            if damageType == 'psychic':
                                t.tortureStacks += 1
                            if attacker.lostTrigger and random.random() <= (t.tortureStacks / 100):
                                finalDamage *= 2
                                exposure = Effects.createOtherworldExposure()
                                mechanics.append(exposure)

                    finalDamage, damageType = attacker.onAttack(finalDamage, damageType, targetUnit, self)
                    finalDamage, evaded = self.applyDamageWithDefenses(target, finalDamage, damageType, targetUnit)
                    finalDamage, damageType = t.onHit(finalDamage, damageType, isCrit, attacker, self)

                    if t.className == 'Ranger':
                        if t._subType == 'Sharpshooter' and evaded:
                            if t.tailwind < t.maxTailwind:
                                t.tailwind += 1
                        if t._subType == 'Scout' and not evaded:
                            t.scoutDodges = 0
                    
                    elif t.className == 'Cultist' and t._ascendancy == 'Harbinger':
                        if attacker.corruption > 0 and t.insanity < 0:
                            attacker.corruption -= 1
                            console.print(f"  [chaos]You were attacked while your Insanity is negative! {attacker._name} is cleansed of 1 Corruption.[/chaos]")

                    if attacker._stats['Bonuses']['lifesteal'] > 0:
                        heal = int(finalDamage * (attacker._stats['Bonuses']['lifesteal'] / 100))
                        attacker.heal(heal)

                    # MULTI-ATTACK CHECKS
                    damageDealt = False

                    if attacker.className == 'Rogue':
                        if attacker._ascendancy == 'Nightblade':
                            finalDamage = int(finalDamage * 0.75)
                            for _ in range(2):
                                t.damage(finalDamage, damageType)
                            damageDealt = True

                    elif attacker.className == 'Wanderer':
                        if attacker._subType == 'Vessel' and attacker.lostTrigger:
                            finalDamage = int(finalDamage * 0.8)
                            for _ in range(2):
                                if attacker._ascendancy == 'Weaver' and damageType != 'psychic':
                                    psyDam = int(finalDamage * 0.1)
                                    console.print(f"  [buff]- Weaver: 10% of Non-Psychic attack damage dealt as Extra Psychic! {psyDam} Extra Psychic damage dealt.[/buff]")
                                    t.damage(finalDamage, damageType)
                                    t.damage(psyDam, 'psychic')
                                    damageDealt = True
                                else:
                                    t.damage(finalDamage, damageType)
                                    damageDealt = True

                    elif attacker.className == 'Ranger':
                        if attacker._ascendancy == 'Tempest' and damageType == 'wind':
                            if random.random() < 0.4:
                                element = random.choice(['wind','earth','fire','cold','lightning'])
                                extraDamage = int(finalDamage * 0.5)
                                attacker.mysticism += 1
                                attacker._stats['Temporary']['increased_evasion'] += 2
                                attacker._stats['Temporary']['elemental'] += 1
                                t.damage(finalDamage, damageType)
                                t.damage(extraDamage, element)
                                damageDealt = True

                    if not damageDealt:
                        t.damage(finalDamage, damageType)

                    # AFTER-HIT EFFECTS

                    if attacker.className == 'Rogue':
                        if attacker._ascendancy == 'Shadow': # can only apply poison dots
                            for mechanic in mechanics:
                                if mechanic.effectType == 'dot' and mechanic.name in ['bleed', 'burn', 'curse']:
                                    mechanics.remove(mechanic)

                    if t.className == 'Rogue':
                        if t._subType == 'Duelist':
                            if random.random() <= 0.25:
                                riposteDamage = int(t._damage * 0.5)
                                attacker.damage(riposteDamage, t._damageType)
                                console.print(f"\n[buff]Duelist: {t._name} Riposted for {riposteDamage} damage against {attacker._name}[/buff]")
                                if t.primed:
                                    weaken = Effects.createWeaken()
                                    mechanics.append(weaken)

                    if mechanics and not t._isDead:
                        for mechanic in mechanics:
                            mechanic.apply(attacker, t, finalDamage, self)
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
                        
                        elif attacker.className == 'Spectre' and attacker._subType == 'Cursed':
                            allAlive = [u.entity for u in self.getUnitsInTeam('enemy')]
                            if len(allAlive) > 0:
                                aoeDamage = int(t._maxHealth * 0.1)
                                if t.cursedTurns > 0:
                                    aoeDamage += int(t._maxHealth * 0.25)
                                for e in allAlive:
                                    e.damage(aoeDamage, 'ethereal')
                                    e.cursedTurns = 5
                                console.print(f"  [ethereal]Cursed: Death spreads! {aoeDamage} damage and 5 turns of Cursed to all enemies![/ethereal]")

                        elif attacker.className == 'Cultist' and attacker._ascendancy == 'Harbinger':
                            if t.corruption >= 5:
                                allAlive = [u.entity for u in self.getUnitsInTeam('enemy')]
                                if len(allAlive) > 0:
                                    aoeDamage = int(t._maxHealth * 0.1)
                                    for e in allAlive:
                                        e.damage(aoeDamage, 'chaos')

                    if attacker.className == 'Spectre' and attacker._ascendancy == 'Reaper' and not death:
                        if t._health <= (t._maxHealth * 0.05):
                            console.print(f"  [gold1 bold]Reaper: EXECUTE![/gold1 bold]")
                            t.damage(t._health, 'true')
                            self.checkDead(t)
                            heal = int(t._maxHealth * 0.1)
                            dmgBuff = int(target._damage * 0.05)
                            attacker.heal(heal)
                            attacker.reaperDamage += dmgBuff
                            console.print(f"  [gold1]Reaper: Executed {t._name}! Healed for {heal} HP and gained {dmgBuff} Damage permanently.[/gold1]")

            ability.currentCooldown = ability.maxCooldown
            return True

    def enemyTurn(self, enemy: Entity, targets: List[Entity]):
        self.checkDead(enemy)
        if not targets or enemy._isDead:
            return
        
        aliveTargets = [t for t in targets if not t._isDead]
        if not aliveTargets:
            return

        target = random.choice(targets)

        availableAbilities = []
        for abilityName, ability in enemy._abilities.items():
            if ability.cooldown == 0:
                availableAbilities.append((abilityName, ability._rollWeight))

        if random.random() < 0.7 - (enemy._level / 200): # chance for basic attack decreases with level
            self.performAttack(enemy, target)
        elif availableAbilities:
            if isinstance(enemy, Boss):
                chosenAbility = enemy.chooseAbility(target)
            else:
                totalWeight = sum(weight for _, weight in availableAbilities)
                roll = random.randint(1, totalWeight)
                currentWeight = 0
                chosenAbility = None

                for abilityName, weight in availableAbilities:
                    currentWeight += weight
                    if roll <= currentWeight:
                        chosenAbility = abilityName
                        break

            if chosenAbility:
                self.performAttack(enemy, target, chosenAbility)
            else:
                self.performAttack(enemy, target)
        else: # no abilities
            self.performAttack(enemy, target)

    def _setPhaseForUnit(self, unit: CombatUnit):
        if unit.team == "player":
            self.currentPhase = TurnPhase.PLAYER_TURN
        elif unit.team == "enemy":
            self.currentPhase = TurnPhase.ENEMY_TURN

...