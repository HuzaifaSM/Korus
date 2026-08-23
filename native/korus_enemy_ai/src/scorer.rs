use crate::types::{Action, ActionCategory, CombatSnapshot, EnemyState};

pub fn scoreAction(action: &Action, enemy: &EnemyState, snapshot: &CombatSnapshot) -> Option<f32> {
    let player = &snapshot.player;

    if !canAfford(action, enemy) {
        return None;
    }

    let hpRatio = enemy.hp as f32 / enemy.maxHp as f32;
    let playerHpRatio = player.hp as f32 / player.maxHp as f32;
    let enemyBaseDmg = enemy.baseDamage.unwrap_or(enemy.hp / 10); // rough fallback

    let score = match action.category {
        ActionCategory::Attack | ActionCategory::Ability => {
            let baseDamage = action.damage.unwrap_or(0) as f32;
            let damageType = action.damageType.as_deref().unwrap_or("physical");

            let resistance = player.resistances.get(damageType).copied().unwrap_or(0);
            let resMult = 1.0 - (resistance as f32 / 100.0);
            let effectiveDmg = baseDamage * resMult;

            // sum estimated value of all status effects this action applies
            let effectValue: f32 = action.effects
                .as_ref()
                .map(|effects| {
                    effects.iter().map(|e| {
                        // curse ignores resistance - dont apply resMult to dot
                        let val = e.estimatedValue(enemyBaseDmg, player.maxHp);
                        if e.mechanic == "curse" { val } else { val * resMult.max(0.1) }
                    }).sum()
                })
                .unwrap_or(0.0);

            let categoryBonus = if action.category == ActionCategory::Ability { 1.15 } else { 1.0 };
            let finisherBonus = if playerHpRatio < 0.25 { 1.4 } else { 1.0 };

            (effectiveDmg + effectValue) * categoryBonus * finisherBonus
        }

        ActionCategory::Consumable => {
            if hpRatio > 0.35 {
                return None;
            }
            let healAmount = action.heal.unwrap_or(0) as f32;
            let recoveryRatio = healAmount / enemy.maxHp as f32;
            50.0 + ( recoveryRatio * 100.0 )
        }
    };

    Some(score)
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