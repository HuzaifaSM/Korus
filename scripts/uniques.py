import random
from json import load
from typing import List, Callable, Optional, Dict
from .abilities import MECHANICS
from .items import Equipment, ItemRarity
from copy import deepcopy

class UniqueTier:
    COMMON = "common" # lvl 10-30, basic effects
    RARE = "rare" # lvl 35-60, strong effects
    EPIC =  "epic" # lv 65-85, very strong effects
    LEGENDARY = "legendary" # level 90-100, game-changing effects
    MYTHIC = "mythic" # level 100+, broken/rebalancing effects

TIER_WEIGHTS = {
    UniqueTier.COMMON: 50,
    UniqueTier.RARE: 30,
    UniqueTier.EPIC: 15,
    UniqueTier.LEGENDARY: 4,
    UniqueTier.MYTHIC: 1
}

def rollUniqueTier() -> str:
    totalWeight = sum(TIER_WEIGHTS.values())
    roll = random.random() * totalWeight
    currentWeight = 0

    for tier, weight in TIER_WEIGHTS.items():
        currentWeight += weight
        if roll <= currentWeight:
            return tier
        
    return UniqueTier.COMMON

def frostchill():
    effects = [MECHANICS["slow"](), MECHANICS["chilled"]()]
    if random.random() < 0.3:
        effects.append(MECHANICS["stun"]())
    return effects

def scorching_wind():
    effects = [MECHANICS["burn"](), MECHANICS["burn"](), MECHANICS["scorched"]()]
    if random.random() < 0.4:
        effects.append(MECHANICS["ablaze"]())
    return effects

def voidheart_pulse():
    return [MECHANICS["curse"]()]

def stormcaller():
    return {"damage": random.randint(50, 200), "damageType": "lightning", "mechanic": [MECHANICS["charged"]()]}

def titan_strike():
    """Titan's Grip - Shatters and stuns"""
    effects = [MECHANICS["fractured"](), MECHANICS["stun"]()]
    if random.random() < 0.5:
        effects.append(MECHANICS["fractured"]())
    return effects

def phase_strike():
    return {"ignore_resistances": True, "mechanic": [MECHANICS["mana_leak"]()]}

def immortal_blessing():
    if random.random() < 0.3:
        return [MECHANICS["regeneration"](), MECHANICS["regeneration"](), MECHANICS["guardian"]()]
    return [MECHANICS["regeneration"](), MECHANICS["self_shield"]()]

def worldbreaker_slam():
    return [MECHANICS["shattered"](), MECHANICS["brittle"](), MECHANICS["exposed"](), MECHANICS["stun"]()]

def infinite_potential():
    if random.random() < 0.015:
        return {"bonus_multiplier": 0.15}
    return None

def fallen_god_wrath():
    effects = [MECHANICS["withered"](), MECHANICS["curse"](), MECHANICS["doom"]()]
    if random.random() < 0.2:
        return effects + [MECHANICS["lifesteal"]()]
    return effects

def spark_of_life():
    return [MECHANICS["regeneration"](), MECHANICS["self_shield"]()]

def shadow_step():
    if random.random() < 0.25:
        return {"dodge": True, "counter_damage": 15}
    return None

def venomous_embrace():
    stacks = random.randint(1, 5)
    return [MECHANICS["poison"]() for _ in range(stacks)]

def arcane_feedback():
    return [MECHANICS["mana_leak"](), MECHANICS["mana_leak"](), MECHANICS["weaken"]()]

def blazing_aegis():
    return {"reflect": 0.30, "burn_attacker": True}

def storm_surge():
    return {"chain_targets": 2, "damage": 25, "mechanic": [MECHANICS["charged"]()]}

def crystalline_resonance():
    elements = ["fire", "cold", "lightning"]
    chosen = random.choice(elements)
    mechanics = {
        "fire": [MECHANICS["burn"](), MECHANICS["scorched"]()],
        "cold": [MECHANICS["chill"](), MECHANICS["chilled"]()],
        "lightning": [MECHANICS["charged"](), MECHANICS["stun"]()]
    }
    return {"bonus_damage_type": chosen, "mechanic": mechanics[chosen]}

