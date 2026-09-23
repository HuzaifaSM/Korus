from .base import CraftingItem, CraftOutcome, CraftResult
from scripts.items.affixes import rollAffix, Affix, resolveAffixPoolKey
import random
from typing import Dict

class BaseGrowthRune(CraftingItem):
    affixesToAdd: int = 1
    market: bool = False
    
    def _serialise(self):
        temp = super()._serialise()
        temp['affixesToAdd'] = self.affixesToAdd
        return temp
    
    @classmethod
    def deserialise(cls, data):
        rune = super().deserialise(data)
        rune.affixesToAdd = data.get('affixesToAdd', 1)
        return rune

    def getRandomEmptySlot(self, item):
        emptyPrefixes = [s for s in item.prefixSlots if s.isEmpty]
        emptySuffixes = [s for s in item.suffixSlots if s.isEmpty]
        allEmpty = emptyPrefixes + emptySuffixes
        if not allEmpty:
            return None
        
        return random.choice(allEmpty)

    def apply(self, item, player=None) -> CraftResult:
        if not item.craftable:
            return CraftResult(
                outcome=CraftOutcome.NO_EFFECT,
                message='Item cannot be modified'
            )
        
        if self.minItemLevel is not None:
            if item.level < self.minItemLevel:
                return CraftResult(
                    outcome=CraftOutcome.NO_EFFECT,
                    message='Item level is too low'
                )

        if item.allSlotsFilled:
            return CraftResult(
                outcome=CraftOutcome.NO_EFFECT,
                message="Item has no empty affix slots"
            )

        added = 0
        addedAffixes: list[Affix] = []

        for _ in range(self.affixesToAdd):
            slot = self.getRandomEmptySlot(item)
            if slot is None:
                return CraftResult(
                    outcome=CraftOutcome.NO_EFFECT,
                    message='Item has no empty affix slots'
                )
            
            prefixExcluded, suffixExcluded = item.getExcludedIds()
            excludedIds = prefixExcluded if slot.kind == 'prefix' else suffixExcluded

            defenseType = item.defenseType

            affixPool = 'market' if self.market else 'affixes'

            affix = rollAffix(
                equipType=resolveAffixPoolKey(item),
                affixType=slot.kind,
                itemLevel=item.level,
                rarity=item.rarity,
                affixPool=affixPool,
                excludeIds=excludedIds,
                tierBias=0.0,
                defenseType=defenseType,
                minAffixLevel=self.minAffixLevel,
                noEmpty=True
            )

            if affix is None:
                continue # pool exhausted, safe fail

            slot.affix = affix
            if affix.stat == 'durability':
                if affix.isFlat:
                    item.durability += affix.value
                else:
                    item.durability = int(item.durability * (1 + (affix.value / 100)))
            added += 1
            addedAffixes.append(affix)

        if added == 0:
            return CraftResult(
                outcome=CraftOutcome.NO_EFFECT,
                message='No affixes were added'
            )
        
        item.update()
        item._generateName()
        item.addEntropy(self.successEntropy)

        addedStr = ""
        for a in addedAffixes:
            addedStr += f"[dim green1]- {a}[/dim green1]\n"

        if added == self.affixesToAdd:
            return CraftResult(
                    outcome=CraftOutcome.SUCCESS,
                    message=f'Added {added} affixes. Added:\n{addedStr}',
                    entropyAdded=self.successEntropy
                )
        else:
            return CraftResult(
                outcome=CraftOutcome.PARTIAL_SUCCESS,
                message=f'[warning dim]Added {added} affixes. Expected {self.affixesToAdd}[/warning dim]',
                entropyAdded=self.successEntropy
            )

class GrowthRune(BaseGrowthRune):
    name = '[green1]Growth Rune[/green1]'
    description = 'Adds 1 random affix to the selected piece of equipment'
    affixesToAdd = 1
    minAffixLevel = 0
    successEntropy = 0.05
    dropWeight = 300

