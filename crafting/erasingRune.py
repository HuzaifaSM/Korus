"""
base = grey70
surgical = white bold (will need many variants per catergory type) <- attemps to remove certain affix type e.g. defense/resistance
predatory = black on bright_white bold (removes lowest level affix)
"""

from .base import CraftingItem, CraftOutcome, CraftResult
import random
from typing import Dict

class BaseErasingRune(CraftingItem):
    affixesToRemove: int = 1
    maxAffixLevel: int | None = None

    def _serialise(self):
        temp = super()._serialise()
        temp['affixesToRemove'] = self.affixesToRemove
        temp['minAffixLevel'] = self.minAffixLevel
        return temp

    @classmethod
    def deserialise(cls, data):
        rune = super().deserialise(data)
        rune.affixesToRemove = data.get('affixesToRemove', 1)
        rune.maxAffixLevel = data.get('maxAffixLevel', None)
        return rune

    def getRemovableSlots(self, item):
        slots = [s for s in item.prefixSlots + item.suffixSlots if not s.isEmpty and not s.locked]

        if self.minAffixLevel is not None:
            slots = [s for s in slots if s.affix.levelReq >= self.minAffixLevel]

        if self.maxAffixLevel is not None:
            slots = [s for s in slots if s.affix.levelReq <= self.maxAffixLevel]

        return slots
    
    def apply(self, item) -> CraftResult:
        if not item.craftable:
            return CraftResult(
                outcome=CraftOutcome.NO_EFFECT,
                message='Item cannot be modified'
            )
        
        if self.minItemLevel > item.level:
            return CraftResult(
                outcome=CraftOutcome.NO_EFFECT,
                message='Item level is too low'
            )
        
        slots = self.getRemovableSlots(item)
        if not slots:CraftResult(
                outcome=CraftOutcome.NO_EFFECT,
                message='Item has no removable affixes'
            )
        
        toRemove = min(self.affixesToRemove, len(slots))
        removed = random.sample(slots, toRemove)
        removedAffixes = [a.affix for a in removed]
        removedStr = ""
        for r in removedAffixes:
            removedStr += f"[dim red]- {r}[/dim red]\n"

        for slot in removed:
            slot.affix = None

        item.update()
        item._generateName()
        if len(removed) > 0:
            item.addEntropy(self.successEntropy)
        message=f'Removed {len(removed)} affixes. Removed:\n{removedStr}'

        if len(removed) < self.affixesToRemove or toRemove < self.affixesToRemove:
            outcome = CraftOutcome.PARTIAL_SUCCESS,
        else:
            outcome = CraftOutcome.SUCCESS

        return CraftResult(
                outcome=outcome,
                message=message,
                entropyAdded=self.successEntropy
            )

class ErasingRune(BaseErasingRune):
    name = '[grey50]Erasing Rune[/grey50]'
    description = 'Removes 1 random affix.'
    affixesToRemove = 1
    minItemLevel = 10
    successEntropy = 0.035
    dropWeight = 300

class GreaterErasingRune(BaseErasingRune):
    name = '[bright_black bold]Greater Erasing Rune[/bright_black bold]'
    description = 'Removes 1 random affix below level 60.'
    affixesToRemove = 1
    minItemLevel = 20
    maxAffixLevel = 60
    successEntropy = 0.7
    dropWeight = 150

class PerfectErasingRune(BaseErasingRune):
    name = '[white bold underline]Perfect Erasing Rune[/white bold underline]'
    description = 'Removes 1 random affix below level 30.'
    affixesToRemove = 1
    minItemLevel = 30
    maxAffixLevel = 30
    successEntropy = 0.12
    dropWeight = 80

class PredatoryErasingRune(BaseErasingRune):
    name = '[dark_red bold]Predatory Erasing Rune[/dark_red bold]'
    description = 'Removes the lowest level affix.'
    affixesToRemove = 1
    minItemLevel = 40
    successEntropy = 0.2
    dropWeight = 35

    def getRemovableSlots(self, item):
        slots = super().getRemovableSlots(item)
        if not slots:
            return []
        weakest = min(slots, key=lambda s: s.affix.levelReq)
        return [weakest]

