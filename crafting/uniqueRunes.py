from .base import CraftingItem, CraftOutcome, CraftResult
from scripts.affixes import rollAffix, Affix
import random
import json
from typing import Dict

class ImmutableRune(CraftingItem):
    name = '[steel_blue bold underline]Immutable Rune[/steel_blue bold underline]'
    description = 'Permanently locks a single random affix. Locked affixes cannot be modified.'
    minItemLevel = 50
    successEntropy = 0.4

    def apply(self, item):
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
        
        if item.locked:
            return CraftResult(
                outcome=CraftOutcome.NO_EFFECT,
                message='Item already contains a locked affix'
            )

        candidates = [
            s for s in item.prefixSlots + item.suffixSlots
            if not s.isEmpty and not s.locked
        ]

        if not candidates:
            return CraftResult(
                outcome=CraftOutcome.NO_EFFECT,
                message='Item has no affixes to lock'
            )
        
        slot = random.choice(candidates)
        slot.lock()

        item.addEntropy(self.successEntropy)
        return CraftResult(
            outcome=CraftOutcome.SUCCESS,
            message='Successfully locked an affix',
            entropyAdded=self.successEntropy
        )

class PreservationRune(CraftingItem):
    name = '[spring_green3 bold]Preservation Rune[/spring_green3 bold]'
    description = "Prevents entropy gain on the next crafting attempt. Permanently reduces entropy resistance by 10%"
    minItemLevel = 30
    successEntropy = 0.15

    def apply(self, item):
        if item.destabilised or item.entropyLocked:
            return CraftResult(
                outcome=CraftOutcome.NO_EFFECT,
                message='Item cannot be modified'
            )
        
        if item.entropyPreserved:
            return CraftResult(
                outcome=CraftOutcome.NO_EFFECT,
                message='Item already has an entropy lock applied'
            )
        
        if item.level < self.minItemLevel:
            return CraftResult(
                outcome=CraftOutcome.NO_EFFECT,
                message='Item level too low'
            )
        
        item.update()
        item.addEntropy(self.successEntropy)
        item.entropyPreserved = True
        item.numPreserved += 1
        return CraftResult(
            outcome=CraftOutcome.SUCCESS,
            message='Item has gained an entropy lock',
            entropyAdded=self.successEntropy
        )

class EchoingRune(CraftingItem):
    name = '[deep_sky_blue3 bold underline]Echoing Rune[/deep_sky_blue3 bold underline]'
    description = 'Adds 1 random affix to the selected piece of equipment. Its value will be copied randomly from an already existing affix.'
    minItemLevel = 30
    successEntropy = 0.15

    def getRandomEmptySlot(self, item):
        emptyPrefixes = [s for s in item.prefixSlots if s.isEmpty]
        emptySuffixes = [s for s in item.suffixSlots if s.isEmpty]
        allEmpty = emptyPrefixes + emptySuffixes
        if not allEmpty:
            return None
        
        return random.choice(allEmpty)
    
    def getCopiedValue(self, item):
        values = []
        for a in item.stats:
            values.append(a.value)
        return random.choice(values)

    def apply(self, item):
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
        added = 0

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

        value = self.getCopiedValue(item)

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
            return CraftResult(
                outcome=CraftOutcome.NO_EFFECT,
                message='No valid affixes available to roll'
            )
        
        affix.baseValue = value
        slot.affix = affix
        added += 1

        if added == 0:
            return CraftResult(
                outcome=CraftOutcome.NO_EFFECT,
                message='No affix was added'
            )
        
        item.update()
        item._generateName()
        item.addEntropy(self.successEntropy)
        return CraftResult(
            outcome=CraftOutcome.NO_EFFECT,
            message='Echoing Rune successfully applied',
            entropyAdded=self.successEntropy
        )

