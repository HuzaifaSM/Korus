from .base import CraftingItem, CraftOutcome, CraftResult
from scripts.affixes import Affix, getTierVariants
from scripts.styles import console
import json
import random
from typing import Dict

class DestabilisedAffix:
    def __init__(self, name: str, stat: str, value: float, isPercent: bool = False):
        markup = 'dark_red bold underline' if 'of' in name else 'red1 italic'
        self.name = f'[{markup}]{name}[/{markup}]'
        self.stat = stat
        self.value = value
        self.isPercent = isPercent
        self.locked = True
        self.destabilised = True

    @property
    def isFlat(self):
        return not self.isPercent
    
    @property
    def isIncreased(self):
        return self.isPercent

    def __str__(self):
        prefix = "+" if self.value > 0 else ""
        suffix = "%" if self.isPercent else ""
        statDisplay = self.stat.replace('_', ' ').title()
        return f"[dark_red bold]{prefix}{self.value}{suffix} {statDisplay}[/dark_red bold]"

    def __rich__(self):
        return self.__str__()

class BaseDestabilisationRune(CraftingItem):
    outcomeWeights: Dict[str, int] = {}

    def _serialise(self):
        temp = super()._serialise()
        temp['outcomeWeights'] = self.outcomeWeights
        return temp
    
    @classmethod
    def deserialise(cls, data):
        rune = super().deserialise(data)
        rune.outcomeWeights = data.get('outcomeWeights', {})
        return rune

    def __init__(self):
        super().__init__()
        self._loadOutcomes()

    def _loadOutcomes(self):
        with open('crafting/data/destabilisation.json', 'r') as f:
            self.data = json.load(f)

    def apply(self, item) -> CraftResult:
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
            
        item.destabilised = True

        outcome = self._rollOutcome()

        outcomeData = self.data['outcomes'][outcome]
        tier = outcomeData.get('tier', 'neutral')
        tierColours = {
            'negative': 'red3',
            'positive': 'green3',
            'godtier': 'gold1 bold'
        }
        colour = tierColours.get(tier, 'white')

        console.print(f"\n[bold dark_red]════════════ DESTABILISATION OUTCOME ════════════[/bold dark_red]")
        console.print(f"[{colour}]{outcomeData['description']}[/{colour}]")
        console.print(f"[bold dark_red]═════════════════════════════════════════════════[/bold dark_red]\n")

        result = self._applyOutcome(item, outcome)

        item.update()
        item._generateName()

        return result
    
    def _rollOutcome(self):
        outcomes = list(self.data['outcomes'].keys())
        weights = []

        for outcomeKey in outcomes:
            outcomeData = self.data['outcomes'][outcomeKey]
            baseWeight = outcomeData['weight']

            if self.outcomeWeights and outcomeKey in self.outcomeWeights:
                baseWeight = self.outcomeWeights[outcomeKey]
            weights.append(baseWeight)

        chosen = random.choices(outcomes, weights=weights, k=1)[0]
        return chosen

    def _applyOutcome(self, item, outcomeKey: str) -> CraftResult:
        outcomeData = self.data['outcomes'][outcomeKey]
        handlers = {
            'brick': self._handleBrick,
            'add_implicit': self._handleAddImplicit,
            'double_affix_value': self._handleDoubleAffix,
            'upgrade_tiers': self._handleUpgradeTiers,
            'mastery_boost': self._handleMasteryShift,
            'downgrade_tiers_minor': self._handleDowngradeTiers,
            'downgrade_tiers_major': self._handleDowngradeTiers,
            'remove_affixes_minor': self._handleRemoveAffixes,
            'remove_affixes_moderate': self._handleRemoveAffixes,
            'remove_affixes_major': self._handleRemoveAffixes,
            'invert_affix': self._handleInvertAffix,
            'add_curse': self._handleAddCurse,
            'mastery_loss': self._handleMasteryShift,
            'eternal': self._handleEternal,
            'transcendent': self._handleTranscendent
        }
        handler = handlers.get(outcomeKey)
        if handler:
            handler(item, outcomeData)
            return CraftResult(
                outcome=CraftOutcome.SUCCESS,
                message='Item was successfully destabilised'
            )
        else:
            return CraftResult(
                outcome=CraftOutcome.NO_EFFECT,
                message='Destabilisation failed'
            )
        
    def _handleBrick(self, item, data):
        pass

    def _handleAddImplicit(self, item, data):
        implicits = self.data['implicits']
        implicitKey = random.choice(list(implicits.keys()))
        implicitData = implicits[implicitKey]

        value = random.uniform(implicitData['min'], implicitData['max'])
        if not implicitData['isPercent']:
            value = round(value, 2) if isinstance(implicitData['min'], float) else int(value)
        else:
            value = int(value)

        destabilised = DestabilisedAffix(
            name=implicitData['name'],
            stat=implicitData['stat'],
            value=value,
            isPercent=implicitData['isPercent']
        )

        if not hasattr(item, 'DestabilisedAffixes'):
            item.destabilisedAffixes = []
        item.destabilisedAffixes.append(destabilised)

    def _handleDoubleAffix(self, item, data):
        """Double one random affix value"""
        allAffixes = [s.affix for s in item.prefixSlots + item.suffixSlots if s.affix]
        if not allAffixes:
            return
        
        chosen = random.choice(allAffixes)
        chosen.baseValue = chosen.baseValue * 2

    def _handleUpgradeTiers(self, item, data):
        """Upgrade all affixes by X tiers"""
        amount = data.get('amount', 1)
        
        for slot in item.prefixSlots + item.suffixSlots:
            if not slot.affix:
                continue
            
            affix = slot.affix
            variants = getTierVariants(item, affix)
            
            # find variants that are exactly 'amount' tiers higher
            targetTier = affix.tier + amount
            upgraded = [v for v in variants if v.tier == targetTier]
            
            if not upgraded:
                # try to get highest available if exact tier doesn't exist
                upgraded = [v for v in variants if v.tier > affix.tier]
                if upgraded:
                    upgraded = [max(upgraded, key=lambda v: v.tier)]
            
            if upgraded:
                newAffix = random.choice(upgraded)
                slot.affix = Affix(
                    id=newAffix.id,
                    name=newAffix.name,
                    levelReq=newAffix.levelReq,
                    tier=newAffix.tier,
                    stat=newAffix.stat,
                    slot=item.slot,
                    minVal=newAffix.minVal,
                    maxVal=newAffix.maxVal,
                    isPercent=newAffix.isPercent,
                    kind=newAffix.kind,
                    weight=newAffix.weight,
                    categories=newAffix.categories
                )
                slot.affix.rollValue()

    def _handleDowngradeTiers(self, item, data):
        """Downgrade all affixes by X tiers"""
        amount = data.get('amount', 1)
        
        for slot in item.prefixSlots + item.suffixSlots:
            if not slot.affix:
                continue
            
            affix = slot.affix
            variants = getTierVariants(item, affix)
            
            # find variants that are exactly 'amount' tiers lower
            targetTier = max(1, affix.tier - amount)
            downgraded = [v for v in variants if v.tier == targetTier]
            
            if not downgraded:
                # get lowest available if exact tier doesn't exist
                downgraded = [v for v in variants if v.tier < affix.tier]
                if downgraded:
                    downgraded = [min(downgraded, key=lambda v: v.tier)]
            
            if downgraded:
                newAffix = random.choice(downgraded)
                slot.affix = Affix(
                    id=newAffix.id,
                    name=newAffix.name,
                    levelReq=newAffix.levelReq,
                    tier=newAffix.tier,
                    stat=newAffix.stat,
                    slot=item.slot,
                    minVal=newAffix.minVal,
                    maxVal=newAffix.maxVal,
                    isPercent=newAffix.isPercent,
                    kind=newAffix.kind,
                    weight=newAffix.weight,
                    categories=newAffix.categories
                )
                slot.affix.rollValue()

    def _handleRemoveAffixes(self, item, data):
        """Remove random affixes"""
        minRemove = data.get('minRemove', 1)
        maxRemove = data.get('maxRemove', 1)
        
        removeCount = random.randint(minRemove, maxRemove)
        
        filledSlots = [s for s in item.prefixSlots + item.suffixSlots if s.affix]
        if not filledSlots:
            return
        
        toRemove = min(removeCount, len(filledSlots))
        removed = random.sample(filledSlots, toRemove)
        
        for slot in removed:
            slot.affix = None

    def _handleInvertAffix(self, item, data):
        """Make one affix negative"""
        allAffixes = [s.affix for s in item.prefixSlots + item.suffixSlots if s.affix]
        if not allAffixes:
            return
        
        chosen = random.choice(allAffixes)
        chosen.baseValue = -abs(chosen.baseValue)

    def _handleAddCurse(self, item, data):
        """Add a negative destabilised modifier"""
        curses = self.data['curses']
        curseKey = random.choice(list(curses.keys()))
        curseData = curses[curseKey]
        
        value = random.uniform(curseData['min'], curseData['max'])
        if not curseData['isPercent']:
            value = round(value, 2) if isinstance(curseData['min'], float) else int(value)
        else:
            value = int(value)
        
        destabilised = DestabilisedAffix(
            name=curseData['name'],
            stat=curseData['stat'],
            value=value,
            isPercent=curseData['isPercent']
        )
        
        if not hasattr(item, 'DestabilisedAffixes'):
            item.destabilisedAffixes = []
        item.destabilisedAffixes.append(destabilised)

    def _handleMasteryShift(self, item, data):
        """Shift mastery up or down"""
        minShift = data.get('minShift', 0)
        maxShift = data.get('maxShift', 0)
        
        shift = random.randint(minShift, maxShift)
        
        item.mastery += shift
    
    def _handleEternal(self, item, data):
        """Make item indestructible"""
        item.maxDurability = float('inf')
        item.durability = float('inf')

    def _handleTranscendent(self, item, data):
        """Upgrade all affixes to max tier with great value rolls"""
        for slot in item.prefixSlots + item.suffixSlots:
            if not slot.affix:
                continue
            
            affix = slot.affix
            variants = getTierVariants(item, affix)
            
            if not variants:
                continue
            
            # get highest tier available
            maxTierAffix = max(variants, key=lambda v: v.tier)
            
            slot.affix = Affix(
                id=maxTierAffix.id,
                name=maxTierAffix.name,
                levelReq=maxTierAffix.levelReq,
                tier=maxTierAffix.tier,
                stat=maxTierAffix.stat,
                slot=item.slot,
                minVal=maxTierAffix.minVal,
                maxVal=maxTierAffix.maxVal,
                isPercent=maxTierAffix.isPercent,
                kind=maxTierAffix.kind,
                weight=maxTierAffix.weight,
                categories=maxTierAffix.categories
            )
            
            # roll twice and take higher value (like greater value randomiser)
            v1 = slot.affix.rollValue()
            v2 = slot.affix.rollValue()
            slot.affix.baseValue = max(v1, v2)

