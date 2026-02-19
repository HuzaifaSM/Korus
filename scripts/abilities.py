from json import load
from typing import Optional, List, Dict, Any, Tuple
from random import random
from .styles import console

def parseSecondaryCost(costData: Dict, player) -> Tuple[Optional[str], Optional[Any], bool]:
    """
    Parse secondaryCost field from ability data.
    Returns: (resourceType, amount, canAfford)
    
    Handles:
    - rage costs (including "all")
    - hp costs (current % or max %, e.g. "10%_current")
    - siphon, combo, mana costs
    - conditional costs (e.g. ifPhoenixConsumed)
    """
    if not costData:
        return None, None, True
    
    for resourceType, amount in costData.items():
        if resourceType == "rage":
            if amount == "all":
                return "rage", player._rage, player._rage > 0
            return "rage", amount, player._rage >= amount
        
        elif resourceType == "hp":
            if isinstance(amount, str):
                if "_current" in amount:
                    percent = float(amount.replace("%_current", "")) / 100
                    hpCost = int(player._health * percent)
                    return "hp", hpCost, player._health > hpCost
                elif "_max" in amount:
                    percent = float(amount.replace("%_max", "")) / 100
                    hpCost = int(player._maxHealth * percent)
                    return "hp", hpCost, player._health > hpCost
            return "hp", amount, player._health > amount
        
        elif resourceType == "siphon":
            return "siphon", amount, hasattr(player, 'siphon') and player.siphon >= amount
        
        elif resourceType == "combo":
            return "combo", amount, hasattr(player, '_combo') and player._combo >= amount
        
        elif resourceType == "mana":
            return "mana", amount, hasattr(player, '_mana') and player._mana >= amount
        
        elif resourceType == "ifPhoenixConsumed":
            # Special conditional for Flamewarden Solar Flare
            if hasattr(player, 'phoenixUsed') and player.phoenixUsed:
                return None, None, True  # No cost if phoenix consumed
            continue
    
    return None, None, True

def parseScalesWithResource(scaleData: Dict, player) -> float:
    """
    Parse dynamic scaling based on resources.
    
    Handles:
    - scalesWithRage: {baseAmount, perRage, maxRage}
    - scalesWithFury: {baseAmount, perFury, maxFury}
    - scalesWithMissingHP: {baseAmount, perMissingPercent, maxBonus}
    """
    if "scalesWithRage" in scaleData:
        data = scaleData["scalesWithRage"]
        baseAmount = data.get("baseAmount", 0)
        perRage = data.get("perRage", 0)
        maxRage = data.get("maxRage", 50)
        currentRage = min(player._rage, maxRage) if hasattr(player, '_rage') else 0
        return baseAmount + (currentRage * perRage)
    
    elif "scalesWithFury" in scaleData:
        data = scaleData["scalesWithFury"]
        baseAmount = data.get("baseAmount", 0)
        perFury = data.get("perFury", 0)
        maxFury = data.get("maxFury", 10)
        currentFury = min(player._fury, maxFury) if hasattr(player, '_fury') else 0
        return baseAmount + (currentFury * perFury)
    
    elif "scalesWithMissingHP" in scaleData:
        data = scaleData["scalesWithMissingHP"]
        baseAmount = data.get("baseAmount", 0)
        perMissingPercent = data.get("perMissingPercent", 0)
        maxBonus = data.get("maxBonus", 1.0)
        missingPercent = 1.0 - (player._health / player._maxHealth)
        bonus = min(maxBonus, missingPercent * perMissingPercent * 100)
        return baseAmount + bonus
    
    return 0

