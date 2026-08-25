from json import load
from copy import deepcopy
from typing import Optional, List, Dict, Any, Tuple
import random
from .styles import console

#=========================================================================================#

class Ability:
    def __init__(self, name: str, category: str, tags: List[str], staminaCost: int,
                 baseDamage: int, damageScaling: float, damageType: str,
                 healBase: int, healPercent: float,
                 cooldown: int, targets: int | str,
                 resources: Dict, effects: Dict, requirements: Dict,
                 description: str):
        self.name = name
        self.category = category
        self.tags = tags
        self.staminaCost = staminaCost

        self.baseDamage = baseDamage
        self.damageScaling = damageScaling
        self.damageType = damageType

        self.healBase = healBase
        self.healPercent = healPercent

        self.maxCooldown = cooldown
        self.cooldown = 0
        self.targets = targets

        self.resources = resources
        self.effects = effects
        self.requirements = requirements

        self.description = description

    # -- true values -- #
    def calculateDamage(self, playerDamage: int) -> int:
        return max(0 ,int(self.baseDamage + (playerDamage * self.damageScaling)))

    def calculateHeal(self, playerMaxHp: int) -> int:
        return max(0, int(self.healBase + (playerMaxHp * self.healPercent)))
    
    # -- resources -- #
    def canUse(self, player) -> Tuple[bool, str]:
        if self.cooldown > 0:
            return False, f"On cooldown for {self.cooldown} more turns."

        if not player.canUseAbility(self):
            return False, f"{player._name} does not have enough stamina."

        required: Dict[str, Any] = self.resources.get('required', {})
        for resource, amount in required.items():
            if resource == 'form':
                if amount.lower() != player.form.lower() and not player.bypassesFormRequirement():
                    return False, f"{player._name} is not in the correct Form. Form Required: {amount.title()}"
            else:
                resolved = _resolveResourceAmount(player, resource, amount)
                playerVal = getattr(player, f'_{resource}', None)
                if playerVal is None: # check if resource doesn't have underscore before it
                    playerVal = getattr(player, resource, 0)
                if playerVal < resolved:
                    return False, f"Not enough {resource}: {playerVal} / {resolved}"

        return True, ""
    
    def _checkRequirements(self, player) -> Tuple[bool, str]:
        req = self.requirements
        if 'form' in req:
            currentForm = getattr(player, 'form', 'human')
            if currentForm != req['form']:
                return False, f"Requires {req['form']} form."
        # extra checks here when added
            
        return True, ""
    
    # -- use -- #
    def applyResourceCosts(self, player):
        """Deduct required resouces and grant resources"""
        required = self.resources.get('required', {})
        for resource, amount in required.items():
            if resource == 'form':
                continue
            resolved = _resolveResourceAmount(player, resource, amount)
            if resource == 'health':
                player.spendHealthForAbility(resolved)
                continue
            attr = f'_{resource}' if hasattr(player, f'_{resource}') else resource
            setattr(player, attr, getattr(player, attr) - resolved)

        gained = self.resources.get('gain', {})
        for resource, amount in gained.items():
            if resource == 'energy_shield':
                player._stats['energy_shield'] = min(player.maxEnergyShield, player.energyShield + amount)
            else:
                attr = f'_{resource}' if hasattr(player, f'_{resource}') else resource
                current = getattr(player, attr, 0)
                mAttr = _findMaxAttr(player, attr)
                if mAttr is not None: # max value
                    setattr(player, attr, min(getattr(player, mAttr), current + amount))
                else:
                    setattr(player, attr, current + amount)

    # -- display -- #
    def __str__(self) -> str:
        cdText = f'[red]Cooldown: {self.cooldown}[/red] | ' if self.cooldown > 0 else ''
        targetText = str(self.targets) if isinstance(self.targets, int) else self.targets
        return f'{self.name} | {cdText}Targets: {targetText}'

    def __rich__(self) -> str:
        return self.__str__()

class BasicAttack(Ability):
    def __init__(self):
        super().__init__('Basic Attack', "damage", ["damage"], 0, 0, 1.0, None,
                         0, 0, 0, 1, {}, {}, {}, "Strike the enemy with a basic attack.")

