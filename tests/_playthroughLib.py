"""
Shared helpers for the real-combat leveling playthrough tests (test_leveling_playthrough.py
and test_leveling_playthrough_single.py).
"""
import random
from copy import deepcopy
from typing import Dict

from scripts.combat import CombatManager
from scripts.enemies.enemy import createEnemy
from scripts.player import deserialisePlayer
from scripts.player_classes.classes import CLASSES

IMMORTAL_HEALTH = 10_000_000_000
BASE_TARGET_LEVEL = 20
ASCENDANCY_TARGET_LEVEL = 30
MAX_TURNS_PER_FIGHT = 200
MAX_FIGHTS_PER_RUN = 500

# className -> serialise()'d level-20 player, built once per class per test session. Levelling
# 1->20 is the expensive, repeated part of this suite (real combat, real enemy-AI subprocess
# calls per turn) - every ascendancy of a class would otherwise redo the identical climb from
# scratch. Cache the *data*, not a live Player, so each caller gets an independent object via
# deserialisePlayer() and can ascend/keep levelling without ever mutating another test's copy.
_level20SnapshotCache: Dict[str, dict] = {}


def _makeImmortal(player):
    player._baseHealth = IMMORTAL_HEALTH
    player._recalculateStats(False)
    player._health = player._maxHealth


def _pickAbility(player) -> str:
    """Randomly among whatever's currently usable, so a run samples the whole kit over time."""
    names = list(player._abilities.keys())
    random.shuffle(names)
    for name in names:
        canUse, _ = player._abilities[name].canUse(player)
        if canUse:
            return name
    return 'Basic Attack'


def _runFight(player, level: int, label: str):
    enemies = [createEnemy(max(1, level)) for _ in range(random.randint(1, 2))]
    cm = CombatManager()
    cm.startBattle(player, enemies)

    turns = 0
    while cm.battleActive:
        turns += 1
        assert turns < MAX_TURNS_PER_FIGHT, f"{label}: a fight exceeded {MAX_TURNS_PER_FIGHT} turns - likely stuck"

        if cm.checkBattleEnd():
            break

        currentUnit = cm.getCurrentUnit()
        if not currentUnit:
            break

        if currentUnit.team == 'player':
            player.onTurnStart(cm)
            if cm.checkBattleEnd():
                break
            aliveEnemies = [e for e in enemies if not e._isDead]
            if aliveEnemies:
                target = random.choice(aliveEnemies)
                cm.performAttack(player, target, _pickAbility(player))
        else:
            cm.enemyTurn(currentUnit.entity, [player])

        if cm.checkBattleEnd():
            break
        cm.nextTurn()

    for enemy in enemies:
        if enemy._isDead:
            player.gainExperience(enemy.getExperienceReward())

    player.onCombatEnd()
    _makeImmortal(player)  # onCombatEnd doesn't touch baseHealth, but keep _health topped up


def _levelPlayerTo(player, targetLevel: int, label: str):
    fights = 0
    while player._level < targetLevel:
        fights += 1
        assert fights < MAX_FIGHTS_PER_RUN, f"{label}: exceeded {MAX_FIGHTS_PER_RUN} fights trying to reach level {targetLevel}"
        _runFight(player, player._level, label)


def _getLevel20Player(className: str, label: str):
    """Returns a fresh, independent level-20 `className` player. The real 1->20 combat climb
    only ever runs once per class per test session (cached below); every call after that
    reconstructs a brand-new player via a serialise()/deserialise() round-trip of the cached
    snapshot, so one test ascending or levelling further can never leak into another's copy."""
    if className not in _level20SnapshotCache:
        seed = CLASSES[className](f"{className} Playthrough")
        _makeImmortal(seed)
        _levelPlayerTo(seed, BASE_TARGET_LEVEL, label)
        assert seed._level >= BASE_TARGET_LEVEL, f"{label}: never reached level {BASE_TARGET_LEVEL}"
        _level20SnapshotCache[className] = seed.serialise()

    player = deserialisePlayer(deepcopy(_level20SnapshotCache[className]))
    _makeImmortal(player)
    return player
