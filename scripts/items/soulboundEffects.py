from copy import deepcopy
from typing import Callable, Dict


def _patchFlowingStrikes(ability, affix):
    ability.effects['self']['haste']['damage'] = 1 + (affix.value / 100)

def _patchOpeningStrike(ability, affix):
    ability.effects['target']['vulnerable']['amount'] = affix.value / 100

def _patchShieldBash(ability, affix):
    ability.effects['target']['exposed']['amount'] = affix.value

def _patchBulwarkStance(ability, affix):
    ability.effects['self']['stoneskin']['amount'] = affix.value / 100

def _patchArcaneDetonation(ability, affix):
    ability.damageScaling = affix.value / 100

def _patchHexbreaker(ability, affix):
    ability.effects['target']['weaken']['amount'] = affix.value / 100

def _patchWardstone(ability, affix):
    ability.effects['self']['shield_generation']['amount_percent'] = affix.value / 100

def _patchSanctuary(ability, affix):
    ability.effects['self']['regeneration']['amount_percent'] = affix.value / 100

def _patchSeveringKick(ability, affix):
    ability.effects['target']['elemental_exposure']['amount'] = affix.value

ABILITY_PATCHERS: Dict[str, Callable] = {
    'flowing_strikes': _patchFlowingStrikes,
    'opening_strike': _patchOpeningStrike,
    'shield_bash': _patchShieldBash,
    'bulwark_stance': _patchBulwarkStance,
    'arcane_detonation': _patchArcaneDetonation,
    'hexbreaker': _patchHexbreaker,
    'wardstone': _patchWardstone,
    'sanctuary': _patchSanctuary,
    # weapon/armour/ring/amulet grants reuse the patchers above - same effect shape, different flavour
    'titans_fury': _patchFlowingStrikes,
    'executioners_verdict': _patchOpeningStrike,
    'third_eye': _patchShieldBash,
    'unbroken_will': _patchBulwarkStance,
    'second_heart': _patchSanctuary,
    'martyrs_resolve': _patchWardstone,
    'relentless_charge': _patchFlowingStrikes,
    'crippling_stride': _patchHexbreaker,
    'windrunners_gait': _patchFlowingStrikes,
    'severing_kick': _patchSeveringKick,
    'bloodpact_surge': _patchOpeningStrike,
    'veins_of_vigor': _patchSanctuary,
    'soul_anchor': _patchWardstone,
    'apotheosis_echo': _patchFlowingStrikes,
}

def buildGrantedSoulboundAbility(affix):
    if affix.stat != 'grant_ability':
        return None
    from scripts.abilities import SOULBOUND_GRANTED_ABILITIES
    abilityKey = affix.data.get('ability')
    baseAbility = SOULBOUND_GRANTED_ABILITIES.get(abilityKey)
    if baseAbility is None:
        return None
    ability = deepcopy(baseAbility)
    patcher = ABILITY_PATCHERS.get(abilityKey)
    if patcher:
        patcher(ability, affix)
    return ability
