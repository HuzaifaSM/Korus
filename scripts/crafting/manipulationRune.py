from .base import CraftingItem, CraftOutcome, CraftResult
from scripts.items.affixes import MAX_TIERS, Affix, AFFIX_POOL, getTierVariants, getTieredAffix, resolveAffixPoolKey
import random
from typing import Dict, List

def tierPower(tier: int) -> int:
    return int((tier ** 2) * 0.9)

def powerToTier(power: int, availableTiers: List[int]) -> int:
    best = min(availableTiers)
    for t in sorted(availableTiers):
        if tierPower(t) <= power:
            best = t
        else:
            break
    return best

def applyEfficiency(power: int, efficiency: float) -> int:
    softened = power ** 0.92
    return int(softened * efficiency)

class FusionRune(CraftingItem):
    name = '[orange3]Fusion Rune[/orange3]'
    description='Removes 2 random affixes ands adds 1 random affix. The added affix is more likely to be similar to the removed affixes. The added affix will combine the tiers of the removed affixes.'
    affixesToRemove: int = 2
    minItemLevel: int = 10
    minAffixLevel: int = 10
    successEntropy = 0.15
    tierEfficiency = 0.8
    dropWeight = 90

    def _serialise(self):
        temp = super()._serialise()
        temp['affixesToRemove'] = self.affixesToRemove
        temp['tierEfficiency'] = self.tierEfficiency
        return temp
    
    @classmethod
    def deserialise(cls, data):
        rune = super().deserialise(data)
        rune.affixesToRemove = data.get('affixesToRemove', 2)
        rune.tierEfficiency = data.get('tierEfficiency', 1.0)
        return rune

    def getRandomEmptySlot(self, item):
        emptyPrefixes = [s for s in item.prefixSlots if s.isEmpty]
        emptySuffixes = [s for s in item.suffixSlots if s.isEmpty]
        allEmpty = emptyPrefixes + emptySuffixes
        if not allEmpty:
            return None
        return random.choice(allEmpty)
    
    def getFilledSlots(self, item, amount: int = 1):
        prefixes = [s for s in item.prefixSlots if not s.isEmpty and not s.locked]
        suffixes = [s for s in item.suffixSlots if not s.isEmpty and not s.locked]
        allFilled = prefixes + suffixes
        if not allFilled:
            return None
        amount = min(len(allFilled), amount)
        return random.sample(allFilled, k=amount)

    def apply(self, item, player=None) -> CraftResult:
        if not item.craftable:
            return CraftResult(
                outcome=CraftOutcome.NO_EFFECT,
                message='Item is unmodifiable'
            )
        if item.level < self.minItemLevel:
            return CraftResult(
                outcome=CraftOutcome.NO_EFFECT,
                message='Item level too low'
            )
        
        removeSlots = self.getFilledSlots(item, amount=self.affixesToRemove)
        if removeSlots is None:
            return CraftResult(
                outcome=CraftOutcome.NO_EFFECT,
                message='No affixes to remove'
            )
        
        removedAffixes = []
        categoryWeights = {}
        removedTiers = []
        totalPower = 0
        for s in removeSlots:
            affix = s.affix
            removedAffixes.append(affix)
            removedTiers.append(affix.tier)
            totalPower += tierPower(affix.tier)

            for cat in affix.categories:
                categoryWeights[cat] = categoryWeights.get(cat, 0) + 1

            s.affix = None
        
        totalPower = applyEfficiency(totalPower, self.tierEfficiency)
        maxRemovedTier = max(removedTiers)
        avgRemovedTier = sum(removedTiers) / len(removedTiers)
        tierFloor = max(
            int(avgRemovedTier * 0.9),
            maxRemovedTier - 2
        )

        addSlot = self.getRandomEmptySlot(item)
        if addSlot is None:
            return CraftResult(
                outcome=CraftOutcome.NO_EFFECT,
                message='No empty slots'
            )

        slotType = resolveAffixPoolKey(item)
        affixType = 'prefixes' if addSlot.kind == 'prefix' else 'suffixes'
        availableAffixes = AFFIX_POOL[slotType][affixType]

        prefixExcluded, suffixExcluded = item.getExcludedIds()
        excludedIds = prefixExcluded if addSlot.kind == 'prefix' else suffixExcluded

        baseAffixes = {}
        baseWeights = {}

        for _, affix in availableAffixes.items():
            baseId = affix.id.rsplit('_t', 1)[0]
            if affix.levelReq > item.level:
                continue
            if baseId in excludedIds:
                continue
            if affix.levelReq < self.minAffixLevel:
                continue

            weight = 1
            for cat in affix.categories:
                if cat in categoryWeights:
                    weight += categoryWeights.get(cat, 0) * 20

            baseWeights[baseId] = baseWeights.get(baseId, 0) + weight
            baseAffixes.setdefault(baseId, []).append(affix)

        chosenBaseId = random.choices(
            list(baseWeights.keys()),
            weights=list(baseWeights.values()),
            k=1
        )[0]
        
        variants = [
            a for a in baseAffixes[chosenBaseId]
            if a.levelReq <= item.level
        ]

        availableTiers = sorted({a.tier for a in variants})
        rawTier = powerToTier(totalPower, availableTiers)

        finalTier = max(
            rawTier,
            min(
                tierFloor,
                max(availableTiers)
            )
        )
        if maxRemovedTier >= 8:
            finalTier = min(finalTier + 1, max(availableTiers))

        chosenAffix = max(
            (a for a in variants if a.tier == finalTier),
            key=lambda a: a.weight
        )

        newAffix = Affix(
            id=chosenAffix.id,
            name=chosenAffix.name,
            levelReq=chosenAffix.levelReq,
            tier=chosenAffix.tier,
            stat=chosenAffix.stat,
            slot=chosenAffix.slot,
            minVal=chosenAffix.minVal,
            maxVal=chosenAffix.maxVal,
            isPercent=chosenAffix.isPercent,
            kind=chosenAffix.kind,
            weight=chosenAffix.weight,
            categories=list(chosenAffix.categories)
        )
        newAffix.rollValue()
        addSlot.affix = newAffix
        if newAffix.stat == 'durability':
            if newAffix.isFlat:
                item.durability += newAffix.value
            else:
                item.durability = int(item.durability * (1 + (newAffix.value / 100)))

        item.update()
        item._generateName()
        item.addEntropy(self.successEntropy)

        removedStr = ""
        for a in removedAffixes:
            removedStr += f"\n- {a}"

        return CraftResult(
            outcome=CraftOutcome.SUCCESS,
            message=f'[green bold]Successfully applied {self.name}[/green bold]\nRemoved:{removedStr}.\nAdded:\n{newAffix}.',
            entropyAdded=self.successEntropy
        )

