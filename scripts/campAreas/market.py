from typing import Optional, Dict
import random
import datetime
from .station import Station
from scripts.items import Equipment, ItemRarity, RESOURCES, CONSUMABLES
from scripts.styles import (
    console, clearScreen, printHeader, printSeparator,
    pause, printWarning, printError, printSuccess, printInfo, checkGlobalCommand
)

class Market(Station):
    # Buy/sell items and equipment
    # Higher levels: better prices, more stock, rare items
    def __init__(self, player):
        super().__init__(player, "Market")
        self.tradeVouchers = 0
        self.stock: Dict[str, tuple[int, int, Optional[Equipment]]] = {}
        self.lastRestock = None
        self._generateStock()

    def _getUpgradeRequirements(self) -> Dict[int, Dict[str, int]]:
        return {
            1: {"wood": 50, "stone": 50, "iron_ore": 10, "leather": 20,
                'description': "Enemies will begin to drop [resource]Trade Vouchers[/resource].\n[resource]Trade Vouchers[/resource] are used to restock the Market's inventory.\nThe market can stock Common and Uncommon equipment."
                },
            2: {"iron_ore": 50, "leather": 50, "cloth": 50, "bone": 25,
                'description': "The market can now stock Rare resources. The market stocks an additional 2 pieces of Equipment. The market can stock Rare equipment."
                },
            3: {"crystal": 25, "bone": 50, "soul": 25,
                'description': "The market stocks an additional 2 pieces of Equipment. The market can stock Epic equipment. The market no longer stocks Common equipment."
                },
            4: {"mana_essence": 40, "diamond": 20, "soul": 50,
                'description': "The market can now stock Epic resources. The market stocks an additional 2 pieces of Equipment. The market can stock Legendary equipment. The market no longer stocks Uncommon equipment."
                },
            5: {"dragon_scale": 15, "ascended_essence": 10, "diamond": 25,
                'description': "The market stocks an additional 2 pieces of Equipment. The market is less likely to stock Rare equipment."
                }
        }

    def _serialise(self):
        temp = super()._serialise()
        temp['tradeVouchers'] = self.tradeVouchers
        stock = {}
        for item, data in self.stock.items():
            if len(data) == 3:
                stock[item] = {
                    'amount': data[0],
                    'value': data[1],
                    'item': data[2].serialise()
                }
            else:
                stock[item] = {
                    'amount': data[0],
                    'value': data[1]
                }
        temp['stock'] = stock
        temp['lastRestock'] = self.lastRestock.isoformat() if self.lastRestock else None
        return temp
    
    def _deserialiseStock(self, data):
        self.stock = {}
        for name, itemData in data.items():
            if len(itemData) == 3: # equipment
                e = Equipment.deserialise(itemData['item'])
                itemData['item'] = e
                self.stock[name] = tuple(itemData.values())
            else:
                self.stock[name] = tuple(itemData.values())

    def _generateStock(self):
        self.stock = {}
        # resources
        resourceCount = 3 + self.level
        availableResources = list(RESOURCES.keys())
        if self.level < 2:
            availableResources = [r for r in availableResources
                                  if RESOURCES[r].rarity.value in ['common', 'uncommon']]
        elif self.level < 4:
            availableResources = [r for r in availableResources
                                  if RESOURCES[r].rarity.value in ['common', 'uncommon', 'rare']]
        else: # level 4/5
            availableResources = [r for r in availableResources
                                  if RESOURCES[r].rarity.value in ['common', 'uncommon', 'rare', 'epic']]
        selectedResources = random.sample(availableResources, min(len(availableResources), resourceCount))
        for resource in selectedResources:
            quantity = random.randint(10 + self.level * 4, 30 + self.level * 10)
            basePrice = RESOURCES[resource].value * 8
            self.stock[resource] = (quantity, basePrice)
        # equipment
        equipmentCount = 2 * self.level + random.randint(1, 3)
        for _ in range(equipmentCount):
            equipLevel = self.player._level + random.randint(1, 1 + self.level * 3)
            slot = random.choice(['weapon', 'head', 'chest', 'legs', 'feet', 'ring', 'amulet'])
            rarityChances = {
                1: [ItemRarity.COMMON, ItemRarity.COMMON, ItemRarity.UNCOMMON],
                2: [ItemRarity.COMMON, ItemRarity.COMMON, ItemRarity.UNCOMMON, ItemRarity.UNCOMMON, ItemRarity.RARE],
                3: [ItemRarity.UNCOMMON, ItemRarity.UNCOMMON, ItemRarity.UNCOMMON, ItemRarity.RARE, ItemRarity.RARE, ItemRarity.EPIC],
                4: [ItemRarity.RARE, ItemRarity.RARE, ItemRarity.RARE, ItemRarity.RARE, ItemRarity.EPIC, ItemRarity.EPIC, ItemRarity.LEGENDARY],
                5: [ItemRarity.RARE, ItemRarity.RARE, ItemRarity.EPIC, ItemRarity.EPIC, ItemRarity.EPIC, ItemRarity.LEGENDARY]
            }
            possibleRarities = rarityChances.get(self.level, [ItemRarity.COMMON, ItemRarity.UNCOMMON])
            rarity = random.choice(possibleRarities)
            equipment = Equipment._generateEquipmentPiece(equipLevel, slot, rarity, className=self.player.className)
            price = int((random.uniform(1, 3) * equipment.value * 5) + 1000)
            price = int(equipment.value * random.uniform(1, 3))
            self.stock[equipment.name] = (1, price, equipment)
        # consumables
        if self.level >= 2:
            consumableCount = 1 + self.level
            for potion in list(CONSUMABLES.keys())[:consumableCount]:
                quantity = random.randint(2, 10)
                price = CONSUMABLES[potion] * 50
                self.stock[potion] = (quantity, price)

        self.lastRestock = datetime.datetime.now()

    def checkRestock(self):
        if not self.lastRestock:
            self._generateStock()
            return
        timeSinceRestock = datetime.datetime.now() - self.lastRestock
        if timeSinceRestock.total_seconds() >= 3600: #1 hour
            printInfo("\n[Market has been restocked!]")
            self._generateStock()

    def forceRestock(self):
        if self.level < 1:
            printWarning(f"Market Level 1 required to force restock. Current level: {self.level}")
            pause()
            return
        cost = self.level * 5
        console.print(f"\n[bold]Force Market Restock for {cost} Trade Vouchers?[/bold]")
        confirm = console.input("\n[cyan]Confirm? (y/n):\n> [/cyan]").strip().lower()
        if confirm == 'y':
            if self.tradeVouchers >= cost:
                self.tradeVouchers -= cost
                self._generateStock()
                printSuccess("\nMarket Restocked!")
            else:
                printWarning("Insufficient trade vouchers.")
        pause()
    
    def mainMenu(self):
        while True:
            self.checkRestock()
            clearScreen()
            printHeader(f"Market - Level {self.level}")
            console.print(f"[gold]Trade Vouchers:[/gold] {self.tradeVouchers}")
            console.print(f"[gold]Gold:[/gold] {self.player._gold}")
            printSeparator()
            console.print("[dim]0.[/dim] Return")
            console.print("[dim]1.[/dim] Buy Items")
            console.print("[dim]2.[/dim] Sell Items")
            if self.level >= 1:
                console.print("[dim]3.[/dim] Force Restock")
            console.print("[dim]9.[/dim] Upgrade Market")
            
            choice = console.input("\n[cyan]>[/cyan] ").strip()
            checkGlobalCommand(choice)

            try:
                choice = int(choice)
                match choice:
                    case 0:
                        return
                    case 1:
                        self.buyItems()
                    case 2:
                        self.sellItems()
                    case 3:
                        if self.level >= 1:
                            self.forceRestock()
                    case 9:
                        self.upgrade()
                    case _:
                        printWarning(f"Invalid choice: {choice}")
                        pause()
            except ValueError:
                printError("Invalid input!")
                pause()

    def buyItems(self):
        clearScreen()
        printHeader("Buy Items")
        console.print(f"[gold]Your Gold: {self.player._gold}[/gold]\n")
        
        if not self.stock:
            printWarning("Market is empty!")
            pause()
            return
        
        console.print("[gold]Available items:[/gold]")
        stockList = list(self.stock.items())
        for i, (itemName, itemData) in enumerate(stockList, 1):
            if len(itemData) == 3:  # equipment
                quantity, price, equipment = itemData
                console.print(f"  [cyan]{i}.[/cyan] {itemName} - [dim]{price}g/each[/dim]")
                console.print(f"     [dim]{equipment}[/dim]")
            else:  # resource or consumable
                quantity, price = itemData
                console.print(f"  [cyan]{i}.[/cyan] {itemName} x{quantity} - [dim]{price}g/each[/dim]")

        choice = console.input("\n[cyan]Choose item to buy (0 to cancel):\n> [/cyan]").strip()
        try:
            index = int(choice) - 1
            if 0 <= index < len(stockList):
                itemName, itemData = stockList[index]
                
                if len(itemData) == 3:
                    quantity, price, equipment = itemData
                else:
                    quantity, price = itemData
                    equipment = None
                
                if not equipment:
                    amount = console.input(f"[bold]How many? (max {quantity}):[/bold]\n[cyan]> [/cyan]").strip()
                    amount = int(amount)
                else:
                    amount = 1
                
                if amount <= 0 or amount > quantity:
                    printWarning("Invalid amount!")
                    pause()
                    return
                
                cost = price * amount
                if self.player._gold >= cost:
                    self.player._gold -= cost

                    if equipment:
                        for _ in range(amount):
                            self.player.addEquipmentToStorage(itemData[2])
                    else:
                        self.player.addItem(itemName, amount)

                    if len(itemData) == 3:
                        new_quantity = quantity - amount
                        if new_quantity > 0:
                            self.stock[itemName] = (new_quantity, price, equipment)
                        else:
                            del self.stock[itemName]
                    else:
                        new_quantity = quantity - amount
                        if new_quantity > 0:
                            self.stock[itemName] = (new_quantity, price)
                        else:
                            del self.stock[itemName]
                    
                    printSuccess(f"\nPurchased {amount}x {itemName} for {cost}g!")
                else:
                    printWarning(f"\nNeed {cost}g! (Current: {self.player._gold}g)")
        except ValueError:
            printError("Invalid input!")
        pause()

    def sellItems(self):
        clearScreen()
        printHeader("Sell Items")
        console.print("\n[bold]What would you like to sell?[/bold]")
        console.print("[cyan]1. Resources[/cyan]")
        console.print("[red1]2. Equipment[/red1]")
        console.print("[dim]0. Cancel[/dim]")
        choice = console.input("\n> ").strip()

        try:
            choice = int(choice)
            if choice == 1:
                self._sellResources()
            elif choice == 2:
                self._sellEquipment()
        except ValueError as e:
            printError(f"[ERROR] {e}")
        pause()

    def _sellResources(self):
        if not self.player._inventory:
            printWarning("No resources to sell.")
            pause()
            return
        console.print("\n[bold]Your resources:[/bold]")
        resourceList = list(self.player._inventory.items())
        for i, (resource, quantity) in enumerate(resourceList, 1):
            if resource in RESOURCES:
                value = RESOURCES[resource].value
                console.print(f"  [cyan]{i}.[/cyan] {resource} x{quantity} - [dim]{value}g/each[/dim]")
        choice = console.input("\n[cyan]Choose resource to sell (0 to cancel):\n> [/cyan]").strip()
        try:
            index = int(choice) - 1
            if 0 <= index < len(resourceList):
                resource, quantity = resourceList[index]
                
                if resource not in RESOURCES:
                    printWarning("Cannot sell this item!")
                    pause()
                    return
                
                amount = console.input(f"[bold]How many? (max {quantity}):[/bold]\n[cyan]> [/cyan]").strip()
                amount = int(amount)
                
                if amount <= 0 or amount > quantity:
                    printWarning("Invalid amount!")
                    pause()
                    return
                value = RESOURCES[resource].value
                totalValue = value * amount
                self.player.removeItem(resource, amount)
                self.player.gainGold(totalValue)
        except ValueError:
            pass
        pause()
    
    def _sellEquipment(self):
        allEq = []
        for i, equip in enumerate(self.player._equipmentStorage):
            allEq.append((f"[STORAGE] #{i+1}", equip))
        if not allEq:
            printWarning("\nNo Equipment to sell.")
            pause()
            return
        console.print("\n[gold]Your Equipment:[/gold]")
        for i, (location, equip) in enumerate(allEq, 1):
            value = equip.value
            console.print(f"  [cyan]{i}.[/cyan] {location} {equip.name} - [gold]{value}g[/gold]")
        choice = console.input("\n[cyan]Choose equipment to sell (0 to cancel):[/cyan]\n[dim red]'all' to sell everything in inventory (exlcuding epic and legendary) | 'all2' to sell EVERYTHING[/dim red]:\n> ").strip()
        if choice.lower() == 'all':
            totalValue = 0
            for _, equip in allEq:
                if equip.rarity.value not in ['epic', 'legendary']:
                    totalValue += min(5000, max(100, equip.value // 10))
            confirm = console.input(f"\n[bold]Sell all items in equipment inventory for {totalValue}g? (y/n):\n> ").strip().lower()
            if confirm == 'y':
                self.player._gold += totalValue
                self.player._equipmentStorage = [e for e in self.player._equipmentStorage if e.rarity.value in ['epic', 'legendary', 'unqiue']]
                printSuccess(f"\nSold all items in inventory for {totalValue}g!")
        elif choice.lower() == 'all2':
            totalValue = 0
            for _, equip in allEq:
                totalValue += min(5000, max(100, equip.value // 10))
            confirm = console.input(f"\n[bold]Sell ALL items in equipment inventory for {totalValue}g? (y/n):\n> ").strip().lower()
            if confirm == 'y':
                self.player._gold += totalValue
                self.player._equipmentStorage = []
                printSuccess(f"\nSold ALL items in equipment inventory for {totalValue}g!")
        try:
            index = int(choice) - 1
            if 0 <= index < len(allEq):
                location, equip = allEq[index]
                
                confirm = console.input(f"\n[bold]Sell {equip.name} for {equip.value}g? (y/n):[/bold]\n[cyan]> [/cyan]").strip().lower()
                if confirm == 'y':
                    # Remove from storage
                    self.player._equipmentStorage.remove(equip)
                    self.player.gainGold(equip.value)
                    
                    printSuccess(f"\nSold {equip.name} for {equip.value}g!")
        except ValueError:
            pass
        pause()
