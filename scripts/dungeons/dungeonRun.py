from typing import Optional

from ..styles import console, clearScreen, printHeader, printSeparator, pause, printWarning, printSuccess
from .mapGraph import DungeonMapGraph, RoomType
from .modifiers import rollDungeonModifiers, aggregateEffects
from .rooms import combatRoom, bossRoom, restRoom, merchantRoom, treasureRoom, eventRoom

# graph width/path-count scale with tier - higher tier dungeons are wider (more choice per floor)
WIDTH_BY_TIER = {1: 4, 2: 4, 3: 5, 4: 5, 5: 6}
PATHS_BY_TIER = {1: 4, 2: 5, 3: 5, 4: 6, 5: 7}

class DungeonRun:
    def __init__(self, game, dungeonMap):
        self.game = game
        self.dungeonMap = dungeonMap
        self.modifiers = rollDungeonModifiers(dungeonMap.tier)
        self.effects = aggregateEffects(self.modifiers)

        tier = min(5, max(1, dungeonMap.tier))
        self.graph = DungeonMapGraph(dungeonMap.floorCount, WIDTH_BY_TIER[tier], PATHS_BY_TIER[tier])

        self.currentNodeId: Optional[str] = None
        self.retreated = False
        self.completed = False

    def _showModifiers(self):
        printSeparator()
        console.print("[gold1]Dungeon Modifiers:[/gold1]")
        for mod in self.modifiers:
            colour = 'success' if mod.modType == 'positive' else 'warning'
            console.print(f"  [{colour}]- {mod.description}[/{colour}]")
        printSeparator()

    def _chooseStart(self) -> str:
        clearScreen()
        printHeader(f"{self.dungeonMap.name} - Entrance")
        self._showModifiers()
        console.print(self.graph.render())
        console.print("\n[cyan]Choose your entrance:[/cyan]")
        for i, nodeId in enumerate(self.graph.startNodeIds, 1):
            console.print(f"  [dim]{i}.[/dim] {self.graph.nodes[nodeId].roomType.value.title()}")

        while True:
            choice = console.input("\n[cyan]>[/cyan] ").strip()
            try:
                index = int(choice) - 1
                if 0 <= index < len(self.graph.startNodeIds):
                    return self.graph.startNodeIds[index]
            except ValueError:
                pass
            printWarning("Invalid choice!")

    def _chooseNext(self, node) -> Optional[str]:
        clearScreen()
        printHeader(self.dungeonMap.name)
        console.print(self.graph.render(currentNodeId=node.id))
        console.print("\n[cyan]Where next?[/cyan]")
        for i, nodeId in enumerate(node.connections, 1):
            console.print(f"  [dim]{i}.[/dim] {self.graph.nodes[nodeId].roomType.value.title()}")
        console.print("  [dim]0.[/dim] [red]Retreat[/red] [dim](banks everything earned so far - this map is spent either way)[/dim]")

        while True:
            choice = console.input("\n[cyan]>[/cyan] ").strip()
            try:
                choice = int(choice)
            except ValueError:
                printWarning("Invalid choice!")
                continue
            if choice == 0:
                return None
            index = choice - 1
            if 0 <= index < len(node.connections):
                return node.connections[index]
            printWarning("Invalid choice!")

    def _runRoom(self, node):
        currentFloor = node.floor
        if node.roomType == RoomType.COMBAT:
            combatRoom(self.game, self.dungeonMap, currentFloor, self.effects)
        elif node.roomType == RoomType.ELITE:
            combatRoom(self.game, self.dungeonMap, currentFloor, self.effects, elite=True)
        elif node.roomType == RoomType.REST:
            restRoom(self.game, self.dungeonMap, self.effects)
        elif node.roomType == RoomType.MERCHANT:
            merchantRoom(self.game, self.dungeonMap)
        elif node.roomType == RoomType.TREASURE:
            treasureRoom(self.game, self.dungeonMap, self.effects)
        elif node.roomType == RoomType.EVENT:
            eventRoom(self.game, self.dungeonMap, currentFloor, self.effects)
        elif node.roomType == RoomType.BOSS:
            bossRoom(self.game, self.dungeonMap, currentFloor, self.effects)

    def start(self):
        """Caller is responsible for removing the DungeonMap from the player's held maps
        BEFORE calling this - the map is spent the moment the player steps in, win or retreat."""
        node = self.graph.nodes[self._chooseStart()]

        while True:
            self.currentNodeId = node.id
            self._runRoom(node)
            node.completed = True

            if node.roomType == RoomType.BOSS:
                self.completed = True
                break

            nextId = self._chooseNext(node)
            if nextId is None:
                self.retreated = True
                break
            node = self.graph.nodes[nextId]

        clearScreen()
        if self.completed:
            printHeader("Dungeon Complete!")
            printSuccess(f"{self.dungeonMap.name} has been cleared.")
        else:
            printHeader("Retreated")
            printSuccess("You made it out with everything you found along the way.")
        console.print("[dim]This map has been consumed.[/dim]")
        pause()
