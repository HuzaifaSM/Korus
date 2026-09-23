"""
runes to add that don't exist:
ascension rarity rune: always upgrades an item's rarity to next tier, scaling entropy cost based on tier
"""

from .base import CraftingItem, CraftOutcome, CraftResult
from .erasingRune import BaseErasingRune
from .growthRune import BaseGrowthRune
from .rarityRune import BaseRarityRune
from ..items.affixes import resolveAffixPoolKey, Affix, AFFIX_POOL, MARKET_AFFIX_POOL, rollAffix
from ..items.items import ItemRarity
import random
from typing import Dict, Optional


RESISTANCE_EXCLUDED_STATS = frozenset({'crit_resistance', 'entropy_resistance'})

def _isResistanceAffix(affix: Affix) -> bool:
    return 'resistance' in affix.categories and affix.stat not in RESISTANCE_EXCLUDED_STATS

def _nonResistanceSuffixBaseIds(equipType: str) -> set:
    """Base ids (no _tN suffix) of every suffix in equipType's pool that ISN'T a resistance affix -
    handed to rollAffix as excludeIds so it can only land on a real resistance roll."""
    pool = AFFIX_POOL.get(equipType, {}).get('suffixes', {})
    return {
        affixId.rsplit('_t', 1)[0]
        for affixId, affix in pool.items()
        if not _isResistanceAffix(affix)
    }

class PassiveErasingRune(BaseErasingRune):
    name = '[red3]Passive Erasing Rune[/red3]'
    description = 'Removes 1 random offensive-related affix.'
    affixesToRemove = 1
    minItemLevel = 20
    successEntropy = 0.1

    def getRemovableSlots(self, item):
        slots = super().getRemovableSlots(item)
        return [s for s in slots if 'offensive' in s.affix.categories]

class RecklessErasingRune(BaseErasingRune):
    name = '[steel_blue]Reckless Erasing Rune[/steel_blue]'
    description = 'Removes 1 random defensive affix.'
    affixesToRemove = 1
    minItemLevel = 20
    successEntropy = 0.1

    def getRemovableSlots(self, item):
        slots = super().getRemovableSlots(item)
        return [s for s in slots if 'defensive' in s.affix.categories]

class ShallowErasingRune(BaseErasingRune):
    name = '[cyan]Shallow Erasing Rune[/cyan]'
    description = 'Removes 1 random utility affix'
    affixesToRemove = 1
    minItemLevel = 20
    successEntropy = 0.1

    def getRemovableSlots(self, item):
        slots = super().getRemovableSlots(item)
        return [s for s in slots if 'utility' in s.affix.categories]

class WastingErasingRune(BaseErasingRune):
    name = '[green]Wasting Erasing Rune[/green]'
    description = 'Removes 1 random health-related affix.'
    affixesToRemove = 1
    minItemLevel = 20
    successEntropy = 0.08

    def getRemovableSlots(self, item):
        slots = super().getRemovableSlots(item)
        return [s for s in slots if 'health' in s.affix.categories]

class BrittleErasingRune(BaseErasingRune):
    name = '[purple]Brittle Erasing Rune[/purple]'
    description = 'Removes 1 random resistance affix.'
    affixesToRemove = 1
    minItemLevel = 20
    successEntropy = 0.08

    def getRemovableSlots(self, item):
        slots = super().getRemovableSlots(item)
        return [s for s in slots if 'resistance' in s.affix.categories]

class UnluckyErasingRune(BaseErasingRune):
    name = '[orange1]Unlucky Erasing Rune[/orange1]'
    description = 'Removes 1 random critical-related affix.'
    affixesToRemove = 1
    minItemLevel = 20
    successEntropy = 0.08

    def getRemovableSlots(self, item):
        slots = super().getRemovableSlots(item)
        return [s for s in slots if 'critical' in s.affix.categories]