class GreaterFusionRune(FusionRune):
    name = '[dark_orange bold]Greater Fusion Rune[/dark_orange bold]'
    description = 'Removes 2 random affix and adds 1 random affix. The added affix is more likely to be similar to the removed affixes. The added affix will combine the tiers of the removed affixes more efficiently.'
    affixesToRemove = 2
    minItemLevel = 25
    successEntropy = 0.2
    tierEfficiency = 0.95
    dropWeight = 65

class PerfectFusionRune(FusionRune):
    name = '[gold1 bold underline]Perfect Fusion Rune[/gold1 bold underline]'
    description = 'Removes 2 random affixes and adds 1 random affix. The added affix is more likely to be similar to the removed affixes. The added affix will very efficiently combine the tiers of the removed affixes.'
    affixesToRemove = 2
    minAffixLevel = 30
    minItemLevel = 50
    successEntropy = 0.3
    tierEfficiency = 1.2
    dropWeight = 35

class HeavyFusionRune(FusionRune):
    name = '[dark_orange3 bold]Heavy Fusion Rune[/dark_orange3 bold]'
    description = 'Removes 3 random affixes and adds 1 random affix. The added affix is more likely to be similar to the removed affixes. The added affix will combine the tiers of the removed affixes.'
    affixesToRemove = 3
    minItemLevel = 20
    successEntropy = 0.2
    tierEfficiency = 0.85
    dropWeight = 80

class SolarFusionRune(FusionRune):
    name = '[bright_yellow bold underline]Solar Fusion Rune[/bright_yellow bold underline]'
    description = 'Removes 4 random affixes and adds 1 random affix. The added affix is more likely to be similar to the removed affixes. The added affix will combine the tiers of the removed affixes with extreme efficiency.'
    affixesToRemove = 4
    minItemLevel = 75
    minAffixLevel = 60
    successEntropy = 0.5
    tierEfficiency = 1.6
    dropWeight = 6

