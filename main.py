from os import remove, path
import time
from typing import List, Optional, Dict
from sys import exit
import random
import subprocess

from scripts.player import Player, selectClass, deserialisePlayer
from scripts.enemies.enemy import Enemy, createEnemy
from scripts.combat import CombatManager
from scripts.runeDrops import rollGuaranteedRunes
from scripts.camp import Camp
from scripts.files import save, load, deleteSave, addToDeathLog, logCrash, undoLastOperation, checkForSaves, displayExistingSaves
from scripts.debug import Debugger
from scripts.difficulty import Difficulty
from scripts.help import Help
from scripts.items.equipment import peekNextEquipmentId, setNextEquipmentId
from scripts.korusFeedClient import ensureServerRunning

from scripts.styles import (
    console, printHeader, printSeparator, pause, clearScreen,
    printWarning, printError, printInfo, printSuccess,
    displayDeath, displayVictory,
    createAbilityTables, createCombatStatusTable, createEnemyPreview,
    ReturnToMainMenu, GoToSaveMenu, checkGlobalCommand
)

class Game:
    def __init__(self):
        self.player: Optional[Player] = None
        self.combatManager = CombatManager()
        self.debugAllowed = False
        self.areaLevel = 1
        self.battlesWon = 0
        self.debugger = Debugger(self)
        self.help = Help()

        self.difficulty = Difficulty.NORMAL
        self.hardcoreMode = False
        self.saveNum: Optional[int] = None

    def _serialise(self):
        return {
            'debugAllowed': self.debugAllowed,
            'areaLevel': self.areaLevel,
            'battlesWon': self.battlesWon,
            'difficulty': self.difficulty.value,
            'hardcoreMode': self.hardcoreMode,
            'saveNum': self.saveNum,
            'nextEquipmentID': peekNextEquipmentId()
        }

    def deserialise(self, data: Dict):
        self.debugAllowed = data.get('debugAllowed', False)
        self.areaLevel = data.get('areaLevel', 1)
        self.battlesWon = data.get('battlesWon', 0)
        difficulty = data.get('difficulty', 'normal')
        self.difficulty = Difficulty(difficulty)
        self.hardcoreMode = data.get('hardcoreMode', False)
        self.saveNum = data.get('saveNum')
        setNextEquipmentId(data.get('nextEquipmentID', 1))

    def titleScreen(self):
        while True:
            clearScreen()
            printHeader("Welcome, Traveller, to Korus.")

            console.print("\n[bold cyan]Main Menu[/bold cyan]")
            console.print("[dim]1.[/dim] [green]New Game[/green]")
            console.print("[dim]2.[/dim] [cyan]Load Game[/cyan]")
            console.print("[dim]3.[/dim] [red]Exit[/red]\n")
            
            choice = console.input("[cyan]Choose an option:\n> [/cyan]").strip()

            if choice in ['cheat', 'quick', 'bug', 'skip']:
                self.difficulty = Difficulty.NORMAL
                self.hardcoreMode = False
                name = "The Hero"
                self.player = selectClass(name, True)
                self.camp = Camp(self.player)
                if not self.mainMenu():
                    break
            
            try:
                choice = int(choice)
                match choice:
                    case 1:
                        self.newGame()
                        if not self.mainMenu():
                            break
                    case 2:
                        if self.loadFromTitleScreen():
                            if not self.mainMenu():
                                break
                    case 3:
                        printSuccess("\nThank you for playing!")
                        exit()
                    case _:
                        printWarning("Invalid choice!")
                        pause()
            except ValueError:
                printWarning("Please enter a number!")
                pause()

    def loadFromTitleScreen(self) -> bool:
        clearScreen()
        printHeader("Load Game")

        if not checkForSaves():
            printWarning("No files found!")
            pause()
            return False

        try:
            saves = displayExistingSaves()

            if not saves:
                printWarning("No saves found.")
                pause()
                return False
            
            console.print("[dim]0.[/dim] [red]Cancel[/red]\n")

            saveNum = console.input("[cyan]Enter save number to load:\n> [/cyan]").strip()

            if saveNum == '0':
                return False
            
            data = load(saveNum)
            if data:
                self.player = deserialisePlayer(data['player'])
                self.camp = Camp(self.player)
                self.camp.deserialiseAll(data['camp'], self.player)
                self.deserialise(data['game'])

                try:
                    self.saveNum = int(saveNum)
                except ValueError:
                    pass

                printSuccess(f"Save {saveNum} loaded Successfully!")
                pause()
                return True
            else:
                return False
        except Exception as e:
            printError(f"Error loading saves: {e}")
            pause()
            return False

    def newGame(self):
        clearScreen()
        printHeader("New Game")

        console.print("\n[cyan]What are you called?[/cyan]")
        name = console.input("[bold cyan]>[/bold cyan] ").strip()
        if not name:
            name = "The Hero"

        #self.selectDifficulty() <-- need to rework difficulty
        self.difficulty = Difficulty.NORMAL

        self.player = selectClass(name)
        self.camp = Camp(self.player)
        console.print(f"\n[success]The journey of {name} begins.[/success]")

        console.print(f"\n[info]Difficulty:[/info] {self.difficulty.getDisplayName()}")
        if self.hardcoreMode:
            console.print("[bold red]⚠️  HARDCORE MODE ACTIVE - Save will be deleted on death! ⚠️[/bold red]")

        pause()

    def selectDifficulty(self):
        while True:
            clearScreen()
            printHeader("Select Difficulty")

            console.print("\n[bold cyan]=== Difficulty Options ===[/bold cyan]\n")
            for i, diff in enumerate(Difficulty, 1):
                console.print(f"[dim]{i}.[/dim] {diff.getDisplayName()}")
                console.print(f"    [dim]{diff.getDescription()}[/dim]\n")

            choice = console.input("[cyan]Choose a difficulty (1-4):\n> [/cyan]")
            try:
                index = int(choice) - 1
                if 0 <= index < len(Difficulty):
                    self.difficulty = list(Difficulty)[index]

                    console.print(f"\n[info]Selected:[/info] {self.difficulty.getDisplayName()}")
                    console.print("\n[bold yellow]=== Hardcore Mode ===[/bold yellow]")
                    console.print("[dim]In Hardcore Mode, your save file will be permanently deleted if you die.[/dim]")
                    console.print("[bold warning]This cannot be changed once the game starts.[/bold warning]")
                    
                    hardcore = console.input("\n[warning]Enable Hardcore Mode? (y/N):[/warning]\n> ").strip().lower()
                    self.hardcoreMode = (hardcore == 'y')

                    if self.hardcoreMode:
                        confirm = console.input("\n[bold red]Are you sure? Your save will be deleted on death. (y/N):[/bold red]\n> ").strip().lower()
                        if confirm != 'y':
                            self.hardcoreMode = False
                            console.print("[info]Hardcore mode disabled.[/info]")

                    return
                else:
                    printWarning("Invalid choice!")
            except ValueError:
                printWarning("Please enter a number!")

    def changeDifficulty(self):
        clearScreen()
        printHeader("Change Difficulty")
        
        console.print(f"\n[info]Current Difficulty:[/info] {self.difficulty.getDisplayName()}")
        if self.hardcoreMode:
            console.print("[bold red]Hardcore Mode: ACTIVE (cannot be changed)[/bold red]")
        
        console.print("\n[bold cyan]=== Select New Difficulty ===[/bold cyan]\n")
        
        for i, diff in enumerate(Difficulty, 1):
            current = " [green](Current)[/green]" if diff == self.difficulty else ""
            console.print(f"[dim]{i}.[/dim] {diff.getDisplayName()}{current}")
            console.print(f"    [dim]{diff.getDescription()}[/dim]\n")
        
        console.print("[dim]0.[/dim] [red]Cancel[/red]\n")
        
        choice = console.input("[cyan]Choose new difficulty (1-4, 0 to cancel):\n> [/cyan]").strip()
        
        try:
            if choice == '0':
                return
            
            index = int(choice) - 1
            if 0 <= index < len(Difficulty):
                newDifficulty = list(Difficulty)[index]
                
                if newDifficulty == self.difficulty:
                    printInfo("Difficulty unchanged.")
                else:
                    confirm = console.input(f"\n[dark_red]Change difficulty to {newDifficulty.getDisplayName()}? (y/N):[/dark_red]\n> ").strip().lower()
                    if confirm == 'y':
                        self.difficulty = newDifficulty
                        printSuccess(f"Difficulty changed to {newDifficulty.getDisplayName()}!")
                    else:
                        printInfo("Difficulty unchanged.")
            else:
                printWarning("Invalid choice!")
        except ValueError:
            printWarning("Please enter a number!")
        
        pause()

    def mainMenu(self):
        while True:
            clearScreen()
            if self.player._ascendancy is None:
                printHeader(f"{self.player._name} - Level {self.player._level} {self.player.className}")
            else:
                printHeader(f"{self.player._name} - Level {self.player._level} {self.player._ascendancy} ({self.player.className})")

            dType = f"[{self.player._damageType}]{self.player._damageType.title()}[/{self.player._damageType}]"
            console.print(f"[health]HP:[/health] {self.player._health}/{self.player._maxHealth} | "
                          f"[damage]DMG:[/damage] {self.player._damage} | Type: {dType} | "
                          f"[critical]Crit Chance:[/critical] {self.player.critChance*100:.0f}% | [critical]Crit Damage:[/critical] {self.player.critMulti*100:.0f}% | "
                          f"[speed]SPD:[/speed] {self.player._speed:.2f}")

            defParts = []
            if self.player.armour > 0:
                defParts.append(f"[armour]Armour:[/armour] {self.player.armour}")
            if self.player.evasion > 0:
                defParts.append(f"[evasion]Evasion:[/evasion] {self.player.evasion}")
            if self.player.energyShield > 0:
                defParts.append(f"[energy_shield]Energy Shield:[/energy_shield] {self.player.energyShield}")
            blockChance = self.player._stats['Bonuses'].get('chance_to_block', 0)
            if blockChance > 0:
                defParts.append(f"[cyan]Chance to Block:[/cyan] {blockChance}%")
            defStr = " | ".join(defParts)
            console.print(f"{defStr}")

            console.print(f"[xp]XP:[/xp] {self.player._xp}/{self.player._xpToNextLevel} | [gold1]Gold:[/gold1] {self.player._gold}")
            console.print(f"\n[info]Area Level:[/info] {self.areaLevel} | [success]Battles Won:[/success] {self.battlesWon}")

            difficultyDisplay = self.difficulty.getDisplayName()
            if self.hardcoreMode:
                difficultyDisplay += " [bold red](HARDCORE)[/bold red]"
            console.print(f"[info]Difficulty:[/info] {difficultyDisplay}")

            printSeparator()

            console.print("[dim]0)[/dim] [red]Quit[/red]")
            console.print("[dim]1)[/dim] [green]Explore[/green] [dim](Find Enemies)[dim]")
            console.print("[dim]2)[/dim] [cyan]Player Menu[/cyan]")
            console.print("[dim]3)[/dim] [bright_cyan]Go to Camp[/bright_cyan]")
            console.print("[dim]4)[/dim] [grey58]Options Menu[/grey58]")
            console.print("[dim]5.[/dim] [gold3]View Class Details[/gold3]")
            if self.areaLevel > 1:
                console.print("[dim]6.[/dim] [dark_red]Reduce Area Level by 1[/dark_red] [dim](Costs 3 Souls)[/dim]")
            console.print("[dim]Save:[/dim] [purple3]Enter 'save' for the Save Menu[/purple3]")
            if self.camp.campfire.level > 0:
                console.print(f"[dim]Heal[/dim] [red]Enter 'heal' to use Campfire heal[/red] [dim](Current Supplies: {self.camp.campfire.supplies})")

            choice = console.input("\n[bold cyan]>[/bold cyan] ").strip()

            try:
                checkGlobalCommand(choice)
            except ReturnToMainMenu:
                continue
            except GoToSaveMenu:
                self.saveMenu()
                continue

            if choice.lower() == "debug" or choice.startswith("/"):
                if self.debugAllowed:
                    auto = None
                    if choice.startswith("/"):
                        auto = choice.split("/")[1]
                    self.debugger.mainMenu(autoCommand=auto)
                    continue
                else:
                    continue
            elif choice.lower() == "data":
                console.print("\n[bold cyan]=== ALL GAME DATA ===[/bold cyan]")
                console.print(f"[red]{self._serialise()}[/red]")
                console.print(f"[green]{self.player.serialise()}[/green]")
                console.print(f"[gold1]{self.camp._serialiseAll()}[/gold1]")
                pause()
                continue
            elif choice.lower() in 'heal':
                if self.camp.campfire.level > 0:
                    self.camp.campfire.rest()
                    pause()
                    continue
            try:
                choice = int(choice)
                match choice:
                    case 0:
                        printSuccess("\nThank you for playing!")
                        return False
                    case 1:
                        self.explore()
                    case 2:
                        self.playerMenu()
                    case 3:
                        self.camp.mainMenu()
                    case 4:
                        self.optionsMenu()
                    case 5:
                        clearScreen()
                        printHeader("Player Class Details")
                        playerAsc = self.player._ascendancy
                        ascStr = f"[asc_{playerAsc.lower()}]{playerAsc}[/asc_{playerAsc.lower()}]\n[bold cyan]Description:[/bold cyan]\n{self.player.ascendancyDescription}\n" if playerAsc is not None else ""
                        console.print(f"[{self.player.className.lower()}]{self.player.className}[/{self.player.className.lower()}]")
                        console.print(f"[bold cyan]Description:[/bold cyan]")
                        console.print(self.player.classDescription)
                        console.print(ascStr)
                        pause()
                    case 6:
                        if self.areaLevel > 1:
                            playerSouls = self.player.getItem('soul')
                            if playerSouls >= 3:
                                self.player.removeItem('soul', 3)
                                self.areaLevel -= 1
                                printSuccess("Area Level successfully reduced by 1!")
                            else:
                                printWarning(f"Not enough Souls! You currently have {playerSouls}/3 Souls.")
                            pause()
                    case _:
                        printError("\nInvalid choice.\n")
            except ValueError as e:
                printError(f"[ERROR] {e}")
            except ReturnToMainMenu:
                continue
            except GoToSaveMenu:
                self.saveMenu()
                continue
            pause()

    def playerMenu(self):
        while True:
            clearScreen()
            printHeader("Player Management")

            printSeparator()
            console.print("[dim]0.[/dim] [red]Exit[/red]")
            console.print("[dim]1.[/dim] [cyan]View Resources[/cyan]")
            console.print("[dim]2.[/dim] [green]View Runes[/green]")
            console.print("[dim]3.[/dim] [yellow]Equipment Management[/yellow]")
            console.print("[dim]4.[/dim] [magenta]View Abilities[/magenta]")

            choice = console.input("[bold cyan]>[/bold cyan] ").strip()
            checkGlobalCommand(choice)

            try:
                choice = int(choice)
                match choice:
                    case 0:
                        return
                    case 1:
                        self.player.showInventory()
                        pause()
                    case 2:
                        self.player.showCraftingInventory()
                        pause()
                    case 3:
                        self.player.equipmentMenu()
                    case 4:
                        self.player.showAbilities()
                        pause()
                    case _:
                        printError("\nInvalid choice.\n")
            except ValueError as e:
                printError(f'[ERROR] {e}')

    def optionsMenu(self):
        while True:
            clearScreen()
            printHeader("Options Menu")

            printSeparator()
            console.print("[dim]0.[/dim] [red]Exit[/red]")
            #console.print("[dim]1.[/dim] [gold1]Change Difficulty[/gold1]")
            console.print("[dim]2.[/dim] [green]Help Menu[/green]")
            console.print("[dim]3.[/dim] [orange1]Save Menu[/orange1]")
            debugStr = "Enable" if not self.debugAllowed else "Disable"
            console.print(f"[dim]4.[/dim] [dim cyan]{debugStr} Debugging[/dim cyan]")

            choice = console.input("[bold cyan]>[/bold cyan] ").strip()
            checkGlobalCommand(choice)

            try:
                choice = int(choice)
                match choice:
                    case 0:
                        return
                    case 1:
                        continue
                        self.changeDifficulty()
                    case 2:
                        self.help.helpMenu()
                    case 3:
                        self.saveMenu()
                    case 4:
                        self.debugAllowed = not self.debugAllowed
                        debugStr = "enabled" if self.debugAllowed else "disabled"
                        printSuccess(f"Debug commands have been {debugStr}")
                    case _:
                        printError("\nInvalid choice.\n")
            except ValueError as e:
                printError(f'[ERROR] {e}')

    def saveMenu(self):
        while True:
            clearScreen()
            printHeader("Save Menu")

            if self.saveNum is not None:
                console.print(f"[info]Current save slot: {self.saveNum}[/info]")
            if self.hardcoreMode:
                console.print("[bold red]⚠️  HARDCORE MODE - Save will be deleted on death[/bold red]")

            printSeparator()
            console.print("[dim]0.[/dim] [red]Exit[/red]")
            console.print("[dim]1.[/dim] [green]Save Game[/green]")
            console.print("[dim]2.[/dim] [cyan]Load Game[/cyan]")
            console.print("[dim]3.[/dim] [orange1]Delete File[/orange1]")
            console.print("[dim]4.[/dim] [yellow]Undo Last Operation[/yellow]")
            choice = console.input("\n[bold cyan]>[/bold cyan] ").strip()
            checkGlobalCommand(choice)
            try:
                choice = int(choice)
                match choice:
                    case 0:
                        return
                    case 1:
                        displayExistingSaves()
                        saveNum = console.input("[cyan]Input the save number you want to save to: (0 to cancel)\n[bold]>[/bold][/cyan] ").strip()
                        checkGlobalCommand(saveNum)
                        if saveNum == '0':
                            printWarning("Cancelled Save")
                            return
                        else:
                            save(self, saveNum)
                            try:
                                self.saveNum = int(saveNum)
                            except ValueError:
                                pass
                        break
                    case 2:
                        displayExistingSaves()
                        saveNum = console.input("[cyan]Input the save number you want to load from: (0 to cancel)\n[bold]>[/bold][/cyan] ").strip()
                        checkGlobalCommand(saveNum)
                        if saveNum == '0':
                            printWarning("Cancelled Load")
                            return
                        else:
                            data = load(saveNum)
                            if data:
                                self.player = deserialisePlayer(data['player'])
                                self.camp.deserialiseAll(data['camp'], self.player)
                                self.deserialise(data['game'])
                        try:
                            self.saveNum = int(saveNum) if not self.saveNum else self.saveNum
                        except ValueError:
                            pass
                        break
                    case 3:
                        displayExistingSaves()
                        saveNum = console.input("[cyan]Input the save number you want to delete: (0 to cancel)\n[bold]>[/bold][/cyan] ").strip()
                        checkGlobalCommand(saveNum)
                        if saveNum == '0':
                            printWarning("Cancelled Save Deletion")
                            return
                        deleteSave(saveNum)
                    case 4:
                        undoLastOperation()
                    case _:
                        printError("Invalid choice.")
                        pause()
            except ValueError as e:
                printError(f"{e}")

    def postBattle(self, result: str, enemies: List[Enemy], *, waveEncounter: bool = False, lootBonus: int = 0):
        if result == "victory":
            self.player.onCombatEnd()
            self.battlesWon += 1
            currentAreaLevel = self.areaLevel
            if self.areaLevel > 100:
                self.areaLevel += 1 if self.battlesWon % 20 == 0 else 0
            else:
                self.areaLevel += 1 if self.battlesWon % 10 == 0 else 0
            if currentAreaLevel != self.areaLevel: #if area level increased
                clearScreen()
                printHeader("Area Level Increased!")
                console.print(f"[gold1]=== New Area Level: {self.areaLevel} ===[/gold1]")
                console.print("[warning]Enemies will be stronger, and rewards will be greater...[/warning]")
            self.victory(enemies, waveEncounter, lootBonus)
        elif result == "defeat":
            clearScreen()
            displayDeath()
            console.print("[error]You have been defeated...[/error]")
            console.print("\n[bold]Final Stats:[/bold]")
            console.print(f"[cyan]Level:[/cyan] {self.player._level} | [xp]XP:[/xp] {self.player._xp} / {self.player._xpToNextLevel}")
            console.print(f"[success]Battles Won:[/success] {self.battlesWon}")
            console.print(f"[info]Difficulty:[/info] {self.difficulty.getDisplayName()}")

            if self.hardcoreMode:
                printHeader("HARDCORE MODE - SAVE DELETED", style="bold red")

                try:
                    savePath = f"Korus/data/saves/Save {self.saveNum}.json"
                    if path.exists(savePath):
                        remove(savePath)
                        printInfo(f"Save {self.saveNum} has been permanently deleted.")
                except Exception as e:
                    printError(f"Failed to delete save: {e}")

            addToDeathLog(self)
            exit()

    def _singleCombat(self):
        console.print("[dim]You look around for a fight...[/dim]")
        time.sleep(1)
        console.print("[warning]You've encountered something![/warning]")
        time.sleep(1)
        enemies = self.generateEnemies()

        result = self.startCombat(enemies)
        self.postBattle(result, enemies)

    def _waveCombat(self):
        numWaves = random.randint(2, max(6, (3 + (self.player._level // 15))))
        currentWave = 1
        wavesCompleted = 0
        rewardPerWave = 100 // numWaves # final wave grants 100% increased item rarity/quantity
        lootBonus = 0
        fled = False

        while wavesCompleted < numWaves and not fled:
            console.print(f"[dim]Wave:[/dim] {currentWave}/{numWaves}")

            cont = console.input("[bold red]Continue to the next wave? (Y/N)[/bold red]\n[cyan]>[/cyan] ").lower().strip()

            if cont == 'n':
                fled = True
                console.print("[dim]You fled from the rest of the waves![/dim]")

            elif cont == 'y':

                time.sleep(0.5)
                console.print("[dim]Next Wave Begins![/dim]")
                time.sleep(1)

                lootBonus += rewardPerWave

                enemies = self.generateEnemies(waveEncounter=True, lootBonus=lootBonus)

                result = self.startCombat(enemies)
                self.postBattle(result, enemies, waveEncounter=True, lootBonus=lootBonus)

                currentWave += 1
                wavesCompleted += 1

            else:
                continue

    def explore(self):
        if self.player._level < 20:
            self._singleCombat()
        else:
            while True:
                clearScreen()
                printHeader("Select Combat Style")
                console.print("[dim]0.[/dim] Exit")
                console.print("[dim]1.[/dim] Fight a random Enemy Encounter")
                console.print("[dim]2.[/dim] Fight waves of Enemies")

                try:
                    choice = int(console.input("[cyan]>[/cyan] "))
                    if choice == 0:
                        return
                    elif choice == 1:
                        self._singleCombat()
                    elif choice == 2:
                        self._waveCombat()

                except ValueError:
                    printWarning("Invalid input")
                    continue
                return

    def generateEnemies(self, waveEncounter: bool = False, lootBonus: int = 0) -> List[Enemy]:
        numEnemies = random.randint(min(3, 1 + (self.player._level + self.areaLevel) // 40), min(1 + self.areaLevel//8, 4))
        enemyBonus = self.player._stats['Bonuses']['enemy_quantity']
        multiplier = 1 + (enemyBonus / 100)
        numEnemies = min(8, int(numEnemies * multiplier)) # hard cap at 8 enemies

        enemies = []
        if waveEncounter:
            enemyLevel = self.player._level + (self.areaLevel // 2) - 1
        else:
            enemyLevel = self.player._level + self.areaLevel - 1
        difficulty = self.difficulty.getMultiplier()

        rarity = (self.player._stats['Bonuses']["item_rarity"] + self.player._getExtraBonuses('item_rarity') + lootBonus) / 100
        quantity = (self.player._stats['Bonuses']["item_quantity"] + self.player._getExtraBonuses('item_quantity') + lootBonus) / 100

        for _ in range(numEnemies):
            enemies.append(createEnemy(enemyLevel, difficulty, rarity, quantity, self.player.className, self.player._name))

        return enemies

    def _monitorCombatResults(self, enemies):
        """returns True if combat ended, False if still going"""
        result = self.combatManager.checkBattleEnd()
        if result:
            result = "victory" if result == "player" else "defeat"
            self.postBattle(result, enemies)
            return False
        return True

    def startCombat(self, enemies: List[Enemy]):
        clearScreen()
        printHeader("Combat Start")

        enemyTable = createEnemyPreview(enemies)
        console.print(enemyTable)

        pause()

        self.combatManager.startBattle(self.player, enemies)

        if getattr(self.player, 'pendingSkeleton', None):
            self.player.currentSkeleton = self.player.pendingSkeleton
            self.player.skeletonTurns = 3
            self.player.pendingSkeleton = None
            console.print(f"[dark_red]Necromancer: {self.player.currentSkeleton._name} joins you for the start of this battle![/dark_red]")
            pause()

        while self.combatManager.battleActive:
            if self._monitorCombatResults(enemies):
            
                currentUnit = self.combatManager.getCurrentUnit()
                if not currentUnit:
                    break

                if currentUnit.team == "player":
                    self.playerTurn(enemies)
                else:
                    self.enemyTurn(currentUnit)

            else:
                break

        return ""

    def playerTurn(self, enemies: List[Enemy]):
        self.player.onTurnStart(self.combatManager)

        if not self._monitorCombatResults(enemies):
            return

        while True:
            clearScreen()
            printHeader(f"Your Turn: Round {self.combatManager.turnNumber}")
            createCombatStatusTable(self.player, enemies)

            aliveEnemies = [e for e in enemies if not e._isDead]

            console.print("\n[bold cyan]=== Actions ===[/bold cyan]\n")
            if self.player.consumable.useable:
                console.print(f"[dim]C.[/dim] [green]Use {self.player.consumable.name} to heal for {int(self.player.consumable.healPercent*100)}% Max HP.[/green] [bold](Free Action)[/bold]")
            console.print("[dim]F.[/dim] [yellow]Flee from Combat[/yellow]")
            console.print("[dim]D.[/dim] [dim red]View Enemy Details[/dim red]")
            console.print("[dim]P. Pass Turn[/dim]")
            if self.player.className == 'Druid':
                console.print(f"[dim]Current Form:[/dim] {self.player.form.title()}")
            console.print()

            if self.player._abilities:
                abilities = self.player._abilities
                abilityTables = createAbilityTables(abilities, self.player._damageType)
                console.print(abilityTables)
                console.print()

            availableAbilities = list(abilities.items())
            action = console.input("\n[cyan]Choose Action (number):[/cyan]\n> ").strip()

            if action.lower() == 'd':
                clearScreen()
                printHeader("Checking Enemy Data")
                for e in enemies:
                    console.print(e)
                    for slot, eq in e._equipment.items():
                        if eq is not None:
                            console.print(f"{slot}:\n{eq}")
                pause()
            elif action.lower() == 'c' and self.player.consumable.useable:
                self.player.useConsumable()
                continue
            elif action.lower() == 'f':
                console.print("[red]Fled from battle.[/red]")
                self.combatManager.battleActive = False
                self.player.onCombatEnd()
                return
            elif action.lower() == 'p':
                console.print("[dim red1]You skipped your turn...[/dim red1]")
                time.sleep(0.5)
            else:
                try:
                    abilityIndex = int(action) - 1
                    if 0 <= abilityIndex < len(availableAbilities):
                        abilityName, ability = availableAbilities[abilityIndex]

                        success, message = ability.canUse(self.player)
                        if not success:
                            printWarning(message)
                            pause()
                            continue

                        if ability.targets in ["all", "multiple"]:
                            target = aliveEnemies[0]
                            console.print(f"\n[buff]{abilityName} will hit {'ALL enemies' if ability.targets == 'all' else 'MULTIPLE enemies'}[/buff]")
                        else:
                            if ability.category == 'damage':
                                target = self.chooseTarget(aliveEnemies)
                            else:
                                target = [self.player]

                        if target:
                            self.combatManager.performAttack(self.player, target, abilityName)
                            self.combatManager.resolveSkeletonAttack(self.player)
                            break
                    else:
                        printError(f"Invalid choice: {action}")
                except ValueError as e:
                    printError(f"{e}")
        pause()
        self.combatManager.nextTurn()

    def chooseTarget(self, enemies: List[Enemy]) -> Optional[Enemy]:
        for enemy in enemies:
            if getattr(enemy, 'taunting', False):
                return enemy

        if len(enemies) == 1:
            return enemies[0]
        
        while True:
            target = console.input("[cyan]Choose target (number):[/cyan]\n> ").strip()
            try:
                index = int(target) - 1
                if 0 <= index < len(enemies):
                    return enemies[index]
                else:
                    printError(f"Invalid target: #{int(target) + 1}")
            except ValueError as e:
                printError(f"{e}")

    def enemyTurn(self, currentUnit):
        enemy = currentUnit.entity

        clearScreen()
        printHeader(f"{enemy._name}'s Turn")

        player = [self.player] if not self.player._isDead else []

        if player:
            self.combatManager.enemyTurn(enemy, player)

        pause()
        self.combatManager.nextTurn()

    def victory(self, enemies: List[Enemy], waveEncounter: bool = False, lootBonus: int = 0):
        clearScreen()
        displayVictory()

        totalXp = 0
        totalGold = 0
        allLoot = {}
        allEquipment = []
        allRunes = []

        blueprints = 0
        fuel = 0
        supplies = 0
        tradeVouchers = 0

        if self.camp.forge.level >= 1:
            fuel = random.randint(1, 4 + self.camp.forge.level)
            blueprints = random.randint(1, 2 + self.camp.forge.level)
        if self.camp.campfire.level >= 1:
            supplies = random.randint(2, 5 + self.camp.campfire.level)
        if self.camp.market.level >= 1:
            tradeVouchers = random.randint(0, 2 + (self.camp.market.level // 2))

        for enemy in enemies:
            totalXp += enemy.getExperienceReward()
            totalGold += max(5, enemy._level // 2) * random.randint(2, 5)

            resources, equipmentPool, runes = enemy.dropLoot()
            
            for resource, (minAmt, maxAmt, dropChance) in resources.items():
                minAmt = int(minAmt)
                maxAmt = int(maxAmt)
                if random.random() <= dropChance:
                    amount = random.randint(minAmt, maxAmt)
                    allLoot[resource] = allLoot.get(resource, 0) + amount

            for equipment, dropChance in equipmentPool:
                if random.random() <= dropChance:
                    allEquipment.append(equipment)

            for category, runeType in runes:
                allRunes.append((category, runeType))

        if waveEncounter:
            bonusRuneCap = (self.player._level // 20) + (self.areaLevel // 15)
            bonusRuneCount = random.randint(3, max(4, min(10, bonusRuneCap)))
            allRunes.extend(rollGuaranteedRunes(self.player._level, bonusRuneCount))

        xpBonus = self.player._stats['Bonuses']['xp_gain'] + lootBonus
        if xpBonus > 0:
            effectiveBonus = xpBonus / (1 + (xpBonus / 100))
            xpModifier = effectiveBonus / 100
        else:
            xpModifier = xpBonus / 100
        goldBonus = self.player._stats['Bonuses']['gold_gain'] + lootBonus

        if xpBonus > 0:
            bonusXp = round(totalXp * xpModifier)
            totalXp += bonusXp
            console.print(f"[buff]XP Bonus: +{bonusXp} (+{xpBonus}%)[/buff]")
        if goldBonus > 0:
            bonusGold = round(totalGold * (goldBonus / 100))
            totalGold += bonusGold
            console.print(f"[buff]Gold Bonus: +{bonusGold} (+{goldBonus}%)[/buff]")

        console.print("\n[gold1 bold]=== Rewards ===[/gold1 bold]")
        self.player.gainExperience(totalXp)
        self.player.gainGold(totalGold)

        if supplies > 0:
            self.camp.campfire.supplies += supplies
            console.print(f"  [green]- Campfire Supplies: +{supplies}[/green]")
        if blueprints > 0:
            self.camp.forge.blueprints += blueprints
            console.print(f"  [cyan]- Blueprints: +{blueprints}[/cyan]")
        if fuel > 0:
            self.camp.forge.fuel += fuel
            console.print(f"  [yellow]- Forge Fuel: +{fuel}[/yellow]")
        if tradeVouchers > 0:
            self.camp.market.tradeVouchers += tradeVouchers
            console.print(f"  [magenta]- Trade Vouchers: +{tradeVouchers}[/magenta]")

        if allLoot:
            console.print("\n[cyan bold]=== Resources Accquired ===[/cyan bold]")
            for item, quantity in allLoot.items():
                self.player.addItem(item, quantity)

        if allEquipment:
            console.print("\n[cyan bold]=== Equipment Found ===[/cyan bold]")
            for equipment in allEquipment:
                console.print(equipment)

                if equipment.slot in self.player._equipment:
                    current = self.player._equipment[equipment.slot]
                    if current:
                        console.print(f"{equipment.compareTo(current)}")

                if equipment.slot in self.player._equipment:
                    choice = console.input(f"\n    [cyan]Equip {equipment.name}? (y/n/s to store):[/cyan] [dim](default = store)[/dim]\n> ").strip().lower()
                    if choice == 'n':
                        continue
                    elif choice == 'y':
                        if not self.player.equip(equipment):
                            self.player.addEquipmentToStorage(equipment)
                    else:
                        self.player.addEquipmentToStorage(equipment)
                else:
                    self.player.addEquipmentToStorage(equipment)

        if allRunes:
            console.print(f"\n[cyan bold]=== Runes ===[/cyan bold]")
            for cat, rtype in allRunes:
                self.player.addRune(cat, rtype, 1)

        self.camp.campfire.applyHeal()

def main():
    try:
        try:
            ensureServerRunning()
        except Exception:
            pass
        subprocess.Popen([ # create a korus watcher to silently track save file changes
            r"tools\korus_watch.exe",
            "data/saves",
            "--log", "data/watch/save_watch.log",
            "--interval", "10", "--silent"
        ])

        game = Game()
        game.titleScreen()
    except KeyboardInterrupt:
        printError("\n\nGame interrupted by user.")
        if game and game.player:
            response = console.input("[cyan]Would you like to save before exiting? (y/n):[/cyan]\n> ").strip().lower()
            if response == "y":
                saveNum = console.input("[cyan]Enter save slot number:[/cyan]\n> ").strip()
                save(game, saveNum)
    except Exception as e:
        console.print("\n" + "="*70)
        printError("CRITICAL ERROR - The game has crashed!")
        console.print("="*70)
        printError(f"\nError: {type(e).__name__}: {e}")
        saveConfirm = console.input("\n[cyan]Save crash log data? (y/n):[/cyan]\n> ").strip().lower()

        if saveConfirm == 'y':
            logPath, jsonPath = logCrash(e, game)

            printInfo(f"\nCrash details saved to:")
            printInfo(f"  - {logPath}")
            printInfo(f"  - {jsonPath}")
            
        if game and hasattr(game, 'player') and game.player:
            saveCrash = console.input("[green]Would you like to save your file before the game exits? (Y/N)[/green]\n[cyan]> [/cyan]").lower().strip()
            if saveCrash == 'y':
                printInfo("\nYour game state has been saved and can be recovered/loaded at any time. The crash save is save file 999")
                save(game, 999)
        pause()
        raise

if __name__ == "__main__":
    main()

...