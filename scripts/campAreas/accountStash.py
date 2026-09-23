from typing import Dict, Optional
from .station import Station
from ..items.items import ItemRarity
from ..items.equipment import Equipment, EQUIPMENT_SLOTS
from ..accounts import loadAccount, saveAccount, Account
from ..styles import (
    console, clearScreen, printHeader, printSeparator,
    pause, printWarning, printError, printSuccess,
    checkGlobalCommand, createEquipmentStoragePages, stepPage
)

class AccountStash(Station):
    maxLevel = 1
    MIN_PLAYER_LEVEL_TO_ACCESS = 30

    def __init__(self, player):
        super().__init__(player, "Account Stash")

    def _getUpgradeRequirements(self):
        return {
            1: {"wood": 25, "stone": 25, "brick": 25, "metal": 25, "leather": 25, "cloth": 25, "paper": 25, "nail": 25, "soul": 50, "ascended_essence": 50,
                "description": "Unlocks the Account Stash. This is a shared equipment storage linked to your account, able to store infinite amounts of items useable on all characters linked to your account.\nYou can only withdraw equipment at or below your own level.\nYou must be level 30 to interact with the Account Stash."
            }
        }

    def _loadAccount(self) -> Optional[Account]:
        accountId = self.player._accountId
        if not accountId or accountId is None:
            printWarning(f"{self.player._name} has no account id.")
            return None
        account = loadAccount(accountId)
        if account is None:
            printError("Failed to load your account's stash.")
        return account

    def mainMenu(self):
        if self.level < 1:
            printWarning("Account Stash Level 1 Required.")
            pause()
            return
        if self.player._level < self.MIN_PLAYER_LEVEL_TO_ACCESS:
            printWarning(f"Must be level {self.MIN_PLAYER_LEVEL_TO_ACCESS} to interact with the Account Stash. Current Level: {self.player._level}")
            pause()
            return

        while True:
            clearScreen()
            printHeader("Account Stash")
            account = self._loadAccount()
            if account is None:
                pause()
                return
            
            console.print(f"[gold]Account:[/gold] {account.name}")
            console.print(f"[gold]Items Stored:[/gold] {len(account.stashedEquipment)}")
            printSeparator()
            console.print("[dim]0.[/dim] Return")
            console.print("[dim]1.[/dim] Deposit Equipment")
            console.print("[dim]2.[/dim] Withdraw Equipment")

            choice = console.input("[cyan]>[/cyan] ").strip()
            checkGlobalCommand(choice)

            try:
                choice = int(choice)
                match choice:
                    case 0:
                        return
                    case 1:
                        self.depositMenu(account)
                    case 2:
                        self.withdrawMenu(account)
                    case _:
                        printWarning(f"Invalid choice: {choice}")
            except ValueError:
                printError("Invalid input!")

    def depositMenu(self, account: Account):
        if not self.player._equipmentStorage:
            printWarning("No equipment in storage to deposit")
            pause()
            return

        currentPage = 1
        while True:
            clearScreen()
            printHeader("Deposit Equipment")
            pages = createEquipmentStoragePages(self.player._equipmentStorage)
            totalPages = len(pages)
            currentPage = min(currentPage, totalPages)
            console.print(f"[dim]Page {currentPage}/{totalPages}[/dim]")
            console.print(pages[currentPage])

            prompt = "\n[cyan]Choose Equipmen to deposit (0 to cancel)"
            if totalPages > 1:
                prompt += ", N for next page, P for previous page"
            prompt += "):\n> [/cyan]"
            choice = console.input(prompt).strip().lower()
            checkGlobalCommand(choice)

            newPage = stepPage(currentPage, totalPages, choice)
            if newPage is not None:
                currentPage = newPage
                continue

            try:
                index = int(choice) - 1
            except ValueError:
                printWarning("Invalid input!")
                return

            if index == -1:
                return

            if not (0 <= index < len(self.player._equipmentStorage)):
                printWarning("Invalid choice")
                continue

            equipment = self.player._equipmentStorage[index]
            console.print(f"\n[bold]Deposit {equipment.name} into the Account Stash? (y/n)[/bold]")
            confirm = console.input("[cyan]>[/cyan] ").strip().lower()
            if confirm == 'y':
                self.player.removeEquipmentFromStorage(equipment=equipment)
                account.stashedEquipment.append(equipment)
                saveAccount(account)
                printSuccess(f"\nDeposited {equipment.name}.")
                pause()
            return

    def withdrawMenu(self, account: Account):
        if not account.stashedEquipment:
            printWarning("The Account Stash is empty.")
            pause()
            return

        rarityFilter: Optional[ItemRarity] = None
        slotFilter: Optional[str] = None
        currentPage = 1

        while True:
            filtered = [
                e for e in account.stashedEquipment
                if (rarityFilter is None or e.rarity == rarityFilter)
                and (slotFilter is None or e.slot == slotFilter)
            ]

            clearScreen()
            printHeader("Withdraw Equipment")
            filterStr = []
            if rarityFilter:
                filterStr.append(f"Rarity: {rarityFilter.value.title()}")
            if slotFilter:
                filterStr.append(f"Slot: {slotFilter.title()}")
            if filterStr:
                console.print(f"[dim]Filters: {' | '.join(filterStr)}[/dim]\n")

            totalPages = 1
            if filtered:
                pages = createEquipmentStoragePages(filtered)
                totalPages = len(pages)
                currentPage = min(currentPage, totalPages)
                console.print(f"[dim]Page {currentPage}/{totalPages}[/dim]")
                console.print(pages[currentPage])
            else:
                printWarning("No items match the current filters")

            console.print("\n[cyan]Options:[/cyan]")
            console.print("  [dim]#.[/dim] Withdraw item number")
            console.print("  [dim]R.[/dim] Filter by Rarity")
            console.print("  [dim]S.[/dim] Filter by Slot")
            console.print("  [dim]C.[/dim] Clear Filters")
            if totalPages > 1:
                console.print("  [dim]N.[/dim] Next Page")
                console.print("  [dim]P.[/dim] Previous Page")
            console.print("  [dim]0.[/dim] Return")

            choice = console.input("\n[cyan]>[/cyan] ").strip().lower()
            checkGlobalCommand(choice)

            newPage = stepPage(currentPage, totalPages, choice)
            if newPage is not None:
                currentPage = newPage
                continue

            if choice == '0' or choice == '':
                return
            elif choice == 'r':
                rarityFilter = self._pickRarity()
                currentPage = 1
            elif choice == 's':
                slotFilter = self._pickSlot()
                currentPage = 1
            elif choice == 'c':
                rarityFilter = None
                slotFilter = None
                currentPage = 1
            else:
                try:
                    index = int(choice) - 1
                except ValueError:
                    printWarning("Invalid input!")
                    pause()
                    continue

                if not (0 <= index < len(filtered)):
                    printWarning("Invalid choice")
                    pause()
                    continue

                equipment = filtered[index]
                if equipment.level > self.player._level:
                    printWarning(f"You must be level {equipment.level} to withdraw this item. Current Level: {self.player._level}")
                    pause()
                    continue

                console.print(f"\n[bold]Withdraw {equipment.name}? (y/n)[/bold]")
                confirm = console.input("[cyan]>[/cyan] ").strip().lower()
                if confirm == 'y':
                    account.stashedEquipment.remove(equipment)
                    saveAccount(account)
                    self.player.addEquipmentToStorage(equipment)
                    printSuccess(f"\nWithdrew {equipment.name} from Account Stash.")
                    pause()
                return

    def _pickRarity(self) -> Optional[ItemRarity]:
        clearScreen()
        printHeader("Filter by Rarity")
        rarities = list(ItemRarity)
        console.print(f"[dim]0.[/dim] Any Rarity")
        for i, r in enumerate(rarities, 1):
            console.print(f"[dim]{i}.[/dim] {r.value.title()}")
        choice = console.input("\n[cyan]>[/cyan] ").strip()
        try:
            index = int(choice) - 1
            if 0 <= index < len(rarities):
                return rarities[index]
        except ValueError:
            pass
        return None

    def _pickSlot(self) -> Optional[str]:
        clearScreen()
        printHeader("Filter by Slot")
        console.print("[dim]0.[/dim] Any Slot")
        for i, slot in enumerate(EQUIPMENT_SLOTS, 1):
            console.print(f"[dim]{i}.[/dim] {slot.title()}")
        choice = console.input("\n[cyan]>[/cyan] ").strip()
        try:
            index = int(choice) - 1
            if 0 <= index < len(EQUIPMENT_SLOTS):
                return EQUIPMENT_SLOTS[index]
        except ValueError:
            pass
        return None