class AbilityTree:
    def __init__(self, baseData: Dict, evolutions: Dict[int, Dict]):
        self.baseData = baseData
        self.evolutions = evolutions

    # -- ability -- #
    def getCurrentAbility(self, playerLevel: int, ascendancyOverlay: Optional[Dict] = None) -> Optional[Ability]:
        if self.baseData['level'] > playerLevel:
            return None

        data = deepcopy(self.baseData)
        for lvl in sorted(lvl for lvl in self.evolutions if lvl <= playerLevel):
            data = _mergeAbilityData(data, self.evolutions[lvl])

        if ascendancyOverlay:
            data = _mergeAbilityData(data, ascendancyOverlay)

        return self._buildAbility(data)

    def _buildAbility(self, data: Dict) -> Ability:
        dScale = data.get('damage_scaling', 0)
        dScaling = dScale / 100 if dScale >= 1 else dScale
        hScale = data.get('heal_percent', 0)
        hScaling = hScale / 100 if hScale >= 1 else hScale

        return Ability(
            data['name'], data['category'], data.get('tags', []), data.get('stamina_cost'),
            data.get('damage_base', 0), dScaling, data.get('damage_type'), data.get('heal_base', 0), hScaling,
            data.get('cooldown', 0), data.get('targets', 1), data.get('resources', {}), data.get('effects', {}), data.get('requirements', {}),
            data.get('description', ''),
        )

# -- helpers -- #
def _mergeAbilityData(base: Dict, overlay: Dict) -> Dict:
    result = deepcopy(base)

    for k, v in overlay.items():
        if k == 'description+':
            result['description'] = result.get('description', '') + '\n' + v
        elif k.endswith('+'):
            field = k[:-1]
            if field in ('effects', 'resources'):
                result[field] = _deepMergeEffects(result.get(field, {}), v)
            elif field == 'tags':
                existing = result.get('tags', [])
                result['tags'] = list(set(existing) | set(v))
            elif field == 'cooldown':
                result['cooldown'] = max(0, result.get('cooldown', 0) + v)
            elif isinstance(result.get(field), (int, float)):
                result[field] = result.get(field, 0) + v
            else:
                result[field] = v
        else:
            result[k] = v

    return result

def _deepMergeEffects(base: Dict, overlay: Dict) -> Dict:
    result = deepcopy(base)
    for k, v in overlay.items():
        if k.endswith('+'):
            field = k[:-1]
            if field in result and isinstance(result[field], (int, float)):
                result[field] += v
            else:
                result[field] = v
        elif isinstance(v, dict) and k in result and isinstance(result[k], dict):
            result[k] = _deepMergeEffects(result[k], v)
        else:
            result[k] = deepcopy(v)
    return result

def _findMaxAttr(player, attr: str) -> Optional[str]:
    x = attr.lstrip('_')
    capitalised = x[0].upper() + x[1:]
    for candidate in (f'_max{capitalised}', f'max{capitalised}', f'_max{x}', f'max{x}'):
        if hasattr(player, candidate):
            return candidate
    return None

def _resolveResourceAmount(player, resource: str, amount) -> int:
    if not isinstance(amount, dict):
        return amount
    if 'damage_type' not in amount:
        return int(amount.get('amount', 0))

    pct = amount.get('amount', 0)
    pct = pct / 100 if pct >= 1 else pct

    attr = f'_{resource}' if hasattr(player, f'_{resource}') else resource
    maxAttr = _findMaxAttr(player, attr)
    maxVal = getattr(player, maxAttr, 0) if maxAttr else 0

    return int(maxVal * pct)

def _buildEvolutions(evoData: Dict[str, Dict], baseName: str) -> Dict[int, Dict]:
    evolutions = {}
    for levelStr, data in evoData.items():
        fullData = deepcopy(data)
        fullData.setdefault('name', baseName)
        evolutions[int(levelStr)] = fullData
    return evolutions

#=========================================================================================#

DAMAGE_TYPES = [
    'physical', 'fire', 'cold', 'lightning', 'dark', 'holy', 'arcane',
    'earth', 'psychic', 'ethereal', 'chaos'
]

#=========================================================================================#