def parseBonusDamagePerResource(bonusData: Dict, player) -> int:
    """
    Parse bonus damage that scales with resource stacks.
    
    Handles resources: rage, fury, fortify, annihilation, combo, prowess
    Respects maxStacks unless noMaxStacks=true
    """
    resource = bonusData.get("resource")
    amount = bonusData.get("amount", 0)
    maxStacks = bonusData.get("maxStacks")
    noMaxStacks = bonusData.get("noMaxStacks", False)
    
    currentStacks = 0
    if resource == "rage" and hasattr(player, '_rage'):
        currentStacks = player._rage
    elif resource == "fury" and hasattr(player, '_fury'):
        currentStacks = player._fury
    elif resource == "fortify" and hasattr(player, '_fortify'):
        currentStacks = player._fortify
    elif resource == "annihilation" and hasattr(player, 'annihilation'):
        currentStacks = player.annihilation
    elif resource == "combo" and hasattr(player, '_combo'):
        currentStacks = player._combo
    elif resource == "prowess" and hasattr(player, '_prowess'):
        currentStacks = player._prowess
    
    if not noMaxStacks and maxStacks:
        currentStacks = min(currentStacks, maxStacks)
    
    return int(currentStacks * amount)

def parseShieldAmount(shieldData, player) -> int:
    """
    Parse complex shield calculations.
    
    Handles:
    - String format: "100_plus_25%_hp"
    - Dict format: {"base": 100, "perRage": 4, "perFortify": 8}
    - Simple int
    """
    if isinstance(shieldData, str):
        parts = shieldData.split("_plus_")
        baseShield = int(parts[0])
        
        if len(parts) > 1:
            percentPart = parts[1].replace("%_hp", "")
            percent = float(percentPart) / 100
            return baseShield + int(player._maxHealth * percent)
        return baseShield
    
    elif isinstance(shieldData, dict):
        baseShield = shieldData.get("base", 0)
        
        if "perRage" in shieldData and hasattr(player, '_rage'):
            baseShield += player._rage * shieldData["perRage"]
        
        if "perFortify" in shieldData and hasattr(player, '_fortify'):
            baseShield += player._fortify * shieldData["perFortify"]
        
        return int(baseShield)
    
    return int(shieldData)

