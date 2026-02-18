from typing import Dict, List
from json import load
from .station import Station
from scripts.styles import (
    console, clearScreen, printHeader, printSeparator,
    pause, printWarning, printError, printSuccess
)

class Quest:
    def __init__(self, name, data):
        self.name = name
        self.tier = data['tier']
        self.task = data['task']
        self.amount = data['amount']
        self.rewards = data['rewards']
        self.description = data['description']

    def __str__(self):
        return f"  - {self.name}:\n    - {self.description}"

def _generateQuests() -> Dict[str, Quest]:
    with open("Korus/data/quests.json", 'r') as file:
        quests = load(file)
    qDict = {}
    for quest in quests:
        data = quests[quest]
        obj = Quest(quest, data)
        qDict[quest] = obj
    return qDict

QUESTS = _generateQuests()

class QuestBoard(Station):
    # recieve quests
    # higher levels: harder quests, better rewards
    def __init__(self, player):
        super().__init__(player, "Quest Board")
        self.activeQuests: Dict[str, Quest] = {} # {'quest name': {'progress': int}}
        self.completedQuests: List[str] = []

    def _getUpgradeRequirements(self) -> Dict[int, Dict[str, int]]:
        return {
            1: {"wood": 30, "stone": 30},
            2: {"wood": 75, "iron_ore": 40},
            3: {"crystal": 20, "soul": 10},
            4: {"mana_essence": 30, "diamond": 15},
            5: {"dragon_scale": 10, "ascended_essence": 5}
        }
    
    def _serialise(self):
        temp = super()._serialise()
        temp['activeQuests'] = self.activeQuests
        temp['completedQuests'] = self.completedQuests
        return temp

    def getMaxQuests(self) -> int:
        return min(2 + self.level, max(1, self.player._level // 5))
    
    def mainMenu(self):
        while True:
            clearScreen()
            printHeader(f"Quest Board - Level {self.level}")
            console.print(f"[info]Active Quests:[/info] {len(self.activeQuests)}/{self.getMaxQuests()}")
            console.print(f"[success]Completed:[/success] {len(self.completedQuests)}")
            printSeparator()
            console.print("[dim]0.[/dim] Return")
            console.print("[dim]1.[/dim] View Active Quests")
            console.print("[dim]2.[/dim] Accept New Quest")
            console.print("[dim]3.[/dim] Abandon Quest")
            console.print("[dim]4.[/dim] Turn In Completed Quests")
            console.print("[dim]9.[/dim] Upgrade Quest Board")
            
            choice = console.input("\n[cyan]>[/cyan] ").strip()
            try:
                choice = int(choice)
                match choice:
                    case 0:
                        break
                    case 1:
                        self.displayQuests()
                        pause()
                    case 2:
                        self.acceptQuest()
                    case 3:
                        self.abandonQuest()
                    case 4:
                        self.turnInQuests()
                    case 9:
                        self.upgrade()
                    case _:
                        printWarning("Invalid choice!")
                        pause()
            except ValueError:
                printError("Invalid input!")
                pause()

    def displayQuests(self):
        clearScreen()
        printHeader("Active Quests")
        if not len(self.quests):
            printWarning("No active quests!")
            return
        console.print(" === [bold gold]Quests:[/bold gold] ===")
        for questName, progressData in self.activeQuests.items():
            if questName in QUESTS:
                quest = QUESTS[questName]
                current = progressData['progress']
                needed = quest.amount
                percentage = (current / needed) / 100

                console.print(f"\n[bold]{questName} [Tier {quest.tier}][/bold]")
                console.print(f"  [dim]{quest.description}[/dim]")
                console.print(f"  [white]Progress: {current} / {needed} ({percentage:.1f}%)[/white]")
                if 'xp' in quest.rewards:
                    console.print(f"    - [yellow]{quest.rewards['xp']} XP[/yellow]")
                if 'gold' in quest.rewards:
                    console.print(f"    - [gold]{quest.rewards['gold']} Gold[/gold]")
                if 'items' in quest.rewards:
                    for item, qty in quest.rewards['items'].items():
                        console.print(f"    - [white]{qty}x {item}[/white]")

                if current >= needed:
                    printSuccess("  {COMPLETE!}")

    def acceptQuest(self):
        if len(self.activeQuests) >= self.getMaxQuests():
            printWarning(f"\nQuest limit reached!")
            pause()
            return
        
        clearScreen()
        printHeader("Accept Quest")
        available = []
        for questName, quest in QUESTS.items():
            if (questName not in self.completedQuests and
                questName not in self.activeQuests and
                quest.tier <= self.level):
                available.append((questName, quest))

        if not available:
            printWarning("No quests available!")
            pause()
            return
        
        console.print("\n[bold]nAvailable Quests:[/bold]")
        for i, (questName, quest) in enumerate(available, 1):
            console.print(f"\n[cyan]{i}.[/cyan] [white]{questName} [Tier {quest.tier}][/white]")
            console.print(f"   [dim]{quest.description}[/dim]")
            console.print(f"   [tan]Rewards: [/tan]", end="")
            rewardParts = []
            if 'xp' in quest.rewards:
                rewardParts.append(f"{quest.rewards['xp']} XP")
            if 'gold' in quest.rewards:
                rewardParts.append(f"{quest.rewards['gold']}g")
            if 'items' in quest.rewards:
                for item, qty in quest.rewards['items'].items():
                    rewardParts.append(f"{qty}x {item}")
            console.print(", ".join(rewardParts))

        choice = console.input("\n[cyan]Choose quest to accept (0 to cancel):\n> [/cyan]").strip()
        try:
            index = int(choice) - 1
            if 0 <= index < len(available):
                questName, quest = available[index]
                self.activeQuests[questName] = {'progress': 0}
                printSuccess(f"\nAccepted quest: {quest.name}")
        except ValueError:
            pass
        pause()

    def abandonQuest(self):
        if not self.activeQuests:
            printWarning("\nNo active quests!")
            pause()
            return
        
        clearScreen()
        printHeader("ABANDON QUEST")
        
        console.print("\n[bold]Active Quests:[/bold]")
        questList = list(self.activeQuests.keys())
        for i, questName in enumerate(questList, 1):
            console.print(f"  [cyan]{i}.[/cyan] [white]{questName}[/white]")
        
        choice = console.input("\n[cyan]Choose quest to abandon (0 to cancel):\n> [/cyan]").strip()
        try:
            index = int(choice) - 1
            if 0 <= index < len(questList):
                questName = questList[index]
                confirm = console.input(f"\n[bold]Abandon {questName}? (y/n):[/bold]\n[cyan]> [/cyan]").strip().lower()
                if confirm == 'y':
                    del self.activeQuests[questName]
                    printSuccess(f"\nAbandoned {questName}")
        except ValueError:
            pass
        pause()

    def updateQuestProgress(self, task: str, amount: int = 1):
        for questName, progressData in self.activeQuests.items():
            if questName in QUESTS:
                quest = QUESTS[questName]
                if quest.task == task:
                    progressData['progress'] = min(
                        progressData["progress"] + amount,
                        quest.amount
                    )
    
    def turnInQuests(self):
        completed = []
        for questName, progressData in self.activeQuests.items():
            if questName in QUESTS:
                quest = QUESTS[questName]
                if progressData['progress'] >= quest.amount:
                    completed.append(questName)

        if not completed:
            printWarning("\nNo quests ready to turn in!")
            pause()
            return
        
        clearScreen()
        printHeader("Turn in quests")

        totalXp = 0
        totalGold = 0
        allItems = {}

        for questName in completed:
            quest = QUESTS[questName]
            console.print(f"\n[gold]Completed: {quest.name}[/gold]")
            if 'xp' in quest.rewards:
                totalXp += quest.rewards['xp']
            if 'gold' in quest.rewards:
                totalGold += quest.rewards['gold']
            if 'items' in quest.rewards:
                for item, qty in quest.rewards['items'].items():
                    allItems[item] = allItems.get(item, 0) + qty
            
            # move to completed
            del self.activeQuests[questName]
            self.completedQuests.append(questName)

        # give rewards
        printSeparator()
        console.print(" === [bold]Rewards:[/bold] ===")
        if totalXp > 0:
            self.player.gainExperience(totalXp)
        if totalGold > 0:
            self.player.gainGold(totalGold)
        if allItems:
            console.print(f"  [white]Items:[/white]")
            for item, amount in allItems.items():
                console.print(f"    - [dim]{amount}x {item}[/dim]")
                self.player.addItem(item, amount)
        pause()