class SoulboundRune(CraftingItem):
    name = '[gold3 bold underline]Soulbound Rune[/gold3 bold underline]'
    description = 'Adds a powerful unique affix to the item, ignoring affix restrictions. Each item can only have 1 soulbound affix. Permanently reduces entropy resistance by 15%.'
    minItemLevel = 75
    successEntropy = 0.5

    def __init__(self):
        super().__init__()
        self._loadSoulboundAffixes()

    def _loadSoulboundAffixes(self):
        with open('crafting/data/soulboundAffixes.json', 'r') as f:
            self.soulboundData = json.load(f)

    def getRandomEmptySlot(self, item):
        emptyPrefixes = [s for s in item.prefixSlots if s.isEmpty]
        emptySuffixes = [s for s in item.suffixSlots if s.isEmpty]
        allEmpty = emptyPrefixes + emptySuffixes
        if not allEmpty:
            return None
        return random.choice(allEmpty)
    
    def apply(self, item):
        if item.entropyLocked or item.destabilised or item.soulbound:
            return CraftResult(
                outcome=CraftOutcome.NO_EFFECT,
                message='Item cannot be modified'
            )
        if item.level < self.minItemLevel:
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
        
        equipType = item.slot
        affixType = 'prefixes' if slot.kind == 'prefix' else 'suffixes'

        if equipType not in self.soulboundData:
            return CraftResult(
                outcome=CraftOutcome.NO_EFFECT,
                message=f'Rolling a soulbound affix failed: {equipType} not in data.'
            )
        if affixType not in self.soulboundData[equipType]:
            return CraftResult(
                outcome=CraftOutcome.NO_EFFECT,
                message=f'Rolling a soulbound affix failed: {affixType} not in data[{equipType}]'
            )
        
        availableAffixes = self.soulboundData[equipType][affixType]

        if not availableAffixes:
            return CraftResult(
                outcome=CraftOutcome.NO_EFFECT,
                message='No available affixes'
            )
        
        validAffixes = {
            affixId: affixData
            for affixId, affixData in availableAffixes.items()
            if affixData.get('levelReq', 0) <= item.level
        }
        if not validAffixes:
            return CraftResult(
                outcome=CraftOutcome.NO_EFFECT,
                message='Affix pool exhausted, no valid soulbound affixes available'
            )
        
        affixId = random.choice(list(validAffixes.keys()))
        affixData = validAffixes[affixId]

        minVal = affixData['min']
        maxVal = affixData['max']

        if isinstance(minVal, float) or isinstance(maxVal, float):
            value = round(random.uniform(minVal, maxVal), 2)
        else:
            value = random.randint(int(minVal), int(maxVal))

        soulboundAffix = Affix(
            id=f"soulbound_{affixId}",
            name=affixData['name'],
            levelReq=affixData.get('levelReq', 75),
            tier=0,
            stat=affixData['stat'],
            minVal=minVal,
            maxVal=maxVal,
            isPercent=affixData.get('isPercent', False),
            kind=slot.kind,
            weight=0,
            categories=affixData.get('categories', ['soulbound'])
        )
        soulboundAffix.baseValue = value
        soulboundAffix.soulbound = True

        slot.affix = soulboundAffix
        
        item.update()
        item._generateName()
        item.addEntropy(self.successEntropy)

        return CraftResult(
                outcome=CraftOutcome.SUCCESS,
                message='Item successfully gained a soulbound affix',
                entropyAdded=self.successEntropy
            )

UNIQUE_RUNES: Dict[str, CraftingItem] = {
    'immutable': ImmutableRune(),
    'preservation': PreservationRune(),
    'echoing': EchoingRune(),
    'soulbound': SoulboundRune()
}

"""
IDEAS:
- foresight rune:
    - lets you see the outcome of the next rune used before it is actually used
    - displays item after craft would be complete, asked for confirmation y/n whether to actually apply item
- parallel rune:
    - duplicates an item, copying it 1 for 1 and making both versions unmodifiable
"""