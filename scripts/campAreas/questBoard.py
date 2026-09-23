from typing import Dict, List, Optional, Any
from json import load
import random
from .station import Station
from scripts.styles import (
    console, clearScreen, printHeader, printSeparator,
    pause, printWarning, printError, printSuccess, checkGlobalCommand, selectFromNumberedList
)
from scripts.crafting.questRune import QUEST_RUNES
from scripts.items.items import ItemRarity
from scripts.items.equipment import Equipment

RECOMBINATION_LEVEL = 4
RECOMBINATION_CREDITS_COST = 10
RECOMBINATION_GOLD_COST = 5000

QUEST_SHOP_CATALOG: dict[str, tuple[int, int]] = {
    'passive':     (3, 1),
    'reckless':    (3, 1),
    'shallow':     (3, 1),
    'wasting':     (3, 1),
    'brittle':     (3, 1),
    'unlucky':     (3, 1),

    'duplicating': (5, 2),
    'imitating':   (5, 2),
    'tempering':   (5, 2),

    'protective':  (6, 3),
    'siphon':      (4, 3),

    "peddler's":   (8, 4),

    'upgrading':      (10, 5),
}
"""rune type: (credits required, quest board level required)"""

ACT_NAMES = {
    1: "Act 1 - The Basics",
    2: "Act 2 - Building Your Camp",
    3: "Act 3 - Gearing Up",
    4: "Act 4 - The Crafter's Path",
    5: "Act 5 - The Long Road",
    "endgame": "Endgame",
}

def _actSortKey(act):
    return (1, 0) if act == "endgame" else (0, act)

def _milestoneCredits(act) -> int:
    """Credits reward for completing a milestone: equal to its act number, or 25 for endgame milestones."""
    if act == "endgame":
        return 25
    return int(act)

LEGENDARY_PLUS_RARITIES = frozenset({'legendary', 'mythic', 'blank'})

def _maxItemMastery(player) -> int:
    allItems = [e for e in player._equipment.values() if e] + list(player._equipmentStorage)
    return max((e.mastery for e in allItems), default=0)

def _legendaryInEverySlot(player) -> int:
    eq = player._equipment
    weapon = eq.get('weapon')
    if not weapon or weapon.rarity.value not in LEGENDARY_PLUS_RARITIES:
        return 0

    offhand = eq.get('offhand')
    offhandOk = weapon.twoHanded or (offhand is not None and offhand.rarity.value in LEGENDARY_PLUS_RARITIES)
    if not offhandOk:
        return 0

    otherSlots = ('head', 'chest', 'legs', 'feet', 'ring', 'amulet', 'sigil_1', 'sigil_2', 'sigil_3', 'sigil_4', 'sigil_5')
    for slot in otherSlots:
        item = eq.get(slot)
        if not item or item.rarity.value not in LEGENDARY_PLUS_RARITIES:
            return 0

    return 1

STATE_CHECKS = {
    'max_resistance': lambda player: max(player._stats['Resistances'].values(), default=0),
    'max_item_mastery': _maxItemMastery,
    'legendary_in_every_slot': _legendaryInEverySlot,
}

class Milestone:
    def __init__(self, id: str, data: dict):
        self.id = id
        self.name = data['name']
        self.description = data['description']
        self.act = data['act']
        self.trigger = data['trigger']
        self.rewards = data.get('rewards', {})

    @property
    def target(self) -> int:
        return self.trigger['target']

def _loadMilestones() -> Dict[str, Milestone]:
    with open("scripts/campAreas/data/milestones.json", 'r') as file:
        data = load(file)
    return {milestoneId: Milestone(milestoneId, milestoneData) for milestoneId, milestoneData in data.items()}

MILESTONES = _loadMilestones()

class BountyTemplate:
    def __init__(self, id: str, data: dict):
        self.id = id
        self.name = data['name']
        self.tier = data['tier']  # 0 (QB level 0+), 1 (QB level 2+), 2 (QB level 4+)
        self.descriptionTemplate = data['descriptionTemplate']
        self.trigger = data['trigger']
        self.randomFilter = data.get('randomFilter')
        self.rewards = data['rewards']

def _loadBounties() -> Dict[str, BountyTemplate]:
    with open("scripts/campAreas/data/bounties.json", 'r') as file:
        data = load(file)
    return {bountyId: BountyTemplate(bountyId, bountyData) for bountyId, bountyData in data.items()}