class BaseConversionRune(CraftingItem):
    toConvert: str | None = None
    successEntropy: float = 0.04

    def _serialise(self):
        temp = super()._serialise()
        temp['toConvert'] = self.toConvert
        return temp
    
    @classmethod
    def deserialise(cls, data):
        rune = super().deserialise(data)
        rune.toConvert = data.get('toConvert', None)
        return rune

    def findEmptySlot(self, item):
        if self.toConvert is None:
            return None, None
        elif self.toConvert == 'prefix':
            for slot in item.prefixSlots:
                if slot.isEmpty:
                    index = item.prefixSlots.index(slot)
                    return slot, index
        else:
            for slot in item.suffixSlots:
                if slot.isEmpty:
                    index = item.suffixSlots.index(slot)
                    return slot, index
        return None, None

    def apply(self, item, player=None):
        if not item.craftable:
            return CraftResult(
                outcome=CraftOutcome.NO_EFFECT,
                message='Item is unmodifiable'
            )
        
        slot, index = self.findEmptySlot(item)
        if slot is None:
            return CraftResult(
                outcome=CraftOutcome.NO_EFFECT,
                message=f'Item has no empty {self.toConvert} slots.'
            )
        
        from scripts.items.equipment import AffixSlot
        if self.toConvert == 'prefix':
            item.prefixSlots.pop(index)
            item.suffixSlots.append(AffixSlot('suffix'))
        else:
            item.suffixSlots.pop(index)
            item.prefixSlots.append(AffixSlot('prefix'))

        item.update()
        item.addEntropy(self.successEntropy)

        return CraftResult(
            outcome=CraftOutcome.SUCCESS,
            message=f'{self.toConvert.title()} slot successfully converted.',
            entropyAdded=self.successEntropy
        )

class PrefixConversionRune(BaseConversionRune):
    name = '[deep_sky_blue3]Prefix Conversion Rune[/deep_sky_blue3]'
    description = 'Converts an empty prefix slot into an empty suffix slot'
    toConvert = 'prefix'
    dropWeight = 150

class SuffixConversionRune(BaseConversionRune):
    name = '[deep_sky_blue4]Suffix Conversion Rune[/deep_sky_blue4]'
    description = 'Converts an empty suffix slot into an empty prefix slot'
    toConvert = 'suffix'
    dropWeight = 150

class EquilibriumRune(CraftingItem):
    name = '[light_slate_blue]Equilibrium Rune[/light_slate_blue]'
    description = 'Balances the tiers of all affixes on an item, making them as equal as possible.'
    minItemLevel = 15
    successEntropy = 0.08
    tierEfficiency: float = 0.9
    dropWeight = 150

    def _serialise(self):
        temp = super()._serialise()
        temp['tierEfficiency'] = self.tierEfficiency
        return temp
    
    @classmethod
    def deserialise(cls, data):
        rune = super().deserialise(data)
        rune.tierEfficiency = data.get('tierEfficiency', 1.0)
        return rune

    def apply(self, item, player=None) -> CraftResult:
        if not item.craftable:
            return CraftResult(
                outcome=CraftOutcome.NO_EFFECT,
                message='Item is unmodifiable'
            )
        if item.level < self.minItemLevel:
            return CraftResult(
                outcome=CraftOutcome.NO_EFFECT,
                message='Item level too low'
            )
        
        slots = [
            s for s in item.prefixSlots + item.suffixSlots
            if not s.isEmpty and not s.locked and not s.soulbound
        ]

        if len(slots) < 2:
            return CraftResult(
                outcome=CraftOutcome.NO_EFFECT,
                message='Item does not have enough affixes'
            )

        affixData = []
        totalPower = 0
        
        for slot in slots:
            affix = slot.affix
            power = tierPower(affix.tier)
            totalPower += power
            affixData.append((slot, affix, power))
        totalPower = applyEfficiency(totalPower, self.tierEfficiency)
        targetPower = totalPower // len(affixData)
        
        # assign new tiers
        overflow = 0
        for slot, affix, _ in affixData:
            variants = getTierVariants(item, affix)
            variants = [a.tier for a in variants]
            availableTiers = sorted(variants)
            tier = powerToTier(targetPower, availableTiers)
            
            if tier < availableTiers[0]:
                tier = availableTiers[0]
            if tier > availableTiers[-1]:
                overflow += tierPower(tier) - tierPower(availableTiers[-1])
                tier = availableTiers[-1]

            affixId = affix.id.rsplit('_t', 1)[0]
            affixId = f"{affixId}_t{tier}"
            newAffix = getTieredAffix(affix.slot, affix.kind, affixId=affixId)
            newAffix.rollValue()
            slot.affix = newAffix

        # carry out overflow
        if overflow > 0:
            for slot, affix, _ in affixData:
                variants = getTierVariants(item, affix)
                variants = [a.tier for a in variants]
                availableTiers = sorted(variants)

                currentIndex = availableTiers.index(affix.tier)
                if currentIndex + 1 >= len(availableTiers):
                    continue

                nextTier = availableTiers[currentIndex + 1]
                cost = tierPower(nextTier) - tierPower(affix.tier)

                if overflow >= cost:
                    affixId = affix.id.rsplit('_t', 1)[0]
                    affixId = f'{affixId}_t{tier}'
                    newAffix = getTieredAffix(affix.slot, affix.kind, affixId=affixId)
                    newAffix.rollValue()
                    slot.affix = affix

                    overflow -= cost
                
                if overflow <= 0:
                    break

        item.update()
        item._generateName()
        item.addEntropy(self.successEntropy)

        return CraftResult(
            outcome=CraftOutcome.SUCCESS,
            message='Affix tiers successfully equilibrated',
            entropyAdded=self.successEntropy
        )