class ConsumingErasingRune(BaseErasingRune):
    name = '[red bold underline]Consuming Erasing Rune[/red bold underline]'
    description = 'Removes the two lowest level affixes.'
    affixesToRemove = 2
    minItemLevel = 50
    successEntropy = 0.35
    dropWeight = 15

    def getRemovableSlots(self, item):
        slots = super().getRemovableSlots(item)
        if not slots:
            return []
        affixes = sorted(slots, key=lambda s: s.affix.levelReq)
        af1, af2 = affixes[0], affixes[1]
        return [af1, af2]

class CleansingErasingRune(BaseErasingRune):
    name = '[light_slate_blue]Cleansing Erasing Rune[/light_slate_blue]'
    description = 'Removes up to 2 random affixes.'
    affixesToRemove = 2
    minItemLevel = 20
    successEntropy = 0.15
    dropWeight = 80

class RuinousErasingRune(BaseErasingRune):
    name = '[deep_pink4 bold underline]Ruinous Erasing Rune[/deep_pink4 bold underline]'
    description = 'Removes up to 3 random affixes.'
    affixesToRemove = 3
    minItemLevel = 30
    successEntropy = 0.22
    dropWeight = 35

class BlankErasingRune(BaseErasingRune):
    name = '[black on white italic bold underline]Blank Erasing Rune[/black on white italic bold underline]'
    description = 'Removes all affixes.'
    affixesToRemove = 99
    minItemLevel = 15
    successEntropy = 0
    dropWeight = 80

class EnlighteningErasingRune(BaseErasingRune):
    name = '[dark_goldenrod bold]Enlightening Erasing Rune[/dark_goldenrod bold]'
    description = 'Removes up to 2 random affixes below level 40.'
    affixesToRemove = 2
    maxAffixLevel = 40
    minItemLevel = 45
    successEntropy = 0.3
    dropWeight = 35

class SectionedErasingRune(BaseErasingRune):
    name = '[grey35 italic]Sectioned Erasing Rune[/grey35 italic]'
    description = 'Removes 1 random affix between level 20 and 60.'
    affixesToRemove = 1
    minAffixLevel = 20
    maxAffixLevel = 60
    minItemLevel = 40
    successEntropy = 0.125
    dropWeight = 80

class PreciseErasingRune(BaseErasingRune):
    name = '[grey7 bold italic]Precise Erasing Rune[/grey7 bold italic]'
    description = 'Removes 1 random affix between level 15 and 40.'
    affixesToRemove = 1
    minAffixLevel = 15
    maxAffixLevel = 40
    minItemLevel = 45
    successEntropy = 0.2
    dropWeight = 80

class PrefixErasingRune(BaseErasingRune):
    name = '[grey63]Prefix Erasing Rune[/grey63]'
    description = 'Removes 1 random prefix.'
    affixesToRemove = 1
    minItemLevel = 15
    successEntropy = 0.06
    dropWeight = 300

    def getRemovableSlots(self, item):
        slots = [s for s in item.prefixSlots if not s.isEmpty and not s.locked]
        if self.maxAffixLevel is not None:
            slots = [s for s in slots if s.affix.levelReq <= self.maxAffixLevel]
        return slots

class GreaterPrefixErasingRune(PrefixErasingRune):
    name = '[grey46 bold]Greater Prefix Erasing Rune[/grey46 bold]'
    description = 'Removes 1 random prefix below level 60.'
    affixesToRemove = 1
    minItemLevel = 25
    maxAffixLevel = 60
    successEntropy = 0.12
    dropWeight = 150

class PerfectPrefixErasingRune(PrefixErasingRune):
    name = '[white bold]Perfect Prefix Erasing Rune[/white bold]'
    description = 'Removes 1 random prefix below level 30.'
    affixesToRemove = 1
    minItemLevel = 35
    maxAffixLevel = 30
    successEntropy = 0.2
    dropWeight = 80

class SuffixErasingRune(BaseErasingRune):
    name = '[grey63]Suffix Erasing Rune[/grey63]'
    description = 'Removes 1 random suffix.'
    affixesToRemove = 1
    minItemLevel = 15
    successEntropy = 0.06
    dropWeight = 300

    def getRemovableSlots(self, item):
        slots = [s for s in item.suffixSlots if not s.isEmpty and not s.locked]
        if self.maxAffixLevel is not None:
            slots = [s for s in slots if s.affix.levelReq <= self.maxAffixLevel]
        return slots

