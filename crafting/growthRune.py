from .base import CraftingItem, CraftOutcome, CraftResult
from scripts.affixes import rollAffix, Affix, AFFIX_POOL
import random
from typing import Dict

class BaseGrowthRune(CraftingItem):
    affixesToAdd: int = 1
    
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

    def apply(self, item) -> CraftResult:
        if item.entropyLocked or item.destabilised:
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
        
        added = 0

        for _ in range(self.affixesToAdd):
            slot = self.getRandomEmptySlot(item)
            if slot is None:
                return CraftResult(
                    outcome=CraftOutcome.NO_EFFECT,
                    message='Item has no empty affix slots'
                )
            
            prefixExcluded, suffixExcluded = item.getExcludedIds()
            excludedIds = prefixExcluded if slot.kind == 'prefix' else suffixExcluded

            defenseType = None
            if hasattr(item, 'defenseType') and item.defenseValue > 0:
                defenseType = item.defenseType
            
            affix = rollAffix(
                equipType=item.slot,
                affixType=slot.kind,
                itemLevel=item.level,
                rarity=item.rarity,
                excludeIds=excludedIds,
                tierBias=0.0,
                defenseType=defenseType,
                minAffixLevel=self.minAffixLevel,
                noEmpty=True
            )

            if affix is None:
                continue # pool exhausted, safe fail

            slot.affix = affix
            added += 1

        if added == 0:
            return CraftResult(
                outcome=CraftOutcome.NO_EFFECT,
                message='No affixes were added'
            )
        
        if added < self.affixesToAdd:
            partialEntropy = self.partialSuccessEntropy * added
            item.addEntropy(partialEntropy)
            return CraftResult(
                outcome=CraftOutcome.PARTIAL_SUCCESS,
                message=f'Added {added} affixes',
                entropyAdded=partialEntropy
            )
        
        item.update()
        item._generateName()
        item.addEntropy(self.successEntropy)

        return CraftResult(
                outcome=CraftOutcome.SUCCESS,
                message=f'Added {added} affixes',
                entropyAdded=self.successEntropy
            )

class GrowthRune(BaseGrowthRune):
    name = '[green1]Growth Rune[/green1]'
    description = 'Adds 1 random affix to the selected piece of equipment'
    affixesToAdd = 1
    minAffixLevel = 0
    successEntropy = 0.05
    partialSuccessEntropy = 0.0125

class GreaterGrowthRune(BaseGrowthRune):
    name = '[green4]Greater Growth Rune[/green4]'
    description = 'Adds 1 random affix above level 30 to the selected piece of equipment'
    affixesToAdd = 1
    minAffixLevel = 30
    minItemLevel = 30
    successEntropy = 0.1
    partialSuccessEntropy = 0.025

class PerfectGrowthRune(BaseGrowthRune):
    name = '[dark_green bold]Perfect Growth Rune[/dark_green bold]'
    description = 'Adds 1 random affix above level 60 to the selected piece of equipment'
    affixesToAdd = 1
    minAffixLevel = 60
    minItemLevel = 60
    successEntropy = 0.2
    partialSuccessEntropy = 0.05

class AbundantGrowthRune(BaseGrowthRune):
    name = '[cyan2]Abundant Growth Rune[/cyan2]'
    description = 'Adds up to 2 random affixes to the selected piece of equipment'
    affixesToAdd = 2
    minAffixLevel = 0
    minItemLevel = 20
    successEntropy = 0.095
    partialSuccessEntropy = 0.02375

class BranchingGrowthRune(BaseGrowthRune):
    name = '[blue_violet bold]Branching Growth Rune[/blue_violet bold]'
    description = 'Adds up to 3 random affixes to the selected piece of equipment'
    affixesToAdd = 3
    minAffixLevel = 0
    minItemLevel = 50
    successEntropy = 0.14
    partialSuccessEntropy = 0.035

class MajesticGrowthRune(BaseGrowthRune):
    name = '[orange3 bold]Majestic Growth Rune[/orange3 bold]'
    description = 'Adds up to 2 random affixes above level 25 to the selected piece of equipment'
    affixesToAdd = 2
    minAffixLevel = 25
    minItemLevel = 30
    successEntropy = 0.15
    partialSuccessEntropy = 0.0375

