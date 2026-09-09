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
from typing import List, Dict, Optional, Callable, Iterable

# custom theme for game
KORUS_THEME = Theme({
    "common": "white",
    "uncommon": "green",
    "rare": "blue",
    "epic": "magenta",
    "legendary": "gold1 bold",
    "mythic": "deep_pink3 bold",
    "blank": "thistle1 bold underline",

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
    "ethereal": "grey70",

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
    "multihit": "turquoise4",
    "durability": "wheat4",
    "loot": "light_goldenrod2",
    "entropy": "red3 bold",

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

    "wanderer_radiance": "light_goldenrod1 bold underline",
    "wanderer_devastation": "dark_magenta bold underline",
    "wanderer_transcendence": "bright_white bold underline",
    "wanderer_harmony": "light_salmon1 bold underline",

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
    "asc_dervish": "sky_blue2 bold",
    "asc_ravager": "dark_orange bold",
    "asc_archon": "yellow1 bold",
    "asc_mirage": "medium_purple1 bold",

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
    "asc_butcher": "light_steel_blue1 bold",

    # Mage ascendancy family
    "asc_calamity": "dark_red bold",
    "asc_arcanist": "purple3 bold",
    "asc_hierophant": "light_goldenrod1 bold",
    "asc_empyrean": "deep_sky_blue1 bold",
    "asc_unmaker": "grey30 bold",

    # Fighter ascendancy family
    "asc_dissenter": "red1 bold",
    "asc_arbiter": "sky_blue3 bold",
    "asc_transgressor": "orchid2 bold",
    "asc_triarch": "grey54 bold",
    "asc_autarch": "gold3 bold",

    # Fighter stance thresholds
    "threshold_complacent": "grey50 bold",
    "threshold_neutral": "grey70 bold",
    "threshold_trained": "dodger_blue2 bold",
    "threshold_dedicated": "dark_orange bold",
    "threshold_allin": "red1 bold",

    # Druid ascendancy family
    "asc_heartwood": "dark_green bold",
    "asc_skinwalker": "orange_red1 bold",
    "asc_confluence": "sea_green2 bold",
    "asc_wellspring": "gold1 bold",
    "asc_numen": "grey58 bold"
})

