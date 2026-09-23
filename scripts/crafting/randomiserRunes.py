from .base import CraftingItem, CraftOutcome, CraftResult
from scripts.items.affixes import getTierVariants, Affix, rollAffix
import random
from typing import Dict

class BaseRandomiserRune(CraftingItem):

    def getValidAffixes(self, item):
        valid = []
        for slot in item.prefixSlots + item.suffixSlots:
            if slot.isEmpty:
                continue
            if slot.locked:
                continue
            valid.append(slot.affix)
        return valid
    
    def apply(self, item, player=None) -> CraftResult:
        if not item.craftable:
            return CraftResult(
                outcome=CraftOutcome.NO_EFFECT,
                message='Item cannot be modified'
            )
        if self.minItemLevel is not None and item.level < self.minItemLevel:
            return CraftResult(
                outcome=CraftOutcome.NO_EFFECT,
                message='Item level too low'
            )
        return CraftResult(
                outcome=CraftOutcome.SUCCESS,
                message='Item successfully randomised'
            )
    
class ValueRandomiserRune(BaseRandomiserRune):
    name = '[gold1]Value Randomiser Rune[/gold1]'
    description = "Rerolls numeric values of all affixes on an item within its current tier."
    successEntropy = 0.15
    minItemLevel = 15
    dropWeight = 150

    def apply(self, item, player=None) -> CraftResult:
        output = super().apply(item, player=None)
        if output.outcome != CraftOutcome.SUCCESS:
            return output
        affixes = self.getValidAffixes(item)

        if not affixes:
            return CraftResult(
                outcome=CraftOutcome.NO_EFFECT,
                message='No affixes to randomise'
            )
        
        for affix in affixes:
            affix.rollValue()

        item.update()
        item.addEntropy(self.successEntropy)

        return CraftResult(
                outcome=CraftOutcome.SUCCESS,
                message='Affix values successfully randomised',
                entropyAdded=self.successEntropy
            )
    
class GreaterValueRandomiserRune(BaseRandomiserRune):
    name = '[gold3 bold]Greater Value Randomiser Rune[/gold3 bold]'
    description = 'Rerolls numeric values of all affixes on an item twice within its current tier, keeping the highest roll.'
    successEntropy = 0.25
    minItemLevel = 30
    dropWeight = 65

    def apply(self, item, player=None):
        output = super().apply(item, player=None)
        if output.outcome != CraftOutcome.SUCCESS:
            return output
        affixes = self.getValidAffixes(item)

        if not affixes:
            return CraftResult(
                outcome=CraftOutcome.NO_EFFECT,
                message="No affixes to randomise"
            )
        
        for affix in affixes:
            v1 = affix.rollValue()
            v2 = affix.rollValue()
            affix.baseValue = max(v1, v2)

        item.update()
        item.addEntropy(self.successEntropy)

        return CraftResult(
            outcome=CraftOutcome.SUCCESS,
            message="Successfully randomised all affix values"
        )
        
class PerfectValueRandomiserRune(BaseRandomiserRune):
    name = '[yellow bold underline]Perfect Value Randomiser Rune[/yellow bold underline]'
    description = 'Rerolls numeric values of all affixes 5 times within in its current tier, keeping the highest roll.'
    successEntropy = 0.35
    minItemLevel = 50
    dropWeight = 15

    def apply(self, item, player=None):
        output = super().apply(item, player=None)
        if output.outcome != CraftOutcome.SUCCESS:
            return output
        affixes = self.getValidAffixes(item)

        if not affixes:
            return CraftResult(
                outcome=CraftOutcome.NO_EFFECT,
                message="No affixes to randomise"
            )
        
        for affix in affixes:
            values = []
            for _ in range(10):
                values.append(affix.rollValue())
            affix.baseValue = max(values)
        
        item.update()
        item.addEntropy(self.successEntropy)

        return CraftResult(
            outcome=CraftOutcome.SUCCESS,
            message="Successfully randomised affix values"
        )

