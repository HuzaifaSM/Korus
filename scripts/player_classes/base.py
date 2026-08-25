from scripts.entities import Entity, ELEMENTAL_RES, DIVINE_RES, OTHERWORLD_RES
from scripts.styles import (
    console, displayLevelUp, formatDamageType, pause,
    formatEffectsDetailed, formatAbilityCost
)
from scripts.abilities import CLASS_ABILITIES

class Player(Entity):
    def __init__(self, name: str, health: int = 50, damage: int = 5, baseCritChance: float = 0.05, baseCritMulti: float = 1.5, damageType: str = "physical", speed: float = 1.0, /,
                 *, className: str = None, classDescription: str = "Basic Player", ascendancy = None, ascendancyDescription: str = None):
        super().__init__(health, damage, baseCritChance, baseCritMulti, damageType, speed, name, className)
        self.defaultDamageType = damageType
        self.classDescription = classDescription
        self._ascendancy: str = ascendancy
        self.ascendancyDescription: str = ascendancyDescription
        self.dungeonKeys = {}
        self._maxLevel = 100
        self.isPlayer = True
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

    def bypassesFormRequirement(self) -> bool:
        """Druid/Confluence: once fused, Form no longer gates which abilities can be used."""
        return False

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

            self._baseHealth += 5
            self._baseDamage += 1
            self._baseSpeed += 0.01
            self._baseMaxStamina += 2

            if self._level == self._maxLevel:
                console.print("[gold1]Congratulations! You have reached the maximum level![/gold1]")
            self._recalculateStats()
            displayLevelUp(self)
            self.gainClassAbilities(True)
            self._health = self._maxHealth
            self._stamina = self._maxStamina
            pause()

    def gainClassAbilities(self, levelUp: bool = False):
        if not self.className or self.className not in CLASS_ABILITIES:
            return

        treesByName = CLASS_ABILITIES[self.className].get('base', {})
        ascendancyData = CLASS_ABILITIES[self.className].get(self._ascendancy, {})
        alterations = ascendancyData.get('alterations', {})
        ascendancyTrees = ascendancyData.get('abilities', {})

        def _learn(name, resolved):
            if not resolved:
                return

            isNew = name not in self._abilities
            self._abilities[name] = resolved

            if isNew and levelUp: # won't print on deserialising or on init
                console.print(f"\n[bold]{'='*50}[/bold]")
                console.print(f"[gold1]🌟 CLASS ABILITY LEARNED: {name} 🌟[/gold1]")
                console.print(f"[bold]{'='*50}[/bold]")
                if resolved.damageType:
                    damageTypeFormatted = formatDamageType(resolved.damageType, resolved.damageType)
                    console.print(f"[cyan]Base Damage:[/cyan] {resolved.baseDamage} [dim]+ {resolved.damageScaling*100:.0f}% of your damage[/dim] ({damageTypeFormatted})")
                if resolved.healBase or resolved.healPercent:
                    console.print(f"[heal]Heal:[/heal] {resolved.healBase} [dim]+ {resolved.healPercent*100:.0f}% of your Max HP[/dim]")
                console.print(f"[cyan]Cooldown:[/cyan] {resolved.maxCooldown} turns")
                costStr = formatAbilityCost(resolved.resources, resolved.staminaCost)
                if costStr != "-":
                    console.print(f"[cyan]Cost:[/cyan] {costStr}")
                for line in formatEffectsDetailed(resolved.effects):
                    console.print(f"[buff]- {line}[/buff]")
                console.print(f"[bold]{'='*50}[/bold]\n")
                pause()

        for name, tree in treesByName.items():
            _learn(name, tree.getCurrentAbility(self._level, alterations.get(name)))

        for name, tree in ascendancyTrees.items():
            _learn(name, tree.getCurrentAbility(self._level, None))

    def _forgetAscendancyAbilities(self):
        for ascendancyName, ascendancyData in CLASS_ABILITIES.get(self.className, {}).items():
            if ascendancyName == 'base':
                continue
            for abilityName in ascendancyData.get('abilities', {}):
                self.removeAbility(abilityName, doPrint=False)

    def onCombatEnd(self):
        for a in self._abilities.values():
            a.cooldown = 0
        self._stamina = self._maxHealth
        self._stats['energy_shield'] = self.maxEnergyShield

        super().onCombatEnd()

    def _recalculateStats(self, doPrint: bool = True, inCombat: bool = False):
        super()._recalculateStats(doPrint, inCombat)
        weapon = self._equipment['weapon']
        if not weapon or not weapon.damageType:
            self._damageType = self.defaultDamageType

    def _applyStatDelta(self, delta: dict, sign: int = 1):
        for path, amount in delta.items():
            parts = path.split('.')
            target = self
            for p in parts[:-1]:
                target = target[p] if isinstance(target, dict) else getattr(target, p)
            leaf = parts[-1]
            if isinstance(target, dict):
                target[leaf] = target.get(leaf, 0) + amount * sign
            else:
                setattr(target, leaf, getattr(target, leaf) + amount * sign)

    def _removeOldAscendancy(self) -> bool:
        """never run super(), always return true"""
        console.print(f"[warning]No 'removeOldAscendancy()' function for {self.className}")
        return False

    def updateAscendancy(self, ascendancy: str) -> bool:
        """always run super() before updating"""
        if self._ascendancy is not None:
            if self._removeOldAscendancy():
                self._forgetAscendancyAbilities()
                return True
            console.print("[warning]Unable to change ascendancy at this time[/warning]")
            pause()
            return False
        return True

