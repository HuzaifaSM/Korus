"""
Ad-hoc balance tool (not a pytest test): runs a full level 1 -> 20 playthrough for every
non-Druid class using the real combat engine (same approach as
tests/_playthroughLib.py's leveling smoke tests), except here the player actually keeps its
real base stats instead of being made immortal via an inflated baseHealth. Survival is instead
handled by temporarily inflating baseHealth only *during* each fight's turns, then restoring the
real value immediately afterward - before XP/level-ups and loot are applied - so the final
reported stats (health, damage, defenses, equipped gear) reflect genuine level-20 progression.

Equipment handling: whenever a dead enemy's loot table rolls an equipment drop, the newest piece
is always equipped immediately; whatever was previously in that slot (if anything) is moved to
equipment storage instead of being discarded, mirroring the real game's addEquipmentToStorage flow.

Run: python equipment_leveling_report.py
"""
import random

from scripts.styles import console
from scripts.combat import CombatManager
from scripts.enemies.enemy import createEnemy
from scripts.player_classes.classes import CLASSES

TARGET_LEVEL = 20
MAX_TURNS_PER_FIGHT = 200
MAX_FIGHTS_PER_RUN = 500
SURVIVAL_HEALTH = 10_000_000_000

ARMOUR_SLOTS_ORDER = ['weapon', 'head', 'chest', 'legs', 'feet', 'ring', 'amulet']

def _setSurvivalMode(player, on: bool):
    """Inflates baseHealth to survive a fight's turns (on=True), or restores the real value
    the player actually earned via leveling (on=False) - call the latter before granting XP/
    looting so those operations act on genuine stats."""
    if on:
        player._trueBaseHealth = player._baseHealth
        player._baseHealth = SURVIVAL_HEALTH
    else:
        player._baseHealth = player._trueBaseHealth
    player._recalculateStats(False)
    player._health = player._maxHealth


def _pickAbility(player) -> str:
    names = list(player._abilities.keys())
    random.shuffle(names)
    for name in names:
        canUse, _ = player._abilities[name].canUse(player)
        if canUse:
            return name
    return 'Basic Attack'


def _equipNewestDrops(player, enemies):
    for enemy in enemies:
        if not enemy._isDead:
            continue
        resources, equipmentPool, runes = enemy.dropLoot()
        for equipment, dropChance in equipmentPool:
            if random.random() <= dropChance:
                current = player._equipment.get(equipment.slot)
                player.equip(equipment, False)
                if current is not None:
                    player.addEquipmentToStorage(current)


def _runFight(player, level: int, label: str):
    enemies = [createEnemy(max(1, level)) for _ in range(random.randint(1, 2))]
    cm = CombatManager()
    cm.startBattle(player, enemies)

    turns = 0
    while cm.battleActive:
        turns += 1
        assert turns < MAX_TURNS_PER_FIGHT, f"{label}: a fight exceeded {MAX_TURNS_PER_FIGHT} turns"

        if cm.checkBattleEnd():
            break

        currentUnit = cm.getCurrentUnit()
        if not currentUnit:
            break

        if currentUnit.team == 'player':
            player.onTurnStart(cm)
            if cm.checkBattleEnd():
                break
            aliveEnemies = [e for e in enemies if not e._isDead]
            if aliveEnemies:
                target = random.choice(aliveEnemies)
                cm.performAttack(player, target, _pickAbility(player))
        else:
            cm.enemyTurn(currentUnit.entity, [player])

        if cm.checkBattleEnd():
            break
        cm.nextTurn()

    player.onCombatEnd()

    # back to real stats before XP/leveling/loot get applied
    _setSurvivalMode(player, False)

    _equipNewestDrops(player, enemies)

    for enemy in enemies:
        if enemy._isDead:
            player.gainExperience(enemy.getExperienceReward())

    # re-inflate for the next fight's turns
    _setSurvivalMode(player, True)


def _levelPlayerTo(player, targetLevel: int, label: str):
    fights = 0
    while player._level < targetLevel:
        fights += 1
        assert fights < MAX_FIGHTS_PER_RUN, f"{label}: exceeded {MAX_FIGHTS_PER_RUN} fights"
        _runFight(player, player._level, label)
    return fights


def _describeEquipment(equipment) -> str:
    if equipment is None:
        return "[dim]Empty[/dim]"
    bits = [equipment.name, f"[dim](Lv.{equipment.level})[/dim]"]
    if equipment.slot == 'weapon' and equipment.damage:
        typeStr = f" {equipment.damageType}" if equipment.damageType else ""
        bits.append(f"[dim]-{typeStr} {equipment.damage} dmg[/dim]")
    elif equipment.defenseType and equipment.defenseValue:
        bits.append(f"[dim]- {equipment.defenseValue} {equipment.defenseType}[/dim]")
    return " ".join(bits)


def run():
    console.input = lambda *a, **k: ""
    realPrint = console.print
    console.print = lambda *a, **k: None

    results = []
    for className, playerClass in CLASSES.items():
        realPrint(f"[bold cyan]Leveling {className} to {TARGET_LEVEL}...[/bold cyan]")
        player = playerClass(f"{className} Playthrough")
        _setSurvivalMode(player, True)
        label = f"{className}/base"

        fights = _levelPlayerTo(player, TARGET_LEVEL, label)

        # final measurement: real stats, no survival inflation
        _setSurvivalMode(player, False)

        results.append({
            'class': className,
            'fights': fights,
            'level': player._level,
            'maxHealth': player._maxHealth,
            'damage': player._damage,
            'damageType': player._damageType,
            'speed': round(player._speed, 3),
            'critChance': round(player.critChance, 3),
            'critMulti': round(player.critMulti, 3),
            'armour': player.armour,
            'evasion': player.evasion,
            'energyShield': player.energyShield,
            'maxEnergyShield': player.maxEnergyShield,
            'maxStamina': player._maxStamina,
            'equipment': dict(player._equipment),
            'storageCount': len(player._equipmentStorage),
        })
        realPrint(f"[green]  done - {fights} fights, level {player._level}[/green]")

    console.print = realPrint

    console.print("\n[bold gold1]" + "=" * 70 + "[/bold gold1]")
    console.print(f"[bold gold1]LEVEL {TARGET_LEVEL} STATS WITH EQUIPMENT (auto-equip newest drop per slot)[/bold gold1]")
    console.print("[bold gold1]" + "=" * 70 + "[/bold gold1]\n")

    for r in results:
        console.print(f"[bold underline]{r['class']}[/bold underline] [dim](reached level {r['level']} in {r['fights']} fights)[/dim]")
        console.print(f"  [health]Max Health:[/health] {r['maxHealth']}")
        console.print(f"  [damage]Damage:[/damage] {r['damage']} [dim]({r['damageType']})[/dim] | [speed]Speed:[/speed] {r['speed']}")
        console.print(f"  Crit Chance: {r['critChance']*100:.1f}% | Crit Multi: {r['critMulti']*100:.0f}%")
        console.print(f"  Armour: {r['armour']} | Evasion: {r['evasion']} | Energy Shield: {r['energyShield']}/{r['maxEnergyShield']}")
        console.print(f"  Max Stamina: {r['maxStamina']}")
        console.print("  [bold]Equipment:[/bold]")
        for slot in ARMOUR_SLOTS_ORDER:
            console.print(f"    {slot.title()}: {_describeEquipment(r['equipment'].get(slot))}")
        console.print(f"  [dim]Equipment Storage: {r['storageCount']} unequipped pieces[/dim]\n")

    return results


if __name__ == "__main__":
    run()
