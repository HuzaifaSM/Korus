from typing import List, Dict, Optional, Tuple
from .styles import (
    clearScreen, printHeader, console, printWarning, pause, checkGlobalCommand
)

HELP_TOPICS: List[Dict] = [
    # -- Combat -- #
    {
        "id": "core_stats",
        "category": ("Combat", "Core Stats"),
        "title": "Core Stats",
        "aliases": ["armour", "armor", "evasion", "energy shield", "speed",
                    "crit chance", "crit multi", "critical", "defenses"],
        "body": """
    [armour]Armour[/armour] reduces incoming damage: reduction = Armour / (Armour + 10x incoming damage), capped at 90%. Ignored entirely by Ethereal damage.

    [evasion]Evasion[/evasion] gives a chance to avoid a hit completely, capped at 75%. Ignored entirely by Psychic damage.

    [energy_shield]Energy Shield[/energy_shield] is an extra pool of "health" that absorbs damage before your real HP. Ignored entirely by Chaos damage.

    [speed]Speed[/speed] determines turn order - higher Speed acts earlier.

    [critical]Crit Chance[/critical] is your odds of landing a critical hit. [critical]Crit Multi[/critical] is how much extra damage that critical hit deals.
    """,
    },
    {
        "id": "combat_mechanics",
        "category": ("Combat", "Combat Mechanics"),
        "title": "Combat Mechanics",
        "aliases": ["lifesteal", "hp regen", "regen", "damage reduction", "resistance",
                    "multihit", "thorns", "cleave", "shield"],
        "body": """
    [lifesteal]Lifesteal[/lifesteal] heals you for a percentage of the damage you deal.

    [regen]HP Regen[/regen] heals a flat amount at the start of every turn.

    [resistance]Damage Reduction[/resistance] and [resistance]Resistance[/resistance] both mitigate incoming damage - Damage Reduction is a flat amount, Resistance is a percentage per damage type.

    [multihit]Multihit[/multihit] gives a chance for an attack to strike more than once - Chance to Multihit is the odds, Added Multihits is how many extra hits you get.

    [damage]Thorns[/damage] reflects flat damage back at whoever hits you. [damage]Cleave[/damage] refers to attacks that hit multiple enemies at once.

    [buff]Shield[/buff] is a temporary pool of extra "health" granted by certain buffs, separate from Energy Shield - it decays away once the buff granting it ends.
    """,
    },
    {
        "id": "damage_types",
        "category": ("Combat", "Damage Types"),
        "title": "Damage Types",
        "aliases": ["physical", "fire", "cold", "lightning", "dark", "holy", "arcane",
                    "earth", "chaos", "psychic", "ethereal", "elemental", "divine",
                    "otherworldly", "otherworld"],
        "body": """
    Every hit has a damage type, which is what your resistances (and the target's) are checked against:

    [physical]Physical[/physical], [fire]Fire[/fire], [cold]Cold[/cold], [lightning]Lightning[/lightning], [dark]Dark[/dark], [holy]Holy[/holy], [arcane]Arcane[/arcane], [earth]Earth[/earth], [chaos]Chaos[/chaos] (ignores Energy Shield), [psychic]Psychic[/psychic] (ignores Evasion), [ethereal]Ethereal[/ethereal] (ignores Armour, and can't be Blocked).

    Three umbrella categories group these for effects like Exposure: [elemental]Elemental[/elemental] (Fire/Cold/Lightning/Earth), [divine]Divine[/divine] (Holy/Dark/Arcane), and [otherworld]Otherworldly[/otherworld] (Chaos/Psychic/Ethereal).
    """,
    },
    {
        "id": "dots",
        "category": ("Combat", "Status Effects"),
        "title": "Damage over Time (DoTs)",
        "aliases": ["bleed", "burn", "poison", "curse", "dot", "dots"],
        "body": """
    DoTs deal damage at the start of each of your turns for a set number of turns, on top of a secondary effect:

    [dot]Bleed[/dot] - 3 turns. Also reduces the target's Speed for the duration.
    [dot]Burn[/dot] - 2 turns. Also lowers all of the target's resistances for the duration.
    [dot]Poison[/dot] - 3 turns. Also reduces the target's healing received for the duration.
    [dot]Curse[/dot] - 4 turns. Ignores resistances entirely - the hardest-hitting DoT.
    """,
    },
    {
        "id": "crowd_control",
        "category": ("Combat", "Status Effects"),
        "title": "Crowd Control (CC)",
        "aliases": ["stun", "freeze", "cc"],
        "body": """
    [cc]Stun[/cc] and [cc]Freeze[/cc] both prevent the target from acting on their next turn(s). Being hit by either grants a temporary boost to Stun Avoidance afterwards, so you can't be chain-CC'd indefinitely. Freeze also increases the crit damage the target takes while frozen.
    """,
    },
    {
        "id": "debuffs",
        "category": ("Combat", "Status Effects"),
        "title": "Debuffs",
        "aliases": ["chill", "slow", "daze", "blind", "shock", "vulnerable", "weaken"],
        "body": """
    [debuff]Chill[/debuff], [debuff]Slow[/debuff], and [debuff]Daze[/debuff] all reduce the target's Speed for a few turns (Daze also reduces their damage dealt).

    [debuff]Blind[/debuff] gives the target a chance to miss their attacks entirely.

    [debuff]Shock[/debuff] and [debuff]Vulnerable[/debuff] both increase the damage the target takes for a few turns.

    [debuff]Weaken[/debuff] reduces the damage the target deals for a few turns.
    """,
    },
    {
        "id": "exposure",
        "category": ("Combat", "Status Effects"),
        "title": "Exposure",
        "aliases": ["exposed", "exposure", "elemental exposure", "divine exposure",
                    "physical exposure", "otherworld exposure"],
        "body": """
    Exposure effects temporarily strip a target's resistances, making them take more damage from those damage types.

    [exposure]Exposed[/exposure] lowers all resistances at once. [exposure]Elemental Exposure[/exposure], [exposure]Divine Exposure[/exposure], [exposure]Physical Exposure[/exposure], and [exposure]Otherworld Exposure[/exposure] each target just one resistance family instead, usually for a larger amount.
    """,
    },
    {
        "id": "status_buffs",
        "category": ("Combat", "Status Effects"),
        "title": "Buffs",
        "aliases": ["haste", "stoneskin", "shield generation", "regeneration",
                    "might", "first strike"],
        "body": """
    [buff]Haste[/buff] grants bonus Speed and damage for its duration.

    [buff]Stoneskin[/buff] reduces a percentage of damage taken for its duration.

    [buff]Shield Generation[/buff] grants a temporary flat Shield.

    [buff]Regeneration[/buff] heals a percentage of Max HP every turn for its duration.

    [buff]Might[/buff] and [buff]First Strike[/buff] are rarer buffs that add flat bonus damage, usually paired with another effect on a specific ability.
    """,
    },
    {
        "id": "enemy_types",
        "category": ("Combat", "Enemy Types"),
        "title": "Enemy Classes, Subclasses & Rarity",
        "aliases": ["attacker", "support", "bruiser", "debilitator", "champion", "fanatic",
                    "healer", "standard bearer", "tank", "enemy rarity",
                    "common", "rare", "epic", "legendary"],
        "body": """
    Every enemy is either an [attacker]Attacker[/attacker] or a [support]Support[/support], and higher-rarity enemies can also roll a Subclass on top:

    Attacker subclasses - [bruiser]Bruiser[/bruiser] (mostly basic attacks, high base damage), [debilitator]Debilitator[/debilitator] (debuff-heavy), [champion]Champion[/champion] (smarter AI, buffs before big hits), [fanatic]Fanatic[/fanatic] (ability spam, no basic attacks).

    Support subclasses - [healer]Healer[/healer] (focuses on healing allies), [standard_bearer]Standard Bearer[/standard_bearer] (focuses on buffing allies), [tank]Tank[/tank] (taunts to force single-target attacks onto itself, high health).

    Enemy rarity (Common/Rare/Epic/Legendary) scales an enemy's stats, how many affixes it can roll, and how sharp its AI plays - rarer enemies play closer to optimally.
    """,
    },

    # -- Equipment & Items -- #
    {
        "id": "item_rarities",
        "category": ("Equipment & Items", "Item Rarities"),
        "title": "Item Rarities",
        "aliases": ["common", "uncommon", "rare", "epic", "legendary", "mythic", "blank"],
        "body": """
    Item rarity runs [common]Common[/common] -> [uncommon]Uncommon[/uncommon] -> [rare]Rare[/rare] -> [epic]Epic[/epic] -> [legendary]Legendary[/legendary] -> [mythic]Mythic[/mythic]/[blank]Blank[/blank], with higher rarities rolling more (and better) affixes.

    [mythic]Mythic[/mythic] and [blank]Blank[/blank] are equivalent top-tier rarities that only start appearing at item level 60+ - any roll that would produce one splits between the two.
    """,
    },
    {
        "id": "durability",
        "category": ("Equipment & Items", "Durability"),
        "title": "Durability",
        "aliases": ["durability", "repair"],
        "body": """
    Every piece of equipment has [durability]Durability[/durability], which chips down as you deal and take damage in combat. At 0 durability, an item stops contributing its stats until it's repaired - repairs are done at the Forge, using Fuel and resources scaled by the item's level and rarity.
    """,
    },
    {
        "id": "loot_modifiers",
        "category": ("Equipment & Items", "Loot Modifiers"),
        "title": "Loot Modifiers",
        "aliases": ["item quantity", "item rarity", "enemy quantity", "loot"],
        "body": """
    [loot]Item Quantity[/loot] increases how much loot drops. [loot]Item Rarity[/loot] skews dropped equipment toward higher rarities. [loot]Enemy Quantity[/loot] increases how many enemies you face at once - more enemies means a tougher fight, but more total loot.
    """,
    },
    {
        "id": "entropy",
        "category": ("Equipment & Items", "Crafting & Runes"),
        "title": "Entropy",
        "aliases": ["entropy", "entropy locked", "destabilised", "corrupted"],
        "body": """
    [entropy]Entropy[/entropy] is a corruption meter on each item, starting at 0. Applying runes adds Entropy; once an item's Entropy hits its cap, it becomes Entropy Locked and can no longer be modified by any rune. Higher-rarity items naturally resist more Entropy per application.
    """,
    },
    {
        "id": "rune_categories",
        "category": ("Equipment & Items", "Crafting & Runes"),
        "title": "Rune Categories",
        "aliases": ["chaos rune", "erasing rune", "growth rune", "randomiser rune",
                    "unique rune", "mastery rune", "rarity rune", "destabilisation rune",
                    "revealing rune", "manipulation rune", "quest rune"],
        "body": """
    Runes are applied at the Forge and fall into a few broad categories:

    [cyan]Growth[/cyan] runes add new affixes to empty slots. [cyan]Erasing[/cyan] runes remove affixes. [cyan]Chaos[/cyan] runes remove and add affixes together, rerolling part of an item at once.

    [cyan]Randomiser[/cyan] runes reroll an affix's tier, value, or type, or an item's base type. [cyan]Rarity[/cyan] runes push an item up a rarity tier. [cyan]Mastery[/cyan] runes raise an item's Mastery, a separate stat that scales its damage/defense independent of rarity.

    [cyan]Manipulation[/cyan] runes swap or rebalance affixes between slots. [cyan]Revealing[/cyan] runes let you preview a rune's result before committing to it (Foresight). [cyan]Destabilisation[/cyan] runes corrupt an item for a random, often powerful (but risky) outcome, and always leave it corrupted afterward - no further crafting possible.

    [cyan]Unique[/cyan] runes create fixed, pre-designed unique items. [cyan]Quest[/cyan] runes are special variants only ever obtainable from the Quest Board's shop.
    """,
    },

    # -- Camp -- #
    {
        "id": "camp_campfire",
        "category": ("Camp", "Campfire"),
        "title": "Campfire",
        "aliases": ["rest", "cook", "food", "supplies"],
        "body": """
    The Campfire automatically heals you a percentage of Max HP after every victory, scaling with its level. Its own resource, Supplies, can be spent to Rest (heal to full outside of combat) or, once upgraded, to Cook Food - single-use items that heal plus grant a random combat buff.
    """,
    },
    {
        "id": "camp_forge",
        "category": ("Camp", "Forge"),
        "title": "Forge",
        "aliases": ["craft", "repair", "fuse", "vaporise", "blueprints", "fuel"],
        "body": """
    The Forge is where equipment gets made and modified. Craft Equipment spends Blueprints to generate a fresh item; Repair spends Fuel and resources to restore durability; Fuse combines several lower-rarity items into one higher-rarity item; Vaporise breaks an item down into a random assortment of runes. Applying runes to existing equipment also happens here.
    """,
    },
    {
        "id": "camp_market",
        "category": ("Camp", "Market"),
        "title": "Market",
        "aliases": ["buy", "sell", "black market", "trade vouchers", "haggle", "commission"],
        "body": """
    The Market buys and sells resources, equipment, and runes, restocking automatically over time (or on demand with Trade Vouchers). Higher Market levels unlock haggling down prices, commissioning a guaranteed item on the next restock, and eventually the Black Market - a separate, pricier stock of higher-rarity gear paid for in gold plus runes.
    """,
    },
    {
        "id": "camp_questboard",
        "category": ("Camp", "Quest Board"),
        "title": "Quest Board",
        "aliases": ["milestones", "bounties", "credits", "recombine"],
        "body": """
    The Quest Board tracks Milestones (one-time, automatically-completed goals) and Bounties (repeatable, player-chosen goals), both paying out Credits. Credits buy specific runes from the Quest Board's own shop, or unwanted runes can be sold here for Credits directly. At higher levels, Recombine lets you merge two items in storage into one, taking prefixes from one and suffixes from the other.
    """,
    },
    {
        "id": "camp_shrine",
        "category": ("Camp", "Shrine"),
        "title": "Shrine",
        "aliases": ["ascend", "ascendancy", "max level"],
        "body": """
    The Shrine unlocks Ascending at level 20 - choosing one of your class's Ascendancies, each with its own unique mechanics (see Classes & Abilities). You can switch Ascendancy freely at any time at no cost. At max Shrine level, you can also spend resources here to permanently raise your character's max level by 1.
    """,
    },
    {
        "id": "camp_accountstash",
        "category": ("Camp", "Account Stash"),
        "title": "Account Stash",
        "aliases": ["shared stash", "account"],
        "body": """
    The Account Stash is shared storage linked to your account rather than any one character - once a character unlocks it, any other character on the same account can deposit and withdraw from the same pool. You must be a high enough level to access the Account Stash at all, and you can only withdraw equipment at or below your own level (though you can deposit anything, any time).
    """,
    },

    # -- Getting Started -- #
    {
        "id": "welcome",
        "category": ("Getting Started",),
        "title": "Welcome to Korus",
        "aliases": [],
        "body": """
    [bold yellow]First Steps:[/bold yellow]
    1. Explore to find enemies and gain XP, gold, and resources.
    2. Visit the Camp after battles to heal and upgrade your buildings.
    3. Equip better gear from your inventory to boost your stats.
    4. Level up to unlock new abilities automatically.

    [bold yellow]Resource Management:[/bold yellow]
    - Gold buys items and upgrades at the Market.
    - Resources drop from enemies and are used to upgrade camp buildings.
    - Runes drop from enemies (or are bought/crafted) and modify your equipment at the Forge.

    [bold yellow]Quick Tips:[/bold yellow]
    - Heal at the Campfire between fights.
    - Check the Market regularly for new stock.
    - Upgrade camp stations to unlock new features.
    - Save your game frequently.
    """,
    },

    # -- Difficulty & Progression -- #
    {
        "id": "difficulty_levels",
        "category": ("Difficulty & Progression",),
        "title": "Difficulty Levels",
        "aliases": ["easy", "normal", "hard", "nightmare", "hell"],
        "body": """
    Difficulty is more than a stat multiplier - it also tunes enemy AI sharpness and aggression, enemy rarity, group composition, loot and rune quality, crafting risk (Entropy gained), and prices/rewards at camp. It can be changed at any time from the Options menu.

    [green]Easy[/green] - Weaker, more predictable enemies in smaller numbers. Loot leans toward quantity over rarity, crafting is more forgiving, prices are cheaper. Good for learning the game.

    [cyan]Normal[/cyan] - Standard difficulty. Balanced challenge, loot, and prices.

    [orange1]Hard[/orange1] - Sharper, more aggressive enemies in tougher numbers. Better loot rarity and rune quality, at the cost of riskier crafting and pricier upkeep.

    [magenta]Nightmare[/magenta] - Noticeably smarter, more dangerous, support-heavy encounters. Significantly better rewards and rarer drops, but crafting and the market punish mistakes harder.

    [red]Hell[/red] - Enemies play close to optimally, in large dangerous groups. The best loot, rune quality, and rewards in the game - matched by the steepest risk and prices.
    """,
    },
    {
        "id": "hardcore_mode",
        "category": ("Difficulty & Progression",),
        "title": "Hardcore Mode",
        "aliases": ["hardcore"],
        "body": """
    Hardcore Mode is an optional, permanent choice made at character creation. If your character dies, their save file is deleted immediately - there's no recovering it. It can't be turned off once a run has started.
    """,
    },

    # -- Classes & Abilities -- #
    {
        "id": "warrior_rage",
        "category": ("Classes & Abilities", "Warrior"),
        "title": "Rage",
        "aliases": ["rage"],
        "className": "Warrior",
        "body": """
    [resource]Rage[/resource] is the Warrior's core resource. It builds from both dealing and taking damage, and every point adds flat bonus damage to your attacks.

    At the end of combat, half of any Rage you have left over converts into healing before resetting to 0.
    """,
    },
    {
        "id": "warrior_fury",
        "category": ("Classes & Abilities", "Warrior"),
        "title": "Fury (Warlord)",
        "aliases": ["fury", "warlord"],
        "className": "Warrior",
        "body": """
    [asc_warlord]Fury[/asc_warlord] builds while you're attacking with 50 or more Rage banked, up to 10 stacks. Each stack grants bonus damage and Lifesteal. At 10 stacks, your next attack hits every enemy for double damage, strips your banked Lifesteal bonus, and resets Fury to 0.
    """,
    },
    {
        "id": "warrior_fortify_bastion",
        "category": ("Classes & Abilities", "Warrior"),
        "title": "Fortify & Bastion (Juggernaut)",
        "aliases": ["fortify", "bastion", "juggernaut"],
        "className": "Warrior",
        "body": """
    [asc_juggernaut]Fortify[/asc_juggernaut] recalculates every turn based on your current Rage (1 stack per 10 Rage, up to 15), each stack granting Damage Reduction, Crit Chance, and Crit Damage. At 15 Fortify with 100+ Rage banked, your next attack stuns every enemy and consumes 100 Rage.

    [asc_juggernaut]Bastion[/asc_juggernaut] is granted whenever you're critically hit: extra Ailment Avoidance, Crit Resistance, and flat damage reduction, plus that crit itself deals less damage. It clears at the start of your next turn.
    """,
    },
    {
        "id": "warrior_annihilation",
        "category": ("Classes & Abilities", "Warrior"),
        "title": "Annihilation (Annihilist)",
        "aliases": ["annihilation", "annihilist"],
        "className": "Warrior",
        "body": """
    [asc_annihilist]Annihilation[/asc_annihilist] stacks build from your total Rage generated in combat (uncapped), granting bonus Fire damage, Crit Multi, and Crit Chance. Killing an enemy consumes a stack to heal you; landing a crit permanently steals a slice of the target's damage per stack; being critically hit burns every enemy for a share of their own Max HP per stack. Rage no longer heals you at combat end with this ascendancy.
    """,
    },
    {
        "id": "warrior_tyrant",
        "category": ("Classes & Abilities", "Warrior"),
        "title": "Tyrant",
        "aliases": ["tyrant"],
        "className": "Warrior",
        "body": """
    Tyrant stops gaining Rage from being hit - instead, Rage builds from damage your Armour prevents, and some of your Evasion/Energy Shield converts into Armour. Non-critical hits deal extra damage scaling off your current Armour, turning Tyrant into a tank that converts mitigation directly into offense.
    """,
    },
    {
        "id": "warrior_conqueror",
        "category": ("Classes & Abilities", "Warrior"),
        "title": "Conqueror",
        "aliases": ["conqueror"],
        "className": "Warrior",
        "body": """
    Conqueror scales with how many enemies you're facing - at combat start you gain stacking Speed, damage, and damage reduction per surviving enemy, and some Armour/Evasion converts both ways between each other. Dodged or heavily-mitigated hits get converted into stored bonus damage, healing, and Rage, at the cost of generating Rage more slowly overall.
    """,
    },

    {
        "id": "fighter_stances",
        "category": ("Classes & Abilities", "Fighter"),
        "title": "Aggression & Discipline",
        "aliases": ["aggression", "discipline", "stance"],
        "className": "Fighter",
        "body": """
    [resource]Aggression[/resource] and [resource]Discipline[/resource] are the Fighter's two Stance meters. Aggression starts each combat at 25 and rises every turn and on every attack; Discipline instead builds from damage taken. They share a combined cap - pushing one up can "steal" available space from the other - and both can drop as low as -30.
    """,
    },
    {
        "id": "fighter_thresholds",
        "category": ("Classes & Abilities", "Fighter"),
        "title": "Stance Thresholds",
        "aliases": ["complacent", "neutral", "trained", "dedicated", "all-in"],
        "className": "Fighter",
        "body": """
    Aggression and Discipline each independently sit in one of five thresholds based on their current value, and only the currently-occupied threshold's bonuses apply:

    [threshold_complacent]Complacent[/threshold_complacent] (below 0) - a penalty state: reduced Speed/Crit Chance on Aggression, reduced defenses/Stun Avoidance on Discipline.
    [threshold_neutral]Neutral[/threshold_neutral] (0-34) - no bonuses or penalties.
    [threshold_trained]Trained[/threshold_trained] (35-69) - Aggression grants Lifesteal, Crit Multi, and bonus Physical damage; Discipline grants Damage Reduction, Increased Defenses, and HP Regen.
    [threshold_dedicated]Dedicated[/threshold_dedicated] (70-109) - stronger versions of the Trained bonuses on both sides, plus Discipline grants Thorns.
    [threshold_allin]All-In[/threshold_allin] (110+) - the strongest tier: Aggression doubles that attack's damage and banks bonus damage from crits, but loses Increased Defenses; Discipline can't crit but gets huge Thorns, Less Damage Taken, and turns kills into permanent bonus damage plus healing.

    These threshold cutoffs can be lowered by certain ascendancy bonuses.
    """,
    },
    {
        "id": "fighter_impatience",
        "category": ("Classes & Abilities", "Fighter"),
        "title": "Impatience (Dissenter)",
        "aliases": ["impatience", "dissenter"],
        "className": "Fighter",
        "body": """
    [asc_dissenter]Impatience[/asc_dissenter] builds every turn neither of your stances is All-In, and feeds extra progress toward your stronger stance. Once a stance reaches All-In, all Impatience converts into ongoing bonuses (Crit Chance/damage for Aggression, HP Regen/Damage Reduction for Discipline) that last until you drop out of All-In. Dissenter also uniquely strengthens the normally-weak Complacent threshold.
    """,
    },
    {
        "id": "fighter_balance",
        "category": ("Classes & Abilities", "Fighter"),
        "title": "Balance (Arbiter)",
        "aliases": ["balance", "arbiter"],
        "className": "Fighter",
        "body": """
    [asc_arbiter]Balance[/asc_arbiter] builds every turn you're holding Trained Aggression and Trained Discipline at the same time, granting bonus damage and Less Damage Taken while held. When a stance reaches Dedicated, all Balance converts into a permanent bonus - Lifesteal for Aggression, Thorns for Discipline.
    """,
    },
    {
        "id": "fighter_transgressor",
        "category": ("Classes & Abilities", "Fighter"),
        "title": "Dual-Stance Synergy (Transgressor)",
        "aliases": ["transgressor", "dual-stance synergy"],
        "className": "Fighter",
        "body": """
    Transgressor rewards holding specific Aggression+Discipline threshold combinations at once - Dedicated Aggression with Trained Discipline, the reverse, or both Dedicated - each unlocking a distinct, powerful bonus package for as long as you hold that combination. It also raises your combined Stance cap over time.
    """,
    },
    {
        "id": "fighter_pact",
        "category": ("Classes & Abilities", "Fighter"),
        "title": "Pact (Autarch)",
        "aliases": ["pact", "autarch"],
        "className": "Fighter",
        "body": """
    [asc_autarch]Pact[/asc_autarch] is a stance-altering effect you choose fresh each turn, lasting until your next turn: Pact of Aggression or Discipline doubles one stance's effect while inverting the other; Pact of Balance (requires a Dedicated stance) layers Trained-tier bonuses from both stances at once; Pact of Purging (requires an All-In stance) strips its debuffs and grants the other stance's All-In buffs instead, at the risk of taking heavy damage if you don't land a kill that turn.
    """,
    },
    {
        "id": "fighter_triarch",
        "category": ("Classes & Abilities", "Fighter"),
        "title": "Triarch",
        "aliases": ["triarch"],
        "className": "Fighter",
        "body": """
    Triarch is a hybrid-defense ascendancy: holding Armour, Evasion, and Energy Shield all at once partially converts each into the other two, scales Crit Chance/Damage off Evasion and HP Regen off Energy Shield, and grows your combined Stance cap with Max Energy Shield.
    """,
    },

    {
        "id": "mage_mastery",
        "category": ("Classes & Abilities", "Mage"),
        "title": "Mastery",
        "aliases": ["mastery"],
        "className": "Mage",
        "body": """
    [resource]Mastery[/resource] builds from Arcane-damage attacks, capped at 10 normally, granting Crit Chance and Crit Multi per stack.
    """,
    },
    {
        "id": "mage_adaptation_archmage",
        "category": ("Classes & Abilities", "Mage"),
        "title": "Adaptation & Archmage",
        "aliases": ["adaptation", "archmage"],
        "className": "Mage",
        "body": """
    Being hit in combat grants a random elemental [class_mage]Adaptation[/class_mage] - Fire (Crit Damage), Cold (Speed), Earth (Elemental Resistances), or Lightning (Crit Chance). Hierophant additionally rolls Holy/Dark/Arcane "Divine" Adaptations.

    [class_mage]Archmage[/class_mage] triggers once you're holding all 4 elemental Adaptations at once, boosting Arcane damage at the cost of higher Mana costs on Arcane attacks.
    """,
    },
    {
        "id": "mage_calamity",
        "category": ("Classes & Abilities", "Mage"),
        "title": "Relinquished & Calamity",
        "aliases": ["relinquished", "calamity"],
        "className": "Mage",
        "body": """
    Every critical hit as Calamity permanently [asc_calamity]Relinquishes[/asc_calamity] one held elemental Adaptation for a stronger, unique buff in its place. Once all 4 have been Relinquished, you enter [asc_calamity]Calamity[/asc_calamity] itself - hugely boosted crit stats and Less Damage Taken, with all your damage doubled.
    """,
    },
    {
        "id": "mage_prophetic",
        "category": ("Classes & Abilities", "Mage"),
        "title": "Prophetic (Hierophant)",
        "aliases": ["prophetic", "hierophant"],
        "className": "Mage",
        "body": """
    [asc_hierophant]Prophetic[/asc_hierophant] triggers once you're holding all 3 Divine Adaptations (Holy/Dark/Arcane) at once, granting Resistance Penetration at the cost of higher Mana costs. Holding both Archmage and Prophetic together unlocks a further crit-focused super-buff.
    """,
    },
    {
        "id": "mage_precision",
        "category": ("Classes & Abilities", "Mage"),
        "title": "Precision (Unmaker)",
        "aliases": ["precision", "unmaker"],
        "className": "Mage",
        "body": """
    [asc_unmaker]Precision[/asc_unmaker] stacks (up to 10) from landing or receiving a critical hit, each adding Crit Chance, a large amount of Crit Multi, and Execute Threshold - if a target's HP falls below that threshold percentage of its Max HP, it's instantly killed. At 10 stacks, your Crit Chance is doubled for a single roll.
    """,
    },
    {
        "id": "mage_arcanist",
        "category": ("Classes & Abilities", "Mage"),
        "title": "Arcanist",
        "aliases": ["arcanist"],
        "className": "Mage",
        "body": """
    Arcanist converts a portion of Max HP into Mana and grows Mana Regen over time. Attacks costing a large chunk of your Mana in one go are cast for free and refund extra Mana, and Arcane damage scales up directly with how much Mana you're currently holding above half.
    """,
    },
    {
        "id": "mage_empyrean",
        "category": ("Classes & Abilities", "Mage"),
        "title": "Empyrean",
        "aliases": ["empyrean"],
        "className": "Mage",
        "body": """
    Empyrean removes Mastery's stack cap and lets it build from being hit or from crits too, converts Energy Shield into bonus Mana, and regenerates Energy Shield from spending Mana. Breaking your own Energy Shield grants a temporary crit/Lifesteal/penetration buff.
    """,
    },

    {
        "id": "tempest_static_flow",
        "category": ("Classes & Abilities", "Tempest"),
        "title": "Static & Flow",
        "aliases": ["static", "flow"],
        "className": "Tempest",
        "body": """
    [resource]Static[/resource] builds when a slower enemy hits you (defensive: Damage Reduction, but slows you slightly), while [resource]Flow[/resource] builds when a faster enemy hits you (offensive: bonus damage and Speed). Both cap at 10 stacks.
    """,
    },
    {
        "id": "tempest_unleash",
        "category": ("Classes & Abilities", "Tempest"),
        "title": "Unleash",
        "aliases": ["unleash"],
        "className": "Tempest",
        "body": """
    Once your combined Static and Flow reach a threshold, your next attack [class_tempest]Unleashes[/class_tempest] - if it's Lightning damage, it deals massively increased damage and Lifesteal, consuming stacks from both meters evenly.
    """,
    },
    {
        "id": "tempest_alternator",
        "category": ("Classes & Abilities", "Tempest"),
        "title": "Positive & Negative (Alternator)",
        "aliases": ["positive", "negative", "alternator"],
        "className": "Tempest",
        "body": """
    [asc_alternator]Positive[/asc_alternator] and [asc_alternator]Negative[/asc_alternator] are streak counters (up to 5 each) - consecutive crits build Positive (Crit Chance/Multi, less defense), consecutive non-crits build Negative (damage, Lifesteal, more defense). Breaking a streak wipes the opposite counter and grants a bonus payoff.
    """,
    },
    {
        "id": "tempest_fleeting",
        "category": ("Classes & Abilities", "Tempest"),
        "title": "Fleeting (Dervish)",
        "aliases": ["fleeting", "dervish"],
        "className": "Tempest",
        "body": """
    [asc_dervish]Fleeting[/asc_dervish] stacks (up to 10) from evading attacks, granting Speed and Lightning damage immediately. On your next crit, all Fleeting is consumed for healing and bonus Crit Damage.
    """,
    },
    {
        "id": "tempest_spark",
        "category": ("Classes & Abilities", "Tempest"),
        "title": "Spark (Archon)",
        "aliases": ["spark", "archon"],
        "className": "Tempest",
        "body": """
    [asc_archon]Spark[/asc_archon] stacks (up to 5) from critically hitting an enemy faster than you, granting Crit Chance and Crit Multi at the cost of some Speed.
    """,
    },
    {
        "id": "tempest_ravager",
        "category": ("Classes & Abilities", "Tempest"),
        "title": "Flurry & Relentless (Ravager)",
        "aliases": ["flurry", "relentless", "ravager"],
        "className": "Tempest",
        "body": """
    [asc_ravager]Flurry[/asc_ravager] stacks (up to 5) from every crit, boosting Multihit Chance and Crit Chance. [asc_ravager]Relentless[/asc_ravager] stacks (up to 3) from every Multihit trigger, boosting Lightning damage and Speed at the cost of some defense.
    """,
    },
    {
        "id": "tempest_mirage",
        "category": ("Classes & Abilities", "Tempest"),
        "title": "Mirage",
        "aliases": ["mirage"],
        "className": "Tempest",
        "body": """
    Mirage splits most of your Armour into Evasion (with a sliver into Energy Shield). Evading grants bonus stored damage and a Flow stack; a hit fully absorbed by Energy Shield grants a Static stack instead. Crit stats scale directly off your raw Evasion/Energy Shield values.
    """,
    },

    {
        "id": "wanderer_hope_hopeless",
        "category": ("Classes & Abilities", "Wanderer"),
        "title": "Hope, Hopeless & Lost",
        "aliases": ["hope", "hopeless", "lost"],
        "className": "Wanderer",
        "body": """
    [resource]Lost[/resource] triggers when a single hit deals a large chunk of your Max HP, redirecting your attack to hit every enemy at once and randomly building either [resource]Hope[/resource] (more likely above 50% HP) or [resource]Hopeless[/resource] (more likely below it), both capped at 5 stacks (higher for some ascendancies). Each Hope stack grants Crit Chance and increased Psychic damage; each Hopeless stack grants Damage Reduction and Crit Damage.
    """,
    },
    {
        "id": "wanderer_radiance_devastation",
        "category": ("Classes & Abilities", "Wanderer"),
        "title": "Radiance & Devastation",
        "aliases": ["radiance", "devastation"],
        "className": "Wanderer",
        "body": """
    Maxing Hope grants [wanderer_radiance]Radiance[/wanderer_radiance] - big Crit Chance/Damage, with crits and kills healing you. Maxing Hopeless grants [wanderer_devastation]Devastation[/wanderer_devastation] - doubled damage dealt and increased damage taken, and every Lost trigger while Devastated adds more permanent bonus damage for the rest of combat.
    """,
    },
    {
        "id": "wanderer_transcendence",
        "category": ("Classes & Abilities", "Wanderer"),
        "title": "Transcendence (Manifestation)",
        "aliases": ["transcendence", "manifestation"],
        "className": "Wanderer",
        "body": """
    [wanderer_transcendence]Transcendence[/wanderer_transcendence] activates when you're holding both Radiance and Devastation together: increased defenses (at the cost of most of your Evasion), guaranteed crits, bonus Psychic damage, and any hit you take reflects a share of the attacker's Max HP back at them.
    """,
    },
    {
        "id": "wanderer_harmony",
        "category": ("Classes & Abilities", "Wanderer"),
        "title": "Harmony (Weaver)",
        "aliases": ["harmony", "weaver"],
        "className": "Wanderer",
        "body": """
    [wanderer_harmony]Harmony[/wanderer_harmony] activates whenever your Hope and Hopeless stacks are exactly equal: bonus Crit Damage, Speed, and increased damage dealt. Triggering Lost while Harmony is active also heals you for a share of the damage it deals.
    """,
    },
    {
        "id": "wanderer_fracture",
        "category": ("Classes & Abilities", "Wanderer"),
        "title": "Fracture (Fractured)",
        "aliases": ["fracture", "fractured"],
        "className": "Wanderer",
        "body": """
    [asc_fractured]Fracture[/asc_fractured] stacks (up to 5) build on every Lost trigger, granting Crit Chance (or Crit Damage instead, while Devastation is active) plus bonus Psychic damage. At 5 stacks, your next Lost trigger deals extra damage before resetting.
    """,
    },
    {
        "id": "wanderer_warped",
        "category": ("Classes & Abilities", "Wanderer"),
        "title": "Warped (Warper)",
        "aliases": ["warped", "warper"],
        "className": "Wanderer",
        "body": """
    [asc_warper]Warped[/asc_warper] is a one-shot buff (Lifesteal and Crit Chance) consumed on your very next attack, granted after certain Lost triggers, when a hit is fully absorbed by Energy Shield, or when you take a very small hit while already Lost.
    """,
    },
    {
        "id": "wanderer_torture",
        "category": ("Classes & Abilities", "Wanderer"),
        "title": "Torture (Mindbreaker)",
        "aliases": ["torture", "mindbreaker"],
        "className": "Wanderer",
        "body": """
    [asc_mindbreaker]Torture[/asc_mindbreaker] is an enemy-side stack applied by your Psychic-damage hits (doubled while Radiant/Devastated), weakening that enemy's own damage dealt and increasing the damage it takes. Enemies lose all their Torture the instant they land a crit on you - unless you have Radiance active, in which case they can't shake it off that way at all, and losing it costs them extra damage if you have Devastation instead.
    """,
    },
    {
        "id": "wanderer_hunted",
        "category": ("Classes & Abilities", "Wanderer"),
        "title": "Hunted (Abyssal)",
        "aliases": ["hunted", "abyssal"],
        "className": "Wanderer",
        "body": """
    [asc_abyssal]Hunted[/asc_abyssal] is a self-buff (not an enemy debuff) that stacks up to 3, each point trading Speed for a large boost to your own damage dealt - and damage taken. At 3 stacks you get guaranteed crits, and your next attack consumes all Hunted for a huge hit that also costs you some HP back.
    """,
    },

    {
        "id": "wretch_basics",
        "category": ("Classes & Abilities", "Wretch"),
        "title": "Wretch Basics",
        "aliases": ["health cost", "manaless"],
        "className": "Wretch",
        "body": """
    Wretches have no Stamina - every ability costs Health directly instead, and you gain Lifesteal that scales with your Missing Health. All Wretches also get bonus Speed and Dark damage below 40% HP.
    """,
    },
    {
        "id": "wretch_bloodspike",
        "category": ("Classes & Abilities", "Wretch"),
        "title": "Blood Spike",
        "aliases": ["blood spike"],
        "className": "Wretch",
        "body": """
    [resource]Blood Spike[/resource] is a stack every Wretch ascendancy builds on enemies from ability hits (up to 5-15 stacks depending on ascendancy). Each stack lowers that enemy's execute threshold - once its HP falls low enough, it's instantly finished off outright, healing you in the process.
    """,
    },
    {
        "id": "wretch_necrosis",
        "category": ("Classes & Abilities", "Wretch"),
        "title": "Necrosis & Rot (Necrose)",
        "aliases": ["necrosis", "rot", "necrose"],
        "className": "Wretch",
        "body": """
    [asc_necrose]Necrosis[/asc_necrose] is an enemy-side stack applied whenever you're hit as Necrose, slowing the enemy and increasing the damage it takes. [asc_necrose]Rot[/asc_necrose] is a separate self-buff (bonus damage and Speed, less Crit Damage) granted for a few turns whenever you Blood-Spike-execute an enemy.
    """,
    },
    {
        "id": "wretch_bloodscent",
        "category": ("Classes & Abilities", "Wretch"),
        "title": "Blood Scent (Plaguebearer)",
        "aliases": ["blood scent", "plaguebearer"],
        "className": "Wretch",
        "body": """
    [asc_plaguebearer]Blood Scent[/asc_plaguebearer] stacks (up to 5) build on getting critically hit or on any kill, each adding Lifesteal, Speed, and bonus damage dealt.
    """,
    },
    {
        "id": "wretch_skeleton",
        "category": ("Classes & Abilities", "Wretch"),
        "title": "Skeleton (Necromancer)",
        "aliases": ["skeleton", "necromancer"],
        "className": "Wretch",
        "body": """
    [asc_necromancer]Skeleton[/asc_necromancer] lets you convert a kill into a temporary allied minion for a few turns, once per battle, keeping a share of the fallen enemy's stats and items.
    """,
    },
    {
        "id": "wretch_exsanguinator",
        "category": ("Classes & Abilities", "Wretch"),
        "title": "Exsanguinator",
        "aliases": ["exsanguinator"],
        "className": "Wretch",
        "body": """
    Exsanguinator burns through enemies' Blood Spike for burst payoff - your crits automatically wipe the target's Blood Spike stacks for bonus crit damage.
    """,
    },
    {
        "id": "wretch_bloodletter",
        "category": ("Classes & Abilities", "Wretch"),
        "title": "Bloodletter",
        "aliases": ["bloodletter"],
        "className": "Wretch",
        "body": """
    Bloodletter turns your own Health loss into a resource - it banks the damage you take and reflects a share of it back as Dark damage whenever you're hit, and separately stores Divine/Otherworldly damage taken to convert into healing later.
    """,
    },

    {
        "id": "marauder_echo_siphon",
        "category": ("Classes & Abilities", "Marauder"),
        "title": "Echo & Siphon",
        "aliases": ["echo", "siphon", "siphoned"],
        "className": "Marauder",
        "body": """
    [class_marauder]Echo[/class_marauder] and [class_marauder]Siphon[/class_marauder] are base Marauder mechanics available to every ascendancy. Attacking an enemy that's already acted this round banks a share of that damage as Echo, which detonates automatically at the start of your next turn. Attacking an enemy before it has acted instead Siphons some of its base damage away permanently (capped, and it can't drop below a floor) - though an enemy that hits you before you've acted can steal a little of that Siphoned damage back.
    """,
    },
    {
        "id": "marauder_crush",
        "category": ("Classes & Abilities", "Marauder"),
        "title": "Crush (Colossus)",
        "aliases": ["crush", "colossus"],
        "className": "Marauder",
        "body": """
    [asc_colossus]Crush[/asc_colossus] is an enemy-side stack (up to 3) that shreds a chunk of the target's Armour per stack, applied when attacking an already-acted enemy.
    """,
    },
    {
        "id": "marauder_deferred",
        "category": ("Classes & Abilities", "Marauder"),
        "title": "Deferred (Dreadnought)",
        "aliases": ["deferred", "dreadnought"],
        "className": "Marauder",
        "body": """
    [asc_dreadnought]Deferred[/asc_dreadnought] damage is a portion of hits you take, delayed and landing on you again one turn later instead of immediately. A slice of each deferred hit also feeds a permanent bonus-damage pool for the rest of combat.
    """,
    },
    {
        "id": "marauder_shame",
        "category": ("Classes & Abilities", "Marauder"),
        "title": "Shame (Sovereign)",
        "aliases": ["shame", "sovereign"],
        "className": "Marauder",
        "body": """
    [asc_sovereign]Shame[/asc_sovereign] is an enemy-side debuff that weakens the target's own attacks for its duration - automatically applied to any enemy that hits you before you've acted this round, and some abilities can apply it directly too.
    """,
    },
    {
        "id": "marauder_empowerment",
        "category": ("Classes & Abilities", "Marauder"),
        "title": "Empowerment (Harrower)",
        "aliases": ["empowerment", "harrower"],
        "className": "Marauder",
        "body": """
    [asc_harrower]Empowerment[/asc_harrower] is a permanent self-buff (bonus HP Regen, less Speed) earned once per combat, boosting your Cold damage while active.
    """,
    },
    {
        "id": "marauder_butcher",
        "category": ("Classes & Abilities", "Marauder"),
        "title": "Marked, Slaughter & Carved (Butcher)",
        "aliases": ["marked", "slaughter", "carved", "butcher"],
        "className": "Marauder",
        "body": """
    [asc_butcher]Marked[/asc_butcher] singles out one random enemy at combat start (re-targeting a new one whenever the current target dies) - it deals more damage and takes more damage while Marked. [asc_butcher]Slaughter[/asc_butcher] is a self-stack from crits, boosting your Crit Multi and Cold damage. [asc_butcher]Carved[/asc_butcher] is an enemy-side stack from attacking already-acted enemies that shreds their Crit Chance and defenses.
    """,
    },

    {
        "id": "paladin_favour",
        "category": ("Classes & Abilities", "Paladin"),
        "title": "Favour",
        "aliases": ["favour", "favor"],
        "className": "Paladin",
        "body": """
    [resource]Favour[/resource] builds every turn and can be spent on a random offensive or defensive buff. Healing at the end of combat scales with however much Favour you have left over.
    """,
    },
    {
        "id": "paladin_zealotry",
        "category": ("Classes & Abilities", "Paladin"),
        "title": "Zealotry (Zealot)",
        "aliases": ["zealotry", "zealot"],
        "className": "Paladin",
        "body": """
    [asc_zealot]Zealotry[/asc_zealot] stacks build from spending Favour offensively, adding flat bonus damage (extra against Holy hits) - but also increasing the damage you take slightly per stack.
    """,
    },
    {
        "id": "paladin_bulwark",
        "category": ("Classes & Abilities", "Paladin"),
        "title": "Bulwark (Guardian)",
        "aliases": ["bulwark", "guardian"],
        "className": "Paladin",
        "body": """
    [asc_guardian]Bulwark[/asc_guardian] stacks (up to 5) build from spending Favour defensively, each slowing you slightly but boosting your Holy damage.
    """,
    },
    {
        "id": "paladin_justice",
        "category": ("Classes & Abilities", "Paladin"),
        "title": "Justice (Justicar)",
        "aliases": ["justice", "justicar"],
        "className": "Paladin",
        "body": """
    [asc_justicar]Justice[/asc_justicar] is a buff window granted on kill: bonus Holy damage and Damage Reduction, plus an immediate one-time boost to Crit Chance and Speed.
    """,
    },
    {
        "id": "paladin_valour",
        "category": ("Classes & Abilities", "Paladin"),
        "title": "Valour (Crusader)",
        "aliases": ["valour", "valor", "crusader"],
        "className": "Paladin",
        "body": """
    [asc_crusader]Valour[/asc_crusader] stacks (up to 10) from kills or big hits, granting Speed and permanent Lifesteal (plus bonus Holy damage) while held - with even bigger crit bonuses once maxed.
    """,
    },
    {
        "id": "paladin_blessing",
        "category": ("Classes & Abilities", "Paladin"),
        "title": "Blessing (Inquisitor)",
        "aliases": ["blessing", "inquisitor"],
        "className": "Paladin",
        "body": """
    [asc_inquisitor]Blessing[/asc_inquisitor] is a short buff window triggered by spending a large chunk of your Favour right after being hit: bonus Favour generation, HP Regen, Holy damage, and Less Damage Taken while it lasts.
    """,
    },

    {
        "id": "spectre_vengeance",
        "category": ("Classes & Abilities", "Spectre"),
        "title": "Vengeance",
        "aliases": ["vengeance"],
        "className": "Spectre",
        "body": """
    [resource]Vengeance[/resource] builds from taking hits (more from crits), granting Ethereal damage, Crit Chance, and Speed per stack. Landing a crit normally consumes all Vengeance for bonus Crit Damage.
    """,
    },
    {
        "id": "spectre_execute",
        "category": ("Classes & Abilities", "Spectre"),
        "title": "Execute (Reaper)",
        "aliases": ["execute", "executing", "reaper"],
        "className": "Spectre",
        "body": """
    [asc_reaper]Execute[/asc_reaper] checks every hit against a low-HP threshold (raised by some abilities) - if the target's HP is below it, they're instantly killed outright. Executing heals you, permanently boosts your damage based on the Vengeance you had banked, and consumes all your Vengeance.
    """,
    },
    {
        "id": "spectre_phased",
        "category": ("Classes & Abilities", "Spectre"),
        "title": "Phased & Shifting (Phantasm)",
        "aliases": ["phased", "shifting", "phantasm"],
        "className": "Spectre",
        "body": """
    [asc_phantasm]Phased[/asc_phantasm] is an enemy-side debuff your Ethereal hits have a chance to apply (higher chance with more Vengeance), reducing that enemy's damage dealt and Speed for a few turns. Attacking a Phased enemy heals you; being hit by one instead grants you [asc_phantasm]Shifting[/asc_phantasm], a temporary boost to all three defenses, at the cost of some Vengeance.
    """,
    },
    {
        "id": "spectre_intangible",
        "category": ("Classes & Abilities", "Spectre"),
        "title": "Intangibility (Revenant)",
        "aliases": ["intangible", "intangibility", "revenant"],
        "className": "Spectre",
        "body": """
    [asc_revenant]Intangibility[/asc_revenant] triggers once per combat: instead of dying to a lethal hit, your HP is set to 1 and you become immune to damage below a threshold for a turn (with damage above that threshold still killing you). Damage prevented this way heals you back once it ends, and your Ethereal damage is boosted while it's active.
    """,
    },
    {
        "id": "spectre_fading",
        "category": ("Classes & Abilities", "Spectre"),
        "title": "Fading (Wraith)",
        "aliases": ["fading", "wraith"],
        "className": "Spectre",
        "body": """
    [asc_wraith]Fading[/asc_wraith] is a counter that builds as you heal via Ghostly effects; every large chunk accrued permanently reduces your Max HP by a small amount. Landing a crit resets Fading to 0 and heals back the accrued amount.
    """,
    },

    {
        "id": "cultist_insanity",
        "category": ("Classes & Abilities", "Cultist"),
        "title": "Insanity",
        "aliases": ["insanity"],
        "className": "Cultist",
        "body": """
    [resource]Insanity[/resource] swings unpredictably every turn between -50 and +50. Strongly positive Insanity boosts Chaos damage (at the cost of Speed); strongly negative Insanity grants a Shield each turn instead. Landing near 0 or hitting either extreme triggers a big one-off bonus or penalty before Insanity rerolls into a new range.
    """,
    },
    {
        "id": "cultist_shadow",
        "category": ("Classes & Abilities", "Cultist"),
        "title": "Shadow (Umbralist)",
        "aliases": ["shadow", "umbralist"],
        "className": "Cultist",
        "body": """
    [asc_umbralist]Shadow[/asc_umbralist] stacks (up to 10) build from negative Insanity, granting Damage Reduction and bonus Chaos damage. At max stacks, your next Chaos hit becomes unresistable True damage and heals you.
    """,
    },
    {
        "id": "cultist_corruption",
        "category": ("Classes & Abilities", "Cultist"),
        "title": "Corruption (Harbinger)",
        "aliases": ["corruption", "harbinger"],
        "className": "Cultist",
        "body": """
    [asc_harbinger]Corruption[/asc_harbinger] is an enemy-side stack (up to 10) your Chaos damage has a chance to apply, amplifying further Chaos damage against that enemy and able to spread between enemies over time. Killing a heavily-Corrupted enemy makes it explode, damaging every other enemy.
    """,
    },
    {
        "id": "cultist_doomsayer",
        "category": ("Classes & Abilities", "Cultist"),
        "title": "Omen & Heresy (Doomsayer)",
        "aliases": ["omen", "heresy", "doomsayer"],
        "className": "Cultist",
        "body": """
    [asc_doomsayer]Omen[/asc_doomsayer] builds when you deliberately shift your own Insanity, [asc_doomsayer]Heresy[/asc_doomsayer] builds when you choose not to - both add Chaos damage and some damage taken, and both convert into Crit Damage/Lifesteal when consumed on a crit.
    """,
    },
    {
        "id": "cultist_ritualist",
        "category": ("Classes & Abilities", "Cultist"),
        "title": "Elevated, Devotion & Faithless (Ritualist)",
        "aliases": ["elevated", "devotion", "faithless", "ritualist"],
        "className": "Cultist",
        "body": """
    [asc_ritualist]Elevated[/asc_ritualist] is a short buff (Chaos damage, Damage Reduction, Ailment Avoidance) from sacrificing HP to forcibly shift your Insanity. [asc_ritualist]Devotion[/asc_ritualist] stacks from attacking at very high Insanity, [asc_ritualist]Faithless[/asc_ritualist] stacks from being hit at very low Insanity - both grant escalating bonuses the more you hold.
    """,
    },
    {
        "id": "cultist_anarchist",
        "category": ("Classes & Abilities", "Cultist"),
        "title": "Volatility & Discharge (Anarchist)",
        "aliases": ["volatility", "discharge", "anarchist"],
        "className": "Cultist",
        "body": """
    [asc_anarchist]Volatility[/asc_anarchist] is a meter that fills from dealing/taking damage (and more from kills/crits); every chunk held boosts your damage dealt slightly at the cost of some damage taken. At full, your next attack triggers [asc_anarchist]Discharge[/asc_anarchist] - a powerful effect that varies depending on whether your Insanity is currently positive, negative, or near zero.
    """,
    },
    {
        "id": "cultist_desecrator",
        "category": ("Classes & Abilities", "Cultist"),
        "title": "Ruin, Tainted & Desecrated (Desecrator)",
        "aliases": ["ruin", "tainted", "desecrated", "desecrator"],
        "className": "Cultist",
        "body": """
    [asc_desecrator]Ruin[/asc_desecrator] is an uncapped enemy-side stack you apply per damage dealt, weakening that enemy's Crit Chance and every resistance. At 5+ stacks the enemy is [asc_desecrator]Tainted[/asc_desecrator] and takes extra damage; at 10+ it's [asc_desecrator]Desecrated[/asc_desecrator] and takes even more, spreading Ruin to other enemies on its turn and death.
    """,
    },

    {
        "id": "druid_forms",
        "category": ("Classes & Abilities", "Druid"),
        "title": "Human & Beast Form",
        "aliases": ["human", "beast", "form", "verdance"],
        "className": "Druid",
        "body": """
    Druids shapeshift between [human]Human[/human] and [beast]Beast[/beast] Form using "Switch Form." Human Form favours HP/Stamina Regen and defenses; Beast Form favours Earth damage and Speed. Both scale up with level and with Verdance, a shared stat built by attacking in Human Form or by tanking hits in Beast Form.
    """,
    },
    {
        "id": "druid_heartwood",
        "category": ("Classes & Abilities", "Druid"),
        "title": "Root, Elderbark & Loam (Heartwood)",
        "aliases": ["root", "rootbound", "elderbark", "loam", "heartwood"],
        "className": "Druid",
        "body": """
    Switching into Human Form grants [asc_heartwood]Root[/asc_heartwood], which ticks down each turn spent there; hitting 0 evolves you into [asc_heartwood]Elderbark[/asc_heartwood], a temporary state with strong Thorns and HP Regen. [asc_heartwood]Loam[/asc_heartwood] stacks in Beast Form instead, consumed on switching back to Human Form for bonus Earth damage and Crit Chance, and to speed up your next trip to Elderbark.
    """,
    },
    {
        "id": "druid_skinwalker",
        "category": ("Classes & Abilities", "Druid"),
        "title": "Ferocity & Instinct (Skinwalker)",
        "aliases": ["ferocity", "instinct", "skinwalker"],
        "className": "Druid",
        "body": """
    [asc_skinwalker]Ferocity[/asc_skinwalker] stacks in Beast Form (from time spent there and from crits), boosting Crit Chance/Damage - guaranteeing crits against low-HP targets once maxed. [asc_skinwalker]Instinct[/asc_skinwalker] stacks in Human Form instead, converting into Ferocity and temporary Damage Reduction/HP Regen when you switch to Beast Form.
    """,
    },
    {
        "id": "druid_confluence",
        "category": ("Classes & Abilities", "Druid"),
        "title": "Flux & Confluence",
        "aliases": ["flux", "confluence"],
        "className": "Druid",
        "body": """
    [asc_confluence]Flux[/asc_confluence] builds every time you switch forms, boosting your Form Effect and Speed permanently while held. At 5 stacks, Switch Form locks and you evolve into a fused Confluence form for the rest of combat, with much stronger defenses and Earth damage at the cost of taking more damage overall.
    """,
    },
    {
        "id": "druid_wellspring",
        "category": ("Classes & Abilities", "Druid"),
        "title": "Blooming (Wellspring)",
        "aliases": ["blooming", "wellspring"],
        "className": "Druid",
        "body": """
    [asc_wellspring]Blooming[/asc_wellspring] triggers when you Switch Form while holding at least half your Max Verdance, consuming it all for a damage nova to every enemy and a strong temporary boost to your Form Effect.
    """,
    },
    {
        "id": "druid_numen",
        "category": ("Classes & Abilities", "Druid"),
        "title": "Numen",
        "aliases": ["numen"],
        "className": "Druid",
        "body": """
    Numen swaps Verdance-based scaling for direct Armour/Energy Shield conversion between forms - Human Form banks a share of Armour as Energy Shield, Beast Form banks a share of Energy Shield as Armour, and damage prevented by whichever defense you're leaning on turns into bonus damage or extra Energy Shield.
    """,
    },
]

