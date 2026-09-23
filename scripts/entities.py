from typing import Dict, Optional, List, TypedDict, TypeVar, Any
import random
from copy import deepcopy
from .items.items import Consumable
from .items.equipment import Equipment
from .items.food import FoodItem
from .abilities import CLASS_ABILITIES, Ability, ENEMY_ABILITIES, EnemyAbility, BasicAttack, Effects
from .runeDrops import getRuneObject
from .styles import (
    console, printSuccess, printWarning, printError, printInfo,
    formatDamageValue, formatRarity, createHealthBar,
    formatEffectsDetailed, formatAbilityCost, pause
)

ELEMENTAL_RES: frozenset = ['fire', 'earth', 'cold', 'lightning']
DIVINE_RES: frozenset = ['holy', 'dark', 'arcane']
OTHERWORLD_RES: frozenset = ['chaos', 'ethereal', 'psychic']
ALL_RES: frozenset = ['physical', 'fire', 'earth', 'cold', 'lightning', 'holy', 'dark', 'arcane', 'chaos', 'ethereal', 'psychic']
"""all non-categorical resistances"""
T = TypeVar("T")

SIGIL_SLOTS = ('sigil_1', 'sigil_2', 'sigil_3', 'sigil_4', 'sigil_5')

def _slotAccepts(slotKey: str, equipment: Equipment) -> bool:
    if slotKey in SIGIL_SLOTS:
        return equipment.slot == 'sigil'
    if slotKey == 'offhand':
        return equipment.slot == 'offhand' or (equipment.slot == 'weapon' and not equipment.twoHanded)
    return equipment.slot == slotKey

_PROC_EFFECTS = {
    'chance_to_bleed': lambda: Effects.createBleed(),
    'chance_to_apply_vulnerable': lambda: Effects.createVulnerable(),
    'chance_to_apply_exposed': lambda: Effects.createExposed(),
    'chance_to_stun': lambda: Effects.createStun(),
    'chance_to_poison': lambda: Effects.createPoison(),
}

class ResistanceBlock(TypedDict):
    physical: float
    fire: float
    cold: float
    earth: float
    lightning: float
    dark: float
    arcane: float
    holy: float
    psychic: float
    ethereal: float
    chaos: float

class BonusBlock(TypedDict):
    item_rarity: float
    item_quantity: float
    enemy_quantity: float
    xp_gain: float
    gold_gain: float
    stun_avoidance: float
    ailment_avoidance: float
    healing_magnitude: float
    crit_chance: float
    crit_multi: float
    crit_resistance: float
    resistance_penetration: float
    chance_to_multihit: float
    lifesteal: float
    damage_reduction: float
    added_multihits: float
    hp_regen: float
    stamina_regen: float
    added_damage: float
    increased_damage: float
    increased_defenses: float
    increased_health: float
    health_on_hit: float
    health_on_kill: float
    stamina_on_hit: float
    stamina_on_kill: float
    thorns: float
    chance_to_bleed: float
    chance_to_apply_vulnerable: float
    chance_to_apply_exposed: float
    chance_to_stun: float
    chance_to_block: float
    execute_threshold: float
    less_damage_taken: float
    rage_gain_on_attack: float
    rage_gain_on_hit: float
    max_rage: float
    mana_cost_reduced: float
    mana_damage_return_increased: float
    mastery_gain_flat: float
    insanity_swing_increased: float
    insanity_penalty_reduction: float
    insanity_extreme_effect_increased: float
    beast_form_damage_flat: float
    verdance_gain_flat: float
    human_form_defenses_flat: float
    aggression_gain_flat: float
    discipline_gain_flat: float
    trained_threshold_reduction: float
    dedicated_threshold_reduction: float
    allin_threshold_reduction: float
    lost_damage_increased: float
    hope_gain_flat: float
    hopeless_gain_flat: float
    blood_spike_gain_flat: float
    buff_effect_increased_low_hp: float
    favour_gain_flat: float
    favour_defensive_effect_increased: float
    favour_heal_increased: float
    crit_chance_when_faster: float
    unleash_cost_reduced: float
    static_flow_gain_flat: float
    vengeance_gain_flat: float
    vengeance_consume_crit_damage_increased: float
    ghostly_heal_increased: float
    siphon_cap_flat: float
    echo_damage_increased: float
    siphon_immune: float
    increased_damage_taken: float
    ability_cost_multiplier: float

class GeneralStatBlock(TypedDict):
    physical: float
    fire: float
    earth: float
    lightning: float
    cold: float
    holy: float
    dark: float
    psychic: float
    chaos: float
    ethereal: float
    arcane: float
    max_physical: float
    max_fire: float
    max_earth: float
    max_lightning: float
    max_cold: float
    max_holy: float
    max_dark: float
    max_psychic: float
    max_chaos: float
    max_ethereal: float
    max_arcane: float
    resistance_penetration: float
    speed: float
    stun_avoidance: float
    ailment_avoidance: float
    healing_magnitude: float
    crit_resistance: float
    crit_chance: float
    crit_multi: float
    lifesteal: float
    thorns: float
    damage_reduction: float
    increased_damage_reduction: float
    hp_regen: float
    less_damage_taken: float
    stamina_regen: float
    added_damage: float
    increased_damage: float
    enemy_quantity: float
    added_multihits: float
    chance_to_multihit: float
    increased_defenses: float
    added_armour: float
    added_evasion: float
    added_energy_shield: float
    increased_armour: float
    increased_evasion: float
    increased_energy_shield: float
    increased_health: float
    increased_crit_chance: float
    increased_crit_multi: float
    chance_to_bleed: float
    chance_to_apply_vulnerable: float
    chance_to_apply_exposed: float
    chance_to_stun: float
    chance_to_block: float
    execute_threshold: float

class Stats(TypedDict):
    Max_Resistances: ResistanceBlock
    Resistances: ResistanceBlock
    Bonuses: BonusBlock
    Permanent: GeneralStatBlock
    Temporary: GeneralStatBlock
    baseCritChance: float
    baseCritMulti: float
    armour: float
    evasion: float
    energy_shield: float
    max_energy_shield: float
    critChanceIncreased: float
    critMultiIncreased: float

class LockedDict(dict):
    """
    a dict that only allows overwriting keys that existed at construction time\n
    prevents any typos or accidental assignments from being allowed to run\n
    pylance will catch these and show error
    """
    def __setitem__(self, key, value):
        if key not in self:
            raise KeyError(
                f"{key!r} is not an existing stat on this dict -"
                f"check for a typo"
            )
        super().__setitem__(key, value)

    def __deepcopy__(self, memo):
        return LockedDict({k: deepcopy(v, memo) for k, v in self.items()})

def _freeze(obj: T) -> T:
    """recursively replace every dict with a LockedDict.\n
    Typed as T -> T (identity) since result is shaped identically to input\n
    runtime-only and deliberately doesn't participate in TypedDict check"""
    if isinstance(obj, dict):
        return LockedDict({k: _freeze(v) for k, v in obj.items()}) # type: ignore[return-value]
    return obj