class BaseTierRandomiserRune(BaseRandomiserRune):
    numRolls: int

    def apply(self, item, player=None) -> CraftResult:
        output = super().apply(item, player=None)
        if output.outcome != CraftOutcome.SUCCESS:
            return output
        validSlots = [
            s for s in item.prefixSlots + item.suffixSlots
            if not s.isEmpty and not s.locked
        ]

        if not validSlots:
            return CraftResult(
                outcome=CraftOutcome.NO_EFFECT,
                message='Item has no valid affix slots to randomise'
            )
        
        changed = 0

        for slot in validSlots:
            affix = slot.affix
            variants = getTierVariants(item, affix)

            if self.minAffixTier is not None:
                variants = [a for a in variants if a.tier >= self.minAffixTier]
            if self.maxTierDelta is not None:
                tiers = sorted({a.tier for a in variants})
                topTiers = tiers[-self.maxTierDelta:]
                variants = [a for a in variants if a.tier in topTiers]

            if not variants:
                continue

            affixRolls = []
            for _ in range(self.numRolls):
                a: Affix = random.choice(variants)
                affixRolls.append(a)

            chosen = sorted(affixRolls, key=lambda a: a.tier)[-1]

            newAffix = Affix(
                id=chosen.id,
                name=chosen.name,
                levelReq=chosen.levelReq,
                tier=chosen.tier,
                stat=chosen.stat,
                slot=chosen.slot,
                minVal=chosen.minVal,
                maxVal=chosen.maxVal,
                isPercent=chosen.isPercent,
                kind=chosen.kind,
                weight=chosen.weight,
                categories=chosen.categories,
            )
            newAffix.rollValue()
            slot.affix = newAffix
            changed += 1

        if changed == 0:
            return CraftResult(
                outcome=CraftOutcome.NO_EFFECT,
                message='Affixes were not changed'
            )
        
        item.update()
        item.addEntropy(self.successEntropy)
        item._generateName()

        return CraftResult(
                outcome=CraftOutcome.SUCCESS,
                message='Affix tiers successfully randomised',
                entropyAdded=self.successEntropy
            )

class TierRandomiserRune(BaseTierRandomiserRune):
    name = '[medium_purple]Tier Randomiser Rune[/medium_purple]'
    description = 'Randomises the tiers of all affixes on an item. Cannot roll tiers higher than the item allows.'
    numRolls = 1
    successEntropy = 0.2
    minItemLevel = 20
    dropWeight = 80

class GreaterTierRandomiserRune(BaseTierRandomiserRune):
    name = '[dark_magenta bold]Greater Tier Randomiser Rune[/dark_magenta bold]'
    description = 'Randomises the tiers of all affixes twice, keeping the highest tier rolled. Cannot roll tiers higher than the item allows.'
    numRolls = 2
    successEntropy = 0.3
    minItemLevel = 40
    dropWeight = 35

class PerfectTierRandomiserRune(BaseTierRandomiserRune):
    name = '[plum1 bold underline]Perfect Tier Randomiser Rune[/plum1 bold underline]'
    description = 'Randomises the tiers of all affixes 4 times, keeping the highest tier rolled. Cannot roll tiers higher than the item allows.'
    numRolls = 4
    successEntropy = 0.4
    minItemLevel = 60
    dropWeight = 15

class BaseAffixRandomiserRune(BaseRandomiserRune):

    def apply(self, item, player=None) -> CraftResult:
        output = super().apply(item, player=None)
        if output.outcome != CraftOutcome.SUCCESS:
            return output
        validSlots = [
            s for s in item.prefixSlots + item.suffixSlots
            if not s.isEmpty and not s.locked
        ]

        if not validSlots:
            return CraftResult(
                outcome=CraftOutcome.NO_EFFECT,
                message='Item has no valid affix slots to randomise'
            )
        
        changed = 0

        excludeIds = []
        for slot in validSlots:
            newAffix = rollAffix(
                equipType=slot.affix.slot,
                affixType=slot.kind,
                itemLevel=item.level,
                rarity=item.rarity,
                excludeIds=excludeIds,
                tierBias=0.0,
                defenseType=item.defenseType,
                minAffixLevel=self.minAffixLevel,
                noEmpty=True
            )
            if newAffix is None:
                continue

            excludeIds.append(newAffix.id.rsplit('_t', 1)[0])
            slot.affix = newAffix
            changed += 1

        if changed == 0:
            return CraftResult(
                outcome=CraftOutcome.NO_EFFECT,
                message='Affixes were not changed'
            )
        
        item.update()
        item._generateName()
        item.addEntropy(self.successEntropy)
        
        return CraftResult(
                outcome=CraftOutcome.SUCCESS,
                message='Affixes successfully randomised',
                entropyAdded=self.successEntropy
            )