class DestabilisationRune(BaseDestabilisationRune):
    name = '[dark_red bold]Destabilisation Rune[/dark_red bold]'
    description = 'Destabilises an item, making it unmodifiable.'
    minItemLevel = 20
    dropWeight = 100

class GreaterDestabilisationRune(BaseDestabilisationRune):
    name = '[red3 bold underline]Greater Destabilisation Rune[/red3 bold underline]'
    description = 'Destabilises an item with improved positive outcome weights.'
    minItemLevel = 65
    dropWeight = 8


    def __init__(self):
        super().__init__()
        # adjust weights to be slightly more favourable
        self.outcomeWeights = {
            'brick': 200,  # reduced from 250
            'add_implicit': 120,  # increased from 100
            'double_affix_value': 80,  # increased from 60
            'upgrade_tiers': 90,  # increased from 70
            'mastery_boost': 100,  # increased from 85
            'downgrade_tiers_minor': 100,  # reduced from 120
            'downgrade_tiers_major': 50,  # reduced from 60
            'eternal': 20,  # increased from 15
            'transcendent': 10  # increased from 5
        }

class PerfectDestabilisationRune(BaseDestabilisationRune):
    name = '[orange_red1 bold underline]Perfect Destabilisation Rune[/orange_red1 bold underline]'
    description = 'Destabilises an item with heavily weighted positive outcomes.'
    minItemLevel = 80
    dropWeight = 4


    def __init__(self):
        super().__init__()
        # heavily favour positive outcomes
        self.outcomeWeights = {
            'brick': 150,  # reduced from 250
            'add_implicit': 150,  # increased from 100
            'double_affix_value': 120,  # increased from 60
            'upgrade_tiers': 130,  # increased from 70
            'mastery_boost': 140,  # increased from 85
            'downgrade_tiers_minor': 80,  # reduced from 120
            'downgrade_tiers_major': 30,  # reduced from 60
            'remove_affixes_minor': 70,  # reduced from 100
            'remove_affixes_moderate': 50,  # reduced from 70
            'remove_affixes_major': 20,  # reduced from 40
            'invert_affix': 60,  # reduced from 90
            'add_curse': 70,  # reduced from 110
            'mastery_loss': 60,  # reduced from 95
            'eternal': 30,  # increased from 15
            'transcendent': 15  # increased from 5
        }

DESTABILISATION_RUNES: Dict[str, BaseDestabilisationRune] = {
    'destabilisation': DestabilisationRune(),
    'greater': GreaterDestabilisationRune(),
    'perfect': PerfectDestabilisationRune()
}
