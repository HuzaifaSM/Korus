use crate::types::{Action, ActionCategory, CombatSnapshot, EnemyState};

pub fn scoreAction(action: &Action, enemy: &EnemyState, snapshot: &CombatSnapshot) -> Option<f32> {
    let player = &snapshot.player;

    if !canAfford(action, enemy) {
        return None;
    }

    let playerHpRatio = player.hp as f32 / player.maxHp as f32;
    let enemyBaseDmg = enemy.baseDamage.unwrap_or(enemy.hp / 10); // rough fallback

    let score = match action.category {
        ActionCategory::Attack | ActionCategory::Ability => {
            let baseDamage = action.damage.unwrap_or(0) as f32;
            let damageType = action.damageType.as_deref().unwrap_or("physical");

            let resistance = player.resistances.get(damageType).copied().unwrap_or(0);
            let resMult = 1.0 - (resistance as f32 / 100.0);
            let effectiveDmg = baseDamage * resMult;

            // effects split based on who they actually apply to
            let mut targetEffectValue = 0.0;
            let mut selfEffectUtility = 0.0;
            if let Some(effects) = &action.effects {
                for e in effects {
                    if e.target.as_deref() == Some("self") {
                        selfEffectUtility += e.selfUtility(enemyBaseDmg);
                    } else {
                        let val = e.estimatedValue(enemyBaseDmg, player.maxHp);
                        targetEffectValue += if e.mechanic == "curse" { val } else { val * resMult.max(0.1) };
                    }
                }
            }

            let categoryBonus = if action.category == ActionCategory::Ability { 1.15 } else { 1.0 };
            let finisherBonus = if playerHpRatio < 0.25 { 1.4 } else { 1.0 };

            (effectiveDmg + targetEffectValue) * categoryBonus * finisherBonus + selfEffectUtility
        }

        ActionCategory::Heal => {
            let ally = findNeediestAlly(enemy, snapshot)?;
            let allyHpRatio = ally.hp as f32 / ally.maxHp.max(1) as f32;

            if allyHpRatio >= 0.9 {
                return None; // nobody actually needs healing - don't waste the turn
            }

            let missingRatio = 1.0 - allyHpRatio;
            let urgency = if missingRatio > 0.7 { 1.5 } else { 1.0 }; // extra priority once an ally is close to dying
            missingRatio * ally.maxHp as f32 * 0.6 * urgency
        }
    };

    Some(score)
}

// finds the most-injured living ally (excluding the enemy itself), if any exist.
// also used by main.rs to report which ally a chosen Heal action should target.
pub fn findNeediestAlly<'a>(enemy: &EnemyState, snapshot: &'a CombatSnapshot) -> Option<&'a EnemyState> {
    snapshot.enemies.iter()
        .filter(|a| a.index != enemy.index && a.hp > 0)
        .min_by(|a, b| {
            let ra = a.hp as f32 / a.maxHp.max(1) as f32;
            let rb = b.hp as f32 / b.maxHp.max(1) as f32;
            ra.partial_cmp(&rb).unwrap_or(std::cmp::Ordering::Equal)
        })
}

// mitigates a raw hit by enemy's own resistance to that damage type
fn mitigatedDamage(rawDamage: i32, damageType: &str, enemy: &EnemyState) -> f32 {
    let resistance = enemy.resistances.get(damageType).copied().unwrap_or(0);
    let resMult = 1.0 - (resistance as f32 / 100.0);
    (rawDamage as f32 * resMult).max(0.0)
}

// true if player's single hardest hit available could immediately kill this enemy
pub fn isLethallyThreatened(enemy: &EnemyState, snapshot: &CombatSnapshot) -> bool {
    let player = &snapshot.player;

    let mut worstHit = mitigatedDamage(player.damage, &player.damageType, enemy);
    for ability in &player.abilities {
        let damageType = ability.damageType.as_deref().unwrap_or(&player.damageType);
        worstHit = worstHit.max(mitigatedDamage(ability.damage, damageType, enemy));
    }

    worstHit >= enemy.hp as f32
}

// whether enemy should use consumable this turn (free action)
pub fn shouldUseConsumable(enemy: &EnemyState, snapshot: &CombatSnapshot) -> bool {
    if !enemy.consumableAvailable {
        return false;
    }
    let hpRatio = enemy.hp as f32 / enemy.maxHp.max(1) as f32;
    hpRatio <= 0.35 || isLethallyThreatened(enemy, snapshot)
}

fn canAfford(action: &Action, enemy: &EnemyState) -> bool {
    for (resource, &cost) in &action.cost {
        let available = enemy.resources.get(resource).copied().unwrap_or(0);
        if available < cost {
            return false;
        }
    }
    true
}

pub fn selectAction<'a>(scored: &[(&'a Action, f32)], difficulty: f32) -> Option<&'a Action> {
    if scored.is_empty() {
        return None;
    }

    let maxScore = scored.iter().map(|(_, s)| *s).fold(f32::NEG_INFINITY, f32::max);
    let exponent = 1.0 + (difficulty * 4.0);

    let weights: Vec<f32> = scored
        .iter()
        .map(|(_, score)| (score / maxScore).powf(exponent))
        .collect();

    let totalWeight: f32 = weights.iter().sum();
    let threshold = totalWeight * 0.5;
    let mut cumulative = 0.0;

    for (i, w) in weights.iter().enumerate() {
        cumulative += w;
        if cumulative >= threshold {
            return Some(scored[i].0);
        }
    }

    scored.iter().max_by(|a, b| a.1.partial_cmp(&b.1).unwrap()).map(|(a, _)| *a)
}

// -- lookahead -- \\

pub fn lookaheadDepth(difficulty: f32) -> u8 {
    if difficulty >= 0.7 { 3 }
    else if difficulty >= 0.4 { 2 }
    else { 1 }
}

pub fn lookaheadValue(action: &Action, ply1Score: f32, bestOtherScore: f32, depth: u8) -> f32 {
    if depth <= 1 || bestOtherScore <= 0.0 {
        return  ply1Score;
    }

    let hasteEffect = action.effects.as_ref().and_then(|effects| {
        effects.iter().find(|e| e.target.as_deref() == Some("self") && e.mechanic == "haste")
    });

    let (mutliplier, buffTurns) = match hasteEffect {
        Some(e) => (e.damageMultiplier.unwrap_or(1.0), e.turns.unwrap_or(1).max(0) as u8),
        None => (1.0, 0),
    };

    let discount: f32 = 0.0;
    let mut total = ply1Score;
    for ply in 1..depth {
        let buffStillActive = ply <= buffTurns;
        let plyMultiplier = if buffStillActive { mutliplier } else { 1.0 };
        total += bestOtherScore * plyMultiplier * discount.powi(ply as i32);
    }
    total
}