class GreaterEquilibriumRune(EquilibriumRune):
    name = '[cornflower_blue bold underline]Greater Equilibrium Rune[/cornflower_blue bold underline]'
    description = 'Balances the tiers of all affixes on an item efficiently, making them as equal as possible.'
    minItemLevel = 35
    successEntropy = 0.12
    tierEfficiency = 1.1
    dropWeight = 150

class PerfectEquilibriumRune(EquilibriumRune):
    name = '[cyan1 bold underline]Perfect Equilibrium Rune[/cyan1 bold underline]'
    description = 'Balances the tiers of all affixes on an item very efficiently, making them as equal as possible'
    minItemLevel = 65
    successEntropy = 0.2
    tierEfficiency = 1.3
    dropWeight = 80

class DeceivingEquilibriumRune(EquilibriumRune):
    name = '[medium_purple3 bold italic underline]Deceiving Equilibrium Rune[/medium_purple3 bold italic underline]'
    description = 'Balances all affix tiers on an item, occasionally grants additional tiers.'
    minItemLevel = 85
    successEntropy = 0.4
    tierEfficiency = 1.5
    dropWeight = 15

    def apply(self, item, player=None):
        output = super().apply(item, player=None)
        if output.outcome != CraftOutcome.SUCCESS:
            return output
        
        slots = [s for s in item.prefixSlots + item.suffixSlots
                 if not s.isEmpty and not s.locked and not s.soulbound]

        for slot in slots:
            if random.random() <= 0.2:
                affix = slot.affix
                afId = affix.id.rsplit('_t', 1)[0]
                nextTier = affix.tier + 1
                affixId = f'{afId}_t{nextTier}'
                newAffix = getTieredAffix(affix.slot, affix.kind, affixId=affixId)
                if newAffix is not None:
                    newAffix.rollValue()
                    slot.affix = newAffix

        item.update()

        return CraftResult(
            outcome=CraftOutcome.SUCCESS,
            message='Affix tiers successfully equilibrated deceitfully.',
            entropyAdded=self.successEntropy
        )