# -- keyword highlighting: maps literal keyword text to a theme style key.
KEYWORDS: Dict[str, str] = {
    # class resources / mechanics
    "Insanity": "resource", "Rage": "resource", "Fury": "resource",
    "Combo": "resource", "Verdance": "resource", "Mastery": "resource",
    "Favour": "resource", "Prowess": "resource", "Momentum": "resource",
    "Insight": "resource", "Mana": "resource", "Blood Spike": "resource",
    "Lost": "resource", "Ghostly": "resource", "Manic": "resource", "Stable": "resource",
    "Static": "resource", "Flow": "resource", "Vengeance": "resource",
    "Hope": "resource", "Hopeless": "resource",
    "Aggression": "resource", "Discipline": "resource",

    # generic stat / affix terms
    "Crit Chance": "critical", "Critical Chance": "critical", "Critically Hit": "critical",
    "Crit Multi": "critical", "Critical Multiplier": "critical",
    "Crit Damage": "critical", "Critical Damage": "critical",
    "Damage Reduction": "resistance", "Resistance": "resistance",
    "Lifesteal": "lifesteal", "Life Leech": "lifesteal",
    "HP Regen": "regen", "Hp Regen": "regen", "Regen": "regen", "Regeneration": "regen",
    "Shield": "buff",
    "Damage": "damage", "Overkill": "damage", "Speed": "speed",
    "Gold": "gold", "XP": "xp", "Xp": "xp", "Experience": "xp",
    "Healing Magnitude": "heal", "Healing": "heal", "Heal": "heal",

    "Chance To Multihit": "multihit", "Added Multihits": "multihit", "Multihit": "multihit",
    "Ailment Avoidance": "resistance", "Stun Avoidance": "cc", "Defenses": "resistance",
    "Durability": "durability",
    "Item Quantity": "loot", "Item Rarity": "loot", "Enemy Quantity": "loot",
    "Entropy": "entropy",
    "Cleave": "damage", "Thorns": "damage",

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
    "Radiance": "wanderer_radiance", "Devastation": "wanderer_devastation",
    "Transcendence": "wanderer_transcendence", "Harmony": "wanderer_harmony",
    "Fracture": "asc_fractured",
    "Warped": "asc_warper",
    "Torture": "asc_mindbreaker",
    "Hunted": "asc_abyssal",

    # Spectre ascendancy mechanics
    "Execute": "asc_reaper", "Executing": "asc_reaper",
    "Phased": "asc_phantasm", "Shifting": "asc_phantasm",
    "Intangible": "asc_revenant", "Intangibility": "asc_revenant",
    "Fading": "asc_wraith",

    # Wretch ascendancy mechanics
    "Blood Scent": "asc_plaguebearer",
    "Necrosis": "asc_necrose", "Rot": "asc_necrose",
    "Skeleton": "asc_necromancer",

    # Tempest ascendancy mechanics
    "Unleash": "class_tempest",
    "Positive": "asc_alternator", "Negative": "asc_alternator",
    "Fleeting": "asc_dervish",
    "Spark": "asc_archon",
    "Flurry": "asc_ravager", "Relentless": "asc_ravager",

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

    # Fighter stance thresholds
    "Complacent": "threshold_complacent",
    "Neutral": "threshold_neutral",
    "Trained": "threshold_trained",
    "Dedicated": "threshold_dedicated",
    "All-In": "threshold_allin",

    # Fighter ascendancy mechanics
    "Stance": "class_fighter",
    "Impatience": "asc_dissenter",
    "Balance": "asc_arbiter",
    "Pact": "asc_autarch",

    # Mage ascendancy mechanics
    "Archmage": "class_mage", "Adaptation": "class_mage",
    "Relinquish": "asc_calamity", "Relinquished": "asc_calamity", "Calamity": "asc_calamity",
    "Prophetic": "asc_hierophant",
    "Precision": "asc_unmaker",

    # Druid ascendancy mechanics
    "Root": "asc_heartwood", "Rootbound": "asc_heartwood",
    "Elderbark": "asc_heartwood", "Loam": "asc_heartwood",
    "Ferocity": "asc_skinwalker", "Instinct": "asc_skinwalker",
    "Flux": "asc_confluence",
    "Blooming": "asc_wellspring",
}

# matches an opening or closing rich markup tag, e.g. "[gold1 bold]" or "[/health]"
_TAG_RE = re.compile(r"\[/?[^\[\]]*\]")

def _buildKeywordPattern() -> "re.Pattern":
    escaped = [re.escape(k) for k in sorted(KEYWORDS, key=len, reverse=True)]
    return re.compile(r"(?<![A-Za-z0-9])(" + "|".join(escaped) + r")(?![A-Za-z0-9])")

_KEYWORD_RE = _buildKeywordPattern()

def _highlightPlainSegment(segment: str) -> str:
    def _wrap(match: "re.Match") -> str:
        keyword = match.group(0)
        style = KEYWORDS[keyword]
        return f"[{style}]{keyword}[/{style}]"
    return _KEYWORD_RE.sub(_wrap, segment)

def highlightKeywords(text: str) -> str:
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

def stepPage(currentPage: int, totalPages: int, choice: str) -> Optional[int]:
    """If choice is a page-navigation command ('n'/'p'), returns the new page number
    (wrapping around). Returns None if choice wasn't a navigation command."""
    if totalPages <= 1:
        return None
    normalised = choice.strip().lower()
    if normalised == 'n':
        return currentPage % totalPages + 1
    if normalised == 'p':
        return (currentPage - 2) % totalPages + 1
    return None

def selectFromNumberedList(items: List, promptText: str, render: Optional[Callable] = None,
                            skip: Iterable[int] = frozenset()) -> Optional[int]:
    """Prints a 1-indexed list (skipping any 0-based indices in `skip`), reads a choice,
    and returns a valid 0-based index. Returns None if the player cancelled with '0' or
    entered something invalid (a warning is already shown in that case)."""
    skip = set(skip)
    for i, item in enumerate(items, 1):
        if i - 1 in skip:
            continue
        if render:
            render(i, item)
        else:
            console.print(f"[cyan]{i}.[/cyan] {item}")

    choice = console.input(f"\n[cyan]{promptText}[/cyan]\n> ").strip()
    if choice == '0':
        return None
    try:
        index = int(choice) - 1
    except ValueError:
        printWarning("Invalid input!")
        pause()
        return None
    if not (0 <= index < len(items)) or index in skip:
        printWarning("Invalid choice!")
        pause()
        return None
    return index

