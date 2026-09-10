import subprocess
import json
import random
from os.path import dirname, abspath, join
from ..entities import Entity
from ..styles import console

_HERE = dirname(abspath(__file__))
_KORUS_ROOT = dirname(_HERE)
_AI_EXE = join(_KORUS_ROOT, "tools", "korus_enemy_ai.exe")

class EnemyAI:
    def __init__(self, enemy: Entity):
        self._enemy = enemy

    def buildActionList(self, allies: list = None) -> list:
        """
        Builds action list of available actions for this enemy.\n
        Call once per enemy at turn start.\n
        `allies` should be the full living enemy-team roster (this enemy included) -
        needed so Support-class enemies can tell whether a basic heal is available.
        """
        actions = []
        enemy = self._enemy

        isSupport = getattr(enemy, 'className', None) is not None and enemy.className.value == 'support'
        ascendancy = getattr(enemy, '_ascendancy', None)
        isHealer = ascendancy is not None and ascendancy.value == 'healer'
        livingAllies = [a for a in (allies or []) if a is not enemy and not a._isDead]

        basicAttackAction = {
            "id": "basic_attack",
            "category": "attack",
            "damage": enemy._damage,
            "damageType": enemy._damageType,
            "cost": {},
            "effects": []
        }

        if isSupport and livingAllies:
            # basic heal: replaces basic attack entirely while allies are alive to heal (per enemy rework TODO)
            actions.append({
                "id": "basic_heal",
                "category": "heal",
                "heal": int(enemy._maxHealth * 0.10),
                "cost": {},
                "effects": []
            })
            if isHealer:
                # healers specifically keep basic attack too - a failsafe for when they have
                # no way to save themselves (all self-heals on cooldown) and are about to die,
                # since their normal healing kit only benefits allies, not themselves
                actions.append(basicAttackAction)
        else:
            actions.append(basicAttackAction)

        for name, ability in self._enemy._abilities.items():
            if name == "Basic Attack":
                continue
            canUse, _ = ability.canUse(self._enemy)
            if not canUse:
                continue

            rustEffects = _flattenEffects(ability.effects)

            actions.append({
                "id": ability.name,
                "category": ability.category,
                "damage": ability.calculateDamage(self._enemy._damage) if ability.isDamaging else 0,
                "damageType": ability.damageType or self._enemy._damageType,
                "cost": {},
                "effects": rustEffects,
            })

        return actions

    def applyDecision(self, decision: dict, player: Entity, combatManager):
        """Executes action Rust engine chose for this enemy"""
        enemy = self._enemy

        # consumable use is a free action (matches the player's own consumable use) -
        # it happens regardless of, and before, whatever the main action turns out to be
        if decision and decision.get('useConsumable') and enemy.consumable.useable:
            self._useConsumable()

        actionId = decision.get('actionId', 'basic_attack') if decision else 'basic_attack'

        if actionId == 'basic_attack':
            combatManager.performAttack(enemy, player, "Basic Attack")
            return

        if actionId == 'basic_heal':
            self._useBasicHeal(decision, player, combatManager)
            return

        if actionId in enemy._abilities:
            ability = enemy._abilities[actionId]
            self._useAbility(ability, player, combatManager)
            return

        combatManager.performAttack(enemy, player, "Basic Attack")

    def _useBasicHeal(self, decision: dict, player: Entity, combatManager):
        """
        Heals the ally the Rust engine identified as neediest (lowest HP%).
        Costs the caster HP equal to 50% of the amount healed.
        Falls back to a basic attack if no valid ally is found (e.g. they died
        earlier in the same round, between snapshot-build and this decision).
        """
        enemy = self._enemy
        allies = combatManager.allAlive
        allyIndex = decision.get('allyTargetIndex') if decision else None
        ally = allies[allyIndex] if allyIndex is not None and 0 <= allyIndex < len(allies) else None

        if ally is None or ally is enemy or ally._isDead:
            combatManager.performAttack(enemy, player, "Basic Attack")
            return

        healAmount = int(enemy._maxHealth * 0.10)
        selfCost = int(healAmount * 0.5)

        console.print(f"\n[ability]{enemy._name}[/ability] channels a healing surge into [bold]{ally._name}[/bold]!")
        ally.heal(healAmount, reason="Basic Heal")
        enemy.damage(selfCost, 'true')

    # -- ability execution -- #
    def _useAbility(self, ability, player: Entity, combatManager):
        enemy = self._enemy

        console.print(f"\n[ability]{enemy._name}[/ability] uses [bold]{ability.name}[/bold]!")

        primaryTarget = enemy
        healRecipients = [enemy]
        if ability.targets == 'ally':
            primaryTarget = self._pickAlly(combatManager) or enemy  # no living ally - fall back to self
            healRecipients = [primaryTarget]
        elif ability.targets == 'all_allies':
            healRecipients = list(combatManager.allAlive)

        heal = ability.spawnedConsumableHeal()
        if heal:
            for recipient in healRecipients:
                recipient.heal(heal)

        if ability.targets in ('self', 'ally', 'all_allies'):
            damageTargets = []
        elif ability.targets == 'all':
            damageTargets = [u.entity for u in combatManager.getUnitsInTeam('player')]
        else:
            damageTargets = [player]

        # damage, effects (ability.effects['target']/['self']), AND cooldown-setting-on-success
        # are all resolved inside performAttack, uniformly for player- and enemy-used abilities.
        # for 'all_allies' abilities, performAttack itself resolves the real recipient list
        # (self.allAlive) for the effects application - the target passed here doesn't matter.
        if damageTargets:
            for t in damageTargets:
                combatManager.performAttack(enemy, t, abilityName=ability.name)
        else:
            combatManager.performAttack(enemy, primaryTarget, abilityName=ability.name)

    def _pickAlly(self, combatManager):
        """Picks a random living ally (never self). Returns None if none are alive."""
        enemy = self._enemy
        allies = [a for a in combatManager.allAlive if a is not enemy and not a._isDead]
        return random.choice(allies) if allies else None

    def _useConsumable(self):
        enemy = self._enemy
        console.print(f"\n[ability]{enemy._name}[/ability] uses [bold]{enemy.consumable.name}[/bold]!")
        enemy.useConsumable()

    # -- turn-level static method -- #
    @staticmethod
    def decideTurn(enemies: list[Entity], player: Entity, actionLists: list) -> dict:
        """
        Sends full round snapshot to Rust Engine.\n
        Returns: dict { enemyIndex: decision } or empty dict on failure
        """
        snapshot = EnemyAI._buildSnapshot(enemies, player, actionLists)
        response = EnemyAI._callEngine(snapshot)
        if response is None:
            return {}
        return {
            d['enemyIndex']: d
            for d in response.get('decisions', [])
            if 'error' not in d
        }

    @staticmethod
    def _buildSnapshot(enemies: list[Entity], player: Entity, actionLists: list) -> dict:
        enemyStates = []
        for i, (enemy, actions) in enumerate(zip(enemies, actionLists)):
            consumableUseable = enemy.consumable.useable
            enemyStates.append({
                "index":              i,
                "hp":                 enemy._health,
                "maxHp":              enemy._maxHealth,
                "damageType":         enemy._damageType,
                "resources":          EnemyAI._getResources(enemy),
                "resistances":        EnemyAI._getResistance(enemy),
                "availableActions":   actions,
                "difficulty":         getattr(enemy, 'aiDifficulty', 0.5),
                "rarity":             enemy.rarity.value if hasattr(enemy, 'rarity') else 'common',
                "className":          enemy.className.value if getattr(enemy, 'className', None) else 'attacker',
                "ascendancy":         enemy._ascendancy.value if getattr(enemy, '_ascendancy', None) else None,
                "baseDamage":         enemy._damage,
                "consumableAvailable": consumableUseable,
                "consumableHeal":      int(enemy._maxHealth * enemy.consumable.healPercent) if consumableUseable else None,
            })
        return {
            "enemies": enemyStates,
            "player": {
                "hp":          player._health,
                "maxHp":       player._maxHealth,
                "resistances": EnemyAI._getResistance(player),
                "speed":       player._speed,
                "damage":      player._damage,
                "damageType":  player._damageType,
                "abilities":   EnemyAI._getPlayerDamagingAbilities(player),
            }
        }

    @staticmethod
    def _getPlayerDamagingAbilities(player: Entity) -> list:
        """Resolved damage numbers for every damaging player ability - used by the
        engine's lethal-threat check. Only damaging abilities are included."""
        result = []
        for ability in player._abilities.values():
            isDamaging = getattr(ability, 'baseDamage', 0) > 0 or getattr(ability, 'damageScaling', 0) > 0
            if not isDamaging:
                continue
            result.append({
                "damage":     ability.calculateDamage(player._damage),
                "damageType": ability.damageType or player._damageType,
            })
        return result

    @staticmethod
    def _callEngine(snapshot: dict) -> dict | None:
        try:
            result = subprocess.run(
                [_AI_EXE],
                input=json.dumps(snapshot),
                capture_output=True,
                text=True,
                timeout=2
            )
            if result.returncode != 0:
                console.print(f"[warning][AI Engine Error] {result.stderr.strip()}[/warning]")
                return None
            return json.loads(result.stdout.strip())
        except (subprocess.TimeoutExpired, json.JSONDecodeError, FileNotFoundError) as e:
            console.print(f"[warning][AI Engine Failed: {e}] Falling back to basic attacks[/warning]")
            return None
        
    @staticmethod
    def _getResistance(player: Entity) -> dict:
        damageTypes = [
            'physical', 'fire', 'cold', 'lightning', 'wind', 'earth',
            'holy', 'dark', 'arcane', 'psychic', 'ethereal', 'chaos'
        ]
        return {
            dt: res
            for dt in damageTypes
            if (res := player._stats['Resistances'].get(dt, 0)) != 0
        }
    
    @staticmethod
    def _getResources(enemy: Entity) -> dict:
        resources = {}
        for attr in ('_mana', '_rage', '_stamina'):
            if hasattr(enemy, attr):
                resources[attr.lstrip('_')] = getattr(enemy, attr)
        return resources
    
# -- flatten effects: converts nested effects dict to flat list for rust engine

EFFECT_TYPES = {
    'bleed': 'dot', 'burn': 'dot', 'poison': 'dot', 'curse': 'dot',
    'stun': 'cc', 'freeze': 'cc',
    'chill': 'debuff', 'slow': 'debuff', 'blind': 'debuff', 'vulnerable': 'debuff',
    'shock': 'debuff', 'weaken': 'debuff', 'exposed': 'debuff', 'daze': 'debuff',
    'elemental_exposure': 'debuff', 'physical_exposure': 'debuff',
    'divine_exposure': 'debuff', 'otherworld_exposure': 'debuff',
    'haste': 'buff', 'stoneskin': 'buff', 'regeneration': 'buff',
}

def _flattenEffects(effects: dict) -> list:
    result = []
    for targetSide, effectDict in effects.items():
        for effectName, params in effectDict.items():
            if effectName == 'spawn_consumable':
                continue
            result.append({
                'mechanic': effectName, 'effectType': EFFECT_TYPES.get(effectName, 'debuff'), 'target': targetSide, **params
            })
    return result