class DuplicatingGrowthRune(BaseGrowthRune):
    name = '[turquoise2 bold]Duplicating Growth Rune[/turquoise2 bold]'
    description = 'Adds a random affix above level 20 based on the tags of existing affixes. Functions as a basic Growth Rune if no valid tags.'
    affixesToAdd = 1
    minAffixLevel = 20
    minItemLevel = 20
    successEntropy = 0.2

    def apply(self, item, player=None) -> CraftResult:
        if not item.craftable:
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
            super().apply(item, player=None)

        equipType = resolveAffixPoolKey(item)
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
            baseId = affix.id.rsplit('_t', 1)[0]
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
            slot=item.slot,
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

    def apply(self, item, player=None) -> CraftResult:
        if not item.craftable:
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

        equipType = resolveAffixPoolKey(item)
        affixType = 'prefixes' if slot.kind == 'prefix' else 'suffixes'
        availableAffixes = AFFIX_POOL[equipType][affixType]
        
        prefixExcluded, suffixExcluded = item.getExcludedIds()
        excludedIds = prefixExcluded if slot.kind == 'prefix' else suffixExcluded
        
        validAffixes = []
        
        for affixId, affix in availableAffixes.items():
            if minLevel <= affix.levelReq <= maxLevel:
                if affixId not in excludedIds:
                    baseId = affixId.rsplit('_t', 1)[0]
                    if baseId not in excludedIds:
                        validAffixes.append(affix)
        
        if not validAffixes:
            return CraftResult(
                outcome=CraftOutcome.NO_EFFECT,
                message='Item has no empty affix slots or no valid affixes available'
            )

        chosenAffix = random.choice(validAffixes)
        added: list[Affix] = []
        
        newAffix = Affix(
            id=chosenAffix.id,
            name=chosenAffix.name,
            levelReq=chosenAffix.levelReq,
            tier=chosenAffix.tier,
            stat=chosenAffix.stat,
            slot=item.slot,
            minVal=chosenAffix.minVal,
            maxVal=chosenAffix.maxVal,
            isPercent=chosenAffix.isPercent,
            kind=chosenAffix.kind,
            weight=chosenAffix.weight,
            categories=chosenAffix.categories
        )
        newAffix.rollValue()
        added.append(newAffix)
        addedStr = ""
        for a in added:
            addedStr += f"[dim green1]- {a}[/dim green1]"

        slot.affix = newAffix
        item.update()
        item._generateName()
        item.addEntropy(self.successEntropy)

        return CraftResult(
                outcome=CraftOutcome.SUCCESS,
                message=f'Added {self.affixesToAdd} affixes. Added:\n{addedStr}',
                entropyAdded=self.successEntropy
            )

class ProtectiveGrowthRune(BaseGrowthRune):
    name = '[steel_blue3 bold]Protective Growth Rune[/steel_blue3 bold]'
    description = 'Adds a guaranteed resistance affix to the selected piece of equipment. Cannot be used on weapons.'
    affixesToAdd = 1
    minAffixLevel = 0
    minItemLevel = 15
    successEntropy = 0.1

    def getRandomEmptySlot(self, item):
        emptySuffixes = [s for s in item.suffixSlots if s.isEmpty]
        if not emptySuffixes:
            return None
        return random.choice(emptySuffixes)

    def apply(self, item, player=None) -> CraftResult:
        if not item.craftable:
            return CraftResult(
                outcome=CraftOutcome.NO_EFFECT,
                message='Item cannot be modified'
            )

        if self.minItemLevel is not None and item.level < self.minItemLevel:
            return CraftResult(
                outcome=CraftOutcome.NO_EFFECT,
                message='Item level is too low'
            )

        if item.slot == 'weapon':
            return CraftResult(
                outcome=CraftOutcome.NO_EFFECT,
                message='Weapons cannot roll resistances'
            )

        slot = self.getRandomEmptySlot(item)
        if slot is None:
            return CraftResult(
                outcome=CraftOutcome.NO_EFFECT,
                message='Item has no empty suffix slots'
            )

        equipType = resolveAffixPoolKey(item)
        _, suffixExcluded = item.getExcludedIds()
        excludeIds = suffixExcluded | _nonResistanceSuffixBaseIds(equipType)

        affix = rollAffix(
            equipType=equipType,
            affixType='suffixes',
            itemLevel=item.level,
            rarity=item.rarity,
            excludeIds=excludeIds,
            tierBias=0.0,
            defenseType=item.defenseType,
            minAffixLevel=self.minAffixLevel,
            noEmpty=True
        )

        if affix is None:
            return CraftResult(
                outcome=CraftOutcome.NO_EFFECT,
                message='This item cannot roll any resistances'
            )

        slot.affix = affix
        item.update()
        item._generateName()
        item.addEntropy(self.successEntropy)

        return CraftResult(
            outcome=CraftOutcome.SUCCESS,
            message=f'Added a resistance affix:\n[dim green1]- {affix}[/dim green1]',
            entropyAdded=self.successEntropy
        )

