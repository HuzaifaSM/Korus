from typing import Dict
from .station import Station
from scripts.abilities import ABILITIES
from scripts.styles import (
    console, clearScreen, printHeader, printSeparator, formatDamageType,
    pause, printWarning, printError, printSuccess, printInfo
)

class TrainingGrounds(Station):
    # Learn and upgrade abilities
    # Higher levels: unlock better abilities, upgrade ability mechanics
    def __init__(self, player):
        super().__init__(player, "Training Grounds")
        self.skillPoints = 0
        self.trainingPoints = 0

    def _serialise(self):
        temp = super()._serialise()
        temp['skillPoints'] = self.skillPoints
        temp['trainingPoints'] = self.trainingPoints
        return temp

    def _getUpgradeRequirements(self) -> Dict[int, Dict[str, int]]:
        return {
            1: {"wood": 100, "stone": 50, "iron_ore": 25},
            2: {"iron_ore": 100, "leather": 50, "bone": 30},
            3: {"crystal": 30, "soul": 20, "mana_essence": 15},
            4: {"mana_essence": 50, "diamond": 25, "ancient_wood": 20},
            5: {"dragon_scale": 20, "ascended_essence": 15, "diamond": 50}
        }
    
    def mainMenu(self):
        while True:
            clearScreen()
            printHeader(f"TRAINING GROUNDS - Level {self.level}")
            console.print(f"[gold]Skill Points:[/gold] {self.skillPoints}")
            console.print(f"[gold]Training Points:[/gold] {self.trainingPoints}")
            printSeparator()
            console.print("[dim]0.[/dim] Return")
            console.print("[dim]1.[/dim] Learn New Ability")
            console.print("[dim]2.[/dim] Upgrade Ability Damage")
            console.print("[dim]3.[/dim] Reduce Ability Cooldown")
            console.print("[dim]4.[/dim] Upgrade Ability Mechanics")
            if self.level >= 4:
                console.print("[dim]5.[/dim] Train Base Stats")
            if self.level >= 5:
                console.print("[dim]6.[/dim] Increase Max Level")
            console.print("[dim]9.[/dim] Upgrade Training Grounds")
            
            choice = console.input("\n[cyan]>[/cyan] ").strip()
            try:
                choice = int(choice)
                match choice:
                    case 0:
                        break
                    case 1:
                        self.learnAbility()
                    case 2:
                        self.upgradeAbilityDamage()
                    case 3:
                        self.reduceAbilityCooldown()
                    case 4:
                        self.upgradeAbilityMechanics()
                    case 5:
                        if self.level >= 4:
                            self.trainBaseStats()
                    case 6:
                        if self.level >= 5:
                            self.increaseMaxLevel()
                    case 9:
                        self.upgrade()
                    case _:
                        printWarning(f"Invalid choice: {choice}")
            except ValueError as e:
                printError(f"{e}")
                pause()

    def learnAbility(self):
        clearScreen()
        printHeader("Learn Ability")

        available = []
        for name, ability in ABILITIES.items():
            if (name not in self.player._abilities and
                self.player._level >= ability.levelReq):
                available.append((name, ability))
        if not available:
            printWarning("No available abilities to learn.")
            pause()
            return
        
        console.print(f"\n[yellow]Gold: {self.player._gold}g[/yellow]")
        console.print(f"[cyan]Skill Points: {self.skillPoints}[/cyan]\n")
        
        console.print("\n[gold]Available abilities:[/gold]")
        for i, (name, ability) in enumerate(available, 1):
            cost = ability.levelReq * 10 * max(1, len(ability._mechanics))
            skillCost = ability.levelReq + len(ability._mechanics)
            console.print(f"  [cyan]{i}.[/cyan] {name} | Cost: [dim]{cost} Gold, {skillCost} Skill Points.[/dim] (Ability level {ability.levelReq})")
            console.print(f"    [dim]Damage: {ability.damage} | Type: {formatDamageType(ability.damageType, ability.damageType)} | Targets: {ability.targets}[/dim]")
            if ability._mechanics:
                console.print(f"    [dim]Effects: {', '.join(ability._mechanics)}[/dim]")

        choice = console.input("\n[cyan]Choose ability to learn (0 to cancel):\n> [/cyan]").strip()
        try:
            index = int(choice) - 1
            if 0 <= index < len(available):
                name, ability = available[index]
                cost = ability.levelReq * 10 * min(1, len(ability._mechanics))
                
                if self.player._gold >= cost:
                    self.player._gold -= cost
                    self.player.gainAbility(name, True)
                else:
                    printWarning("\nInsufficient resources.")
        except ValueError:
            pass
        pause()

    def upgradeAbilityDamage(self):
        clearScreen()
        printHeader("Upgrade Ability Damage")

        if not self.player._abilities:
            printWarning("No abillities to upgrade!")
            pause()
            return
        
        console.print("\n[gold]Your Abilities:[/gold]")
        abilitiesList = list(self.player._abilities.items())
        for i, (name, ability) in enumerate(abilitiesList, 1):
            cost = 5 + (ability.damage // 10) + len(ability._mechanics)
            console.print(f"  [cyan]{i}.[/cyan] {name}")
            console.print(f"    [dim]Damage: {ability.damage}[/dim]")
            console.print(f"  - [dim]Upgrade Cost: {cost} Skill Points[/dim]")
        
        choice = console.input("\n[cyan]Choose ability (0 to cancel):\n> [/cyan]").strip()
        try:
            index = int(choice) - 1
            if 0 <= index < len(abilitiesList):
                name, ability = abilitiesList[index]
                cost = 5 + (ability.damage // 10) + len(ability._mechanics)
                upgradeAmount = (5 + (ability.levelReq // 2.5) * 2)

                console.print(f"\n[bold]Upgrade {name}'s damage by +{upgradeAmount}[bold]")
                console.print(f"  [dim]- Cost: {cost} Skill Points[/dim]")
                confirm = console.input("\n[cyan]Confirm? (y/n):\n> [/cyan]").strip().lower()
                if confirm == 'y':
                    if self.skillPoints >= cost:
                        self.skillPoints -= cost
                        ability.damage += upgradeAmount
                        printSuccess(f"\n{name} damage increased to {ability.damage}.")
                    else:
                        printWarning("Insufficient skill points to upgrade.")
        except ValueError:
            pass
        pause()

    def reduceAbilityCooldown(self):
        if self.level < 2:
            printWarning(f"Training Grounds Level 2 required to reduce cooldowns. Current level: {self.level}")
            pause()
            return
        clearScreen()
        printHeader("Reduce Ability Cooldown")

        if not self.player._abilities:
            printWarning("No abilities to upgrade.")
            pause()
            return
        
        console.print("\n[gold]Your Abilities:[/gold]")
        abilitiesList = list(self.player._abilities.items())
        for i, (name, ability) in enumerate(abilitiesList, 1):
            cost = ability.maxCooldown * 20
            console.print(f"  [cyan]{i}.[/cyan] {name}")
            console.print(f"    [dim]Current Cooldown: {ability.maxCooldown}[/dim]")
            console.print(f"    [dim]Reduce Cooldown Cost: {cost} Skill Points[/dim]")
        choice = console.input("\n[cyan]Choose ability (0 to cancel):\n> [/cyan]").strip()

        try:
            index = int(choice) - 1
            if 0 <= index < len(abilitiesList):
                name, ability = abilitiesList[index]

                if ability.maxCooldown <= 1:
                    printWarning(f"\n{name}'s Cooldown cannot be reduced further.")
                    pause()
                    return
                
                cost = ability.maxCooldown * 20
                console.print(f"\n[bold]Reduce {name}'s cooldown from {ability.maxCooldown} to {ability.maxCooldown - 1}[/bold]")
                console.print(f"  [dim] - Cost: {cost} Skill Points[/dim]")
                confirm = console.input("\n[cyan]Confirm? (y/n):\n> [/cyan]").strip().lower()
                if confirm == 'y':
                    if self.skillPoints >= cost:
                        self.skillPoints -= cost
                        ability.maxCooldown -= 1
                        printSuccess(f"\n{name}'s cooldown has been reduced to {ability.maxCooldown}.")
                    else:
                        printWarning("\nInsufficient skill points.")
        except ValueError:
            pass
        pause()

    def trainBaseStats(self):
        if self.level < 4:
            printWarning(f"Training Grounds Level 4 requied to train stats. Current level: {self.level}")
            pause()
            return
        clearScreen()
        printHeader("Train Base Stats")

        console.print("\n[gold]Available training:[/gold]")
        console.print("[red1]1. Health[/red1] (+5) - Cost: [dim]5 Soul, 3 Mana Essence, 1 Training Point[/dim]")
        console.print("[damage]2. Damage[/damage] (+1) - Cost: [dim]3 Soul, 5 Mana Essence, 1 Training Point[/dim]")
        console.print("[cyan]3. Speed[/cyan] (+0.01) - Cost: [dim]4 Soul, 4 Mana Essence, 1 Training Point[/dim]")
        
        choice = console.input("\n[cyan]Choose training (0 to cancel):\n> [/cyan]").strip()

        try:
            choice = int(choice)
            match choice:
                case 0:
                    return
                case 1:
                    if self.player.hasItem("soul", 5) and self.player.hasItem("mana_essence", 3) and self.trainingPoints > 0:
                        self.player.removeItem("soul", 5)
                        self.player.removeItem("mana_essence", 3)
                        self.trainingPoints -= 1
                        self.player._baseHealth += 5
                        printSuccess("\nBase Health increased by 5!")
                        self.player._recalculateStats()
                        pause()
                    else:
                        printWarning("Insufficient resources!")
                case 2:
                    if self.player.hasItem("soul", 3) and self.player.hasItem("mana_essence", 5) and self.trainingPoints > 0:
                        self.player.removeItem("soul", 3)
                        self.player.removeItem("mana_essence", 5)
                        self.trainingPoints -= 1
                        self.player._baseDamage += 1
                        printSuccess("\nBase Damage increased by 1!")
                        self.player._recalculateStats()
                        pause()
                    else:
                        printWarning("Insufficient resources!")
                case 3:
                    if self.player.hasItem("soul", 4) and self.player.hasItem("mana_essence", 4) and self.trainingPoints > 0:
                        self.player.removeItem("soul", 4)
                        self.player.removeItem("mana_essence", 4)
                        self.trainingPoints -= 1
                        self.player._baseSpeed += 0.01
                        printSuccess("\nBase Speed increased by 0.01!")
                        self.player._recalculateStats()
                        pause()
                    else:
                        printWarning("Insufficient resources!")
                case _:
                    printWarning("Invalid choice!")
        except ValueError:
            pass
        pause()

    def increaseMaxLevel(self):
        if self.level < 5:
            printWarning(f"Training Grounds Level 5 required to increse max level. Current level: {self.level}")
            pause()
            return
        clearScreen()
        printHeader("[bold gold]Increase Max Level[/bold gold]")
        printInfo("To upgrade max level by 1, it costs: Diamond x250, Ascended Essence x100, Soul x500, Training Points x10")
        printInfo("\nYou have:")
        console.print(f"  - [cyan1]Diamond x{self.player.getItem('diamond')}[/cyan1]")
        console.print(f"  - [gold]Ascended Essence x{self.player.getItem('ascended_essence')}[/gold]")
        console.print(f"  - [grey37]Soul x{self.player.getItem('soul')}[/grey37]")
        console.print(f"  - [violet]Training Points x{self.trainingPoints}[/violet]\n")
        choice = console.input("\n[cyan]Confirm? (y/n)\n> [/cyan]").strip().lower()
        if choice == 'y':
            if self.player.hasItem("diamond", 250) and \
                self.player.hasItem("ascended_essence", 100) and \
                self.player.hasItem("soul", 500) and \
                self.trainingPoints >= 10:

                self.player.removeItem("diamond", 50)
                self.player.removeItem("ascended_essence", 30)
                self.player.removeItem("soul", 100)
                self.trainingPoints -= 10

                self.player._maxLevel += 1
                printSuccess(f"Raised your max level by 1! New Max Level: {self.player._maxLevel}")
                pause()
            else:
                printWarning("Insufficient resources!")
