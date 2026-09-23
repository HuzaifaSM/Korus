import random
from copy import deepcopy
from typing import Callable, Dict, Optional
from ..entities import ELEMENTAL_RES, DIVINE_RES, OTHERWORLD_RES

_RESISTANCE_GROUPS = {
    'physical': ['physical'],
    'elemental': ELEMENTAL_RES,
    'divine': DIVINE_RES,
    'otherworld': OTHERWORLD_RES,
}

ALL_DAMAGE_TYPES = ['physical', 'fire', 'cold', 'lightning', 'earth', 'dark', 'holy',
                    'arcane', 'ethereal', 'psychic', 'chaos']


def _resolveTargetEntity(target):
    return getattr(target, 'entity', target)

# -- damage_type_double: locks the weapon's damage type and doubles damage of that type -- #

def _damageTypeDouble(entity, line, ability, damage, damageType, targets, combatManager):
    dtype = line.meta.get('damage_type')
    if not dtype:
        return None
    return {'damageType': dtype, 'damage': damage * 2}

# -- damage_type_override: chance to switch to whichever type the target resists least -- #

def _damageTypeOverride(entity, line, ability, damage, damageType, targets, combatManager):
    chance = line.values.get('x', 0) / 100
    if random.random() >= chance:
        return None
    if not targets:
        return None
    targetEntity = _resolveTargetEntity(targets[0])
    pool = line.meta.get('pool', 'all')
    candidates = list(OTHERWORLD_RES) if pool == 'otherworld' else list(ALL_DAMAGE_TYPES)
    resistances = targetEntity._stats.get('Resistances', {})
    best = min(candidates, key=lambda t: resistances.get(t, 0))
    return {'damageType': best}

# -- negate_resistance_group: attacks of a given group treat the target's resistance as
#    negative by temporarily spiking this attacker's own resistance_penetration (an existing,
#    already-wired stat CombatUnit.getResistanceModifier reads from the attacker) for the
#    duration of the hit, then resetting it once the attack resolves -- #

def _negateResistanceGroupOnAttack(entity, line, damageDealt, damageType, target, combatManager, ability, crit):
    group = _RESISTANCE_GROUPS.get(line.meta.get('group'), [])
    if damageType not in group:
        return None
    ratio = line.values.get('x', 1.0)
    baseline = entity._stats['Bonuses'].get('resistance_penetration', 0)
    line.meta['_penBaseline'] = baseline  # restore this, not 0, so other gear's own bonus survives
    entity._stats['Bonuses']['resistance_penetration'] = max(baseline, min(200, ratio * 100))
    return None

def _negateResistanceGroupOnAfterAttack(entity, line, target, targetUnit, finalDamage, combatManager):
    if '_penBaseline' in line.meta:
        entity._stats['Bonuses']['resistance_penetration'] = line.meta.pop('_penBaseline')
    return None

# -- ignore_stat_defense (ignore_crit_resistance): same cross-entity shape as above, applied
#    to the defender's crit_resistance instead, scoped to this one crit -- #

def _ignoreCritResistanceOnCrit(entity, line, targets, combatManager, critDamage):
    if not targets:
        return None
    ratio = line.values.get('x', 0) / 100
    targetEntity = _resolveTargetEntity(targets[0])
    critResist = targetEntity._stats['Bonuses'].get('crit_resistance', 0)
    recovered = critDamage * (critResist / 100) * ratio
    return int(critDamage + recovered)

# -- unyielding: caps any single hit at a fraction of max HP -- #

def _unyieldingOnAfterMitigation(entity, line, attacker, finalDamage, damageType, evaded,
                                  armourDamagePrevented, esDamagePrevented, preMitigationDamage, combatManager):
    if evaded or finalDamage <= 0:
        return None
    threshold = line.values.get('x', 0) / 100 * entity._maxHealth
    if finalDamage >= threshold:
        return 0
    return None

# -- clarity: first time you drop below 25% HP each combat, cleanse debuffs and become
#    immune to new ones for a couple of turns -- #

def _clarityOnAfterMitigation(entity, line, attacker, finalDamage, damageType, evaded,
                               armourDamagePrevented, esDamagePrevented, preMitigationDamage, combatManager):
    if line.meta.get('_triggered'):
        return None
    hpAfter = entity._health - finalDamage
    if entity._maxHealth <= 0 or hpAfter / entity._maxHealth >= 0.25:
        return None
    line.meta['_triggered'] = True
    turns = int(line.values.get('x', 1))
    if entity.combatUnit is not None:
        entity.combatUnit.statusEffects = [s for s in entity.combatUnit.statusEffects if s.effectType != 'debuff']
    line.meta['_immuneTurns'] = turns
    return None

