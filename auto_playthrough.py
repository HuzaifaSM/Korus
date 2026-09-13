"""
Fully automated playthrough: plays a real character from level 1 up to level 100, with death as a possibility.
Stores data upon death in tests/saves/ in json format

Run examples:
    py -3.14 auto_playthrough.py --target-class=Warrior
    py -3.14 auto_playthrough.py --target-class=Paladin --ascendancy=Zealot

runtime arugments:
--target-class=
--ascendancy=    
"""

import argparse
import json
import random
import time
from pathlib import Path
from typing import Optional, List
from rich.text import Text
from collections import deque

from scripts.styles import console
from scripts.combat import CombatManager
from scripts.enemies.enemy import createEnemy
from scripts.player_classes.classes import CLASSES, ASCENDANCIES, Player
from scripts.player_classes.fighter import Threshold
from scripts.items.equipment import ARMOUR_SLOTS, Equipment
from scripts.entities import SIGIL_SLOTS
from scripts.campAreas.campfire import Campfire
from scripts.campAreas.market import Market
from scripts.abilities import Ability, resolveEffects
from scripts.runeDrops import getRuneObject
from scripts.crafting.base import CraftingItem

TARGET_LEVEL = 100
ASCEND_AT_LEVEL = 20
MAX_TURNS_PER_FIGHT = 100
MAX_FIGHTS_PER_RUN = 10000 # safety ceiling to prevent infinite loop. very high to allow level 100 to be reached
MAX_FLEE_PER_RUN = 50000
MAX_FLEE_PER_LEVEL = 1000

SAVE_DIR = Path(__file__).parent / "tests" / "save"

# DECISION MAKING: uses simple heuristics

def _pickTarget(aliveEnemies):
    """focuses lowest health enemy"""
    return min(aliveEnemies, key=lambda e: e._health)

EFFECT_TURN_WEIGHT = 10

def _effectsValue(effectsDict: dict) -> float:
    if not effectsDict:
        return 0.0
    resolved = resolveEffects(effectsDict)
    return sum(EFFECT_TURN_WEIGHT * max(1, e.turns) for e in resolved)

def _healthCostFraction(ability: Ability, player: Player) -> float:
    """fraction of player's current health this ability would spend, 0 if no cost"""
    healthReq = ability.resources.get('required', {}).get('health')
    if healthReq is None:
        return 0.0
    if isinstance(healthReq, dict):
        pct = healthReq.get('amount', 0)
        pct = pct / 100 if pct >= 1 else pct
        costHp = pct * player._maxHealth
    else:
        costHp = healthReq
    return costHp / max(1, player._health)

HEALTH_COST_PENALTY_WEIGHT = 300

def _abilityPower(ability: Ability, numTargets: int = 1, player: Player = None) -> float:
    base = (ability.baseDamage or 0) + (ability.damageScaling or 0) * 100 + (ability.healBase or 0) + (ability.healPercent or 0) * 100
    base *= max(1, numTargets)
    base += _effectsValue(ability.effects.get('self', {}))
    base += _effectsValue(ability.effects.get('target', {}))
    if player is not None:
        costFrac = _healthCostFraction(ability, player)
        if costFrac > 0:
            base -= HEALTH_COST_PENALTY_WEIGHT * (costFrac ** 2)
    return base

def _pickAbility(player: Player, aliveEnemies: list) -> str:
    usable = [name for name, ab in player._abilities.items() if ab.canUse(player)[0]]
    if not usable:
        return 'Basic Attack'

    def _power(name: str) -> float:
        ability = player._abilities[name]
        if ability.targets == 'all':
            numTargets = max(1, len(aliveEnemies))
        elif ability.targets == 'multiple':
            numTargets = min(2, max(1, len(aliveEnemies)))
        else:
            numTargets = 1
        return _abilityPower(ability, numTargets, player)

    if player._health / player._maxHealth < 0.4:
        healers = [n for n in usable if player._abilities[n].healBase or player._abilities[n].healPercent]
        if healers:
            return max(healers, key=_power)

    offensive = [n for n in usable if n != 'Basic Attack']
    if offensive:
        return max(offensive, key=_power)
    return 'Basic Attack'

def _autarchPactChoice(player: Player) -> str:
    options = ['aggression', 'discipline']
    aggAllIn = player.currentAggressionTreshold == Threshold.ALL_IN
    discAllIn = player.currentDisciplineThreshold == Threshold.ALL_IN
    if player.currentAggressionTreshold == Threshold.DEDICATED or player.currentDisciplineThreshold == Threshold.DEDICATED:
        options.append('balance')
    if aggAllIn or discAllIn:
        options.append('purging')

    hpFraction = player._health / player._maxHealth
    if 'purging' in options and hpFraction > 0.6:
        desired = 'purging'

    elif 'balance' in options:
        desired = 'balance'
    else:
        desired = 'aggression' if player.aggression >= player.discipline else 'discipline'  # double whichever stance is currently stronger

    return str(options.index(desired) + 1)

