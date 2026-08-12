from typing import Dict
from scripts.styles import console, printWarning, pause, displayResourceCost, printError, printSuccess

class Station:
    def __init__(self, player, name: str):
        self.player = player
        self.name = name
        self.level = 0
        self.resourcesNeeded = self._getUpgradeRequirements()[self.level + 1] if self.level < 5 else {}

    def _getUpgradeRequirements(self) -> Dict[int, Dict]:
        """Do not use .super() | Rewrite!"""
        return {
            1: {},
            2: {},
            3: {},
            4: {},
            5: {}
        }

    def upgrade(self) -> bool:
        if self.level >= 5:
            printWarning(f"{self.name} is already at max level.")
            pause()
            return False
        
        required = self._getUpgradeRequirements()[self.level + 1]
        
        console.print(f"\n[cyan]Upgrade {self.name} to level {self.level + 1}?[/cyan]")
        console.print(f"[bold]Required Resources:[/bold]")

        costTable = displayResourceCost(required, self.player._inventory)
        console.print(costTable)
        
        confirm = console.input("\n[bold]Proceed with upgrade? (y/n): [/bold]").strip().lower()
        if confirm != 'y':
            return False
        
        # Check if player has all resources
        for resource, amount in required.items():
            if not self.player.hasItem(resource, amount):
                printError(f"Missing {amount}x {resource}")
                pause()
                return False
        
        # Remove resources
        for resource, amount in required.items():
            self.player.removeItem(resource, amount)
        
        self.level += 1
        self.resourcesNeeded = self._getUpgradeRequirements()[self.level + 1] if self.level < 5 else {}
        printSuccess(f"\n{self.name} has been upgraded to level {self.level}!")
        pause()
        return True

    def _serialise(self):
        return {
            "name": self.name,
            "resourcesNeeded": self.resourcesNeeded,
            "level": self.level,
        }