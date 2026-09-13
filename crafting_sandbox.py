"""
Crafting Sandbox - Test your crafting runes!
"""
from scripts.items.items import ItemRarity
from scripts.items.equipment import Equipment
from scripts.crafting.chaosRune import CHAOS_RUNES
from scripts.crafting.erasingRune import ERASING_RUNES
from scripts.crafting.growthRune import GROWTH_RUNES
from scripts.crafting.randomiserRunes import RANDOMISER_RUNES
from scripts.crafting.uniqueRunes import UNIQUE_RUNES
from scripts.crafting.masteryRune import MASTERY_RUNES
from scripts.crafting.rarityRune import RARITY_RUNES
from scripts.crafting.destabilisationRune import DESTABILISATION_RUNES
from scripts.crafting.revealingRune import REVEALING_RUNES
from scripts.crafting.manipulationRune import MANIPULATION_RUNES
from scripts.crafting.base import CraftOutcome, CraftResult
from scripts.styles import console, pause, printError
from scripts.korusFeedClient import reportItem
from rich.prompt import Prompt, IntPrompt
from copy import deepcopy

# mirrors Forge._IGNORES_FORESIGHT - runes whose effect isn't captured by a prefix/suffix
# slot snapshot (mastery/rarity/base type/etc change something Foresight can't preview-and-restore)
IGNORES_FORESIGHT = frozenset({'mastery', 'conversion', 'revealing', 'rarity', 'base type', 'mythic chaos'})

def createTestItem():
    """Create a test item for crafting"""
    console.print("[cyan bold]=== Create Test Item ===[/cyan bold]")

    # Choose slot
    slots = ['weapon', 'head', 'chest', 'legs', 'feet', 'ring', 'amulet', 'offhand', 'sigil']
    console.print("\n[bold]Available slots:[/bold]")
    for i, slot in enumerate(slots, 1):
        console.print(f"{i}. {slot.title()}")
    slotChoice = IntPrompt.ask("Choose slot", choices=[str(i) for i in range(1, len(slots)+1)])
    slot = slots[int(slotChoice)-1]

    # Choose rarity
    rarities = [ItemRarity.COMMON, ItemRarity.UNCOMMON, ItemRarity.RARE, ItemRarity.EPIC, ItemRarity.LEGENDARY, ItemRarity.MYTHIC]
    console.print("\n[bold]Available rarities:[/bold]")
    for i, rarity in enumerate(rarities, 1):
        console.print(f"{i}. {rarity.value.title()}")
    rarityChoice = IntPrompt.ask("Choose rarity", choices=[str(i) for i in range(1, len(rarities)+1)])
    rarity = rarities[int(rarityChoice)-1]

    # Choose level
    level = IntPrompt.ask("Choose item level", default=100)

    if rarity == ItemRarity.MYTHIC and level < 60:
        printError("[ERROR] Mythic items cannot be below level 60")
        return False

    # Generate item
    item = Equipment._generateEquipmentPiece(level, slot, rarity, playerName='Sandbox')

    console.print("\n[green bold]✓ Item created![/green bold]")
    console.print(item)
    
    return item

def getAllRunes():
    """Get all available runes"""
    allRunes = {}
    allRunes.update({f"chaos_{k}": v for k, v in CHAOS_RUNES.items()})
    allRunes.update({f"erasing_{k}": v for k, v in ERASING_RUNES.items()})
    allRunes.update({f"growth_{k}": v for k, v in GROWTH_RUNES.items()})
    allRunes.update({f"randomiser_{k}": v for k, v in RANDOMISER_RUNES.items()})
    allRunes.update({f"unique_{k}": v for k, v in UNIQUE_RUNES.items()})
    allRunes.update({f"mastery_{k}": v for k, v in MASTERY_RUNES.items()})
    allRunes.update({f"rarity_{k}": v for k, v in RARITY_RUNES.items()})
    allRunes.update({f"destabilisation_{k}": v for k, v in DESTABILISATION_RUNES.items()})
    allRunes.update({f"revealing_{k}": v for k, v in REVEALING_RUNES.items()})
    allRunes.update({f"manipulation_{k}": v for k, v in MANIPULATION_RUNES.items()})
    return allRunes

def displayRuneCategories():
    """Display rune categories"""
    categories = {
        "1": ("Chaos Runes", CHAOS_RUNES),
        "2": ("Erasing Runes", ERASING_RUNES),
        "3": ("Growth Runes", GROWTH_RUNES),
        "4": ("Randomiser Runes", RANDOMISER_RUNES),
        "5": ("Unique Runes", UNIQUE_RUNES),
        "6": ("Mastery Runes", MASTERY_RUNES),
        "7": ("Rarity Runes", RARITY_RUNES),
        "8": ("Destabilisation Runes", DESTABILISATION_RUNES),
        "9": ("Revealing Runes", REVEALING_RUNES),
        "10": ("Manipulation Runes", MANIPULATION_RUNES)
    }
    
    console.print("\n[cyan bold]=== Rune Categories ===[/cyan bold]")
    for num, (name, _) in categories.items():
        console.print(f"{num}. {name}")
    console.print("0. View item stats")
    console.print("q. Quit")
    
    return categories

def selectRuneFromCategory(categoryRunes):
    """Select a specific rune from a category"""
    console.print("\n[bold]Available runes:[/bold]")
    runeList = list(categoryRunes.items())
    for i, (_, rune) in enumerate(runeList, 1):
        console.print(f"{i}. {rune}")

    choice = Prompt.ask("Choose rune (or 'b' to go back)", 
                       choices=[str(i) for i in range(1, len(runeList)+1)] + ['b'])
    
    if choice == 'b':
        return None
    
    return runeList[int(choice)-1][1]