def formatRarity(text: str, rarity: str) -> str:
    colour = RARITY_COLOURS.get(rarity.lower(), 'white')
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

def formatDamageBreakdown(baseDamage: int, log: List, finalDamage: int, damageType: str) -> List[str]:
    dmgTypeFormatted = f"[{damageType}]{damageType.title()}[/{damageType}]"
    lines = [f"[damage]Dealt {baseDamage} {dmgTypeFormatted} Damage.[/damage]"]
    for reason, flat, percent in log:
        if percent:
            verb = "Increased" if percent > 0 else "Reduced"
            lines.append(f"  [dim]- {abs(percent) * 100:.0f}% {verb} Damage from {reason}[/dim]")
        if flat:
            sign = "+" if flat > 0 else "-"
            lines.append(f"  [dim]- {sign}{abs(flat)} Damage from {reason}[/dim]")
    return lines

def formatEffectsSummary(effects: Dict) -> str:
    parts = []
    for side in ('target', 'self'):
        names = [name for name in effects.get(side, {}).keys() if name != 'spawn_consumable']
        if names:
            parts.append(f"{', '.join(n.replace('_', ' ') for n in names)} ({side})")
    return '; '.join(parts)

def _formatEffectMagnitude(params: Dict) -> str:
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

def createEquipmentStoragePages(equipmentList: list, itemsPerColumn: int = 5, render: Optional[Callable] = None) -> Dict[int, Table]:
    """Paginates `equipmentList` into a 2-column Rich Table per page, numbered globally
    across pages. Each item is placed into its cell as-is unless `render` is given, in
    which case the cell content is `render(item)` instead (e.g. to prefix a location
    label onto an (label, Equipment) tuple)."""
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
            if render:
                leftItem = render(leftItem) if leftItem != "" else ""
                rightItem = render(rightItem) if rightItem != "" else ""
            table.add_row(leftNum, leftItem, rightNum, rightItem)

        pages[pageNum] = table

    return pages

def displayCombatStatus(player, enemies: list):
    playerHP = createHealthBar(player._health, player._maxHealth, width=15)
    playerInfo = f"[bold cyan]{player._name}[/bold cyan] (Lv. {player._level})\n"
    playerInfo += f"HP: {playerHP}\n"
    playerInfo += f"DMG: [damage]{player._damage}[/damage] | "
    playerInfo += f"Type: [{player._damageType}]{player._damageType.title()}[/{player._damageType}]"

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
    [health]HP: {player._maxHealth}[/health]
    [stamina]Stamina: {player._maxStamina}[/stamina]
    [damage]DMG: {player._damage}[/damage]
    [speed]SPD: {player._speed:.2f}[/speed]
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
        col.append(f"[damage]DMG:[/damage] {enemy._damage} | Type: [{enemy._damageType}]{enemy._damageType.title()}[/{enemy._damageType}]")
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