def _clarityOnCombatStart(entity, line, combatManager, combatUnit):
    line.meta['_triggered'] = False
    line.meta['_immuneTurns'] = 0
    return None

def _clarityOnTurnStart(entity, line, combatManager):
    if line.meta.get('_immuneTurns', 0) > 0:
        line.meta['_immuneTurns'] -= 1
    return None

def _clarityOnStatusApplied(entity, line, status, attacker):
    if line.meta.get('_immuneTurns', 0) > 0 and getattr(status, 'effectType', None) == 'debuff':
        return False
    return status

# -- vital_nova: first time you drop below 25% HP, nova all enemies for a % of current HP -- #

def _vitalNovaOnAfterMitigation(entity, line, attacker, finalDamage, damageType, evaded,
                                 armourDamagePrevented, esDamagePrevented, preMitigationDamage, combatManager):
    if line.meta.get('_triggered'):
        return None
    hpAfter = entity._health - finalDamage
    if entity._maxHealth <= 0 or hpAfter / entity._maxHealth >= 0.25:
        return None
    line.meta['_triggered'] = True
    if hpAfter <= 0:
        return None  # this hit is lethal - nothing left to nova with
    novaDamage = int(hpAfter * (line.values.get('x', 0) / 100))
    combatMgr = combatManager
    enemies = [u for u in getattr(combatMgr, 'allAlive', []) if u is not entity and getattr(u, 'team', None) != getattr(entity, 'team', None)]
    for unit in enemies:
        target = _resolveTargetEntity(unit)
        target.damage(novaDamage, 'true')
    return None

def _vitalNovaOnCombatStart(entity, line, combatManager, combatUnit):
    line.meta['_triggered'] = False
    return None

# -- momentum (conditional_modifier, "enemies_defeated_this_combat"): the running kill count
#    lives on line.meta (reset each combat) - _recalculateStats reads it every turn to apply
#    the speed bonus, since a live kill counter has nowhere else to live -- #

def _momentumOnKill(entity, line, target, killData, combatManager):
    line.meta['_mythicKills'] = line.meta.get('_mythicKills', 0) + 1
    return None

def _momentumOnCombatStart(entity, line, combatManager, combatUnit):
    line.meta['_mythicKills'] = 0
    return None

# -- broken_rhythm (conditional_modifier, "every_3rd_attack_taken"): a per-hit counter, doesn't
#    fit the live-stat-check model _recalculateStats uses for the rest of the family -- #

def _brokenRhythmOnAfterMitigation(entity, line, attacker, finalDamage, damageType, evaded,
                                    armourDamagePrevented, esDamagePrevented, preMitigationDamage, combatManager):
    if evaded or finalDamage <= 0:
        return None
    line.meta['_hitsTaken'] = line.meta.get('_hitsTaken', 0) + 1
    if line.meta['_hitsTaken'] % 3 == 0:
        return int(finalDamage * (1 - line.values.get('x', 0) / 100))
    return None

# -- self_reliance (conditional_modifier, "no_status_buffs"): the flat damage/defense/resistance
#    trade and the hp_regen removal are handled live in _recalculateStats; only the "cannot gain
#    buffs" half needs a hook, to actually block incoming buff statuses -- #

def _selfRelianceOnStatusApplied(entity, line, status, attacker):
    if getattr(status, 'effectType', None) == 'buff':
        return False  # falsy, not None - see _clarityOnStatusApplied for why
    return status

BESPOKE_HANDLERS: Dict[str, Dict[str, Callable]] = {}

for _affixId in ('weapon_double_physical', 'weapon_double_fire', 'weapon_double_cold',
                 'weapon_double_lightning', 'weapon_double_earth', 'weapon_double_dark',
                 'weapon_double_holy', 'weapon_double_arcane', 'weapon_double_ethereal',
                 'weapon_double_psychic', 'weapon_double_chaos'):
    BESPOKE_HANDLERS[_affixId] = {'onBeforeDamage': _damageTypeDouble}

BESPOKE_HANDLERS['voidstep'] = {'onBeforeDamage': _damageTypeOverride}
BESPOKE_HANDLERS['exploit_weakness'] = {'onBeforeDamage': _damageTypeOverride}

for _affixId in ('sunder_physical_resistance', 'sunder_elemental_resistance',
                 'sunder_otherworld_resistance', 'sunder_divine_resistance'):
    BESPOKE_HANDLERS[_affixId] = {
        'onAttack': _negateResistanceGroupOnAttack,
        'onAfterAttack': _negateResistanceGroupOnAfterAttack,
    }

BESPOKE_HANDLERS['ignore_crit_resistance'] = {'onCrit': _ignoreCritResistanceOnCrit}

BESPOKE_HANDLERS['unyielding'] = {'onAfterMitigation': _unyieldingOnAfterMitigation}

