from typing import Dict, Optional, List
from .station import Station
import random
from scripts.items.items import ItemRarity, rollRarity, RARITY_SERIALS
from scripts.items.equipment import Equipment
from scripts.styles import (
    console, clearScreen, printHeader, printSeparator,
    pause, printWarning, printError, printSuccess, formatRarity,
    Panel, checkGlobalCommand, createEquipmentStoragePages, stepPage
)
from scripts.runeDrops import getRuneObject
from scripts.korusFeedClient import reportItem
from scripts.crafting.base import CraftOutcome, CraftResult, CraftingItem
from rich.columns import Columns
from rich.table import Table
from rich import box
from copy import deepcopy

class Forge(Station):
    """
    Crafting station for creating equipment and applying runes to equipment.\n
    Features a split-screen interface showing before/after item states
    """
    _FILLED_BLOCKED_RUNES = frozenset({'growth', 'conversion', 'revealing', 'soulbound', 'echoing'})
    _EMPTY_BLOCKED_RUNES = frozenset({'erasing', 'fusion', 'equilibrium', 'sacrifice', 'chaos',
                                       'tier randomiser', 'value randomiser', 'affix randomiser', 'immutable'})

    def __init__(self, player):
        super().__init__(player, "Forge")
        self.fuel = 0
        self.blueprints = 0
        self.previousItem = None
        self.currentItem = None
        self.currentCraftingPage = 1
        self.runeFilter = ""
        self._runePagesCache: Dict[int, List[Dict[str, int]]] = {}
        self._runePagesDirty = True

    def _invalidateRunePages(self):
        self._runePagesDirty = True

    def _getUpgradeRequirements(self) -> Dict[int, Dict[str, int]]:
        return {
            1: {"iron_ore": 5, "stone": 25, "wood": 10,
                'description': 'Enemies will begin to drop [resource]Fuel[/resource] and [resource]Blueprints[/resource].\n[resource]Fuel[/resource] is used to repair and fuse equipment. [resource]Blueprints[/resource] are used to craft and fuse new peices of equipment.\nYou are able to craft Common and Uncommon equipment.\nYou are able to fuse Common Equipment to Uncommon.'
                },
            2: {"iron_ore": 50, "crystal": 15, "bone": 10,
                'description': "Repairing items grants 20% more durability recovered. You can now craft Rare equipment. You can fuse Uncommon Equipment to Rare."
                },
            3: {"crystal": 40, "mana_essence": 20, "ancient_wood": 10,
                'description': "Repairing items grants 20% more durability recovered. You can now craft Epic equipment. You can fuse Rare Equipment to Epic."
                },
            4: {"mana_essence": 50, "diamond": 30, "dragon_scale": 10,
                'description': "Repairing items grants 20% more durability recovered. You can now craft Legendary equipment. Crafted equipment cannot be Common. You can fuse Epic Equipment to Legendary."
                },
            5: {"dragon_scale": 30, "ascended_essence": 20, "diamond": 100,
                'description': "Repairing items grants 20% more durability recovered. Crafted equipment cannot be Uncommon. Fusing requires 1 less item per tier."
                }
        }

    def _checkRuneEligibility(self, rune: CraftingItem) -> bool:
        eq = self.currentItem
        runeLevel = rune.minItemLevel or 1
        runeName = rune.name.lower()

        if hasattr(rune, 'fromRarity'):
            if rune.fromRarity != eq.rarity:
                return False

        if 'base type randomiser' in runeName and not getattr(eq, 'baseTypeName', None):
            return False

        if eq.allSlotsFilled and any(k in runeName for k in self._FILLED_BLOCKED_RUNES):
            return False

        if eq.allSlotsEmpty and any(k in runeName for k in self._EMPTY_BLOCKED_RUNES):
            return False

        if eq.mastery >= 20 and 'mastery' in runeName:
            return False

        if eq.level < runeLevel:
            return False
        
        if self.runeFilter != "":
            if self.runeFilter not in rune.name.lower():
                return False

        return True

    @property
    def runePages(self) -> Dict[int, List[Dict[str, int]]]:
        if self._runePagesDirty:
            self._runePagesCache = self._buildRunePages()
            self._runePagesDirty = False
        return self._runePagesCache

    def _buildRunePages(self) -> Dict[int, List[Dict[str, int]]]:
        temp: dict[int, list[Dict[str, int]]] = {}
        for i in range(20):
            temp[i+1] = []
        runesAdded = 0
        playerRunes = self.player._craftingInventory

        for rune, quant in playerRunes.items():
            page = runesAdded // 12 + 1
            cat, rType = rune.split('_', 1)
            runeObj = getRuneObject(cat, rType)

            if self._checkRuneEligibility(runeObj):
                temp[page].append({rune: quant})
                runesAdded += 1

        for k, v in temp.copy().items():
            if v == []:
                temp.pop(k)
        return temp

    @property
    def runeList(self) -> List[Dict[str, int]]:
        pages = self.runePages
        if not pages:
            return []
        if self.currentCraftingPage not in pages:
            self.currentCraftingPage = min(pages.keys())
        return pages[self.currentCraftingPage]

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
            console.print("[dim]4.[/dim] Fuse Equipment")
            console.print("[dim]9.[/dim] Upgrade Forge")

            choice = console.input("\n[cyan]>[/cyan] ").strip()
            checkGlobalCommand(choice)

            try:
                choice = int(choice)
                match choice:
                    case 0:
                        return
                    case 1:
                        self.craftingMenu()
                    case 2:
                        self.repairEquipment()
                    case 3:
                        self.craftingInterface()
                    case 4:
                        self.fuseEquipmentMenu()
                    case 9:
                        self.upgrade()
                    case _:
                        printWarning(f"Invalid choice: {choice}")
            except ValueError as e:
                printError(f"{e}")
                pause()

    def craftingMenu(self):
        if self.level > 0:
            clearScreen()
            printHeader("CRAFT EQUIPMENT")
            console.print(f"[gold]Blueprints:[/gold] {self.blueprints}")
            
            slots = ['weapon', 'head', 'chest', 'legs', 'feet', 'ring', 'amulet', 'offhand', 'sigil']
            console.print("\n[bold]Select slot to craft:[/bold]")
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
        else:
            printWarning(f"Forge Level 1 required for crafting. Current Level: {self.level}")
            pause()
            return

    def craftEquipment(self, slot: str):
        if self.level < 1:
            printWarning(f"Forge Level 1 required for crafting. Current Level: {self.level}")
            pause()
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

        rarityBonus = int(self.player._stats['Bonuses']['item_rarity'] * 0.5) # rarity applied at half value
        rarity = rollRarity(rarityBonus)

        roll = random.random()
        cumulative = 0
        for r, chance in rarityChances[self.level].items():
            cumulative += chance
            if roll <= cumulative:
                rarity = r
                break
        # generate equipment
        equipment = Equipment._generateEquipmentPiece(self.player._level, slot, rarity, self.player.className, self.player._name)
        self.blueprints -= blueprintCost
        console.print(f"\n[success]Crafted:[/success] {formatRarity(equipment.name, equipment.rarity.value)}")
        console.print(f"    [dim]{equipment}[/dim]")
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

                durabilityNeeded = equip.maxDurability - equip.durability
                fuelCost = max(1, durabilityNeeded // 10)

                resourceCost = {
                    ItemRarity.COMMON: ("stone", 2),
                    ItemRarity.UNCOMMON: ("iron_ore", 3),
                    ItemRarity.RARE: ("crystal", 3),
                    ItemRarity.EPIC: ("mana_essence", 3),
                    ItemRarity.LEGENDARY: ("dragon_scale", 2)
                }
                resource, amount = resourceCost.get(equip.rarity, ("iron_ore", 5))
                amount *= equip.level * int(1 + 0.2 * self.level)

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
        self._invalidateRunePages()

        while True:
            clearScreen()

            layout = self._createSplitLayout()

            console.print(layout)
            console.print(self._createRunePanel())
            printSeparator()

            if item.entropyLocked:
                console.print("[red bold]⚠ ITEM IS ENTROPY LOCKED - NO MORE CRAFTING POSSIBLE[/red bold]")
                pause()
                break

            if item.destabilised:
                console.print("[dark_red bold]⚠ ITEM IS CORRUPTED - NO MORE CRAFTING POSSIBLE[/dark_red bold]")
                pause()
                break

            if self.runeFilter != "":
                console.print(f"Current Filter: [bold]{self.runeFilter}[bold]")
            console.print("[cyan]Options:[/cyan]")
            console.print("  [dim]0.[/dim] Finish Crafting")
            console.print("  [dim]#.[/dim] Apply Rune (enter a rune number from the table above)")
            console.print("  [dim]I.[/dim] View Crafting Inventory")
            if self.runeFilter != "":
                console.print("  [dim]C.[/dim] Clear Current Filter")
            else:
                console.print("  [dim]?.[/dim] Type a word/keyword to filter for Runes of that type")
            if len(self.runePages) > 1:
                console.print("  [dim]N.[/dim] Next Rune Page")
                console.print("  [dim]P.[/dim] Previous Rune Page")

            choice = console.input("\n[cyan]>[/cyan] ").strip()
            checkGlobalCommand(choice)

            if choice.lstrip('-').isdigit():
                index = int(choice) - 1
                if index == -1:
                    break

                runeList = self.runeList
                if not (0 <= index < len(runeList)):
                    printWarning("Invalid choice")
                    pause()
                    continue

                key = next(iter(runeList[index]))
                category, runeType = key.split('_', 1)
                rune = getRuneObject(category, runeType)

                if not rune:
                    printError(f"Failed to load rune: {runeType}")
                    pause()
                    continue

                self.previousItem = deepcopy(self.currentItem)

                console.print(f"\n[yellow]Applying:[/yellow] {rune.name}")
                console.print(f"[cyan]Effect:[/cyan] [dim]{rune.description}[/dim]")
                confirm = console.input("\n[cyan]Confirm? (y/n):\n>[/cyan] ").strip().lower()

                if confirm == 'y':
                    result = rune.apply(self.currentItem, self.player)
                    outcome = result.outcome
                    self._invalidateRunePages()
                    reportItem(self.currentItem, self.player._name, event=f"Applied {rune.name}:\n{result.message}")

                    self.player._recalculateStats(False)

                    self._showCraftingResult(result, rune.name)
                    clearScreen()

                    if outcome in [CraftOutcome.SUCCESS, CraftOutcome.PARTIAL_SUCCESS]:
                        self.player.removeRune(category, runeType, 1)

                    pause()
                else:
                    self.previousItem = None

            elif choice.lower() == 'i':
                self._viewCraftingInventory()
            elif choice.lower() == 'n':
                if len(self.runePages) > 1:
                    self.currentCraftingPage = min(len(self.runePages), self.currentCraftingPage + 1)
                    console.print(f'[dim]Now on crafting page {self.currentCraftingPage}[/dim]')
                    pause()
                else:
                    printWarning("Invalid choice")
                    pause()
            elif choice.lower() == 'p':
                if len(self.runePages) > 1:
                    self.currentCraftingPage = max(1, self.currentCraftingPage - 1)
                    console.print(f'[dim]Now on crafting page {self.currentCraftingPage}[/dim]')
                    pause()
                else:
                    printWarning("Invalid choice")
                    pause()
            elif choice.lower() == 'c':
                self.runeFilter = ""
                self.currentCraftingPage = 1
                self._invalidateRunePages()
            elif choice.strip().lower() != "":
                self.runeFilter = choice.lower().strip()
                self.currentCraftingPage = 1
                self._invalidateRunePages()

        clearScreen()
        console.print("[gold1 bold]=== CRAFTING COMPLETE ===[/gold1 bold]\n")
        console.print(self.currentItem)
        pause()

    def getFusionPieces(self) -> List[List[Equipment], str, str]:
        availableRarities: List[str] = []
        if self.level > 0:
            availableRarities.append('uncommon')
        if self.level > 1:
            availableRarities.append('rare')
        if self.level > 2:
            availableRarities.append('epic')
        if self.level > 3:
            availableRarities.append('legendary')

        while True:
            clearScreen()
            printHeader("Pick a Rarity to Fuse into:")
            console.print("[dim]0.[/dim] Cancel")
            for i, r in enumerate(availableRarities, start=1):
                console.print(f"[cyan]{i}.[/cyan] {r.title()}") # 1 unc, 2 rare, 3 epic, 4 legendary
            try:
                rar = int(console.input("[cyan]>[/cyan] ").strip())
                if rar == 0:
                    return None, None

                chosenRarity = RARITY_SERIALS[availableRarities[rar - 1]]

                rarList = list(ItemRarity)
                fusionRarity = rarList[rarList.index(chosenRarity) - 1]

                availablePieces = [
                    e for e in self.player._equipmentStorage if e.rarity == fusionRarity
                ]

                return availablePieces, fusionRarity, chosenRarity

            except ValueError as e:
                printWarning("Invalid Input")
            except IndexError as e:
                printWarning("Invalid Choice")
            except KeyError as e:
                printWarning("Invalid Choice")

    def getFusionSlot(self) -> str:
        slots = ['weapon', 'head', 'chest', 'legs', 'feet', 'ring', 'amulet', 'offhand', 'sigil']
        chosenSlot = None
        while True:
            clearScreen()
            printHeader("Choose a slot to guarantee Fusion will make (0 to cancel)")
            for i, s in enumerate(slots, start = 1):
                console.print(f"[dim]{i}.[/dim] {s.title()}")
            choice = console.input("[cyan]>[/cyan] ")
            try:
                choice = int(choice)
                if choice == 0:
                    return None

                if 0 < choice < len(slots):
                    chosenSlot = slots[choice - 1]

                    return chosenSlot

            except ValueError:
                printWarning("Invalid choice")
                pause()
                continue

    def fuseEquipmentMenu(self):
        if self.level == 0:
            printWarning("Forge Level 1 required for Fusion. Current Level: 0")
            pause()
            return

        RARITY_TO_FUSE = {
            ItemRarity.COMMON: 3,
            ItemRarity.UNCOMMON: 3,
            ItemRarity.RARE: 4,
            ItemRarity.EPIC: 4
        }

        fusionPieces, fusedRarity, newRarity = self.getFusionPieces()
        if fusionPieces is None or fusedRarity is None:
            return
        slot = self.getFusionSlot()
        if slot is None:
            return

        neededToFuse = RARITY_TO_FUSE[fusedRarity]
        if self.level == 5:
            neededToFuse -= 1
        chosenToFuse: list[Equipment] = []

        if len(fusionPieces) < neededToFuse:
            printWarning(f"You do not have enough {fusedRarity.value} Equipment to Fuse! Needed pieces of equipment: {neededToFuse}")
            pause()
            return

        while len(chosenToFuse) != neededToFuse:
            pages = createEquipmentStoragePages(fusionPieces, 4)
            totalPages = len(pages)
            currentPage = 1
            if pages:
                console.print(pages[currentPage])
                console.print(f"Page {currentPage}/{totalPages}")

                prompt = "\n[red]Choose Item to add to Fusion (0 to cancel"
                if totalPages > 1:
                    prompt += ", N for next page, P for previous page"
                prompt += "):[/red]"

                console.print(prompt)
                console.print(f"[dim]{len(chosenToFuse)}/{neededToFuse} chosen[/dim]")

                choice = console.input("[cyan]> [/cyan] ").strip().lower()

                try:
                    index = int(choice) - 1
                except ValueError:
                    printWarning("Invalid input")
                    pause()
                    continue

                if index == -1:
                    break

                if 0 <= index < len(fusionPieces):
                    eq = fusionPieces[index]
                    chosenToFuse.append(eq)
                    fusionPieces.pop(index)
                    printSuccess(f"{eq.name} has been added for fusion")
                else:
                    printWarning("Invalid Choice")
                    pause()

        totalLevel = 0
        for e in chosenToFuse:
            totalLevel += e.level
            self.player._equipmentStorage.remove(e)

        level = self.player._level + totalLevel // len(chosenToFuse)

        newEquipment = Equipment._generateEquipmentPiece(level, slot, newRarity, self.player.className, self.player._name)
        self.player.addEquipmentToStorage(newEquipment)
        printSuccess(f"Successfully fused {neededToFuse} {fusedRarity.value.title()} pieces of Equipment to create {newEquipment.name}")
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

    def _createSplitLayout(self) -> Columns | Panel:
        currentPanel = Panel(
            self.currentItem.__str__(),
            title='[gold]Current State[/gold]',
            border_style='gold1',
            height=18
        )

        if not self.previousItem:
            return currentPanel

        prevPanel = Panel(
            self.previousItem.__str__(),
            title='[dim]Previous State[/dim]',
            border_style='dim',
            height=18
        )

        return Columns([prevPanel, currentPanel], equal=True, expand=True)

    def _createRunePanel(self) -> Panel:
        title = f'[cyan]Available Runes[/cyan] | Page: {self.currentCraftingPage} / {max(len(self.runePages), 1)}'

        if not self.runeList:
            if self.runeFilter:
                content = f"[dim]No runes match filter '{self.runeFilter}'. Press C to clear it.[/dim]"
            elif not self.player._craftingInventory:
                content = "[dim]You have no runes.[/dim]"
            else:
                content = "[dim]No runes are usable on this item.[/dim]"
            return Panel(content, title=title, border_style='cyan')

        return Panel(
            self._createRuneTable(),
            title=title,
            border_style='cyan'
        )

    def _createRuneTable(self) -> Table:
        table = Table(box=box.HORIZONTALS, show_header=True, header_style='bold cyan', expand=True, show_lines=True)
        table.add_column("#", justify="right", width=3, overflow="fold")
        table.add_column("Rune")
        table.add_column("#", justify="right", width=3, overflow="fold")
        table.add_column("Rune")
        table.add_column("#", justify="right", width=3, overflow="fold")
        table.add_column("Rune")

        runeList = self.runeList
        rows = 4

        for row in range(rows):
            leftIndex = row
            centreIndex = row + rows
            rightIndex = row + rows * 2

            leftNum, leftName = "", ""
            if leftIndex < len(runeList):
                leftNum = str(leftIndex + 1)
                leftName = self._formatRuneEntry(runeList[leftIndex])

            centNum, centName = "", ""
            if centreIndex < len(runeList):
                centNum = str(centreIndex + 1)
                centName = self._formatRuneEntry(runeList[centreIndex])

            rightNum, rightName = "", ""
            if rightIndex < len(runeList):
                rightNum = str(rightIndex + 1)
                rightName = self._formatRuneEntry(runeList[rightIndex])

            table.add_row(leftNum, leftName, centNum, centName, rightNum, rightName)

        return table

    def _formatRuneEntry(self, data: Dict[str, int]) -> str:
        key, quantity = next(iter(data.items()))
        category, runeType = key.split('_', 1)
        rune = getRuneObject(category, runeType)
        return f"{rune} [dim](x{quantity})[/dim]"

    def _selectEquipment(self) -> Optional[Equipment]:
        allEquipment = []

        for _, equip in self.player._equipment.items():
            if equip and not equip.entropyLocked and not equip.destabilised:
                allEquipment.append((f'[EQUIPPED] ', equip))
        for i, equip in enumerate(self.player._equipmentStorage):
            if not equip.entropyLocked and not equip.destabilised:
                allEquipment.append((f'[STORAGE] #{i+1}', equip))

        if not allEquipment:
            clearScreen()
            printHeader('Select Equipment')
            printWarning('No equipment available.')
            pause()
            return None

        pages = createEquipmentStoragePages(allEquipment, render=lambda pair: f"[dim]{pair[0]}[/dim]\n{pair[1]}")
        totalPages = len(pages)
        currentPage = 1

        while True:
            clearScreen()
            printHeader('Select Equipment')
            console.print(f"\n[bold cyan]=== Available Equipment (Page {currentPage}/{totalPages}) ===[/bold cyan]")
            console.print(pages[currentPage])

            prompt = "\n[cyan]Choose equipment (0 to cancel"
            if totalPages > 1:
                prompt += ", N for next page, P for previous page"
            prompt += "):[/cyan]\n> "
            choice = console.input(prompt).strip().lower()

            newPage = stepPage(currentPage, totalPages, choice)
            if newPage is not None:
                currentPage = newPage
                continue

            try:
                index = int(choice) - 1
            except ValueError:
                printWarning("Invalid input!")
                pause()
                return None
            break

        if 0 <= index < len(allEquipment):
            return allEquipment[index][1]
        return None

...