class DivineGrowthRune(BaseGrowthRune):
    name = '[deep_pink3 bold underline]Divine Growth Rune[/deep_pink3 bold underline]'
    description = 'Adds up to 3 random affixes above level 50 to the selected piece of equipment'
    affixesToAdd = 3
    minAffixLevel = 50
    minItemLevel = 55
    successEntropy = 0.35
    partialSuccessEntropy = 0.08725

class PrefixGrowthRune(BaseGrowthRune):
    name = '[sea_green2]Prefix Growth Rune[/sea_green2]'
    description = 'Adds 1 random prefix to the selected piece of equipment'
    affixesToAdd = 1
    minAffixLevel = 0
    successEntropy = 0.07

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

class PerfectPrefixGrowthRune(PrefixGrowthRune):
    name = '[chartreuse4 bold]Perfect Prefix Growth Rune[/chartreuse4 bold]'
    description = 'Adds 1 random prefix above level 55 to the selected piece of equipment'
    affixesToAdd = 1
    minAffixLevel = 55
    minItemLevel = 55
    successEntropy = 0.25

class SuffixGrowthRune(BaseGrowthRune):
    name = '[sea_green2]Suffix Growth Rune[/sea_green2]'
    description = 'Adds 1 random suffix to the selected piece of equipment'
    affixesToAdd = 1
    minAffixLevel = 0
    successEntropy = 0.07

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

class PerfectSuffixGrowthRune(SuffixGrowthRune):
    name = '[chartreuse4 bold]Perfect Suffix Growth Rune[/chartreuse4 bold]'
    description = 'Adds 1 random suffix above level 55 to the selected piece of equipment'
    affixesToAdd = 1
    minAffixLevel = 55
    minItemLevel = 55
    successEntropy = 0.25

class DuplicatingGrowthRune(BaseGrowthRune):
    name = '[turquoise2 bold]Duplicating Growth Rune[/turquoise2 bold]'
    description = 'Adds a random affix above level 20 based on the tags of existing affixes. Functions as a basic Growth Rune if no valid tags.'
    affixesToAdd = 1
    minAffixLevel = 20
    minItemLevel = 20
    successEntropy = 0.2

    def apply(self, item) -> CraftResult:
        if item.entropyLocked or item.destabilised:
            return CraftResult(
                outcome=CraftOutcome.NO_EFFECT,
                message='Item cannot be modified'
            )
        if item.level < self.minItemLevel:
            return CraftResult(
                outcome=CraftOutcome.NO_EFFECT,
                message='Item level is too low'
            )
        
        slot = self.getRandomEmptySlot(item)
        if slot is None:
            return CraftResult(
                outcome=CraftOutcome.NO_EFFECT,
                message='Item has no empty affix slots'
            )

        categoryWeights = {}
        for s in item.prefixSlots + item.suffixSlots:
            if s.affix:
                for cat in s.affix.categories:
                    categoryWeights[cat] = categoryWeights.get(cat, 0) + 1

        if not categoryWeights:
            super().apply(item)

        equipType = item.slot
        affixType = 'prefixes' if slot.kind == 'prefix' else 'suffixes'
        availableAffixes = AFFIX_POOL[equipType][affixType]

        prefixExcluded, suffixExcluded = item.getExcludedIds()
        excludedIds = prefixExcluded if slot.kind == 'prefix' else suffixExcluded

        validAffixes = []
        weights = []

        for affixId, affix in availableAffixes.items():
            if affix.levelReq > item.level:
                continue
            if affixId in excludedIds:
                continue
            baseId = affix.id.split('_t')[0]
            if baseId in excludedIds:
                continue

            weight = 1
            for cat in affix.categories:
                if cat in categoryWeights:
                    weight += categoryWeights[cat] * 10

            validAffixes.append(affix)
            weights.append(weight)

        if not validAffixes:
            return CraftResult(
                outcome=CraftOutcome.NO_EFFECT,
                message='Item has no empty affix slots or has no valid affixes available'
            )
        
        chosenAffix = random.choices(validAffixes, weights=weights, k=1)[0]

        newAffix = Affix(
            id=chosenAffix.id,
            name=chosenAffix.name,
            levelReq=chosenAffix.levelReq,
            tier=chosenAffix.tier,
            stat=chosenAffix.stat,
            minVal=chosenAffix.minVal,
            maxVal=chosenAffix.maxVal,
            isPercent=chosenAffix.isPercent,
            kind=chosenAffix.kind,
            weight=chosenAffix.weight,
            categories=chosenAffix.categories
        )
        newAffix.rollValue()

        slot.affix = newAffix
        item.update()
        item._generateName()
        item.addEntropy(self.successEntropy)
        
        return CraftResult(
                outcome=CraftOutcome.SUCCESS,
                message=f'Added {self.affixesToAdd} affixes',
                entropyAdded=self.successEntropy
            )