BOUNTIES = _loadBounties()
BOUNTY_TIER_MIN_LEVEL = {0: 0, 1: 2, 2: 4}

def _matchesFilter(filterDict: Optional[dict], data: dict) -> bool:
    if not filterDict:
        return True
    return all(data.get(k) == v for k, v in filterDict.items())

class QuestBoard(Station):
    def __init__(self, player):
        super().__init__(player, "Quest Board")
        self.milestoneProgress: Dict[str, int] = {}
        self.completedMilestones: List[str] = []
        self.credits: int = 0
        self.activeBounties: List[Dict[str, Any]] = []

    @property
    def maxBounties(self) -> int:
        return self.level // 2 + 1

    def _getUpgradeRequirements(self) -> Dict[int, Dict[str, int]]:
        return {
            1: {"paper": 20, "nail": 15,
                'description': 'Milestones are tracked automatically as you play, regardless of Quest Board level.\nUnlocks the Quest Board Shop, selling the Passive, Reckless, Shallow, Wasting, Brittle and Unlucky Erasing Runes for Credits, earned by completing Milestones.\nUnlocks selling unwanted runes (weight 15-150) for Credits.'
                },
            2: {"paper": 40, "nail": 30,
                'description': 'The Shop now also sells the Duplicating and Imitating Growth Runes, and the Tempering Rune.'
                },
            3: {"paper": 60, "nail": 45,
                'description': "The Shop now also sells the Protective Growth Rune and the Siphon Rune."
                },
            4: {"paper": 85, "nail": 60,
                'description': f"The Shop now also sells the Peddler's Growth Rune.\nUnlocks Recombining two items in storage into one, for {RECOMBINATION_CREDITS_COST} Credits and {RECOMBINATION_GOLD_COST}g."
                },
            5: {"paper": 120, "nail": 90,
                'description': 'The Shop now also sells the Ascension Rarity Rune.'
                }
        }

    def _serialise(self):
        temp = super()._serialise()
        temp['milestoneProgress'] = self.milestoneProgress
        temp['completedMilestones'] = self.completedMilestones
        temp['credits'] = self.credits
        temp['activeBounties'] = self.activeBounties
        return temp

    def notifyEvent(self, eventType: str, **data) -> bool:
        """Advances any not-yet-completed milestone AND any active bounty whose trigger matches
        this event. Returns True if at least one milestone or bounty completed as a result."""
        completedAny = False
        for milestoneId, milestone in MILESTONES.items():
            if milestoneId in self.completedMilestones:
                continue

            trigger = milestone.trigger
            if trigger['event'] != eventType:
                continue

            mode = trigger.get('mode', 'counter')

            if mode == 'multi':
                bitmask = self.milestoneProgress.get(milestoneId, 0)
                for i, subFilter in enumerate(trigger.get('filters', [])):
                    if _matchesFilter(subFilter, data):
                        bitmask |= (1 << i)
                self.milestoneProgress[milestoneId] = bitmask
            else:
                if not _matchesFilter(trigger.get('filter'), data):
                    continue

                if mode == 'gauge':
                    valueKey = trigger.get('valueKey', 'amount')
                    newValue = data.get(valueKey, 0)
                    current = self.milestoneProgress.get(milestoneId, 0)
                    if newValue > current:
                        self.milestoneProgress[milestoneId] = newValue
                else:
                    amount = data.get('amount', 1)
                    self.milestoneProgress[milestoneId] = self.milestoneProgress.get(milestoneId, 0) + amount

            if self.milestoneProgress.get(milestoneId, 0) >= trigger['target']:
                self._completeMilestone(milestoneId, milestone)
                completedAny = True

        for bounty in list(self.activeBounties):
            if bounty['event'] != eventType:
                continue
            if not _matchesFilter(bounty.get('filter'), data):
                continue

            if bounty.get('mode') == 'gauge':
                valueKey = bounty.get('valueKey', 'amount')
                newValue = data.get(valueKey, 0)
                if newValue > bounty['progress']:
                    bounty['progress'] = newValue
            else:
                bounty['progress'] += data.get('amount', 1)

            if bounty['progress'] >= bounty['target']:
                self._completeBounty(bounty)
                completedAny = True

        return completedAny

    def refreshStateChecks(self) -> bool:
        """Re-evaluates every not-yet-completed 'state_check' milestone against current player state."""
        completedAny = False
        for milestoneId, milestone in MILESTONES.items():
            if milestoneId in self.completedMilestones:
                continue

            trigger = milestone.trigger
            if trigger['event'] != 'state_check':
                continue

            checkFn = STATE_CHECKS.get(trigger.get('check'))
            if not checkFn:
                continue

            value = checkFn(self.player)
            self.milestoneProgress[milestoneId] = value

            if value >= trigger['target']:
                self._completeMilestone(milestoneId, milestone)
                completedAny = True

        return completedAny

    def _completeMilestone(self, milestoneId: str, milestone: Milestone):
        self.completedMilestones.append(milestoneId)

        console.print(f"\n[gold1 bold]{'=' * 50}[/gold1 bold]")
        console.print(f"[gold1 bold]MILESTONE COMPLETE: {milestone.name}[/gold1 bold]")
        console.print(f"[dim]{milestone.description}[/dim]")

        rewards = milestone.rewards
        if 'xp' in rewards:
            self.player.gainExperience(rewards['xp'])
        if 'gold' in rewards:
            self.player.gainGold(rewards['gold'])
        if 'items' in rewards:
            for item, qty in rewards['items'].items():
                self.player.addItem(item, qty)
        if 'runes' in rewards:
            for runeReward in rewards['runes']:
                self.player.addRune(runeReward['category'], runeReward['runeType'], runeReward.get('quantity', 1))
        if 'title' in rewards:
            title = rewards['title']
            if title not in self.player.titles:
                self.player.titles.append(title)
                displayName = f"{title['text']} {self.player._name}" if title.get('style') == 'prefix' else f"{self.player._name} {title['text']}"
                console.print(f"[cyan]  + New Title Unlocked: \"{displayName}\"[/cyan]")
                if self.player.equippedTitle is None:
                    self.player.equippedTitle = title

        creditsGained = _milestoneCredits(milestone.act)
        self.credits += creditsGained
        console.print(f"[cyan]  + {creditsGained} Credits[/cyan] [dim](Total: {self.credits})[/dim]")
        console.print(f"[gold1 bold]{'=' * 50}[/gold1 bold]\n")

    def _completeBounty(self, bounty: Dict[str, Any]):
        self.activeBounties.remove(bounty)

        console.print(f"\n[gold1]{'-' * 40}[/gold1]")
        console.print(f"[gold1]BOUNTY COMPLETE: {bounty['name']}[/gold1]")
        console.print(f"[dim]{bounty['description']}[/dim]")

        self.credits += bounty['creditsReward']
        console.print(f"[cyan]  + {bounty['creditsReward']} Credits[/cyan] [dim](Total: {self.credits})[/dim]")
        console.print(f"[gold1]{'-' * 40}[/gold1]\n")

    def _eligibleBountyTemplates(self) -> List[BountyTemplate]:
        return [t for t in BOUNTIES.values() if self.level >= BOUNTY_TIER_MIN_LEVEL[t.tier]]

    def _rollBounty(self, template: BountyTemplate) -> Dict[str, Any]:
        trigger = template.trigger
        target = random.randint(*trigger['targetRange'])
        creditsReward = random.randint(*template.rewards['creditsRange'])

        filterDict = dict(trigger.get('filter', {}))
        filterChoice = None
        if template.randomFilter:
            filterChoice = random.choice(template.randomFilter['choices'])
            filterDict[template.randomFilter['key']] = filterChoice

        description = template.descriptionTemplate.format(
            target=target,
            filterChoice=filterChoice.replace('_', ' ').title() if filterChoice else ''
        )

        return {
            'templateId': template.id,
            'name': template.name,
            'description': description,
            'event': trigger['event'],
            'filter': filterDict,
            'mode': trigger.get('mode', 'counter'),
            'valueKey': trigger.get('valueKey', 'amount'),
            'target': target,
            'progress': 0,
            'creditsReward': creditsReward,
        }

    def bountiesMenu(self):
        while True:
            clearScreen()
            printHeader("Bounties")
            console.print(f"[cyan]Credits:[/cyan] {self.credits}")
            console.print(f"[success]Active Bounties:[/success] {len(self.activeBounties)}/{self.maxBounties}")
            printSeparator()

            if self.activeBounties:
                console.print("\n[bold gold]Active:[/bold gold]")
                for i, bounty in enumerate(self.activeBounties, 1):
                    console.print(f"  [cyan]{i}.[/cyan] [bold]{bounty['name']}[/bold] [dim]({min(bounty['progress'], bounty['target'])}/{bounty['target']})[/dim]")
                    console.print(f"      [dim]{bounty['description']} - {bounty['creditsReward']} Credits[/dim]")
            else:
                console.print("\n[dim]No active bounties.[/dim]")

            console.print("\n[dim]0.[/dim] Return")
            if len(self.activeBounties) < self.maxBounties:
                console.print("[dim]1.[/dim] Accept New Bounty")
            if self.activeBounties:
                console.print("[dim]2.[/dim] Abandon a Bounty")

            choice = console.input("\n[cyan]>[/cyan] ").strip()
            checkGlobalCommand(choice)
            try:
                choice = int(choice)
                match choice:
                    case 0:
                        return
                    case 1:
                        if len(self.activeBounties) < self.maxBounties:
                            self._acceptBountyMenu()
                    case 2:
                        if self.activeBounties:
                            self._abandonBountyMenu()
                    case _:
                        printWarning("Invalid choice!")
                        pause()
            except ValueError:
                printWarning("Invalid input!")
                pause()

    def _acceptBountyMenu(self):
        clearScreen()
        printHeader("Accept a Bounty")

        templates = self._eligibleBountyTemplates()
        for i, t in enumerate(templates, 1):
            targetLo, targetHi = t.trigger['targetRange']
            creditsLo, creditsHi = t.rewards['creditsRange']
            console.print(f"  [cyan]{i}.[/cyan] [bold]{t.name}[/bold]")
            console.print(f"      [dim]{t.descriptionTemplate.format(target=f'{targetLo}-{targetHi}', filterChoice='?')} - {creditsLo}-{creditsHi} Credits[/dim]")

        choice = console.input("\n[cyan]Accept which bounty? (0 to cancel):\n> [/cyan]").strip()
        try:
            index = int(choice) - 1
        except ValueError:
            printError("Invalid input!")
            pause()
            return
        if index == -1:
            return
        if not (0 <= index < len(templates)):
            printWarning("Invalid choice")
            pause()
            return

        bounty = self._rollBounty(templates[index])
        self.activeBounties.append(bounty)
        printSuccess(f"\nAccepted: {bounty['name']} - {bounty['description']} ({bounty['creditsReward']} Credits)")
        pause()

    def _abandonBountyMenu(self):
        clearScreen()
        printHeader("Abandon a Bounty")
        for i, bounty in enumerate(self.activeBounties, 1):
            console.print(f"  [cyan]{i}.[/cyan] {bounty['name']} [dim]({min(bounty['progress'], bounty['target'])}/{bounty['target']})[/dim]")

        choice = console.input("\n[cyan]Abandon which bounty? (0 to cancel):\n> [/cyan]").strip()
        try:
            index = int(choice) - 1
        except ValueError:
            printError("Invalid input!")
            pause()
            return
        if index == -1:
            return
        if not (0 <= index < len(self.activeBounties)):
            printWarning("Invalid choice")
            pause()
            return

        confirm = console.input(f"\n[bold]Abandon {self.activeBounties[index]['name']}? (y/n):\n> [/bold]").strip().lower()
        if confirm == 'y':
            self.activeBounties.pop(index)
            printSuccess("Bounty abandoned.")
        pause()

    def mainMenu(self):
        while True:
            clearScreen()
            printHeader(f"Quest Board - Level {self.level}")
            console.print(f"[cyan]Credits:[/cyan] {self.credits}")
            console.print(f"[success]Milestones Completed:[/success] {len(self.completedMilestones)}/{len(MILESTONES)}")
            printSeparator()
            console.print("[dim]0.[/dim] Return")
            console.print("[dim]1.[/dim] View Milestones")
            console.print("[dim]2.[/dim] Titles")
            console.print("[dim]5.[/dim] Bounties")
            if self.level >= 1:
                console.print("[dim]3.[/dim] Shop")
                console.print("[dim]4.[/dim] Sell Runes for Credits")
            if self.level >= RECOMBINATION_LEVEL:
                console.print("[dim]6.[/dim] Recombine Items")
            console.print("[dim]9.[/dim] Upgrade Quest Board")

            choice = console.input("\n[cyan]>[/cyan] ").strip()
            checkGlobalCommand(choice)
            try:
                choice = int(choice)
                match choice:
                    case 0:
                        return
                    case 1:
                        self.displayMilestones()
                        pause()
                    case 2:
                        self.titlesMenu()
                    case 3:
                        if self.level >= 1:
                            self.shopMenu()
                    case 4:
                        if self.level >= 1:
                            self.sellRunesMenu()
                    case 5:
                        self.bountiesMenu()
                    case 6:
                        if self.level >= RECOMBINATION_LEVEL:
                            self.recombineMenu()
                    case 9:
                        self.upgrade()
                    case _:
                        printWarning("Invalid choice!")
                        pause()
            except ValueError:
                printWarning("Invalid input!")
                pause()

    def recombineMenu(self):
        if self.level < RECOMBINATION_LEVEL:
            printWarning(f"Quest Board Level {RECOMBINATION_LEVEL} required to Recombine. Current Level: {self.level}")
            pause()
            return

        clearScreen()
        printHeader("Recombine Items")
        console.print(f"[cyan]Credits:[/cyan] {self.credits} | [gold]Gold:[/gold] {self.player._gold}")
        console.print(f"[dim]Select two items of the same slot from storage. The result takes the first item's "
                       f"prefixes and the second item's suffixes (blank slots dropped), a base randomly chosen "
                       f"from one of the two if they differ, entropy equal to 80% of both combined, and a rarity "
                       f"equal to the median of the two. Both source items are consumed.[/dim]\n")

        if self.credits < RECOMBINATION_CREDITS_COST or self.player._gold < RECOMBINATION_GOLD_COST:
            printWarning(f"Requires {RECOMBINATION_CREDITS_COST} Credits and {RECOMBINATION_GOLD_COST}g. "
                         f"(Current: {self.credits} Credits, {self.player._gold}g)")
            pause()
            return

        storage = self.player._equipmentStorage
        if len(storage) < 2:
            printWarning("Need at least 2 items in storage to combine.")
            pause()
            return

        console.print("[bold]Choose the first item (its prefixes will be kept):[/bold]")
        index1 = selectFromNumberedList(storage, "Choose item (0 to cancel)")
        if index1 is None:
            return
        item1 = storage[index1]

        candidates = [e for e in storage if e is not item1 and e.slot == item1.slot]
        if not candidates:
            printWarning(f"No other {item1.slot} in storage to combine with.")
            pause()
            return

        console.print(f"\n[bold]Choose a second {item1.slot} (its suffixes will be kept):[/bold]")
        index2 = selectFromNumberedList(candidates, "Choose item (0 to cancel)")
        if index2 is None:
            return
        item2 = candidates[index2]

        console.print(f"\n[bold]Combine {item1.name} and {item2.name} for {RECOMBINATION_CREDITS_COST} Credits and {RECOMBINATION_GOLD_COST}g? (y/n)[/bold]")
        confirm = console.input("[cyan]> [/cyan]").strip().lower()
        if confirm != 'y':
            return

        newItem = self._recombine(item1, item2)

        self.credits -= RECOMBINATION_CREDITS_COST
        self.player._gold -= RECOMBINATION_GOLD_COST
        self.player._equipmentStorage.remove(item1)
        self.player._equipmentStorage.remove(item2)
        self.player.addEquipmentToStorage(newItem)

        clearScreen()
        printSuccess("Combined into a new item:")
        console.print(newItem)
        pause()

    def _recombine(self, item1: Equipment, item2: Equipment) -> Equipment:
        templateParent = item1 if item1.baseTypeName == item2.baseTypeName else random.choice([item1, item2])
        resultRarity = ItemRarity.numToRarity((item1.rarity.num + item2.rarity.num) / 2)
        resultLevel = max(1, round((item1.level + item2.level) / 2))
        prefixAffixes = [s.affix for s in item1.prefixSlots if s.affix]
        suffixAffixes = [s.affix for s in item2.suffixSlots if s.affix]
        combinedEntropyRaw = round(0.8 * (item1.entropy + item2.entropy), 4)
        m1, m2 = item1.mythicAffix, item2.mythicAffix

        newItem = Equipment(
            slot=item1.slot,
            rarity=resultRarity,
            defenses={
                'defenseType': templateParent.defenseType,
                'defenseValue': templateParent.defenseValue,
                'baseDefenseValue': templateParent.baseDefenseValue,
            },
            damages={
                'damage': templateParent.damage,
                'baseDamage': templateParent.baseDamage,
                'damageType': templateParent.damageType,
                'twoHanded': templateParent.twoHanded,
            },
            implicits=dict(templateParent.implicits),
            prefixes=prefixAffixes,
            suffixes=suffixAffixes,
            numPrefixes=len(prefixAffixes),
            numSuffixes=len(suffixAffixes),
            level=resultLevel,
            baseTypeName=templateParent.baseTypeName,
        )

        # A Mythic result is only even possible here because numToRarity truncates the median,
        # which mathematically requires both parents to already be Mythic. Transfer whichever
        # parent's mythic line matches its donor role (item1->prefix, item2->suffix); if both
        # exist and share the same kind, that shared kind is what carries over.
        if resultRarity == ItemRarity.MYTHIC:
            if m1 and m1.kind == 'prefix':
                newItem.mythicAffix = m1
            elif m2 and m2.kind == 'suffix':
                newItem.mythicAffix = m2
            elif m1 and m2 and m1.kind == m2.kind:
                newItem.mythicAffix = m1
            elif m1:
                newItem.mythicAffix = m1
            elif m2:
                newItem.mythicAffix = m2
            if newItem.mythicAffix:
                newItem.update()

        newItem.entropy = min(newItem.maxEntropy, combinedEntropyRaw)
        newItem._generateName()
        return newItem

    RUNE_SELL_WEIGHT_RANGE = (15, 150)  # same eligibility band and 100/weight value convention as the Market's Black Market

    def sellRunesMenu(self):
        if self.level < 1:
            printWarning(f"Quest Board Level 1 required to sell runes. Current Level: {self.level}")
            pause()
            return

        from scripts.runeDrops import getRuneObject

        loWeight, hiWeight = self.RUNE_SELL_WEIGHT_RANGE
        eligible = []
        for runeKey, quantity in self.player._craftingInventory.items():
            category, runeType = runeKey.split('_', 1)
            rune = getRuneObject(category, runeType)
            if rune and loWeight <= rune.dropWeight <= hiWeight:
                eligible.append((runeKey, rune, quantity))

        clearScreen()
        printHeader("Sell Runes for Credits")
        console.print(f"[cyan]Credits:[/cyan] {self.credits}")
        console.print(f"[dim]Only runes weighing {loWeight}-{hiWeight} can be sold, worth 100/weight Credits each.[/dim]\n")

        if not eligible:
            printWarning(f"You have no eligible runes (weight {loWeight}-{hiWeight}) to sell.")
            pause()
            return

        for i, (runeKey, rune, quantity) in enumerate(eligible, 1):
            perUnit = 100 / rune.dropWeight
            console.print(f"  [cyan]{i}.[/cyan] {rune.name} x{quantity} [dim](weight {rune.dropWeight}, {perUnit:.1f} Credits each)[/dim]")

        choice = console.input("\n[cyan]Sell which rune? (0 to cancel):\n> [/cyan]").strip()
        try:
            if choice == '0':
                return
            index = int(choice) - 1
        except ValueError:
            printError("Invalid input!")
            pause()
            return

        if not (0 <= index < len(eligible)):
            printWarning("Invalid choice")
            pause()
            return

        runeKey, rune, quantity = eligible[index]
        amountStr = console.input(f"[bold]Sell how many {rune.name}? (max {quantity}):[/bold]\n[cyan]> [/cyan]").strip()
        try:
            amount = int(amountStr)
        except ValueError:
            printError("Invalid input!")
            pause()
            return

        if amount <= 0 or amount > quantity:
            printWarning("Invalid amount!")
            pause()
            return

        creditsGained = round(amount * 100 / rune.dropWeight)
        category, runeType = runeKey.split('_', 1)

        console.print(f"\n[bold]Sell {amount}x {rune.name} for {creditsGained} Credits? (y/n)[/bold]")
        confirm = console.input("[cyan]> [/cyan]").strip().lower()
        if confirm == 'y':
            self.player.removeRune(category, runeType, amount)
            self.credits += creditsGained
            printSuccess(f"\nSold {amount}x {rune.name} for {creditsGained} Credits!")
        pause()

    def shopMenu(self):
        if self.level < 1:
            printWarning(f"Quest Board Level 1 required for the Shop. Current Level: {self.level}")
            pause()
            return

        while True:
            clearScreen()
            printHeader("Quest Board Shop")
            console.print(f"[cyan]Credits:[/cyan] {self.credits}\n")

            available = [
                (runeType, price) for runeType, (price, unlockLevel) in QUEST_SHOP_CATALOG.items()
                if unlockLevel <= self.level
            ]
            for i, (runeType, price) in enumerate(available, 1):
                rune = QUEST_RUNES[runeType]
                console.print(f"  [cyan]{i}.[/cyan] {rune.name} - [cyan]{price} Credits[/cyan]")
                console.print(f"      [dim]{rune.description}[/dim]")

            if len(available) < len(QUEST_SHOP_CATALOG):
                console.print(f"\n[dim]More runes unlock as the Quest Board levels up.[/dim]")

            choice = console.input("\n[cyan]Buy which rune? (0 to cancel):\n> [/cyan]").strip()
            try:
                if choice == '0':
                    return
                index = int(choice) - 1
            except ValueError:
                printError("Invalid input!")
                pause()
                continue

            if not (0 <= index < len(available)):
                printWarning("Invalid choice")
                pause()
                continue

            runeType, price = available[index]
            rune = QUEST_RUNES[runeType]

            console.print(f"\n[bold]Buy {rune.name} for {price} Credits? (y/n)[/bold]")
            confirm = console.input("[cyan]> [/cyan]").strip().lower()
            if confirm == 'y':
                if self.credits < price:
                    printWarning(f"Need {price} Credits! (Current: {self.credits})")
                else:
                    self.credits -= price
                    self.player.addRune('quest', runeType, 1)
                    printSuccess(f"\nPurchased {rune.name}!")
            pause()

    def titlesMenu(self):
        clearScreen()
        printHeader("Titles")

        if not self.player.titles:
            printWarning("You haven't unlocked any titles yet - completing endgame Milestones grants them.")
            pause()
            return

        console.print(f"[dim]Currently displayed as:[/dim] [bold]{self.player.formatTitledName()}[/bold]\n")
        console.print("[gold]Unlocked Titles:[/gold]")
        for i, title in enumerate(self.player.titles, 1):
            preview = f"{title['text']} {self.player._name}" if title.get('style') == 'prefix' else f"{self.player._name} {title['text']}"
            equippedTag = " [success](equipped)[/success]" if self.player.equippedTitle == title else ""
            console.print(f"  [cyan]{i}.[/cyan] \"{preview}\"{equippedTag}")

        choice = console.input("\n[cyan]Equip which title? (0 to clear your title, Enter to cancel):\n> [/cyan]").strip()
        if choice == "":
            return
        try:
            index = int(choice)
            if index == 0:
                self.player.equippedTitle = None
                printSuccess("Title cleared.")
            elif 1 <= index <= len(self.player.titles):
                self.player.equippedTitle = self.player.titles[index - 1]
                printSuccess(f"Now displayed as: {self.player.formatTitledName()}")
            else:
                printWarning("Invalid choice!")
        except ValueError:
            printWarning("Invalid input!")
        pause()

    def displayMilestones(self):
        clearScreen()
        printHeader("Milestones")

        byAct: Dict[int, List[Milestone]] = {}
        for milestone in MILESTONES.values():
            byAct.setdefault(milestone.act, []).append(milestone)

        for act in sorted(byAct.keys(), key=_actSortKey):
            console.print(f"\n[bold gold]{ACT_NAMES.get(act, f'Act {act}')}[/bold gold]")
            for milestone in byAct[act]:
                progress = self.milestoneProgress.get(milestone.id, 0)
                target = milestone.target
                isComplete = milestone.id in self.completedMilestones

                credits = _milestoneCredits(milestone.act)
                if isComplete:
                    console.print(f"  [success]✓[/success] [bold]{milestone.name}[/bold] [cyan dim](+{credits} Credits)[/cyan dim]")
                else:
                    console.print(f"  [dim]○[/dim] [bold]{milestone.name}[/bold] [dim]({min(progress, target)}/{target})[/dim] [cyan dim](+{credits} Credits)[/cyan dim]")
                console.print(f"      [dim]{milestone.description}[/dim]")

...