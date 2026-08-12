from rich.console import Console
from rich.theme import Theme
from rich.table import Table
from rich.columns import Columns
from rich.panel import Panel
from rich.progress import BarColumn, Progress, TextColumn
from rich.text import Text
from rich.align import Align
from rich import box
from typing import List, Dict

# custom theme for game
KORUS_THEME = Theme({
    "common": "white",
    "uncommon": "green",
    "rare": "blue",
    "epic": "magenta",
    "legendary": "gold1 bold",
    "unique": "orange3 bold underline",

    "ability": "dim cyan",

    "physical": "white",
    "fire": "dark_red",
    "cold": "cyan",
    "lightning": "yellow",
    "dark": "magenta",
    "holy": "gold1",
    "arcane": "purple",
    "wind": "bright_green",
    "earth": "green4",
    "heal": "green",
    "chaos": "dark_magenta",
    "psychic": "bright_magenta",
    "ethereal": "grey85",

    "dot": "red",
    "hot": "green",
    "debuff": "orange1",
    "buff": "bright_green",
    "cc": "bright_red bold",

    "header": "bold cyan",
    "success": "bold green",
    "warning": "bold yellow",
    "error": "bold red",
    "info": "bright_blue",
    "gold": "yellow",
    "xp": "bright_cyan",
    "health": "red",
    "damage": "orange1",
    "speed": "bright_cyan",

    "human": "green",
    "beast": "yellow"
})

console = Console(theme=KORUS_THEME, markup=True)

#print("STYLES LOADED, CONSOLE = ", console)

RARITY_COLOURS = {
    "common": "common",
    "uncommon": "uncommon",
    "rare": "rare",
    "epic": "epic",
    "legendary": "legendary",
    "unique": "unique",
}

DAMAGE_TYPE_COLOURS = {
    "physical": "physical",
    "fire": "fire",
    "cold": "cold",
    "lightning": "lightning",
    "dark": "dark",
    "holy": "holy",
    "arcane": "arcane",
    "wind": "wind",
    "earth": "earth",
    "chaos": "chaos",
    "psychic": "psychic",
    "ethereal": "ethereal"
}

def printHeader(text: str, style: str = "header"):
    if '[' in text and ']' in text:
        console.print(Panel(text,
                            box=box.DOUBLE,
                            style=style))
    else:
        console.print(Panel(f"[{style}]{text.upper()}[/{style}]",
                            box=box.DOUBLE,
                            style=style))
    
def printSeparator(char: str = "=", length: int = 50):
    console.print(char * length, style="dim")

def pause():
    console.input("\n[dim]Press Enter to continue...[/dim]")

def clearScreen():
    console.clear()

def formatRarity(text: str, rarity: str) -> str:
    colour = RARITY_COLOURS.get(rarity.lower(), 'white')
    return f"[{colour}]{text}[/{colour}]"

def formatDamageType(text: str, damageType: str) -> str:
    colour = DAMAGE_TYPE_COLOURS.get(damageType.lower(), "white")
    return f"[{colour}]{text}[/{colour}]"

def formatEffectsSummary(effects: Dict) -> str:
    """Short human-readable summary of an ability's effects dict,
    e.g. 'curse, otherworld exposure (target); haste (self)'"""
    parts = []
    for side in ('target', 'self'):
        names = [name for name in effects.get(side, {}).keys() if name != 'spawn_consumable']
        if names:
            parts.append(f"{', '.join(n.replace('_', ' ') for n in names)} ({side})")
    return '; '.join(parts)

def formatStatChange(value: float) -> str:
    if value > 0:
        return f"[success]+{value}[/success]"
    elif value < 0:
        return f"[error]-{value}[/error]"
    else:
        return f"[dim]{value}[/dim]"
    
def createHealthBar(current: int, maximum: int, width: int = 20) -> str:
    percentage = current / maximum if maximum > 0 else 0
    filled = int(width * percentage)
    empty = width - filled

    if percentage > 0.6:
        colour = "green"
    elif percentage > 0.3:
        colour = "yellow"
    else:
        colour = "red"
    
    bar = f"[{colour}]{'█' * filled}[/{colour}][dim]{'░' * empty}[/dim]"
    return f"{bar} [{current}/{maximum}]"

def createEquipmentTable(equipmentDict: dict) -> Table:
    table = Table(title="Equipment", box=box.ROUNDED, show_header=True)
    table.add_column("Slot", style="cyan", no_wrap=True)
    table.add_column("Item", style="white")
    table.add_column("Stats", style="dim")

    for slot, equip in equipmentDict.items():
        if equip:
            itemName = formatRarity(equip.name, equip.rarity.value)
            stats = ", ".join([f"{k}: +{v}" for k, v in equip.stats.items()])
            table.add_row(slot.capitalize(), itemName, stats)
        else:
            table.add_row(slot.capitalize(), "[dim]Empty[/dim]", "")

    return table

