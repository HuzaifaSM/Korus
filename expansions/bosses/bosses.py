import random
from typing import Dict, Any, Optional, List
from scripts.abilities import ABILITIES, Ability
from scripts.enemy import Enemy
from scripts.styles import console

class Boss(Enemy):
    def __init__(self, name: str, level: int = 1, health: int = 100, damage: int = 10, 
                 critChance: float = 0.08, critMulti: float = 1.8, damageType: str = "physical",
                 speed: float = 1.0, lootTable = None):
        super().__init__(name, level, health, damage, critChance, critMulti, damageType, speed, lootTable)

        self.phases = []
        self.currentPhase = 0
        self.abilityWeights = {}
        self.turnCount = 0

        self.playerWeaknesses = {}
        self.lastEffectiveAbility = None
        self.damageTypeEffectiveness = {}

        self.enraged = False
        self.desperation = False

        self.phaseTransitionMessage = None

    def setupPhases(self, phases: List[Dict]):
        self.phases = sorted(phases, key=lambda x: x['threshold'], reverse=True)
    
    def checkPhaseTransition(self) -> Optional[str]:
        hpPercent = self._health / self._maxHealth
        
        for i, phase in enumerate(self.phases):
            if i > self.currentPhase and hpPercent <= phase['threshold']:
                self.triggerPhase(i, phase)
                return self.triggerPhase(i, phase)
        return None
    
    def triggerPhase(self, phaseNum: int, phaseData: Dict) -> str:
        self.currentPhase = phaseNum

        if 'abilities' in phaseData:
            for name, data in phaseData['abilities'].items():
                self.specialAbilities[name] = data

        if 'effects' in phaseData:
            for effect, value in phaseData['effects'].items():
                if effect == 'enrage':
                    self.enraged = True
                    self._baseDamage = round(self._baseDamage * 1.5)
                    console.print(f"  [bold red]>>> {self._name} becomes ENRAGED![/bold red]")
                    self._recalculateStats(False)
                elif effect == 'desperation':
                    self.desperation = True
                    self._baseSpeed += 0.2
                    self._baseDamage = round(self._baseDamage * 1.2)
                    console.print(f"  [bold red]>>> {self._name} enters desperation phase![/bold red]")
                    self._recalculateStats(False)

        return phaseData.get('message', f"{self._name} enters a new phase!")
    
    def analysePlayer(self, player):
        weaknesses = {}

        for res, amount in player._stats['resitances'].items():
            score = max(0, 75 - amount)
            if score > 0:
                weaknesses[res] = score

        self.playerWeaknesses = weaknesses
        return weaknesses
    
    def calculateAbilityWeights(self, player):
        weights = {}

        for name, ability in self.specialAbilities.items():
            weight = ability.get('rollWeight', 10)

            if ability.cooldown > 0:
                weights[name] = 0
                continue

            damageType = ability.damageType