def vampiric_hunger():
    return [MECHANICS["bleed"](), MECHANICS["lacerate"](), MECHANICS["lifesteal"]()]

def earth_shaker():
    return {"aoe_stun": True, "mechanic": [MECHANICS["stun"](), MECHANICS["fractured"]()]}

def holy_wrath():
    return [MECHANICS["glowing"](), MECHANICS["burn"](), MECHANICS["consecration"]()]

def void_corruption():
    return [MECHANICS["withered"](), MECHANICS["curse"](), MECHANICS["disarm"](), MECHANICS["slow"]()]

def dragon_fury():
    return [MECHANICS["ablaze"](), MECHANICS["ablaze"](), MECHANICS["scorched"](), MECHANICS["exposed"](), MECHANICS["brittle"]()]

def time_distortion():
    return {"cooldown_reduction": 2, "speed_boost": 0.3, "mechanic": [MECHANICS["slow"](), MECHANICS["freeze"]()]}

def soul_reaver():
    return [MECHANICS["doom"](), MECHANICS["doom"](), MECHANICS["vampirism"](), MECHANICS["withered"]()]

def celestial_judgment():
    return {"execute_threshold": 0.10, "mechanic": [MECHANICS["glowing"](), MECHANICS["ablaze"](), MECHANICS["stun"]()]}

def unstoppable_force():
    return [MECHANICS['brittle'](), MECHANICS['brittle'](), MECHANICS['exposed']()]

def living_armour():
    """Defensive boost for any class"""
    return [MECHANICS["regeneration"](), MECHANICS["self_shield"](), MECHANICS["guardian"]()]

def dawnbreaker():
    return [MECHANICS['ablaze'](), MECHANICS['ablaze'](), MECHANICS['scorched'](), MECHANICS['glowing']()]

def gods_grace():
    return [MECHANICS['burn'](), MECHANICS['doom'](), MECHANICS['regeneration'](), MECHANICS['weaken']()]

def void_touch():
    return [MECHANICS['doom'](), MECHANICS['freeze'](), MECHANICS['venom'](), MECHANICS['lacerate'](), MECHANICS['exhaustion']()]

def livewire():
    return [MECHANICS['charged']()]

def rejuvenate():
    return [MECHANICS['regeneration'](), MECHANICS['self_shield']()]

def breeze():
    return [MECHANICS['windswept']()]

def bloodstone():
    return [MECHANICS['lifesteal'](), MECHANICS['bleed']()]

def skewer():
    return [MECHANICS['bleed'](), MECHANICS['burn']()]

def plague():
    return [MECHANICS['poison'](), MECHANICS['venom'](), MECHANICS['weaken']()]

def boneweave():
    return [MECHANICS['guardian']()]

def crush():
    return [MECHANICS['brittle'](), MECHANICS['shattered']()]

def biting_cold():
    return [MECHANICS['slow'](), MECHANICS['chilled']()]

def starstruck():
    return [MECHANICS['mana_leak'](), MECHANICS['exposed'](), MECHANICS['weaken']()]

def frosting():
    return [MECHANICS['freeze'](), MECHANICS['chilled']()]

def doom_call():
    return [MECHANICS['doom'](), MECHANICS['curse']()]

def manastorm():
    return [MECHANICS['mana_leak']()]

def reflection():
    return [MECHANICS['weaken'](), MECHANICS['slow'](), MECHANICS['exposed']()]

def flare():
    return [MECHANICS['scorched'](), MECHANICS['ablaze']()]

def soul_harvest():
    return {"full_heal_on_death": True}

def insanity():
    return [MECHANICS['weaken'](), MECHANICS['slow'](), MECHANICS['blind']()]

