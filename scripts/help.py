from .styles import (
    clearScreen, printHeader, console, printWarning, pause
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
    - [yellow]Skill Points[/yellow]: Earned from victories, spent at Training Grounds
    - [green]Supplies/Fuel/Blueprints[/green]: Used at specific camp stations

    [bold yellow]Quick Tips:[/bold yellow]
    - Heal at the [red]Campfire[/red] between fights (uses supplies)
    - Check the [green]Market[/green] regularly for good deals
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
    - [debuff]Debuffs[/debuff]: Weaken, Vulnerable, Exposed
    - [buff]Buffs[/buff]: Regeneration, Shield, Lifesteal

    [bold yellow]Strategy Tips:[/bold yellow]
    - Use abilities on cooldown for maximum damage
    - Target low-health enemies first
    - Check enemy resistances before choosing attacks

    [dim]Press Enter to return...[/dim]
    """
        console.print(guide)

    def _helpCamp(self):
        clearScreen()
        printHeader("Camp Buildings")
        
        guide = """
    [bold cyan]Camp Overview:[/bold cyan]

    Your camp contains 6 stations that grow stronger as you upgrade them.

    [bold red]1. CAMPFIRE (Healing & Potions)[/bold red]
    - [green]Rest[/green]: Use supplies to heal to full HP
    - [cyan]Brew Potions[/cyan]: Create health potions (Level 2+)
    - Automatically heals you after each victory ([heal]+20% healing per level[/heal])

    [bold cyan]2. CRAFTER (Equipment Creation)[/bold cyan]
    - [yellow]Craft Equipment[/yellow]: Create new gear with blueprints
    - [magenta]Enchant Equipment[/magenta]: Add special properties (Level 3+)
    - Higher levels = better rarity chances

    [bold yellow]3. FORGE (Equipment Upgrades)[/bold yellow]
    - [green]Repair[/green]: Fix damaged equipment
    - [cyan]Upgrade Stats[/cyan]: Boost equipment values
    - [orange1]Add Stats[/orange1]: Give equipment new properties (Level 2+)
    - [red]Reforge[/red]: Reroll all stats (Level 2+)

    [bold magenta]4. TRAINING GROUNDS (Abilities)[/bold magenta]
    - [green]Learn Abilities[/green]: Purchase new attacks
    - [cyan]Upgrade Damage[/cyan]: Increase ability power
    - [yellow]Reduce Cooldown[/yellow]: Use abilities more often (Level 2+)
    - [orange1]Upgrade Mechanics[/orange1]: Enhance effects (Level 3+)
    - [red]Train Stats[/red]: Boost base stats (Level 4+)
    - [gold1]Increase Max Level[/gold1]: Raise level cap (Level 5+)

    [bold green]5. MARKET (Trading)[/bold green]
    - [cyan]Buy/Sell[/cyan]: Trade resources and equipment
    - [yellow]Force Restock[/yellow]: Refresh shop inventory (Level 1+)
    - Stock updates every hour automatically

    [bold blue]6. QUEST BOARD (Objectives)[/bold blue]
    - [green]Accept Quests[/green]: Take on challenges
    - [yellow]Complete Quests[/yellow]: Earn XP, gold, and items
    - Quest limit increases with level

    [bold yellow]Priority Upgrades:[/bold yellow]
    1. [red]Campfire to Level 2[/red] (unlock potion brewing)
    2. [magenta]Training Grounds to Level 2[/magenta] (cooldown reduction)
    3. [cyan]Crafter to Level 1[/cyan] (equipment crafting)
    4. [yellow]Forge to Level 1[/yellow] (repairs and upgrades)

    [dim]Press Enter to return...[/dim]
    """
        console.print(guide)

    def _helpClasses(self):
        clearScreen()
        printHeader("Classes & Abilities")
        
        guide = """
    [bold cyan]Player Classes:[/bold cyan]

    [bold red]WARRIOR[/bold red] (Fire Damage)
    - Builds [damage]Rage[/damage] during combat
    - Higher rage = more damage
    - Rage converts to healing after battle
    - [buff]High burst damage.[/buff]

    [bold magenta]ROGUE[/bold magenta] (Dark Damage)
    - Gains [buff]Siphon[/buff] stacks on hit. Each Siphon stack grants 5% lifesteal. Stacks up to 10 stacks.
    - [buff]First Strike[/buff] abilities deal 2x damage to full HP enemies
    - High speed and critical chance
    - [buff]Strong opener, good sustain.[/buff]

    [bold purple]MAGE[/bold purple] (Arcane Damage)
    - Uses [cyan]Mana[/cyan] to empower elemental attacks
    - Bonus damage for using same element consecutively
    - [buff]Versatile damage types.[/buff]

    [bold white]FIGHTER[/bold white] (Physical Damage)
    - Builds [buff]Combo[/buff] with each hit
    - Combo multiplies damage exponentially
    - [buff]Quickly ramps damage.[/buff]

    [bold bright_cyan]RANGER[/bold bright_cyan] (Wind Damage)
    - High [buff]Dodge Chance[/buff] (scales with level)
    - [debuff]Blind[/debuff] enemies to reduce accuracy
    - [buff]High base speed, chance to dodge.[/buff]

    [bold green]DRUID[/bold green] (Earth Damage)
    - Shapeshifts between [human]Human[/human] and [beast]Beast[/beast] forms each turn
    - Builds [earth]Thorns[/earth] for defense
    - [nature]Nature[/nature] abilities generate thorns (human form)
    - [harvest]Harvest[/harvest] abilities consume thorns as cost (beast form)
    - [buff]Versatile playstyle due to switching forms.[/buff]

    [bold gold1]PALADIN[/bold gold1] (Holy Damage)
    - Gains [gold1]Divine Favour[/gold1] each turn
    - Spends favour for random combat buffs
    - [buff]High health, strong attacks. Power of RNGesus[/buff]

    [bold cyan]MONK[/bold cyan] (Lightning/Cold)
    - Alternates between [lightning]Lightning[/lightning] and [cold]Cold[/cold] damage
    - Gains permanent [buff]Combat Prowess[/buff] (damage + speed)
    - [buff]Highly balanced, quickly scales and allows potential to ignore resistances[/buff]

    [bold yellow]Ability Tips:[/bold yellow]
    - Learn abilities that complement your class
    - Upgrade ability damage at Training Grounds
    - Reduce cooldowns to use abilities more often
    - Upgrade mechanics to enhance effects (e.g., Bleed → Lacerate)

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
    [common]Common[/common] → [uncommon]Uncommon[/uncommon] → [rare]Rare[/rare] → [epic]Epic[/epic] → [legendary]Legendary[/legendary] → [unique]Unique[/unique]
    Higher rarity = better stats and more stat slots

    [bold yellow]Equipment Sources:[/bold yellow]
    - [green]Enemy Drops[/green]: Random loot from victories
    - [cyan]Crafter[/cyan]: Craft with blueprints
    - [yellow]Market[/yellow]: Buy from shop inventory

    [bold yellow]Equipment Management:[/bold yellow]
    - [green]Equip/Unequip[/green]: Move items between equipment and storage
    - [yellow]Compare[/yellow]: Check stat differences
    - [red]Repair[/red]: Fix durability at Forge
    - [cyan]Upgrade[/cyan]: Boost stats at Forge
    - [gold]Sell[/gold]: Trade unwanted gear at Market

    [bold yellow]Item Types:[/bold yellow]

    [cyan]Resources[/cyan]:
    - Wood, Stone, Iron Ore (common materials)
    - Crystal, Soul, Mana Essence (rare materials)
    - Diamond, Dragon Scale, Ascended Essence (legendary)

    [green]Consumables[/green]:
    - Health Potions (Small → Godly)
    - Brew at Campfire Level 2+

    [bold yellow]Tips:[/bold yellow]
    - Keep higher rarity items even if stats are lower (can upgrade)
    - Sell excess common/uncommon equipment for gold
    - Repair equipment before durability reaches 0
    - Compare equipment before equipping new gear

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

    [bold cyan]Progression Tips:[/bold cyan]

    [bold yellow]Early Game (Level 1-20):[/bold yellow]
    - Focus on [green]upgrading Campfire[/green] for healing
    - Learn a few key [magenta]abilities[/magenta]
    - [cyan]Equip any gear you find[/cyan]

    [bold yellow]Mid Game (Level 21-50):[/bold yellow]
    - Upgrade [cyan]Crafter[/cyan] to craft better equipment
    - Invest in [yellow]ability cooldown reduction[/yellow]
    - Start [red]enchanting and upgrading[/red] equipment
    - Accept [blue]quests[/blue] for extra resources

    [bold yellow]Late Game (Level 51-100):[/bold yellow]
    - Max out [magenta]Training Grounds[/magenta] for stat training
    - Focus on [legendary]Legendary/Unique[/legendary] equipment
    - Upgrade [orange1]ability mechanics[/orange1]
    - Use [gold1]Training Points[/gold1] to boost base stats

    [bold yellow]Endgame (Level 100+):[/bold yellow]
    - Increase [gold1]Max Level[/gold1] at Training Grounds Level 5
    - Perfect your equipment with [cyan]reforging[/cyan]
    - Complete all [blue]quests[/blue]
    - Challenge yourself on Hell difficulty!

    [bold yellow]Area Level:[/bold yellow]
    - Increases every 5-15 victories
    - Higher area level = stronger enemies
    - Scales infinitely for endless progression

    [bold yellow]General Strategy:[/bold yellow]
    - [green]Save frequently[/green]!
    - Balance offense and defense
    - Don't neglect camp upgrades
    - Experiment with different ability combinations
    - Change difficulty if too easy/hard

    [dim]Press Enter to return...[/dim]
    """
        console.print(guide)

...