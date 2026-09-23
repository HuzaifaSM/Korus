import datetime
from typing import Dict
from .styles import (
    console, printHeader, printSeparator, clearScreen,
    printWarning, printError, printInfo, checkGlobalCommand,
)

from .campAreas.campfire import Campfire
from .campAreas.forge import Forge
from .campAreas.market import Market
from .campAreas.questBoard import QuestBoard
from .campAreas.shrine import Shrine
from .campAreas.accountStash import AccountStash

class Camp:
    """Collection of all camp buildings in one place:
        - Campfire
        - Forge
        - Market
        - Quest Board
        - Shrine
        - Account Stash"""
    def __init__(self, player):
        self.player = player
        self.campfire = Campfire(self.player)
        self.forge = Forge(self.player)
        self.market = Market(self.player)
        self.questBoard = QuestBoard(self.player)
        self.shrine = Shrine(self.player)
        self.accountStash = AccountStash(player)
        self.player._questBoard = self.questBoard
        self.player._campfire = self.campfire

    def _serialiseAll(self):
        return {
            'campfire': self.campfire._serialise(),
            'forge': self.forge._serialise(),
            'market': self.market._serialise(),
            'questBoard': self.questBoard._serialise(),
            'shrine': self.shrine._serialise(),
            'accountStash': self.accountStash._serialise()
        }

    def deserialiseAll(self, data: Dict[str, Dict], player: object):
        self.player = player
        # update player references
        self.campfire.player = player
        self.forge.player = player
        self.market.player = player
        self.questBoard.player = player
        self.shrine.player = player
        player._questBoard = self.questBoard
        player._campfire = self.campfire

        campfire = data['campfire']
        self.campfire.name = campfire.get('name', 'Campfire')
        self.campfire.resourcesNeeded = campfire.get('resourcesNeeded', {})
        self.campfire.level = campfire.get('level', 1)
        self.campfire.supplies = campfire.get('supplies', 0)

        forge = data['forge']
        self.forge.name = forge.get('name', 'Forge')
        self.forge.resourcesNeeded = forge.get('resourcesNeeded', {})
        self.forge.level = forge.get('level', 1)
        self.forge.fuel = forge.get('fuel', 0)
        self.forge.blueprints = forge.get('blueprints', 0)

        market = data['market']
        self.market.name = market.get('name', 'trainingGrounds')
        self.market.resourcesNeeded = market.get('resourcesNeeded', {})
        self.market.level = market.get('level', 1)
        self.market.tradeVouchers = market.get('tradeVouchers', 0)
        stock = market.get('stock', {})
        if stock:
            self.market._deserialiseStock(stock)
        blackMarketStock = market.get('blackMarketStock', {})
        if blackMarketStock:
            self.market._deserialiseBlackMarketStock(blackMarketStock)
        else:
            self.market.blackMarketStock = {}
        recentlySold = market.get('recentlySold', [])
        if recentlySold:
            self.market._deserialiseRecentlySold(recentlySold)
        else:
            self.market.recentlySold = []
        self.market.commission = market.get('commission', None)
        self.market.haggledItems = set(market.get('haggledItems', []))
        lastRestock = market.get('lastRestock')
        if lastRestock:
            self.market.lastRestock = datetime.datetime.fromisoformat(lastRestock)
        else:
            self.market.lastRestock = None
        
        questBoard = data['questBoard']
        self.questBoard.name = data.get('name', 'Quest Board')
        self.questBoard.resourcesNeeded = questBoard.get('resourcesNeeded', {})
        self.questBoard.level = questBoard.get('level', 0)
        self.questBoard.milestoneProgress = questBoard.get('milestoneProgress', {})
        self.questBoard.completedMilestones = questBoard.get('completedMilestones', [])
        self.questBoard.credits = questBoard.get('credits', 0)
        self.questBoard.activeBounties = questBoard.get('activeBounties', [])

        shrine = data.get('shrine', {})
        self.shrine.name = shrine.get('shrine', 'Shrine')
        self.shrine.resourcesNeeded = shrine.get('resourcesNeeded', {})
        self.shrine.level = shrine.get('level', 0)

        accountStash = data.get('accountStash', {})
        self.accountStash.name = accountStash.get('name', 'Account Stash')
        self.accountStash.resourcesNeeded = accountStash.get('resourcesNeeded', {})
        self.accountStash.level = accountStash.get('level', 0)

    def mainMenu(self):
        while True:
            clearScreen()
            printHeader(f"{self.player.formatTitledName()} - Level {self.player._level}")
            console.print(self.player.__str__())
            console.print("\n[dim]Area: Camp[/dim]")
            printSeparator()
            campLines = [
                "[dim]0)[/dim] Return",
                f"[dim]1)[/dim] [red]Campfire[/red] | Current Level: {self.campfire.level}\n  [dim]Upgrade Requirements:[/dim] {self.campfire.formatUpgradeRequirements()}",
                f"[dim]2)[/dim] [yellow]Forge[/yellow] | Current Level: {self.forge.level}\n  [dim]Upgrade Requirements:[/dim] {self.forge.formatUpgradeRequirements()}",
                f"[dim]3)[/dim] [green]Market[/green] | Current Level: {self.market.level}\n  [dim]Upgrade Requirements:[/dim] {self.market.formatUpgradeRequirements()}",
                f"[dim]4)[/dim] [gold1]Shrine[/gold1] | Current Level: {self.shrine.level}\n  [dim]Upgrade Requirements:[/dim] {self.shrine.formatUpgradeRequirements()}",
                f"[dim]5)[/dim] [blue]Quest Board[/blue] | Current Level: {self.questBoard.level}\n  [dim]Upgrade Requirements:[/dim] {self.questBoard.formatUpgradeRequirements()}",
                f"[dim]6)[/dim] [magenta]Account Stash[/magenta] | Current Level: {self.accountStash.level}\n  [dim]Upgrade Requirements:[/dim] {self.accountStash.formatUpgradeRequirements()}"
            ]
            for line in campLines:
                console.print(line + "\n")
            choice = console.input("\n[cyan]>[/cyan] ").strip()
            checkGlobalCommand(choice)
            try:
                choice = int(choice)
                match choice:
                    case 0:
                        printInfo("Leaving Camp...")
                        return
                    case 1:
                        self.campfire.mainMenu()
                    case 2:
                        self.forge.mainMenu()
                    case 3:
                        self.market.mainMenu()
                    case 4:
                        self.shrine.mainMenu()
                    case 5:
                        self.questBoard.mainMenu()
                    case 6:
                        self.accountStash.mainMenu()
                    case _:
                        printWarning("\nInvalid choice.")
            except ValueError as e:
                printError(f"\nAn error occured: {e}")

...