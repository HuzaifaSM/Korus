"""
Round-trip tests for the ASCENDANCY_DELTAS / _applyStatDelta pattern used by every
player class (see scripts/player_classes/base.py and e.g. scripts/player_classes/warrior.py).

For every ascendancy on every class: 
- gaining it should change exactly the stats listed in its delta table by exactly the listed amount
- removing it should put every one of those stats back to precisely where it started.
"""
import pytest

from scripts.styles import console
from scripts.player_classes.warrior import Warrior
from scripts.player_classes.marauder import Marauder
from scripts.player_classes.wretch import Wretch
from scripts.player_classes.druid import Druid
from scripts.player_classes.spectre import Spectre
from scripts.player_classes.tempest import Tempest
from scripts.player_classes.cultist import Cultist
from scripts.player_classes.paladin import Paladin
from scripts.player_classes.mage import Mage
from scripts.player_classes.wanderer import Wanderer

CLASSES = [Warrior, Marauder, Wretch, Druid, Spectre, Tempest, Cultist, Paladin, Mage, Wanderer]

def _resolve(entity, path: str):
    parts = path.split('.')
    target = entity
    for p in parts[:-1]:
        target = target[p] if isinstance(target, dict) else getattr(target, p)
    return target, parts[-1]


def _snapshot(entity, delta: dict) -> dict:
    snap = {}
    for path in delta:
        target, leaf = _resolve(entity, path)
        snap[path] = target[leaf] if isinstance(target, dict) else getattr(target, leaf)
    return snap


def _cases():
    for cls in CLASSES:
        for ascendancy in cls.ASCENDANCY_DELTAS:
            yield cls, ascendancy


@pytest.fixture(autouse=True)
def _no_interactive_pauses(monkeypatch):
    """prevents pause() calls blocking tests from running"""
    monkeypatch.setattr(console, "input", lambda *args, **kwargs: "")

@pytest.mark.parametrize("cls,ascendancy", list(_cases()))
def test_ascendancy_gain_and_removal_round_trip(cls, ascendancy):
    delta = cls.ASCENDANCY_DELTAS[ascendancy]
    entity = cls("Test")

    before = _snapshot(entity, delta)
    entity.updateAscendancy(ascendancy)
    after = _snapshot(entity, delta)

    for path, amount in delta.items():
        assert after[path] == pytest.approx(before[path] + amount), (
            f"{cls.__name__}/{ascendancy}: gaining should change '{path}' "
            f"by {amount}, went {before[path]} -> {after[path]}"
        )

    entity._removeOldAscendancy()
    reverted = _snapshot(entity, delta)

    for path in delta:
        assert reverted[path] == pytest.approx(before[path]), (
            f"{cls.__name__}/{ascendancy}: removing should restore '{path}' "
            f"to {before[path]}, got {reverted[path]}"
        )
