from typing import Dict
from scripts.styles import console, printWarning, pause, displayResourceCost, printError, printSuccess
from scripts.player_classes.base import Player

class Station:
    maxLevel: int = 5

    def __init__(self, player: Player, name: str):
        self.player = player
        self.name = name
        self.level = 0
        self.resourcesNeeded = self._getUpgradeRequirements()[self.level + 1] if self._isLevelImplemented(self.level + 1) else {}

    def _getUpgradeRequirements(self) -> Dict[int, Dict]:
        """rewrite per station"""
        return {
            1: {},
            2: {},
            3: {},
            4: {},
            5: {}
        }

    def _isLevelImplemented(self, level: int) -> bool:
        if level > self.maxLevel:
            return False
        required = self._getUpgradeRequirements().get(level)
        if required is None:
            return False
        return required.get('description') is not None

    def formatUpgradeRequirements(self) -> str:
        nextLevel = self.level + 1
        if self._isLevelImplemented(nextLevel):
            lines = []
            for resource, amount in self._getUpgradeRequirements().get(self.level + 1, {}).items():
                if resource == 'description':
                    continue
                playerResource = self.player._inventory.get(resource, 0)
                sign = "[success]✓[/success]" if playerResource >= amount else "[error]✗[/error]"
                lines.append(f"{playerResource}/{amount} {resource.replace('_', ' ').title()} {sign}")
            return " | ".join(lines)
        return " | [dim bold]Max Level[/dim bold]"

    def upgrade(self) -> bool:
        nextLevel = self.level + 1
        if not self._isLevelImplemented(nextLevel):
            printWarning(f"{self.name} is already at max level.")
            pause()
            return False

        required = self._getUpgradeRequirements()[self.level + 1]
        
        console.print(f"\n[cyan]Upgrade {self.name} to level {self.level + 1}?[/cyan]")
        console.print(f"[bold]Required Resources:[/bold]")

        costTable = displayResourceCost(required, self.player._inventory)
        console.print(costTable)
        description = required.get('description', '')
        console.print(description)

        confirm = console.input("\n[bold]Proceed with upgrade? (y/n): [/bold]").strip().lower()
        if confirm != 'y':
            return False
        
        # Check if player has all resources
        for resource, amount in required.items():
            if resource == 'description':
                continue
            if not self.player.hasItem(resource, amount):
                printError(f"Missing {amount}x {resource}")
                pause()
                return False

        # Remove resources
        for resource, amount in required.items():
            if resource == 'description':
                continue
            self.player.removeItem(resource, amount)

        self.level += 1
        self.resourcesNeeded = self._getUpgradeRequirements()[self.level + 1] if self._isLevelImplemented(self.level + 1) else {}
        questBoard = getattr(self.player, '_questBoard', None)
        if questBoard is not None:
            questBoard.notifyEvent('station_upgraded', station=self.name, level=self.level)
        printSuccess(f"\n{self.name} has been upgraded to level {self.level}!")
        pause()
        return True

    def _serialise(self):
        return {
            "name": self.name,
            "resourcesNeeded": self.resourcesNeeded,
            "level": self.level,
        }