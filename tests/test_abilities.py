"""
Coverage for the ability system across every class/ascendancy combination.

Two things are checked:
- structural: every populated ascendancy entry in data/abilities.json corresponds to a real,
  currently-selectable ascendancy for that class. Classes get reworked over time and their
  ascendancy names change; abilities.json previously carried several silently-unreachable
  stubs left over from before a rework (e.g. Warrior's "Blood Reaver", Fighter's entire old
  ascendancy set) - this guards against ever reintroducing that.
- smoke: for every class, at max level, with no ascendancy and with every real ascendancy,
  every ability the player knows can actually be cast against a dummy enemy without raising,
  and goes on cooldown afterward. This does not assert exact damage numbers (those change as
  balance passes happen) - it exists to catch crashes, typos in effect/tag keys, and abilities
  that silently never go on cooldown (the bug fixed in combat.py for heal-category abilities).
"""
import pytest

from scripts.styles import console
from scripts.abilities import CLASS_ABILITIES
from scripts.combat import CombatManager
from scripts.enemy import Enemy
from scripts.player_classes.classes import CLASSES, ASCENDANCIES

DUMMY_HEALTH = 10_000_000
MAX_LEVEL = 100


@pytest.fixture(autouse=True)
def _no_interactive_io(monkeypatch):
    """Prevents any stray console.input() prompt from blocking the sweep, and keeps output quiet."""
    monkeypatch.setattr(console, "input", lambda *args, **kwargs: "")
    monkeypatch.setattr(console, "print", lambda *args, **kwargs: None)


def _makeDummy(level: int = 50) -> Enemy:
    dummy = Enemy("Dummy", level=level)
    dummy._health = dummy._maxHealth = DUMMY_HEALTH
    return dummy


def _makeBattle(player):
    dummy1, dummy2 = _makeDummy(), _makeDummy()
    cm = CombatManager()
    cm.startBattle(player, [dummy1, dummy2])
    return cm, dummy1, dummy2


def _cases():
    for className in CLASSES:
        yield className, None
        for ascendancy in ASCENDANCIES.get(className, []):
            yield className, ascendancy


def test_no_orphaned_ascendancy_ability_data():
    for className, ascendancyData in CLASS_ABILITIES.items():
        if className not in ASCENDANCIES:
            continue
        realNames = set(ASCENDANCIES[className])
        for ascName, entry in ascendancyData.items():
            if ascName == 'base':
                continue
            hasContent = bool(entry.get('alterations')) or bool(entry.get('abilities'))
            if hasContent:
                assert ascName in realNames, (
                    f"{className}/{ascName} has populated ability data but is not a real, "
                    f"currently-selectable ascendancy (real ascendancies: {sorted(realNames)}). "
                    f"This usually means a stale/renamed stub left over from before the class "
                    f"was reworked - the content is unreachable in-game."
                )


@pytest.mark.parametrize("className,ascendancy", list(_cases()))
def test_every_known_ability_can_be_cast(className, ascendancy):
    player = CLASSES[className](f"{className} Test")
    for _ in range(MAX_LEVEL - 1):
        player._levelUp()

    if ascendancy:
        assert player.updateAscendancy(ascendancy), f"{className} failed to ascend into {ascendancy}"

    abilityNames = list(player._abilities.keys())
    label = f"{className}/{ascendancy or 'base'}"
    assert abilityNames, f"{label} has no abilities at level {MAX_LEVEL}"

    for name in abilityNames:
        cm, dummy1, dummy2 = _makeBattle(player)
        player._health = player._maxHealth
        player._stamina = player._maxStamina

        ability = player._abilities[name]
        maxCooldown = ability.maxCooldown

        try:
            cm.performAttack(player, dummy1, name)
        except Exception as e:
            pytest.fail(f"{label}: casting '{name}' raised {type(e).__name__}: {e}")

        if maxCooldown > 0:
            assert ability.cooldown == maxCooldown, (
                f"{label}: '{name}' should be on cooldown ({maxCooldown}) immediately after use, "
                f"got {ability.cooldown} - it may never actually lock out reuse in a real battle."
            )