class Entity:
    def __init__(self, health: int, damage: int, baseCritChance: float, baseCritMulti: float,
                 damageType: str, speed: float,
                 name: str, className: str = None, isPlayer: bool = False):
        self._maxHealth = health
        self._health = health
        self._shield = 0
        self._damage = damage
        self._damageType = damageType or "physical"
        self._speed = speed
        _rawStats: Stats = {
            'Max_Resistances': {
                'physical': 75,
                'fire': 75,
                'cold': 75,
                'lightning': 75,
                'dark': 75,
                'holy': 75,
                'arcane': 75,
                'earth': 75,
                'psychic': 75,
                'ethereal': 75,
                'chaos': 75,
            },
            'Resistances': {
                'physical': 0,
                'fire': 0,
                'cold': 0,
                'lightning': 0,
                'dark': 0,
                'holy': 0,
                'arcane': 0,
                'earth': 0,
                'psychic': 0,
                'ethereal': 0,
                'chaos': 0,
            },
            'Bonuses': {
                'item_rarity': 0,
                'item_quantity': 0,
                'enemy_quantity': 0,
                'xp_gain': 0,
                'gold_gain': 0,
                'stun_avoidance': 0,
                'ailment_avoidance': 0,
                'healing_magnitude': 100,
                'crit_chance': 0,
                'crit_multi': 0,
                'crit_resistance': 0,
                'resistance_penetration': 0,
                'chance_to_multihit': 0,
                'lifesteal': 0,
                'damage_reduction': 0,
                'added_multihits': 0,
                'hp_regen': 0,
                'stamina_regen': 0,
                'added_damage': 0,
                'increased_damage': 0,
                'increased_defenses': 0,
                'increased_health': 0,
                'health_on_hit': 0,
                'health_on_kill': 0,
                'stamina_on_hit': 0,
                'stamina_on_kill': 0,
                'thorns': 0,
                'chance_to_bleed': 0,
                'chance_to_apply_vulnerable': 0,
                'chance_to_apply_exposed': 0,
                'chance_to_stun': 0,
                'chance_to_block': 0,
                'execute_threshold': 0,
                'less_damage_taken': 0,
                'rage_gain_on_attack': 0,
                'rage_gain_on_hit': 0,
                'max_rage': 0,
                'mana_cost_reduced': 0,
                'mana_damage_return_increased': 0,
                'mastery_gain_flat': 0,
                'insanity_swing_increased': 0,
                'insanity_penalty_reduction': 0,
                'insanity_extreme_effect_increased': 0,
                'beast_form_damage_flat': 0,
                'verdance_gain_flat': 0,
                'human_form_defenses_flat': 0,
                'aggression_gain_flat': 0,
                'discipline_gain_flat': 0,
                'trained_threshold_reduction': 0,
                'dedicated_threshold_reduction': 0,
                'allin_threshold_reduction': 0,
                'lost_damage_increased': 0,
                'hope_gain_flat': 0,
                'hopeless_gain_flat': 0,
                'blood_spike_gain_flat': 0,
                'buff_effect_increased_low_hp': 0,
                'favour_gain_flat': 0,
                'favour_defensive_effect_increased': 0,
                'favour_heal_increased': 0,
                'crit_chance_when_faster': 0,
                'unleash_cost_reduced': 0,
                'static_flow_gain_flat': 0,
                'vengeance_gain_flat': 0,
                'vengeance_consume_crit_damage_increased': 0,
                'ghostly_heal_increased': 0,
                'siphon_cap_flat': 0,
                'echo_damage_increased': 0,
                'siphon_immune': 0,
                'increased_damage_taken': 0,
                'ability_cost_multiplier': 0,
            },
            'Permanent': {
                'physical': 0,
                'fire': 0,
                'earth': 0,
                'lightning': 0,
                'cold': 0,
                'holy': 0,
                'dark': 0,
                'psychic': 0,
                'chaos': 0,
                'ethereal': 0,
                'arcane': 0,
                'max_physical': 0,
                'max_fire': 0,
                'max_earth': 0,
                'max_lightning': 0,
                'max_cold': 0,
                'max_holy': 0,
                'max_dark': 0,
                'max_psychic': 0,
                'max_chaos': 0,
                'max_ethereal': 0,
                'max_arcane': 0,
                'resistance_penetration': 0,
                'stun_avoidance': 0,
                'ailment_avoidance': 0,
                'speed': 0,
                'healing_magnitude': 0,
                'crit_resistance': 0,
                'crit_chance': (baseCritChance - 0.05) if baseCritChance else 0,
                'crit_multi': (baseCritMulti - 1.5) if baseCritMulti else 0,
                'increased_crit_chance': 0,
                'increased_crit_multi': 0,
                'lifesteal': 0,
                'damage_reduction': 0,
                'increased_damage_reduction': 0,
                'hp_regen': 0,
                'thorns': 0,
                'chance_to_bleed': 0,
                'chance_to_apply_vulnerable': 0,
                'chance_to_apply_exposed': 0,
                'chance_to_stun': 0,
                'chance_to_block': 0,
                'execute_threshold': 0,
                'less_damage_taken': 0,
                'stamina_regen': 0,
                'added_damage': 0,
                'increased_damage': 0,
                'enemy_quantity': 0,
                'added_multihits': 0,
                'chance_to_multihit': 0,
                'increased_defenses': 0,
                'added_armour': 0,
                'added_evasion': 0,
                'added_energy_shield': 0,
                'increased_armour': 0,
                'increased_evasion': 0,
                'increased_energy_shield': 0,
                'increased_health': 0,
            },
            'Temporary': {
                'physical': 0,
                'fire': 0,
                'earth': 0,
                'lightning': 0,
                'cold': 0,
                'holy': 0,
                'dark': 0,
                'psychic': 0,
                'chaos': 0,
                'ethereal': 0,
                'arcane': 0,
                'max_physical': 0,
                'max_fire': 0,
                'max_earth': 0,
                'max_lightning': 0,
                'max_cold': 0,
                'max_holy': 0,
                'max_dark': 0,
                'max_psychic': 0,
                'max_chaos': 0,
                'max_ethereal': 0,
                'max_arcane': 0,
                'resistance_penetration': 0,
                'stun_avoidance': 0,
                'ailment_avoidance': 0,
                'speed': 0,
                'healing_magnitude': 0,
                'crit_resistance': 0,
                'crit_chance': 0,
                'crit_multi': 0,
                'increased_crit_chance': 0,
                'increased_crit_multi': 0,
                'lifesteal': 0,
                'damage_reduction': 0,
                'increased_damage_reduction': 0,
                'hp_regen': 0,
                'thorns': 0,
                'chance_to_bleed': 0,
                'chance_to_apply_vulnerable': 0,
                'chance_to_apply_exposed': 0,
                'chance_to_stun': 0,
                'chance_to_block': 0,
                'execute_threshold': 0,
                'less_damage_taken': 0,
                'stamina_regen': 0,
                'added_damage': 0,
                'increased_damage': 0,
                'enemy_quantity': 0,
                'added_multihits': 0,
                'chance_to_multihit': 0,
                'increased_defenses': 0,
                'added_armour': 0,
                'added_evasion': 0,
                'added_energy_shield': 0,
                'increased_armour': 0,
                'increased_evasion': 0,
                'increased_energy_shield': 0,
                'increased_health': 0,
            },
            'baseCritChance': 0.05,
            'baseCritMulti': 1.5,
            'armour': 0,
            'evasion': 0,
            'energy_shield': 0,
            'max_energy_shield': 0,
            'critChanceIncreased': 0,
            'critMultiIncreased': 0
        }
        self._stats: Stats = _freeze(_rawStats)
        self._abilities: Dict[str, Ability | EnemyAbility] = {"Basic Attack": BasicAttack()}
        self._inventory: Dict[str, int] = {}  # {item_name: quantity}
        self._craftingInventory: Dict[str, int] = {}
        """{f'{category}_{runeType}': quantity}"""
        self._equipmentStorage: List[Equipment] = []
        self._equipment: Dict[str, Optional[Equipment]] = {
            'weapon': None,
            'offhand': None,
            'head': None,
            'chest': None,
            'legs': None,
            'feet': None,
            'ring': None,
            'amulet': None,
            'sigil_1': None,
            'sigil_2': None,
            'sigil_3': None,
            'sigil_4': None,
            'sigil_5': None,
        }
        # stats before equipment
        self._baseHealth = health
        self._baseDamage = damage
        self._baseSpeed = speed
        self._baseStamina = 100
        self._stamina = 100
        self._baseMaxStamina = 100
        self._maxStamina = 100
        self._gold = 0
        self._level = 1
        self._xp = 0
        self.calcXpRequirement()
        self._name = name
        self.titles: List[Dict[str, str]] = []
        self.equippedTitle: Optional[Dict[str, str]] = None
        self.className = className
        self.classDescription = None
        self._ascendancy = None
        self.ascendancyDescription = None
        self.isPlayer = isPlayer
        self.consumable = Consumable()
        self.combatUnit = None
        self._pendingEffects = []
        self._damageLog: List[tuple] = []  # (reason, flatAmount, percentAmount) contributions to the hit currently being resolved
        self._foodInventory: List = []  # cooked FoodItems, single-use
        self._foodBuff: Optional[Dict[str, Any]] = None  # active {prefix, suffix, turnsRemaining} from the last eaten food
        self._emergencyRevivalUsedThisCombat = False

    @property
    def _isDead(self) -> bool:
        return self._health <= 0

    @property
    def armour(self) -> int:
        return self._stats['armour']
    
    @property
    def evasion(self) -> int:
        return self._stats['evasion']
    
    @property
    def energyShield(self) -> int:
        return self._stats['energy_shield']

    @property
    def maxEnergyShield(self) -> int:
        return self._stats['max_energy_shield']

    @property
    def unlockedSigilSlots(self) -> int:
        return len(SIGIL_SLOTS)

    @property
    def critChance(self) -> float:
        flat = self._stats['baseCritChance'] + self._stats['Bonuses']['crit_chance'] + self._getExtraBonuses('crit_chance')
        increased = self._stats['critChanceIncreased'] + self._getExtraBonuses('increased_crit_chance')
        return round(flat * round(1 + increased), 2)

    @property
    def critMulti(self) -> float:
        flat = self._stats['baseCritMulti'] + self._stats['Bonuses']['crit_multi'] + self._getExtraBonuses('crit_multi')
        increased = self._stats['critMultiIncreased'] + self._getExtraBonuses('increased_crit_multi')
        return round(flat * (1 + increased), 2)

    @property
    def numMultihits(self) -> int:
        return 2 + self._getExtraBonuses('added_multihits') + self._stats['Bonuses']['added_multihits']

    @property
    def chanceToMultihit(self) -> float:
        return round((self._stats['Bonuses']['chance_to_multihit'] + self._getExtraBonuses('chance_to_multihit')) / 100, 2)

    def formatTitledName(self) -> str:
        if not self.equippedTitle:
            return self._name
        text = self.equippedTitle['text']
        if self.equippedTitle.get('style') == 'prefix':
            return f"{text} {self._name}"
        return f"{self._name} {text}"

    def __rich__(self):
        return self.__str__()

    def __str__(self):
        healthBar = createHealthBar(self._health, self._maxHealth)
        baseStr =  f"[health]Health:[/health] {healthBar} | [damage]Damage:[/damage] {self._damage} | Type: [{self._damageType}]{self._damageType.title()}[/{self._damageType}] | [speed]Speed:[/speed] {self._speed}"

        if self._stats.get('armour', 0) > 0:
            baseStr += f"\n[armour]Armour:[/armour] {self.armour}"
        if self._stats.get('evasion', 0) > 0:
            baseStr += f"\n[evasion]Evasion:[/evasion] {self.evasion}"
        if self._stats.get('max_energy_shield', 0) > 0:
            es = self.energyShield
            maxEs = self.maxEnergyShield
            baseStr += f"\n[energy_shield]Energy Shield:[/energy_shield] {es} / {maxEs}"
        if self._stats['Bonuses'].get('chance_to_block', 0) > 0:
            baseStr += f"\n[cyan]Chance to Block:[/cyan] {self._stats['Bonuses']['chance_to_block']}%"

        return baseStr

    def __repr__(self):
        return f"{self.serialise()}"

    def serialise(self):
        equipped = {}
        for slot, equip in self._equipment.items():
            if equip:
                equipped[slot] = equip.serialise()

        equipmentStorage = []
        for equipment in self._equipmentStorage:
            if equipment:
                equipmentStorage.append(equipment.serialise())

        return {'maxHealth': self._maxHealth,
                'baseHealth': self._baseHealth,
                'health': self._health,
                'maxStamina': self._maxStamina,
                'baseMaxStamina': self._baseMaxStamina,
                'stamina': self._stamina,
                'baseDamage': self._baseDamage,
                'damageType': self._damageType,
                'baseSpeed': self._baseSpeed,
                'stats': self._stats,
                'name': self._name,
                'titles': self.titles,
                'equippedTitle': self.equippedTitle,
                'level': self._level,
                'xp': self._xp,
                'xpToNextLevel': self._xpToNextLevel,
                'gold': self._gold,
                'equipped': equipped,
                'equipmentStorage': equipmentStorage,
                'craftingInventory': self._craftingInventory,
                'inventory': self._inventory,
                'foodInventory': [f.serialise() for f in self._foodInventory],
                'consumable': self.consumable.serialise(),
                'className': self.className,
                'classDescription': self.classDescription,
                'ascendancy': self._ascendancy,
                'ascendancyDescription': self.ascendancyDescription,
        }

    def deserialise(self, data: Dict):
        self._maxHealth = data.get('maxHealth', 50)
        self._baseHealth = data.get('baseHealth', 50)
        self._health = data.get('health', 50)
        self._maxStamina = data.get('maxStamina', 100)
        self._baseMaxStamina = data.get('baseMaxStamina', 100)
        self._stamina = data.get('stamina', 100)
        self._baseDamage = data.get('baseDamage', 5)
        self._damageType = data.get('damageType', 'physical')
        self._baseSpeed = data.get('baseSpeed', 1.0)
        self._stats = data.get('stats')
        self._name = data.get('name', 'Entity')
        self.titles = data.get('titles', [])
        self.equippedTitle = data.get('equippedTitle', None)
        self._level = data.get('level', 0)
        self._xp = data.get('xp', 0)
        self._xpToNextLevel = data.get('xpToNextLevel', 50)
        self._gold = data.get('gold', 0)
        self.className = data.get('className')
        self.classDescription = data.get('classDescription', 'Basic Player')
        self._ascendancy = data.get('ascendancy', None)
        self.ascendancyDescription = data.get('ascendancyDescription', None)
        equipment = data.get('equipped')

        if equipment:
            for slot, eqData in equipment.items():
                e = Equipment.deserialise(eqData)
                self._equipment[slot] = e

        equipmentStorage = data.get('equipmentStorage')
        if equipmentStorage:
            for eqData in equipmentStorage:
                e = Equipment.deserialise(eqData)
                self._equipmentStorage.append(e)
        
        self._inventory = data.get('inventory', {})
        self._craftingInventory = data.get('craftingInventory', {})
        self._foodInventory = [FoodItem.deserialise(f) for f in data.get('foodInventory', [])]
        if 'consumable' in data:
            self.consumable = self.consumable.deserialise(data['consumable'])
        else:
            self.consumable.updateValue(self._level)
        self._abilities = {"Basic Attack": BasicAttack()}
        for e in self._equipment.values():
            self._grantMythicAbilities(e)
            self._grantSoulboundAbilities(e)

        self._recalculateStats()

    def _addResistance(self, resistance: str, amount: int):
        if resistance in self._stats['Permanent']:
            self._stats['Permanent'][resistance] += amount

    def calcXpRequirement(self):
        self._xpToNextLevel = max(int((self._level * 25) ** 0.717), (3 * self._level) ** 2)

    def damage(self, damage: int, damageType: str='physical', combatUnit = None, *, lethal: bool = True, attacker: Entity = None) -> int:
        """'true' damageType means no resistances apply. returns damageReductionValue"""
        if damage < 1:
            return 0
        if combatUnit:
            resistMod = combatUnit.getResistanceModifier(damageType, attacker)
            stoneskinMod = combatUnit.getStoneskinModifier()
        else:
            resistMod = self._stats['Resistances'].get(damageType, 0) / 100
            resistMod = min(0.75, resistMod)
            stoneskinMod = 0
        if damageType == 'true':
            resistMod = 0
            stoneskinMod = 0

        preMitigation = damage
        damage = max(0, damage - self._stats['Bonuses']['damage_reduction'])
        damageReductionValue = preMitigation - damage

        lessDamageTaken = self._stats['Bonuses']['less_damage_taken']
        if lessDamageTaken != 0:
            damage = int(round(damage * (1 - lessDamageTaken / 100)))

        if damageReductionValue > 0:
            console.print(f"  [dim]- -{damageReductionValue} Damage from Damage Reduction[/dim]")
        if lessDamageTaken != 0:
            console.print(f"  [dim]- {'-' if lessDamageTaken > 0 else '+'}{abs(round(lessDamageTaken))}% Damage from Less Damage Taken[/dim]")
        if resistMod != 0:
            console.print(f"  [dim]- {'-' if resistMod > 0 else '+'}{round(resistMod * 100)}% Damage from {damageType.title()} Resistance[/dim]")
        if stoneskinMod != 0:
            console.print(f"  [dim]- -{round(stoneskinMod  * 100)} Damage from Stoneskin Buff%[/dim]")

        damage = int(round(damage * (1 - resistMod) * (1 - stoneskinMod)))
        damage = int(round(damage * (1 + self._stats['Bonuses']['increased_damage_taken'] / 100)))
        trueDamage = max(0, damage - self._shield)
        damagePrevented = damage - trueDamage
        self._shield -= damagePrevented

        if trueDamage > 0:
            self._health -= trueDamage
            if not lethal and self._health <= 0:
                self._health = 1
                console.print(f"  [warning]Non-lethal damage dealt![/warning]")
            damageTypeFormatted = f"[{damageType}]{damageType.title()}[/{damageType}]"
            dmgColour = formatDamageValue(trueDamage)
            console.print(f"[damage]- {self._name} took[/damage] [{dmgColour}]{trueDamage}[/{dmgColour}] [damage]{damageTypeFormatted} damage.[/damage] [dim]({damagePrevented} damage prevented with shield)[/dim] | [health]HP remaining: {self._health} / {self._maxHealth}[/health]")
            if self._isDead and not self._tryEmergencyRevival():
                self.death()
        elif damagePrevented > 0:
            console.print(f"[cyan]- {self._name}'s shield fully absorbed the hit![/cyan] [dim]({damagePrevented} damage prevented with shield)[/dim] | [health]HP remaining: {self._health} / {self._maxHealth}[/health]")

        return damageReductionValue

    def heal(self, amount: int, doPrint: bool = True, reason: Optional[str] = None) -> int:
        if amount <= 0:
            return 0
        magnitude = self._stats['Bonuses']['healing_magnitude'] / 100
        modifiedAmount = int(amount * magnitude)
        reasonStr = f" due to {reason}" if reason else ""
        if modifiedAmount > 0:
            self._health = min(self._health + modifiedAmount, self._maxHealth)
            self.onHeal(modifiedAmount)
            self._mythicDispatch('onHeal', modifiedAmount)
            if doPrint:
                console.print(f"[success]{self._name} healed for {modifiedAmount} HP{reasonStr}.[/success] [dim]HP Remaining: {self._health} / {self._maxHealth}[/dim]")
        elif modifiedAmount < 0:
            damageTaken = abs(modifiedAmount)
            self._health -= damageTaken
            if doPrint:
                printError(f"{self._name}'s negative Healing Magnitude dealt {damageTaken} damage{reasonStr}! [dim]HP Remaining: {self._health} / {self._maxHealth}[/dim]")
            if self._isDead and not self._tryEmergencyRevival():
                self.death()
        else:
            if doPrint:
                printWarning(f"[warning]{self._name}'s healing was nullified{reasonStr}![/warning]")
        return modifiedAmount

    def death(self):
        console.print(f"[error]{self._name} has been defeated[/error]")
        return True

    def _tryEmergencyRevival(self) -> bool:
        campfire = getattr(self, '_campfire', None)
        if campfire is None or campfire.level < 5:
            return False
        if self._emergencyRevivalUsedThisCombat:
            return False
        cost = getattr(campfire, 'EMERGENCY_REVIVAL_SUPPLIES_COST', 50)
        if campfire.supplies < cost:
            return False

        campfire.supplies -= cost
        self._emergencyRevivalUsedThisCombat = True
        self._health = max(1, round(self._maxHealth * 0.20))
        console.print(f"[gold1 bold]The warmth of your Campfire pulls you back from the brink! Revived at {self._health} HP, consuming {cost} Supplies.[/gold1 bold]")
        return True

    def eatFood(self, food) -> None:
        if self._foodBuff is not None:
            oldPrefix = self._foodBuff.get('prefix')
            oldSuffix = self._foodBuff.get('suffix')
            if oldPrefix:
                self._stats['Temporary'][oldPrefix['stat']] -= oldPrefix['value']
            if oldSuffix:
                self._stats['Temporary'][oldSuffix['stat']] -= oldSuffix['value']
            self._foodBuff = None

        healAmount = round(self._maxHealth * food.totalHealPercent / 100)
        if healAmount > 0:
            self.heal(healAmount, reason=food.name)

        prefix = food.combatPrefix
        suffix = food.combatSuffix
        if prefix or suffix:
            if prefix:
                self._stats['Temporary'][prefix['stat']] = self._stats['Temporary'].get(prefix['stat'], 0) + prefix['value']
            if suffix:
                self._stats['Temporary'][suffix['stat']] = self._stats['Temporary'].get(suffix['stat'], 0) + suffix['value']
            self._foodBuff = {'prefix': prefix, 'suffix': suffix, 'turnsRemaining': food.buffDuration}
            self._recalculateStats(False, True)

    def rollCritical(self, target: Entity, damageDealt: int=None) -> tuple[bool, float]:
        """target is combatUnit"""
        if random.random() < self.critChance:
            return True, self.critMulti
        return False, 1.0

    def gainGold(self, amount: int):
        self._gold += amount
        console.print(f"[gold]{self._name} got +{amount}g.[/gold] [dim]Total gold: {self._gold}[/dim]")
        questBoard = getattr(self, '_questBoard', None)
        if questBoard is not None:
            questBoard.notifyEvent('gold_gained', amount=amount)

    def gainAbility(self, ability: str, doPrint: bool = True):
        if self.isPlayer:
            tree = CLASS_ABILITIES.get(self.className, {}).get('base', {}).get(ability)
            if not tree:
                return
            overlay = CLASS_ABILITIES.get(self.className, {}).get(self._ascendancy, {}).get(ability)
            resolved = tree.getCurrentAbility(self._level, overlay)
            if not resolved:
                return
        else:
            classPools = ENEMY_ABILITIES.get(self.className.value, {})
            pool = dict(classPools.get('base', {}))
            if getattr(self, '_ascendancy', None) is not None:
                pool.update(classPools.get(self._ascendancy.value, {}))
            if ability not in pool:
                return
            resolved = deepcopy(pool[ability]) # used to separate references

        self._abilities[ability] = resolved
        if doPrint:
            console.print(f"[success]{self._name} Learnt {ability}![/success]")
            if resolved.damageType:
                damageTypeFormatted = f"[{resolved.damageType}]{resolved.damageType.title()}[/{resolved.damageType}]"
                console.print(f"[dim]Base Damage: {resolved.baseDamage} + {resolved.damageScaling*100:.0f}% of damage | Type: {damageTypeFormatted}[/dim]")
            costStr = formatAbilityCost(getattr(resolved, 'resources', {}))
            if costStr != "-":
                console.print(f"[dim]Cost: {costStr}[/dim]")
            for line in formatEffectsDetailed(resolved.effects):
                console.print(f"  [buff]- {line}[/buff]")

    def removeAbility(self, ability: str, doPrint: bool = True):
        if ability in self._abilities:
            del self._abilities[ability]
            if doPrint:
                console.print(f"[warning]{self._name} no longer has the ability: {ability}[/warning]")

    def canUseAbility(self, ability: Ability) -> bool:
        cost = int(ability.staminaCost * (1 + self._stats['Bonuses']['ability_cost_multiplier'] / 100))
        if self._stamina < cost:
            return False
        self._stamina -= cost
        return True

    def spendHealthForAbility(self, amount: int):
        self._health = max(0, self._health - amount)
        if self._isDead and not self._tryEmergencyRevival():
            self.death()

    def displayAbilities(self):
        console.print("\n[bold cyan]=== Abilities ===[/bold cyan]")
        for name, ability in self._abilities.items():
            console.print(f"  [cyan]- {name}[/cyan]")
            if ability.damageType:
                damageTypeFormatted = f"[{ability.damageType}]{ability.damageType.title()}[/{ability.damageType}]"
                console.print(f"    [dim]Base Damage: {ability.baseDamage} + {ability.damageScaling*100:.0f}% of damage | Type: {damageTypeFormatted}[/dim]")
            if ability.healBase or ability.healPercent:
                console.print(f"    [heal]Heal: {ability.healBase} + {ability.healPercent*100:.0f}% Max HP[/heal]")
            costStr = formatAbilityCost(getattr(ability, 'resources', {}))
            if costStr != "-":
                console.print(f"    [dim]Cost: {costStr}[/dim]")
            for line in formatEffectsDetailed(ability.effects):
                console.print(f"    [buff]- {line}[/buff]")

    def addRune(self, category: str, runeType: str, quantity: int = 1, doPrint: bool = True):
        key = f'{category}_{runeType}'
        if key in self._craftingInventory:
            self._craftingInventory[key] += quantity
        else:
            self._craftingInventory[key] = quantity
        rune = getRuneObject(category, runeType)
        runeName = rune.name if rune else runeType
        if doPrint:
            console.print(f'[success]  - Gained {quantity}x {runeName}[/success]')

    def removeRune(self, category: str, runeType: str, quantity: int = 1) -> bool:
        key = f'{category}_{runeType}'
        if key not in self._craftingInventory:
            return False
        if self._craftingInventory[key] < quantity:
            return False
        self._craftingInventory[key] -= quantity
        if self._craftingInventory[key] <= 0:
            del self._craftingInventory[key]
        return True

    def addItem(self, itemName: str, quantity: int = 1, doPrint: bool = True):
        if quantity > 0:
            self._inventory[itemName] = self._inventory.get(itemName, 0) + quantity
            if doPrint:
                console.print(f"[success]  - Gained {quantity}x {itemName}[/success]")
            questBoard = getattr(self, '_questBoard', None)
            if questBoard is not None:
                questBoard.notifyEvent('resource_gained', amount=quantity)

    def removeItem(self, itemName: str, quantity: int = 1) -> bool:
        if self._inventory.get(itemName) >= quantity:
            self._inventory[itemName] -= quantity
            if self._inventory[itemName] <= 0:
                del self._inventory[itemName]
            return True
        return False

    def hasItem(self, itemName: str, quantity: int = 1) -> bool:
        return self._inventory.get(itemName, 0) >= quantity

    def getItem(self, itemName: str) -> int:
        return self._inventory.get(itemName, 0)

    def addEquipmentToStorage(self, equipment: Equipment, doPrint: bool = True):
        self._equipmentStorage.append(equipment)
        if doPrint:
            equipName = formatRarity(equipment.name, equipment.rarity.value)
            console.print(f"[info]Stored {equipName} in equipment storage.[/info]")
        questBoard = getattr(self, '_questBoard', None)
        if questBoard is not None:
            questBoard.notifyEvent('item_found', rarity=equipment.rarity.value)

    def removeEquipmentFromStorage(self, *, index: int = None, equipment: Equipment = None) -> Optional[Equipment]:
        if index:
            if 0 <= index < len(self._equipmentStorage):
                return self._equipmentStorage.pop(index)
        if equipment:
            if equipment in self._equipmentStorage:
                index = self._equipmentStorage.index(equipment)
                return self._equipmentStorage.pop(index)
        return None

    def _resolveEquipSlot(self, equipment: Equipment) -> str:
        if equipment.slot == 'sigil':
            unlockedSlots = SIGIL_SLOTS[:self.unlockedSigilSlots]
            return next((s for s in unlockedSlots if self._equipment.get(s) is None), SIGIL_SLOTS[0])
        if equipment.slot == 'weapon':
            mainHand = self._equipment.get('weapon')
            if mainHand is not None and not equipment.twoHanded and not mainHand.twoHanded \
                    and self._equipment.get('offhand') is None:
                return 'offhand'
            return 'weapon'
        return equipment.slot

    def equip(self, equipment: Equipment, doPrint: bool = True, slot: Optional[str] = None) -> bool:
        if equipment.durability == 0:
            printError(f"{equipment.name} has no durability and cannot be equipped. Repair at the Forge before equipping")
            pause()
            return False

        if slot is None:
            slot = self._resolveEquipSlot(equipment)

        if slot not in self._equipment:
            if doPrint:
                printError(f"Invalid equipment slot: {slot}")
            return False

        if not _slotAccepts(slot, equipment):
            if doPrint:
                printError(f"{equipment.name} cannot be equipped in the {slot} slot.")
            return False

        if slot in SIGIL_SLOTS:
            slotIndex = SIGIL_SLOTS.index(slot) + 1
            if slotIndex > self.unlockedSigilSlots:
                if doPrint:
                    printError(f"Sigil slot {slotIndex} is not unlocked yet (unlocks at level {(slotIndex - 1) * 20}).")
                return False

        if slot == 'weapon' and equipment.twoHanded and self._equipment.get('offhand'):
            evicted = self.unequip('offhand', False, doPrint)
            if evicted:
                self.addEquipmentToStorage(evicted, doPrint)

        elif slot == 'offhand' and self._equipment['weapon'] is not None and self._equipment.get('weapon').twoHanded:
            evicted = self.unequip('weapon', False, doPrint)
            if evicted:
                self.addEquipmentToStorage(evicted, doPrint)

        if self._equipment[slot]:
            displaced = self.unequip(slot, False, doPrint)
            if displaced:
                self.addEquipmentToStorage(displaced, doPrint)

        self._equipment[slot] = equipment
        self._grantMythicAbilities(equipment)
        self._grantSoulboundAbilities(equipment)
        self._recalculateStats(doPrint)
        if equipment.slot != 'weapon':
            hGain, hInc, _ = equipment.getStatBonuses('health')
            self._health = min(
                self._maxHealth,
                (self._health + hGain) * (1 + hInc)
            )
        equipName = formatRarity(equipment.name, equipment.rarity.value)
        if doPrint:
            printSuccess(f"Equipped {equipName} in {slot} slot.")
        return True

    def unequip(self, slot: str, toStorage: bool = True, doPrint: bool = True) -> Optional[Equipment]:
        if slot in self._equipment and self._equipment[slot]:
            item = self._equipment[slot]
            self._equipment[slot] = None
            self._revokeMythicAbilities(item)
            self._revokeSoulboundAbilities(item)
            self._recalculateStats(doPrint)
            printInfo(f"Unequipped {item.name}")
            if toStorage:
                self.addEquipmentToStorage(item, doPrint)
            return item
        return None

    def _grantMythicAbilities(self, equipment: Optional[Equipment]):
        if not equipment or not equipment.mythicAffix:
            return
        from scripts.items.mythicEffects import buildGrantedAbility
        for line in equipment.mythicAffix.lines:
            if line.effect == 'grant_ability':
                ability = buildGrantedAbility(line, equipment)
                if ability:
                    self._abilities[ability.name] = ability

    def _revokeMythicAbilities(self, equipment: Optional[Equipment]):
        if not equipment or not equipment.mythicAffix:
            return
        from scripts.abilities import MYTHIC_GRANTED_ABILITIES
        for line in equipment.mythicAffix.lines:
            if line.effect == 'grant_ability':
                baseAbility = MYTHIC_GRANTED_ABILITIES.get(line.meta.get('ability'))
                if baseAbility and baseAbility.name in self._abilities:
                    del self._abilities[baseAbility.name]

    def _grantSoulboundAbilities(self, equipment: Optional[Equipment]):
        if not equipment or not equipment.soulbound:
            return
        from scripts.items.soulboundEffects import buildGrantedSoulboundAbility
        for affix in equipment.stats:
            if affix.soulbound and affix.stat == 'grant_ability':
                ability = buildGrantedSoulboundAbility(affix)
                if ability:
                    self._abilities[ability.name] = ability

    def _revokeSoulboundAbilities(self, equipment: Optional[Equipment]):
        if not equipment or not equipment.soulbound:
            return
        from scripts.abilities import SOULBOUND_GRANTED_ABILITIES
        for affix in equipment.stats:
            if affix.soulbound and affix.stat == 'grant_ability':
                baseAbility = SOULBOUND_GRANTED_ABILITIES.get(affix.data.get('ability'))
                if baseAbility and baseAbility.name in self._abilities:
                    del self._abilities[baseAbility.name]

    def hasLiveConditionalModifiers(self) -> bool:
        for equipment in self._equipment.values():
            if equipment and equipment.mythicAffix:
                for line in equipment.mythicAffix.lines:
                    if line.effect == 'conditional_modifier':
                        return True
        return False

    def _getExtraBonuses(self, stat: str) -> int:
        """gets temporary + permanent buffs for a stat, divided by 100 if 'increased_'"""
        perm = self._stats['Permanent'].get(stat, 0)
        temp = self._stats['Temporary'].get(stat, 0)
        total = perm + temp
        lowHpBonus = self._stats['Bonuses'].get('buff_effect_increased_low_hp', 0)
        if lowHpBonus and self._maxHealth > 0 and self._health / self._maxHealth < 0.4:
            total *= (1 + lowHpBonus / 100)
        if 'increased_' in stat:
            return (total / 100)
        return total

    def _recalculateStats(self, doPrint: bool = True, inCombat: bool = False):
        # one-time self-heal for saves/sessions predating the categorical-resistance refactor:
        # 'elemental'/'divine'/'otherworld'/'all' are no longer real stats, just a shorthand that
        # gets distributed into their real children at the source - a save's `_stats` dict loaded
        # verbatim via deserialise() can still carry these as literal leftover keys, which would
        # otherwise get double-counted or shown as a phantom, non-functional resistance line.
        for legacyName in ('elemental', 'divine', 'otherworld', 'all'):
            for sub in ('Resistances', 'Max_Resistances', 'Permanent', 'Temporary'):
                self._stats[sub].pop(legacyName, None)
            self._stats['Permanent'].pop(f'max_{legacyName}', None)
            self._stats['Temporary'].pop(f'max_{legacyName}', None)

        self._maxHealth = self._baseHealth
        self._damage = self._baseDamage
        self._speed = self._baseSpeed

        for bonus in self._stats['Bonuses']:
            if bonus == 'healing_magnitude':
                self._stats['Bonuses'][bonus] = 100
            else:
                self._stats['Bonuses'][bonus] = 0

        for res in self._stats['Resistances']:
            self._stats['Resistances'][res] = 0
            self._stats['Max_Resistances'][res] = 75

        conditionalLines = []

        armour = 0
        evasion = 0
        es = 0
        globalArmourInc = 0
        globalEvasionInc = 0
        globalEsInc = 0

        healthFlat = 0
        healthInc = 0
        staminaFlat = 0
        dmgFlat = 0
        dmgInc = 0
        spdFlat = 0
        spdInc = 0
        critChanceInc = 0
        critMultiInc = 0

        for slot, equipment in self._equipment.items():
            if equipment:
                hFlat, hInc, _ = equipment.getStatBonuses('health')
                healthFlat += hFlat
                healthInc += hInc

                stFlat, _, _ = equipment.getStatBonuses('added_stamina')
                staminaFlat += stFlat

                if equipment.slot == 'weapon':
                    dmgFlat += equipment.damage
                else:
                    dFlat, dInc, _ = equipment.getStatBonuses('damage')
                    dmgFlat += dFlat
                    dmgInc += dInc

                sFlat, sInc, _ = equipment.getStatBonuses('speed')
                spdFlat += sFlat
                spdInc += sInc

                if slot == "weapon":
                    self._damageType = equipment.getDamageType() if equipment.getDamageType() else self._damageType

                else: # all non-weapons can roll resistances/max resistances. no min() calculations here, done after this for loop
                    categoricalNames = ('elemental', 'divine', 'otherworld', 'all')
                    realResistanceKeys = [k for k in self._stats['Resistances'].keys() if k not in categoricalNames]
                    for damageType in realResistanceKeys + list(categoricalNames):
                        resFlat, _, _ = equipment.getStatBonuses(f'{damageType}_resistance')
                        maxResFlat, _, _ = equipment.getStatBonuses(f'max_{damageType}_resistance')

                        if damageType == 'elemental':
                            for res in ELEMENTAL_RES:
                                self._stats['Resistances'][res] += resFlat
                                self._stats['Max_Resistances'][res] += maxResFlat
                        elif damageType == 'otherworld':
                            for res in OTHERWORLD_RES:
                                self._stats['Resistances'][res] += resFlat
                                self._stats['Max_Resistances'][res] += maxResFlat
                        elif damageType == 'divine':
                            for res in DIVINE_RES:
                                self._stats['Resistances'][res] += resFlat
                                self._stats['Max_Resistances'][res] += maxResFlat
                        elif damageType == 'all':
                            for res in ALL_RES:
                                self._stats['Resistances'][res] += resFlat
                                self._stats['Max_Resistances'][res] += maxResFlat
                        else:
                            self._stats['Max_Resistances'][damageType] += maxResFlat
                            self._stats['Resistances'][damageType] += resFlat

                for bonus in self._stats['Bonuses'].keys():
                    bonusFlat, bonusInc, _ = equipment.getStatBonuses(bonus)
                    if bonus == 'crit_chance':
                        self._stats['Bonuses'][bonus] += bonusFlat / 100
                        critChanceInc += bonusInc
                    elif bonus == 'crit_multi':
                        self._stats['Bonuses'][bonus] += bonusFlat / 100
                        critMultiInc += bonusInc
                    else:
                        self._stats['Bonuses'][bonus] += round(bonusFlat * (1 + bonusInc))

                if hasattr(equipment, 'defenseType') and equipment.defenseType:
                    if equipment.defenseType == 'armour':
                        armour += equipment.defenseValue
                    elif equipment.defenseType == 'evasion':
                        evasion += equipment.defenseValue
                    elif equipment.defenseType == 'energy_shield':
                        es += equipment.defenseValue

                armour += equipment.implicits.get('armour', 0)
                evasion += equipment.implicits.get('evasion', 0)
                es += equipment.implicits.get('energy_shield', 0)

                if equipment.mythicAffix:
                    for line in equipment.mythicAffix.lines:
                        if line.effect == 'secondary_defense_conversion':
                            secondaryValue = equipment.defenseValue * (line.values.get('x', 0) / 100)
                            target = line.meta.get('target_defense')
                            if target == 'armour':
                                armour += secondaryValue
                            elif target == 'evasion':
                                evasion += secondaryValue
                            elif target == 'energy_shield':
                                es += secondaryValue
                        elif line.effect == 'conditional_modifier':
                            conditionalLines.append(line)

                if equipment.slot == 'amulet':
                    _, _, gIncArm = equipment.getStatBonuses('armour')
                    globalArmourInc += gIncArm
                    _, _, gIncEva = equipment.getStatBonuses('evasion')
                    globalEvasionInc += gIncEva
                    _, _, gIncEs = equipment.getStatBonuses('energy_shield')
                    globalEsInc += gIncEs

        for damageType in self._stats['Resistances'].keys(): # also caps all resistances to correct values
            maxExtra = self._getExtraBonuses(f'max_{damageType}')
            extra = self._getExtraBonuses(damageType)
            self._stats['Max_Resistances'][damageType] = min(
                self._stats['Max_Resistances'][damageType] + maxExtra, 90
            )
            self._stats['Resistances'][damageType] = min(
                self._stats['Resistances'][damageType] + extra,
                self._stats['Max_Resistances'][damageType]
            )

        for bonus in self._stats['Bonuses'].keys():
            if bonus in ('crit_chance', 'crit_multi'):
                continue
            self._stats['Bonuses'][bonus] += round(self._getExtraBonuses(bonus))

        self._stats['critChanceIncreased'] = critChanceInc
        self._stats['critMultiIncreased'] = critMultiInc

        healthInc += self._getExtraBonuses('increased_health')
        globalArmourInc += self._getExtraBonuses('increased_armour')
        globalEvasionInc += self._getExtraBonuses('increased_evasion')
        globalEsInc += self._getExtraBonuses('increased_energy_shield')
        armour += self._getExtraBonuses('added_armour')
        evasion += self._getExtraBonuses('added_evasion')
        es += self._getExtraBonuses('added_energy_shield')
        dmgFlat += self._getExtraBonuses('added_damage')
        dmgInc += self._getExtraBonuses('increased_damage')

        self._damage = int((self._baseDamage + dmgFlat) * (1 + dmgInc))
        self._maxHealth = int((self._maxHealth + healthFlat) * (1 + healthInc))
        self._maxStamina = self._baseMaxStamina + staminaFlat
        self._speed = (self._speed + spdFlat) * (1 + spdInc)
        self._speed += self._getExtraBonuses('speed')
        self._speed = round(self._speed, 2)

        # cap bonuses
        self._stats['Bonuses']['enemy_quantity'] = min(self._stats['Bonuses']['enemy_quantity'], 100)
        self._stats['Bonuses']['stun_avoidance'] = min(self._stats['Bonuses']['stun_avoidance'], 100)
        self._stats['Bonuses']['crit_resistance'] = min(self._stats['Bonuses']['crit_resistance'], 100)
        self._stats['Bonuses']['resistance_penetration'] = min(self._stats['Bonuses']['resistance_penetration'], 200)
        self._stats['Bonuses']['chance_to_block'] = min(self._stats['Bonuses']['chance_to_block'], 75)

        globalIncDef = self._stats['Bonuses']['increased_defenses'] / 100
        finalArmour = int(armour * (1 + globalArmourInc + globalIncDef))
        finalEvasion = int(evasion * (1 + globalEvasionInc + globalIncDef))
        finalEs = int(es * (1 + globalEsInc + globalIncDef))

        self._stats['armour'] = finalArmour
        self._stats['evasion'] = finalEvasion
        if not inCombat:
            self._stats['energy_shield'] = finalEs
        self._stats['max_energy_shield'] = finalEs

        if not inCombat:
            self._health = min(self._health, self._maxHealth)
        self._speed = round(self._speed, 2)

        self._applyConditionalModifiers(conditionalLines, inCombat)

        questBoard = getattr(self, '_questBoard', None)
        if questBoard is not None:
            questBoard.refreshStateChecks()

        if doPrint:
            console.print("\n[bold cyan]Stats updated:[/bold cyan]")
            console.print(f"[health]HP:[/health] {self._health} / {self._maxHealth}")
            console.print(f"[damage]DMG:[/damage] {self._damage} |[{self._damageType}] Type: {self._damageType.title()}[/{self._damageType}]")
            console.print(f"[speed]Speed:[/speed] {self._speed:.2f}")

            resistances = {}
            for res, val in self._stats['Resistances'].items():
                if val != 0:
                    resistances[res] = val
            if resistances:
                console.print("\n[bold]Resistances:[/bold]")
                for r, v in resistances.items():
                    vMax = self._stats['Max_Resistances'][r]
                    console.print(f"-  [{r}]{r.title()}[/{r}]: {v}% [dim](Max: {vMax}%)[/dim]")

            console.print()
            pause()

    def _applyConditionalModifiers(self, conditionalLines: list, inCombat: bool):
        for line in conditionalLines:
            condition = line.meta.get('condition')
            values = line.values

            if condition == 'damage_exceeds_max_hp':  # glass_cannon
                if self._damage > self._maxHealth:
                    self._damage = int(self._damage * (1 + values.get('x', 0) / 100))
                    defenseMult = 1 - values.get('y', 0) / 100
                    self._stats['armour'] = int(self._stats['armour'] * defenseMult)
                    self._stats['evasion'] = int(self._stats['evasion'] * defenseMult)
                    self._stats['max_energy_shield'] = int(self._stats['max_energy_shield'] * defenseMult)
                    if not inCombat:
                        self._stats['energy_shield'] = int(self._stats['energy_shield'] * defenseMult)
                    self._maxHealth = int(self._maxHealth * (1 - values.get('z', 0) / 100))
                    if not inCombat:
                        self._health = min(self._health, self._maxHealth)

            elif condition == 'two_or_more_debuffs':  # debuffed_fury
                debuffCount = 0
                if self.combatUnit is not None:
                    debuffCount = len([s for s in self.combatUnit.statusEffects
                                        if getattr(s, 'effectType', None) == 'debuff'])
                if debuffCount >= 2:
                    self._damage = int(self._damage * (1 + values.get('x', 0) / 100))
                    self._stats['Bonuses']['crit_chance'] += values.get('y', 0) / 100
                    self._stats['Bonuses']['increased_damage_taken'] += values.get('z', 0)

            elif condition == 'above_90_percent_hp':  # perfect_form
                hpFrac = (self._health / self._maxHealth) if self._maxHealth > 0 else 0
                if hpFrac > 0.9:
                    bonus = values.get('x', 0)
                    for res in ALL_RES:
                        self._stats['Resistances'][res] = min(
                            self._stats['Resistances'][res] + bonus,
                            self._stats['Max_Resistances'][res]
                        )

            elif condition == 'hp_above_below_50_percent':  # reckless_stride
                hpFrac = (self._health / self._maxHealth) if self._maxHealth > 0 else 1
                mult = values.get('x', 1.0) if hpFrac > 0.5 else values.get('y', 1.0)
                self._stats['evasion'] = int(self._stats['evasion'] * mult)

            elif condition == 'enemies_defeated_this_combat':  # momentum
                kills = line.meta.get('_mythicKills', 0)
                if kills:
                    self._speed = round(self._speed * (1 + kills * values.get('x', 0) / 100), 2)

            elif condition == 'stamina_full_or_below_50':  # tempo
                staminaFrac = (self._stamina / self._maxStamina) if self._maxStamina > 0 else 0
                if staminaFrac >= 1.0:
                    self._stats['Bonuses']['ability_cost_multiplier'] -= values.get('x', 0)
                elif staminaFrac < 0.5:
                    self._stats['Bonuses']['ability_cost_multiplier'] += values.get('y', 0)

            elif condition == 'no_status_buffs':
                self._damage = int(self._damage * (1 + values.get('x', 0) / 100))
                defenseMult = 1 + values.get('y', 0) / 100
                self._stats['armour'] = int(self._stats['armour'] * defenseMult)
                self._stats['evasion'] = int(self._stats['evasion'] * defenseMult)
                self._stats['max_energy_shield'] = int(self._stats['max_energy_shield'] * defenseMult)
                if not inCombat:
                    self._stats['energy_shield'] = int(self._stats['energy_shield'] * defenseMult)
                for res in self._stats['Resistances']:
                    self._stats['Resistances'][res] = min(
                        self._stats['Resistances'][res] + values.get('z', 0),
                        self._stats['Max_Resistances'][res]
                    )
                self._stats['Bonuses']['hp_regen'] = 0

    def useConsumable(self):
        if self.consumable.useable:
            heal = int(self._maxHealth * self.consumable.healPercent)
            self.heal(heal, reason=self.consumable.name)
            self.consumable.usesRemaining -= 1

    def showInventory(self):
        console.print("\n[bold cyan]=== INVENTORY ===[/bold cyan]")
        if not self._inventory:
            console.print(" [dim]- Empty[/dim]")
        else:
            for item, quantity in sorted(self._inventory.items()):
                item = item.replace('_', ' ').title()
                console.print(f" [cyan]- {item}:[/cyan] [gold]{quantity}[/gold]")

    def showAbilities(self):
        console.print("\n[bold cyan]=== abilities ===[/bold cyan]")
        if not self._abilities:
            printWarning("No abilities learnt yet!")
            return
        for name, ability in self._abilities.items():
            console.print(f" [bold]= {name} =[/bold]")
            if ability.damageType:
                damageTypeFormatted = f"[{ability.damageType}]{ability.damageType.title()}[/{ability.damageType}]"
                console.print(f"  [dim]- Base Damage: {ability.baseDamage} + {ability.damageScaling*100:.0f}% of damage | Type: {damageTypeFormatted}[/dim]")
            if ability.healBase or ability.healPercent:
                console.print(f"  [heal]- Heal: {ability.healBase} + {ability.healPercent*100:.0f}% Max HP[/heal]")
            console.print(f"  [dim]- Cooldown: {ability.maxCooldown} turns[/dim]")
            costStr = formatAbilityCost(ability.resources, ability.staminaCost)
            if costStr != "-":
                console.print(f"  [dim]- Cost: {costStr}[/dim]")
            for line in formatEffectsDetailed(ability.effects):
                console.print(f"  [buff]- {line}[/buff]")

    def showCraftingInventory(self):
        console.print('\n[cyan bold]=== Crafting Inventory ===[/cyan bold]')
        if not self._craftingInventory:
            console.print("[dim]No runes in crafting inventory[/dim]")
            return

        for key, quantity in sorted(self._craftingInventory.items()):
            cat, rtype = key.split('_', 1)
            rune = getRuneObject(cat, rtype)
            console.print(rune)
            console.print(f'[dim]Quantity: {quantity}[/dim]')
    
    # ===================================================================================== #
    # COMBAT HOOKS
    # Called by CombatManager.performAttack/applyDamageWithDefenses in this order, per attack:
    #   1. onBeforeDamage    (attacker) -> retarget/reroll before anything is finalised
    #   1.5. onMultihitActivated (Attacher) -> only called if a multihit is activated
    #   2. onBeforeCritRoll  (attacker) -> rollCritical() -> onAfterCritRoll (attacker)
    #   3. onCrit (attacker) / onCriticallyHit (target)      - only if the roll crit
    #   4. per target, once per multihit:
    #        onPrepareHit (attacker)     - attacker adjusts the hit for this specific target
    #        onBeforeHit (target)        - target reacts before mitigation is applied
    #        getArmourIgnorePercent (attacker)
    #        onAttack (attacker)
    #        getEffectiveEvasion / getEvasionRollCount / getEffectiveArmour (target) / onEnergyShieldBroken (target)
    #          - used inside applyDamageWithDefenses while rolling evasion/armour/energy shield
    #        onHit (target)              - target reacts to the mitigated damage number
    #        onDealDamage (attacker)     - attacker reacts, before damage is actually applied
    #        onAfterMitigation (target)  - target's last chance to change finalDamage
    #        onEvade (target)            - called if the hit was evaded, rendering further functions irrelevant
    #        damage is applied to target
    #        onDamaged (target)          - target reacts to the damage that just landed
    #        onAfterAttack (attacker)    - attacker reacts to the damage they just dealt
    #   5. once per target, after all multihits: mechanics/status effects applied, death checked
    #   6. onKill (attacker) if the target died, else onExecuteCheck (attacker)
    # Any hook may queue a StatusEffect via self._queueEffect() instead of returning one -
    # CombatManager drains _pendingEffects after the hook call and applies it to the
    # relevant target(s) once evasion has been resolved.
    # Every hook default here is a no-op/pass-through; rewrite per class as needed.
    # ===================================================================================== #

    def _queueEffect(self, effect):
        """Queues a StatusEffect (or list of them) to be applied once the current hit lands."""
        if isinstance(effect, list):
            self._pendingEffects.extend(effect)
        else:
            self._pendingEffects.append(effect)

    def _logDamage(self, reason: str, *, flat: int = 0, percent: float = 0.0):
        """Records why a hit's damage changed, for the breakdown CombatManager prints once the hit resolves.
        flat is an absolute amount (+/-), percent is a fraction of current damage (e.g. 0.1 for +10%).
        Call from any combat hook (attacker's or target's) that changes finalDamage/damageDealt - always
        on the top-level attacker passed into that hook, so every modifier for a hit lands in one log
        regardless of which side (attacker or target) applied it."""
        if flat or percent:
            self._damageLog.append((reason, flat, percent))

    def _mythicDispatch(self, hookName: str, *args, **kwargs) -> list:
        results = []
        for equipment in self._equipment.values():
            if not equipment or not equipment.mythicAffix:
                continue
            for line in equipment.mythicAffix.lines:
                handler = line.onActions.get(hookName)
                if handler:
                    result = handler(self, line, *args, **kwargs)
                    if result is not None:
                        results.append(result)
        return results

    def onBeforeDamage(self, ability: Ability, damage: int, damageType: str, targets: list[Entity], combatManager):
        """Rewrite per class. Returns: damage, damageType, targets"""
        return damage, damageType, targets

    def onBeforeCritRoll(self, targetUnit, targets: list[Entity], combatManager):
        """Rewrite per class"""
        pass

    def onAfterCritRoll(self, targetUnit, targets: list, combatManager):
        """Rewrite per class. Undo whatever onBeforeCritRoll applied. No return value."""
        pass

    def getArmourIgnorePercent(self) -> float:
        """Rewrite per class. Returns the fraction (0-1) of the target's armour this attack ignores."""
        return 0.0

    def getEffectiveEvasion(self, damageType: str, combatUnit) -> float:
        """Rewrite per class. Returns the evasion value to roll against for this hit."""
        return self.evasion

    def getEvasionRollCount(self, damageType: str) -> int:
        """Rewrite per class. Number of independent evasion rolls for this hit (evades if any succeed)."""
        return 1

    def getEffectiveArmour(self, damageType: str, combatUnit) -> float:
        """Rewrite per class. Returns the armour value to mitigate this hit with."""
        return self.armour

    def onEnergyShieldBroken(self, combatManager):
        """Rewrite per class. Called the moment this entity's energy shield is reduced to 0."""
        pass

    def onBeforeHit(self, finalDamage: int, damageType: str, attacker: Entity, combatManager) -> int:
        """Rewrite per class. return finalDamage"""
        return finalDamage

    def onAfterMitigation(self, attacker: Entity, finalDamage: int, damageType: str, evaded: bool,
                           armourDamagePrevented: int, esDamagePrevented: int, preMitigationDamage: int,
                           combatManager) -> int:
        """Rewrite per class. return finalDamage"""
        return finalDamage

    def onPrepareHit(self, target: Entity, targetUnit, finalDamage: int, damageType: str, combatManager) -> int:
        """Rewrite per class. return finalDamage"""
        return finalDamage

    def onDamaged(self, attacker: Entity, damageReductionValue: int, armourDamagePrevented: int, combatManager):
        """Rewrite per class"""
        pass

    def onDealDamage(self, target: Entity, targetUnit, finalDamage: int, damageType: str, evaded: bool,
                      armourDamagePrevented: int, esDamagePrevented: int, combatManager) -> int:
        """Rewrite per class. return finalDamage"""
        return finalDamage

    def onExecuteCheck(self, target: Entity, combatManager) -> bool:
        """Return true if executed, false if not. execute_threshold is stored as whole percentage points."""
        if target._health < target._maxHealth * (self._stats['Bonuses']['execute_threshold'] / 100):
            return True
        return False

    def onCC(self, attacker: Entity, combatManager):
        """Rewrite per class"""
        pass

    def onStatusApplied(self, status, attacker: Entity):
        """Rewrite per class, return status or None"""
        return status

    def onEvade(self, combatManager):
        """Rewrite per class"""
        return

    def onBlock(self, combatManager):
        """Rewrite per class"""
        return

    def onMultihitActivated(self):
        """Rewrite per class"""
        return

    def onAbilityCast(self, ability: Ability, combatManager):
        return

    def onAttack(self, damageDealt: int, damageType: str, target, combatManager, ability: Ability, crit: bool = False):
        """Target should be combatUnit. Fires once per target before mitigation (once per multihit)."""
        durabilityLoss = max(1, damageDealt // 25)
        if self._equipment.get('weapon'):
            weapon = self._equipment.get('weapon')
            weapon.durability = max(0, weapon.durability - (durabilityLoss // max(1, weapon.level // 10)))
            if weapon.durability == 0:
                printWarning(f"{weapon.name} has broken!")
                self.unequip('weapon', True, False)
        accessoryLoss = durabilityLoss // 2
        for slot in ['ring', 'amulet']:
            if self._equipment.get(slot):
                accessory = self._equipment.get(slot)
                accessory.durability = max(0, accessory.durability - (accessoryLoss // max(1, accessory.level // 10)))
                if accessory.durability == 0:
                    printWarning(f"{accessory.name} has broken!")
                    self.unequip(slot, True, False)

        healOnHit = self._stats['Bonuses']['health_on_hit']
        if healOnHit != 0:
            self.heal(healOnHit, reason="Health on Hit")

        ability.cooldown = ability.maxCooldown

        for stat, factory in _PROC_EFFECTS.items():
            chance = self._stats['Bonuses'].get(stat, 0)
            if chance > 0 and random.random() * 100 < chance:
                self._queueEffect(factory())

        return damageDealt, damageType

    def onHit(self, damageTaken: int, damageType: str, crit: bool, attacker: Entity, combatManager):
        durabilityLoss = max(1, damageTaken // 30)
        for slot in ['head', 'chest', 'legs', 'feet', 'offhand']:
            if self._equipment.get(slot):
                armour = self._equipment.get(slot)
                armour.durability = max(0, armour.durability - (durabilityLoss // max(1, armour.level // 10)))
                if armour.durability == 0:
                    printWarning(f"{armour.name} has broken!")
                    self.unequip(slot, True, False)

        self._stamina = min(self._maxStamina, self._stamina + self._stats['Bonuses']['stamina_on_hit'])

        return damageTaken, damageType

    def onKill(self, entity: Entity=None, attackData: Dict=None, combatManager=None) -> Optional[Dict]:
        """Rewrite per class. Call super() first (applies health/stamina on kill), always return None/dict\n
        attackData should include: final attack damage, damage type, mechanics of ability used"""
        healOnKill = self._stats['Bonuses']['health_on_kill']
        if healOnKill != 0:
            self.heal(healOnKill, reason="Health on Kill")
        self._stamina = min(self._maxStamina, self._stamina + self._stats['Bonuses']['stamina_on_kill'])
        return {}

    def onHeal(self, healAmount: int):
        """Rewrite per class"""
        pass

    def onCrit(self, targets: list[Entity], combatManager, critDamage: int) -> int:
        """Rewrite per class, called when dealing a critical hit. Returns critDamage"""
        return critDamage

    def onCriticallyHit(self, attacker: Entity, combatManager, critDamage: int, damageType: str) -> int:
        """Use super before overwriting, called when being critically hit. Reduces damage dealt by crit resistance. Returns critDamage"""
        critDamage = int(critDamage * (1 - (self._stats['Bonuses']['crit_resistance'] / 100)))
        return critDamage

    def onTurnStart(self, combatManager):
        """Recalculates stats for temp + permanent additions, use at end of onTurnStart methods"""
        self._recalculateStats(False, True)
        heal = self._stats['Bonuses']['hp_regen']
        if heal != 0:
            self.heal(heal, reason="HP Regeneration")
        self._stamina = min(self._maxStamina, self._stamina + 3 + self._stats['Bonuses']['stamina_regen'])
        if self._speed < 0.2: # minimum speed is 0.2
            self._speed = 0.2

        if self._foodBuff is not None:
            self._foodBuff['turnsRemaining'] -= 1
            if self._foodBuff['turnsRemaining'] <= 0:
                prefix = self._foodBuff.get('prefix')
                suffix = self._foodBuff.get('suffix')
                if prefix:
                    self._stats['Temporary'][prefix['stat']] -= prefix['value']
                if suffix:
                    self._stats['Temporary'][suffix['stat']] -= suffix['value']
                console.print(f"[dim]Your food's effects have worn off.[/dim]")
                self._foodBuff = None
                self._recalculateStats(False, True)

    def onTurnEnd(self):
        """Rewrite per class"""
        pass

    def onCombatStart(self, combatManager, combatUnit):
        """Assigns given combatUnit to self. run at the start of each onCombatStart"""
        self.combatUnit = combatUnit
        self._emergencyRevivalUsedThisCombat = False

    def onCombatEnd(self):
        """Sets all temporary stats to 0 and sets self.combatUnit to None, use at end of onCombatEnd methods."""
        for stat in self._stats['Temporary'].keys():
            self._stats['Temporary'][stat] = 0
        self.combatUnit = None
        self.consumable.usesRemaining = self.consumable.maxUses

    def onAfterAttack(self, target: Entity, targetUnit, finalDamage: int, combatManager):
        """Rewrite per class. No return"""
        pass

...