def _decidePrompt(text: str, player: Player) -> str:
    hpFraction = player._health / player._maxHealth

    if "Spend Favour this turn" in text:
        return 'y'  # in-combat buffs beat banking Favour for a smaller heal at combat end

    if "skew your Insanity?" in text:
        return 'y'

    if "positively or negatively" in text:
        return '1' if hpFraction >= 0.5 else '2'  # healthy: lean offensive, hurt: lean defensive

    if "Sacrifice 5% HP to gain Elevated" in text:
        return 'y' if hpFraction > 0.5 else 'n'  # only spend HP we can actually spare

    if "Gain 20 Insanity" in text:  # Ritualist's post-sacrifice direction choice
        return '1' if hpFraction >= 0.5 else '2'

    if "into a skeleton" in text:
        return 'y'  # a free extra attacker with no cost to the player - always take it

    if "Choose a Pact" in text:
        return _autarchPactChoice(player)

    return ""

# COMBAT LOOP

def _equipNewestDrops(player: Player, enemies):
    for enemy in enemies:
        if not enemy._isDead:
            continue
        equipment: Equipment
        resources, equipmentPool, runes = enemy.dropLoot()
        for equipment, dropChance in equipmentPool:
            if random.random() <= dropChance:
                current = player._equipment.get(equipment.slot)
                if current is not None:
                    if equipment.slot == 'weapon':
                        if equipment.damage > current.damage:
                            player.equip(equipment)
                    elif equipment.slot in ARMOUR_SLOTS:
                        if equipment.defenseValue > current.defenseValue:
                            player.equip(equipment)
                    else:
                        if equipment.level > current.level:
                            player.equip(equipment)
                else:
                    player.equip(equipment)
        for resource, (minAmt, maxAmt, dropChance) in resources.items():
            minAmt = int(minAmt)
            maxAmt = int(maxAmt)
            if random.random() <= dropChance:
                amount = random.randint(minAmt, maxAmt)
                player.addItem(resource, amount)
        for cat, rType in runes:
            player.addRune(cat, rType)

