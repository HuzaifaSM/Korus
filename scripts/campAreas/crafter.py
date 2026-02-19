from typing import Optional
import random
from .station import Station
from scripts.items import Equipment, ItemRarity, rollRarity
from scripts.styles import (
    console, clearScreen, printHeader, printSeparator,
    pause, printWarning, printError, printSuccess, formatRarity
)

class Crafter(Station):
        # crafter is simplest functioning station. higher levels allow better crafting options
        # e.g. higher stat rolls, more stats, higher rarity chances etc.
    def __init__(self, player):
        super().__init__(player, "Crafter")
        self.blueprints = 0

    def _getUpgradeRequirements(self):
        return {
            1: {"wood": 50, "stone": 50, "iron_ore": 20},
            2: {"wood": 100, "iron_ore": 50, "leather": 30},
            3: {"iron_ore": 100, "crystal": 10, "bone": 20},
            4: {"crystal": 30, "mana_essence": 10, "soul": 15},
            5: {"mana_essence": 50, "diamond": 20, "dragon_scale": 5}
        }
    
    def _serialise(self):
        temp = super()._serialise()
        temp['blueprints'] = self.blueprints
        return temp

    def mainMenu(self):
        while True:
            clearScreen()
            printHeader(f"Crafter Level {self.level}")
            console.print(f"[gold]Blueprints:[/gold] {self.blueprints}")
            printSeparator()
            console.print("[dim]0.[/dim] Return")
            if self.level >= 1:
                console.print("[dim]1.[/dim] Craft Equipment")
            if self.level >= 2:
                console.print("[dim]2.[/dim] Enchant Equipment")
            console.print("[dim]9.[/dim] Upgrade Crafter")
            
            choice = console.input("\n[cyan]>[/cyan] ").strip()

            try:
                choice = int(choice)
                match choice:
                    case 0:
                        break
                    case 1:
                        if self.level >= 1:
                            self.craftingMenu()
                    case 2:
                        if self.level >= 3:
                            self.enchantingMenu()
                    case 9:
                        self.upgrade()
                    case _:
                        printWarning(f"Invalid choice: {choice}")
            except ValueError as e:
                printError(f"{e}")
                pause()

    def craftingMenu(self):
        clearScreen()
        printHeader("CRAFT EQUIPMENT")
        console.print(f"[gold]Blueprints:[/gold] {self.blueprints}")
        
        slots = ['weapon', 'head', 'chest', 'legs', 'feet', 'ring', 'amulet']
        console.print("\n[bold]nSelect slot to craft:[/bold]")
        for i, slot in enumerate(slots, 1):
            console.print(f"  [cyan]{i}.[/cyan] {slot.capitalize()}")
        
        choice = console.input("\n[cyan]Choose slot (0 to cancel):\n>[/cyan] ").strip()
        try:
            index = int(choice) - 1
            if 0 <= index < len(slots):
                self.craftEquipment(slots[index])
        except ValueError:
            pass
        pause()

    def craftEquipment(self, slot: str):
        if self.level < 1:
            printWarning(f"Crafter Level 1 required for crafting. Current Level: {self.level}")
            return
        
        blueprintCost = 5 + (self.level * 5)
        if self.blueprints < blueprintCost:
            printWarning(f"Need {blueprintCost} blueprints to craft. Current blueprints: {self.blueprints}")
            return
        # rarities based on crafter level
        rarityChances = {
            1: {ItemRarity.COMMON: 0.8, ItemRarity.UNCOMMON: 0.2},
            2: {ItemRarity.COMMON: 0.6, ItemRarity.UNCOMMON: 0.3, ItemRarity.RARE: 0.1},
            3: {ItemRarity.COMMON: 0.4, ItemRarity.UNCOMMON: 0.35, ItemRarity.RARE: 0.2, ItemRarity.EPIC: 0.05},
            4: {ItemRarity.UNCOMMON: 0.4, ItemRarity.RARE: 0.35, ItemRarity.EPIC: 0.2, ItemRarity.LEGENDARY: 0.05},
            5: {ItemRarity.RARE: 0.5, ItemRarity.EPIC: 0.35, ItemRarity.LEGENDARY: 0.15}
        }

        rarityBonus = int(self.player._stats['Bonuses']['itemRarity'] * 0.5) # rarity applied at half value
        rarity = rollRarity(rarityBonus)

        roll = random.random()
        cumulative = 0
        rarity = ItemRarity.COMMON
        for r, chance in rarityChances[self.level].items():
            cumulative += chance
            if roll <= cumulative:
                rarity = r
                break
        # generate equipment
        equipment = Equipment._generateEquipmentPiece(self.player._level, slot, rarity)
        self.blueprints -= blueprintCost
        console.print(f"\n[success]Crafted:[/success] {formatRarity(equipment.name, equipment.rarity.value)}")
        console.print(f"    [dim]{equipment._formatStats()}[/dim]")
        self.player.addEquipmentToStorage(equipment)

    def enchantingMenu(self):
        clearScreen()
        printHeader("Enchant Equipment")
        console.print(f"[gold]Blueprints:[/gold] {self.blueprints}")
        
        # Select equipment
        equip = self._selectEquipment()
        if not equip:
            return
        
        # Show enchantments
        enchantments = {
            "vampiric": ("Lifesteal", {"lifesteal": 0.10}),
            "thorns": ("Damage Reflection", {"reflect_damage": 0.1}),
            "haste": ("Speed Boost", {"speed": 0.15}),
            "vitality": ("Health Boost", {"health": 50}),
            "powerful": ("Damage Boost", {"damage": 10})
        }
        
        console.print("\n[gold]Available enchantments:[/gold]")
        enchantList = list(enchantments.items())
        for i, (_, (name, _)) in enumerate(enchantList, 1):
            console.print(f"  [cyan]{i}.[/cyan] {name}")
        
        choice = console.input("\n[cyan]Choose enchantment:\n> [/cyan]").strip()
        try:
            index = int(choice) - 1
            if 0 <= index < len(enchantList):
                enchantKey = enchantList[index][0]
                self.enchantEquipment(equip, enchantKey)
        except ValueError:
            pass
        pause()

    def enchantEquipment(self, equipment: Equipment, enchantmentType: str):
        if self.level < 3:
            printWarning(f"Crafter Level 3 required to enchant. Current level: {self.level}")
            return
        enchantCost = 20
        if self.blueprints < enchantCost:
            printWarning(f"Need {enchantCost} blueprints to enchant. Current blueprints: {self.blueprints}")
            return
        # enchantments
        enchantments = {
            "vampiric": {"lifesteal": 0.10}, #10% lifesteal on hit
            "thorns": {"reflect_damage": 0.1}, # 10% damage reflected
            "haste": {"speed": 0.15},
            "vitality": {"health": 50},
            "powerful": {"damage": 10}
        }
        if enchantmentType not in enchantments:
            printWarning(f"Unknown enchantment: {enchantmentType}")
            return
        # add enchantment stats
        for stat, value in enchantments[enchantmentType].items():
            equipment.stats[stat] = equipment.get(stat, 0) + value
        self.blueprints -= enchantCost
        printSuccess(f"\nEnchanted {equipment.name} with {enchantmentType}")
        console.print(f"[dim]New stats: {equipment._formatStats()}[/dim]")

    def _selectEquipment(self) -> Optional[Equipment]:
        allEquipment = []

        for slot, equip in self.player._equipment.items():
            if equip:
                allEquipment.append((f"[EQUIPPED] {slot}", equip))
        for i, equip in enumerate(self.player._equipmentStorage):
            allEquipment.append((f"[STORAGE] #{i+1}", equip))

        if not allEquipment:
            printWarning("No equipment available")
            pause()
            return None
        
        console.print("\n[bold]Available equipment:[/bold]")
        for i, (location, equip) in enumerate(allEquipment, 1):
            console.print(f"  [cyan]{i}.[/cyan] {location} {equip.name}")
            console.print(f"    [dim]{equip._formatStats()}[/dim]")

        choice = console.input("\n[cyan]Choose equipment (0 to cancel):\n> [/cyan]").strip()
        try:
            index = int(choice) - 1
            if 0 <= index < len(allEquipment):
                return allEquipment[index][1]
        except ValueError:
            pass
        
        return None