def _childrenAt(pathPrefix: Tuple[str, ...], topics: List[Dict]) -> Tuple[List[str], List[Dict]]:
    """Returns (subCategoryNames, leafTopics) one level below pathPrefix."""
    subCats: List[str] = []
    leaves: List[Dict] = []
    seen = set()
    for t in topics:
        cat = t["category"]
        if cat[:len(pathPrefix)] != pathPrefix:
            continue
        remainder = cat[len(pathPrefix):]
        if not remainder:
            leaves.append(t)
        elif remainder[0] not in seen:
            seen.add(remainder[0])
            subCats.append(remainder[0])
    return subCats, leaves

class Help:
    def __init__(self):
        self.player = None

    def helpMenu(self, player=None):
        self.player = player
        while True:
            clearScreen()
            printHeader("HELP & GUIDE")

            console.print("\n[bold cyan]=== Help Topics ===[/bold cyan]\n")
            console.print("[dim]0.[/dim] [red]Return[/red]")
            console.print("[dim]1.[/dim] [green]Getting Started[/green]")
            console.print("[dim]2.[/dim] [cyan]Combat[/cyan]")
            console.print("[dim]3.[/dim] [yellow]Camp Buildings[/yellow]")
            console.print("[dim]4.[/dim] [magenta]Classes & Abilities[/magenta]")
            console.print("[dim]5.[/dim] [orange1]Equipment & Items[/orange1]")
            console.print("[dim]6.[/dim] [blue]Difficulty & Progression[/blue]")
            console.print("\n[dim]Type a word or phrase to search all Help topics.[/dim]")

            choice = console.input("\n[cyan]Choose topic:\n> [/cyan]").strip()
            checkGlobalCommand(choice)

            if choice == '0':
                return
            elif choice == '1':
                self._browseMenu(("Getting Started",), HELP_TOPICS)
            elif choice == '2':
                self._browseMenu(("Combat",), HELP_TOPICS)
            elif choice == '3':
                self._browseMenu(("Camp",), HELP_TOPICS)
            elif choice == '4':
                self._classesMenu()
            elif choice == '5':
                self._browseMenu(("Equipment & Items",), HELP_TOPICS)
            elif choice == '6':
                self._browseMenu(("Difficulty & Progression",), HELP_TOPICS)
            elif choice != '':
                self._searchFlow(choice)

    def _classesMenu(self):
        if not self.player:
            printWarning("No character loaded - can't show class-specific Help.")
            pause()
            return
        classTopics = [t for t in HELP_TOPICS if t.get("className") == self.player.className]
        if not classTopics:
            printWarning(f"No Help topics written for {self.player.className} yet.")
            pause()
            return
        self._browseMenu(("Classes & Abilities", self.player.className), classTopics,
                          headerLabel=f"{self.player.className} - Classes & Abilities")

    def _browseMenu(self, pathPrefix: Tuple[str, ...], topics: List[Dict], headerLabel: Optional[str] = None):
        while True:
            subCats, leaves = _childrenAt(pathPrefix, topics)
            options = [('cat', name) for name in subCats] + [('topic', t) for t in leaves]

            clearScreen()
            printHeader(headerLabel or (" > ".join(pathPrefix) if pathPrefix else "Help"))
            console.print("[dim]0.[/dim] Return")
            for i, (kind, val) in enumerate(options, 1):
                label = val if kind == 'cat' else val['title']
                console.print(f"[dim]{i}.[/dim] {label}")
            console.print("\n[dim]Type a word or phrase to search all Help topics.[/dim]")

            choice = console.input("\n[cyan]>[/cyan] ").strip()
            checkGlobalCommand(choice)

            if choice == '0':
                return
            if choice == '':
                continue

            try:
                index = int(choice) - 1
            except ValueError:
                self._searchFlow(choice)
                continue

            if 0 <= index < len(options):
                kind, val = options[index]
                if kind == 'cat':
                    self._browseMenu(pathPrefix + (val,), topics)
                else:
                    self._viewTopic(val)
            else:
                printWarning("Invalid choice")
                pause()

    def _searchFlow(self, query: str):
        matches = self._searchTopics(query)
        while True:
            clearScreen()
            printHeader(f"Search results for '{query}'")
            if not matches:
                printWarning("No matching Help topics found.")
            else:
                console.print("[dim]0.[/dim] Return")
                for i, t in enumerate(matches, 1):
                    categoryStr = " > ".join(t['category'])
                    console.print(f"[dim]{i}.[/dim] {t['title']} [dim]({categoryStr})[/dim]")

            newQuery = console.input(
                "\n[cyan]Type a number to view, a new phrase to search again, or 0 to return:\n> [/cyan]"
            ).strip()
            checkGlobalCommand(newQuery)

            if newQuery == '0' or newQuery == '':
                return

            try:
                index = int(newQuery) - 1
            except ValueError:
                query = newQuery
                matches = self._searchTopics(query)
                continue

            if matches and 0 <= index < len(matches):
                self._viewTopic(matches[index])
            else:
                printWarning("Invalid choice")
                pause()

    def _searchTopics(self, query: str, topics: Optional[List[Dict]] = None) -> List[Dict]:
        topics = topics if topics is not None else HELP_TOPICS
        q = query.strip().lower()
        if not q:
            return []
        results = []
        for t in topics:
            haystack = " ".join([
                t["title"], " ".join(t.get("aliases", [])),
                " ".join(t["category"]), t["body"]
            ]).lower()
            if q in haystack:
                results.append(t)
        return results

    def _viewTopic(self, topic: Dict):
        clearScreen()
        printHeader(topic["title"])
        console.print(topic["body"])
        pause()
