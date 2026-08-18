from .items import Equipment, RESOURCES, CONSUMABLES, ItemRarity
from .abilities import CLASS_ABILITIES
from crafting.base import CraftingItem
from crafting.chaosRune import CHAOS_RUNES
from crafting.erasingRune import ERASING_RUNES
from crafting.growthRune import GROWTH_RUNES
from crafting.randomiserRunes import RANDOMISER_RUNES
from crafting.uniqueRunes import UNIQUE_RUNES
from crafting.masteryRune import MASTERY_RUNES
from crafting.rarityRune import RARITY_RUNES
from crafting.destabilisationRune import DESTABILISATION_RUNES
from crafting.revealingRune import REVEALING_RUNES
from crafting.manipulationRune import MANIPULATION_RUNES
from scripts.runeDrops import getRuneObject
from .styles import (
    console, clearScreen, pause, printHeader, printSeparator,
    printSuccess, printWarning, printError, formatRarity
)
from typing import Dict

def getAllRunes() -> Dict[str, str]: # make get runes/crafting debug: 100 of each rune
    """Get all available runes"""
    allRunes = {}
    allRunes.update({f"chaos_{k}": v for k, v in CHAOS_RUNES.items()})
    allRunes.update({f"erasing_{k}": v for k, v in ERASING_RUNES.items()})
    allRunes.update({f"growth_{k}": v for k, v in GROWTH_RUNES.items()})
    allRunes.update({f"randomiser_{k}": v for k, v in RANDOMISER_RUNES.items()})
    allRunes.update({f"unique_{k}": v for k, v in UNIQUE_RUNES.items()})
    allRunes.update({f"mastery_{k}": v for k, v in MASTERY_RUNES.items()})
    allRunes.update({f"rarity_{k}": v for k, v in RARITY_RUNES.items()})
    allRunes.update({f"destabilisation_{k}": v for k, v in DESTABILISATION_RUNES.items()})
    allRunes.update({f"revealing_{k}": v for k, v in REVEALING_RUNES.items()})
    allRunes.update({f"manipulation_{k}": v for k, v in MANIPULATION_RUNES.items()})
    return allRunes

COMMANDS = {
    "give_item", "remove_item", "give_equipment", 'eq', "give_consumable", "consumable", "give_xp", "xp", "give_gold", "gold",
    "restock", "area", "area_level", "heal", 'runes', 'give_runes', 'crafting', 'lvl', 'level', 'recalc', 'stats'
}

SLOTS = {
    1: "weapon", 2: "head", 3: "chest", 4: "legs", 5: "feet", 6: "ring", 7: "amulet"
}

RARITIES = {
    1: ItemRarity.COMMON, 2: ItemRarity.UNCOMMON, 3: ItemRarity.RARE, 4: ItemRarity.EPIC, 5: ItemRarity.LEGENDARY
}

