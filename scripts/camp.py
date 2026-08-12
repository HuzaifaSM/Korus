import datetime
from typing import Dict
from .styles import (
    console, printHeader, printSeparator, clearScreen,
    printWarning, printError, printInfo,
)

from .campAreas.campfire import Campfire
from .campAreas.crafter import Crafter
from .campAreas.forge import Forge
from .campAreas.market import Market
from .campAreas.questBoard import QuestBoard

def printChoices():
    """Print camp choices"""
    choices = [
        "[dim]0)[/dim] Return",
        "[dim]1)[/dim] [red]Campfire[/red]",
        "[dim]2)[/dim] [cyan]Crafter[/cyan]",
        "[dim]3)[/dim] [yellow]Forge[/yellow]",
        "[dim]4)[/dim] [green]Market[/green]",
        "[dim]5)[/dim] [blue]Quest Board[/blue]"
    ]
    for line in choices:
        console.print(line)

class Camp:
    """Collection of all camp buildings in one place:
        - Campfire
        - Crafter
        - Forge
        - Market
        - Quest Board"""
    def __init__(self, player):
        self.player = player
        self.campfire = Campfire(self.player) #1
        self.crafter = Crafter(self.player) #2
        self.forge = Forge(self.player) #3
        self.market = Market(self.player) #4
        self.questBoard = QuestBoard(self.player) #5

    def _serialiseAll(self):
        return {
            'campfire': self.campfire._serialise(),
            'crafter': self.crafter._serialise(),
            'forge': self.forge._serialise(),
            'market': self.market._serialise(),
            'questBoard': self.questBoard._serialise()
        }

    def deserialiseAll(self, data: Dict[str, Dict], player: object):
        self.player = player
        # update player references
        self.campfire.player = player
        self.crafter.player = player
        self.forge.player = player
        self.market.player = player
        self.questBoard.player = player

        campfire = data['campfire']
        self.campfire.name = campfire.get('name', 'Campfire')
        self.campfire.resourcesNeeded = campfire.get('resourcesNeeded', {})
        self.campfire.level = campfire.get('level', 1)
        self.campfire.supplies = campfire.get('supplies', 0)

        crafter = data['crafter']
        self.crafter.name = crafter.get('name', 'Crafter')
        self.crafter.resourcesNeeded = crafter.get('resourcesNeeded', {})
        self.crafter.level = crafter.get('level', 1)
        self.crafter.blueprints = crafter.get('blueprints', 0)

        forge = data['forge']
        self.forge.name = forge.get('name', 'Forge')
        self.forge.resourcesNeeded = forge.get('resourcesNeeded', {})
        self.forge.level = forge.get('level', 1)
        self.forge.fuel = forge.get('fuel', 0)

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

    def mainMenu(self):
        while True:
            clearScreen()
            printHeader(f"{self.player._name} - Level {self.player._level}")
            console.print(self.player.__str__())
            console.print("\n[dim]Area: Camp[/dim]")
            printSeparator()
            printChoices()
            choice = console.input("\n[cyan]>[/cyan] ").strip()
            try:
                choice = int(choice)
                match choice:
                    case 0:
                        printInfo("Leaving Camp...")
                        break
                    case 1:
                        self.campfire.mainMenu()
                    case 2:
                        self.crafter.mainMenu()
                    case 3:
                        self.forge.mainMenu()
                    case 4:
                        self.market.mainMenu()
                    case 5:
                        self.questBoard.mainMenu()
                    case _:
                        printWarning("\nInvalid choice.")
            except Exception as e:
                printError(f"\nAn error occured: {e}")

...