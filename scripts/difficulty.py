from enum import Enum

class Difficulty(Enum):
    EASY = "easy"
    NORMAL = "normal"
    HARD = "hard"
    HELL = "hell"

    def getMultiplier(self):
        multipliers = {
            Difficulty.EASY: 0.75,
            Difficulty.NORMAL: 1.0,
            Difficulty.HARD: 1.5,
            Difficulty.HELL: 2.0
        }
        return multipliers[self]
    
    def getDisplayName(self):
        colours = {
            Difficulty.EASY: "green",
            Difficulty.NORMAL: "cyan",
            Difficulty.HARD: "orange1",
            Difficulty.HELL: "red"
        }
        return f"[{colours[self]}]{self.value.capitalize()}[/{colours[self]}]"
    
    def getDescription(self):
        descriptions = {
            Difficulty.EASY: "Enemies have 75% stats. Perfect for learning the game.",
            Difficulty.NORMAL: "Standard difficulty. Balanced challenge.",
            Difficulty.HARD: "Enemies have 150% stats. For experienced players.",
            Difficulty.HELL: "Enemies have 200% stats. Brutal challenge for veterans."
        }
        return descriptions[self]
    
...