def createAbilityTable(abilities: dict) -> Table:
    table = Table(title="Abilities", box=box.ROUNDED, show_header=True)
    table.add_column("#", style="cyan", no_wrap=True)
    table.add_column("Ability", style="white")
    table.add_column("Damage", justify="right")
    table.add_column("Type", style="dim")
    table.add_column("Cooldown", justify="center")
    table.add_column("Effects", style="dim")

    for i, (name, ability) in enumerate(abilities.items(), 1):
        damageStr = str(ability.baseDamage) if ability.baseDamage >= 0 else f"[green]{-ability.baseDamage} HP[/green]"
        damageType = formatDamageType(ability.damageType, ability.damageType) if ability.damageType else "-"
        cooldownStr = f"[red]{ability.cooldown}[/red]" if ability.cooldown > 0 else f"[green]0[/green]"
        effects = formatEffectsSummary(ability.effects)
        table.add_row(str(i), name, damageStr, damageType, cooldownStr, effects)

    return table

def createInventoryTable(inventory: dict) -> Table:
    table = Table(title="Inventory", box=box.ROUNDED, show_header=True)
    table.add_column("Item", style="white")
    table.add_column("Quantity", justify="right", style="cyan")
    
    for item, quantity in sorted(inventory.items()):
        table.add_row(item, str(quantity))

    return table

def displayCombatStatus(player, enemies: list):
    playerHP = createHealthBar(player._health, player._maxHealth, width=15)
    playerInfo = f"[bold cyan]{player._name}[/bold cyan] (Lv. {player._level})\n"
    playerInfo += f"HP: {playerHP}\n"
    playerInfo += f"DMG: [damage]{player._damage}[/damage] | "
    playerInfo += f"Type: {formatDamageType(player._damageType, player._damageType)}"

    playerPanel = Panel(playerInfo, title="[bold green]Player[/bold green]",
                        box=box.ROUNDED, border_style="green")
    
    enemyPanels = []
    for i, enemy in enumerate(enemies, 1):
        if not enemy._isDead:
            enemyHP = createHealthBar(enemy._health, enemy._maxHealth, width=10)
            enemyInfo = f"[bold red]{enemy._name}[/bold red] (Lv.{enemy._level})\n"
            enemyInfo += f"HP: {enemyHP}\n"
            enemyInfo += f"DMG: [damage]{enemy._damage}[/damage]"
            
            enemyPanel = Panel(enemyInfo, title=f"[bold red]Enemy {i}[/bold red]", 
                               box=box.ROUNDED, border_style="red", width=40)
            enemyPanels.append(enemyPanel)

    console.print(playerPanel)
    if enemyPanels:
        console.print(Columns(enemyPanels, equal=True, expand=True))

def displayLoot(resources: dict, equipment: list):
    if resources:
        table = Table(title="[gold]Resources Acquired[/gold]", box=box.ROUNDED)
        table.add_column("Resource", style="white")
        table.add_column("Amount", justify="right", style="cyan")
        
        for resource, amount in sorted(resources.items()):
            table.add_row(resource, str(amount))
        
        console.print(table)

    if equipment:
        table = Table(title="[legendary]Equipment Acquired[/legendary]", box=box.ROUNDED)
        table.add_column("Equipment", style="white")
        table.add_column("Slot", style="cyan")
        table.add_column("Rarity", style="white")
        
        for equip in equipment:
            name = formatRarity(equip.name, equip.rarity.value)
            table.add_row(name, equip.slot.capitalize(), equip.rarity.value.capitalize())
        
        console.print(table)

def displayLevelUp(player):
    message = f"""
    [bold][gold1]★ LEVEL UP! ★[/bold][/gold1]
    
    [cyan]You are now level {player._level}[/cyan]
    [green]HP: {player._maxHealth}[/green]
    [orange1]DMG: {player._damage}[/orange1]
    [bright_cyan]SPD: {player._speed:.2f}[/bright_cyan]
    """

    panel = Panel(
        Align.center(message),
        box=box.DOUBLE,
        border_style="gold1",
        padding=(1, 4)
    )

    console.print(panel)

def displayDeath():
    message = """
    [bold red]☠ YOU HAVE DIED ☠[/bold red]

    [dim]Your journey ends here...[/dim]
    """

    panel = Panel(
        Align.center(message),
        box=box.DOUBLE,
        border_style="red",
        padding=(2, 4)
    )

    console.print(panel)

