from scripts.entities import Entity, ELEMENTAL_RES, DIVINE_RES, OTHERWORLD_RES
from scripts.styles import (
    console, displayLevelUp, formatDamageType, pause,
    printSuccess, printWarning, printInfo, clearScreen
)
import random
from typing import Dict
from scripts.abilities import Ability, CLASS_ABILITIES
from copy import deepcopy

class Player(Entity):
    def __init__(self, name: str, health: int = 50, damage: int = 5, baseCritChance: float = 0.05, baseCritMulti: float = 1.5, damageType: str = "physical", speed: float = 1.0, /,
                 *, className: str = None, classDescription: str = "Basic Player", ascendancy = None, ascendancyDescription: str = None):
        super().__init__(health, damage, baseCritChance, baseCritMulti, damageType, speed, name, className)
        self.defaultDamageType = damageType
        self.classDescription = classDescription
        self._ascendancy = ascendancy
        self.ascendancyDescription = ascendancyDescription
        self.dungeonKeys = {}
        self._maxLevel = 100
        self.gainClassAbilities()

        self.consumableUsed = False

    def serialise(self):
        temp = super().serialise()
        temp['maxLevel'] = self._maxLevel
        return temp

    def deserialise(self, data):
        super().deserialise(data)
        self._maxLevel = data.get('maxLevel', 100)
        self.gainClassAbilities()

    def death(self):
        console.print("\n[bold red]" + "="*25 + "[/bold red]")
        console.print("[bold red]YOU HAVE DIED[/bold red]")
        console.print("[bold red]" + "="*25 + "[/bold red]\n")
        return True
    
    def __rich__(self):
        return self.__str__()

    def __str__(self):
        return f"[health]HP:[/health] {self._health} / {self._maxHealth}\n[damage]Damage:[/damage] {self._damage} [dim]({formatDamageType(self._damageType, self._damageType)})[/dim] | [speed]Speed:[/speed] {self._speed}\n[xp]XP:[/xp] {self._xp} / {self._xpToNextLevel}"

    def __repr__(self):
        return f"[bold cyan]Player:[/bold cyan] {self._name} | [dim]Class = {self.className}. Description = {self.classDescription}[/dim]\n{self.__str__()}\n[damage]Damage:[/damage] {self._damage} [dim]({formatDamageType(self._damageType, self._damageType)})[/dim] | [speed]Speed:[/speed] {self._speed:.2f}"

    def gainExperience(self, amount: int):
        self._xp += amount
        console.print(f"[xp]Gained {amount} XP.[/xp] [dim]Total XP: {self._xp} / {self._xpToNextLevel}[/dim]")

        while self._xp >= self._xpToNextLevel:
            if self._level >= self._maxLevel:
                break
            self._levelUp()
            pause()

    def _levelUp(self):
        if self._level < self._maxLevel:
            self._xp -= self._xpToNextLevel
            self._level += 1
            self.calcXpRequirement()
            self.gainClassAbilities()

            self._baseHealth += 5
            self._baseDamage += 1
            self._baseSpeed += 0.01
            self._baseStamina += 4

            if self._level == self._maxLevel:
                console.print("[gold1]Congratulations! You have reached the maximum level![/gold1]")
            self._recalculateStats()
            displayLevelUp(self)
            pause()

    def gainClassAbilities(self):
        if not self.className or self.className not in CLASS_ABILITIES:
            return
        
        classAbilities = CLASS_ABILITIES[self.className]['base']

        for name, ability in classAbilities.items():
            if self._level >= ability.levelReq and name not in self._abilities:
                self._abilities[name] = deepcopy(ability)
                console.print(f"\n[bold]{'='*50}[/bold]")
                console.print(f"[gold1]🌟 CLASS ABILITY LEARNED: {name} 🌟[/gold1]")
                console.print(f"[bold]{'='*50}[/bold]")
                damageTypeFormatted = formatDamageType(ability.damageType, ability.damageType)
                console.print(f"[cyan]Damage:[/cyan] {ability.damage} ({damageTypeFormatted})")
                console.print(f"[cyan]Cooldown:[/cyan] {ability.maxCooldown} turns")
                if ability._mechanics:
                    console.print(f"[buff]Effects: {', '.join(ability._mechanics)}[/buff]")
                console.print(f"[bold]{'='*50}[/bold]\n")
                pause()

    def _recalculateStats(self, doPrint: bool = True, inCombat: bool = False):
        super()._recalculateStats(doPrint, inCombat)
        if not self._equipment['weapon']:
            self._damageType = self.defaultDamageType

    def _removeOldAscendancy(self):
        """rewrite per class"""
        pass

    def updateAscendancy(self, ascendancy):
        """ascendancy should be .title() version"""
        pass

