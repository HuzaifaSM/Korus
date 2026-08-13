from typing import Dict, Optional, List
from .station import Station
import random
from scripts.items import Equipment, ItemRarity, rollRarity
from scripts.styles import (
    console, clearScreen, printHeader, printSeparator,
    pause, printWarning, printError, printSuccess, formatRarity,
    Panel
)
from scripts.runeDrops import getRuneObject
from crafting.base import CraftOutcome, CraftResult
from rich.layout import Layout
from copy import deepcopy

class Forge(Station):
    """
    Crafting station for creating equipment and applying runes to equipment.\n
    Features a split-screen interface showing before/after item states
    """
    def __init__(self, player):
        super().__init__(player, "Forge")
        self.fuel = 0
        self.blueprints = 0
        self.previousItem = None
        self.currentItem = None
        self.currentCraftingPage = 1

    def _getUpgradeRequirements(self) -> Dict[int, Dict[str, int]]:
        return {
            1: {"iron_ore": 50, "stone": 100, "wood": 50},
            2: {"iron_ore": 150, "crystal": 15, "bone": 30},
            3: {"crystal": 40, "mana_essence": 20, "ancient_wood": 10},
            4: {"mana_essence": 60, "diamond": 30, "dragon_scale": 10},
            5: {"dragon_scale": 30, "ascended_essence": 20, "diamond": 100}
        }

    @property
    def runePages(self) -> Dict[int, List[Dict[str, int]]]:
        temp = {}
        for i in range(20):
            temp[i+1] = []
        playerRunes = self.player._craftingInventory
        for i, (rune, quant) in enumerate(playerRunes.items()):
            page = i // 10 + 1
            temp[page].append({rune: quant})
        for k, v in temp.copy().items():
            if v == []:
                temp.pop(k)
        return temp

    @property
    def runeList(self) -> List[Dict[str, int]]:
        return self.runePages[self.currentCraftingPage]

    def _serialise(self):
        temp = super()._serialise()
        temp['fuel'] = self.fuel
        temp['blueprints'] = self.blueprints
        return temp

    def mainMenu(self):
        while True:
            clearScreen()
            printHeader(f"Forge - Level {self.level}")
            console.print(f"[gold]Fuel:[/gold] {self.fuel}")
            console.print(f"[gold]Blueprints:[/gold] {self.blueprints}")
            printSeparator()
            console.print("[dim]0.[/dim] Return")
            console.print("[dim]1.[/dim] Craft Equipment")
            console.print("[dim]2.[/dim] Repair Equipment")
            console.print("[dim]3.[/dim] Craft With Runes")
            console.print("[dim]9.[/dim] Upgrade Forge")

            choice = console.input("\n[cyan]>[/cyan] ").strip()

            try:
                choice = int(choice)
                match choice:
                    case 0:
                        break
                    case 1:
                        self.craftingMenu()
                    case 2:
                        self.repairEquipment()
                    case 3:
                        self.craftingInterface()
                    case 9:
                        self.upgrade()
                    case _:
                        printWarning(f"Invalid choice: {choice}")
            except ValueError as e:
                printError(f"{e}")
                pause()

    def craftingMenu(self):
        clearScreen()
        printHeader("CRAFT EQUIPMENT")
        console.print(f"[gold]Blueprints:[/gold] {self.blueprints}")
        
        slots = ['weapon', 'head', 'chest', 'legs', 'feet', 'ring', 'amulet']
        console.print("\n[bold]nSelect slot to craft:[/bold]")
        for i, slot in enumerate(slots, 1):
            console.print(f"  [cyan]{i}.[/cyan] {slot.capitalize()}")
        
        choice = console.input("\n[cyan]Choose slot (0 to cancel):\n>[/cyan] ").strip()
        try:
            index = int(choice) - 1
            if 0 <= index < len(slots):
                self.craftEquipment(slots[index])
        except ValueError:
            pass
        pause()

    def craftEquipment(self, slot: str):
        if self.level < 1:
            printWarning(f"Forge Level 1 required for crafting. Current Level: {self.level}")
            return
        
        blueprintCost = 5 + (self.level * 5)
        if self.blueprints < blueprintCost:
            printWarning(f"Need {blueprintCost} blueprints to craft. Current blueprints: {self.blueprints}")
            return
        rarityChances = {
            1: {ItemRarity.COMMON: 0.8, ItemRarity.UNCOMMON: 0.2},
            2: {ItemRarity.COMMON: 0.6, ItemRarity.UNCOMMON: 0.3, ItemRarity.RARE: 0.1},
            3: {ItemRarity.COMMON: 0.4, ItemRarity.UNCOMMON: 0.35, ItemRarity.RARE: 0.2, ItemRarity.EPIC: 0.05},
            4: {ItemRarity.UNCOMMON: 0.4, ItemRarity.RARE: 0.35, ItemRarity.EPIC: 0.2, ItemRarity.LEGENDARY: 0.05},
            5: {ItemRarity.RARE: 0.5, ItemRarity.EPIC: 0.35, ItemRarity.LEGENDARY: 0.15}
        }

        rarityBonus = int(self.player._stats['Bonuses']['itemRarity'] * 0.5) # rarity applied at half value
        rarity = rollRarity(rarityBonus)

        roll = random.random()
        cumulative = 0
        rarity = ItemRarity.COMMON
        for r, chance in rarityChances[self.level].items():
            cumulative += chance
            if roll <= cumulative:
                rarity = r
                break
        # generate equipment
        equipment = Equipment._generateEquipmentPiece(self.player._level, slot, rarity)
        self.blueprints -= blueprintCost
        console.print(f"\n[success]Crafted:[/success] {formatRarity(equipment.name, equipment.rarity.value)}")
        console.print(f"    [dim]{equipment._formatStats()}[/dim]")
        self.player.addEquipmentToStorage(equipment)


    def repairEquipment(self):
        clearScreen()
        printHeader("Repair Equipment")
        
        allEquipment = []
        for slot, equip in self.player._equipment.items():
            if equip and equip.durability < equip.maxDurability:
                allEquipment.append((f"[EQUIPPED] {slot}", equip))
        for i, equip in enumerate(self.player._equipmentStorage):
            if equip.durability < equip.maxDurability:
                allEquipment.append((f"[STORAGE] #{i+1}", equip))

        if not allEquipment:
            printWarning("No equipment needs repairing.")
            pause()
            return

        console.print("\n[cyan]Equipment needing repair:[/cyan]")
        for i, (location, equip) in enumerate(allEquipment, 1):
            durabilityPct = round(equip.durability / equip.maxDurability * 100, 2)
            console.print(f"  [cyan]{i}.[/cyan] {location} {equip.name}")
            console.print(f"    [dim]Durability: {equip.durability} / {equip.maxDurability} ({durabilityPct})[/dim]")
        choice = console.input("\n[cyan]Choose equipment to repair (0 to cancel):\n> [/cyan]").strip()
        try:
            index = int(choice) - 1
            if 0 <= index < len(allEquipment):
                _, equip = allEquipment[index]
                # calculate repair cost
                durabilityNeeded = equip.maxDurability - equip.durability
                fuelCost = max(1, durabilityNeeded // 10)
                # resource cost based on rarity
                resourceCost = {
                    ItemRarity.COMMON: ("iron_ore", 5),
                    ItemRarity.UNCOMMON: ("iron_ore", 10),
                    ItemRarity.RARE: ("crystal", 5),
                    ItemRarity.EPIC: ("mana_essence", 3),
                    ItemRarity.LEGENDARY: ("dragon_scale", 2)
                }
                resource, amount = resourceCost.get(equip.rarity, ("iron_ore", 5))
                amount *= equip.level

                console.print("\n[yellow]Repair cost:[/yellow]\n"
                      f"  - [white]Fuel: {fuelCost}[/white]\n"
                      f"  - [white]{resource}: {amount}[/white]\n")
                confirm = console.input("[cyan]Confirm repair? (y/n)\n> [/cyan]").strip().lower()
                if confirm == 'y':
                    if self.fuel >= fuelCost and self.player.hasItem(resource, amount):
                        self.fuel -= fuelCost
                        self.player.removeItem(resource, amount)
                        equip.repair()
                        printSuccess(f"\n{equip.name} repaired to full durability.")
                    else:
                        printWarning("Insufficient resources.")
                pause()
        except ValueError:
            pass

    def craftingInterface(self):
        clearScreen()

        item = self._selectEquipment()
        if not item:
            return
        
        self.currentItem = item
        self.previousItem = None

        while True:
            clearScreen()

            layout = self._createSplitLayout()

            console.print(layout)
            printSeparator()

            if item.entropyLocked:
                console.print("[red bold]⚠ ITEM IS ENTROPY LOCKED - NO MORE CRAFTING POSSIBLE[/red bold]")
                pause()
                break
            
            if item.destabilised:
                console.print("[dark_red bold]⚠ ITEM IS CORRUPTED - NO MORE CRAFTING POSSIBLE[/dark_red bold]")
                pause()
                break

            console.print("[cyan]Options:[/cyan]")
            console.print("  [dim]1.[/dim] View Crafting Inventory")
            console.print("  [dim]2.[/dim] Apply Rune")
            console.print("  [dim]3.[/dim] Next Rune Page")
            console.print("  [dim]4.[/dim] Previous Rune Page")
            console.print("  [dim]5.[/dim] View Item Details")
            console.print("  [dim]0.[/dim] Finish Crafting")
            
            choice = console.input("\n[cyan]>[/cyan] ").strip()
            
            try:
                choice = int(choice)
                if choice == 0:
                    break
                elif choice == 1:
                    self._viewCraftingInventory()
                elif choice == 2:
                    self._applyRune()
                elif choice == 3:
                    self.currentCraftingPage = min(len(self.runePages), self.currentCraftingPage + 1)
                    console.print(f'[dim]Now on crafting page {self.currentCraftingPage}[/dim]')
                    pause()
                elif choice == 4:
                    self.currentCraftingPage = max(1, self.currentCraftingPage - 1)
                    console.print(f'[dim]Now on crafting page {self.currentCraftingPage}[/dim]')
                    pause()
                elif choice == 5:
                    self._viewItemDetails()
                else:
                    printWarning("Invalid choice")
                    pause()
            except ValueError:
                printWarning("Invalid input")
                pause()

        clearScreen()
        console.print("[gold1 bold]=== CRAFTING COMPLETE ===[/gold1 bold]\n")
        console.print(self.currentItem)
        pause()

    def _applyRune(self):
        clearScreen()
        printSeparator()
        printHeader('Apply Rune')
        printSeparator()

        if not self.player._craftingInventory:
            printWarning('You have no runes!')
            pause()
            return

        console.print(f'[cyan]Available Runes:[/cyan] | Page: {self.currentCraftingPage} / {len(self.runePages)}\n')
        runeList = self.runeList
        for i, data in enumerate(runeList):
            for key, quantity in data.items():
                category, runeType = key.split('_', 1)
                rune = getRuneObject(category, runeType)
                console.print(f'  [cyan]{i+1}.[/cyan] {rune}')
                console.print(f'[dim]Quantity: {quantity}[/dim]\n')

        choice = console.input("[cyan]Choose rune to apply (0 to cancel):\n>[/cyan] ").strip()

        try:
            index = int(choice) - 1
            if 0 <= index <= len(runeList):
                for info, _ in runeList[index].items():
                    info = info.split('_', 1)
                    category, runeType = info[0], info[1]
                    rune = getRuneObject(category, runeType)

                if not rune:
                    printError(f"Failed to load rune: {runeType}")
                    pause()
                    return
                
                self.previousItem = deepcopy(self.currentItem)

                console.print(f"\n[yellow]Applying:[/yellow] {rune.name}")
                console.print(f"[cyan]Effect:[/cyan] [dim]{rune.description}[/dim]")
                confirm = console.input("\n[cyan]Confirm? (y/n):\n>[/cyan]").strip().lower()

                if confirm == 'y':
                    result = rune.apply(self.currentItem)
                    outcome = result.outcome

                    self._showCraftingResult(result, rune.name)
                    pause()
                    clearScreen()

                    if outcome in [CraftOutcome.SUCCESS, CraftOutcome.PARTIAL_SUCCESS]:
                        self.player.removeRune(category, runeType, 1)
                    
                    pause()
                else:
                    self.previousItem = None
        except ValueError:
            printWarning('Invalid input')
            pause()

    def _showCraftingResult(self, result: CraftResult, runeName: str):
        if result.outcome == CraftOutcome.SUCCESS:
            console.print("[green bold]✓ CRAFTING SUCCESSFUL![/green bold]")
            console.print(f"[green]Applied {runeName}[/green]")
            console.print(f"[dim green]{result.message}[/dim green]")
        elif result.outcome == CraftOutcome.PARTIAL_SUCCESS:
            console.print("[yellow bold]⚠ PARTIAL SUCCESS[/yellow bold]")
            console.print(f"[yellow]{result.message}[/yellow]")
        else:
            console.print("[dim]○ No Effect[/dim]")
            console.print(f"[dim]{result.message}[/dim]")

        pause()

    def _viewCraftingInventory(self):
        clearScreen()
        printHeader('Crafting Inventory')
        self.player.showCraftingInventory()
        pause()

    def _createSplitLayout(self) -> Panel:
        layout = Layout()

        if self.previousItem:
            prevPanel = Panel(
                self.previousItem.__str__(),
                title='[dim]Previous State[/dim]',
                border_style='dim',
                height=20
            )

        currentPanel = Panel(
            self.currentItem.__str__(),
            title='[gold]Current State[/gold]',
            border_style='gold1',
            height=20
        )

        if self.previousItem:
            layout.split_row(
                Layout(prevPanel),
                Layout(currentPanel)
            )
        else:
            layout.update(currentPanel)

        return Panel(
            layout,
            height=22,
            border_style='dim'
        )

    def _selectEquipment(self) -> Optional[Equipment]:
        clearScreen()
        printHeader('Select Equipment')

        allEquipment = []

        for slot, equip in self.player._equipment.items():
            if equip and not equip.entropyLocked and not equip.destabilised:
                allEquipment.append((f'[EQUIPPED] {slot}', equip))
        for i, equip in enumerate(self.player._equipmentStorage):
            if not equip.entropyLocked and not equip.destabilised:
                allEquipment.append((f'[STORAGE] #{i+1}', equip))

        if not allEquipment:
            printWarning('No equipment available.')
            pause()
            return None
        
        console.print(f'[gold]Available Equipment[/gold]\n')
        for i, (location, equip) in enumerate(allEquipment, 1):
            console.print(f"  [cyan]{i}.[/cyan] {location} {equip.name}")
            console.print(f"      [dim]Entropy: {equip.entropy} / {equip.maxEntropy} | "
                          f"Level: {equip.level} | Rarity: {equip.rarity.value.title()}[/dim]\n")
        
        choice = console.input("\n[cyan]Choose equipment (0 to cancel):\n> [/cyan]").strip()
        try:
            index = int(choice) - 1
            if 0 <= index < len(allEquipment):
                return allEquipment[index][1]
        except ValueError:
            pass

        return None

    def _viewItemDetails(self):
        clearScreen()
        printHeader('Item Details')

        console.print(self.currentItem)
        pause()