def displayVictory():
    message = """
    [bold gold1]⚔ VICTORY! ⚔[/bold gold1]
    
    [green]Your enemies have been vanquished![/green]
    """
    
    panel = Panel(
        Align.center(message),
        box=box.DOUBLE,
        border_style="gold1",
        padding=(1, 4)
    )
    
    console.print(panel)

def printInfo(message: str):
    console.print(f"[info]{message}[/info]")

def printSuccess(message: str):
    console.print(f"[success]{message}[/success]")

def printWarning(message: str):
    console.print(f"[warning]{message}[/warning]")

def printError(message: str):
    console.print(f"[error]{message}[/error]")

def displayResourceCost(required: dict, current: dict) -> Table:
    table = Table(box=box.SIMPLE, show_header=False)
    table.add_column("Status", style="white", width=3)
    table.add_column("Resource", style="cyan")
    table.add_column("Amount", justify="right", style="white")
    
    for resource, amount in required.items():
        has = current.get(resource, 0)
        status = "[success]✓[/success]" if has >= amount else "[error]✗[/error]"
        table.add_row(status, resource, f"{has}/{amount}")
    
    return table

def createEnemyPreview(enemies: List) -> Table:
    table = Table(show_header=True, header_style="bold magenta", box=None, padding=(0, 1))

    for i, enemy in enumerate(enemies, 1):
        table.add_column(f"Enemy {i}", style="red", justify="left")

    enemyColumns = []
    maxRows = 0

    for enemy in enemies:
        col = []
        col.append(f"[bold red]{enemy._name}[/bold red]")
        col.append(f"[dim](Level {enemy._level})[/dim]")
        col.append("")

        col.append(f"[health]HP:[/health] {enemy._health}/{enemy._maxHealth}")
        col.append(f"[damage]DMG:[/damage] {enemy._damage} [dim]({formatDamageType(enemy._damageType, enemy._damageType)})[/dim]")
        col.append(f"[speed]SPD:[/speed] {enemy._speed}")
        col.append("")

        if enemy._abilities:
            col.append("[bold cyan]Abilities:[/bold cyan]")
            for name, ability in enemy._abilities.items():
                effectsSummary = formatEffectsSummary(ability.effects)
                mechText = f" [dim]({effectsSummary})[/dim]" if effectsSummary else ""
                col.append(f"  [cyan]•[/cyan] {name}{mechText}")
            col.append("")

        resources = enemy._lootTable.resources
        if resources:
            col.append("[bold gold]Resources:[/bold gold]")
            resourceParts = []
            for resource, (minAmt, maxAmt, chance) in resources.items():
                resourceParts.append(f"{resource}: {minAmt}-{maxAmt} | Drop Chance = {int(chance*100)}%")
            col.append(f"[gold]" + ", ".join(resourceParts) + "[/gold]")

        equipment = enemy._lootTable.equipmentPool
        if equipment:
            col.append("[bold yellow]Equipment:[/bold yellow]")
            equipmentParts = []
            for equip, chance in equipment:
                equipmentParts.append(f"{equip.name} | Drop Chance = {int(chance*100)}%")
            col.append("[yellow]" + "\n".join(equipmentParts) + "[/yellow]")

        enemyColumns.append(col)
        maxRows = max(maxRows, len(col))
        
    for col in enemyColumns:
        while len(col) < maxRows:
            col.append("")
    
    rows = []
    for i in range(maxRows):
        row = []
        for col in enemyColumns:
            row.append(col[i])
        rows.append(row)

    for row in rows:
        if any(cell.strip() for cell in row):
            table.add_row(*row)

    return table

