mod types;
mod scorer;

use types::CombatSnapshot;
use crate::scorer::{scoreAction, selectAction};
use serde_json::json;
use std::io::{self, Read};

fn main() {
    let mut input = String::new();
    if let Err(e) = io::stdin().read_to_string(&mut input) {
        eprintln!("Error reading stdin: {}", e);
        std::process::exit(1);
    }

    let snapshot: CombatSnapshot = match serde_json::from_str(&input) {
        Ok(s) => s,
        Err(e) => {
            eprintln!("Error parsing JSON: {}", e);
            std::process::exit(1);
        }
    };

    // produce 1 decision per enemy
    let decisions: Vec<serde_json::Value> = snapshot.enemies.iter().map(|enemy| {
        let difficulty = enemy.difficulty.clamp(0.0, 1.0);

        let mut scored: Vec<(&types::Action, f32)> = enemy.availableActions
            .iter()
            .filter_map(|action| {
                scoreAction(action, enemy, &snapshot).map(|score| (action, score))
            })
            .collect();
        
        scored.sort_by(|a, b| b.1.partial_cmp(&a.1).unwrap_or(std::cmp::Ordering::Equal));

        match selectAction(&scored, difficulty) {
            Some(action) => {
                let reasoning = buildReasoning(enemy, action, &snapshot);
                json!({
                    "enemyIndex": enemy.index,
                    "actionId": action.id,
                    "category": format!("{:?}", action.category).to_lowercase(),
                    "reasoning": reasoning,
                    "scores": scored.iter().map(|(a, s)| {
                        json!({ "actionId": a.id, "score": (s * 100.0).round() / 100.0 })
                    }).collect::<Vec<_>>()
                })
            }
            None => {
                let fallback = enemy.availableActions.first();
                match fallback {
                    Some(a) => json!({
                        "enemyIndex": enemy.index,
                        "actionId":   a.id,
                        "category":   "attack",
                        "reasoning":  "fallback - no valid actions scored",
                        "scores":     []
                        }),
                    None => json!({
                        "enemyIndex": enemy.index,
                        "error": "no actions available"
                    }),
                }
            }
        }
    }).collect();

    println!("{}", json!({ "decisions": decisions }));
}

fn buildReasoning(
    enemy: &types::EnemyState,
    action: &types::Action,
    snapshot: &CombatSnapshot,
) -> String {
    let player = &snapshot.player;
    let hpRatio = enemy.hp as f32 / enemy.maxHp as f32;
    let playerHpRatio = player.hp as f32 / player.maxHp as f32;

    match action.category {
        types::ActionCategory::Attack | types::ActionCategory::Ability => {
            let dmgType = action.damageType.as_deref().unwrap_or("physical");
            let resistance = player.resistances.get(dmgType).copied().unwrap_or(0);

            let hasEffects = action.effects.as_ref().map(|e| !e.is_empty()).unwrap_or(false);
            let effectNote = if hasEffects { " (applies status effects)" } else { "" };

            if resistance < 0 {
                format!("Player is weak to {}{} ({}% Resistance)", dmgType, effectNote, resistance)
            } else if playerHpRatio < 0.25 {
                format!("Player is on low HP ({}/{}), going for the kill{}", player.hp, player.maxHp, effectNote)
            } else {
                format!("Best damage option - {} dmg, {} type{}", action.damage.unwrap_or(0), dmgType, effectNote)
            }
        }
        types::ActionCategory::Consumable => {
            format!("Low HP ({:.0}%), using consumable", hpRatio * 100.0)
        }
    }
}