class AffixRandomiserRune(BaseAffixRandomiserRune):
    name = '[slate_blue3]Affix Randomiser Rune[/slate_blue3]'
    description = 'Replaces each affix on an item with another random affix.'
    successEntropy = 0.15
    minItemLevel = 15
    dropWeight = 150

class GreaterAffixRandomiserRune(BaseAffixRandomiserRune):
    name = '[royal_blue1 bold]Greater Affix Randomiser Rune[/royal_blue1 bold]'
    description = 'Replaces each affix on an item with another random affix above level 30.'
    successEntropy = 0.25
    minAffixLevel = 30
    minItemLevel = 35
    dropWeight = 85

class PerfectAffixRandomiserRune(BaseAffixRandomiserRune):
    name = '[steel_blue bold underline]Perfect Affix Randomiser Rune[/steel_blue bold underline]'
    description = 'Replaces each affix on an item with another random affix above level 50.'
    successEntropy = 0.45
    minAffixLevel = 50
    minItemLevel = 60
    dropWeight = 15

class BaseTypeRandomiserRune(BaseRandomiserRune):
    name = '[dodger_blue2]Base Type Randomiser Rune[/dodger_blue2]'
    description = 'Randomises the item into a different base type of the same tier (a different weapon type, armour/shield defense type, or ring/amulet archetype), excluding its current one.'
    successEntropy = 0.05
    dropWeight = 150

    def apply(self, item, player=None):
        from scripts.items.equipment import Equipment
        output = super().apply(item, player=None)
        if output.outcome != CraftOutcome.SUCCESS:
            return output

        if not Equipment._rerollBaseType(item):
            return CraftResult(
                CraftOutcome.NO_EFFECT,
                message='Item has no other base type to randomise into'
            )

        item.addEntropy(self.successEntropy)
        item.update()
        item._generateName()

        return CraftResult(
            CraftOutcome.SUCCESS,
            message='Item base type successfully randomised',
            entropyAdded=self.successEntropy
        )

class MasteryRandomiserRune(CraftingItem):
    name = '[orange4 bold]Mastery Randomiser Rune[/orange4 bold]'
    description = 'Randomises the mastery on an item between 1 and 20. The item must have mastery already.'
    successEntropy = 0.1
    minItemLevel = 20
    dropWeight = 100

    def apply(self, item, player=None):
        if not item.craftable:
            return CraftResult(
                outcome=CraftOutcome.NO_EFFECT,
                message='Item cannot be modified'
            )
        if item.level < self.minItemLevel:
            return CraftResult(
                outcome=CraftOutcome.NO_EFFECT,
                message="Item level too low."
            )

        if item.mastery == 0:
            return CraftResult(
                outcome=CraftOutcome.NO_EFFECT,
                message="Item does not have any mastery to randomise"
            )

        diff = 0
        while diff == 0:
            newMastery = random.randint(1, 20)
            diff = newMastery - item.mastery

        item.gainMastery(diff)
        item.addEntropy(self.successEntropy)

        return CraftResult(
            outcome=CraftOutcome.SUCCESS,
            message=f"Mastery successfully randomised. New Mastery: {newMastery} ({'Gained' if diff > 0 else 'Lost'} {abs(diff)} Mastery)"
        )

RANDOMISER_RUNES: Dict[str, BaseRandomiserRune] = {
    'value': ValueRandomiserRune(),
    'greater_value': GreaterValueRandomiserRune(),
    'perfect_value': PerfectValueRandomiserRune(),

    'tier': TierRandomiserRune(),
    'greater_tier': GreaterTierRandomiserRune(),
    'perfect_tier': PerfectTierRandomiserRune(),

    'affix': AffixRandomiserRune(),
    'greater_affix': GreaterAffixRandomiserRune(),
    'perfect_affix': PerfectAffixRandomiserRune(),

    'base_type': BaseTypeRandomiserRune(),
    'mastery': MasteryRandomiserRune(),
}

"""
IDEAS:
- only randomise prefix rune
- only randomise suffix rune
"""