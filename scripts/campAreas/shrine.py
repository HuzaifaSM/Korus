from .station import Station
from player.classes import ASCENDANCIES, DESCRIPTIONS
from scripts.styles import (
    console, clearScreen, printHeader, printSeparator,
    pause, printWarning, printError, printSuccess, checkGlobalCommand
)
from time import sleep

class Shrine(Station):
    """
    Ascendancy station
    """
    def __init__(self, player):
        super().__init__(player, "Shrine")

    def _getUpgradeRequirements(self):
        return {
            1: {"cloth": 20, "crystal": 5, "ascended_essence": 3,
                'description': 'Unlock the option to [gold1 bold]Ascend[/gold1 bold] at level 20.\nYou will be given multiple choices of [gold1]Ascendancies[/gold1] to pick from, and are allowed to switch at any point for free.'
                },
            2: {
                'description': 'Not yet implemented.'
                },
            3: {
                'description': 'Not yet implemented.'
                },
            4: {
                'description': 'Not yet implemented.'
                },
            5: {
                'description': 'Not yet implemented.'
                }
        }

    def playerAscend(self):
        if self.level == 0:
            printWarning("Shrine Level 1 required to ascend. Current Level: 0")
            return
        if self.player._level < 20:
            printWarning("You must be at least level 20 to ascend!")
            return

        playerClass = self.player.className

        def _displayDescriptions():
            printHeader("Available Ascendancies")
            for i, (ascendancy, description) in enumerate(DESCRIPTIONS[playerClass].items()):
                if ascendancy == playerClass:
                    continue

                lore, description = description.split('[/lore]')
                lore += '[/lore]'

                console.print(f"[cyan]{i}:[/cyan] [asc_{ascendancy.lower()}]{ascendancy}:[/asc_{ascendancy.lower()}] {lore}\n{description}")
                sleep(0.5)
                console.print()

        ascendancies: dict[int, str] = {}
        for i, ascendancy in enumerate(ASCENDANCIES[playerClass]):
            ascendancies[i+1] = ascendancy

        while True:
            clearScreen()
            printHeader("Select an Ascendancy")
            _displayDescriptions()
            console.print("[dim]0.[/dim] Return")
            for i, asc in ascendancies.items():
                grammar = "an" if asc[0].lower() in ['a', 'e', 'i', 'o', 'u'] else "a"
                console.print(f"[dim]{i}.[/dim] [class_{playerClass}]Become {grammar}[/class_{playerClass}] [asc_{asc.lower()}]{asc}[/asc_{asc.lower()}]")

            choice = console.input("\n[cyan]>[/cyan] ").strip()
            validChoices = range(1, len(ascendancies) + 1)

            try:
                choice = int(choice)
                match choice:
                    case 0:
                        return
                    case _:
                        if choice in validChoices:
                            chosen = ascendancies[choice]
                            if self.player.updateAscendancy(chosen):
                                grammar = "an" if chosen[0].lower() in ['a', 'e', 'i', 'o', 'u'] else "a"
                                printSuccess(f"You have successfully ascended into {grammar} [asc_{chosen.lower()}]{chosen}[/asc_{chosen.lower()}]")
                            else:
                                printError(f"You were unable to ascend at this time.")
                            pause()
                            return
                        else:
                            printWarning(f"Invalid choice: {choice}")
            except ValueError as e:
                printError(f"{e}")
                pause()

    def mainMenu(self):
        while True:
            clearScreen()
            printHeader(f"Shrine - Level {self.level}")
            console.print()
            console.print("[dim]0.[/dim] Return")
            if self.level > 0:
                console.print("[dim]1.[/dim] Ascend")
            if self.level == 5:
                console.print("[dim]2.[/dim] Increased Max Level")
            console.print("[dim]9.[/dim] Upgrade Shrine")

            choice = console.input("\n[cyan]>[/cyan] ").strip()
            checkGlobalCommand(choice)

            try:
                choice = int(choice)
                match choice:
                    case 0:
                        return
                    case 1:
                        self.playerAscend()
                    case 2:
                        console.print("[error]No implementation for this function yet[/error]")
                        # self.increasePlayerMaxLevel()
                    case 9:
                        self.upgrade()
                    case _:
                        printWarning(f"Invalid choice: {choice}")
            except ValueError as e:
                printError(f"{e}")
                pause()
