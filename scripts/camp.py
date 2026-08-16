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

class Camp:
    """Collection of all camp buildings in one place:
        - Campfire
        - Forge
        - Market
        - Quest Board"""
    def __init__(self, player):
        self.player = player
        self.campfire = Campfire(self.player)
        self.forge = Forge(self.player)
        self.market = Market(self.player)
        self.questBoard = QuestBoard(self.player)
        self.shrine = Shrine(self.player)

    def _serialiseAll(self):
        return {
            'campfire': self.campfire._serialise(),
            'forge': self.forge._serialise(),
            'market': self.market._serialise(),
            'questBoard': self.questBoard._serialise(),
            'shrine': self.shrine._serialise(),
        }

    def deserialiseAll(self, data: Dict[str, Dict], player: object):
        self.player = player
        # update player references
        self.campfire.player = player
        self.forge.player = player
        self.market.player = player
        self.questBoard.player = player
        self.shrine.player = player

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
        lastRestock = market.get('lastRestock')
        if lastRestock:
            self.market.lastRestock = datetime.datetime.fromisoformat(lastRestock)
        else:
            self.market.lastRestock = None
        
        questBoard = data['questBoard']
        self.questBoard.name = data.get('name', 'Quest Board')
        self.questBoard.resourcesNeeded = questBoard.get('resourcesNeeded', {})
        self.questBoard.level = questBoard.get('level', 0)
        self.questBoard.activeQuests = questBoard.get('activeQuests', {})
        self.questBoard.completedQuests = questBoard.get('completedQuests', [])

        shrine = data.get('shrine', {})
        self.shrine.name = shrine.get('shrine', 'Shrine')
        self.shrine.resourcesNeeded = shrine.get('resourcesNeeded', {})
        self.shrine.level = shrine.get('level', 0)

    def mainMenu(self):
        while True:
            clearScreen()
            printHeader(f"{self.player._name} - Level {self.player._level}")
            console.print(self.player.__str__())
            console.print("\n[dim]Area: Camp[/dim]")
            printSeparator()
            campLines = [
                "[dim]0)[/dim] Return",
                f"[dim]1)[/dim] [red]Campfire[/red] | Current Level: {self.campfire.level}\n  [dim]Upgrade Requirements:[/dim] {self.campfire.formatUpgradeRequirements()}",
                f"[dim]2)[/dim] [yellow]Forge[/yellow] | Current Level: {self.forge.level}\n  [dim]Upgrade Requirements:[/dim] {self.forge.formatUpgradeRequirements()}",
                f"[dim]3)[/dim] [green]Market[/green] | Current Level: {self.market.level}\n  [dim]Upgrade Requirements:[/dim] {self.market.formatUpgradeRequirements()}",
                f"[dim]4)[/dim] [gold1]Shrine[/gold1] | Current Level: {self.shrine.level}\n  [dim]Upgrade Requirements:[/dim] {self.shrine.formatUpgradeRequirements()}"
                #f"[dim]4)[/dim] [blue]Quest Board[/blue] | Current Level: {self.questBoard.level}\n  [dim]Upgrade Requirements:[/dim] {self.questBoard.formatUpgradeRequirements()}",
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
                    case _:
                        printWarning("\nInvalid choice.")
            except ValueError as e:
                printError(f"\nAn error occured: {e}")

...