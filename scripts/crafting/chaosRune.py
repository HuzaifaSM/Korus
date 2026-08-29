from .base import CraftingItem, CraftOutcome, CraftResult
from scripts.affixes import rollAffix, resolveAffixPoolKey
import random
from typing import Dict

class BaseChaosRune(CraftingItem):
    affixesToRemove: int = 1
    affixesToAdd: int = 1

    successEntropy: float | None = None
    partialSuccessEntropy: float | None = None

    def _serialise(self):
        temp = super()._serialise()
        temp['affixesToRemove'] = self.affixesToRemove
        temp['affixesToAdd'] = self.affixesToAdd
        return temp

    @classmethod
    def deserialise(cls, data):
        rune = super().deserialise(data)
        rune.affixesToRemove = data.get('affixesToRemove', 1)
        rune.affixesToAdd = data.get('affixesToAdd', 1)
        return rune

    def getFilledSlots(self, item):
        slots = [s for s in item.prefixSlots + item.suffixSlots if not s.isEmpty and not s.locked]
        return slots
    
    def getEmptySlots(self, item):
        return [s for s in item.prefixSlots + item.suffixSlots if s.isEmpty]
    
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
            
        filledSlots = self.getFilledSlots(item)
        if not filledSlots:
            return CraftResult(
                outcome=CraftOutcome.NO_EFFECT,
                message='Item has no modifiers to remove'
            )
        
        # removal
        toRemove = min(self.affixesToRemove, len(filledSlots))
        removedSlots = random.sample(filledSlots, toRemove)
        removedData = {s: s.affix for s in removedSlots}

        for slot in removedSlots:
            slot.affix = None

        # addition
        added = 0
        addedData = {}
        for _ in range(self.affixesToAdd):
            emptySlots = self.getEmptySlots(item)
            if not emptySlots:
                break

            slot = random.choice(emptySlots)

            prefixExcluded, suffixExcluded = item.getExcludedIds()
            excludedIds = prefixExcluded if slot.kind == 'prefix' else suffixExcluded

            defenseType = None
            if hasattr(item, 'defenseType') and item.defenseValue > 0:
                defenseType = item.defenseType

            affix = rollAffix(
                equipType=resolveAffixPoolKey(item),
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
                continue

            slot.affix = affix
            if affix.stat == 'durability':
                if affix.isFlat:
                    item.durability += affix.value
                else:
                    item.durability = int(item.durability * (1 + (affix.value / 100)))
            added += 1
            addedData[slot] = affix

        item.update()
        item._generateName()

        # resolution
        if len(removedSlots) == self.affixesToRemove and added == self.affixesToAdd:
            item.addEntropy(self.successEntropy)
            removedStr = ""
            for a in removedData.values():
                removedStr += f"\n- {a}"
            addedStr = ""
            for a in addedData.values():
                addedStr += f"\n- {a}"
            return CraftResult(
                outcome=CraftOutcome.SUCCESS,
                message=f'[green]Successfully applied {self.name}\n[bold red]Removed:[/bold red]{removedStr}\n[bold green]Added:[/bold green]{addedStr}',
                entropyAdded=self.successEntropy
            )
        else: # unsuccessful, revert to original state, no entropy
            slot.affix = None
            for s, aff in removedData.items():
                s.affix = aff
            return CraftResult(
                outcome=CraftOutcome.FAILURE,
                message=f'Failed to remove {toRemove} Affixes and add {self.affixesToAdd} Affixes. No change was made to the item.',
            )

class ChaosRune(BaseChaosRune):
    name = '[purple4]Chaos Rune[/purple4]'
    description = 'Removes 1 random affix and adds 1 new random affix.'
    affixesToAdd = 1
    affixesToRemove = 1
    minAffixLevel = 0
    minItemLevel = 10
    successEntropy = 0.06
    dropWeight = 300

class GreaterChaosRune(BaseChaosRune):
    name = '[dark_magenta bold]Greater Chaos Rune[/dark_magenta bold]'
    description = 'Removes 1 random affix and adds 1 new random affix above level 30'
    affixesToAdd = 1
    affixesToRemove = 1
    minItemLevel = 30
    minAffixLevel = 30
    successEntropy = 0.12
    dropWeight = 150

class PerfectChaosRune(BaseChaosRune):
    name = '[magenta bold underline]Perfect Chaos Rune[/magenta bold underline]'
    description = 'Removes 1 random affix and adds 1 new random affix above level 60'
    affixesToAdd = 1
    affixesToRemove = 1
    minAffixLevel = 60
    minItemLevel = 65
    successEntropy = 0.2
    dropWeight = 80

class DevouringChaosRune(BaseChaosRune):
    name = '[dark_red on purple4 bold]Devouring Chaos Rune[/dark_red on purple4 bold]'
    description = 'Removes the lowest level affix and adds 1 random new affix above level 20'
    affixesToAdd = 1
    affixesToRemove = 1
    minAffixLevel = 20
    minItemLevel = 30
    successEntropy = 0.2
    partialSuccessEntropy = 0.05
    dropWeight = 80

    def getFilledSlots(self, item):
        slots = super().getFilledSlots(item)
        if not slots:
            return []
        weakest = min(slots, key=lambda s: s.affix.levelReq)
        return [weakest]

class SpreadingChaosRune(BaseChaosRune):
    name = '[purple3 italic]Spreading Chaos Rune[/purple3 italic]'
    description = 'Removes up to 2 random affixes and adds 1 new random affix.'
    minAffixLevel = 0
    minItemLevel = 20
    affixesToAdd = 1
    affixesToRemove = 2
    successEntropy = 0.1
    partialSuccessEntropy = 0.025
    dropWeight = 150

class SplittingChaosRune(BaseChaosRune):
    name = '[orchid bold]Splitting Chaos Rune[/orchid bold]'
    description = 'Removes 1 random affix above level 35 and adds 2 new random affixes above level 20.'
    minAffixLevel = 20
    minItemLevel = 30
    affixesToAdd = 2
    affixesToRemove = 1
    successEntropy = 0.2
    partialSuccessEntropy = 0.05
    dropWeight = 80

    def getFilledSlots(self, item):
        slots = super().getFilledSlots(item)
        if not slots:
            return []
        slots = [s for s in slots if s.affix.levelReq >= 35]
        return slots

class UnstableChaosRune(BaseChaosRune):
    name = '[bright_magenta bold]Unstable Chaos Rune[/bright_magenta bold]'
    description = 'Removes up to 2 random affixes and adds up to 2 new random affixes above level 10.'
    affixesToAdd = 2
    affixesToRemove = 2
    minAffixLevel = 10
    minItemLevel = 15
    successEntropy = 0.24
    partialSuccessEntropy = 0.06
    dropWeight = 80

class AscendantChaosRune(BaseChaosRune):
    name = '[deep_pink4 bold underline]Ascendant Chaos Rune[/deep_pink4 bold underline]'
    description = 'Removes 1 random affix and adds 1 new random affix above level 50.'
    affixesToAdd = 1
    affixesToRemove = 1
    minAffixLevel = 50
    minItemLevel = 60
    successEntropy = 0.4
    partialSuccessEntropy = 0.1
    dropWeight = 15

class SovereignChaosRune(BaseChaosRune):
    name = '[hot_pink bold underline]Sovereign Chaos Rune[/hot_pink bold underline]'
    description = 'Removes up to 2 random affixes and adds 2 new random affixes above level 60.'
    affixesToAdd = 2
    affixesToRemove = 2
    minAffixLevel = 60
    minItemLevel = 75
    successEntropy = 0.6
    partialSuccessEntropy = 0.15
    dropWeight = 6

CHAOS_RUNES: Dict[str, BaseChaosRune] = {
    'chaos': ChaosRune(),
    'greater': GreaterChaosRune(),
    'perfect': PerfectChaosRune(),
    'devouring': DevouringChaosRune(),
    'spreading': SpreadingChaosRune(),
    'splitting': SplittingChaosRune(),
    'unstable': UnstableChaosRune(),
    'ascendant': AscendantChaosRune(),
    'sovereign': SovereignChaosRune()
}

"""
IDEAS:
- hellish chaos rune:
    - remove 3 random affixes, add 1 affix of level 70+
    - dark_red bold italic underline
- only chaos prefix rune
- only chaos suffix rune
"""