from .base import CraftingItem, CraftOutcome, CraftResult
from scripts.items.items import ItemRarity, RARITY_VALUES
from scripts.items.equipment import ENTROPY_RESISTANCE
import random
from typing import Dict

class BaseRarityRune(CraftingItem):
    fromRarity: ItemRarity | None = None
    toRarity: ItemRarity | None = None

    def _serialise(self):
        temp = super()._serialise()
        temp['fromRarity'] = self.fromRarity
        temp['toRarity'] = self.toRarity
        return temp
    
    @classmethod
    def deserialise(cls, data):
        rune = super().deserialise(data)
        rune.fromRarity = data.get('fromRarity', None)
        rune.toRarity = data.get('toRarity', None)
        return rune

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
                    message='Item level too low'
                )
            
        if self.fromRarity is not None:
            if item.rarity != self.fromRarity:
                return CraftResult(
                    outcome=CraftOutcome.NO_EFFECT,
                    message='Item is the incorrect rarity'
            )
            
        if self.toRarity is not None:
            item.rarity = self.toRarity

        item.baseEntropyResistance = ENTROPY_RESISTANCE[item.rarity]
        valStatMult = len(item.stats)
        if valStatMult == 0:
            valStatMult = 1
        item.value = 500 * RARITY_VALUES[item.rarity.value] * valStatMult

        self._recalculateAffixSlots(item)

        item.update()
        item._generateName()
        item.addEntropy(self.successEntropy)

        return CraftResult(
                outcome=CraftOutcome.SUCCESS,
                message='Item rarity successfully upgraded',
                entropyAdded=self.successEntropy
            )
    
    def _recalculateAffixSlots(self, item):
        bases = {
            ItemRarity.COMMON: ([1], [1]),
            ItemRarity.UNCOMMON: ([1, 2], [1, 2]),
            ItemRarity.RARE: ([2], [2]),
            ItemRarity.EPIC: ([2, 3], [2, 3]),
            ItemRarity.LEGENDARY: ([3], [3])
        }

        basePrefixes, baseSuffixes = bases.get(item.rarity, [[1], [1]])
        extra = item.level // 34
        newPrefixCount = random.choice(basePrefixes) + extra
        newSuffixCount = random.choice(baseSuffixes) + extra

        currentPrefixCount = len(item.prefixSlots)
        if newPrefixCount > currentPrefixCount:
            from scripts.items.equipment import AffixSlot
            for _ in range(newPrefixCount - currentPrefixCount):
                item.prefixSlots.append(AffixSlot('prefix'))
        elif newPrefixCount < currentPrefixCount:
            while len(item.prefixSlots) > newPrefixCount:
                if item.prefixSlots[-1].isEmpty:
                    item.prefixSlots.pop()
                else:
                    break

        currentSuffixCount = len(item.suffixSlots)
        if newSuffixCount > currentSuffixCount:
            from scripts.items.equipment import AffixSlot
            for _ in range(newSuffixCount - currentSuffixCount):
                item.suffixSlots.append(AffixSlot('suffix'))
        elif newSuffixCount < currentSuffixCount:
            while len(item.suffixSlots) > newSuffixCount:
                if item.suffixSlots[-1].isEmpty:
                    item.suffixSlots.pop()
                else:
                    break

class CommonRarityRune(BaseRarityRune):
    name = '[green_yellow]Rarity Rune: Uncommon[/green_yellow]'
    description = 'Updates a common item to uncommon rarity.'
    fromRarity = ItemRarity.COMMON
    toRarity = ItemRarity.UNCOMMON
    minItemLevel = 1
    successEntropy = 0.05
    dropWeight = 175

class UncommonRarityRune(BaseRarityRune):
    name = '[dodger_blue2 bold]Rarity Rune: Rare[/dodger_blue2 bold]'
    description = 'Upgrades an uncommon item to rare rarity.'
    fromRarity = ItemRarity.UNCOMMON
    toRarity = ItemRarity.RARE
    minItemLevel = 10
    successEntropy = 0.1
    dropWeight = 100

class RareRarityRune(BaseRarityRune):
    name = '[medium_purple bold]Rarity Rune: Epic[/medium_purple bold]'
    description = 'Upgrades a rare item to epic rarity.'
    fromRarity = ItemRarity.RARE
    toRarity = ItemRarity.EPIC
    minItemLevel = 20
    successEntropy = 0.15
    dropWeight = 65

class EpicRarityRune(BaseRarityRune):
    name = '[gold1 bold underline]Rarity Rune: Legendary[/gold1 bold underline]'
    description = 'Upgrades an epic item to legendary rarity.'
    fromRarity = ItemRarity.EPIC
    toRarity = ItemRarity.LEGENDARY
    minItemLevel = 40
    successEntropy = 0.2
    dropWeight = 35

class LegendaryRarityRune(BaseRarityRune):
    name = '[red3 bold underline]Rarity Rune: Mythic[/red3 bold underline]'
    description = 'Upgrades a legendary item to mythic rarity and removes some entropy from the item.'
    fromRarity = ItemRarity.LEGENDARY
    toRarity = ItemRarity.MYTHIC
    minItemLevel = 65
    successEntropy = -0.1
    dropWeight = 2

class ChaosRarityRune(BaseRarityRune):
    name = '[magenta bold italic]Chaos Rarity Rune[/magenta bold italic]'
    description = 'Upgrades a common item to a random rarity (uncommon 40%, rare 30%, epic 20%, legendary 10%).'
    fromRarity = ItemRarity.COMMON
    minItemLevel = 10
    successEntropy = 0.25
    dropWeight = 80

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

        if item.rarity != ItemRarity.COMMON:
            return CraftResult(
                outcome=CraftOutcome.NO_EFFECT,
                message='Item rarity is not common'
            )

        rarities = [ItemRarity.UNCOMMON, ItemRarity.RARE, ItemRarity.EPIC, ItemRarity.LEGENDARY]
        weights = [50, 30, 15, 5]

        self.toRarity = random.choices(rarities, weights=weights)[0]

        return super().apply(item)

RARITY_RUNES: Dict[str, BaseRarityRune] = {
    'common': CommonRarityRune(),
    'uncommon': UncommonRarityRune(),
    'rare': RareRarityRune(),
    'epic': EpicRarityRune(),
    'legendary': LegendaryRarityRune(),
    'chaos': ChaosRarityRune()
}

"""
IDEAS:
ascension rarity rune:
    - always upgrades item to next tier rarity
"""