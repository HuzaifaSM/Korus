"""
Crafting Sandbox - Test your crafting runes!
"""
from scripts.items import Equipment, ItemRarity
from crafting.chaosRune import CHAOS_RUNES
from crafting.erasingRune import ERASING_RUNES
from crafting.growthRune import GROWTH_RUNES
from crafting.randomiserRunes import RANDOMISER_RUNES
from crafting.uniqueRunes import UNIQUE_RUNES
from crafting.masteryRune import MASTERY_RUNES
from crafting.rarityRune import RARITY_RUNES
from crafting.destabilisationRune import DESTABILISATION_RUNES
from crafting.revealingRune import REVEALING_RUNES
from crafting.manipulationRune import MANIPULATION_RUNES
from crafting.base import CraftOutcome
from scripts.styles import console
from rich.prompt import Prompt, IntPrompt

def createTestItem():
    """Create a test item for crafting"""
    console.print("[cyan bold]=== Create Test Item ===[/cyan bold]")
    
    # Choose slot
    slots = ['weapon', 'head', 'chest', 'legs', 'feet', 'ring', 'amulet']
    console.print("\n[bold]Available slots:[/bold]")
    for i, slot in enumerate(slots, 1):
        console.print(f"{i}. {slot.title()}")
    slotChoice = IntPrompt.ask("Choose slot", choices=[str(i) for i in range(1, len(slots)+1)])
    slot = slots[int(slotChoice)-1]
    
    # Choose rarity
    rarities = [ItemRarity.COMMON, ItemRarity.UNCOMMON, ItemRarity.RARE, ItemRarity.EPIC, ItemRarity.LEGENDARY]
    console.print("\n[bold]Available rarities:[/bold]")
    for i, rarity in enumerate(rarities, 1):
        console.print(f"{i}. {rarity.value.title()}")
    rarityChoice = IntPrompt.ask("Choose rarity", choices=[str(i) for i in range(1, len(rarities)+1)])
    rarity = rarities[int(rarityChoice)-1]
    
    # Choose level
    level = IntPrompt.ask("Choose item level", default=100)
    
    # Generate item
    item = Equipment._generateEquipmentPiece(level, slot, rarity)
    
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
        
        # Apply the rune
        console.print(f"\n[yellow]Applying {rune.name}...[/yellow]")
        result = rune.apply(item)
        
        if result == CraftOutcome.NO_EFFECT:
            console.print("[red]✗ Rune had no effect![/red]")
        elif result == CraftOutcome.SUCCESS:
            console.print("[green bold]✓ Rune applied successfully![/green bold]")
        elif result == CraftOutcome.PARTIAL_SUCCESS:
            console.print("[yellow]⚠ Rune partially succeeded[/yellow]")

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