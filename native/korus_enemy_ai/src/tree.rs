use crate::scorer::isLethallyThreatened;
use crate::types::{Action, ActionCategory, CombatSnapshot, EnemyState};

pub fn selectCandidatePool<'a>(enemy: &'a EnemyState, snapshot: &CombatSnapshot) -> Vec<&'a Action> {
    let all: Vec<&Action> = enemy.availableActions.iter().collect();

    // survival takes priority - unless this enemy's aggression roll says to
    // ignore the danger and act normally anyway (rolled in python per turn)
    if isLethallyThreatened(enemy, snapshot) && !enemy.ignoresDanger {
        let survival = survivalSequence(&all);
        if !survival.is_empty() {
            return survival;
        }
        // nothing purely defensive available, at minimum don't self-stun
        let safe: Vec<&Action> = all.iter().copied().filter(|a| !hasSelfCC(a)).collect();
        if !safe.is_empty() {
            return  safe;
        }
    }

    // support: always heal or buff while any other ally is alive, no exceptions
    // beyond the survival check above. buildActionList only ever offers a Heal
    // category action while a living ally exists, so its presence here already
    // means "not alone" - and basic_heal itself always satisfies this filter,
    // so it's never empty while that's true.
    if enemy.className == "support" {
        let hasHealOption = all.iter().any(|a| a.category == ActionCategory::Heal);
        if hasHealOption {
            let supportive: Vec<&Action> = all.iter().copied()
                .filter(|a| a.category == ActionCategory::Heal || hasSelfBenefit(a))
                .collect();
            if !supportive.is_empty() {
                return supportive;
            }
        }
    }

    // keep buffs up: no active buff right now, OR this enemy's cautious roll
    // says to play defensively anyway -> prioritise a genuinely safe buff
    // option if one exists. hasSelfBenefit already excludes anything that
    // also carries a self-stun/freeze, so a champion's charge-up abilities are
    // untouched here and stay governed entirely by championSequence's own hp gate
    if !enemy.hasActiveBuff || enemy.actsDefensively {
        let buffOptions: Vec<&Action> = all.iter().copied().filter(|a| hasSelfBenefit(a)).collect();
        if !buffOptions.is_empty() {
            return buffOptions;
        }
    }

    let narrowed = if enemy.className == "support" {
        supportTree(enemy, &all)
    } else {
        attackerTree(enemy, &all)
    };

    if narrowed.is_empty() { all } else { narrowed }
}

// -- survival -- \\

fn survivalSequence<'a>(all: &[&'a Action]) -> Vec<&'a Action> {
    let selfDefensive: Vec<&Action> = all.iter().copied().filter(|a| hasSelfBenefit(a)).collect();
    if !selfDefensive.is_empty() {
        return selfDefensive;
    }

    match all.iter().find(|a| a.id == "basic_attack") {
        Some(&a) => vec![a],
        None => Vec::new(),
    }
}

fn hasSelfBenefit(action: &Action) -> bool {
    if hasSelfCC(action) {
        return false;
    }

    action.effects.as_ref().map_or(false, |effects| {
        effects.iter().any(|e| e.target.as_deref() == Some("self") && e.effectType == "buff")
    })
}

fn hasSelfCC(action: &Action) -> bool {
    action.effects.as_ref().map_or(false, |effects| {
        effects.iter().any(|e| e.target.as_deref() == Some("self") && e.effectType == "cc")
    })
}

// -- attacker subtree -- \\

fn attackerTree<'a>(enemy: &'a EnemyState, all: &[&'a Action]) -> Vec<&'a Action> {
    match enemy.ascendancy.as_deref() {
        Some("champion") => championSequence(enemy, all),
        Some("fanatic") => fanaticSelector(all),
        Some("debilitator") => debilitatorSelector(all),
        _ => Vec::new(),
    }
}

// champion: if a "charge" ability is available (self-stun) and this enemy isn't critically low, prioritise it
fn championSequence<'a>(enemy: &'a EnemyState, all: &[&'a Action]) -> Vec<&'a Action> {
    let hpRatio = enemy.hp as f32 / enemy.maxHp.max(1) as f32;
    if hpRatio < 0.4 {
        return Vec::new();
    }

    match all.iter().find(|a| isChargeAbility(a)) {
        Some(&a) => vec![a],
        None => Vec::new(),
    }
}

fn isChargeAbility(action: &Action) -> bool {
    action.effects.as_ref().map_or(false, |effects| {
        effects.iter().any(|e| e.mechanic == "stun" && e.target.as_deref() == Some("self"))
    })
}

// fanatic: never basic attack whilt it has any ability available
fn fanaticSelector<'a>(all: &[&'a Action]) -> Vec<&'a Action> {
    all.iter().copied().filter(|a| a.id != "basic_attack").collect()
}

// debilitator: strongly prefers offensie abilites that apply debuff/dot to target
fn debilitatorSelector<'a>(all: &[&'a Action]) -> Vec<&'a Action> {
    all.iter().copied().filter(|a| hasTargetDebuff(a)).collect()
}

fn hasTargetDebuff(action: &Action) -> bool {
    action.effects.as_ref().map_or(false, |effects| {
        effects.iter().any(|e| {
            e.target.as_deref() != Some("self") && matches!(e.effectType.as_str(), "dot" | "debuff" | "cc")
        })
    })
}

// -- support subtree -- \\

// only ever reached once no living ally exists (the root-level check above
// already handles the "any ally alive" case before this function runs)
fn supportTree<'a>(enemy: &'a EnemyState, all: &[&'a Action]) -> Vec<&'a Action> {
    match enemy.ascendancy.as_deref() {
        Some("tank") => tankSelector(all),
        Some("standard_bearer") => buffSelector(all),
        _ => Vec::new(),
    }
}

// tank: prioritise keeping taunt up or reinforcing self
fn tankSelector<'a>(all: &[&'a Action]) -> Vec<&'a Action> {
    all.iter().copied().filter(|a| {
        a.effects.as_ref().map_or(false, |effects| {
            effects.iter().any(|e| e.mechanic == "taunt" || e.effectType == "buff")
        })
    }).collect()
}

// standard_bearer: prioritise buff kit
fn buffSelector<'a>(all: &[&'a Action]) -> Vec<&'a Action> {
    all.iter().copied().filter(|a| {
        a.effects.as_ref().map_or(false, |effects| {
            effects.iter().any(|e| e.effectType == "buff")
        })
    }).collect()
}