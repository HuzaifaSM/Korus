from enum import Enum

class Difficulty(Enum):
    EASY = "easy"
    NORMAL = "normal"
    HARD = "hard"
    NIGHTMARE = "nightmare"
    HELL = "hell"

    def getMultiplier(self):
        multipliers = {
            Difficulty.EASY: 0.75,
            Difficulty.NORMAL: 1.0,
            Difficulty.HARD: 1.3,
            Difficulty.NIGHTMARE: 1.65,
            Difficulty.HELL: 2.0
        }
        return multipliers[self]

    def getAiDifficultyBonus(self) -> float:
        """flat add to enemy aiDifficulty (0.0-1.0 scale), clamped by the caller"""
        bonuses = {
            Difficulty.EASY: -0.15,
            Difficulty.NORMAL: 0.0,
            Difficulty.HARD: 0.10,
            Difficulty.NIGHTMARE: 0.20,
            Difficulty.HELL: 0.30
        }
        return bonuses[self]

    def getAggressionCautiousBonus(self) -> float:
        """flat add to enemy aggression and cautious rolls, clamped by the caller"""
        bonuses = {
            Difficulty.EASY: -0.05,
            Difficulty.NORMAL: 0.0,
            Difficulty.HARD: 0.05,
            Difficulty.NIGHTMARE: 0.10,
            Difficulty.HELL: 0.15
        }
        return bonuses[self]

    def getEnemyRarityShiftBonus(self) -> float:
        """extra shift added on top of the level-based enemy rarity curve"""
        bonuses = {
            Difficulty.EASY: -0.10,
            Difficulty.NORMAL: 0.0,
            Difficulty.HARD: 0.08,
            Difficulty.NIGHTMARE: 0.15,
            Difficulty.HELL: 0.25
        }
        return bonuses[self]

    def getSupportBiasDelta(self) -> int:
        """shift toward (positive) or away from (negative) support-heavy encounters"""
        deltas = {
            Difficulty.EASY: -1,
            Difficulty.NORMAL: 0,
            Difficulty.HARD: 0,
            Difficulty.NIGHTMARE: 1,
            Difficulty.HELL: 1
        }
        return deltas[self]

    def getLootRarityBonus(self) -> float:
        """flat % added directly to the player's item_rarity Bonus"""
        bonuses = {
            Difficulty.EASY: -10,
            Difficulty.NORMAL: 0,
            Difficulty.HARD: 10,
            Difficulty.NIGHTMARE: 20,
            Difficulty.HELL: 35
        }
        return bonuses[self]

    def getLootQuantityBonus(self) -> float:
        """flat % added directly to the player's item_quantity Bonus"""
        bonuses = {
            Difficulty.EASY: 10,
            Difficulty.NORMAL: 0,
            Difficulty.HARD: 5,
            Difficulty.NIGHTMARE: 10,
            Difficulty.HELL: 15
        }
        return bonuses[self]

    def getEnemyQuantityBonus(self) -> float:
        """flat % added directly to the player's enemy_quantity Bonus"""
        bonuses = {
            Difficulty.EASY: -15,
            Difficulty.NORMAL: 0,
            Difficulty.HARD: 10,
            Difficulty.NIGHTMARE: 20,
            Difficulty.HELL: 30
        }
        return bonuses[self]

    def getRuneQualityBiasExponent(self) -> float:
        """exponent applied to (100 / dropWeight) when weighting rune drops - positive skews rarer"""
        exponents = {
            Difficulty.EASY: -0.2,
            Difficulty.NORMAL: 0.0,
            Difficulty.HARD: 0.15,
            Difficulty.NIGHTMARE: 0.3,
            Difficulty.HELL: 0.5
        }
        return exponents[self]

    def getEntropyMultiplier(self) -> float:
        """scales positive entropy gained from crafting"""
        multipliers = {
            Difficulty.EASY: 0.7,
            Difficulty.NORMAL: 1.0,
            Difficulty.HARD: 1.15,
            Difficulty.NIGHTMARE: 1.3,
            Difficulty.HELL: 1.5
        }
        return multipliers[self]

    def getEconomyMultiplier(self) -> float:
        """scales market prices and forge repair costs"""
        multipliers = {
            Difficulty.EASY: 0.75,
            Difficulty.NORMAL: 1.0,
            Difficulty.HARD: 1.15,
            Difficulty.NIGHTMARE: 1.3,
            Difficulty.HELL: 1.5
        }
        return multipliers[self]

    def getRewardMultiplier(self) -> float:
        """bonus fraction added to enemy gold/XP rewards"""
        multipliers = {
            Difficulty.EASY: -0.15,
            Difficulty.NORMAL: 0.0,
            Difficulty.HARD: 0.15,
            Difficulty.NIGHTMARE: 0.30,
            Difficulty.HELL: 0.50
        }
        return multipliers[self]

    def getDisplayName(self):
        colours = {
            Difficulty.EASY: "green",
            Difficulty.NORMAL: "cyan",
            Difficulty.HARD: "orange1",
            Difficulty.NIGHTMARE: "magenta",
            Difficulty.HELL: "red"
        }
        return f"[{colours[self]}]{self.value.capitalize()}[/{colours[self]}]"

    def getDescription(self):
        descriptions = {
            Difficulty.EASY: "Weaker, more predictable enemies in smaller numbers. Loot leans toward quantity over rarity, crafting is more forgiving, and prices are cheaper. Perfect for learning the game.",
            Difficulty.NORMAL: "Standard difficulty. Balanced challenge, loot, and prices.",
            Difficulty.HARD: "Sharper, more aggressive enemies in tougher numbers. Better loot rarity and rune quality, at the cost of riskier crafting and pricier upkeep. For experienced players.",
            Difficulty.NIGHTMARE: "Noticeably smarter and more dangerous enemies, favouring tougher support-heavy encounters. Significantly better rewards and rarer drops, but crafting and the market both punish mistakes harder.",
            Difficulty.HELL: "Enemies play close to optimally and hit hard in large, dangerous groups. The best loot, rune quality, and rewards in the game - matched by the highest crafting risk and steepest prices. Brutal challenge for veterans."
        }
        return descriptions[self]


_activeDifficulty: Difficulty = Difficulty.NORMAL

def setActiveDifficulty(difficulty: Difficulty):
    global _activeDifficulty
    _activeDifficulty = difficulty

def getActiveDifficulty() -> Difficulty:
    return _activeDifficulty
