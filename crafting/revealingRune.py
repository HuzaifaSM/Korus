from .base import CraftingItem, CraftOutcome, CraftResult
from scripts.affixes import rollAffix, Affix
import random
from typing import Dict
from scripts.styles import console

class BaseRevealingRune(CraftingItem):
    numChoices: int = 3

    def _serialise(self):
        temp = super()._serialise()
        temp['numChoices'] = self.numChoices
        return temp
    
    @classmethod
    def deserialise(cls, data):
        rune = super().deserialise(data)
        rune.numChoices = data.get('numChoices', 3)
        return rune

    def getRandomEmptySlot(self, item):
        emptyPrefixes = [s for s in item.prefixSlots if s.isEmpty]
        emptySuffixes = [s for s in item.suffixSlots if s.isEmpty]
        allEmpty = emptyPrefixes + emptySuffixes
        if not allEmpty:
            return None
        return random.choice(allEmpty)

    def rollAffixOptions(self, item, slot, numOptions: int):
        options = []
        usedBaseIds = set()

        prefixExcluded, suffixExcluded = item.getExcludedIds()
        excludedIds = prefixExcluded if slot.kind == 'prefix' else suffixExcluded
        
        defenseType = None
        if hasattr(item, 'defenseType') and item.defenseValue > 0:
            defenseType = item.defenseType

        attempts = 0
        maxAttempts = numOptions * 10

        while len(options) < numOptions and attempts < maxAttempts:
            attempts += 1

            currentExcluded = excludedIds | usedBaseIds
            affix = rollAffix(
                equipType=item.slot,
                affixType=slot.kind,
                itemLevel=item.level,
                rarity=item.rarity,
                excludeIds=currentExcluded,
                tierBias=0.0,
                defenseType=defenseType,
                minAffixLevel=self.minAffixLevel,
                noEmpty=True
            )
            
            if affix:
                baseId = affix.id.split('_t')[0]
                if baseId not in usedBaseIds:
                    options.append(affix)
                    usedBaseIds.add(baseId)

        return options

    def presentChoices(self, options):
        console.print('\n[cyan bold]=== Choose an Affix ===[/cyan bold]\n')

        for i, affix in enumerate(options, 1):
            console.print(f'  [cyan]{i}.[/cyan] {affix}')
            console.print(f'    [dim]Tier {affix.tier} | Level {affix.levelReq} | Range: {affix.minVal} - {affix.maxVal}[/dim]\n')

        while True:
            choice = console.input(f'[cyan]Choose Affix (1-{len(options)}):\n>[/cyan] ').strip()
            try:
                index = int(choice) - 1
                if 0 <= index <= len(options):
                    return options[index]
                else:
                    console.print('[red]Invalid Input[/red]')
            except ValueError:
                console.print('[red]Invalid Input[/red]')

    def apply(self, item) -> CraftResult:
        if item.entropyLocked or item.destabilised:
            return CraftResult(
                outcome=CraftOutcome.NO_EFFECT,
                message='Item cannot be modified'
            )
        
        if self.minItemLevel is not None and item.level < self.minItemLevel:
            return CraftResult(
                outcome=CraftOutcome.NO_EFFECT,
                message='Item level too low'
            )
        
        slot = self.getRandomEmptySlot(item)
        if slot is None:
            return CraftResult(
                outcome=CraftOutcome.NO_EFFECT,
                message='Item has no empty affix slots'
            )
        
        options = self.rollAffixOptions(item, slot, self.numChoices)
        if not options:
            return CraftResult(
                outcome=CraftOutcome.NO_EFFECT,
                message='Failed to roll any valid affixes'
            )
        
        chosenAffix = self.presentChoices(options)

        slot.affix = chosenAffix
        item.update()
        item._generateName()
        item.addEntropy(self.successEntropy)

        return CraftResult(
                outcome=CraftOutcome.SUCCESS,
                message=f'Revealing rune successfully used. Added chosen affix: {chosenAffix.name}',
                entropyAdded=self.successEntropy
            )

class RevealingRune(BaseRevealingRune):
    name = '[light_sky_blue1]Revealing Rune[/light_sky_blue1]'
    description = 'Reveals 3 random affixes and lets you choose which one to add to the item.'
    numChoices = 3
    minAffixLevel = 0
    minItemLevel = 15
    successEntropy = 0.15
    dropWeight = 80

class GreaterRevealingRune(BaseRevealingRune):
    name = '[deep_sky_blue1 bold]Greater Revealing Rune[/deep_sky_blue1 bold]'
    description = 'Reveals 3 random affixes above level 25 and lets you choose which one to add.'
    numChoices = 3
    minAffixLevel = 25
    minItemLevel = 30
    successEntropy = 0.25
    dropWeight = 35

class PerfectRevealingRune(BaseRevealingRune):
    name = '[dodger_blue2 bold underline]Perfect Revealing Rune[/dodger_blue2 bold underline]'
    description = 'Reveals 3 random affixes above level 50 and lets you choose which one to add.'
    numChoices = 3
    minAffixLevel = 50
    minItemLevel = 60
    successEntropy = 0.35
    dropWeight = 15

class AbundantRevealingRune(BaseRevealingRune):
    name = '[sky_blue1 bold]Abundant Revealing Rune[/sky_blue1 bold]'
    description = 'Reveals 4 random affixes and lets you choose which one to add.'
    numChoices = 4
    minAffixLevel = 10
    minItemLevel = 25
    successEntropy = 0.2
    dropWeight = 80

class DivineRevealingRune(BaseRevealingRune):
    name = '[light_cyan1 bold underline]Divine Revealing Rune[/light_cyan1 bold underline]'
    description = 'Reveals 4 random affixes above level 40 and lets you choose which one to add.'
    numChoices = 4
    minAffixLevel = 40
    minItemLevel = 50
    successEntropy = 0.45
    dropWeight = 15

class FocusedRevealingRune(BaseRevealingRune):
    name = '[steel_blue1 bold]Focused Revealing Rune[/steel_blue1 bold]'
    description = 'Reveals 2 affixes above level 60.'
    numChoices = 2
    minAffixLevel = 60
    minItemLevel = 70
    successEntropy = 0.5
    dropWeight = 6

class PinpointRevealingRune(BaseRevealingRune):
    name = '[cyan bold underline]Pinpoint Revealing Rune[/cyan bold underline]'
    description = 'Reveals 2 random affixes above level 75.'
    numChoices = 2
    minAffixLevel = 75
    minItemLevel = 80
    successEntropy = 0.6
    dropWeight = 6

REVEALING_RUNES: Dict[str, BaseRevealingRune] = {
    'revealing': RevealingRune(),
    'greater': GreaterRevealingRune(),
    'perfect': PerfectRevealingRune(),
    'abundant': AbundantRevealingRune(),
    'divine': DivineRevealingRune(),
    'focused': FocusedRevealingRune(),
    'pinpoint': PinpointRevealingRune()
}