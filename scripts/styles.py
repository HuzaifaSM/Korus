import re
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
    "mythic": "deep_pink3 bold",
    "blank": "bold thistle1 italic",

    "ability": "dim cyan",

    "physical": "white",
    "fire": "dark_red",
    "cold": "cyan",
    "lightning": "yellow",
    "dark": "magenta",
    "holy": "gold1",
    "arcane": "purple",
    "earth": "green4",
    "heal": "green",
    "chaos": "dark_magenta",
    "psychic": "bright_magenta",
    "ethereal": "grey85",

    "divine": "light_goldenrod1",
    "otherworld": "blue_violet",
    "elemental": "orange3",
    "all": "bright_white",

    "dot": "red",
    "hot": "green",
    "debuff": "orange1",
    "buff": "bright_green",
    "cc": "bright_red bold",
    "exposure": "plum1",

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
    "stamina": "sky_blue1",

    "armour": "grey53",
    "evasion": "chartreuse3",
    "energy_shield": "deep_sky_blue1",

    "human": "green",
    "beast": "yellow",

    # keyword categories
    "resource": "turquoise2 bold",
    "critical": "gold3 bold",
    "resistance": "steel_blue1",
    "lifesteal": "red3 bold",
    "regen": "spring_green3",

    "lore": "medium_violet_red dim bold",

    # class colours
    "class_warrior": "dark_red bold",
    "class_fighter": "white bold",
    "class_mage": "purple bold",
    "class_wanderer": "bright_magenta bold",
    "class_wretch": "magenta bold",
    "class_paladin": "gold1 bold",
    "class_spectre": "grey85 bold",
    "class_cultist": "dark_magenta bold",
    "class_tempest": "yellow bold",
    "class_marauder": "cyan bold",

    # Cultist ascendancy family
    "asc_umbralist": "purple4 bold",
    "asc_harbinger": "dark_violet bold",
    "asc_doomsayer": "medium_orchid bold",
    "asc_ritualist": "deep_pink4 bold",
    "asc_anarchist": "bright_magenta bold",
    "asc_desecrator": "medium_purple bold",

    # Paladin ascendancy family
    "asc_zealot": "dark_goldenrod bold",
    "asc_guardian": "light_goldenrod3 bold",
    "asc_justicar": "gold3 bold",
    "asc_crusader": "yellow3 bold",
    "asc_inquisitor": "wheat1 bold",

    # Spectre ascendancy family
    "asc_wraith": "grey62 bold",
    "asc_reaper": "grey42 bold",
    "asc_phantasm": "grey78 bold",
    "asc_revenant": "grey58 bold",
    "asc_lich": "grey93 bold",

    # Wanderer ascendancy family
    "asc_fractured": "orchid bold",
    "asc_manifestation": "plum2 bold",
    "asc_weaver": "medium_orchid3 bold",
    "asc_abyssal": "magenta3 bold",
    "asc_warper": "hot_pink3 bold",
    "asc_mindbreaker": "deep_pink2 bold",

    # Wretch ascendancy family
    "asc_exsanguinator": "indian_red bold",
    "asc_bloodletter": "indian_red1 bold",
    "asc_plaguebearer": "dark_khaki bold",
    "asc_necrose": "grey39 bold",
    "asc_necromancer": "medium_purple4 bold",

    # Tempest ascendancy family
    "asc_alternator": "light_yellow3 bold",

    # Warrior ascendancy family
    "asc_warlord": "orange_red1 bold",
    "asc_juggernaut": "grey46 bold",
    "asc_annihilist": "red3 bold",
    "asc_tyrant": "dark_orange3 bold",
    "asc_conqueror": "tan bold",

    # Marauder ascendancy family
    "asc_colossus": "deep_sky_blue3 bold",
    "asc_dreadnought": "royal_blue1 bold",
    "asc_sovereign": "light_slate_blue bold",
    "asc_harrower": "dark_cyan bold",
    "asc_butcher": "light_steel_blue1 bold"
})

