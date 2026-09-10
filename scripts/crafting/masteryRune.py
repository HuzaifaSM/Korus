from .base import CraftingItem, CraftOutcome, CraftResult
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

    def apply(self, item, player=None) -> CraftResult:
        if not item.craftable:
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
    name = '[gold1 bold]Mastery Rune[/gold1 bold]'
    description = 'Increases the mastery of an item by 5%, enhancing its affix values. Maximum 20% mastery.'
    masteryToAdd = 5
    successEntropy = 0.06
    minItemLevel = 10
    dropWeight = 150

class GreaterMasteryRune(BaseMasteryRune):
    name = '[yellow1 bold underline]Greater Mastery Rune[/yellow1 bold underline]'
    description = 'Increases the mastery of an item by 10%, enhancing its affix values. Maximum 20% mastery.'
    masteryToAdd = 10
    successEntropy = 0.11
    minItemLevel = 30
    dropWeight = 90

class PerfectMasteryRune(BaseMasteryRune):
    name = '[light_goldenrod1 bold underline]Perfect Mastery Rune[/light_goldenrod1 bold underline]'
    description = 'Increases the mastery of an item by 15%, enhancing its affix values. Maximum 20% mastery.'
    masteryToAdd = 15
    minItemLevel = 50
    successEntropy = 0.16
    dropWeight = 35

MASTERY_RUNES: Dict[str, BaseMasteryRune] = {
    'mastery': MasteryRune(),
    'greater': GreaterMasteryRune(),
    'perfect': PerfectMasteryRune(),
}