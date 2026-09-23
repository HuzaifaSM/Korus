from typing import Optional, Dict
import random
import datetime
from .station import Station
from ..items.items import ItemRarity, RESOURCES, RARITY_SERIALS
from ..items.equipment import Equipment
from ..styles import (
    console, clearScreen, printHeader, printSeparator,
    pause, printWarning, printError, printSuccess, printInfo, checkGlobalCommand
)
from ..runeDrops import rollGuaranteedRunes, getRuneObject, getRuneDetails, calculateRunePrice
from ..difficulty import getActiveDifficulty

class Market(Station):
    # Buy/sell items and equipment
    # Higher levels: better prices, more stock, rare items
    EQUIPMENT_RARITY_CHANCES = {
        1: [ItemRarity.COMMON, ItemRarity.COMMON, ItemRarity.UNCOMMON],
        2: [ItemRarity.COMMON, ItemRarity.COMMON, ItemRarity.UNCOMMON, ItemRarity.UNCOMMON, ItemRarity.RARE],
        3: [ItemRarity.UNCOMMON, ItemRarity.UNCOMMON, ItemRarity.UNCOMMON, ItemRarity.RARE, ItemRarity.RARE, ItemRarity.EPIC],
        4: [ItemRarity.RARE, ItemRarity.RARE, ItemRarity.RARE, ItemRarity.RARE, ItemRarity.EPIC, ItemRarity.EPIC, ItemRarity.LEGENDARY],
        5: [ItemRarity.RARE, ItemRarity.RARE, ItemRarity.EPIC, ItemRarity.EPIC, ItemRarity.EPIC, ItemRarity.LEGENDARY]
    }
    EQUIPMENT_SLOTS = ['weapon', 'head', 'chest', 'legs', 'feet', 'ring', 'amulet', 'offhand', 'sigil']

    HAGGLE_DISCOUNT_RANGE = (0.10, 0.35)
    COMMISSION_VOUCHER_COST_PER_LEVEL = 8
    COMMISSION_GOLD_COST_PER_LEVEL = 200

    BLACK_MARKET_RARITY_FLOOR = {
        4: ['rare', 'epic', 'legendary'],
        5: ['epic', 'legendary'],
    }
    BLACK_MARKET_BONUS_RARITY_MIN_PLAYER_LEVEL = 60
    BLACK_MARKET_MARKET_AFFIX_CHANCE = {4: 0.65, 5: 0.80}
    BLACK_MARKET_TIER_BOOST = {4: 1, 5: 2}
    BLACK_MARKET_RUNE_VALUE_NEEDED = {4: 60, 5: 100}
    BLACK_MARKET_RUNE_WEIGHT_RANGE = (15, 150)

    def __init__(self, player):
        super().__init__(player, "Market")
        self.tradeVouchers = 0
        self.stock: Dict[str, tuple[int, int, Optional[Equipment]]] = {}
        self.blackMarketStock: Dict[str, tuple[int, int, Equipment]] = {}
        self.recentlySold: list[tuple[Equipment, int]] = []
        self.commission: Optional[str] = None
        self.haggledItems: set[str] = set()
        self.lastRestock = None
        self._generateStock()

    def _getUpgradeRequirements(self) -> Dict[int, Dict[str, int]]:
        return {
            1: {"leather": 10, "cloth": 5,
                'description': "Enemies will begin to drop [resource]Trade Vouchers[/resource].\n[resource]Trade Vouchers[/resource] are used to restock the Market's inventory, and to haggle down or commission equipment.\nThe market can stock Common and Uncommon equipment.\nThe market can stock [resource]crafting runes[/resource] up to the player's current level.\nYou can now use Resource Conversion to swap between resource types.\nBuyback of recently sold equipment is now available."
                },
            2: {"leather": 15, "cloth": 10,
                'description': "The market stocks more resources. The market stocks an additional 2 pieces of Equipment. The market can stock Rare equipment. The market stocks more crafting runes.\nYou can now place a Special Commission to guarantee a chosen equipment slot at the next restock, rolled a rarity tier higher than normal."
                },
            3: {"leather": 30, "cloth": 20,
                'description': "The market stocks more resources The market stocks an additional 2 pieces of Equipment. The market can stock Epic equipment. The market no longer stocks Common equipment. The market cannot stock crafting runes below level 15."
                },
            4: {"leather": 50, "cloth": 30,
                'description': "The market stocks more resources. The market stocks an additional 2 pieces of Equipment. The market can stock Legendary equipment. The market no longer stocks Uncommon equipment. The market stocks more crafting runes.\nA Black Market opens, selling 3 pieces of Rare+ equipment with a much higher chance of unique market affixes, paid for in gold and runes."
                },
            5: {"leather": 75, "cloth": 50,
                'description': "The market stocks more resources The market stocks an additional 2 pieces of Equipment. The market is less likely to stock Rare equipment. The market cannot stock crafting runes below level 30. The market stocks more crafting runes\nThe Black Market now sells 5 pieces of Epic+ equipment, with an even higher chance of unique market affixes. If the player is above level 60, the Black Market can also stock Mythic and Blank rarity items."
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

        blackMarket = {}
        for name, (goldPrice, runeValueNeeded, equipment) in self.blackMarketStock.items():
            blackMarket[name] = {
                'goldPrice': goldPrice,
                'runeValueNeeded': runeValueNeeded,
                'item': equipment.serialise()
            }
        temp['blackMarketStock'] = blackMarket

        temp['recentlySold'] = [
            {'item': equip.serialise(), 'price': price} for equip, price in self.recentlySold
        ]
        temp['commission'] = self.commission
        temp['haggledItems'] = list(self.haggledItems)
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

    def _deserialiseBlackMarketStock(self, data):
        self.blackMarketStock = {}
        for name, itemData in data.items():
            e = Equipment.deserialise(itemData['item'])
            self.blackMarketStock[name] = (itemData['goldPrice'], itemData['runeValueNeeded'], e)

    def _deserialiseRecentlySold(self, data):
        self.recentlySold = [(Equipment.deserialise(d['item']), d['price']) for d in data]

    def _bumpRarityTier(self, rarity: ItemRarity) -> ItemRarity:
        if rarity.value in ('mythic', 'blank', 'quest'):
            return rarity
        bumped = rarity + 1
        if bumped.value in ('mythic', 'blank'):
            return ItemRarity.LEGENDARY
        return bumped

    def _generateStock(self):
        self.stock = {}
        self.haggledItems = set()
        self.recentlySold = []

        economyMultiplier = getActiveDifficulty().getEconomyMultiplier()

        # resources
        resourceCount = 3 + self.level
        availableResources = list(RESOURCES.keys())
        selectedResources = random.sample(availableResources, min(len(availableResources), resourceCount))
        for resource in selectedResources:
            quantity = random.randint(10 + self.level * 4, 30 + self.level * 10)
            price = max(1, round(RESOURCES[resource].value * economyMultiplier))
            self.stock[resource] = (quantity, price)

        # equipment
        equipmentCount = 2 * self.level + random.randint(1, 3)
        for _ in range(equipmentCount):
            equipLevel = self.player._level + random.randint(1, 1 + self.level * 3)
            slot = random.choice(self.EQUIPMENT_SLOTS)
            possibleRarities = self.EQUIPMENT_RARITY_CHANCES.get(self.level, [ItemRarity.COMMON, ItemRarity.UNCOMMON])
            rarity = random.choice(possibleRarities)
            equipment = Equipment._generateEquipmentPiece(equipLevel, slot, rarity, self.player.className, self.player._name, market=True)
            price = int(((random.uniform(1, 5) * equipment.value) * (1 + equipLevel // 10) + 1000) * economyMultiplier)
            self.stock[equipment.name] = (1, price, equipment)

        # special commission fulfilment: one guaranteed extra item, rarity bumped up a tier
        if self.commission:
            equipLevel = self.player._level + random.randint(1, 1 + self.level * 3)
            possibleRarities = self.EQUIPMENT_RARITY_CHANCES.get(self.level, [ItemRarity.COMMON, ItemRarity.UNCOMMON])
            rolledRarity = self._bumpRarityTier(random.choice(possibleRarities))
            equipment = Equipment._generateEquipmentPiece(equipLevel, self.commission, rolledRarity, self.player.className, self.player._name, market=True)
            price = int(((random.uniform(1, 5) * equipment.value) * (1 + equipLevel // 10) + 1000) * economyMultiplier)
            self.stock[equipment.name] = (1, price, equipment)
            self.commission = None

        # runes
        if self.level > 0:
            runesStock = {}
            runeCount = 3 * self.level + random.randint(1, 4)
            runeMinLevel = 0 if self.level < 3 else (15 if self.level < 5 else 30)
            runes = rollGuaranteedRunes(self.player._level, runeCount, runeMinLevel)
            for runeCat, runeType in runes:
                rune = getRuneObject(runeCat, runeType)
                runesStock[rune] = runesStock.get(rune, 0) + 1
            for rune, quantity in runesStock.items():
                price = max(1, round(calculateRunePrice(rune) * economyMultiplier))
                self.stock[rune] = (quantity, price)

        # black market
        self.blackMarketStock = {}
        if self.level >= 4:
            bmCount = 5 if self.level == 5 else 3
            rarityPool = list(self.BLACK_MARKET_RARITY_FLOOR[self.level])
            if self.level == 5 and self.player._level > self.BLACK_MARKET_BONUS_RARITY_MIN_PLAYER_LEVEL:
                rarityPool += ['mythic', 'blank']
            marketAffixChance = self.BLACK_MARKET_MARKET_AFFIX_CHANCE[self.level]
            tierBoost = self.BLACK_MARKET_TIER_BOOST[self.level]
            runeValueNeeded = self.BLACK_MARKET_RUNE_VALUE_NEEDED[self.level]

            for _ in range(bmCount):
                equipLevel = self.player._level + random.randint(1, 1 + self.level * 3)
                slot = random.choice(self.EQUIPMENT_SLOTS)
                rarityStr = random.choice(rarityPool)
                if rarityStr == 'blank':
                    equipment = Equipment._generateBlankEquipmentPiece(equipLevel, slot, self.player.className, self.player._name)
                else:
                    rarity = RARITY_SERIALS[rarityStr]
                    equipment = Equipment._generateEquipmentPiece(
                        equipLevel, slot, rarity, self.player.className, self.player._name,
                        market=True, marketAffixChance=marketAffixChance, nonMarketTierBoost=tierBoost
                    )
                goldPrice = int(((random.uniform(2, 6) * equipment.value) * (1 + equipLevel // 10) + 2000) * economyMultiplier)
                self.blackMarketStock[equipment.name] = (goldPrice, runeValueNeeded, equipment)

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
                console.print("[dim]4.[/dim] Resource Conversion")
            if self.level >= 2:
                console.print("[dim]5.[/dim] Special Commission")
            if self.level >= 4:
                console.print("[dim]6.[/dim] Black Market")
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
                    case 4:
                        if self.level >= 1:
                            self.resourceConversion()
                    case 5:
                        if self.level >= 2:
                            self.commissionItem()
                    case 6:
                        if self.level >= 4:
                            self.blackMarketMenu()
                    case 9:
                        self.upgrade()
                    case _:
                        printWarning(f"Invalid choice: {choice}")
                        pause()
            except ValueError:
                printError("Invalid input!")
                pause()

    def buyItems(self):
        while True:
            clearScreen()
            printHeader("Buy Items")
            console.print(f"[gold]Your Gold: {self.player._gold}[/gold]")
            if self.level >= 1:
                console.print(f"[gold]Trade Vouchers: {self.tradeVouchers}[/gold]")
            console.print("")

            if not self.stock:
                printWarning("Market is empty!")
                pause()
                return

            console.print("[gold]Available items:[/gold]")
            stockList = list(self.stock.items())
            for i, (item, itemData) in enumerate(stockList, 1):
                if len(itemData) == 3:  # equipment
                    quantity, price, equipment = itemData
                    haggledTag = " [dim](haggled)[/dim]" if item in self.haggledItems else ""
                    console.print(f"  [cyan]{i}.[/cyan] [dim]{price}g{haggledTag}\n{equipment}")
                else:
                    quantity, price = itemData
                    if type(item) is str: # resources
                        console.print(f"  [cyan]{i}.[/cyan] {item.title()} x{quantity} - [dim]{price}g/each[/dim]")
                    else: # runes
                        console.print(f"  [cyan]{i}.[/cyan] {item.name} x{quantity} - [dim]{price}g/each[/dim]")

            prompt = "\n[cyan]Choose item to buy (0 to cancel"
            if self.level >= 1:
                prompt += ", 'h<#>' to haggle a piece of equipment's price down"
            prompt += "):\n> [/cyan]"
            choice = console.input(prompt).strip()
            try:
                if choice == '0':
                    return

                if self.level >= 1 and choice.lower().startswith('h') and choice[1:].strip().lstrip('-').isdigit():
                    index = int(choice[1:].strip()) - 1
                    self._haggleItem(index, stockList)
                    continue

                index = int(choice) - 1
                if 0 <= index < len(stockList):
                    item, itemData = stockList[index]

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
                            self.player.addItem(item, amount)

                        if len(itemData) == 3:
                            new_quantity = quantity - amount
                            if new_quantity > 0:
                                self.stock[item] = (new_quantity, price, equipment)
                            else:
                                del self.stock[item]
                        else:
                            if type(item) is str:
                                new_quantity = quantity - amount
                                if new_quantity > 0:
                                    self.stock[item] = (new_quantity, price)
                                else:
                                    del self.stock[item]
                            else:
                                runeCat, runeType = getRuneDetails(item)
                                self.player.addRune(runeCat, runeType, doPrint=False)

                        printSuccess(f"\nPurchased {amount}x {item} for {cost}g!")
                    else:
                        printWarning(f"\nNeed {cost}g! (Current: {self.player._gold}g)")
            except ValueError:
                printError("Invalid input!")
            pause()

    def _haggleItem(self, index: int, stockList: list):
        if index < 0 or index >= len(stockList):
            printWarning("Invalid choice")
            pause()
            return

        key, itemData = stockList[index]
        if len(itemData) != 3:
            printWarning("You can only haggle over equipment.")
            pause()
            return

        if key in self.haggledItems:
            printWarning("You've already haggled over this item's price.")
            pause()
            return

        cost = 2 + self.level
        if self.tradeVouchers < cost:
            printWarning(f"Need {cost} Trade Vouchers to haggle! (Current: {self.tradeVouchers})")
            pause()
            return

        quantity, price, equipment = itemData
        console.print(f"\n[bold]Spend {cost} Trade Vouchers to haggle over {equipment.name}'s price? (y/n)[/bold]")
        confirm = console.input("[cyan]> [/cyan]").strip().lower()
        if confirm != 'y':
            return

        self.tradeVouchers -= cost
        discount = random.uniform(*self.HAGGLE_DISCOUNT_RANGE)
        newPrice = max(1, int(price * (1 - discount)))
        self.stock[key] = (quantity, newPrice, equipment)
        self.haggledItems.add(key)
        printSuccess(f"\nHaggled {equipment.name} down to {newPrice}g! ({discount * 100:.0f}% off)")
        pause()

    def resourceConversion(self):
        if self.level < 1:
            printWarning(f"Market Level 1 required for Resource Conversion. Current Level: {self.level}")
            pause()
            return

        tradeable = [name for name, res in RESOURCES.items() if res.use != 'Player']

        clearScreen()
        printHeader("Resource Conversion")
        console.print("[dim]Convert any resource into an equal amount of another, for a small gold fee.[/dim]\n")

        ownedTradeable = [(r, self.player._inventory.get(r, 0)) for r in tradeable if self.player._inventory.get(r, 0) > 0]
        if not ownedTradeable:
            printWarning("You have no tradeable resources.")
            pause()
            return

        console.print("[gold]Your resources:[/gold]")
        for i, (r, qty) in enumerate(ownedTradeable, 1):
            console.print(f"  [cyan]{i}.[/cyan] {r.title()} x{qty}")

        choice = console.input("\n[cyan]Convert which resource? (0 to cancel):\n> [/cyan]").strip()
        try:
            index = int(choice) - 1
        except ValueError:
            printError("Invalid input!")
            pause()
            return
        if index == -1:
            return
        if not (0 <= index < len(ownedTradeable)):
            printWarning("Invalid choice")
            pause()
            return
        fromResource, available = ownedTradeable[index]

        otherResources = [r for r in tradeable if r != fromResource]
        console.print(f"\n[gold]Convert {fromResource.title()} into:[/gold]")
        for i, r in enumerate(otherResources, 1):
            console.print(f"  [cyan]{i}.[/cyan] {r.title()}")

        choice = console.input("\n[cyan]Convert into which resource? (0 to cancel):\n> [/cyan]").strip()
        try:
            index = int(choice) - 1
        except ValueError:
            printError("Invalid input!")
            pause()
            return
        if index == -1:
            return
        if not (0 <= index < len(otherResources)):
            printWarning("Invalid choice")
            pause()
            return
        toResource = otherResources[index]

        amount = console.input(f"\n[bold]How many {fromResource.title()} to convert? (max {available}):[/bold]\n[cyan]> [/cyan]").strip()
        try:
            amount = int(amount)
        except ValueError:
            printError("Invalid input!")
            pause()
            return
        if amount <= 0 or amount > available:
            printWarning("Invalid amount!")
            pause()
            return

        fee = max(5, amount * 2)
        console.print(f"\n[bold]Convert {amount}x {fromResource.title()} into {amount}x {toResource.title()} for {fee}g? (y/n)[/bold]")
        confirm = console.input("[cyan]> [/cyan]").strip().lower()
        if confirm == 'y':
            if self.player._gold < fee:
                printWarning(f"Need {fee}g! (Current: {self.player._gold}g)")
                pause()
                return
            self.player._gold -= fee
            self.player.removeItem(fromResource, amount)
            self.player.addItem(toResource, amount)
            printSuccess(f"\nConverted {amount}x {fromResource.title()} into {amount}x {toResource.title()}!")
        pause()

    def commissionItem(self):
        if self.level < 2:
            printWarning(f"Market Level 2 required for Special Commission. Current Level: {self.level}")
            pause()
            return

        if self.commission:
            printWarning(f"You already have an active commission for {self.commission.title()}. It will be fulfilled on the next restock.")
            pause()
            return

        clearScreen()
        printHeader("Special Commission")
        console.print("[dim]Guarantee a specific equipment slot appears at the next restock, rolled one rarity tier higher than normal (never Mythic/Blank).[/dim]\n")
        for i, slot in enumerate(self.EQUIPMENT_SLOTS, 1):
            console.print(f"  [cyan]{i}.[/cyan] {slot.title()}")

        choice = console.input("\n[cyan]Commission which slot? (0 to cancel):\n> [/cyan]").strip()
        try:
            index = int(choice) - 1
        except ValueError:
            printError("Invalid input!")
            pause()
            return
        if index == -1:
            return
        if not (0 <= index < len(self.EQUIPMENT_SLOTS)):
            printWarning("Invalid choice")
            pause()
            return
        slot = self.EQUIPMENT_SLOTS[index]

        voucherCost = self.COMMISSION_VOUCHER_COST_PER_LEVEL * self.level
        goldCost = self.COMMISSION_GOLD_COST_PER_LEVEL * self.level

        console.print(f"\n[bold]Commission a {slot.title()} for {voucherCost} Trade Vouchers and {goldCost}g? (y/n)[/bold]")
        confirm = console.input("[cyan]> [/cyan]").strip().lower()
        if confirm == 'y':
            if self.tradeVouchers < voucherCost:
                printWarning(f"Need {voucherCost} Trade Vouchers! (Current: {self.tradeVouchers})")
            elif self.player._gold < goldCost:
                printWarning(f"Need {goldCost}g! (Current: {self.player._gold}g)")
            else:
                self.tradeVouchers -= voucherCost
                self.player._gold -= goldCost
                self.commission = slot
                printSuccess(f"\nCommissioned a {slot.title()}! It will appear at the next restock.")
        pause()

    def blackMarketMenu(self):
        if self.level < 4:
            printWarning(f"Market Level 4 required for the Black Market. Current Level: {self.level}")
            pause()
            return

        while True:
            clearScreen()
            printHeader("Black Market")
            console.print(f"[gold]Your Gold: {self.player._gold}[/gold]")
            loWeight, hiWeight = self.BLACK_MARKET_RUNE_WEIGHT_RANGE
            console.print(f"[dim]Paid for in gold and runes. Only runes weighing {loWeight}-{hiWeight} count toward the Rune Value, each worth 100/weight.[/dim]\n")

            if not self.blackMarketStock:
                printWarning("The Black Market is empty right now. Check back after a restock.")
                pause()
                return

            stockList = list(self.blackMarketStock.items())
            for i, (name, (goldPrice, runeValueNeeded, equipment)) in enumerate(stockList, 1):
                console.print(f"  [cyan]{i}.[/cyan] [dim]{goldPrice}g + {runeValueNeeded} Rune Value\n{equipment}")

            choice = console.input("\n[cyan]Choose item to buy (0 to cancel):\n> [/cyan]").strip()
            try:
                if choice == '0':
                    return
                index = int(choice) - 1
            except ValueError:
                printError("Invalid input!")
                pause()
                continue
            if not (0 <= index < len(stockList)):
                printWarning("Invalid choice")
                pause()
                continue

            key, (goldPrice, runeValueNeeded, equipment) = stockList[index]
            self._buyBlackMarketItem(key, goldPrice, runeValueNeeded, equipment)

    def _buyBlackMarketItem(self, key: str, goldPrice: int, runeValueNeeded: int, equipment: Equipment):
        if self.player._gold < goldPrice:
            printWarning(f"Need {goldPrice}g! (Current: {self.player._gold}g)")
            pause()
            return

        loWeight, hiWeight = self.BLACK_MARKET_RUNE_WEIGHT_RANGE
        eligibleRunes = []
        for runeKey, quantity in self.player._craftingInventory.items():
            category, runeType = runeKey.split('_', 1)
            rune = getRuneObject(category, runeType)
            if rune and loWeight <= rune.dropWeight <= hiWeight:
                eligibleRunes.append((runeKey, rune, quantity))

        if not eligibleRunes:
            printWarning(f"You have no eligible runes (weight {loWeight}-{hiWeight}) to offer.")
            pause()
            return

        console.print(f"\n[gold]{equipment.name}[/gold] costs {goldPrice}g + {runeValueNeeded} Rune Value")
        console.print("[dim]Offer runes toward the Rune Value below. Purchase finalises once you reach the total (0 at any point cancels).[/dim]")

        offered: Dict[str, int] = {}
        totalValue = 0.0
        while totalValue < runeValueNeeded:
            console.print(f"\n[gold]Rune Value offered: {totalValue:.1f} / {runeValueNeeded}[/gold]")
            for i, (runeKey, rune, quantity) in enumerate(eligibleRunes, 1):
                remaining = quantity - offered.get(runeKey, 0)
                perUnitValue = 100 / rune.dropWeight
                console.print(f"  [cyan]{i}.[/cyan] {rune.name} x{remaining} available [dim](weight {rune.dropWeight}, {perUnitValue:.1f} value each)[/dim]")

            choice = console.input("\n[cyan]Offer which rune? (0 to cancel):\n> [/cyan]").strip()
            try:
                if choice == '0':
                    printWarning("Cancelled.")
                    pause()
                    return
                index = int(choice) - 1
            except ValueError:
                printWarning("Invalid input")
                continue
            if not (0 <= index < len(eligibleRunes)):
                printWarning("Invalid choice")
                continue

            runeKey, rune, quantity = eligibleRunes[index]
            remaining = quantity - offered.get(runeKey, 0)
            if remaining <= 0:
                printWarning("None of that rune left to offer.")
                continue

            amountStr = console.input(f"[bold]How many {rune.name}? (max {remaining}):[/bold]\n[cyan]> [/cyan]").strip()
            try:
                amount = int(amountStr)
            except ValueError:
                printWarning("Invalid input")
                continue
            if amount <= 0 or amount > remaining:
                printWarning("Invalid amount")
                continue

            offered[runeKey] = offered.get(runeKey, 0) + amount
            totalValue += amount * (100 / rune.dropWeight)

        console.print(f"\n[bold]Finalise purchase of {equipment.name} for {goldPrice}g + the offered runes? (y/n)[/bold]")
        confirm = console.input("[cyan]> [/cyan]").strip().lower()
        if confirm != 'y':
            printWarning("Cancelled.")
            pause()
            return

        self.player._gold -= goldPrice
        for runeKey, amount in offered.items():
            category, runeType = runeKey.split('_', 1)
            self.player.removeRune(category, runeType, amount)
        self.player.addEquipmentToStorage(equipment)
        questBoard = getattr(self.player, '_questBoard', None)
        if questBoard is not None:
            questBoard.notifyEvent('black_market_purchase', rarity=equipment.rarity.value)
        del self.blackMarketStock[key]
        printSuccess(f"\nAcquired {equipment.name} from the Black Market!")
        pause()

    def sellItems(self):
        clearScreen()
        printHeader("Sell Items")
        console.print("\n[bold]What would you like to sell?[/bold]")
        console.print("[cyan]1. Resources[/cyan]")
        console.print("[red1]2. Equipment[/red1]")
        console.print("[gold]3. Buyback Recently Sold[/gold]")
        console.print("[dim]0. Cancel[/dim]")
        choice = console.input("\n> ").strip()

        try:
            choice = int(choice)
            if choice == 1:
                self._sellResources()
            elif choice == 2:
                self._sellEquipment()
            elif choice == 3:
                self._buybackEquipment()
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
                    soldPrice = equip.value
                    self.player.gainGold(soldPrice)
                    self.recentlySold.insert(0, (equip, soldPrice))
                    self.recentlySold = self.recentlySold[:10]

                    printSuccess(f"\nSold {equip.name} for {soldPrice}g!")
        except ValueError:
            pass
        pause()

    def _buybackEquipment(self):
        if not self.recentlySold:
            printWarning("\nNo recently sold equipment to buy back.")
            pause()
            return
        console.print("\n[gold]Recently Sold:[/gold]")
        for i, (equip, soldPrice) in enumerate(self.recentlySold, 1):
            console.print(f"  [cyan]{i}.[/cyan] [dim]{soldPrice}g\n{equip}")
        choice = console.input("\n[cyan]Choose equipment to buy back (0 to cancel):\n> [/cyan]").strip()
        try:
            index = int(choice) - 1
            if 0 <= index < len(self.recentlySold):
                equip, soldPrice = self.recentlySold[index]
                confirm = console.input(f"\n[bold]Buy back {equip.name} for {soldPrice}g? (y/n):[/bold]\n[cyan]> [/cyan]").strip().lower()
                if confirm == 'y':
                    if self.player._gold >= soldPrice:
                        self.player._gold -= soldPrice
                        self.player.addEquipmentToStorage(equip)
                        self.recentlySold.pop(index)
                        printSuccess(f"\nBought back {equip.name}!")
                    else:
                        printWarning(f"Need {soldPrice}g! (Current: {self.player._gold}g)")
        except ValueError:
            pass
        pause()