def checkConditionalRequirement(condition: str, player, target=None) -> bool:
    """
    Check if conditional requirements are met.
    
    Handles:
    - fury_above_X
    - fortify_above_X
    - fortify_at_max
    - annihilation_above_X
    - target_below_30%
    - requiresPhoenixAspect
    """
    if condition.startswith("fury_above_"):
        threshold = int(condition.replace("fury_above_", ""))
        return hasattr(player, '_fury') and player._fury > threshold
    
    elif condition.startswith("fortify_above_"):
        threshold = int(condition.replace("fortify_above_", ""))
        return hasattr(player, '_fortify') and player._fortify > threshold
    
    elif condition == "fortify_at_max":
        return (hasattr(player, '_fortify') and hasattr(player, '_maxFortify') 
                and player._fortify >= player._maxFortify)
    
    elif condition.startswith("annihilation_above_"):
        threshold = int(condition.replace("annihilation_above_", ""))
        return hasattr(player, 'annihilation') and player.annihilation > threshold
    
    elif condition == "target_below_30%" and target:
        return target._health < (target._maxHealth * 0.3)
    
    elif condition == "requiresPhoenixAspect":
        return hasattr(player, 'phoenixAspect') and player.phoenixAspect
    
    return False

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
# NEED TO REWRITE ABILITY AND ABILITY TREE CLASSSES
class Ability:
    def __init__(self, name: str, baseDamage: int, damageScaling: float,
                 damageType: str, staminaCost: int, cooldown: int,
                 effects: List[StatusEffect], targets: str = "single",
                 resourceCost: Optional[Dict] = None,
                 secondaryCost: Optional[Dict] = None):
        self.name = name
        self.baseDamage = baseDamage
        self.damageScaling = damageScaling
        self.damageType = damageType
        self.staminaCost = staminaCost
        self.cooldown = cooldown
        self.maxCooldown = cooldown
        self.currentCooldown = 0
        self.effects = effects
        self.targets = targets
        self.resourceCost = resourceCost
        self.secondaryCost = secondaryCost

    def calculateDamage(self, playerDamage: int) -> int:
        return int(self.baseDamage + (playerDamage * self.damageScaling))
    
    def canUse(self, player) -> Tuple[bool, str]:
        if self.currentCooldown > 0:
            return False, f"On cooldown for {self.currentCooldown} more turns."
        
        if player._stamina < self.staminaCost:
            return False, f"Not enough stamina: {player._stamina} / {self.staminaCost}"
        
        if self.resourceCost:
            resType = self.resourceCost.get('type')
            resAmount = self.resourceCost.get('amount')
            if resType == 'rage':
                if resAmount == 'all':
                    if player._rage == 0:
                        return False, "No rage to consume"
                elif player._rage < resAmount:
                    return False, f"Not enough rage: {player._rage} / {resAmount}"
            elif resType == 'siphon':
                if player.siphon < resAmount:
                    return False, f"Not enough siphon: {player.siphon} / {resAmount}"
            elif resType == "mana":
                if player._mana < resAmount:
                    return False, f"Not enough mana ({player._mana}/{resAmount})"
            elif resType == "combo":
                if player._combo < resAmount:
                    return False, f"Not enough combo ({player._combo}/{resAmount})"
        
        if self.secondaryCost:
            resType, resAmount, canAfford = parseSecondaryCost(self.secondaryCost, player)
            if not canAfford:
                return False, f"Not enough {resType}: cannot afford {resAmount}"

        return True, ""

    def use(self, player):
        player._stamina -= self.staminaCost

        if self.resourceCost:
            resType = self.resourceCost.get('type')
            resAmount = self.resourceCost.get('amount')
            consume = self.resourceCost.get('consume', True)
            
            if consume:
                if resType == "rage":
                    if resAmount == "all":
                        player._rage = 0
                    else:
                        player._rage -= resAmount
                elif resType == "siphon":
                    player.siphon -= resAmount
                elif resType == "mana":
                    player._mana -= resAmount
                elif resType == "combo":
                    player._combo -= resAmount

        if self.secondaryCost:
            resType, resAmount, _ = parseSecondaryCost(self.secondaryCost, player)
            if resType and resAmount:
                if resType == "rage":
                    player._rage = max(0, player._rage - resAmount)
                elif resType == "hp":
                    player._health = max(1, player._health - resAmount)
                elif resType == "siphon":
                    player.siphon = max(0, player.siphon - resAmount)
                elif resType == "combo":
                    player._combo = max(0, player._combo - resAmount)
                elif resType == "mana":
                    player._mana = max(0, player._mana - resAmount)

        self.currentCooldown = self.maxCooldown

    def tickCooldown(self):
        self.currentCooldown = max(0, self.currentCooldown - 1)

    def __rich__(self):
        return self.__str__()

    def __str__(self):
        cdText = f"[red]CD: {self.currentCooldown}[/red] | " if self.currentCooldown > 0 else ""
        targetText = {"single": "1 enemy", "double": "2 enemies", 
                     "triple": "3 enemies", "all": "all enemies"}[self.targets]
        return f"{self.name} | {cdText}Stamina: {self.staminaCost} | Targets: {targetText}"

