from json import load
from copy import deepcopy
from typing import Optional, List, Dict, Any, Tuple
from random import random
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
        return int(self.baseDamage + (playerDamage * self.damageScaling))

    def calculateHeal(self, playerMaxHp: int) -> int:
        return int(self.healBase + (playerMaxHp * self.healPercent))
    
    # -- resources -- #
    def canUse(self, player) -> Tuple[bool, str]:
        if self.cooldown > 0:
            return False, f"On cooldown for {self.cooldown} more turns."
        
        if not player.canUseAbility(self):
            return False, f"{player._name} does not have enough stamina."
        
        required: Dict[str, int] = self.resources.get('required', {})
        for resource, amount in required.items():
            playerVal = getattr(player, f'_{resource}', None)
            if playerVal is None: # check if resource doesn't have underscore before it
                playerVal = getattr(player, resource, 0)
            if playerVal < amount:
                return False, f"Not enough {resource}: {playerVal} / {amount}"
            
        if hasattr(self, 'requirements') and self.requirements:
            ok, reason = self._checkRequirements(player)
            if not ok:
                return False, reason
            
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
            attr = f'_{resource}' if hasattr(player, f'_{resource}') else resource
            setattr(player, attr, getattr(player, attr) - amount)
        
        gained = self.resources.get('gain', {})
        for resource, amount in gained.items():
            if resource == 'energy_shield':
                player._stats['energyShield'] = min(player.maxEnergyShield, player.energyShield + amount)
            else:
                attr = f'_{resource}' if hasattr(player, f'_{resource}') else resource
                current = getattr(player, attr, 0)
                x = attr.lstrip('_')
                mAttr = f'_max{x}' if hasattr(player, f'_max{x}') else f'max{x}' if hasattr(player, f'max{x}') else None
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

class AbilityTree:
    def __init__(self, baseData: Dict, evolutions: Dict[int, Dict], variants: Dict[str, Dict]):
        self.baseData = baseData
        self.evolutions = evolutions
        self.variants = variants
        self.currentVariant = None

    # -- ability -- #
    def getCurrentAbility(self, playerLevel: int) -> Optional[Ability]:
        if self.baseData['level'] > playerLevel:
            return None

        available = [lvl for lvl in self.evolutions if lvl <= playerLevel]

        if available:
            evoLevel = max(available)
            data = deepcopy(self.evolutions[evoLevel])
        else:
            data = deepcopy(self.baseData)
        
        if self.currentVariant:
            data = self._applyVariantMods(data, self.currentVariant)
        
        return self._buildAbility(data)

    def _applyVariantMods(self, base: Dict, variantName: str) -> Dict:
        """
        Apply a variant's modifications onto the resolved evolution data.\n
        Keys ending in + are additive:
            - damage_base+     → base['damage_base'] += value
            - cooldown+        → base['cooldown']    += value
            - effects+         → deep-merge into base['effects']
            - resources+       → deep-merge into base['resources']
            - tags+            → extend base['tags']
        \n
        Keys without + are replacements:
            - targets, cooldown, damage_base, damage_scaling, etc.
        """
        if variantName not in self.variants:
            return base
        
        result = deepcopy(base)
        variant = self.variants[variantName]

        for k, v in variant.items():
            if k == 'description+':
                result['description'] = result.get('description', '') + '\n' + v
            elif k.endswith('+'):
                field = k[:-1]
                if field == 'effects':
                    result['effects'] = _deepMergeEffects(result.get('effects', {}), v)
                
                elif field == 'resources':
                    result['resources'] = _deepMergeEffects(result.get('resources', {}), v)
                
                elif field == 'tags':
                    existing = result.get('tags', [])
                    result['tags'] = list(set(existing) | set(v))

                elif field == 'damage_base':
                    result['damage_base'] = result.get('damage_base', 0) + v
                elif field == 'damage_scaling':
                    result['damage_scaling'] = result.get('damage_scaling', 0) + v
                
                elif field == 'heal_base':
                    result['heal_base'] = result.get('heal_base', 0) + v
                elif field == 'heal_percent':
                    result['heal_percent'] = result.get('heal_percent', 0) + v

                elif field == 'cooldown':
                    result['cooldown'] = max(0, result.get('cooldown', 0) + v)
                
            else:
                result[k] = v

        return result

    def _buildAbility(self, data: Dict) -> Ability:
        dScale = data.get('damage_scaling', 0)
        dScaling = dScale / 100 if dScale >= 1 else dScale
        hScale = data.get('heal_percent', 0)
        hScaling = hScale / 100 if hScale >= 1 else dScale

        return Ability(
            data['name'], data['category'], data.get('tags', []), data.get('stamina_cost'),
            data.get('damage_base', 0), dScaling, data.get('damage_type'), data.get('heal_base', 0), hScaling,
            data.get('cooldown', 0), data.get('targets', 1), data.get('resources', {}), data.get('effects', {}), data.get('requirements', {}),
            data.get('description', ''),
        )

    def unlockVariant(self, variantName: str) -> bool:
        if variantName not in self.variants:
            return False
        self.variants[variantName]['unlocked'] = True
        return True

    def setActiveVariant(self, variantName: Optional[str]) -> bool:
        if variantName and variantName not in self.variants:
            return False
        self.currentVariant = variantName
        return True