def craftingSandbox():
    """Main crafting sandbox loop"""
    console.print("[gold1 bold]═══════════════════════════════════[/gold1 bold]")
    console.print("[gold1 bold]    CRAFTING SANDBOX - TEST MODE   [/gold1 bold]")
    console.print("[gold1 bold]═══════════════════════════════════[/gold1 bold]\n")
    
    item = createTestItem()
    if not item:
        exit()
    
    while not item.entropyLocked and not item.destabilised:
        categories = displayRuneCategories()
        
        choice = Prompt.ask("\nSelect category")
        
        if choice == 'q':
            console.print("\n[yellow]Exiting sandbox...[/yellow]")
            break
        
        if choice == '0':
            console.print("\n" + "="*50)
            console.print(item.detailed())
            console.print("="*50)
            continue
        
        if choice not in categories:
            console.print("[red]Invalid choice![/red]")
            continue
        
        categoryName, categoryRunes = categories[choice]
        console.print(f"\n[cyan bold]=== {categoryName} ===[/cyan bold]")
        
        rune = selectRuneFromCategory(categoryRunes)
        if rune is None:
            continue
        
        # Apply the rune (Foresight-aware, mirrors Forge.craftingInterface())
        console.print(f"\n[yellow]Applying {rune.name}...[/yellow]")

        if item.foresighted:
            if any(n in rune.name.lower() for n in IGNORES_FORESIGHT):
                console.print(f"[yellow]{rune.name} ignores Foresight! This will not consume foresight.[/yellow]")
                if Prompt.ask("Apply anyway?", choices=['y', 'n']) == 'y':
                    result = rune.apply(item)
                    reportItem(item, 'Sandbox', f'Applied {rune.name}:\n{result.message}')
                else:
                    continue

            elif rune.name in item.foresightResults:
                console.print(f"[medium_violet_red]This Rune has had its results foretold already. Results:[/medium_violet_red]\n{item.foresightResults[rune.name]['message']}")
                if Prompt.ask(f"Apply {rune.name}? This will consume your Foresight.", choices=['y', 'n']) == 'y':
                    foreseenMessage = item.foresightResults[rune.name]['message']
                    for kind in ['prefixes', 'suffixes']:
                        for data in item.foresightResults[rune.name][kind]:
                            if kind == 'prefixes':
                                item.prefixSlots[data['slot']].affix = data['affix']
                            else:
                                item.suffixSlots[data['slot']].affix = data['affix']

                    item.foresighted = False
                    item.foresightResults = {}
                    item.update()
                    item._generateName()
                    realEntropy = round(rune.successEntropy * 1.3, 3)
                    item.addEntropy(realEntropy)
                    reportItem(item, 'Sandbox', f'Applied {rune.name} and consumed Foresight')
                    result = CraftResult(
                        outcome=CraftOutcome.SUCCESS,
                        message=foreseenMessage,
                        entropyAdded=realEntropy
                    )
                else:
                    continue

            else:
                fakeItem = deepcopy(item)
                result = rune.apply(fakeItem)
                if result.outcome in [CraftOutcome.SUCCESS, CraftOutcome.PARTIAL_SUCCESS]:
                    changes = {'prefixes': [], 'suffixes': [], 'message': result.message}
                    for i in range(len(item.prefixSlots)):
                        changes['prefixes'].append({'slot': i, 'affix': fakeItem.prefixSlots[i].affix})
                    for i in range(len(item.suffixSlots)):
                        changes['suffixes'].append({'slot': i, 'affix': fakeItem.suffixSlots[i].affix})
                    item.foresightResults[rune.name] = changes
                    reportItem(fakeItem, 'Sandbox', f'Foresight Rune saw the results of {rune.name}. Results:\n{result.message}')
                else:
                    printError(f"Attempted to apply {rune.name} to {item.name} but failed:\n{result.message}")
                console.print(f"\n{result.message}\n")
                pause()
                console.print("\n" + "="*50)
                console.print(item)
                console.print("="*50)
                continue
        else:
            result = rune.apply(item)
            reportItem(item, 'Sandbox', f'Applied {rune.name}:\n{result.message}')

        if result.outcome == CraftOutcome.NO_EFFECT:
            console.print("[red]✗ Rune had no effect![/red]")
        elif result.outcome == CraftOutcome.SUCCESS:
            console.print("[green bold]✓ Rune applied successfully![/green bold]")
        elif result.outcome == CraftOutcome.PARTIAL_SUCCESS:
            console.print("[yellow]⚠ Rune partially succeeded[/yellow]")
        console.print(f"\n{result.message}\n")
        pause()

        # Show updated item
        console.print("\n" + "="*50)
        console.print(item)
        console.print("="*50)
        
        if item.entropyLocked:
            console.print("\n[red bold]ITEM IS ENTROPY LOCKED - NO MORE CRAFTING POSSIBLE[/red bold]")
        if item.destabilised:
            console.print("\n[dark_red bold]ITEM IS CORRUPTED - NO MORE CRAFTING POSSIBLE[/dark_red bold]")
    
    console.print("\n[gold1 bold]=== FINAL ITEM ===[/gold1 bold]")
    console.print(item)
    console.print("\n[cyan]Thanks for using the crafting sandbox![/cyan]")

if __name__ == "__main__":
    craftingSandbox()
    exit()