class GreaterSuffixErasingRune(SuffixErasingRune):
    name = '[grey46 bold]Greater Suffix Erasing Rune[/grey46 bold]'
    description = 'Removes 1 random suffix below level 60.'
    affixesToRemove = 1
    minItemLevel = 25
    maxAffixLevel = 60
    successEntropy = 0.12
    dropWeight = 150

class PerfectSuffixErasingRune(SuffixErasingRune):
    name = '[white bold]Perfect Suffix Erasing Rune[/white bold]'
    description = 'Removes 1 random suffix below level 30.'
    affixesToRemove = 1
    minItemLevel = 35
    maxAffixLevel = 30
    successEntropy = 0.2
    dropWeight = 80

class PassiveErasingRune(BaseErasingRune):
    name = '[red3]Passive Erasing Rune[/red3]'
    description = 'Removes 1 random offensive-related affix.'
    affixesToRemove = 1
    minItemLevel = 20
    successEntropy = 0.1
    dropWeight = 150

    def getRemovableSlots(self, item):
        slots = super().getRemovableSlots(item)
        return [s for s in slots if 'offensive' in s.affix.categories]

class RecklessErasingRune(BaseErasingRune):
    name = '[steel_blue]Reckless Erasing Rune[/steel_blue]'
    description = 'Removes 1 random defensive affix.'
    affixesToRemove = 1
    minItemLevel = 20
    successEntropy = 0.1
    dropWeight = 150

    def getRemovableSlots(self, item):
        slots = super().getRemovableSlots(item)
        return [s for s in slots if 'defensive' in s.affix.categories]

class ShallowErasingRune(BaseErasingRune):
    name = '[cyan]Shallow Erasing Rune[/cyan]'
    description = 'Removes 1 random utility affix'
    affixesToRemove = 1
    minItemLevel = 20
    successEntropy = 0.1
    dropWeight = 150

    def getRemovableSlots(self, item):
        slots = super().getRemovableSlots(item)
        return [s for s in slots if 'utility' in s.affix.categories]

class WastingErasingRune(BaseErasingRune):
    name = '[green]Wasting Erasing Rune[/green]'
    description = 'Removes 1 random health-related affix.'
    affixesToRemove = 1
    minItemLevel = 20
    successEntropy = 0.08
    dropWeight = 150

    def getRemovableSlots(self, item):
        slots = super().getRemovableSlots(item)
        return [s for s in slots if 'health' in s.affix.categories]

class BrittleErasingRune(BaseErasingRune):
    name = '[purple]Brittle Erasing Rune[/purple]'
    description = 'Removes 1 random resistance affix.'
    affixesToRemove = 1
    minItemLevel = 20
    successEntropy = 0.08
    dropWeight = 150

    def getRemovableSlots(self, item):
        slots = super().getRemovableSlots(item)
        return [s for s in slots if 'resistance' in s.affix.categories]

class UnluckyErasingRune(BaseErasingRune):
    name = '[orange1]Unlucky Erasing Rune[/orange1]'
    description = 'Removes 1 random critical-related affix.'
    affixesToRemove = 1
    minItemLevel = 20
    successEntropy = 0.08
    dropWeight = 150

    def getRemovableSlots(self, item):
        slots = super().getRemovableSlots(item)
        return [s for s in slots if 'critical' in s.affix.categories]

ERASING_RUNES: Dict[str, BaseErasingRune] = {
    'erasing': ErasingRune(),
    'greater': GreaterErasingRune(),
    'perfect': PerfectErasingRune(),

    'predatory': PredatoryErasingRune(),
    'consuming': ConsumingErasingRune(),

    'cleansing': CleansingErasingRune(),
    'ruinous': RuinousErasingRune(),
    'blank': BlankErasingRune(),

    'enlightening': EnlighteningErasingRune(),

    'sectioned': SectionedErasingRune(),
    'precise': PreciseErasingRune(),

    'prefix': PrefixErasingRune(),
    'greater_prefix': GreaterPrefixErasingRune(),
    'perfect_prefix': PerfectPrefixErasingRune(),
    'suffix': SuffixErasingRune(),
    'greater_suffix': GreaterSuffixErasingRune(),
    'perfect_suffix': PerfectSuffixErasingRune(),

    'passive': PassiveErasingRune(),
    'reckless': RecklessErasingRune(),
    'shallow': ShallowErasingRune(),
    'wasting': WastingErasingRune(),
    'brittle': BrittleErasingRune(),
    'unlucky': UnluckyErasingRune(),

}

"""
IDEAS:
"""