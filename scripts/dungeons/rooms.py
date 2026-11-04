import random
from typing import Dict

from ..styles import (
    console, clearScreen, printHeader, printSeparator, pause,
    printWarning, printSuccess, printError, printInfo
)
from ..enemies.enemy import createEnemy, rollEncounterClasses, EnemyRarity
from ..items.equipment import Equipment, EQUIPMENT_SLOTS
from ..items.items import rollRarity, RESOURCES, ItemRarity
from .modifiers import applyEnemyModifiers
from .bosses import createBossEncounter

def combatRoom(game, dungeonMap, currentFloor: int, effects: Dict, elite: bool = False):
    player = game.player
    clearScreen()
    printHeader("Elite Encounter" if elite else "Combat Encounter")

    numEnemies = random.randint(2, 3 + dungeonMap.tier // 2) + int(effects.get('extra_enemies', 0))
    difficulty = dungeonMap.getDifficultyMultiplier() * (1.3 if elite else 1.0)
    rarityBonus = effects.get('item_rarity', 0) / 100
    quantityBonus = effects.get('item_quantity', 0) / 100
    enemyLevel = dungeonMap.level + int(effects.get('enemy_level', 0))

    enemies = []
    for enemyClass in rollEncounterClasses(numEnemies):
        enemy = createEnemy(enemyLevel, difficulty, rarityBonus, quantityBonus, player.className, player._name,
                             enemyClass=enemyClass, groupSize=numEnemies, playerLevel=player._level,
                             forcedRarity=EnemyRarity.EPIC if elite else None)
        applyEnemyModifiers(enemy, effects, currentFloor)
        enemy._health = enemy._maxHealth
        enemies.append(enemy)

    game.startCombat(enemies, affectsOverworldProgression=False)

def bossRoom(game, dungeonMap, currentFloor: int, effects: Dict):
    player = game.player
    clearScreen()
    printHeader("Boss Encounter")

    difficulty = dungeonMap.getDifficultyMultiplier() * 1.4
    rarityBonus = effects.get('item_rarity', 0) / 100
    quantityBonus = effects.get('item_quantity', 0) / 100
    enemyLevel = dungeonMap.level + int(effects.get('enemy_level', 0))

    enemies, template = createBossEncounter(enemyLevel, dungeonMap.tier, difficulty, rarityBonus, quantityBonus,
                                             player.className, player._name, effects, currentFloor)

    console.print(f"[bold gold1]{template['name']}[/bold gold1]")
    console.print(f"[dim]{template['title']}[/dim]")
    if len(enemies) > 1:
        console.print(f"[warning]...accompanied by {len(enemies) - 1} lesser threat(s).[/warning]")
    pause()

    game.startCombat(enemies, affectsOverworldProgression=False)

    for dropSpec in effects.get('guaranteed_drops', []):
        minRarity = {'common': 1, 'uncommon': 2, 'rare': 3, 'epic': 4, 'legendary': 5}.get(dropSpec.get('minRarity', 'legendary'), 5)
        for _ in range(dropSpec.get('count', 1)):
            rolledRarity = rollRarity(dungeonMap.level, dungeonMap.getRewardMultiplier())
            if rolledRarity.num < minRarity:
                rolledRarity = ItemRarity.numToRarity(minRarity)
            equipment = Equipment._generateEquipmentPiece(dungeonMap.level, 'any', rolledRarity, player.className, player._name)
            console.print(f"\n[cyan bold]=== Guaranteed Drop ===[/cyan bold]")
            console.print(equipment)
            if not player.equip(equipment):
                player.addEquipmentToStorage(equipment)
    if effects.get('guaranteed_drops'):
        pause()

def restRoom(game, dungeonMap, effects: Dict):
    player = game.player
    clearScreen()
    printHeader("Rest Site")

    multiplier = max(0.0, 1 + effects.get('rest_heal_multiplier', 0))
    healPercent = 0.4 * multiplier
    healAmount = round(player._maxHealth * healPercent)

    if healAmount > 0:
        console.print("[green]A quiet spot, safe enough to catch your breath.[/green]")
        player.heal(healAmount, reason="dungeon rest site")
    else:
        printWarning("This rest site has been drained of whatever once made it safe. It does nothing.")
    player._stamina = player._maxStamina
    pause()

def merchantRoom(game, dungeonMap):
    player = game.player
    stock = []
    for _ in range(random.randint(3, 4)):
        itemRarity = rollRarity(dungeonMap.level, dungeonMap.getRewardMultiplier())
        slot = random.choice(EQUIPMENT_SLOTS)
        equipment = Equipment._generateEquipmentPiece(dungeonMap.level, slot, itemRarity, player.className, player._name)
        price = int(equipment.value * random.uniform(2.5, 3.5))
        stock.append([equipment, price])

    while stock:
        clearScreen()
        printHeader("Dungeon Merchant")
        console.print(f"[gold1]Your Gold:[/gold1] {player._gold}")
        printSeparator()
        for i, (equipment, price) in enumerate(stock, 1):
            console.print(f"[dim]{i}.[/dim] {equipment.name} - [gold1]{price} Gold[/gold1]")
            console.print(equipment)
        console.print("[dim]0.[/dim] Leave")

        choice = console.input("\n[cyan]>[/cyan] ").strip()
        try:
            choice = int(choice)
        except ValueError:
            printError("Invalid input!")
            pause()
            continue

        if choice == 0:
            return
        index = choice - 1
        if not (0 <= index < len(stock)):
            printError("Invalid choice!")
            pause()
            continue

        equipment, price = stock[index]
        if player._gold < price:
            printWarning("Not enough gold!")
            pause()
            continue

        player._gold -= price
        if not player.equip(equipment):
            player.addEquipmentToStorage(equipment)
        printSuccess(f"Purchased {equipment.name}!")
        stock.pop(index)
        pause()

def treasureRoom(game, dungeonMap, effects: Dict):
    player = game.player
    clearScreen()
    printHeader("Treasure Room")

    rarityBonus = effects.get('item_rarity', 0) / 100
    quantityBonus = effects.get('item_quantity', 0) / 100

    gold = round(random.randint(40, 90) * dungeonMap.getRewardMultiplier() * (1 + rarityBonus))
    player.gainGold(gold)

    for _ in range(random.randint(2, 3)):
        resource = random.choice(list(RESOURCES.keys()))
        amount = round(random.randint(4, 12) * dungeonMap.getRewardMultiplier() * (1 + quantityBonus))
        player.addItem(resource, amount)

    if random.random() < 0.6:
        itemRarity = rollRarity(dungeonMap.level, dungeonMap.getRewardMultiplier() * (1 + rarityBonus))
        equipment = Equipment._generateEquipmentPiece(dungeonMap.level, 'any', itemRarity, player.className, player._name)
        console.print(equipment)
        if not player.equip(equipment):
            player.addEquipmentToStorage(equipment)

    pause()

def _eventShrine(game, dungeonMap, effects, currentFloor):
    player = game.player
    console.print("[magenta]A cracked shrine hums with leftover magic.[/magenta]")
    console.print("[dim]1.[/dim] Offer 10% of your current HP for a burst of gold and resources")
    console.print("[dim]2.[/dim] Leave it alone")
    choice = console.input("\n[cyan]>[/cyan] ").strip()
    if choice == '1':
        cost = max(1, round(player._health * 0.1))
        player._health -= cost
        gold = random.randint(30, 80)
        player.gainGold(gold)
        printSuccess(f"You feel lighter - {cost} HP drained, {gold} gold gained.")
    else:
        printInfo("You leave the shrine undisturbed.")

def _eventCache(game, dungeonMap, effects, currentFloor):
    player = game.player
    console.print("[cyan]A hidden cache, wedged behind a collapsed wall.[/cyan]")
    resource = random.choice(list(RESOURCES.keys()))
    amount = random.randint(5, 15)
    player.addItem(resource, amount)
    printSuccess(f"Found {amount}x {resource.replace('_', ' ').title()}!")

def _eventTrial(game, dungeonMap, effects, currentFloor):
    console.print("[yellow]An old trial marker, etched with a challenge.[/yellow]")
    console.print("[dim]1.[/dim] Accept - a tougher fight, for better rewards")
    console.print("[dim]2.[/dim] Walk away")
    choice = console.input("\n[cyan]>[/cyan] ").strip()
    if choice == '1':
        combatRoom(game, dungeonMap, currentFloor, effects, elite=True)
    else:
        printInfo("You walk away from the marker.")

EVENTS = [_eventShrine, _eventCache, _eventTrial]

def eventRoom(game, dungeonMap, currentFloor: int, effects: Dict):
    clearScreen()
    printHeader("???")
    random.choice(EVENTS)(game, dungeonMap, effects, currentFloor)
    pause()
