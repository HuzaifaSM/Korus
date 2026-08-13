import subprocess
import json
from os.path import dirname, abspath, join
from .entities import Entity
from .styles import console

_HERE = dirname(abspath(__file__))
_KORUS_ROOT = dirname(_HERE)
_AI_EXE = join(_KORUS_ROOT, "tools", "korus_enemy_ai.exe")

class EnemyAI:
    def __init__(self, enemy: Entity):
        self._enemy = enemy

    def buildActionList(self) -> list:
        """
        Builds action list of available actions for this enemy.\n
        Call once per enemy at turn start
        """
        actions = []

        # basic attack
        actions.append({
            "id": "basic_attack",
            "category": "attack",
            "damage": self._enemy._damage,
            "damageType": self._enemy._damageType,
            "cost": {},
            "effects": []
        })

        for name, ability in self._enemy._abilities.items():
            if name == "Basic Attack":
                continue
            canUse, _ = ability.canUse()
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

        # consumables
        for itemName, item in self._enemy._inventory.items():
            healVal = getattr(item, 'healAmount', None)
            if healVal:
                actions.append({
                    "id": itemName,
                    "category": "consumable",
                    "heal": healVal,
                    "cost": {},
                    "effects": []
                })

        return actions

    def applyDecision(self, decision: dict, player: Entity, combatManager):
        """Executes action Rust engine chose for this enemy"""       
        enemy = self._enemy 
        actionId = decision.get('actionId', 'basic_attack') if decision else 'basic_attack'

        if actionId == 'basic_attack':
            combatManager.performAttack(enemy, player, "Basic Attack")
            return

        if actionId in enemy._inventory:
            self._useConsumable(actionId)
            return

        if actionId in enemy._abilities:
            ability = enemy._abilities[actionId]
            self._useAbility(ability, player, combatManager)
            return

        combatManager.performAttack(enemy, player, "Basic Attack")

    # -- ability execution -- #
    def _useAbility(self, ability, player: Entity, combatManager):
        enemy = self._enemy

        console.print(f"\n[ability]{enemy._name}[/ability] uses [bold]{ability.name}[/bold]!")

        heal = ability.spawnedConsumableHeal()
        if heal:
            enemy.heal(heal)

        if ability.targets == 'self':
            damageTargets = []
        elif ability.targets == 'all':
            damageTargets = [u.entity for u in combatManager.getUnitsInTeam('player')]
        else:
            damageTargets = [player]

        # damage AND effects (ability.effects['target']/['self']) are both resolved inside
        # performAttack, uniformly for player- and enemy-used abilities
        if damageTargets:
            for t in damageTargets:
                combatManager.performAttack(enemy, t, abilityName=ability.name)
        elif ability.targets == 'self':
            combatManager.performAttack(enemy, enemy, abilityName=ability.name)

        ability.cooldown = ability.maxCooldown

    def _useConsumable(self, itemName: str):
        from .items import CONSUMABLES
        enemy = self._enemy
        amount = enemy._inventory.get(itemName)
        if amount is None or amount <= 0:
            return
        heal = CONSUMABLES.get(itemName)
        if heal:
            enemy.heal(heal)
        enemy._inventory[itemName] -= 1

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
            enemyStates.append({
                "index":            i,
                "hp":               enemy._health,
                "maxHp":            enemy._maxHealth,
                "damageType":       enemy._damageType,
                "resources":        EnemyAI._getResources(enemy),
                "availableActions": actions,
                "difficulty":       getattr(enemy, 'aiDifficulty', 0.5),
                "baseDamage":       enemy._damage,
            })
        return {
            "enemies": enemyStates,
            "player": {
                "hp":          player._health,
                "maxHp":       player._maxHealth,
                "resistances": EnemyAI._getResistance(player),
                "speed":       player._speed,
            }
        }

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
