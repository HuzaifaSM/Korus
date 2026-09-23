from .styles import console, clearScreen, printHeader, printSuccess, pause
from .player_classes.warrior import Warrior
from .camp import Camp
from .enemies.enemy import Enemy, EnemyClass, EnemyRarity

TUTORIAL_HEALTH = 500  # generous safety buffer against the fixed, weak tutorial enemies - see runTutorial()

def _narrate(text: str):
    clearScreen()
    console.print(text)
    pause()

def _fixedEnemy(name: str, level: int, health: int, damage: int, speed: float) -> Enemy:
    return Enemy(name, level=level, health=health, damage=damage, critChance=0.05, critMulti=1.5,
                 damageType="physical", speed=speed, rarity=EnemyRarity.COMMON, enemyClass=EnemyClass.ATTACKER)

def _ensureLevel(player, minLevel: int):
    while player._level < minLevel:
        player.gainExperience(player._xpToNextLevel)

def _healToFull(player):
    player._health = player._maxHealth
    if hasattr(player, '_stamina'):
        player._stamina = player._maxStamina

def _safeCombat(game, enemies) -> bool:
    try:
        game.startCombat(enemies)
        return True
    except SystemExit:
        clearScreen()
        console.print("[warning]That fight went sideways for a moment there - let's patch you up and carry on.[/warning]")
        _healToFull(game.player)
        pause()
        return False

def runTutorial(game):
    clearScreen()
    _narrate("""
    [bold cyan]=== Welcome to Korus ===[/bold cyan]

    This is a short, guided walkthrough of the basics - a few fights, a trip to Camp, and a
    couple of level ups. Everything here is fixed (your class included) so it plays out the
    same way every time. Nothing you do here is saved.

    Press Enter whenever you're ready to continue.
    """)

    game.player = Warrior("Traveller")
    game.player._baseHealth = TUTORIAL_HEALTH
    game.player._recalculateStats(False)
    game.player._health = game.player._maxHealth
    game.camp = Camp(game.player)
    game.hardcoreMode = False

    _narrate("""
    [bold cyan]=== Your Character ===[/bold cyan]

    For this tutorial, you're playing a [class_warrior]Warrior[/class_warrior] - one of the simpler classes. A few stats to know:

    [health]Health[/health] - your HP. Hit 0 and you're defeated.
    [stamina]Stamina[/stamina] - spent on Abilities. Basic Attack is always free. [dim]The [class_mage]Mage[/class_mage] and [class_wretch]Wretch[/class_wretch] do not use [stamina]Stamina[/stamina].[/dim]
    [resource]Rage[/resource] - the Warrior's own resource. It builds as you deal and take damage, and adds bonus damage to your attacks.
    
    Every class has their own set of unique mechanics, the [class_warrior]Warrior's Rage[/class_warrior] mechanic is one of the simpler mechanics, hence its use in this tutorial.

    Every character also has [speed]Speed[/speed] (who acts first each round), [critical]Crit Chance[/critical]
    and [critical]Crit Multi[/critical] (odds and size of a critical hit), and [armour]Armour[/armour]/[evasion]Evasion[/evasion]
    (reducing or avoiding incoming damage).
    """)

    # -- Fight 1 -- #
    _narrate("""
    [bold cyan]=== Your First Fight ===[/bold cyan]

    A Training Dummy is about to attack. In combat, you'll pick an action each turn - Basic
    Attack (free) or one of your Abilities (costs Stamina, usually hits harder or does
    something extra). Turn order is decided by Speed - whoever's faster goes first.

    Give it a shot.
    """)
    dummy = _fixedEnemy("Training Dummy", level=1, health=15, damage=2, speed=0.5)
    _safeCombat(game, [dummy])
    _healToFull(game.player)
    _ensureLevel(game.player, 2)

    _narrate("""
    [bold cyan]=== After the Fight ===[/bold cyan]

    Winning a fight grants [xp]XP[/xp] (levels you up - more HP, more damage, new Abilities),
    [gold]Gold[/gold], and sometimes Resources or Equipment. You just leveled up - notice your
    stats went up automatically.
    """)

    # -- Camp -- #
    _narrate("""
    [bold cyan]=== Camp ===[/bold cyan]

    Between fights, you return to Camp. The Campfire heals you automatically after every
    victory - watch your HP.
    """)
    game.camp.campfire.applyHeal()
    _narrate("""
    Camp has several buildings, each unlocked and upgraded with resources you find while
    exploring: the [red]Campfire[/red] (healing), [yellow]Forge[/yellow] (crafting and repairing
    equipment), [green]Market[/green] (buying/selling), [blue]Quest Board[/blue] (milestones and
    bounties), [gold1]Shrine[/gold1] (Ascendancies, from level 20), and the Account Stash (shared
    storage across your characters). We won't visit all of them now - the in-game Help menu
    covers every one of these in detail.
    """)

    # -- Fight 2 -- #
    _narrate("""
    [bold cyan]=== Second Fight ===[/bold cyan]

    A Forest Wolf, a little tougher this time. You should have an Ability or two available
    now beyond Basic Attack - abilities usually hit harder or add an extra effect, at the cost
    of some Stamina. Keep an eye on your HP and Stamina bars as you go.
    """)
    wolf = _fixedEnemy("Forest Wolf", level=2, health=22, damage=3, speed=1.0)
    _safeCombat(game, [wolf])
    _healToFull(game.player)
    _ensureLevel(game.player, 3)

    _narrate("""
    [bold cyan]=== Loot & Equipment ===[/bold cyan]

    Equipment you find gets added to storage rather than worn automatically - check your
    Inventory to compare and equip new gear. Better rarities (shown by colour: Common,
    Uncommon, Rare, Epic, Legendary, and beyond) generally mean better stats and more of them.
    The Help menu's Equipment & Items section covers rarities, durability, and crafting.
    """)

    # -- Fight 3 -- #
    _narrate("""
    [bold cyan]=== Third Fight ===[/bold cyan]

    This time you're facing two enemies at once - Speed still decides turn order between
    everyone in the fight, allies and enemies alike, and you'll be able to choose which enemy
    to target with your attacks.
    """)
    scout = _fixedEnemy("Bandit Scout", level=3, health=18, damage=3, speed=1.1)
    thug = _fixedEnemy("Bandit Thug", level=3, health=28, damage=4, speed=0.6)
    _safeCombat(game, [scout, thug])
    _healToFull(game.player)
    _ensureLevel(game.player, 4)

    _narrate(f"""
    [bold cyan]=== That's the Basics ===[/bold cyan]

    You're now level {game.player._level}, and that covers the core loop: fight, level up,
    gear up, repeat. A few things to know for later - every class has its own resource and
    mechanics (yours was Rage), status effects like [dot]Bleed[/dot] or [cc]Stun[/cc] can turn
    a fight around either way, and at level 20 you'll choose an Ascendancy at the Shrine that
    reshapes how your class plays.

    The in-game [magenta]Help menu[/magenta] (from the options menu, or by typing a search phrase
    at any Help screen) covers everything in much more detail - status effects, damage types,
    every class and Ascendancy, camp buildings, crafting, and more.

    That's it! Returning you to the title screen - when you're ready, [green]New Game[/green]
    will let you pick your own class for real.
    """)
    printSuccess("Tutorial complete!")
    pause()

    game.player = None
    game.camp = None
