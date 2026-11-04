import random
from enum import Enum
from typing import List, Dict
from rich.table import Table
from rich.text import Text
from ..styles import console

class RoomType(Enum):
    COMBAT = "combat"
    ELITE = "elite"
    REST = "rest"
    MERCHANT = "merchant"
    TREASURE = "treasure"
    EVENT = "event"
    BOSS = "boss"

ROOM_STYLES = {
    RoomType.COMBAT: ("⚔", "white"),
    RoomType.ELITE: ("☠", "bold red"),
    RoomType.REST: ("♥", "green"),
    RoomType.MERCHANT: ("$", "gold1"),
    RoomType.TREASURE: ("♦", "cyan"),
    RoomType.EVENT: ("?", "magenta"),
    RoomType.BOSS: ("♛", "bold gold1"),
}
CONNECTOR_STYLE = "grey50"

NO_REPEAT_TYPES = {RoomType.REST, RoomType.MERCHANT, RoomType.TREASURE, RoomType.EVENT}

ROOM_WEIGHTS_BY_DEPTH = {
    'early': {RoomType.COMBAT: 45, RoomType.ELITE: 5,  RoomType.REST: 12, RoomType.MERCHANT: 12, RoomType.TREASURE: 12, RoomType.EVENT: 14},
    'mid':   {RoomType.COMBAT: 38, RoomType.ELITE: 15, RoomType.REST: 12, RoomType.MERCHANT: 10, RoomType.TREASURE: 11, RoomType.EVENT: 14},
    'late':  {RoomType.COMBAT: 32, RoomType.ELITE: 24, RoomType.REST: 12, RoomType.MERCHANT: 8,  RoomType.TREASURE: 10, RoomType.EVENT: 14},
}

class DungeonNode:
    def __init__(self, nodeId: str, floor: int, column: int, roomType: RoomType):
        self.id = nodeId
        """{floor}-{column}"""
        self.floor = floor
        self.column = column
        self.roomType = roomType
        self.connections: List[str] = []
        self.completed = False

    def __repr__(self):
        return f"<{self.roomType.value} floor={self.floor} column={self.column}>"

class DungeonMapGraph:
    def __init__(self, floorCount: int, width: int = 6, pathCount: int = 6):
        """floorCount includes entrance floor (0) and boss floor (floorCount - 1)"""
        if floorCount < 3:
            raise ValueError(f"A dungeon needs at least 3 floors. This dungeon only generated with {floorCount} floors.")

        self.floorCount = floorCount
        self.width = width
        self.nodes: Dict[str, DungeonNode] = {}
        self.floorNodeIds: List[List[str]] = [[] for _ in range(floorCount)]
        self.startNodeIds: List[str] = []

        self._generatePaths(pathCount)
        self._assignRoomTypes()

    def _nodeId(self, floor: int, column: int) -> str:
        return f"{floor}-{column}"

    def _getOrCreateNode(self, floor: int, column: int, roomType: RoomType) -> DungeonNode:
        nodeId = self._nodeId(floor, column)
        if nodeId not in self.nodes:
            node = DungeonNode(nodeId, floor, column, roomType)
            self.nodes[nodeId] = node
            self.floorNodeIds[floor].append(nodeId)
        return self.nodes[nodeId]

    def _generatePaths(self, pathCount: int):
        """walk 'pathCount random paths top-to-bottom, each drifting between -1 and 1 columns per floor"""
        bossColumn = self.width // 2
        self._getOrCreateNode(self.floorCount - 1, bossColumn, RoomType.BOSS)

        for _ in range(pathCount):
            column = random.randint(0, self.width - 1)
            current = self._getOrCreateNode(0, column, RoomType.COMBAT)
            if not current.id in self.startNodeIds:
                self.startNodeIds.append(current.id)

            for floor in range(1, self.floorCount - 1):
                step = random.choice([-1, 0, 1])
                column = max(0, min(self.width - 1, column + step))
                nextNode = self._getOrCreateNode(floor, column, RoomType.COMBAT)
                if nextNode.id not in current.connections:
                    current.connections.append(nextNode.id)
                current = nextNode

            bossNode = self.nodes[self._nodeId(self.floorCount - 1, bossColumn)]
            if bossNode.id not in current.connections:
                current.connections.append(bossNode.id)

    def _assignRoomTypes(self):
        for nodeId in self.floorNodeIds[0]:
            self.nodes[nodeId].roomType = RoomType.COMBAT # entrance always a fight

        lastRoomFloor = self.floorCount - 2 # floor right before boss

        for floor in range(1, self.floorCount - 1):
            depthFraction = floor / lastRoomFloor
            if depthFraction < 0.34:
                weights = ROOM_WEIGHTS_BY_DEPTH['early']
            elif depthFraction < 0.7:
                weights = ROOM_WEIGHTS_BY_DEPTH['mid']
            else:
                weights = ROOM_WEIGHTS_BY_DEPTH['late']

            for nodeId in self.floorNodeIds[floor]:
                node = self.nodes[nodeId]

                if floor == lastRoomFloor:
                    node.roomType = RoomType.REST
                    continue

                predecessorTypes = {
                    self.nodes[pid].roomType for pid in self.nodes
                    if nodeId in self.nodes[pid].connections
                }
                candidates = {
                    rt: w for rt, w in weights.items()
                    if not (rt in NO_REPEAT_TYPES and rt in predecessorTypes)
                }
                if not candidates:
                    candidates = weights

                node.roomType = random.choices(list(candidates.keys()), weights=list(candidates.values()), k=1)[0]

    def _connectorRow(self, lowerFloor: int) -> List[Text]:
        glyphs: Dict[int, set] = {c: set() for c in range(self.width)}

        for nodeId in self.floorNodeIds[lowerFloor]:
            node = self.nodes[nodeId]
            for targetId in node.connections:
                targetColumn = self.nodes[targetId].column
                if targetColumn == node.column:
                    glyphs[node.column].add('|')
                elif targetColumn > node.column:
                    glyphs[node.column].add('╱')
                else:
                    glyphs[node.column].add('╲')

        row = []
        for c in range(self.width):
            marks = glyphs[c]
            if not marks:
                symbol = ""
            elif len(marks) > 1:
                symbol = "┼"
            else:
                symbol = next(iter(marks))
            row.append(Text(symbol, style=CONNECTOR_STYLE))
        return row

    def render(self, currentNodeId: str = None) -> Table:
        table = Table(show_header=False, show_lines=False, box=None, padding=(0, 1))
        for _ in range(self.width):
            table.add_column(justify="center")

        for floor in range(self.floorCount - 1, -1, -1):
            row = [""] * self.width
            for nodeId in self.floorNodeIds[floor]:
                node = self.nodes[nodeId]
                symbol, colour = ROOM_STYLES[node.roomType]

                if node.id == currentNodeId:
                    cell = Text(f" {symbol}", style=f"bold {colour} reverse")
                elif node.completed:
                    cell = Text(symbol, style=f"dim {colour}")
                else:
                    cell = Text(symbol, style=colour)

                row[node.column] = cell
            table.add_row(*row)

            if floor > 0:
                table.add_row(*self._connectorRow(floor - 1))

        return table

