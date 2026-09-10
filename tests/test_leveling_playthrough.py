"""
Full multi-turn combat playthroughs, one per class and one per ascendancy.

This is a different, slower layer of coverage than test_abilities.py: that file casts each
ability once against a static dummy (no retaliation, no turn loop, no multi-turn state).
Here the player actually fights real, leveling enemies turn by turn - real turn order, real
enemy AI retaliation (onHit, defensive mechanics), real onTurnStart/onTurnEnd ticks, and
mechanics that only build up over several real turns (Transgressor's stance cap, Dissenter's
Impatience, Colossus's once-per-combat Energy Shield break, etc.).

The player's base health is set absurdly high so it can never actually die - death would abort
the run without telling us anything useful; the point is to catch crashes across a realistic
leveling arc, not to model fair combat. Ability choice each turn is randomised among whatever
is currently usable (ability.canUse()), so a run exercises a broad, varied slice of the kit
rather than spamming one attack.

Slow by design (a full sweep runs real combat to level 20 for every class, then level 20->30
for every ascendancy on top of that) - not meant to run on every quick iteration.
"""
import pytest

from scripts.styles import console
from scripts.player_classes.classes import CLASSES, ASCENDANCIES
from _playthroughLib import (
    BASE_TARGET_LEVEL, ASCENDANCY_TARGET_LEVEL, _makeImmortal, _levelPlayerTo, _getLevel20Player,
)


@pytest.fixture(autouse=True)
def _no_interactive_io(monkeypatch):
    """Every interactive prompt in the game degrades to a safe default on empty input
    (no-skew, no-sacrifice, first-listed Pact, etc.) - none of them loop on invalid input,
    so this can't hang."""
    monkeypatch.setattr(console, "input", lambda *args, **kwargs: "")
    monkeypatch.setattr(console, "print", lambda *args, **kwargs: None)


def _cases():
    for className in CLASSES:
        yield className, None
        for ascendancy in ASCENDANCIES.get(className, []):
            yield className, ascendancy


@pytest.mark.parametrize("className,ascendancy", list(_cases()))
def test_leveling_playthrough(className, ascendancy):
    label = f"{className}/{ascendancy or 'base'}"
    player = _getLevel20Player(className, label)
    assert player._level >= BASE_TARGET_LEVEL, f"{label}: snapshot restore landed below level {BASE_TARGET_LEVEL}"

    if ascendancy:
        assert player.updateAscendancy(ascendancy), f"{label}: failed to ascend into {ascendancy}"
        _makeImmortal(player)

        _levelPlayerTo(player, ASCENDANCY_TARGET_LEVEL, label)
        assert player._level >= ASCENDANCY_TARGET_LEVEL, f"{label}: never reached level {ASCENDANCY_TARGET_LEVEL}"