class StatusEffect:
    def __init__(self, name: str, effectType: str, turns: int, attacker=None, target=None, **kwargs):
        self.name = name
        self.effectType = effectType
        self.turns = turns
        self.attacker = attacker
        self.target = target
        self.applied = False
        self.data = kwargs

    def __repr__(self):
        return f"StatusEffect({self.name}, type={self.effectType}, turns={self.turns})"
    
    def toDict(self) -> Dict[str, Any]:
        return {
            'name': self.name,
            'type': self.effectType,
            'turns': self.turns,
            **self.data
        }

    def _applySecondaryEffect(self, inverse: bool = False):
        mult = 1 if not inverse else -1
        if self.name == 'bleed':
            self.target._stats['Temporary']['speed'] -= self.data['speedReduction'] * mult
        elif self.name == 'poison':
            self.target._stats['Temporary']['healing_magnitude'] -= self.data['healingReduction'] * mult
        elif self.name in ['stun', 'freeze']:
            self.target._stats['Temporary']['stun_avoidance'] += self.data['grantsAvoidance'] * mult
        elif self.name in ['chill', 'slow']:
            self.target._stats['Temporary']['speed'] -= self.data['amount'] * mult
        elif self.name == 'daze':
            self.target._stats['Temporary']['speed'] -= self.data['speedReduction'] * mult
        elif self.name == 'haste':
            self.target._stats['Temporary']['speed'] += self.data['speedBonus'] * mult
        elif self.name == 'shield_generation':
            if not inverse:
                amount = int(self.attacker._maxHealth * self.data.get('shieldAmount', 0))
                self.data['_grantedShield'] = amount
                self.target._shield += amount
            else:
                granted = self.data.get('_grantedShield', 0)
                self.target._shield = max(0, self.target._shield - granted)

    def tick(self) -> bool:
        if not self.applied:
            self._applySecondaryEffect()
            self.applied = True

        if self.effectType == 'dot':
            damage = self.data['baseDamage'] + int(self.attacker._damage * self.data['damagePercent'])
            damageType = self.data.get('damageType')
            dotResistance = self.target._stats['Bonuses'].get('dot_resistance', 0)
            if dotResistance > 0:
                damage = int(damage * (1 - (dotResistance / 100)))
                if damage < 0:
                    damage = 0

            if self.target.className == 'Rogue' and self.target._ascendancy == 'Shadow' and self.name == 'poison':
                damage //= 2

            self.target.damage(damage, damageType)
            console.print(f" - [dot]{self.name}[/dot] deals [damage]{damage}[/damage] damage")

        elif self.name == 'regeneration':
            healAmount = self.data.get('healFlatPerTurn', 0) + int(self.attacker._maxHealth * self.data.get('healPercentPerTurn', 0))
            if healAmount > 0:
                self.target.heal(healAmount)

        self.turns -= 1
        if self.turns == 0:
            self._applySecondaryEffect(True)
            return True
        return False