class ImitatingGrowthRune(BaseGrowthRune):
    name = '[light_goldenrod1 bold underline]Imitating Growth Rune[/light_goldenrod1 bold underline]'
    description = 'Adds a random affix with level between the highest and lowest level existing affixes.'
    affixesToAdd = 1
    minItemLevel = 30
    successEntropy = 0.2

    def apply(self, item) -> CraftResult:
        if item.entropyLocked or item.destabilised:
            return CraftResult(
                outcome=CraftOutcome.NO_EFFECT,
                message='Item cannot be modified'
            )
        if item.level < self.minItemLevel:
            return CraftResult(
                outcome=CraftOutcome.NO_EFFECT,
                message='Item level is too low'
            )
        
        slot = self.getRandomEmptySlot(item)
        if slot is None:
            return CraftResult(
                outcome=CraftOutcome.NO_EFFECT,
                message='Item has no empty affix slots'
            )
        
        existingAffixes = [s.affix for s in item.prefixSlots + item.suffixSlots if s.affix]

        if not existingAffixes:
            minLevel = min(1, item.level - 15)
            maxLevel = item.level
        else:
            minLevel = min(a.levelReq for a in existingAffixes)
            maxLevel = max(a.levelReq for a in existingAffixes)

        equipType = item.slot
        affixType = 'prefixes' if slot.kind == 'prefix' else 'suffixes'
        availableAffixes = AFFIX_POOL[equipType][affixType]
        
        prefixExcluded, suffixExcluded = item.getExcludedIds()
        excludedIds = prefixExcluded if slot.kind == 'prefix' else suffixExcluded
        
        validAffixes = []
        
        for affixId, affix in availableAffixes.items():
            if minLevel <= affix.levelReq <= maxLevel:
                if affixId not in excludedIds:
                    baseId = affixId.split('_t')[0]
                    if baseId not in excludedIds:
                        validAffixes.append(affix)
        
        if not validAffixes:
            return CraftResult(
                outcome=CraftOutcome.NO_EFFECT,
                message='Item has no empty affix slots or no valid affixes available'
            )

        chosenAffix = random.choice(validAffixes)
        
        newAffix = Affix(
            id=chosenAffix.id,
            name=chosenAffix.name,
            levelReq=chosenAffix.levelReq,
            tier=chosenAffix.tier,
            stat=chosenAffix.stat,
            minVal=chosenAffix.minVal,
            maxVal=chosenAffix.maxVal,
            isPercent=chosenAffix.isPercent,
            kind=chosenAffix.kind,
            weight=chosenAffix.weight,
            categories=chosenAffix.categories
        )
        newAffix.rollValue()
        
        slot.affix = newAffix
        item.update()
        item._generateName()
        item.addEntropy(self.successEntropy)
        
        return CraftResult(
                outcome=CraftOutcome.SUCCESS,
                message=f'Added {self.affixesToAdd} affixes',
                entropyAdded=self.successEntropy
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

    'duplicating': DuplicatingGrowthRune(),

    'imitating': ImitatingGrowthRune()
}

"""
IDEAS:
- specific category rune
"""