# -- keyword highlighting: maps literal keyword text to a theme style key.
# Longest phrases are matched first so multi-word keywords aren't shadowed by
# shorter ones they contain (e.g. "Crit Chance" vs a hypothetical "Chance").
KEYWORDS: Dict[str, str] = {
    # class resources / mechanics
    "Insanity": "resource", "Rage": "resource", "Fury": "resource",
    "Combo": "resource", "Verdance": "resource", "Mastery": "resource",
    "Favour": "resource", "Prowess": "resource", "Momentum": "resource",
    "Insight": "resource", "Mana": "resource", "Blood Spike": "resource",
    "Lost": "resource", "Ghostly": "resource", "Manic": "resource", "Stable": "resource",
    "Static": "resource", "Flow": "resource",

    # generic stat / affix terms
    "Crit Chance": "critical", "Critical Chance": "critical",
    "Crit Multi": "critical", "Critical Multiplier": "critical",
    "Crit Damage": "critical", "Critical Damage": "critical",
    "Damage Reduction": "resistance", "Resistance": "resistance",
    "Lifesteal": "lifesteal", "Life Leech": "lifesteal",
    "HP Regen": "regen", "Regen": "regen", "Regeneration": "regen",
    "Shield": "buff",

    # core stats
    "Health": "health", "HP": "health", "Stamina": "stamina",
    "Armour Rating": "armour", "Armour": "armour", "Evasion": "evasion",
    "Energy Shield": "energy_shield",

    # damage types
    "Physical": "physical", "Fire": "fire", "Cold": "cold", "Lightning": "lightning",
    "Dark": "dark", "Holy": "holy", "Arcane": "arcane",
    "Earth": "earth", "Chaos": "chaos", "Psychic": "psychic", "Ethereal": "ethereal",

    # umbrella resistance categories
    "Divine": "divine", "Otherworldly": "otherworld", "Otherworld": "otherworld",
    "Elemental": "elemental",

    # shapeshift forms
    "Human": "human", "Beast": "beast",

    # status effects
    "Bleed": "dot", "Burn": "dot", "Poison": "dot", "Curse": "dot",
    "Stun": "cc", "Freeze": "cc",
    "Chill": "debuff", "Slow": "debuff", "Blind": "debuff", "Shock": "debuff", "Vulnerable": "debuff", "Weaken": "debuff", "Daze": "debuff",
    "Exposed": "exposure", "Elemental Exposure": "exposure", "Divine Exposure": "exposure", "Physical Exposure": "exposure", "Otherworld Exposure": "exposure",
    "Shield Generation": "buff", "Haste": "buff", "Might": "buff", "Stoneskin": "buff", "First Strike": "buff",

    # Cultist ascendancy mechanics
    "Shadow": "asc_umbralist",
    "Corruption": "asc_harbinger",
    "Omen": "asc_doomsayer", "Heresy": "asc_doomsayer",
    "Elevated": "asc_ritualist", "Devotion": "asc_ritualist", "Faithless": "asc_ritualist",
    "Volatility": "asc_anarchist", "Discharge": "asc_anarchist",
    "Ruin": "asc_desecrator", "Tainted": "asc_desecrator", "Desecrated": "asc_desecrator",

    # Paladin ascendancy mechanics
    "Zealotry": "asc_zealot",
    "Bulwark": "asc_guardian",
    "Justice": "asc_justicar",
    "Valour": "asc_crusader",
    "Blessing": "asc_inquisitor",

    # Wanderer ascendancy mechanics
    "Fracture": "asc_fractured",
    "Warped": "asc_warper",
    "Torture": "asc_mindbreaker",

    # Spectre ascendancy mechanics
    "Execute": "asc_reaper", "Executing": "asc_reaper",
    "Phased": "asc_phantasm", "Shifting": "asc_phantasm",
    "Intangible": "asc_revenant",

    # Wretch ascendancy mechanics
    "Blood Scent": "asc_plaguebearer",
    "Necrosis": "asc_necrose", "Rot": "asc_necrose",

    # Tempest ascendancy mechanics
    "Unleash": "class_tempest",
    "Positive": "asc_alternator", "Negative": "asc_alternator",

    # Marauder ascendancy mechanics
    "Echo": "class_marauder", "Siphon": "class_marauder", "Siphoned": "class_marauder",
    "Crush": "asc_colossus",
    "Deferred": "asc_dreadnought",
    "Shame": "asc_sovereign",
    "Empowerment": "asc_harrower",
    "Marked": "asc_butcher", "Slaughter": "asc_butcher", "Carved": "asc_butcher",

    # Warrior ascendancy mechanics
    "Fortify": "asc_juggernaut", "Bastion": "asc_juggernaut",
    "Annihilation": "asc_annihilist",
}