def smite():
    return [MECHANICS['glowing'](), MECHANICS['burn'](), MECHANICS['burn'](), MECHANICS['consecration']()]

def nullify():
    return [MECHANICS['peaceful'](), MECHANICS['disarm']()]

def dragon_fire():
    return [MECHANICS["ablaze"](), MECHANICS["ablaze"](), MECHANICS["scorched"]()]

def eviscerate():
    return [MECHANICS["first_strike"](), MECHANICS["brittle"]()]

def execute():
    if random.random() < 0.15:
        return {"execute_threshold": 0.2, "mechanic": [MECHANICS["doom"]()]}
    return [MECHANICS['doom'](), MECHANICS['withered']()]

def fracture():
    return [MECHANICS["fractured"](), MECHANICS["shattered"]()]

def absolute_zero():
    return [MECHANICS["freeze"](), MECHANICS["chilled"]()]

def primed():
    return [MECHANICS['exposed'](), MECHANICS['exposed'](), MECHANICS['brittle']()]

def absorb():
    return {"absorb_damage": 0.1}

def blinding():
    return [MECHANICS["blind"](), MECHANICS["blind"]()]

def depths_pressure():
    return [MECHANICS["freeze"](), MECHANICS["chilled"](), MECHANICS["lacerate"](), MECHANICS["disarm"]()]

def perfection():
    effects = []
    if random.random() < 0.5:
        effects.append(MECHANICS['consecration'])
        effects.append(MECHANICS['consecration'])
    if random.random() < 0.5:
        effects.append(MECHANICS['guardian'])
        effects.append(MECHANICS['guardian'])
    return effects

def distortion():
    return [MECHANICS["freeze"](), MECHANICS["weaken"](), MECHANICS["weaken"](), MECHANICS["mana_leak"]()]

def gladiator():
    return {"stat_boost_per_kill": {"damage": 25, "speed": 0.1}}

def gods_favour():
    return [MECHANICS["glowing"](), MECHANICS["consecration"](), MECHANICS["guardian"]()]

def ragnarok():
    return [MECHANICS["ablaze"](), MECHANICS["ablaze"](), MECHANICS["scorched"](), MECHANICS["exposed"](), MECHANICS["brittle"](), MECHANICS["doom"]()]

def inevitability():
    return [MECHANICS["doom"](), MECHANICS["doom"](), MECHANICS["curse"]()]

def first_light():
    return [MECHANICS['consecration'](), MECHANICS['ablaze'](), MECHANICS['ablaze'](), MECHANICS['glowing'](), MECHANICS['brittle']()]

def decay():
    return [MECHANICS["curse"](), MECHANICS["doom"](), MECHANICS["withered"](), MECHANICS["venom"]()]

def alpha_protocol():
    return [MECHANICS["regeneration"](), MECHANICS["regeneration"](), MECHANICS["consecration"](), MECHANICS["guardian"](), MECHANICS["self_shield"]()]

def omega_protocol():
    allMechanics = [
        MECHANICS["exposed"](), MECHANICS["brittle"](),
        MECHANICS["shattered"](), MECHANICS["doom"]()
    ]
    double = random.random() < 0.4
    return {"double_damage": double, "mechanic": allMechanics}

def beta_protocol():
    return [MECHANICS["ablaze"](), MECHANICS["burn"](), MECHANICS["venom"](), MECHANICS["poison"](), MECHANICS["scorched"](), MECHANICS['withered']()]

def gamma_protocol():
    return [MECHANICS["lacerate"](), MECHANICS["ablaze"](), MECHANICS["venom"](), MECHANICS["doom"]()]

# class uniques
def rage_amplifier():
    return {"damage_multiplier": 0.05, "mechanic": [MECHANICS['burn']()]}

def shadow_dance():
    return {"siphon_boost": 10, "mechanic": [MECHANICS["poison"](), MECHANICS["blind"]()]}

def mana_overflow():
    return {"mana_restore": 20, "mechanic": [MECHANICS["mana_leak"]()]}

