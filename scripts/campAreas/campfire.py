from typing import Dict
from .station import Station
from scripts.styles import (
    console, clearScreen, printHeader, printSeparator,
    pause, printWarning, printError, printSuccess, checkGlobalCommand
)
from scripts.items.food import cookFood, MAX_SUPPLIES_FOR_BASE_HEAL

class Campfire(Station):
    # most basic station, main function is to heal after each combat
    COOKING_LEVEL = 2
    EMERGENCY_REVIVAL_LEVEL = 5
    EMERGENCY_REVIVAL_SUPPLIES_COST = 50

    def __init__(self, player):
        self.supplies = 0 #campfire main resource
        super().__init__(player, "Campfire")
        self.level = 1 # campfire starts at level 1

    def _serialise(self):
        temp = super()._serialise()
        temp['supplies'] = self.supplies
        return temp

    def _getUpgradeRequirements(self) -> Dict[int, Dict[str, int]]:
        return {
            1: {"wood": 5, "stone": 5,
                'description': "Enemies will begin to drop [resource]Supplies[/resource].\nA new option will be unlocked: [red]Rest[/red]. [resource]Supplies[/resource] are used to [red]Rest[/red] in order to recover health.\nAt the end of combat, heal for 10% of your Max HP."
                },
            2: {"wood": 15, "stone": 15,
                'description': "At the end of combat, heal for 20% of your Max HP.\nUnlocks [red]Cook Food[/red]: spend Supplies to cook a single-use Food item, healing on top of a random combat buff, consumed as a Bonus Action."
                },
            3: {"wood": 30, "stone": 30,
                'description': "At the end of combat, heal for 30% of your Max HP.\nCooking can now roll stronger (Tier 2) Food affixes."
                },
            4: {"wood": 50, "stone": 50,
                'description': "At the end of combat, heal for 40% of your Max HP.\nCooking can now roll the strongest (Tier 3) Food affixes."
                },
            5: {"wood": 75, "stone": 75,
                'description': f"At the end of combat, heal for 50% of your Max HP.\nUnlocks Emergency Revival: if you would die in combat, you're instead revived at 20% Max HP, consuming {Campfire.EMERGENCY_REVIVAL_SUPPLIES_COST} Supplies (once per combat)."
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
            if self.level >= self.COOKING_LEVEL:
                console.print("[dim]2.[/dim] Cook Food")
                console.print(f"[dim]Food Inventory:[/dim] {len(self.player._foodInventory)}")
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
                    case 2:
                        if self.level >= self.COOKING_LEVEL:
                            self.cook()
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
            self.player.heal(healAmount, reason="campfire heal")
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

    def cook(self):
        if self.level < self.COOKING_LEVEL:
            printWarning(f"Campfire Level {self.COOKING_LEVEL} required to cook. Current Level: {self.level}")
            pause()
            return
        if not self.supplies:
            printWarning("No supplies to cook with.")
            return

        console.print(f"[dim]2 Supplies = 1% Max HP recovered on eating, capped at {MAX_SUPPLIES_FOR_BASE_HEAL} Supplies (20% Max HP) - a Food affix can push the total past that cap.[/dim]")
        amountStr = console.input(f"[bold]How many Supplies to spend? (max {min(self.supplies, MAX_SUPPLIES_FOR_BASE_HEAL)}):[/bold]\n[cyan]> [/cyan]").strip()
        try:
            amount = int(amountStr)
        except ValueError:
            printError("Invalid input!")
            return
        if amount <= 0 or amount > self.supplies:
            printWarning("Invalid amount!")
            return

        self.supplies -= amount
        food = cookFood(amount, self.level)
        self.player._foodInventory.append(food)
        printSuccess(f"\nCooked: {food.describe()}")

...