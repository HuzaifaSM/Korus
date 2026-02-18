from typing import Dict, Optional
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

    def _hasPlayerAbilities(self) -> bool:
        return len(self.player._abilities) > 0

    def _selectPlayerAbility(self, filterFunc=None) -> Optional[tuple]:
        if not self._hasPlayerAbilities():
            printWarning("No abilities available!")
            pause()
            return None
        
        abList = list(self.player._abilities.items())
        if filterFunc:
            abList = [(name, ab) for name, ab in abList if filterFunc(ab)]
        
        if not abList:
            printWarning("No abilities match the criteria!")
            pause()
            return None
        
        console.print(f"\n[bold cyan]Your Abilities:[/bold cyan]")
        for i, (name, ability) in enumerate(abList, 1):
            console.print(f"  [cyan]{i}.[/cyan] {name}")
            console.print(f"     [dim]Damage: {ability.damage} | Cooldown: {ability.maxCooldown}[/dim]")
            if ability._mechanics:
                console.print(f"     [dim]Mechanics: {', '.join(ability._mechanics)}[/dim]")
        
        choice = console.input("\n[cyan]Choose ability (0 to cancel):\n> [/cyan]").strip()
        try:
            index = int(choice) - 1
            if 0 <= index < len(abList):
                return abList[index]
        except ValueError:
            pass
        
        return None