def _runFightOrDie(player: Player, level: int, label: str, camp: Campfire) -> tuple[str, Optional[dict]]:
    """returns 'won', 'fled', 'died' or 'stalemate'"""
    enemies = [createEnemy(max(1, level), playerClassName=player.className, playerName=player._name)
               for _ in range(random.randint(min(3, 1 + (player._level) // 30), min(1 + player._level//16, 4)))
               ]
    cm = CombatManager()
    cm.startBattle(player, enemies)

    FLEE_DAMAGE_THRESHOLD = 0.2
    FLEE_HP_THRESHOLD = 0.3
    fled = False
    stalemate = False
    turns = 0
    outcome = None
    while cm.battleActive:
        turns += 1
        if turns >= MAX_TURNS_PER_FIGHT:
            cm.endBattle()
            stalemate = True
            break

        outcome = cm.checkBattleEnd()
        if outcome:
            break

        currentUnit = cm.getCurrentUnit()
        if not currentUnit:
            break

        if currentUnit.team == 'player':
            player.onTurnStart(cm)
            player._mythicDispatch('onTurnStart', cm)
            if player.hasLiveConditionalModifiers():
                player._recalculateStats(False, True)
            outcome = cm.checkBattleEnd()
            if outcome:
                break
            aliveEnemies = cm.allAlive
            if aliveEnemies:
                threat = sum(e._damage for e in aliveEnemies)

                def _inDanger():
                    hpFraction = player._health / player._maxHealth
                    return threat > player._maxHealth * FLEE_DAMAGE_THRESHOLD or hpFraction < FLEE_HP_THRESHOLD

                if _inDanger() and player.consumable.useable and player.consumable.healPercent * player._maxHealth > threat:
                    player.useConsumable()

                if _inDanger(): # still going to die after consumable, flee
                    cm.endBattle()
                    player.onCombatEnd()
                    player._mythicDispatch('onCombatEnd')
                    fled = True
                    break

                target = _pickTarget(aliveEnemies)
                cm.performAttack(player, target, _pickAbility(player, aliveEnemies))
        else:
            cm.enemyTurn(currentUnit.entity, [player])

        outcome = cm.checkBattleEnd()
        if outcome:
            break
        cm.nextTurn()

    fightData = {'enemies': _summariseEnemies(enemies), 'combatLog': cm.combatLog}

    if stalemate:
        player.onCombatEnd()
        player._mythicDispatch('onCombatEnd')
        return 'stalemate', fightData

    if fled:
        return 'fled', fightData

    player.onCombatEnd()
    player._mythicDispatch('onCombatEnd')

    if outcome == 'enemy':
        return 'died', fightData

    _equipNewestDrops(player, enemies)
    totalXp = 0
    totalGold = 0
    for enemy in enemies:
        if enemy._isDead:
            xp = enemy.getExperienceReward()
            gold = enemy.getGoldReward()
            xpBonus = player._stats['Bonuses']['xp_gain']
            if xpBonus > 0:
                effectiveBonus = xpBonus / (1.5 + (xpBonus / 100))
                xp += round(xp * (effectiveBonus / 100))
            totalXp += xp

            goldBonus = player._stats['Bonuses']['gold_gain']
            if goldBonus > 0:
                gold += round(gold * (goldBonus / 100))
            totalGold += gold

    player.gainExperience(totalXp)
    player.gainGold(totalGold)

    if camp.level > 0:
        camp.supplies += random.randint(2, 5 + camp.level)

    return 'won', fightData

def _visitMarket(player: Player, market: Market):
    market._generateStock()

    for itemName, itemData in list(market.stock.items()):
        if len(itemData) != 3:
            continue  # resource or rune stock, not equipment
        quantity, price, equipment = itemData
        if player._gold < price:
            continue

        current = player._equipment.get(equipment.slot)
        if current is None:
            isUpgrade = True
        elif equipment.slot == 'weapon':
            isUpgrade = equipment.damage > current.damage
        elif equipment.slot in ARMOUR_SLOTS:
            isUpgrade = equipment.defenseValue > current.defenseValue
        else:
            isUpgrade = equipment.level > current.level

        if not isUpgrade:
            continue

        player._gold -= price
        player.equip(equipment)
        if current is not None:
            player.addEquipmentToStorage(current)
        del market.stock[itemName]

def _attemptRuneApplications(player: Player):
    for eq in player._equipment.values():
        if eq is None:
            continue
        runeInventory = list(player._craftingInventory.keys())
        if not runeInventory:
            return

        runes: list[CraftingItem] = [getRuneObject(*runeData.split('_', 1)) for runeData in runeInventory]
        runes = [r for r in runes if r is not None]
        growth = [r for r in runes if "growth" in r.name]
        mastery =[r for r in runes if "mastery" in r.name]
        fusion = [r for r in runes if "fusion" in r.name]
        destabilisation = [r for r in runes if "destabilisation" in r.name]
        chosenRune: CraftingItem = None
        chosen: list[CraftingItem] = []

        if not eq.craftable:
            continue
        if eq.allSlotsFilled and eq.mastery < eq.maxMastery and mastery:
            chosen = sorted(mastery, key=lambda m: m.masteryToAdd, reverse=True)

        if not eq.allSlotsFilled and growth:
            chosen = sorted(growth, key=lambda g: g.minItemLevel, reverse=True)

        if not eq.allSlotsEmpty and not eq.allSlotsFilled and fusion:
            chosen = sorted(fusion, key=lambda f: f.minItemLevel, reverse=True)

        if not chosen:
            chosen = sorted(destabilisation, key=lambda d: d.minItemLevel, reverse=True)

        if chosen:
            chosen = [r for r in chosen if r.minItemLevel <= eq.level]
            if chosen:
                chosenRune = chosen[0] # picks highest item level since higher item level = better
                chosenRune.apply(eq, player)

def _getTotalResistanceValue(equipment: Equipment) -> int:
    if equipment.slot == 'weapon':
        return 0
    total = 0
    for a in equipment.prefixes + equipment.suffixes:
        if 'resistance' in a.categories or 'resistance' in a.stat:
            total += a.value * (2 if 'max' in a.stat else 1) # max resistances count as 2x resistance value
    return total

def _ensureEquipment(player: Player):
    for slot, eq in player._equipment.items():
        # stored sigils are all generically tagged .slot == 'sigil', never 'sigil_2'/'sigil_3'/etc,
        # so a plain e.slot == slot check can never match a numbered sigil slot
        isSigilSlot = slot in SIGIL_SLOTS
        valid = [e for e in player._equipmentStorage if e.slot == slot or (isSigilSlot and e.slot == 'sigil')]
        # equip() only auto-stores the item being *displaced*, not the one being pulled in -
        # anything sourced from storage here must be removed manually or it stays "in stock"
        # and can get equipped again into the next matching empty/upgradeable slot this same pass
        # (this bites sigils specifically, since all 5 numbered slots share one generic storage pool)
        def _takeFromStorage(item):
            player._equipmentStorage.remove(item)
            player.equip(item, slot=slot)

        if eq is None:
            if valid:
                new = sorted(valid, key=lambda e: e.level, reverse=True)[0]
                _takeFromStorage(new)
        else:
            if slot == 'weapon':
                if valid:
                    potential = sorted(valid, key=lambda e: e.damage, reverse=True)[0]
                    if potential.damage > eq.damage and potential.rarity - 1 >= eq.rarity:
                        _takeFromStorage(potential)
            elif slot in ARMOUR_SLOTS:
                if valid:
                    potential = sorted(valid, key=lambda e: e.defenseValue, reverse=True)[0:3]
                    weights = []
                    for e in potential:
                        weights.append(1 if e.defenseType != 'energy_shield' else 2)
                    potential = random.choices(potential, weights, k=1)[0]
                    bias = potential.defenseValue // 5 if potential.defenseType == 'energy_shield' else 0
                    currentResVal = _getTotalResistanceValue(eq)
                    newResVal = _getTotalResistanceValue(potential)
                    if (potential.defenseValue + bias > eq.defenseValue or newResVal - 10 >= currentResVal) and potential.rarity - 1 >= eq.rarity:
                        _takeFromStorage(potential)
            else:
                if valid:
                    potential = sorted(valid, key=lambda e: e.level, reverse=True)[0]
                    currentResVal = _getTotalResistanceValue(eq)
                    newResVal = _getTotalResistanceValue(potential)
                    if potential.level > eq.level or newResVal - 10 >= currentResVal or (potential.level > eq.level - 10 and potential.rarity - 1 >= eq.rarity):
                        _takeFromStorage(potential)

def _summariseEnemies(enemies) -> list:
    return [{
        'name': e._name,
        'level': e._level,
        'rarity': e.rarity.value,
        'maxHealth': e._maxHealth,
        'damage': e._damage,
        'damageType': e._damageType,
        'critChance': round(e.critChance, 3),
        'critMulti': round(e.critMulti, 3),
        'abilities': list(e._abilities.keys()),
    } for e in enemies]

def _climbOrDie(player: Player, targetLevel: int, label: str, fightLog: list, realPrint, recentCombats: deque) -> tuple[str, int]:
    """returns 'reached_target', 'died', or 'stalled' and number of fled combats"""
    fights = 0
    flee = 0
    fleeFromLastLevelUp = 0
    camp = Campfire(player)
    market = Market(player)
    while player._level < targetLevel:
        if camp.level > 0 and camp.supplies > 0 and player._health < player._maxHealth:
            camp.rest()

        fights += 1
        if fights > MAX_FIGHTS_PER_RUN:
            return 'stalled', flee

        levelBefore = player._level
        hpBefore = player._health
        result, fightData = _runFightOrDie(player, player._level, label, camp)
        recentCombats.append({'fight': fights, 'result': result, **fightData})
        logEntry = {
            'fight': len(fightLog) + 1,
            'level': player._level,
            'hpBefore': hpBefore,
            'hpAfter': player._health,
            'maxHp': player._maxHealth,
            'result': result,            
        }
        if result == 'died':
            logEntry['killedBy'] = fightData
        elif result == 'stalemate':
            logEntry['stalemateData'] = fightData
        fightLog.append(logEntry)

        if result == 'died':
            realPrint(f"[bold red]{label}: died at level {player._level}, fight {fights}[/bold red]")
            return 'died', flee
        elif result == 'stalemate':
            realPrint(f"[bold red]{label}: a fight stalemated (exceeded {MAX_TURNS_PER_FIGHT} turns) at level {player._level}, fight {fights}[/bold red]")
            return 'stalemate', flee
        elif result == 'fled':
            realPrint(f"[yellow]{label}: fled a dangerous fight at level {player._level} (fight {fights})[/yellow]")
            fights -= 1
            flee += 1
            fleeFromLastLevelUp += 1
            player._health = min(player._maxHealth, hpBefore) # fleeing counts fight as never happened
            if flee > MAX_FLEE_PER_RUN:
                return 'stalled', flee
            if fleeFromLastLevelUp > MAX_FLEE_PER_LEVEL:
                return 'stalled', flee
        else:
            realPrint(f"[bold green]{label}: Won fight {fights}[/bold green]")

        if player._level > levelBefore:
            realPrint(f"[dim]{label}: level {player._level} (fight {fights}), HP {player._health}/{player._maxHealth}")
            fleeFromLastLevelUp = 0

        if camp.level < 5: # try to upgrade campfire every level since it's useful for survivability
            camp.upgrade()

        if fights > 0 and fights % 25 == 0:
            _ensureEquipment(player)
            realPrint(f"[dim]{label}: refreshed all worn equipment[/dim]")

        if fights > 0 and fights % 50 == 0:
            if market.level < 5:
                market.upgrade()
            _visitMarket(player, market)
            _attemptRuneApplications(player)
            realPrint(f"[dim]{label}: Used their runes and visited the market at fight {fights} (gold: {player._gold})[/dim]")

    return 'reached_target', flee

def _writeRunReport(player: Player, className: str, ascendancy: str, outcome: str, fightLog: list, fledCombats: int, recentCombats: deque) -> Path:
    SAVE_DIR.mkdir(parents=True, exist_ok=True)
    stamp = time.strftime("%Y%m%d_%H%M%S")
    path = SAVE_DIR / f"{className}_{ascendancy or 'base'}_{stamp}.json"

    report = {
        'class': className,
        'ascendancy': ascendancy,
        'outcome': outcome,
        'finalLevel': player._level,
        'fightsSurvived': len(fightLog),
        'fightsFled': fledCombats,
        'fightLog': fightLog,
        'recentCombats': recentCombats,
        'finalState': player.serialise(),
    }
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(report, f, indent=2, default=str)
    return path

# ---------------------------------------

def run(className: str, ascendancy: str = None):
    if className not in CLASSES:
        raise SystemExit(f"Unknown class {className!r}. Valid: {', '.join(CLASSES)}")
    if ascendancy and ascendancy not in ASCENDANCIES.get(className, []):
        valid = ', '.join(ASCENDANCIES.get(className, []) or '(none)')
        raise SystemExit(f"{ascendancy!r} is not a valid ascendancy for {className}. Valid: {valid}")

    console.input = lambda *a, **k: ""
    realPrint = console.print
    console.print = lambda *a, **k: None

    player: Player = CLASSES[className](f"{className} Auto-Playthrough {ascendancy or 'base'}")
    label = f"{className}/{ascendancy or 'base'}"
    fightLog = []

    recentPrints: List[str] = []

    def _trackingPrint(*args, **kwargs):
        for arg in args:
            if isinstance(arg, str):
                recentPrints.append(arg)

    def _smartInput(*args, **kwargs) -> str:
        promptArg = args[0] if args else ""
        context = " ".join(recentPrints) + " " + str(promptArg)
        recentPrints.clear()
        plain = Text.from_markup(context).plain
        return _decidePrompt(plain, player)

    console.print = _trackingPrint
    console.input = _smartInput

    realPrint(f"[bold cyan]Starting {label} - target level {TARGET_LEVEL}[/bold cyan]")

    recentCombats = deque(maxlen=5)
    firstPhaseTarget = ASCEND_AT_LEVEL if ascendancy else TARGET_LEVEL
    fledCombats = 0
    outcome, numFled = _climbOrDie(player, firstPhaseTarget, label, fightLog, realPrint, recentCombats)
    fledCombats += numFled

    if outcome == 'reached_target' and ascendancy:
        if player.updateAscendancy(ascendancy):
            player._health = min(player._health, player._maxHealth)  # ascending can shift maxHealth
            realPrint(f"[bold gold1]{label}: ascended into {ascendancy} at level {player._level}[/bold gold1]")
            outcome, numFled = _climbOrDie(player, TARGET_LEVEL, label, fightLog, realPrint, recentCombats)
            fledCombats += numFled
        else:
            outcome = 'ascend_failed'
            realPrint(f"[bold red]{label}: failed to ascend into {ascendancy}[/bold red]")

    console.print = realPrint

    path = _writeRunReport(player, className, ascendancy, outcome, fightLog, fledCombats, list(recentCombats))

    realPrint(f"\n[bold gold1]{'=' * 60}[/bold gold1]")
    realPrint(f"[bold gold1]{label}: {outcome}[/bold gold1]")
    realPrint(f"  Final level: {player._level} / {TARGET_LEVEL}")
    realPrint(f"  Fights survived: {len(fightLog)}")
    realPrint(f"  Final HP: {player._health} / {player._maxHealth}")
    realPrint(f"  Report saved to: {path}")
    realPrint(f"[bold gold1]{'=' * 60}[/bold gold1]\n")

    return outcome, path

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--target-class", default="Warrior", help="Class to player (default: Warrior)")
    parser.add_argument("--ascendancy", default=None, help="Ascendancy to take at level 20 (optional)")
    args = parser.parse_args()

    run(args.target_class, args.ascendancy)

...