BESPOKE_HANDLERS['clarity'] = {
    'onAfterMitigation': _clarityOnAfterMitigation,
    'onCombatStart': _clarityOnCombatStart,
    'onTurnStart': _clarityOnTurnStart,
    'onStatusApplied': _clarityOnStatusApplied,
}

BESPOKE_HANDLERS['vital_nova'] = {
    'onAfterMitigation': _vitalNovaOnAfterMitigation,
    'onCombatStart': _vitalNovaOnCombatStart,
}

BESPOKE_HANDLERS['momentum'] = {
    'onKill': _momentumOnKill,
    'onCombatStart': _momentumOnCombatStart,
}

BESPOKE_HANDLERS['broken_rhythm'] = {'onAfterMitigation': _brokenRhythmOnAfterMitigation}

BESPOKE_HANDLERS['self_reliance'] = {'onStatusApplied': _selfRelianceOnStatusApplied}


def getHandlers(affixId: Optional[str], effect: str) -> Dict[str, Callable]:
    return BESPOKE_HANDLERS.get(affixId, {})

# ============================================================================================ #
# -- grant_ability: patches the rolled line's values into a copy of that affix's Ability.
#    A few of these (noted per-patcher) collapse a dynamic flavour-text mechanic - stacks
#    spent this cast, cumulative combat damage, stolen buffs, temporary lifesteal - into a
#    fixed numeric buff, since there's no live counter/status plumbing for them yet. -- #

def _patchOverpower(ability, line):
    # "[x]% Execute Threshold per 10 Stamina spent, [y]% increased Damage per 5 Stamina spent"
    # no execute-threshold mechanic exists to hook x into, so both rolls collapse into one
    # flat damage buff sized off the ability's own (fixed) Stamina cost.
    stamina = ability.staminaCost or 40
    totalPercent = line.values.get('x', 1.0) * (stamina / 10) + line.values.get('y', 1.0) * (stamina / 5)
    ability.effects['self']['haste']['damage'] = 1 + (totalPercent / 100)

def _patchUnderworldStrike(ability, line, equipment=None):
    twoHanded = bool(getattr(equipment, 'twoHanded', True))
    ability.damageScaling = line.values.get('x', 1.5) if twoHanded else line.values.get('y', 1.2)
    ability.effects['target']['vulnerable']['amount'] = line.values.get('z', 20) / 100

def _patchBuffTheft(ability, line):
    # "steal one active enemy buff" simplifies to a flat Weaken, scaled off the steal chance.
    ability.effects['target']['weaken']['amount'] = round(line.values.get('x', 70) / 100 * 0.3, 3)

def _patchBloodlust(ability, line):
    # lifesteal (y) has no temporary-buff plumbing to hook into; only the damage buff (x) applies.
    ability.effects['self']['haste']['damage'] = 1 + (line.values.get('x', 50) / 100)

def _patchDetonate(ability, line):
    # "% of total Damage dealt so far this combat" has no running counter to read at cast time;
    # collapses to a flat weapon-damage multiplier of the same magnitude.
    ability.damageScaling = 1 + (line.values.get('x', 10) / 100)

def _patchAegis(ability, line):
    ability.effects['self']['shield_generation']['amount_percent'] = line.values.get('x', 25) / 100

def _patchAllIn(ability, line):
    # crit chance/multiplier (x/y) and self-defense-reduction (w) have no matching status types;
    # collapse into one flat damage buff, keeping the (real) flat Speed bonus from z.
    ability.effects['self']['haste']['damage'] = 1 + ((line.values.get('x', 100) + line.values.get('y', 100)) / 200)
    ability.effects['self']['haste']['speed'] = line.values.get('z', 0.5)

ABILITY_PATCHERS: Dict[str, Callable] = {
    'overpower': _patchOverpower,
    'underworld_strike': _patchUnderworldStrike,
    'buff_theft': _patchBuffTheft,
    'bloodlust': _patchBloodlust,
    'detonate': _patchDetonate,
    'aegis': _patchAegis,
    'all_in': _patchAllIn,
}

def buildGrantedAbility(line, equipment=None):
    """Returns a fresh, rolled-value-patched Ability for this line's grant_ability affix,
    or None if it's not a recognised grant_ability line (or the base ability is missing)."""
    if line.effect != 'grant_ability':
        return None
    from scripts.abilities import MYTHIC_GRANTED_ABILITIES
    abilityKey = line.meta.get('ability')
    baseAbility = MYTHIC_GRANTED_ABILITIES.get(abilityKey)
    if baseAbility is None:
        return None
    ability = deepcopy(baseAbility)
    patcher = ABILITY_PATCHERS.get(abilityKey)
    if patcher:
        if abilityKey == 'underworld_strike':
            patcher(ability, line, equipment)
        else:
            patcher(ability, line)
    return ability