class AbilityTree:
    def __init__(self, abilityName: str, level: int, category: str,
                 evolutions: Dict[int, Dict], variants: Dict[str, Dict]):
        self.abilityName = abilityName
        self.level = level
        self.category = category
        self.evolutions = evolutions
        self.variants = variants

        self.currentEvolutionLevel = None
        self.currentVariant = None

    def getCurrentAbility(self, playerLevel: int) -> Optional[Ability]:
        availableEvolutions = [lvl for lvl in self.evolutions.keys() if lvl <= playerLevel]
        if not availableEvolutions:
            return None

        evolutionLevel = max(availableEvolutions)
        self.currentEvolutionLevel = evolutionLevel

        evoData = self.evolutions[evolutionLevel]

        if self.currentVariant:
            evoData = self._applyVariantMods(evoData, self.currentVariant)

        return self._buildAbility(evoData)
    
    def _applyVariantMods(self, baseData: Dict, variantName: str) -> Dict:
        if variantName not in self.variants:
            return baseData
        
        variantMods = self.variants[variantName]['mods']
        modifiedData = baseData.copy()

        for mKey, mVal in variantMods.items():
            if mKey == 'base':
                if isinstance(mVal, str) and '%' in mVal:
                    mult = float(mVal.strip('+-%')) / 100
                    if '-' in mVal:
                        modifiedData['base'] = int(modifiedData['base'] * (1 - mult))
                    else:
                        modifiedData['base'] = int(modifiedData['base'] * (1 + mult))
                else:
                    modifiedData['base'] = mVal

            elif mKey == 'scaling':
                if isinstance(mVal, str) and '%' in mVal:
                    mult = float(mVal.strip('+-%')) / 100
                    if '-' in mVal:
                        modifiedData['scaling'] = modifiedData['scaling'] * (1 - mult)
                    else:
                        modifiedData['scaling'] = modifiedData['scaling'] * (1 + mult)
            
            elif mKey == "stamina":
                if isinstance(mVal, str) and '%' in mVal:
                    mult = float(mVal.strip('+-%')) / 100
                    modifiedData['stamina'] = int(modifiedData['stamina'] * (1 + mult))
            
            elif mKey == "cd":
                if isinstance(mVal, str):
                    if mVal == "0":
                        modifiedData['cd'] = 0
                    elif '+' in mVal or '-' in mVal:
                        change = int(mVal)
                        modifiedData['cd'] = max(0, modifiedData['cd'] + change)

            elif mKey == "targets":
                modifiedData['targets'] = mVal
            
            elif mKey == "addEffect":
                if 'effects' not in modifiedData:
                    modifiedData['effects'] = []
                modifiedData['effects'].append(mVal)
            
            elif mKey == "removeEffect":
                if 'effects' in modifiedData:
                    modifiedData['effects'] = [e for e in modifiedData['effects'] 
                                              if e.get('resourceGain') != mVal]
            
            elif mKey == "addCost":
                modifiedData['rageCost'] = mVal.get('rage', 0)
                modifiedData['siphonCost'] = mVal.get('siphon', 0)
        
            elif mKey == "secondaryCost":
                modifiedData['secondaryCost'] = mVal

            elif mKey == "guaranteedCrit":
                if 'effects' not in modifiedData:
                    modifiedData['effects'] = []
                modifiedData['effects'].append({"guaranteedCrit": True})
                
            elif mKey == "requiresResource":
                if 'effects' not in modifiedData:
                    modifiedData['effects'] = []
                modifiedData['effects'].append({"requiresResource": mVal})

            elif mKey == "consumeResource":
                if 'effects' not in modifiedData:
                    modifiedData['effects'] = []
                modifiedData['effects'].append({"consumeResource": mVal})

        return modifiedData

    def unlockVariant(self, variantName: str) -> bool:
        if variantName not in self.variants:
            return False
        self.variants[variantName]['unlocked'] = True
        return True

    def setActiveVariant(self, variantName: Optional[str]):
        if variantName and variantName not in self.variants:
            return False
        self.currentVariant = variantName
        return True

#=========================================================================================#
# NEED TO REWRITE LOAD ABILITIES
def loadAbilities() -> Dict[str, AbilityTree]:
    with open('Korus/data/abilities.json', 'r') as f:
        data: Dict[str, Dict[str, Dict]] = load(f)

    classAbilities = {}

    for className, classData in data.items(): # splits by classes
        classAbilities[className] = {}

        for ascendancyName, ascendancyAbilities in classData.items(): # splits by ascendancies including 'base'
            classAbilities[className][ascendancyName] = {}
            for abilityName, abilityData in ascendancyAbilities.items(): # splits by actual abilities
                tree = AbilityTree(
                    abilityName=abilityName,
                    level=abilityData['level'],
                    category=abilityData['category'],
                    evolutions=abilityData['evolutions'],
                    variants=abilityData.get('variants', {})
                )
                classAbilities[className][abilityName] = tree

    return classAbilities

ABILITIES = {} # temp
CLASS_ABILITIES = {} #loadAbilities()

...