class SacrificeRune(CraftingItem):
    name = '[red1]Sacrifice Rune[/red1]'
    description = 'Removes 1 affix and adds its tiers to another random affix'
    minItemLevel = 20
    successEntropy = 0.15
    tierEfficiency: float = 1.0
    dropWeight = 90

    def _serialise(self):
        temp = super()._serialise()
        temp['tierEfficiency'] = self.tierEfficiency
        return temp

    @classmethod
    def deserialise(cls, data):
        rune = super().deserialise(data)
        rune.tierEfficiency = data.get('tierEfficiency', 1.0)
        return rune

    def getFilledSlots(self, item):
        filled = [s for s in item.prefixSlots + item.suffixSlots
                  if not s.isEmpty and not s.locked]
        return filled

    def apply(self, item, player=None):
        if not item.craftable:
            return CraftResult(
                outcome=CraftOutcome.NO_EFFECT,
                message='Item is unmodifiable'
            )
        
        if item.level < self.minItemLevel:
            return CraftResult(
                outcome=CraftOutcome.NO_EFFECT,
                message='Item level too low'
            )

        slots = self.getFilledSlots(item)
        if len(slots) < 2:
            return CraftResult(
                outcome=CraftOutcome.NO_EFFECT,
                message='Not enough slots to carry out operations'
            )

        sacrifice = random.choice(slots) # slot with affix being removed
        sacrifiedAffix = sacrifice.affix
        slots.remove(sacrifice) # removed to prevent being attempted to add onto
        sacrificeTier = sacrifice.affix.tier

        totalPower = tierPower(sacrificeTier)
        totalPower = applyEfficiency(totalPower, self.tierEfficiency)

        candidates = []
        for s in slots:
            affix = s.affix
            baseId = affix.id.rsplit('_t', 1)[0]
            maxTier = MAX_TIERS.get((affix.slot, baseId))
            if maxTier is None:
                continue
            if affix.tier < maxTier and powerToTier(totalPower, list(range(1, maxTier + 1))) > affix.tier: # if affix isn't max tier, and if the result will actually increase the affix's tier
                candidates.append(s)
        if not candidates:
            return CraftResult(
                outcome=CraftOutcome.NO_EFFECT,
                message='No valid affixes to upgrade'
            )

        targetSlot = random.choice(candidates)
        targetAffix = targetSlot.affix

        baseId = targetAffix.id.rsplit('_t', 1)[0]
        maxTier = MAX_TIERS[(targetAffix.slot, baseId)]
        availableTiers = list(range(1, maxTier + 1))

        rawTier = powerToTier(totalPower, availableTiers)

        oldTier = targetAffix.tier
        finalTier = max(rawTier, targetAffix.tier + 1)
        finalTier = min(finalTier, maxTier)

        if finalTier <= targetAffix.tier:
            return CraftResult(
                outcome=CraftOutcome.NO_EFFECT,
                message='Failed to upgrade any affixes'
            )
        
        newAffixId = f'{baseId}_t{finalTier}'
        newAffix = getTieredAffix(
            slot=targetAffix.slot, kind=targetAffix.kind, affixId=newAffixId
        )
        newAffix.rollValue()
        targetSlot.affix = newAffix
        if newAffix.stat == 'durability':
            if newAffix.isFlat:
                item.durability += newAffix.value
            else:
                item.durability = int(item.durability * (1 + (newAffix.value / 100)))
        sacrifice.affix = None # only removed on success, otherwise kept, so placing here means it won't change if rune failed

        item.update()
        item._generateName()
        item.addEntropy(self.successEntropy)

        return CraftResult(
            outcome=CraftOutcome.SUCCESS,
            message=f'Removed {sacrifiedAffix}.\nUpgraded {newAffix} from Tier {oldTier} to Tier {finalTier}',
            entropyAdded=self.successEntropy
        )

class GreaterSacrificeRune(SacrificeRune):
    name = '[red3 bold]Greater Sacrifice Rune[/red3 bold]'
    description = 'Removes 1 affix and adds its tiers efficiently to another random affix'
    minItemLevel = 40
    successEntropy = 0.2
    tierEfficiency = 1.3
    dropWeight = 65

class PerfectSacrificeRune(SacrificeRune):
    name = '[dark_red italic bold underline]Perfect Sacrifice Rune[/dark_red italic bold underline]'
    description = 'Removes 1 affix and adds its tiers very efficiently to another random affix'
    minItemLevel = 55
    successEntropy = 0.3
    tierEfficiency = 1.9
    dropWeight = 35

MANIPULATION_RUNES: Dict[str, CraftingItem] = {
    'fusion': FusionRune(),
    'greater_fusion': GreaterFusionRune(),
    'perfect_fusion': PerfectFusionRune(),
    'heavy_fusion': HeavyFusionRune(),
    'solar_fusion': SolarFusionRune(),

    'prefix': PrefixConversionRune(),
    'suffix': SuffixConversionRune(),

    'equilibrium': EquilibriumRune(),
    'greater_equilibrium': GreaterEquilibriumRune(),
    'perfect_equilibrium': PerfectEquilibriumRune(),
    'deceiving_equilibrium': DeceivingEquilibriumRune(),

    'sacrifice': SacrificeRune(),
    'greater_sacrifice': GreaterSacrificeRune(),
    'perfect_sacrifice': PerfectSacrificeRune()
}

"""
IDEAS:
"""