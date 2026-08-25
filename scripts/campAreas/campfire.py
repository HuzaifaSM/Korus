from typing import Dict
from .station import Station
from scripts.styles import (
    console, clearScreen, printHeader, printSeparator,
    pause, printWarning, printError, printSuccess, checkGlobalCommand
)

class Campfire(Station):
    # most basic station, main function is to heal after each combat
    def __init__(self, player):
        self.supplies = 0 #campfire main resource
        super().__init__(player, "Campfire")

    def _serialise(self):
        temp = super()._serialise()
        temp['supplies'] = self.supplies
        return temp
    
    def _getUpgradeRequirements(self) -> Dict[int, Dict[str, int]]:
        return {
            1: {"wood": 5, "stone": 5,
                'description': "Enemies will begin to drop [resource]Supplies[/resource].\nA new option will be unlocked: [red]Rest[/red]. [resource]Supplies[/resource] are used to [red]Rest[/red] in order to recover health.\nAt the end of combat, heal for 10% of your Max HP."
                },
            2: {"wood": 20, "stone": 25, "iron_ore": 10,
                'description': "At the end of combat, heal for 20% of your Max HP."
                },
            3: {"herbs": 30, "leather": 20, "iron_ore": 15,
                'description': "At the end of combat, heal for 30% of your Max HP"
                },
            4: {"bone": 10, "wood": 60, "stone": 50, "iron_ore": 25,
                'description': "At the end of combat, heal for 40% of your Max HP"
                },
            5: {"soul": 30, "iron_ore": 50, "diamond": 10,
                'description': "At the end of combat, heal for 50% of your Max HP"
                }
        }

    def mainMenu(self):
        """Campfire main menu"""
        while True:
            clearScreen()
            printHeader(f"CAMPFIRE - Level {self.level}")
            console.print(f"[gold]Supplies:[/gold] {self.supplies}")
            printSeparator()
            console.print("[dim]0.[/dim] Return")
            if self.level >= 1:
                console.print("[dim]1.[/dim] Rest (Uses Supplies)")
            console.print("[dim]9.[/dim] Upgrade Campfire")
            
            choice = console.input("\n[cyan]>[/cyan] ").strip()
            checkGlobalCommand(choice)

            try:
                choice = int(choice)
                match choice:
                    case 0:
                        return
                    case 1:
                        if self.level >= 1:
                            self.rest()
                    case 9:
                        self.upgrade()
                    case _:
                        printWarning("Invalid choice!")
            except ValueError:
                printError("Invalid input!")
            pause()

    def applyHeal(self):
        if self.level > 0:
            healAmount = round(self.player._maxHealth * (0.1 * self.level))
            self.player.heal(healAmount)
            pause()

    def rest(self):
        if self.level < 1:
            printWarning(f"Campfire Level 1 required for resting. Current Level: {self.level}")
            pause()
            return
        if not self.supplies:
            printWarning("No supplies to aid in recovery.")
            return
        healAmount = round(self.player._maxHealth * 0.15)
        console.print(f"[heal]Healing {healAmount} per supply.[/heal]")
        suppliesUsed = 0
        while self.supplies and not (self.player._health == self.player._maxHealth):
            self.player.heal(healAmount, False)
            self.supplies -= 1
            suppliesUsed += 1
        printSuccess(f"\nUsed {suppliesUsed} supplies to recover to full health.")

...