def combo_breaker():
    mechanics = []
    if random.random() < 0.1:
        mechanics.append(MECHANICS["goad"]())
    if random.random() < 0.5:
        mechanics.append(MECHANICS["weaken"]())
    if random.random() < 0.4:
        mechanics.append(MECHANICS["slow"]())
    
    return {"combo_boost": 2, "mechanic": mechanics}

def perfect_shot():
    return {"dodge_boost": 0.15, "critDamage": 0.1, "duration": 2}

def natures_harvest():
    effects = [MECHANICS['nature'](), MECHANICS['nature']()]
    if random.random() < 0.3:
        effects.append(MECHANICS['lacerate']())
    return {"thorn_damage_boost": True, "mechanic": effects}

def divine_radiance():
    mechanics = [MECHANICS["burn"]()]
    if random.random() < 0.25:
        mechanics.append(MECHANICS['regeneration']())
    return {"favour_boost": 5, "mechanic": mechanics}

def inner_peace():
    return {"prowess_multiplier": 1.5, "mechanic": [MECHANICS["regeneration"]()]}

UNIQUE_CALLBACKS = {
    "Frostfang": frostchill,
    "scorching_wind": scorching_wind,
    "voidheart_pulse": voidheart_pulse,
    "stormcaller": stormcaller,
    "titan_strike": titan_strike,
    "phase_strike": phase_strike,
    "immortal_blessing": immortal_blessing,
    "worldbreaker_slam": worldbreaker_slam,
    "infinite_potential": infinite_potential,
    "fallen_god_wrath": infinite_potential,
    "spark_of_life": spark_of_life,
    "shadow_step": shadow_step,
    "venomous_embrace": venomous_embrace,
    "arcane_feedback": arcane_feedback,
    "blazing_aegis": blazing_aegis,
    "storm_surge": storm_surge,
    "crystalline_resonance": crystalline_resonance,
    "vampiric_hunger": vampiric_hunger,
    "earth_shaker": earth_shaker,
    "holy_wrath": holy_wrath,
    "void_corruption": void_corruption,
    "dragon_fury": dragon_fury,
    "time_distortion": time_distortion,
    "soul_reaver": soul_reaver,
    "celestial_judgment": celestial_judgment,
    "unstoppable_force": unstoppable_force,
    "living_armour": living_armour,
    "dawnbreaker": dawnbreaker,
    "gods_grace": gods_grace,
    "livewire": livewire,
    "rejuvenate": rejuvenate,
    "breeze": breeze,
    "bloodstone": bloodstone,
    "skewer": skewer,
    "plague": plague,
    "boneweave": boneweave,
    "crush": crush,
    "biting_cold": biting_cold,
    "starstruck": starstruck,
    "frosting": frosting,
    "doom_call": doom_call,
    "manastorm": manastorm,
    "reflection": reflection,
    "flare": flare,
    "soul_harvest": soul_harvest,
    "insanity": insanity,
    "smite": smite,
    "nullify": nullify,
    "dragon_fire": dragon_fire,
    "eviscerate": eviscerate,
    "execute": execute,
    "fracture": fracture,
    "absolute_zero": absolute_zero,
    "primed": primed,
    "absorb": absorb,
    "blinding": blinding,
    "depths_pressure": depths_pressure,
    "perfection": perfection,
    "distortion": distortion,
    "gladiator": gladiator,
    "gods_favour": gods_favour,
    "ragnarok": ragnarok,
    "inevitability": inevitability,
    "decay": decay,
    "first_light": first_light,
    #endgame set
    "alpha_protocol": alpha_protocol,
    "beta_protocol": beta_protocol,
    "gamma_protocol": gamma_protocol,
    "omega_protocol": omega_protocol,
    #class specific
    "rage_amplifier": rage_amplifier,
    "shadow_dance": shadow_dance,
    "mana_overflow": mana_overflow,
    "combo_breaker": combo_breaker,
    "perfect_shot": perfect_shot,
    "natures_harvest": natures_harvest,
    "divine_radiance": divine_radiance,
    "inner_peace": inner_peace,
}

