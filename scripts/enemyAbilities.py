from json import load
from typing import Dict, Optional, Tuple
from .abilities import Effects
import random

class EnemyAbility:
    def __init__(self, name: str, category: str, tier: int, levelReq: int,
                 cooldown: int, targets: int | str,
                 damageBase: int, damageScaling: float, damageType: Optional[str],
                 weight: int, effects: Dict, description: str):
        self.name = name
        self.category = category
        self.tier = tier
        self.levelReq = levelReq
        self.maxCooldown = cooldown
        self.cooldown = 0
        self.targets = targets
        self.damageBase = damageBase
        self.damageScaling = damageScaling
        self.damageType = damageType
        self.weight = weight
        self.effects = effects
        self.description = description

    def calculateDamage(self, enemyBaseDamage: int) -> int:
        return int(self.damageBase + (enemyBaseDamage * self.damageScaling))
    
    def canUse(self) -> Tuple[bool, str]:
        if self.cooldown > 0:
            return False, f"On cooldown for {self.cooldown} more turns."
        return True, ""
    
    @property
    def isDamaging(self) -> bool:
        return self.damageBase > 0 or self.damageScaling > 0
    
    def spawnedConsumableHeal(self) -> Optional[int]:
        """Returns heal amount if ability spawns a consumable, else None"""
        return self.effects.get('self', {}).get('spawn_consumable', {}).get('heal')

    def __str__(self) -> str:
        cdText = f"  Cooldown: {self.cooldown}" if self.cooldown > 0 else ""
        return f"{self.name}{cdText} | Tier: {self.tier} | {self.category}"
    
    def __repr__(self) -> str:
        return f"EnemyAbility({self.name!r}), tier={self.tier}, lvl={self.levelReq}"

def resolveEffects(effectsDict: Dict, attacker, target, combatManager):
    """Converts a raw effects sub-dict into StatusEffect objects and applies via combat manager"""
    for effectName, params in effectsDict.items():
        if effectName == 'spawn_consumable':
            continue

        statusEffects = []
        
        match effectName:
            # -- dots -- #
            case 'bleed':
                statusEffects = Effects.createBleed(params.get('stacks', 1))
            case 'burn':
                statusEffects = Effects.createBurn(params.get('stacks', 1))
            case 'poison':
                statusEffects = Effects.createPoison(params.get('stacks', 1))
            case 'curse':
                statusEffects = Effects.createCurse(params.get('curse', 1))
            # -- cc -- #
            case 'stun':
                if random.random() < params.get('chance', 1.0):
                    statusEffects = [Effects.createStun(params.get('turns', 1))]
            case 'freeze':
                if random.random() < params.get('chance', 1.0):
                    statusEffects = [Effects.createFreeze(params.get('turns', 1))]
            # -- debuffs -- #
            case 'chill':
                statusEffects = Effects.createChill(
                    params.get('stacks', 1), params.get('turns', 2), params.get('amount', 0.2)
                )
            case 'slow':
                statusEffects = [Effects.createSlow(
                    params.get('turns', 2), params.get('amount', 0.2)
                )]
            case 'blind':
                statusEffects = [Effects.createBlind(
                    params.get('turns', 3), params.get('amount', 0.2)
                )]
            case 'shock':
                statusEffects = [Effects.createShock(
                    params.get('turns', 3), params.get('amount', 0.2)
                )]
            case 'vulnerable':
                statusEffects = [Effects.createVulnerable(
                    params.get('turns', 2), params.get('amount', 0.2)
                )]
            case 'weaken':
                statusEffects = [Effects.createWeaken(
                    params.get('turns', 2), params.get('amount', 0.25)
                )]
            case 'exposed':
                statusEffects = [Effects.createExposed(
                    params.get('turns', 2), params.get('amount', 10)
                )]
            case 'elemental_exposure':
                statusEffects = [Effects.createElementalExposure(
                    params.get('turns', 3), params.get('amount', 30)
                )]
            case 'divine_exposure':
                statusEffects = [Effects.createDivineExposure(
                    params.get('turns', 3), params.get('amount', 30)
                )]
            case 'physical_exposure':
                statusEffects = [Effects.createPhysicalExposure(
                    params.get('turns', 3), params.get('amount', 30)
                )]
            case 'otherworld_exposure':
                statusEffects = [Effects.createOtherworldExposure(
                    params.get('turns', 3), params.get('amount', 30)
                )]
            case 'daze':
                statusEffects = [Effects.createDaze(
                    params.get('turns', 2), abs(params.get('speed', 0.1)), params.get('damage', 0.9)
                )]
            # -- buffs -- #
            case 'regeneration':
                pct = params.get('amount_percent', 0)
                statusEffects = [Effects.createRegeneration(
                    params.get('turns', 2), (pct / 100 if pct > 1 else pct), params.get('amount_flat', 0)
                )]
            case 'stoneskin':
                statusEffects = [Effects.createStoneskin(
                    params.get('turns', 2), params.get('amount', 0.1)
                )]
            case 'haste':
                statusEffects = [Effects.createHaste(
                    params.get('turns', 2), params.get('speed', 0.1), params.get('damage', 1.1)
                )]
        
        for effect in statusEffects:
            combatManager.addStatusEffect(target, effect, attacker)

def _buildEnemyAbility(data: Dict) -> EnemyAbility:
    rawScaling = data.get('damage_scaling', 0)
    scaling = rawScaling / 100 if rawScaling > 1 else rawScaling

    return EnemyAbility(
        data['name'], data['category'], data['tier'], data['level_req'], data['cooldown'],
        data['targets'], data.get('damage_base', 0), scaling, data.get('damage_type'),
        data['weight'], data.get('effects', {}), data['description']
    )

def loadEnemyAbilities() -> Dict[str, EnemyAbility]:
    with open('data/enemyAbilities.json', 'r') as f:
        data = load(f)
    return {name: _buildEnemyAbility(ability) for name, ability in data.items()}

ENEMY_ABILITIES: Dict[str, EnemyAbility] = loadEnemyAbilities()