class PeddlersGrowthRune(BaseGrowthRune):
    name = "[light_goldenrod3]Peddler's Growth Rune[/light_goldenrod3]"
    description = 'Adds a guaranteed Market Affix to an item'
    affixesToAdd = 1
    minItemLevel = 20
    successEntropy = 0.2
    market = True


class UpgradingRarityRune(BaseRarityRune):
    name = '[gold3 bold]Ascension Rarity Rune[/gold3 bold]'
    description = 'Upgrades the rarity of an item to the next rarity. Does not work on Legendary, Mythic or Blank rarity items. Entropy applied increases based on item rarity.'
    minItemLevel = 10
    successEntropy = 0.07

    def apply(self, item, player=None):
        if item.rarity in [ItemRarity.LEGENDARY, ItemRarity.MYTHIC, ItemRarity.BLANK]:
            return CraftResult(
                outcome=CraftOutcome.NO_EFFECT,
                message="Ascension rarity rune cannot be applied to this item rarity."
            )
        self.successEntropy += (item.rarity.num - 1) * 0.05
        self.fromRarity = item.rarity
        self.toRarity = item.rarity + 1
        return super().apply(item, player)


FLAT_PREFIXES = ('added_', 'flat_')
PERCENT_PREFIX = 'increased_'

def _statRootAndDirection(baseId: str):
    for p in FLAT_PREFIXES:
        if baseId.startswith(p):
            return baseId[len(p):], 'flat_to_percent'
    if baseId.startswith(PERCENT_PREFIX):
        return baseId[len(PERCENT_PREFIX):], 'percent_to_flat'
    return None, None

def _pickReplacementTier(pool: dict, equipType: str, kind: str, targetBaseId: str, desiredTier: int, itemLevel: int) -> Optional[Affix]:
    tierAffixes = [a for affixId, a in pool.get(equipType, {}).get(kind, {}).items() if affixId.rsplit('_t', 1)[0] == targetBaseId]
    if not tierAffixes:
        return None
    eligible = [a for a in tierAffixes if a.levelReq <= itemLevel]
    if not eligible:
        return None
    exactTier = [a for a in eligible if a.tier == desiredTier]
    return exactTier[0] if exactTier else max(eligible, key=lambda a: a.tier)

def _cloneAffixAtTier(template: Affix, forcedKind: str) -> Affix:
    newAffix = Affix(
        id=template.id, name=template.name, levelReq=template.levelReq, tier=template.tier,
        stat=template.stat, slot=template.slot, minVal=template.minVal, maxVal=template.maxVal,
        isPercent=template.isPercent, kind=forcedKind, weight=template.weight,
        categories=list(template.categories), isGlobal=getattr(template, 'isGlobal', False),
    )
    newAffix.rollValue()
    return newAffix

class TemperingRune(CraftingItem):
    name = '[cyan3 bold]Tempering Rune[/cyan3 bold]'
    description = "Converts a random 'added flat' or 'percentage increased' affix to the other version."
    minItemLevel = 15
    successEntropy = 0.12

    def apply(self, item, player=None) -> CraftResult:
        if not item.craftable:
            return CraftResult(outcome=CraftOutcome.NO_EFFECT, message='Item cannot be modified')
        if item.level < self.minItemLevel:
            return CraftResult(outcome=CraftOutcome.NO_EFFECT, message='Item level is too low')

        equipType = resolveAffixPoolKey(item)
        candidates = []
        for s in item.prefixSlots + item.suffixSlots:
            if s.isEmpty or s.locked:
                continue
            baseId = s.affix.id.rsplit('_t', 1)[0]
            root, direction = _statRootAndDirection(baseId)
            if root is None:
                continue
            targetBaseId = (PERCENT_PREFIX if direction == 'flat_to_percent' else 'added_') + root
            candidates.append((s, targetBaseId))

        if not candidates:
            return CraftResult(outcome=CraftOutcome.NO_EFFECT, message='No affix on this item has a flat/% Increased counterpart')

        slot, targetBaseId = random.choice(candidates)
        kind = 'prefixes' if slot.kind == 'prefix' else 'suffixes'
        template = _pickReplacementTier(AFFIX_POOL, equipType, kind, targetBaseId, slot.affix.tier, item.level)

        if template is None:
            return CraftResult(outcome=CraftOutcome.NO_EFFECT, message=f"This item cannot roll {targetBaseId.replace('_', ' ').title()}")

        oldAffix = slot.affix
        slot.affix = _cloneAffixAtTier(template, slot.kind)
        item.update()
        item._generateName()
        item.addEntropy(self.successEntropy)

        return CraftResult(
            outcome=CraftOutcome.SUCCESS,
            message=f'Tempered {oldAffix.stat.replace("_", " ").title()} into:\n[dim green1]- {slot.affix}[/dim green1]',
            entropyAdded=self.successEntropy
        )