# matches an opening or closing rich markup tag, e.g. "[gold1 bold]" or "[/health]"
_TAG_RE = re.compile(r"\[/?[^\[\]]*\]")

def _buildKeywordPattern() -> "re.Pattern":
    escaped = [re.escape(k) for k in sorted(KEYWORDS, key=len, reverse=True)]
    # boundaries are "not a letter/digit" rather than \b, so keywords match against
    # whitespace or punctuation on either side but not when glued inside another word
    # (e.g. "Shield" in "Shielded" is rejected, "Shield," and "Shield-Breaker" are matched)
    return re.compile(r"(?<![A-Za-z0-9])(" + "|".join(escaped) + r")(?![A-Za-z0-9])")

_KEYWORD_RE = _buildKeywordPattern()

def _highlightPlainSegment(segment: str) -> str:
    def _wrap(match: "re.Match") -> str:
        keyword = match.group(0)
        style = KEYWORDS[keyword]
        return f"[{style}]{keyword}[/{style}]"
    return _KEYWORD_RE.sub(_wrap, segment)

def highlightKeywords(text: str) -> str:
    """Wraps known keyword text in its theme style. Text already inside an
    existing rich markup tag (manual colouring) is left untouched, so this is
    safe to run over text that's already partially styled."""
    pieces = []
    depth = 0
    lastEnd = 0
    for tagMatch in _TAG_RE.finditer(text):
        segment = text[lastEnd:tagMatch.start()]
        pieces.append(_highlightPlainSegment(segment) if depth == 0 else segment)
        tag = tagMatch.group(0)
        pieces.append(tag)
        depth = max(0, depth - 1) if tag.startswith('[/') else depth + 1
        lastEnd = tagMatch.end()
    tail = text[lastEnd:]
    pieces.append(_highlightPlainSegment(tail) if depth == 0 else tail)
    return ''.join(pieces)

class HighlightingConsole(Console):
    """Console that automatically runs any printed text through highlightKeywords,
    so keyword colouring no longer has to be typed out by hand at every call site."""
    def print(self, *args, **kwargs):
        args = tuple(highlightKeywords(a) if isinstance(a, str) else a for a in args)
        super().print(*args, **kwargs)

console = HighlightingConsole(theme=KORUS_THEME, markup=True)

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

class ReturnToMainMenu(Exception):
    """Raised to unwind out of any nested menu, all the way back to the main game menu."""
    pass

class GoToSaveMenu(Exception):
    """Raised to unwind out of any nested menu, all the way back to the save menu."""
    pass

GLOBAL_MENU_COMMAND = "menu"
GLOBAL_SAVE_COMMAND = "save"

def checkGlobalCommand(choice: str):
    """Raises ReturnToMainMenu / GoToSaveMenu if the player typed a global navigation command."""
    normalised = choice.strip().lower()
    if normalised == GLOBAL_MENU_COMMAND:
        raise ReturnToMainMenu()
    elif normalised == GLOBAL_SAVE_COMMAND:
        raise GoToSaveMenu()

def formatRarity(text: str, rarity: str) -> str:
    colour = RARITY_COLOURS.get(rarity.lower(), 'white')
    return f"[{colour}]{text}[/{colour}]"

def formatDamageType(text: str, damageType: str) -> str:
    colour = DAMAGE_TYPE_COLOURS.get(damageType.lower(), "white")
    return f"[{colour}]{text}[/{colour}]"

def formatDamageValue(damage: int) -> str:
    if damage < 100:
        return 'orange1'
    elif damage < 250:
        return 'dark_orange'
    elif damage < 500:
        return 'orange_red1 bold'
    elif damage < 1000:
        return 'deep_pink2 bold'
    else:
        return 'red3 bold underline'