# one class to store all factory functions to reduce imports
class Effects:
    """A class holding every factory function for creating ailments. Contains:\n
    (all methods begin with create)\n
    - Bleed
    - Burn
    - Poison
    - Curse
    - Stun
    - Freeze
    - Chill
    - Slow
    - Blind
    - Shock
    - Vulnerable
    - Weaken
    - Exposed
    - Elemental Exposure
    - Divine Exposure
    - Physical Exposure
    - Otherworld Exposure
    - Daze (speed+dmg reduction)
    - Shield Generation
    - Regeneration
    - Haste (speed+dmg multiplier)
    - Stokeskin
    """
    @staticmethod
    def createBleed(stacks: int = 1) -> List[StatusEffect]:
        return [StatusEffect('bleed', 'dot', turns=3, damageType='physical',
                            baseDamage=8, damagePercent=0.1, speedReduction=0.05)
                            for _ in range(stacks)]

    @staticmethod
    def createBurn(stacks: int = 1) -> List[StatusEffect]:
        return [StatusEffect('burn', 'dot', turns=2, damageType='fire',
                            baseDamage=10, damagePercent=0.12, resistanceReduction=5)
                            for _ in range(stacks)]

    @staticmethod
    def createPoison(stacks: int = 1) -> List[StatusEffect]:
        return [StatusEffect('poison', 'dot', turns=3, damageType='chaos',
                            baseDamage=6, damagePercent=0.08, healingReduction=10)
                            for _ in range(stacks)]

    @staticmethod
    def createCurse(stacks: int = 1) -> List[StatusEffect]:
        return [StatusEffect('curse', 'dot', turns=4, damageType='dark',
                            baseDamage=12, damagePercent=0.15, ignoresResistance=True)
                            for _ in range(stacks)]

    @staticmethod
    def createStun(turns: int = 1, chance: int = 100) -> StatusEffect:
        return StatusEffect("stun", "cc", turns=turns, effect="cannot_act",
                        grantsAvoidance=50, chance=chance)

    @staticmethod
    def createFreeze(turns: int = 1, chance: int = 100) -> StatusEffect:
        return StatusEffect("freeze", "cc", turns=turns, effect="cannot_act",
                        critDamageTaken=0.25, grantsAvoidance=50, chance=chance)

    @staticmethod
    def createChill(stacks: int = 1, turns: int = 2, amount: float = 0.2) -> List[StatusEffect]:
        return [StatusEffect("chill", "debuff", turns=turns, amount=amount)
                for _ in range(stacks)]
    
    @staticmethod
    def createSlow(turns: int = 2, amount: float = 0.2) -> StatusEffect:
        return StatusEffect("slow", "debuff", turns=turns, amount=amount)

    @staticmethod
    def createBlind(turns: int = 3, amount: float = 0.2) -> StatusEffect:
        return StatusEffect("blind", "debuff", turns=turns, amount=amount)

    @staticmethod
    def createVulnerable(turns: int = 2, amount: float=0.5) -> StatusEffect:
        return StatusEffect("vulnerable", "debuff", turns=turns, 
                        damageTakenMultiplier=amount)

    @staticmethod
    def createShock(turns: int = 3, amount: float=0.2) -> StatusEffect:
        return StatusEffect("shock", "debuff", turns=turns,
                            damageTakenMultiplier=amount)

    @staticmethod
    def createWeaken(turns: int = 2, amount: float=0.25) -> StatusEffect:
        return StatusEffect("weaken", "debuff", turns=turns,
                        damageDealtReduction=amount)

    @staticmethod
    def createExposed(turns: int = 2, amount: int=10) -> StatusEffect:
        return StatusEffect("exposed", "debuff", turns=turns,
                        allResistanceReduction=amount)

    @staticmethod
    def createElementalExposure(turns: int = 3, amount: int=30) -> StatusEffect:
        return StatusEffect("elemental_exposure", "debuff", turns=turns,
                        elementalResistanceReduction=amount)

    @staticmethod
    def createDivineExposure(turns: int = 3, amount: int=30) -> StatusEffect:
        return StatusEffect("divine_exposure", "debuff", turns=turns,
                        divineResistanceReduction=amount)

    @staticmethod
    def createPhysicalExposure(turns: int = 3, amount: int=30) -> StatusEffect:
        return StatusEffect("physical_exposure", "debuff", turns=turns,
                        physicalResistanceReduction=amount)

    @staticmethod
    def createOtherworldExposure(turns: int = 3, amount: int=30) -> StatusEffect:
        return StatusEffect("otherworld_exposure", "debuff", turns=turns,
                            otherworldResistanceReduction=amount)

    @staticmethod
    def createDaze(turns: int, speedReduction: float, damageMultiplier: float) -> StatusEffect:
        return StatusEffect("daze", "debuff", turns=turns,
                            speedReduction=speedReduction, damageMultiplier=damageMultiplier)

    # Buffs
    @staticmethod
    def createShieldGeneration(turns: int, amount: float) -> StatusEffect:
        return StatusEffect("shield_generation", "buff", turns=turns, shieldAmount=amount)

    @staticmethod
    def createRegeneration(turns: int, percentPerTurn: float, flatPerTurn: int) -> StatusEffect:
        return StatusEffect("regeneration", "buff", turns=turns,
                        healPercentPerTurn=percentPerTurn, healFlatPerTurn=flatPerTurn)

    @staticmethod
    def createHaste(turns: int, speed: float, damage: float) -> StatusEffect:
        return StatusEffect("haste", "buff", turns=turns,
                        speedBonus=speed, damageMultiplier=damage)

    @staticmethod
    def createStoneskin(turns: int, amount: float) -> StatusEffect:
        return StatusEffect("stoneskin", "buff", turns=turns,
                            damageReduction=amount)

    # Special
    @staticmethod
    def createCustom(*, name: str, effectType: str, turns: int,
                     **kwargs):
        return StatusEffect(name, effectType, turns, kwargs)

#=========================================================================================#

