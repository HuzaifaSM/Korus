"""
mastery = deep_sky_blue3
perfect = steel_blue bold"""

from .base import CraftingItem, CraftOutcome, CraftResult
import random
from typing import Dict

class BaseMasteryRune(CraftingItem):
    masteryToAdd: int = 1

    def _serialise(self):
        temp = super()._serialise()
        temp['masteryToAdd'] = self.masteryToAdd
        return temp
    
    @classmethod
    def deserialise(cls, data):
        rune = super().deserialise(data)
        rune.masteryToAdd = data.get('masteryToAdd', 1.0)
        return rune

    def apply(self, item) -> CraftResult:
        if item.entropyLocked or item.destabilised:
            return CraftResult(
                outcome=CraftOutcome.NO_EFFECT,
                message='Item cannot be modified'
            )
        
        if item.level < self.minItemLevel:
            return CraftResult(
                outcome=CraftOutcome.NO_EFFECT,
                message='Item level too low'
            )
        
        item.gainMastery(self.masteryToAdd)
        item.addEntropy(self.successEntropy)
        
        return CraftResult(
                outcome=CraftOutcome.SUCCESS,
                message=f'Item gained {self.masteryToAdd}% mastery.',
                entropyAdded=self.successEntropy
            )
    
class MasteryRune(BaseMasteryRune):
    name = '[bright_white]Mastery Rune[/bright_white]'
    description = 'Increases the mastery of an item by 1%, enhancing its affix values. Maximum 20% mastery.'
    masteryToAdd = 1
    successEntropy = 0.02
    minItemLevel = 5

class GreaterMasteryRune(BaseMasteryRune):
    name = '[gold1 bold]Greater Mastery Rune[/gold1 bold]'
    description = 'Increases the mastery of an item by 2%, enhancing its affix values. Maximum 20% mastery.'
    masteryToAdd = 2
    successEntropy = 0.035
    minItemLevel = 20

class PerfectMassteryRune(BaseMasteryRune):
    name = '[yellow1 bold underline]Perfect Mastery Rune[/yellow1 bold underline]'
    description = 'Increases the mastery of an item by 5%, enhancing its affix values. Maximum 20% mastery.'
    masteryToAdd = 5
    successEntropy = 0.09
    minItemLevel = 35

class DivineMasteryRune(BaseMasteryRune):
    name = '[light_goldenrod1 bold underline]Divine Mastery Rune[/light_goldenrod1 bold underline]'
    description = 'Increases the mastery of an item by 10%, enhancing its affix values. Maximum 20% mastery.'
    masteryToAdd = 10
    minItemLevel = 60
    successEntropy = 0.18

MASTERY_RUNES: Dict[str, BaseMasteryRune] = {
    'mastery': MasteryRune(),
    'greater': GreaterMasteryRune(),
    'perfect': PerfectMassteryRune(),
    'divine': DivineMasteryRune()
}