class GreaterGrowthRune(BaseGrowthRune):
    name = '[green4]Greater Growth Rune[/green4]'
    description = 'Adds 1 random affix above level 30 to the selected piece of equipment'
    affixesToAdd = 1
    minAffixLevel = 30
    minItemLevel = 30
    successEntropy = 0.1
    dropWeight = 150

class PerfectGrowthRune(BaseGrowthRune):
    name = '[dark_green bold]Perfect Growth Rune[/dark_green bold]'
    description = 'Adds 1 random affix above level 60 to the selected piece of equipment'
    affixesToAdd = 1
    minAffixLevel = 60
    minItemLevel = 60
    successEntropy = 0.2
    dropWeight = 80

class AbundantGrowthRune(BaseGrowthRune):
    name = '[cyan2]Abundant Growth Rune[/cyan2]'
    description = 'Adds up to 2 random affixes to the selected piece of equipment'
    affixesToAdd = 2
    minAffixLevel = 0
    minItemLevel = 20
    successEntropy = 0.095
    dropWeight = 150

class BranchingGrowthRune(BaseGrowthRune):
    name = '[blue_violet bold]Branching Growth Rune[/blue_violet bold]'
    description = 'Adds up to 3 random affixes to the selected piece of equipment'
    affixesToAdd = 3
    minAffixLevel = 0
    minItemLevel = 50
    successEntropy = 0.15
    dropWeight = 80

class MajesticGrowthRune(BaseGrowthRune):
    name = '[orange3 bold]Majestic Growth Rune[/orange3 bold]'
    description = 'Adds up to 2 random affixes above level 25 to the selected piece of equipment'
    affixesToAdd = 2
    minAffixLevel = 25
    minItemLevel = 30
    successEntropy = 0.2
    dropWeight = 80

class DivineGrowthRune(BaseGrowthRune):
    name = '[deep_pink3 bold underline]Divine Growth Rune[/deep_pink3 bold underline]'
    description = 'Adds up to 3 random affixes above level 50 to the selected piece of equipment'
    affixesToAdd = 3
    minAffixLevel = 45
    minItemLevel = 55
    successEntropy = 0.4
    dropWeight = 15

class PrefixGrowthRune(BaseGrowthRune):
    name = '[sea_green2]Prefix Growth Rune[/sea_green2]'
    description = 'Adds 1 random prefix to the selected piece of equipment'
    affixesToAdd = 1
    minAffixLevel = 0
    successEntropy = 0.07
    dropWeight = 280

    def getRandomEmptySlot(self, item):
        emptyPrefixes = [s for s in item.prefixSlots if s.isEmpty]
        if not emptyPrefixes:
            return None
        return random.choice(emptyPrefixes)

class GreaterPrefixGrowthRune(PrefixGrowthRune):
    name = '[medium_spring_green]Greater Prefix Growth Rune[/medium_spring_green]'
    description = 'Adds 1 random prefix above level 25 to the selected piece of equipment'
    affixesToAdd = 1
    minAffixLevel = 25
    minItemLevel = 25
    successEntropy = 0.125
    dropWeight = 80

class PerfectPrefixGrowthRune(PrefixGrowthRune):
    name = '[chartreuse4 bold]Perfect Prefix Growth Rune[/chartreuse4 bold]'
    description = 'Adds 1 random prefix above level 55 to the selected piece of equipment'
    affixesToAdd = 1
    minAffixLevel = 55
    minItemLevel = 55
    successEntropy = 0.25
    dropWeight = 35

class SuffixGrowthRune(BaseGrowthRune):
    name = '[sea_green2]Suffix Growth Rune[/sea_green2]'
    description = 'Adds 1 random suffix to the selected piece of equipment'
    affixesToAdd = 1
    minAffixLevel = 0
    successEntropy = 0.07
    dropWeight = 280

    def getRandomEmptySlot(self, item):
        emptySuffixes = [s for s in item.suffixSlots if s.isEmpty]
        if not emptySuffixes:
            return None
        return random.choice(emptySuffixes)

