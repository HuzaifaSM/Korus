import random
from typing import List, Dict
from scripts.enemy import createEnemy

from scripts.styles import console, printSuccess, printWarning, pause, clearScreen, printSeparator
from scripts.items.items import ItemRarity, DungeonMap

class DungeonModifier:
    def __init__(self, name: str, modType: str, value: float, description: str):
        self.name = name
        self.modType = modType #positive or negativex
        self.value = value
        self.description = description

    def apply(self, entity=None, lootMultiplier=None):
        if self.modType == 'positive':
            if 'rarity' in self.name.lower():
                return {'rarityBonus': self.value}
            elif 'quantity' in self.name.lower():
                return {'quantityBonus': self.value}
            elif 'experience' in self.name.lower():
                return {'xpBonus': self.value}
            elif 'gold' in self.name.lower():
                return {'goldBonus': self.value}
            elif 'abundant' in self.name.lower():
                return {'rarityBonus': self.value, 'quantityBonus': self.value}
        else: #negative
            if entity:
                if 'damage' in self.name.lower():
                    entity._baseDamage = int(entity._baseDamage * (1 + self.value))
                elif 'health' in self.name.lower():
                    entity._baseHealth = int(entity._baseHealth * (1 + self.value))
                elif 'speed' in self.name.lower():
                    entity._baseSpeed *= (1 + self.value)
                elif 'relentless' in self.name.lower():
                    entity._baseDamage = int(entity._baseDamage * (1 + self.value))
                    entity._baseHealth = int(entity._baseHealth * (1 + self.value))
                    entity._baseSpeed *= (1 + self.value)
                entity._recalculateStats(False)
        return {}

POSITIVE_MODIFIERS = [
    DungeonModifier("Bountiful", "positive", 0.5, "+50% Item Quantity"),
    DungeonModifier("Fortunate", "positive", 0.3, "+30% Item Rarity"),
    DungeonModifier("Enlightening", "positive", 0.5, "+50% Experience Gained"),
    DungeonModifier("Wealthy", "positive", 0.75, "+75% Gold Dropped"),
    DungeonModifier("Abundant", "positive", 0.25, "+25% Item Quantity & Rarity"),
]

NEGATIVE_MODIFIERS = [
    DungeonModifier("Brutal", "negative", 0.30, "Enemies deal 30% more damage"),
    DungeonModifier("Fortified", "negative", 0.40, "Enemies have 40% more health"),
    DungeonModifier("Swift", "negative", 0.25, "Enemies have 25% more speed"),
    DungeonModifier("Overwhelming", "negative", 0.20, "Enemies have 20% more damage & health"),
    DungeonModifier("Relentless", "negative", 0.15, "Enemies have 15% more all stats"),
]