def formatEffectsSummary(effects: Dict) -> str:
    """Short human-readable summary of an ability's effects dict,
    e.g. 'curse, otherworld exposure (target); haste (self)'"""
    parts = []
    for side in ('target', 'self'):
        names = [name for name in effects.get(side, {}).keys() if name != 'spawn_consumable']
        if names:
            parts.append(f"{', '.join(n.replace('_', ' ') for n in names)} ({side})")
    return '; '.join(parts)

def _formatEffectMagnitude(params: Dict) -> str:
    """Pulls the meaningful numeric detail(s) out of a single effect's param dict,
    e.g. {'stacks': 2} -> '2 stacks', {'amount': 0.2, 'turns': 2} -> '20% for 2 turns'"""
    bits = []
    if 'stacks' in params:
        n = params['stacks']
        bits.append(f"{n} stack{'s' if n != 1 else ''}")
    if 'amount_percent' in params:
        pct = params['amount_percent']
        pct = pct * 100 if isinstance(pct, float) and abs(pct) <= 1 else pct
        bits.append(f"{pct:.0f}% Max HP" if pct == int(pct) else f"{pct}% Max HP")
    if 'amount_flat' in params:
        bits.append(f"{params['amount_flat']} flat")
    if 'amount' in params:
        amt = params['amount']
        bits.append(f"{amt*100:.0f}%" if isinstance(amt, float) and abs(amt) <= 1 else f"{amt}%")
    if 'speed' in params:
        bits.append(f"{'+' if params['speed'] >= 0 else ''}{params['speed']} Speed")
    if 'damage' in params:
        mult = params['damage']
        pct = int(round((mult - 1) * 100))
        bits.append(f"{'+' if pct >= 0 else ''}{pct}% Damage")
    if 'chance' in params and params['chance'] < 100:
        bits.append(f"{params['chance']}% chance")

    detail = ', '.join(bits)
    if 'turns' in params:
        n = params['turns']
        turnsStr = f"{n} turn{'s' if n != 1 else ''}"
        detail = f"{detail} for {turnsStr}" if detail else turnsStr
    return detail

def formatEffectsDetailed(effects: Dict) -> List[str]:
    """One line per effect with its actual numbers, e.g.
    ['Bleed: 2 stacks (target)', 'Haste: +10% Damage for 2 turns (self)']"""
    if effects:
        lines = []
        for side in ('target', 'self'):
            for name, params in effects.get(side, {}).items():
                if name == 'spawn_consumable':
                    continue
                label = name.replace('_', ' ').title()
                detail = _formatEffectMagnitude(params)
                lines.append(f"{label}: {detail} ({side})" if detail else f"{label} ({side})")
        return lines
    return []

def formatResourceGainDetailed(gains: Dict) -> List[str]:
    if gains:
        lines = []
        for name, value in gains.items():
            label = name.replace('_', ' ').title()
            lines.append(f"{label}: +{value}")
        return lines
    return []

def formatAbilityCost(resources: Dict, staminaCost: int) -> str:
    """Human-readable resource cost, e.g. '8 Health' or '6% Max Health' or '20 Mana'"""
    if resources or staminaCost:
        if not resources and staminaCost == 0:
            return "-"
        parts = []
        if staminaCost > 0:
            parts.append(f'[stamina]Stamina:[/stamina] {staminaCost}')
        if resources:
            for resource, amount in resources.items():
                label = resource.replace('_', ' ').title()
                if isinstance(amount, dict):
                    pct = amount.get('amount', 0)
                    pct = pct * 100 if abs(pct) <= 1 else pct
                    parts.append(f"{pct:.0f}% Max {label}")
                else:
                    if type(amount) is str:
                        amount = amount.title()
                    parts.append(f"{amount} {label}")
        return ', '.join(parts)
    return "-"

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
    
    bar = f"[{colour}]{'■' * filled}[/{colour}][dim]{'□' * empty}[/dim]"
    return f"{bar} [{current}/{maximum}]"

def createStaminaBar(current: int, maximum: int, width: int = 20) -> str:
    percentage = current / maximum if maximum > 0 else 0
    filled = int(width * percentage)
    empty = width - filled

    if percentage > 0.6:
        colour = "turquoise2"
    elif percentage > 0.3:
        colour = "dodger_blue1"
    else:
        colour = "deep_sky_blue4"

    bar = f"[{colour}]{'■' * filled}[/{colour}][dim]{'□' * empty}[/dim]"
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