# -- helpers -- #
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
    'wind', 'earth', 'psychic', 'ethereal', 'chaos'
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
        elif self.name == 'burn':
            for dt in DAMAGE_TYPES:
                self.target._stats['Temporary'][dt] -= self.data['resistanceReduction'] * mult
        elif self.name == 'poison':
            self.target._stats['Temporary']['healingMagnitude'] -= self.data['healingReduction'] * mult
        elif self.name in ['stun', 'freeze']:
            self.target._stats['Temporary']['stunAvoidance'] += self.data['grantsAvoidance'] * mult
        elif self.name in ['chill', 'slow']: # has a more complex calculation to implement later, stacks non-linearly up to a max of 99%
            self.target._stats['Temporary']['speed'] -= self.data['amount'] * mult
        elif self.name == 'exposed':
            self.target._stats['Temporary']['all'] -= self.data['allResistanceReduction'] * mult
        elif self.name == 'elemental_exposure':
            self.target._stats['Temporary']['elemental'] -= self.data['elementalResistanceReduction'] * mult
        elif self.name == 'divine_exposure':
            self.target._stats['Temporary']['divine'] -= self.data['divineResistanceReduction'] * mult
        elif self.name == 'physical_exposure':
            self.target._stats['Temporary']['physical'] -= self.data['physicalResistanceReduction'] * mult
        elif self.name == 'otherworld_exposure':
            self.target._stats['Temporary']['otherworld'] -= self.data['otherworldResistanceReduction'] * mult
        elif self.name == 'daze':
            self.target._stats['Temporary']['speed'] -= self.data['speedReduction'] * mult
        elif self.name == 'haste':
            self.target._stats['Temporary']['speed'] += self.data['speedBonus'] * mult

    def tick(self) -> bool:
        if not self.applied:
            self._applySecondaryEffect()
            self.applied = True

        if self.effectType == 'dot':
            damage = self.data['baseDamage'] + int(self.attacker._damage * self.data['damagePercent'])
            damageType = self.data.get('damageType')
            dotResistance = self.target._stats['Bonuses'].get('dotResistance', 0)
            if dotResistance > 0:
                damage = int(damage * (1 - (dotResistance / 100)))
                if damage < 0:
                    damage = 0

            if self.target.className == 'Rogue' and self.target._ascendancy == 'Shadow' and self.name == 'poison':
                damage //= 2

            self.target.damage(damage, damageType)
            console.print(f" - [dot]{self.name}[/dot] deals [damage]{damage}[/damage] damage")

        elif self.effectType == 'shield_generation':
            self.target._shield += self.data['shield']

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
    - First Strike
    """
    @staticmethod
    def createBleed(stacks: int = 1) -> List[StatusEffect]:
        return [StatusEffect('bleed', 'dot', turns=3, damageType='physical',
                            baseDamage=8, damagePercent=0.1, speedReduction=0.05)
                            for _ in range(stacks)]

    @staticmethod
    def createBurn(stacks: int = 1) -> List[StatusEffect]:
        return [StatusEffect('fire', 'dot', turns=2, damageType='fire',
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
    def createShieldGeneration(turns: int, amount: int) -> StatusEffect:
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
    def createMight(turns: int, flatGain: int, percentGain: float) -> StatusEffect:
        return StatusEffect("might", "buff", turns=turns,
                            damageBuffFlat=flatGain, damageBuffPercent=percentGain)

    @staticmethod
    def createStoneskin(turns: int, amount: float) -> StatusEffect:
        return StatusEffect("stoneskin", "buff", turns=turns,
                            damageReduction=amount)

    # Special
    @staticmethod
    def createFirstStrike(multiplier: float=2.0) -> StatusEffect:
        return StatusEffect("first_strike", "special", turns=1,
                            damageMultiplier=multiplier)

    @staticmethod
    def createCustom(*, name: str, effectType: str, turns: int,
                     **kwargs):
        return StatusEffect(name, effectType, turns, kwargs)

#=========================================================================================#

def loadAbilities() -> Dict[str, Dict[str, Dict[str, AbilityTree]]]:
    """
    Returns:
        classAbilties[className][ascendancyName][abilityName] = AbilityTree
    """
    with open('data/abilities.json', 'r') as f:
        data: Dict[str, Any] = load(f)

    classAbilities = {}

    for className, classData in data.items():
        classAbilities[className] = {}

        for ascendancyName, ascendancyAbilities in classData.items():
            classAbilities[className][ascendancyName] = {}

            if not ascendancyAbilities:
                continue

            for abilityName, abilityData in ascendancyAbilities.items():
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
                    'targets': abilityData.get('targets', 1),
                    'resources': abilityData.get('resources', {}),
                    'effects': abilityData.get('effects', {}),
                    'requirements': abilityData.get('requirements', {}),
                    'description': abilityData.get('description', ''),
                }

                evolutions = _buildEvolutions(abilityData.get('evolutions', {}), abilityName)

                tree = AbilityTree(
                    baseData, evolutions, abilityData.get('variants', {}),
                )

                classAbilities[className][ascendancyName][abilityName] = tree

    return classAbilities

CLASS_ABILITIES: Dict[str, Dict[str, Dict[str, AbilityTree]]] = loadAbilities()

...