class Dungeon:
    def __init__(self, dungeonMap: DungeonMap):
        """No upper tier"""
        self.name = dungeonMap.name
        self.level = dungeonMap.level
        self.waves = dungeonMap.waves
        self.tier = dungeonMap.tier
        self.rarity = dungeonMap.rarity
        self.description = dungeonMap.description

        baseDifficulty = 0.9 + (0.1 * self.tier)
        self.difficulty = baseDifficulty * dungeonMap.getDifficultyMultiplier()
        self.rewardMultipler = dungeonMap.getRewardMultiplier()

        self.modifiers: List[DungeonModifier] = []
        self._generateModifiers()

    def _generateModifiers(self):
        numPositive = random.randint(1, min(3, 1 + self.tier // 4))
        numNegative = random.randint(1, min(3, 1 + self.tier // 4))

        self.modifiers.extend(
            random.sample(POSITIVE_MODIFIERS, numPositive)
        )
        self.modifiers.extend(
            random.sample(NEGATIVE_MODIFIERS, numNegative)
        )
        self._calculateModifiers()

    def _calculateModifiers(self):
        self.rarity = 0
        self.quantity = 0
        self.xp = 0
        self.gold = 0
        for mod in self.modifiers:
            if mod.modType == 'positive':
                bonus = mod.apply()
                for k, v in bonus.items():
                    if k == 'rarity':
                        self.rarity += v
                    elif k == 'quantity':
                        self.quantity += v
                    elif k == 'xp':
                        self.xp += v
                    elif k == 'gold':
                        self.gold += v

    def displayInfo(self):
        printSeparator()
        console.print(f"[bold gold1]DUNGEON: {self.name}[/bold gold1]")
        printSeparator()
        console.print(f"[cyan]Level:[/cyan] {self.level} | [cyan]Waves:[/cyan] {self.waves} | [cyan]Tier:[/cyan] {self.tier}")
        console.print(f"\n[gold1]Modifiers:[/gold1]")

        for mod in self.modifiers:
            colour = 'success' if mod.modType == 'positive' else 'warning'
            console.print(f"    [{colour}]- {mod.description}[/{colour}]")

        printSeparator()
        
    def run(self, game):
        clearScreen()
        self.displayInfo()

        printWarning('!!! No Healing between Waves !!!')
        confirm = console.input("[cyan]Enter this dungeon?[/cyan] [dim](y/N)[/dim]\n> ")

        if confirm != 'y':
            printWarning('Dungeon Cancelled')
            pause()
            return False
        
        startingHP = game.player._health

        for wave in range(1, self.waves + 1):
            clearScreen()
            printSeparator()
            console.print(f"[bold cyan]WAVE {wave}/{self.waves}[/bold cyan]")
            printSeparator()

            numEnemies = random.randint(1, 3 + wave // 2 + self.tier // 5)
            enemies = []

            for _ in range(numEnemies):
                enemy = createEnemy(self.level, difficulty=self.difficulty,
                                    rarity=self.rarity, quantity=self.quantity)

                for mod in self.modifiers:
                    if mod.modType == 'negative':
                        mod.apply(entity=enemy)
                
                enemies.append(enemy)

            outcome = game.startCombat(enemies)

            if outcome != 'victory':
                console.print('[bold red]DUNGEON FAILED[/bold red]')
                console.print(f'[dim]You made it to Wave {wave}/{self.waves}[/dim]')
                pause()
                return False
            
            elif outcome == 'victory':
                game.victory(enemies)

            if wave < self.waves:
                console.print(f"[cyan]Wave {wave} complete! Wave {wave+1} is now beginning...[/cyan]")
                console.print(f"[red]HP: {game.player_health} / {game.player._maxHealth}[/red]")
                pause()

        clearScreen() # dungeon complete
        printSeparator()
        console.print("[bold success]Dungeon Complete![/bold success]")

        survivalBonus = int((game.player._health / game.player._maxHealth) * 100)
        printSuccess(f"Survival: {survivalBonus}% HP remaining.")
        printSuccess(f"Waves cleared: {self.waves}")

        pause()
        return True

FIRST_NAMES = [
    'Cursed', 'Forgotten', 'Twisted', 'Corrupted', 'Abyssal',
    'Forsaken', 'Voiden', 'Shattered', 'Dark', 'Winding',
    'Tormenting', 'Lifeless', 'Malicious', 'Vile', 'Ominous'
]

SECOND_NAMES = [
    'Catacombs', 'Temple', 'Depths', 'Ruins', 'Sanctuary',
    'Shrine', 'Chambers', 'Halls', 'Monastery', 'Halls',
    'Manor', 'Estate', 'Crpyt', 'Ghetto', 'Maze'
]

def generateDungeonMap(enemyLevel: int) -> Dict:
    dropChance = 0.02 + (enemyLevel / 1000)

    if random.random() < dropChance:
        tier = max(1, (enemyLevel // 10) + random.randint(-1, 2))
        level = enemyLevel + random.randint(-5, 10)
        waves = random.randint(2, 4 + tier)

        name = f"{random.choice(FIRST_NAMES)} {random.choice(SECOND_NAMES)}"

        return DungeonMap(
            name=name,
            level=level,
            tier=tier,
            waves=waves,
            description=f"Level {level} | {waves} Waves | Tier {tier}",
        )
    
    return None