def createInventoryTable(inventory: dict) -> Table:
    table = Table(title="Inventory", box=box.ROUNDED, show_header=True)
    table.add_column("Item", style="white")
    table.add_column("Quantity", justify="right", style="cyan")

    for item, quantity in sorted(inventory.items()):
        table.add_row(item, str(quantity))

    return table

def createEquipmentStoragePages(equipmentList: list, itemsPerColumn: int = 5) -> Dict[int, Table]:
    itemsPerPage = itemsPerColumn * 2
    pages: Dict[int, Table] = {}
    totalPages = max(1, (len(equipmentList) + itemsPerPage - 1) // itemsPerPage)

    for pageNum in range(1, totalPages + 1):
        startIdx = (pageNum - 1) * itemsPerPage
        pageItems = equipmentList[startIdx:startIdx + itemsPerPage]
        leftItems = pageItems[:itemsPerColumn]
        rightItems = pageItems[itemsPerColumn:]

        table = Table(box=box.ROUNDED, show_header=False, show_lines=True)
        table.add_column("#", style="cyan", justify="right", width=3)
        table.add_column("Item", ratio=1)
        table.add_column("#", style="cyan", justify="right", width=3)
        table.add_column("Item", ratio=1)

        for row in range(itemsPerColumn):
            leftNum = str(startIdx + row + 1) if row < len(leftItems) else ""
            leftItem = leftItems[row] if row < len(leftItems) else ""
            rightNum = str(startIdx + itemsPerColumn + row + 1) if row < len(rightItems) else ""
            rightItem = rightItems[row] if row < len(rightItems) else ""
            table.add_row(leftNum, leftItem, rightNum, rightItem)

        pages[pageNum] = table

    return pages

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
        if resource != 'description':
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
                resourceParts.append(f"{resource}: {minAmt}-{maxAmt} | Drop Chance = {int(chance*100)}%\n")
            col.append(f"[gold]" + ", ".join(resourceParts) + "[/gold]")

        equipment = enemy._lootTable.equipmentPool
        if equipment:
            col.append("[bold yellow]Equipment:[/bold yellow]")
            equipmentParts = []
            for equip, chance in equipment:
                equipmentParts.append(f"{equip.name} | Drop Chance = {int(chance*100)}%")
            col.append("[yellow]" + "\n".join(equipmentParts) + "[/yellow]")

        runes = enemy._lootTable.runeDrops
        if runes:
            from .runeDrops import getRuneObject
            col.append("[bold light_cyan3]Runes:[/bold light_cyan3]")
            runeParts = []
            for cat, runeType, dropChance in runes:
                runeObj = getRuneObject(cat, runeType)
                runeName = runeObj.name if runeObj else runeType
                runeParts.append(f"{runeName} | Drop Chance = {int(dropChance*100)}%")
            col.append("[light_cyan3]" + "\n".join(runeParts) + "[/light_cyan3]")

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
        col.append(f"[health]Health:[/health]  {healthBar}")
        if entity.energyShield > 0 and entity.maxEnergyShield > 0:
            col.append(f"[energy_shield]Energy Shield:[/energy_shield] {entity.energyShield}/{entity.maxEnergyShield}")
        if entity._shield > 0:
            col.append(f"[dim cyan]Shield:[/dim cyan] {entity._shield}")
        if isPlayer:
            if player.className not in ['Mage', 'Wretch']: # both manaless classes
                staminaBar = createStaminaBar(entity._stamina, entity._maxStamina, width)
                col.append(f'[stamina]Stamina:[/stamina] {staminaBar}')
            if player.className == 'Mage':
                manaBar = createStaminaBar(entity._mana, entity._maxMana, width) # mana uses same colours as stamina
                col.append(f'[arcane]Mana:[/arcane]    {manaBar}')
        col.append(f"[damage]DMG:[/damage] {entity._damage} [dim]({formatDamageType(entity._damageType, entity._damageType)})[/dim]")
        col.append(f"[speed]SPD:[/speed] {entity._speed if not isPlayer else f'{entity._speed:.2f}'}")

        if isPlayer:
            if player.className == 'Warrior':
                col.append(f"[class_warrior]Rage:[/class_warrior] {player._rage}/{player._maxRage}")
            elif player.className == 'Wanderer':
                col.append(f"[class_wanderer]Lost Active:[/class_wanderer] {player.lostTrigger}")
            elif player.className == 'Paladin':
                col.append(f"[class_paladin]Favour:[/class_paladin] {player.favour}/{player.maxFavour}")
            elif player.className == 'Cultist':
                col.append(f"[class_cultist]Insanity:[/class_cultist] {player.insanity}")
        else:
            if entity.tortureStacks > 0:
                col.append(f"Torture Stacks: {entity.tortureStacks}")
            if entity.hauntedStacks > 0:
                col.append(f"Haunted Stacks: {entity.hauntedStacks}")
            if entity.phasedTurns > 0:
                col.append("Phased")
            if entity.cursedTurns > 0:
                col.append("Cursed")
            if entity.earthboundTurns > 0:
                col.append("Earthbound")
            if entity.corruption > 0:
                col.append(f"Corruption: {entity.corruption}")
            if entity.ruin > 0:
                col.append(f"Ruin: {entity.ruin}")
            if entity.bloodSpike > 0:
                executeHp = int(entity._maxHealth * 0.02 * entity.bloodSpike)
                col.append(f"Blood Spikes: {entity.bloodSpike} (Execute at {executeHp} HP)")
            if entity.necrosis > 0:
                col.append(f"Necrosis Stacks: {entity.necrosis}")
            if entity.crush > 0:
                col.append(f"Crush Stacks: {entity.crush}")
            if entity.shameTurns > 0:
                col.append(f"Shamed for {entity.shameTurns} turn{'s' if entity.shameTurns > 1 else ''}")
            if entity.marked:
                col.append(f"Marked")
            if entity.carved > 0:
                col.append(f"Carved Stacks: {entity.carved}")

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

def createAbilityTables(abilities: dict, playerDamageType: str) -> Table:
    table = Table(show_header=True, header_style="bold cyan", box=box.ROUNDED, padding=(0, 1), show_lines=True)
    table.add_column("#", style="dim", width=2)
    table.add_column("Ability", style="cyan")
    table.add_column("Base DMG", style="damage", justify="right")
    table.add_column("Scaling", justify="right")
    table.add_column("Type")
    table.add_column("Heal", justify="right")
    table.add_column("CD", style="yellow", justify="center")
    table.add_column("Cost", style="dim")
    table.add_column("Resource Gain", style="green")
    table.add_column("Effects", style="buff")
    table.add_column("Targets", style="dim red", justify="center")

    for j, (name, ability) in enumerate(abilities.items(), 1):
        cdText = str(ability.cooldown) if ability.cooldown > 0 else "✓"
        cdStyle = "red" if ability.cooldown > 0 else "green"

        damageStr = str(ability.baseDamage) if ability.baseDamage else "-"
        scalingStr = f"{ability.damageScaling*100:.0f}%" if ability.damageScaling else "-"
        dmgTypeFormatted = formatDamageType(ability.damageType, ability.damageType) if ability.damageType else formatDamageType(playerDamageType, playerDamageType)
        healStr = f"{ability.healBase}+{ability.healPercent*100:.0f}%" if (ability.healBase or ability.healPercent) else "-"
        costStr = formatAbilityCost(ability.resources.get('required'), ability.staminaCost)
        gainLines = formatResourceGainDetailed(ability.resources.get('gain'))
        gainText = "\n".join(gainLines) if gainLines else "-"
        effectsLines = formatEffectsDetailed(ability.effects)
        effectsText = "\n".join(effectsLines) if effectsLines else "-"
        targets = ability.targets if type(ability.targets) is int else ability.targets.title()

        table.add_row(
            str(j),
            name,
            damageStr,
            scalingStr,
            dmgTypeFormatted,
            healStr,
            f"[{cdStyle}]{cdText}[/{cdStyle}]",
            costStr,
            gainText,
            effectsText,
            str(targets)
        )

    return table

...