class Unique(Equipment):
    def __init__(self, name, slot, stats = None, level = 1, defenses = {}, damages = {},
                 callback: str = None, tier: str = UniqueTier.COMMON,
                 description: str = "", classRestriction: str = None):
        tier_multipliers = {
            UniqueTier.COMMON: 1,
            UniqueTier.RARE: 2,
            UniqueTier.EPIC: 3,
            UniqueTier.LEGENDARY: 5,
            UniqueTier.MYTHIC: 10
        }
        multiplier = tier_multipliers.get(tier, 1)
        self.value = round(level * random.randint(100, 1000) * multiplier)
        
        super().__init__(slot, ItemRarity.UNIQUE, defenses, damages, prefixes=stats, level=level)
        self.name = name
        self.callbackName = callback
        self.callback = UNIQUE_CALLBACKS.get(callback) if callback else None
        self.tier = tier
        self.description = description
        self.classRestriction = classRestriction

    @staticmethod
    def _generateEquipmentPiece(level, slot, rarity=ItemRarity.UNIQUE, className = None, uniqueTier=None) -> 'Unique':
        # return super()._generateEquipmentPiece(level, slot, rarity, className, uniqueTier)
        return generateUnique(level, slot, className, uniqueTier)

    def __str__(self):
        temp = super().__str__()
        temp2 = list(temp.split('\n'))
        temp = f"{temp2[0]}\n[unique]Unique Tier: {self.tier}[/unique] | [dim white]Description: {self.description}[/dim white]\n{temp2[1]}"
        return temp

    def triggerEffect(self, target=None, attacker=None):
        if self.callback:
            return self.callback()
        return None
    
    def _formatStats(self):
        temp = super()._formatStats()
        temp += f" | [bold orange3]Unique Mechanic: {self.callbackName}[/bold orange3]"
        return temp

def _createUniques() -> Dict[str, Unique]:
    with open('Korus/data/uniques.json', 'r') as file:
        uniques = load(file)
    unDict = {}
    for name, data in uniques.items():
        slot = data.get('slot')
        stats = data.get('stats', {})
        defenses = {
            'defenseType': stats.get('defenseType', None),
            'defenseValue': stats.get('defenseValue', 0)
        }
        damages = {
            'damage': stats.get('damage', 0),
            'baseDamage': stats.get('baseDamage', 0),
            'damageType': stats.get('damageType', None)
        }
        level = data.get('level', 1)
        callback = data.get('callback')
        tier = data.get('tier', UniqueTier.COMMON)
        description = data.get('description', '')

        obj = Unique(name, slot, stats, level, defenses, damages, callback, tier, description)
        unDict[name] = obj

    return unDict

#UNIQUES = _createUniques()
UNIQUES = {}

def generateUnique(level: int, slot: str, playerClass: str = None, uniqueTier: UniqueTier = None) -> Optional[Unique]:
    if not uniqueTier:
        tier = rollUniqueTier()
    else:
        tier = uniqueTier

    hierarchy = [
        UniqueTier.MYTHIC,
        UniqueTier.LEGENDARY,
        UniqueTier.EPIC,
        UniqueTier.RARE,
        UniqueTier.COMMON
    ]

    rolledTier = hierarchy.index(tier)

    if not uniqueTier:
        allowed = hierarchy[rolledTier:]
    else:
        allowed = hierarchy[rolledTier]

    validUniques = []
    for unique in UNIQUES.values():
        if unique.slot == slot and unique.tier in allowed and unique.level <= level:
            if not unique.classRestriction or unique.classRestriction == playerClass:
                validUniques.append(unique)

    if not validUniques:
        return None
    
    chosen = random.choice(validUniques)
    newUnique = deepcopy(chosen)

    return newUnique

...