def _buildAbilityTree(abilityName: str, abilityData: Dict) -> AbilityTree:
    baseData = {
        'name': abilityData['name'],
        'category': abilityData.get('category', 'damage'),
        'tags': abilityData.get('tags', []),
        'stamina_cost': abilityData.get('stamina_cost'),
        'damage_base': abilityData.get('damage_base', 0),
        'damage_scaling': abilityData.get('damage_scaling', 0),
        'damage_type': abilityData.get('damage_type'),
        'heal_base': abilityData.get('heal_base', 0),
        'heal_percent': abilityData.get('heal_percent', 0),
        'cooldown': abilityData.get('cooldown', 0),
        'level': abilityData.get('level', 1),
        'targets': abilityData.get('targets', 1),
        'resources': abilityData.get('resources', {}),
        'effects': abilityData.get('effects', {}),
        'requirements': abilityData.get('requirements', {}),
        'description': abilityData.get('description', ''),
    }
    evolutions = _buildEvolutions(abilityData.get('evolutions', {}), abilityName)
    return AbilityTree(baseData, evolutions)

def loadAbilities() -> Dict[str, Dict[str, Dict]]:
    """
    Ascendancy sections in abilities.json are flat {abilityName: data} maps whose entries
    fall into two kinds, told apart by whether the name matches a base ability:
      - matches a base ability name -> an ALTERATION: a flat overlay dict merged onto that
        ability's resolved data via _mergeAbilityData/getCurrentAbility (edits an existing ability).
      - anything else -> a brand new ascendancy-exclusive ability, shaped exactly like a base
        ability entry (its own 'level'/'evolutions'/etc.) and built into its own AbilityTree.
    Stored per ascendancy as {'alterations': {...}, 'abilities': {...}} so
    scripts/player_classes/base.py's gainClassAbilities() can resolve each kind the way it needs to.
    """
    with open('data/abilities.json', 'r') as f:
        data: Dict[str, Any] = load(f)

    classAbilities = {}

    for className, classData in data.items():
        baseTrees = {
            abilityName: _buildAbilityTree(abilityName, abilityData)
            for abilityName, abilityData in (classData.get('base') or {}).items()
        }
        classAbilities[className] = {'base': baseTrees}

        for ascendancyName, ascendancyAbilities in classData.items():
            if ascendancyName == 'base':
                continue

            alterations = {}
            newAbilities = {}
            for abilityName, abilityData in (ascendancyAbilities or {}).items():
                if abilityName in baseTrees:
                    alterations[abilityName] = abilityData
                else:
                    newAbilities[abilityName] = _buildAbilityTree(abilityName, abilityData)

            classAbilities[className][ascendancyName] = {'alterations': alterations, 'abilities': newAbilities}

    return classAbilities

CLASS_ABILITIES: Dict[str, Dict[str, Dict]] = loadAbilities()

#=========================================================================================#
# -- shared effect resolution (used by both player Ability and EnemyAbility effects) -- #

def resolveEffects(effectsDict: Dict) -> List[StatusEffect]:
    result: List[StatusEffect] = []

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
                statusEffects = Effects.createCurse(params.get('stacks', 1))
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
            case 'shield_generation':
                statusEffects = [Effects.createShieldGeneration(
                    params.get('turns', 2), params.get('amount_percent', 0)
                )]

        result.extend(statusEffects)

    return result

#=========================================================================================#
# -- enemy abilities -- #

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
        self.baseDamage = damageBase
        self.damageScaling = damageScaling
        self.damageType = damageType
        self.weight = weight
        self.effects = effects
        self.description = description
        self.tags = []

    def calculateDamage(self, enemyBaseDamage: int) -> int:
        return int(self.baseDamage + (enemyBaseDamage * self.damageScaling))

    def canUse(self) -> Tuple[bool, str]:
        if self.cooldown > 0:
            return False, f"On cooldown for {self.cooldown} more turns."
        return True, ""

    @property
    def isDamaging(self) -> bool:
        return self.baseDamage > 0 or self.damageScaling > 0

    def spawnedConsumableHeal(self) -> Optional[int]:
        """Returns heal amount if ability spawns a consumable, else None"""
        return self.effects.get('self', {}).get('spawn_consumable', {}).get('heal')

    def __str__(self) -> str:
        cdText = f"  Cooldown: {self.cooldown}" if self.cooldown > 0 else ""
        return f"{self.name}{cdText} | Tier: {self.tier} | {self.category}"

    def __repr__(self) -> str:
        return f"EnemyAbility({self.name!r}), tier={self.tier}, lvl={self.levelReq}"

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

...