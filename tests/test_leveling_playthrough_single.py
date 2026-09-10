"""
Fast single-class companion to test_leveling_playthrough.py. Runs the base class plus every one
of its ascendancies (not every class in the game), so you can validate just what you're working
on instead of waiting on the full ~15 minute sweep. Two ways to pick the class:

    pytest tests/test_leveling_playthrough_single.py --target-class=Warrior -q
    (or edit DEFAULT_TARGET_CLASS below and run with no flag)

Same real-combat engine as test_leveling_playthrough.py (see that file's docstring) - this one
just narrows the class axis instead of running every parametrized case.
"""
import pytest

from scripts.styles import console
from scripts.player_classes.classes import CLASSES, ASCENDANCIES
from _playthroughLib import (
    BASE_TARGET_LEVEL, ASCENDANCY_TARGET_LEVEL, _makeImmortal, _levelPlayerTo, _getLevel20Player,
)

# used only when --target-class isn't passed on the command line
DEFAULT_TARGET_CLASS = "Warrior"


@pytest.fixture(autouse=True)
def _no_interactive_io(monkeypatch):
    monkeypatch.setattr(console, "input", lambda *args, **kwargs: "")
    monkeypatch.setattr(console, "print", lambda *args, **kwargs: None)


def pytest_generate_tests(metafunc):
    if "className" not in metafunc.fixturenames or "ascendancy" not in metafunc.fixturenames:
        return

    targetClass = metafunc.config.getoption("--target-class") or DEFAULT_TARGET_CLASS
    assert targetClass in CLASSES, (
        f"Unknown class {targetClass!r} - check CLASSES in scripts/player_classes/classes.py, or pass --target-class"
    )

    cases = [(targetClass, None)] + [(targetClass, asc) for asc in ASCENDANCIES.get(targetClass, [])]
    ids = [asc or "base" for _, asc in cases]
    metafunc.parametrize("className,ascendancy", cases, ids=ids)


def test_single_class_leveling_playthrough(className, ascendancy):
    label = f"{className}/{ascendancy or 'base'}"
    player = _getLevel20Player(className, label)
    assert player._level >= BASE_TARGET_LEVEL, f"{label}: snapshot restore landed below level {BASE_TARGET_LEVEL}"

    if ascendancy:
        assert player.updateAscendancy(ascendancy), f"{label}: failed to ascend into {ascendancy}"
        _makeImmortal(player)

        _levelPlayerTo(player, ASCENDANCY_TARGET_LEVEL, label)
        assert player._level >= ASCENDANCY_TARGET_LEVEL, f"{label}: never reached level {ASCENDANCY_TARGET_LEVEL}"
