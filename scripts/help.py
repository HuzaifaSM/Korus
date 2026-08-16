from .styles import (
    clearScreen, printHeader, console, printWarning, pause, checkGlobalCommand
    )

class Help:
    def helpMenu(self):
        while True:
            clearScreen()
            printHeader("HELP & GUIDE")
            
            console.print("\n[bold cyan]=== Help Topics ===[/bold cyan]\n")
            console.print("[dim]0.[/dim] [red]Return[/red]")
            console.print("[dim]1.[/dim] [green]Getting Started[/green]")
            console.print("[dim]2.[/dim] [cyan]Combat System[/cyan]")
            console.print("[dim]3.[/dim] [yellow]Camp Buildings[/yellow]")
            console.print("[dim]4.[/dim] [magenta]Classes & Abilities[/magenta]")
            console.print("[dim]5.[/dim] [orange1]Equipment & Items[/orange1]")
            console.print("[dim]6.[/dim] [blue]Difficulty & Progression[/blue]")
            
            choice = console.input("\n[cyan]Choose topic:\n> [/cyan]").strip()
            checkGlobalCommand(choice)

            try:
                choice = int(choice)
                match choice:
                    case 0:
                        break
                    case 1:
                        self._helpGettingStarted()
                    case 2:
                        self._helpCombat()
                    case 3:
                        self._helpCamp()
                    case 4:
                        self._helpClasses()
                    case 5:
                        self._helpEquipment()
                    case 6:
                        self._helpProgression()
                    case _:
                        printWarning("Invalid choice!")
            except ValueError:
                printWarning("Please enter a number!")
            pause()

    def _helpGettingStarted(self):
        clearScreen()
        printHeader("Getting Started")
        
        guide = """
    [bold cyan]Welcome to Korus![/bold cyan]

    [bold yellow]First Steps:[/bold yellow]
    1. [green]Explore[/green] to find enemies and gain XP, gold, and resources
    2. Visit the [red]Camp[/red] after battles to heal and upgrade
    3. [cyan]Equip better gear[/cyan] from your inventory to boost stats
    4. [magenta]Learn new abilities[/magenta] at the Training Grounds

    [bold yellow]Resource Management:[/bold yellow]
    - [gold]Gold[/gold]: Used for buying items and upgrades
    - [cyan]Resources[/cyan]: Dropped by enemies, used for crafting and upgrading
    - [blue]Runes[/blue]: Dropped by enemies, used to modify equipment in various ways

    [bold yellow]Quick Tips:[/bold yellow]
    - Heal at the [red]Campfire[/red] between fights (uses supplies)
    - Check the [green]Market[/green] regularly for resources and new pieces of equipment
    - [orange1]Upgrade camp stations[/orange1] to unlock new features
    - Save your game frequently!

    [dim]Press Enter to return...[/dim]
    """
        console.print(guide)

    def _helpCombat(self):
        clearScreen()
        printHeader("Combat System")
        
        guide = """
    [bold cyan]Combat Basics:[/bold cyan]

    [bold yellow]Turn Order:[/bold yellow]
    - Initiative determined by [speed]Speed[/speed] stat
    - Higher speed = earlier turns
    - Check the turn order at battle start

    [bold yellow]Actions:[/bold yellow]
    - [cyan]Basic Attack[/cyan]: Use your base damage (no cooldown)
    - [magenta]Abilities[/magenta]: Powerful attacks with cooldowns
    - [green]Consumables[/green]: Use potions (free action)
    - [yellow]Flee[/yellow]: Escape from battle

    [bold yellow]Status Effects:[/bold yellow]
    - [dot]DoTs[/dot]: Bleed, Burn, Poison, Curse (damage over time)
    - [cc]CC[/cc]: Stun, Freeze, Slow (crowd control)
    - [debuff]Debuffs[/debuff]: Weaken, Vulnerable, Exposed, Exposure
    - [buff]Buffs[/buff]: Regeneration, Shield, Lifesteal

    [dim]Press Enter to return...[/dim]
    """
        console.print(guide)

    def _helpCamp(self):
        clearScreen()
        printHeader("Camp Buildings")
        
        guide = """
    [bold cyan]Camp Overview:[/bold cyan]

    Your camp contains 4 stations that grow stronger as you upgrade them.
    Upon reaching level 1 of a camp, you will begin finding specific resources for them whenever winning a combat.

    [bold red]1. CAMPFIRE (Healing & Potions)[/bold red]
    - Adds supplies to combat rewards (Level 1+)
    - Automatically heals you after each victory (Level 1+)
    - [green]Rest[/green]: Use supplies found from combat to heal to full HP
    - [cyan]Brew Potions[/cyan]: Create health potions (Level 2+)

    [bold yellow]2. FORGE (Equipment Upgrades)[/bold yellow]
    - [gold3]Craft Equipment[/gold3] (Level 1+)
    - [green]Repair[/green]: Fix damaged equipment
    - [cyan]Apply Runes[/cyan]: Use your runes to modify equipment

    [bold green]3. MARKET (Trading)[/bold green]
    - [cyan]Buy/Sell[/cyan]: Trade resources and equipment
    - [yellow]Force Restock[/yellow]: Refresh shop inventory (Level 1+)
    - Stock updates every hour automatically

    [bold blue]4. QUEST BOARD (Objectives)[/bold blue] (currently not working)
    - [green]Accept Quests[/green]: Take on challenges
    - [yellow]Complete Quests[/yellow]: Earn XP, gold, and items
    - Quest limit increases with level

    [dim]Press Enter to return...[/dim]
    """
        console.print(guide)

    def _helpClasses(self):
        clearScreen()
        printHeader("Classes & Ascendancies")

        guide = """
    [bold cyan]Player Classes:[/bold cyan] (REDO COMPLETELY)

    [class_cultist]Cultist[/class_cultist] | [chaos]Chaos Damage[/chaos]

    [class_druid]Druid[/class_druid] | [earth]Earth Damage[/earth]

    [class_fighter]Fighter[/class_fighter] | [physical]Physical Damage[/physical]

    [class_mage]Mage[/class_mage] | [arcane]Arcane Damage[/arcane]

    [class_monk]Monk[/class_monk] | [lightning]Lightning[/lightning] and [cold]Cold[/cold] Damage

    [class_paladin]Paladin[/class_paladin] | [holy]Holy Damage[/holy]
    
    [class_spectre]Spectre[/class_spectre] | [ethereal]Ethereal Damage[/ethereal]

    [class_wanderer]Wanderer[/class_wanderer] | [psychic]Psychic Damage[/psychic]

    [class_warrior]Warrior[/class_warrior] | [fire]Fire Damage[/fire]

    [class_wretch]Wretch[/class_wretch] | [dark]Dark Damage[/dark]

    [dim]Press Enter to return...[/dim]
    """
        console.print(guide)

    def _helpEquipment(self):
        clearScreen()
        printHeader("Equipment & Items")
        
        guide = """
    [bold cyan]Equipment System:[/bold cyan]

    [bold yellow]Equipment Slots:[/bold yellow]
    - [red]Weapon[/red]: Main damage source
    - [cyan]Armor[/cyan]: Head, Chest, Legs, Feet
    - [gold]Accessories[/gold]: Ring, Amulet

    [bold yellow]Rarity Tiers:[/bold yellow]
    [common]Common[/common] → [uncommon]Uncommon[/uncommon] → [rare]Rare[/rare] → [epic]Epic[/epic] → [legendary]Legendary[/legendary]
    Higher rarity = better stats and more stat slots

    [bold yellow]Equipment Sources:[/bold yellow]
    - [green]Enemy Drops[/green]: Random loot from victories
    - [cyan]Forge[/cyan]: Craft with blueprints
    - [yellow]Market[/yellow]: Buy from shop inventory

    [bold yellow]Equipment Management:[/bold yellow]
    - [green]Equip/Unequip[/green]: Move items between equipment and storage
    - [yellow]Compare[/yellow]: Check stat differences
    - [red]Repair[/red]: Fix durability at Forge
    - [cyan]Upgrade[/cyan]: Use runes at the Forge
    - [gold]Sell[/gold]: Trade unwanted gear at Market

    [bold yellow]Item Types:[/bold yellow]

    [cyan]Resources[/cyan]:
    - Wood, Stone, Iron Ore (common materials)
    - Crystal, Soul, Mana Essence (rare materials)
    - Diamond, Dragon Scale, Ascended Essence (legendary)

    [green]Consumables[/green]:
    - Health Potions (Small → Godly)
    - Brew at Campfire Level 2+

    [dim]Press Enter to return...[/dim]
    """
        console.print(guide)

    def _helpProgression(self):
        clearScreen()
        printHeader("Difficulty & Progression")
        
        guide = """
    [bold cyan]Difficulty Levels:[/bold cyan]

    [green]EASY (0.75x)[/green]: Enemies have 75% stats
    - Perfect for learning the game
    - Lower risk, steady progression

    [cyan]NORMAL (1.0x)[/cyan]: Standard difficulty
    - Balanced challenge
    - Recommended for first playthrough

    [orange1]HARD (1.5x)[/orange1]: Enemies have 150% stats
    - For experienced players
    - Better rewards, higher risk

    [red]HELL (2.0x)[/red]: Enemies have 200% stats
    - Brutal challenge for veterans
    - Extreme difficulty, rewarding completion

    [bold red]HARDCORE MODE:[/bold red]
    - Save file deleted on death
    - Cannot be toggled after game starts
    - For the ultimate challenge

    [bold yellow]Area Level:[/bold yellow]
    - Increases every 5-15 victories
    - Higher area level = stronger enemies
    - You can reduce Area Level by 1 by spending 3 Souls. (NYI)

    [dim]Press Enter to return...[/dim]
    """
        console.print(guide)

...