SIPHON_STAT_MAP = {
    'health': 'siphon_health_on_kill',
    'damage': 'siphon_damage_on_kill',
    'crit_chance': 'siphon_crit_chance_on_kill',
    'crit_multi': 'siphon_crit_damage_on_kill',
    'speed': 'siphon_speed_on_kill',
}

class SiphonRune(CraftingItem):
    name = '[dark_red bold]Siphon Rune[/dark_red bold]'
    description = "Converts an existing Health, Damage, Crit Chance, Crit Multi or Speed suffix into it's siphon-on-kill variant."
    minItemLevel = 30
    successEntropy = 0.15

    def apply(self, item, player=None) -> CraftResult:
        if not item.craftable:
            return CraftResult(outcome=CraftOutcome.NO_EFFECT, message='Item cannot be modified')
        if item.level < self.minItemLevel:
            return CraftResult(outcome=CraftOutcome.NO_EFFECT, message='Item level is too low')

        equipType = resolveAffixPoolKey(item)
        marketSuffixPool = MARKET_AFFIX_POOL.get(equipType, {}).get('suffixes', {})

        candidates = []
        for s in item.suffixSlots:
            if s.isEmpty or s.locked:
                continue
            baseId = s.affix.id.rsplit('_t', 1)[0]
            for prefix in ('added_', 'increased_'):
                if not baseId.startswith(prefix):
                    continue
                root = baseId[len(prefix):]
                siphonBaseId = SIPHON_STAT_MAP.get(root)
                if siphonBaseId and any(affixId.rsplit('_t', 1)[0] == siphonBaseId for affixId in marketSuffixPool):
                    candidates.append((s, siphonBaseId))
                break

        if not candidates:
            return CraftResult(
                outcome=CraftOutcome.NO_EFFECT,
                message='This item has no Health, Damage, Crit Chance, Crit Multiplier or Speed suffix that can be siphoned'
            )

        slot, siphonBaseId = random.choice(candidates)
        template = _pickReplacementTier(MARKET_AFFIX_POOL, equipType, 'suffixes', siphonBaseId, slot.affix.tier, item.level)

        if template is None:
            return CraftResult(outcome=CraftOutcome.NO_EFFECT, message='This item cannot roll that siphon effect')

        slot.affix = _cloneAffixAtTier(template, 'suffix')
        item.update()
        item._generateName()
        item.addEntropy(self.successEntropy)

        return CraftResult(
            outcome=CraftOutcome.SUCCESS,
            message=f'Siphoned into:\n[dim green1]- {slot.affix}[/dim green1]',
            entropyAdded=self.successEntropy
        )


QUEST_RUNES: Dict[str, CraftingItem] = {
    'passive': PassiveErasingRune(),
    'reckless': RecklessErasingRune(),
    'shallow': ShallowErasingRune(),
    'wasting': WastingErasingRune(),
    'brittle': BrittleErasingRune(),
    'unlucky': UnluckyErasingRune(),

    'duplicating': DuplicatingGrowthRune(),
    'imitating': ImitatingGrowthRune(),
    'protective': ProtectiveGrowthRune(),
    "peddler's": PeddlersGrowthRune(),

    'upgrading': UpgradingRarityRune(),

    'tempering': TemperingRune(),
    'siphon': SiphonRune(),
}