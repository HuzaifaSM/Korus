import time

from scripts.entities import Entity, ELEMENTAL_RES, DIVINE_RES, OTHERWORLD_RES, SIGIL_SLOTS
from scripts.styles import (
    console, displayLevelUp, pause,
    formatEffectsDetailed, formatAbilityCost, clearScreen, printHeader,
    printSeparator, printWarning, printSuccess, formatRarity,
    createEquipmentStoragePages, stepPage, selectFromNumberedList,
    checkGlobalCommand
)
from scripts.abilities import CLASS_ABILITIES

def _abilityChanged(old, new) -> bool:
    return (
        old.baseDamage != new.baseDamage or
        old.damageScaling != new.damageScaling or
        old.damageType != new.damageType or
        old.healBase != new.healBase or
        old.healPercent != new.healPercent or
        old.maxCooldown != new.maxCooldown or
        old.staminaCost != new.staminaCost or
        old.targets != new.targets or
        old.resources != new.resources or
        old.effects != new.effects or
        old.description != new.description
    )

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

    @property
    def unlockedSigilSlots(self) -> int:
        """Players start with 1 sigil slot, unlocking 1 more every 20 levels, up to 5 total."""
        return min(5, 1 + self._level // 20)

    def death(self):
        console.print("\n[bold red]" + "="*25 + "[/bold red]")
        console.print("[bold red]YOU HAVE DIED[/bold red]")
        console.print("[bold red]" + "="*25 + "[/bold red]\n")
        return True
    
    def __rich__(self):
        return self.__str__()

    def __str__(self):
        return f"[health]HP:[/health] {self._health} / {self._maxHealth}\n[damage]Damage:[/damage] {self._damage} | Type: [{self._damageType}]{self._damageType.title()}[/{self._damageType}] | [speed]Speed:[/speed] {self._speed}\n[xp]XP:[/xp] {self._xp} / {self._xpToNextLevel}"

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
            self.consumable.updateValue(self._level)

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

            previous = self._abilities.get(name)
            isNew = previous is None
            isUpgrade = not isNew and _abilityChanged(previous, resolved)
            self._abilities[name] = resolved

            if levelUp and (isNew or isUpgrade): # won't print on deserialising or on init
                title = "CLASS ABILITY LEARNED" if isNew else "ABILITY UPGRADED"
                emoji = "🌟" if isNew else "⬆️"
                colour = "gold1" if isNew else "cyan"
                console.print(f"\n[bold]{'='*50}[/bold]")
                console.print(f"[{colour}]{emoji} {title}: {name} {emoji}[/{colour}]")
                console.print(f"[bold]{'='*50}[/bold]")
                if resolved.damageType:
                    damageTypeFormatted = f" [{resolved.damageType}]{resolved.damageType.title()}[/{resolved.damageType}]"
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

    def equipmentMenu(self):
        while True:
            clearScreen()
            printHeader("Equipment Management")

            console.print("\n[bold cyan]=== Currently Equipped ===[/bold cyan]")
            hasEquipment = False
            for _, equip in self._equipment.items():
                if equip:
                    hasEquipment = True
                    console.print(equip)
            if not hasEquipment:
                console.print("  [dim]Nothing equipped[/dim]")

            # Show storage count
            console.print(f"\n[bold cyan]=== Equipment Storage ===[/bold cyan]")
            console.print(f"[dim]Items in storage: {len(self._equipmentStorage)}[/dim]")

            printSeparator()
            console.print("[dim]0.[/dim] [red]Return[/red]")
            console.print("[dim]1.[/dim] [green]Equip from Storage[/green]")
            console.print("[dim]2.[/dim] [yellow]Unequip to Storage[/yellow]")
            console.print("[dim]3.[/dim] [orange1]Compare Equipment[/orange1]")

            choice = console.input("\n[bold cyan]>[/bold cyan] ").strip()
            checkGlobalCommand(choice)

            try:
                choice = int(choice)
                match choice:
                    case 0:
                        return
                    case 1:
                        self.equipFromStorage()
                    case 2:
                        self.unequipToStorage()
                    case 3:
                        self.compareEquipment()
                    case _:
                        printWarning("Invalid choice!")
                        time.sleep(1)
            except ValueError:
                printWarning("Invalid input!")
                time.sleep(1)

    def equipFromStorage(self):
        if not self._equipmentStorage:
            printWarning("No equipment in storage!")
            pause()
            return

        slots = []
        for slot in self._equipment.keys():
            if slot in SIGIL_SLOTS:
                if 'sigil' not in slots:
                    slots.append('sigil')
                continue
            slots.append(slot)

        while True:
            clearScreen()
            printHeader("Equip from Storage")

            console.print("\n[bold cyan]=== Choose a Slot ===[/bold cyan]")
            for i, slot in enumerate(slots, 1):
                count = sum(1 for equip in self._equipmentStorage if equip.slot == slot)
                countLabel = f"[dim]({count} in storage)[/dim]" if count else "[dim](none in storage)[/dim]"
                console.print(f"[cyan]{i}.[/cyan] {slot.capitalize()} {countLabel}")

            choice = console.input("\n[cyan]Choose a slot to equip (0 to cancel):[/cyan]\n> ").strip()
            if choice == '0':
                return
            try:
                index = int(choice) - 1
            except ValueError:
                printWarning("Invalid input!")
                pause()
                continue
            if not (0 <= index < len(slots)):
                printWarning("Invalid choice!")
                pause()
                continue

            self._equipSlotFromStorage(slots[index])

    def _equipSlotFromStorage(self, slot: str):
        slotItems = [(i, equip) for i, equip in enumerate(self._equipmentStorage) if equip.slot == slot]
        if not slotItems:
            printWarning(f"No {slot.capitalize()} in storage!")
            pause()
            return

        inventoryPages = createEquipmentStoragePages([equip for _, equip in slotItems])
        totalPages = len(inventoryPages)
        currentPage = 1

        while True:
            clearScreen()
            printHeader(f"Equip {slot.capitalize()} from Storage")

            console.print(f"\n[bold cyan]=== {slot.capitalize()} (Page {currentPage}/{totalPages}) ===[/bold cyan]")
            console.print(inventoryPages[currentPage])

            prompt = "\n[cyan]Choose item to equip (0 to cancel"
            if totalPages > 1:
                prompt += ", N for next page, P for previous page"
            prompt += "):[/cyan]\n> "
            choice = console.input(prompt).strip().lower()

            newPage = stepPage(currentPage, totalPages, choice)
            if newPage is not None:
                currentPage = newPage
                continue

            try:
                choiceIndex = int(choice) - 1
            except ValueError:
                printWarning("Invalid input!")
                pause()
                return
            break

        if not (0 <= choiceIndex < len(slotItems)):
            printWarning("Invalid choice!")
            pause()
            return

        storageIndex, equipment = slotItems[choiceIndex]

        if slot == 'sigil':
            unlockedSlots = SIGIL_SLOTS[:self.unlockedSigilSlots]
            targetSlot = next((s for s in unlockedSlots if self._equipment.get(s) is None), None)
            if targetSlot is None:
                console.print("\n[bold cyan]=== Choose Sigil Slot to Replace ===[/bold cyan]")
                for i, s in enumerate(unlockedSlots, 1):
                    equipped = self._equipment[s]
                    console.print(f"[cyan]{i}.[/cyan] {equipped.name}")
                replaceChoice = console.input("\n[cyan]Choose a sigil slot (0 to cancel):[/cyan]\n> ").strip()
                if replaceChoice == '0':
                    return
                try:
                    replaceIndex = int(replaceChoice) - 1
                except ValueError:
                    printWarning("Invalid input!")
                    pause()
                    return
                if not (0 <= replaceIndex < len(unlockedSlots)):
                    printWarning("Invalid choice!")
                    pause()
                    return
                targetSlot = unlockedSlots[replaceIndex]
        else:
            targetSlot = slot

        # Show comparison if slot is occupied
        if self._equipment[targetSlot]:
            current = self._equipment[targetSlot]
            console.print(f"\n{equipment.compareTo(current)}")
            confirm = console.input("\n[cyan]Equip this item? (y/n):[/cyan] ").strip().lower()
            if confirm != 'y':
                return

            # Unequip current and move to storage
            old = self.unequip(targetSlot)
            if old:
                self._equipmentStorage.append(old)

        # Equip new item and remove from storage
        self._equipmentStorage.pop(storageIndex)
        self.equip(equipment, slot=targetSlot)
        printSuccess(f"Equipped {equipment.name}!")
        pause()

    def unequipToStorage(self):
        equippedSlots = [(slot, equip) for slot, equip in self._equipment.items() if equip]

        if not equippedSlots:
            printWarning("Nothing equipped!")
            pause()
            return

        clearScreen()
        printHeader("Unequip to Storage")

        console.print("\n[bold cyan]=== Equipped Items ===[/bold cyan]")

        def renderEquipped(i, slotEquip):
            slot, equip = slotEquip
            equipName = formatRarity(equip.name, equip.rarity.value)
            console.print(f"[cyan]{i}.[/cyan] [{slot.upper()}] {equipName}")
            console.print(f"{equip}")

        index = selectFromNumberedList(equippedSlots, "Choose item to unequip (0 to cancel):", render=renderEquipped)
        if index is None:
            return

        slot, equipment = equippedSlots[index]
        confirm = console.input(f"\n[warning]Unequip {equipment.name}? (y/n):[/warning] ").strip().lower()
        if confirm == 'y':
            unequipped = self.unequip(slot)
            if unequipped:
                self._equipmentStorage.append(unequipped)
                printSuccess(f"Unequipped {equipment.name} to storage!")
                pause()

    def compareEquipment(self):
        clearScreen()
        printHeader("Compare Equipment")

        allEquipment = []
        for slot, equip in self._equipment.items():
            if equip:
                allEquipment.append((f"[EQUIPPED] {slot}", equip))
        for i, equip in enumerate(self._equipmentStorage):
            allEquipment.append((f"[STORAGE] #{i+1}", equip))

        if len(allEquipment) < 2:
            printWarning("Need at least 2 equipment pieces to compare!")
            return

        def renderChoice(i, locationEquip):
            location, equip = locationEquip
            equipName = formatRarity(equip.name, equip.rarity.value)
            console.print(f"  [cyan]{i}.[/cyan] [dim]{location}[/dim] {equipName}")

        console.print("\n[bold cyan]=== Select First Item ===[/bold cyan]")
        index1 = selectFromNumberedList(allEquipment, "Choose first item:", render=renderChoice)
        if index1 is None:
            return

        console.print("\n[bold cyan]=== Select Second Item ===[/bold cyan]")
        index2 = selectFromNumberedList(allEquipment, "Choose second item:", render=renderChoice, skip={index1})
        if index2 is None:
            return

        _, equip1 = allEquipment[index1]
        _, equip2 = allEquipment[index2]

        console.print("\n" + "="*50)
        console.print(equip1.compareTo(equip2))
        console.print("="*50)
        pause()