class Debugger:
    def __init__(self, game):
        self.game = game

    def giveItem(self):
        while True:
            clearScreen()
            printHeader("Give Item - Debug")
            console.print("[dim]0.[/dim] Exit")
            console.print("[dim]1.[/dim] View Item Names")
            console.print("\n[cyan]Otherwise type item to give[/cyan]")
            choice = console.input("> ").strip().lower()
            if choice == "0":
                break
            elif choice == "1":
                console.print("\n[bold cyan]=== Available Resources ===[/bold cyan]")
                for i, resource in enumerate(RESOURCES.keys(), 1):
                    console.print(f"  [dim]{i}.[/dim] {resource}")
                pause()
            else:
                if choice in list(RESOURCES.keys()):
                    amount = console.input("[cyan]How much?[/cyan]\n> ").strip()
                    try:
                        amount = int(amount)
                        if amount > 0:
                            self.game.player.addItem(choice, amount)
                            printSuccess(f"Gave {amount}x {choice}")
                            pause()
                            break
                    except ValueError:
                        printError("Invalid amount!")
                        pause()
                else:
                    printWarning(f"Unknown item: {choice}")
                    pause()

    def removeItem(self):
        while True:
            clearScreen()
            printHeader("Remove Item - Debug")
            console.print("[dim]0.[/dim] Exit")
            console.print("[dim]1.[/dim] View Item Names")
            console.print("\n[cyan]Otherwise type item to remove[/cyan]")
            choice = console.input("> ").strip().lower()
            if choice == "0":
                break
            elif choice == "1":
                console.print("\n[bold cyan]=== Available Resources ===[/bold cyan]")
                for i, resource in enumerate(RESOURCES.keys(), 1):
                    console.print(f"  [dim]{i}.[/dim] {resource}")
                pause()
            else:
                if choice in list(RESOURCES.keys()):
                    if choice not in self.game.player._inventory:
                        printWarning(f"You don't have any {choice}")
                        pause()
                        continue
                    currentAmount = self.game.player._inventory[choice]
                    console.print(f"[cyan]Current amount:[/cyan] {currentAmount}")
                    amount = console.input("[cyan]How much? (type 'all' to remove all)[/cyan]\n> ").strip()
                    if amount.lower() == "all":
                        self.game.player.removeItem(choice, currentAmount)
                        printSuccess(f"Removed all {choice}")
                        pause()
                        break
                    try:
                        amount = int(amount)
                        if amount <= currentAmount:
                            self.game.player.removeItem(choice, amount)
                            printSuccess(f"Removed {amount}x {choice}")
                        else:
                            self.game.player.removeItem(choice, currentAmount)
                            printWarning(f"Only had {currentAmount}, removed all")
                        pause()
                        break
                    except ValueError:
                        printError("Invalid amount!")
                        pause()
                else:
                    printWarning(f"Unknown item: {choice}")
                    pause()

    def giveEquipment(self):
        def _chooseSlot() -> str:
            console.print("\n[bold cyan]=== Choose Slot ===[/bold cyan]")
            for i, slot in SLOTS.items():
                console.print(f"  [cyan]{i}.[/cyan] {slot}")
            choice = console.input("> ").strip()
            try:
                choice = int(choice)
                if choice in SLOTS:
                    return SLOTS[choice]
            except ValueError:
                pass
            return "weapon"

        def _chooseLevel() -> int:
            level = console.input("[cyan]What level item do you want to create? (default 1)[/cyan]\n> ").strip()
            try:
                level = int(level)
                if level > 0:
                    return level
            except ValueError:
                pass
            return 1
            
        def _chooseRarity() -> ItemRarity:
            console.print("\n[bold cyan]=== Choose Rarity ===[/bold cyan]")
            for i, rarity in RARITIES.items():
                rarityName = formatRarity(rarity.value, rarity.value)
                console.print(f"  [cyan]{i}.[/cyan] {rarityName}")
            choice = console.input("> ").strip()
            try:
                choice = int(choice)
                if choice in RARITIES:
                    return RARITIES[choice]
            except ValueError:
                pass
            return ItemRarity.COMMON

        while True:
            clearScreen()
            printHeader("Equipment Spawner - Debug")
            console.print("[dim]0.[/dim] Exit")
            console.print("[dim]1.[/dim] Begin Item Creation")
            choice = console.input("> ").strip()
            if choice == "0":
                break
            else:
                console.print("\n[bold gold1]=== Equipment Spawner ===[/bold gold1]")
                console.print("[dim]Defaults: slot = weapon | level = 1 | rarity = common[/dim]")
                slot = _chooseSlot()
                level = _chooseLevel()
                rarity = _chooseRarity()
                equipment = Equipment._generateEquipmentPiece(level, slot, rarity, self.game.player.className)
                self.game.player.addEquipmentToStorage(equipment)
                equipName = formatRarity(equipment.name, equipment.rarity.value)
                console.print(f"\n[success]Generated equipment![/success]")
                console.print(f"[cyan]Slot:[/cyan] {slot} | [cyan]Level:[/cyan] {level} | [cyan]Rarity:[/cyan] {formatRarity(rarity.value, rarity.value)}")
                console.print(f"{equipName}")
                console.print(f"[dim]{equipment}[/dim]")
                pause()
                break

    def giveConsumable(self):
        while True:
            clearScreen()
            printHeader("Give Consumable - Debug")
            console.print("[dim]0.[/dim] Exit")
            console.print("[dim]1.[/dim] View Consumables")
            console.print("\n[cyan]Otherwise type number to get consumable[/cyan]")
            choice = console.input("> ").strip()
            if choice == "0":
                break
            elif choice == "1":
                console.print("\n[bold cyan]=== Available Consumables ===[/bold cyan]")
                for cons, heal in CONSUMABLES.items():
                    console.print(f"  [green]{cons}:[/green] [health]+{heal} HP[/health]")
                pause()
            else:
                console.print("\n[bold cyan]=== Select Consumable ===[/bold cyan]")
                for i, cons in enumerate(CONSUMABLES.keys(), 1):
                    console.print(f"  [cyan]{i}.[/cyan] {cons}")
                choice = console.input("> ").strip()
                try:
                    choice = int(choice)
                    if 0 < choice <= len(CONSUMABLES):
                        name = list(CONSUMABLES.keys())[choice - 1]
                        amount = int(console.input("[cyan]Input amount to get:[/cyan]\n> ").strip())
                        if amount > 0:
                            self.game.player.addItem(name, amount)
                            printSuccess(f"Gave {amount}x {name}")
                            pause()
                            break
                    else:
                        printError("Invalid choice!")
                        pause()
                except ValueError:
                    printError("Invalid input!")
                    pause()

    def giveXp(self):
        while True:
            clearScreen()
            printHeader("Give XP - Debug")
            amount = console.input("[dim]0.[/dim] Exit\n[cyan]Otherwise type xp amount[/cyan]\n> ").strip()
            try:
                amount = int(amount)
                if amount == 0:
                    break
                else:
                    if amount > 0:
                        self.game.player.gainExperience(amount)
                        printSuccess(f"Gave {amount} XP")
                        pause()
                        break
                    else:
                        printWarning("Amount must be positive!")
                        pause()
            except ValueError:
                printError("Invalid input!")
                pause()

    def giveGold(self):
        while True:
            clearScreen()
            printHeader("Give Gold - Debug")
            amount = console.input("[dim]0.[/dim] Exit\n[cyan]Otherwise type gold amount[/cyan]\n> ").strip()
            try:
                amount = int(amount)
                if amount == 0:
                    break
                else:
                    if amount > 0:
                        self.game.player.gainGold(amount)
                        printSuccess(f"Gave {amount} gold")
                        pause()
                        break
                    else:
                        printWarning("Amount must be positive!")
                        pause()
            except ValueError:
                printError("Invalid input!")
                pause()

    def changeAreaLevel(self):
        while True:
            clearScreen()
            printHeader("Change Area Level - Debug")
            level = console.input("[dim]0.[/dim] Exit\n[cyan]Otherwise type positive integer to change area level[/cyan]\n> ").strip()
            try:
                level = int(level)
                if level > 0:
                    self.game.areaLevel = level
                    printSuccess(f"Game area level is now {self.game.areaLevel}")
                    pause()
                    break
            except ValueError:
                printError("Invalid input!")
                pause()

    def heal(self):
        self.game.player._health = self.game.player._maxHealth
        printSuccess('Healed player to max hp')

    def giveRunes(self):
        newInv = {}
        for runeInfo, rune in getAllRunes().items():
            info = runeInfo.split('_', 1)
            cat = info[0]
            rType = info[1]
            newInv[f'{cat}_{rType}'] = 100
        self.game.player._craftingInventory = newInv
        printSuccess('Given player 100 of each crafting rune')

    def setPlayerLevel(self):
        while True:
            clearScreen()
            printHeader("Set Player Level - Debug")
            level = console.input("What level do you want to be set to?\n[cyan]>[/cyan] ").strip()
            try:
                level = int(level)
                if level < 0:
                    printWarning('Level must be positive!')
                    pause()
                else:
                    while self.game.player._level < level:
                        xp = self.game.player._xpToNextLevel
                        self.game.player.gainExperience(xp)
                    pause()
                    break
            except ValueError:
                printError('Invalid input!')
                pause()

    def mainMenu(self, autoCommand: str = None):
        if autoCommand:
            self.processChoice(autoCommand)
        else:
            while True:
                clearScreen()
                printHeader("Debug Menu")
                console.print("[dim]0.[/dim] Exit")
                console.print("[dim]1.[/dim] View Commands")
                console.print("\n[cyan]Type a command to use it[/cyan]")
                choice = console.input("> ").strip()
                if choice == "0":
                    break
                elif choice == "1":
                    console.print("\n[bold cyan]=== Available Commands ===[/bold cyan]")
                    for i, command in enumerate(COMMANDS, 1):
                        console.print(f"  [dim]{i}.[/dim] [cyan]{command}[/cyan]")
                    pause()
                else:
                    self.processChoice(choice)

    def processChoice(self, choice: str):
        choice = choice.lower()
        if choice in COMMANDS:
            if choice == "give_item":
                self.giveItem()
            elif choice == "remove_item":
                self.removeItem()
            elif choice in ["give_equipment", "eq"]:
                self.giveEquipment()
            elif choice in ["give_consumable", "consumable"]:
                self.giveConsumable()
            elif choice in ["give_xp", "xp"]:
                self.giveXp()
            elif choice in ["give_gold", "gold"]:
                self.giveGold()
            elif choice in ['restock']:
                self.game.camp.market._generateStock()
            elif choice in ['area', 'area_level']:
                self.changeAreaLevel()
            elif choice in ['heal']:
                self.heal()
            elif choice in ['runes', 'crafting']:
                self.giveRunes()
            elif choice in ['level', 'lvl']:
                self.setPlayerLevel()
            elif choice in ['recalc', 'stats']:
                self.game.player._recalculateStats()
            else:
                printError(f"Invalid choice: {choice}")
                pause()
        else:
            printWarning(f"Unknown command: {choice}")
            pause()

...