import random
from enum import Enum, auto
from typing import Any, Optional

class CraftOutcome(Enum):
    SUCCESS = auto()
    PARTIAL_SUCCESS = auto()
    NO_EFFECT = auto()
    FAILURE = auto()

class CraftResult:
    def __init__(self,
                 outcome: CraftOutcome, message: str,
                 entropyAdded: float = 0.0,
                 metadata: Optional[dict[str, Any]] = None):
        self.outcome = outcome
        self.message = message
        self.entropyAdded = entropyAdded
        self.metadata = metadata or {}

    @property
    def success(self) -> bool:
        return self.outcome == CraftOutcome.SUCCESS

class CraftingItem:
    name: str = "Unnamed crafting item"
    description: str = "Undefined crafting item"

    successEntropy: float = 0.0

    minAffixLevel: Optional[int] = None
    minAffixTier: Optional[int] = None
    minItemLevel: Optional[int] = None
    maxTierDelta: Optional[int] = None

    # relative weight used when rolling which rune drops (scripts/runeDrops.py) - higher is more
    # common. Set explicitly per-rune based on power: roughly 300=basic/utility, 150=common,
    # 80=uncommon, 35=rare, 15=very rare, 6=build-defining/extremely rare
    dropWeight: float = 100.0

    def _serialise(self):
        """covers:\n
        - name
        - description
        - successEntropy
        - partialSuccessEntropy
        - minAffixLevel
        - minAffixTier
        - minItemLevel
        - maxTierDelta
        - dropWeight"""
        return {
            'name': self.name,
            'description': self.description,
            'successEntropy': self.successEntropy,
            'partialSuccessEntropy': self.partialSuccessEntropy,
            'minAffixLevel': self.minAffixLevel,
            'minAffixTier': self.minAffixTier,
            'minItemLevel': self.minItemLevel,
            'maxTierDelta': self.maxTierDelta,
            'dropWeight': self.dropWeight
        }

    @classmethod
    def deserialise(cls, data):
        rune = cls()
        rune.name = data.get('name', 'Rune')
        rune.description = data.get('descripton', 'A crafting item')
        rune.successEntropy = data.get('successEntropy', 0.0)
        rune.partialSuccessEntropy = data.get('partialSuccessEntropy', 0.0)
        rune.minAffixLevel = data.get('minAffixLevel', None)
        rune.minAffixTier = data.get('minAffixTier', None)
        rune.minItemLevel = data.get('minItemLevel', None)
        rune.maxTierDelta = data.get('maxTierDelta', None)
        rune.dropWeight = data.get('dropWeight', cls.dropWeight)
        return rune

    def __rich__(self):
        return self.__str__()

    def __str__(self) -> str:
        string = f"[cyan bold]Name:[/cyan bold] {self.name}\n[cyan bold]Description:[/cyan bold] {self.description}\n[red3]Entropy Added:[/red3] {self.successEntropy}"
        return string

    def apply(self, item) -> CraftResult:
        return NotImplementedError

...