def formatPlayerMechanics(player, col: list) -> list:
    if player.className == 'Warrior':
        col.append(f"[class_warrior]Rage:[/class_warrior] {player._rage}/{player.maxRage}")
        if player._ascendancy == 'Warlord':
            col.append(f"[asc_warlord]Fury:[/asc_warlord] {player._fury}/{player._maxFury}")
        elif player._ascendancy == 'Juggernaut':
            col.append(f"[asc_juggernaut]Fortify:[/asc_juggernaut] {player._fortify}/{player._maxFortify}")
        elif player._ascendancy == 'Annihilist':
            col.append(f"[asc_annihilist]Annihilation:[/asc_annihilist] {player.annihilation}")

    elif player.className == 'Wanderer':
        wandererStateStr = "Radiance" if player.radiance else "Devastation" if player.devastation else ""
        if player._ascendancy == 'Manifestation' and player.transcendence:
            wandererStateStr = "Transcendence"
        elif player._ascendancy == 'Weaver' and player.harmony:
            wandererStateStr = "Harmony"
        col.append(f"[resource]Hope:[/resource] {player.hope}/{player.maxHope} | [resource]Hopeless:[/resource] {player.hopeless}/{player.maxHopeless}")
        if wandererStateStr != "":
            col.append(f"[class_wanderer]State:[/class_wanderer] {highlightKeywords(wandererStateStr)}")
        col.append(f"[resource]Lost:[/resource] [bold]{'Yes' if player.lostTrigger else 'No'}[/bold]")
        if player._ascendancy == 'Fractured':
            col.append(f"[asc_fractured]Fracture:[/asc_fractured] {player.fracture}/5")
        elif player._ascendancy == 'Abyssal':
            col.append(f"[asc_abyssal]Hunted:[/asc_abyssal] {player.hunted}/3")
        elif player._ascendancy == 'Warper':
            col.append(f"[asc_warper]Warped:[/asc_warper] [bold]{'Yes' if player.warped else 'No'}[/bold]")

    elif player.className == 'Paladin':
        col.append(f"[class_paladin]Favour:[/class_paladin] {player.favour}/{player.maxFavour}")
        if player._ascendancy == 'Zealot':
            col.append(f"[asc_zealot]Zealotry:[/asc_zealot] {player.zealotry}")
        elif player._ascendancy == 'Guardian':
            col.append(f"[asc_guardian]Bulwark:[/asc_guardian] {player.bulwark}/5")
        elif player._ascendancy == 'Justicar':
            if player.justiceTurns > 0:
                col.append(f"[asc_justicar]Justice Turns Remaining:[/asc_justicar] {player.justiceTurns}")
        elif player._ascendancy == 'Crusader':
            col.append(f"[asc_crusader]Valour:[/asc_crusader] {player.valour}/10")
        elif player._ascendancy == 'Inquisitor':
            if player.blessedTurns > 0:
                col.append(f"[asc_inquisitor]Blessed Turns Remaining:[/asc_inquisitor] {player.blessedTurns}")

    elif player.className == 'Cultist':
        col.append(f"[class_cultist]Insanity:[/class_cultist] {player.insanity}")
        if player._ascendancy == 'Umbralist':
            col.append(f"[asc_umbralist]Shadow:[/asc_umbralist] {player.shadow}/10")
        elif player._ascendancy == 'Doomsayer':
            col.append(f"[asc_doomsayer]Omen:[/asc_doomsayer] {player.omen}/5 | [asc_doomsayer]Heresy:[/asc_doomsayer] {player.heresy}/10")
        elif player._ascendancy == 'Ritualist':
            col.append(f"[asc_ritualist]Devotion:[/asc_ritualist] {player.devotion}/5 | [asc_ritualist]Faithless:[/asc_ritualist] {player.faithless}/10")
        elif player._ascendancy == 'Anarchist':
            col.append(f"[asc_anarchist]Volatility:[/asc_anarchist] {player.volatility}/{player.maxVolatility}")

    elif player.className == 'Spectre':
        col.append(f"[class_spectre]Vengeance:[/class_spectre] {player.vengeance}/{player.maxVengeance}")
        if player._ascendancy == 'Wraith':
            col.append(f"[asc_wraith]Fading:[/asc_wraith] {player.wraithFading}/300")
        elif player._ascendancy == 'Reaper':
            if player.reaperDamage > 0:
                col.append(f"[asc_reaper]Bonus Damage from Executes:[/asc_reaper] +{player.reaperDamage}")
        elif player._ascendancy == 'Phantasm':
            if player.shiftingTurns > 0:
                col.append(f"[asc_phantasm]Shifting Turns Remaining:[/asc_phantasm] {player.shiftingTurns}")
        elif player._ascendancy == 'Revenant':
            col.append(f"[asc_revenant]Intangibility Used:[/asc_revenant] [bold]{'Yes' if player.intangibilityUsed else 'No'}[/bold]")
            if player.intangibleTurns > 0:
                col.append(f"[asc_revenant underline]Currently Intangible[/asc_revenant underline]")
        elif player._ascendancy == 'Lich':
            col.append(f"[asc_lich]Empowered (Energy Shield > 50%):[/asc_lich] [bold]{'Yes' if player.lichBuffsActive else 'No'}[/bold]")

    elif player.className == 'Marauder':
        if player._ascendancy != 'Harrower':
            col.append(f"[class_marauder]Siphoned Damage:[/class_marauder] {player.siphonedDamage}")
        else:
            col.append(f"[class_marauder]Siphoned Speed:[/class_marauder] {player.harrowerSiphonedSpeed:.2f}")
            if player.harrowerEmpowered:
                col.append(f"[asc_harrower underline]Empowered[/asc_harrower underline]")
        if player._ascendancy == 'Butcher':
            col.append(f"[asc_butcher]Slaughter:[/asc_butcher] {player.butcherSlaughter}/5")

    elif player.className == 'Tempest':
        col.append(f"[class_tempest]Static:[/class_tempest] {player.static}/10 | [class_tempest]Flow:[/class_tempest] {player.flow}/10")
        if player._ascendancy == 'Alternator':
            col.append(f"[asc_alternator]Positive:[/asc_alternator] {player.alternatorPositive}/10 | [asc_alternator]Negative:[/asc_alternator] {player.alternatorNegative}/10")
            col.append(f"[asc_alternator]Speed Bonuses Flipped:[/asc_alternator] [bold]{'Yes' if player.alternatorFlip else 'No'}")
        elif player._ascendancy == 'Dervish':
            col.append(f"[asc_dervish]Fleeting:[/asc_dervish] {player.dervishFleeting}/10")
        elif player._ascendancy == 'Ravager':
            col.append(f"[asc_ravager]Flurry:[/asc_ravager] {player.ravagerFlurry}/5 | [asc_ravager]Relentless:[/asc_ravager] {player.ravagerRelentless}/3")
        elif player._ascendancy == 'Archon':
            col.append(f"[asc_archon]Current:[/asc_archon] {player.archonCurrent}/10 | [asc_archon]Spark:[/asc_archon] {player.archonSpark}/5")

    elif player.className == 'Mage':
        masteryCap = '' if player._ascendancy == 'Empyrean' else f"/{player.maxMastery}"
        col.append(f"[resource]Mastery:[/resource] {player.mastery}{masteryCap}")

        adaptations = []
        if player.fireAdaptation: adaptations.append('Fire')
        if player.coldAdaptation: adaptations.append('Cold')
        if player.earthAdaptation: adaptations.append('Earth')
        if player.lightningAdaptation: adaptations.append('Lightning')
        if player._ascendancy == 'Hierophant':
            if player.holyAdaptation: adaptations.append('Holy')
            if player.darkAdaptation: adaptations.append('Dark')
            if player.arcaneAdaptation: adaptations.append('Arcane')
        if adaptations:
            col.append(f"[class_mage]Adaptations:[/class_mage] {', '.join(adaptations)}")
        if player.archmage:
            col.append(f"[class_mage underline]Archmage[/class_mage underline]")

        if player._ascendancy == 'Calamity':
            relinquished = []
            if player.relinquishedFire: relinquished.append('Fire')
            if player.relinquishedCold: relinquished.append('Cold')
            if player.relinquishedEarth: relinquished.append('Earth')
            if player.relinquishedLightning: relinquished.append('Lightning')
            if relinquished:
                col.append(f"[asc_calamity]Relinquished:[/asc_calamity] {', '.join(relinquished)}")
            if player.calamity:
                col.append(f"[asc_calamity underline]Calamity[/asc_calamity underline]")
        elif player._ascendancy == 'Hierophant':
            if player.prophetic:
                col.append(f"[asc_hierophant underline]Prophetic[/asc_hierophant underline]")
        elif player._ascendancy == 'Unmaker':
            col.append(f"[asc_unmaker]Precision:[/asc_unmaker] {player.unmakerPrecision}/10")

    elif player.className == 'Fighter':
        col.append(f"[class_fighter]Aggression:[/class_fighter] {player.aggression} ({player.currentAggressionTreshold.value.title()})\n[class_fighter]Discipline:[/class_fighter] {player.discipline} ({player.currentDisciplineThreshold.value.title()})")
        if player.stanceCap != 100:
            col.append(f"[class_fighter]Stance Cap:[/class_fighter] {player.stanceCap}")

        if player._ascendancy == 'Dissenter':
            col.append(f"[asc_dissenter]Impatience:[/asc_dissenter] {player.impatience}")
        elif player._ascendancy == 'Arbiter':
            col.append(f"[asc_arbiter]Balance:[/asc_arbiter] {player.balance}")
        elif player._ascendancy == 'Transgressor':
            if player.transgressorSyncTier:
                col.append(f"[asc_transgressor underline]Dual-Stance Synergy Active[/asc_transgressor underline]")
        elif player._ascendancy == 'Autarch':
            if player.autarchPact:
                col.append(f"[asc_autarch]Pact:[/asc_autarch] {player.autarchPact.title()}")

    return col