def createCombatStatusTable(player, enemies: List) -> Table:
    aliveEnemies = [e for e in enemies if not e._isDead]
    maxEntitiesPerRow = 5

    def createEntityColumn(entity, isPlayer=False):
        col = []
        if isPlayer:
            col.append(f"[bold green]{entity._name}[/bold green] [dim](Lv.{entity._level})[/dim]")
        else:
            col.append(f"[bold red]{entity._name}[/bold red]")
            col.append(f"[dim](Lv.{entity._level})[/dim]")
        
        width = 15 if isPlayer else 10
        healthBar = createHealthBar(entity._health, entity._maxHealth, width)
        col.append(f"[health]HP:[/health] {healthBar}")
        col.append(f"[damage]DMG:[/damage] {entity._damage} [dim]({formatDamageType(entity._damageType, entity._damageType)})[/dim]")
        col.append(f"[speed]SPD:[/speed] {entity._speed if not isPlayer else f'{entity._speed:.2f}'}")
        col.append("")
        
        activeResists = {k: v for k, v in entity._stats['Resistances'].items() if v != 0}
        if activeResists:
            col.append("[bold]Resistances:[/bold]")
            resistParts = []
            for dtype, amount in activeResists.items():
                colourCode = DAMAGE_TYPE_COLOURS.get(dtype.lower(), "white")
                resistParts.append(f"[{colourCode}]{dtype}:[/{colourCode}] {amount}%")
            for i in range(0, len(resistParts), 2):
                col.append("  " + ", ".join(resistParts[i:i+2]))
        
        return col

    totalEntities = 1 + len(aliveEnemies)

    firstRowEnemyCount = min(4, len(aliveEnemies))

    remainingEnemies = aliveEnemies[firstRowEnemyCount:]

    table1 = Table(show_header=True, header_style="bold cyan", box=None, padding=(0, 1))
    table1.add_column("Player", style="green", justify="left", width=35)
    
    for i in range(firstRowEnemyCount):
        table1.add_column(f"Enemy {i+1}", style="red", justify="left", width=35)

    firstRowColumns = [createEntityColumn(player, isPlayer=True)]
    for i, enemy in enumerate(aliveEnemies[:firstRowEnemyCount]):
        firstRowColumns.append(createEntityColumn(enemy))

    maxRows = max(len(col) for col in firstRowColumns)
    for col in firstRowColumns:
        while len(col) < maxRows:
            col.append("")

    for i in range(maxRows):
        row = [col[i] for col in firstRowColumns]
        if any(cell.strip() for cell in row):
            table1.add_row(*row)
    
    console.print(table1)

    enemyIndex = firstRowEnemyCount + 1
    while remainingEnemies:
        console.print()

        batchSize = min(maxEntitiesPerRow, len(remainingEnemies))
        currentBatch = remainingEnemies[:batchSize]
        remainingEnemies = remainingEnemies[batchSize:]

        tableN = Table(show_header=True, header_style="bold cyan", box=None, padding=(0, 1))
        
        for i in range(batchSize):
            tableN.add_column(f"Enemy {enemyIndex + i}", style="red", justify="left", width=35)

        batchColumns = []
        for enemy in currentBatch:
            batchColumns.append(createEntityColumn(enemy))

        maxRows = max(len(col) for col in batchColumns)
        for col in batchColumns:
            while len(col) < maxRows:
                col.append("")

        for i in range(maxRows):
            row = [col[i] for col in batchColumns]
            if any(cell.strip() for cell in row):
                tableN.add_row(*row)
        
        console.print(tableN)
        enemyIndex += batchSize

def createAbilityTables(abilities: dict, maxPerTable: int = 10) -> Columns:
    abilityList = list(abilities.items())
    tables = []
    maxColumns = 3

    #console.print(f"[dim]DEBUG: Total abilities: {len(abilityList)}, maxPerTable: {maxPerTable}[/dim]")

    for i in range(0, len(abilityList), maxPerTable):
        chunk = abilityList[i:i+maxPerTable]

        #console.print(f"[dim]DEBUG: Creating table {len(tables)+1} with abilities {i+1} to {i+len(chunk)}[/dim]")

        table = Table(show_header=True, header_style="bold cyan", box=box.ROUNDED, padding=(0, 1))
        table.add_column("#", style="dim", width=2)
        table.add_column("Ability", style="cyan", width=15)
        table.add_column("DMG", style="damage", width=3)
        table.add_column("Type", width=9)
        table.add_column("CD", style="yellow", width=2)
        table.add_column("Effects", style="buff", width=15)

        for j, (name, ability) in enumerate(chunk, start=i+1):
            cdText = str(ability.cooldown) if ability.cooldown > 0 else "✓"
            cdStyle = "red" if ability.cooldown > 0 else "green"
            effectsText = formatEffectsSummary(ability.effects)
            if len(effectsText) > 15:
                effectsText = effectsText[:14] + "..."

            dmgTypeFormatted = formatDamageType(ability.damageType, ability.damageType) if ability.damageType else "-"

            table.add_row(
                str(j),
                name[:16] + ".." if len(name) > 16 else name,
                str(ability.baseDamage),
                dmgTypeFormatted,
                f"[{cdStyle}]{cdText}[/{cdStyle}]",
                effectsText
            )

        tables.append(table)

        if len(tables) >= maxColumns:
            break

    return Columns(tables, equal=False, expand=False)

...