class GreaterSuffixGrowthRune(SuffixGrowthRune):
    name = '[medium_spring_green]Greater Suffix Growth Rune[/medium_spring_green]'
    description = 'Adds 1 random suffix above level 25 to the selected piece of equipment'
    affixesToAdd = 1
    minAffixLevel = 25
    minItemLevel = 25
    successEntropy = 0.125
    dropWeight = 80

class PerfectSuffixGrowthRune(SuffixGrowthRune):
    name = '[chartreuse4 bold]Perfect Suffix Growth Rune[/chartreuse4 bold]'
    description = 'Adds 1 random suffix above level 55 to the selected piece of equipment'
    affixesToAdd = 1
    minAffixLevel = 55
    minItemLevel = 55
    successEntropy = 0.25
    dropWeight = 35

class OverflowingGrowthRune(BaseGrowthRune):
    name = '[bold italic spring_green4]Overflowing Growth Rune[/bold italic spring_green4]'
    description = 'Adds a random affix to every empty affix slot.'
    minItemLevel = 40
    successEntropy = 0.25
    dropWeight = 125

    def apply(self, item, player=None) -> CraftResult:
        if not item.craftable:
            return CraftResult(
                outcome=CraftOutcome.NO_EFFECT,
                message="Item cannot be modified",
            )
        if item.level < self.minItemLevel:
            return CraftResult(
                outcome=CraftOutcome.NO_EFFECT,
                message="Item level is too low"
            )
        if item.allSlotsFilled:
            return CraftResult(
                outcome=CraftOutcome.NO_EFFECT,
                message="Item has no empty affix slots"
            )

        addedAffixes = []
        failedAttempts = 0

        while not item.allSlotsFilled and failedAttempts < 5:
            slot = self.getRandomEmptySlot(item)
            equipType = resolveAffixPoolKey(item)
            affixType = 'prefixes' if slot.kind == 'prefix' else 'suffixes'

            prefixExcluded, suffixExcluded = item.getExcludedIds()
            excludedIds = prefixExcluded if slot.kind == 'prefix' else suffixExcluded

            defenseType = item.defenseType

            affix = rollAffix(
                equipType,
                affixType,
                item.level,
                item.rarity,
                excludedIds,
                tierBias=0.0,
                defenseType=defenseType,
                noEmpty=True
            )

            if affix is None:
                failedAttempts += 1
                continue

            slot.affix = affix
            if affix.stat == 'durability':
                if affix.isFlat:
                    item.durability += affix.value
                else:
                    item.durability = int(item.durability * (1 + (affix.value / 100)))

            addedAffixes.append(affix)

        if len(addedAffixes) == 0:
            return CraftResult(
                outcome=CraftOutcome.NO_EFFECT,
                message="No affixes were added"
            )

        item.update()
        item._generateName()
        item.addEntropy(self.successEntropy)

        addedStr = ""
        for a in addedAffixes:
            addedStr += f"[dim green1]- {a}[/dim green1]\n"

        return CraftResult(
            outcome=CraftOutcome.SUCCESS,
            message=f"[green1]Successfully added {len(addedAffixes)} affixes. Added:[/green1]\n{addedStr}"
        )

GROWTH_RUNES: Dict[str, BaseGrowthRune] = {
    'growth': GrowthRune(),
    'greater': GreaterGrowthRune(),
    'perfect': PerfectGrowthRune(),

    'abundant': AbundantGrowthRune(),
    'branching': BranchingGrowthRune(),

    'majestic': MajesticGrowthRune(),
    'divine': DivineGrowthRune(),

    'prefix': PrefixGrowthRune(),
    'greater_prefix': GreaterPrefixGrowthRune(),
    'perfect_prefix': PerfectPrefixGrowthRune(),

    'suffix': SuffixGrowthRune(),
    'greater_suffix': GreaterSuffixGrowthRune(),
    'perfect_suffix': PerfectSuffixGrowthRune(),

    'overflowing': OverflowingGrowthRune(),
}

"""
IDEAS:
- specific category rune
"""