def formatEntityMechanics(entity, col: list) -> list:
    if entity.tortureStacks > 0:
        col.append(f"[asc_mindbreaker]Torture:[/asc_mindbreaker] {entity.tortureStacks}")
    if entity.phasedTurns > 0:
        col.append("[asc_phantasm]Phased[/asc_phantasm]")
    if entity.cursedTurns > 0:
        col.append("[dot]Cursed[/dot]")
    if entity.earthboundTurns > 0:
        col.append("[debuff]Earthbound[/debuff]")
    if entity.corruption > 0:
        col.append(f"[asc_harbinger]Corruption:[/asc_harbinger] {entity.corruption}")
    if entity.ruin > 0:
        col.append(f"[asc_desecrator]Ruin:[/asc_desecrator] {entity.ruin}")
    if entity.bloodSpike > 0:
        executeHp = int(entity._maxHealth * 0.02 * entity.bloodSpike)
        col.append(f"[resource]Blood Spikes:[/resource] {entity.bloodSpike} (Execute at {executeHp} HP)")
    if entity.necrosis > 0:
        col.append(f"[asc_necrose]Necrosis:[/asc_necrose] {entity.necrosis}")
    if entity.crush > 0:
        col.append(f"[asc_colossus]Crush:[/asc_colossus] {entity.crush}")
    if entity.shameTurns > 0:
        col.append(f"[asc_sovereign]Shamed[/asc_sovereign] for {entity.shameTurns} turn{'s' if entity.shameTurns > 1 else ''}")
    if entity.marked:
        col.append(f"[asc_butcher underline]Marked[/asc_butcher underline]")
    if entity.carved > 0:
        col.append(f"[asc_butcher]Carved:[/asc_butcher] {entity.carved}")

    return col

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
        defStr = ""
        if entity.armour > 0 and entity.evasion > 0:
            defStr = f"[armour]Armour:[/armour] {entity.armour} | [evasion]Evasion:[/evasion] {entity.evasion}"
        else:
            if entity.armour > 0:
                defStr = f"[armour]Armour:[/armour] {entity.armour}"
            if entity.evasion > 0:
                defStr = f"[evasion]Evasion:[/evasion] {entity.evasion}"
        if defStr != "":
            col.append(defStr)
        blockChance = entity._stats['Bonuses'].get('chance_to_block', 0)
        if blockChance > 0:
            col.append(f"[cyan]Chance to Block:[/cyan] {blockChance}%")
        if entity._shield > 0:
            col.append(f"[dim cyan]Shield:[/dim cyan] {entity._shield}")
        if isPlayer:
            if player.className not in ['Mage', 'Wretch']: # both manaless classes
                staminaBar = createStaminaBar(entity._stamina, entity._maxStamina, width)
                col.append(f'[stamina]Stamina:[/stamina] {staminaBar}')
            if player.className == 'Mage':
                manaBar = createStaminaBar(entity._mana, entity._maxMana, width) # mana uses same colours as stamina
                col.append(f'[arcane]Mana:[/arcane]    {manaBar}')
        col.append(f"[damage]DMG:[/damage] {entity._damage} | Type: [{entity._damageType}]{entity._damageType.title()}[/{entity._damageType}]")
        col.append(f"[speed]SPD:[/speed] {entity._speed if not isPlayer else f'{entity._speed:.2f}'}")

        if isPlayer:
            col = formatPlayerMechanics(entity, col)
        else:
            col= formatEntityMechanics(entity, col)

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
        dmgTypeFormatted = f"[{ability.damageType}]{ability.damageType.title()}[/{ability.damageType}]" if ability.damageType else f"[{playerDamageType}]{playerDamageType.title()}[/{playerDamageType}]"
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