#![allow(non_snake_case, unused_assignments, dead_code)]

mod types;
mod scorer;
mod tree;

use types::CombatSnapshot;
use crate::scorer::{scoreAction, selectAction, findNeediestAlly, shouldUseConsumable, lookaheadDepth, lookaheadValue};
use crate::tree::selectCandidatePool;
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

        let useConsumable = shouldUseConsumable(enemy, &snapshot);

        let candidatePool = selectCandidatePool(enemy, &snapshot);

        // 1-ply scores for everything in tree-narrowed pool
        let scoredPly1: Vec<(&types::Action, f32)> = candidatePool.into_iter().filter_map(|action| {
            scoreAction(action, enemy, &snapshot).map(|score| (action, score))
        }).collect();

        // extend each candidate's score using other candidate's 1-ply scores as a stand in for what would happen next turn
        let depth = lookaheadDepth(difficulty);
        let mut scored: Vec<(&types::Action, f32)> = scoredPly1.iter().map(|&(action,ply1Score)| {
            let bestOther = scoredPly1.iter().filter(|(a, _)| a.id != action.id)
                .map(|(_, s)| *s).fold(f32::NEG_INFINITY, f32::max);
            let bestOther = if bestOther.is_finite() { bestOther } else { 0.0 };
            (action, lookaheadValue(action, ply1Score, bestOther, depth))
        }).collect();

        scored.sort_by(|a, b| b.1.partial_cmp(&a.1).unwrap_or(std::cmp::Ordering::Equal));

        match selectAction(&scored, difficulty) {
            Some(action) => {
                let reasoning = buildReasoning(enemy, action, &snapshot);
                let mut decision = json!({
                    "enemyIndex": enemy.index,
                    "actionId": action.id,
                    "category": format!("{:?}", action.category).to_lowercase(),
                    "reasoning": reasoning,
                    "useConsumable": useConsumable,
                    "scores": scored.iter().map(|(a, s)| {
                        json!({ "actionId": a.id, "score": (s * 100.0).round() / 100.0 })
                    }).collect::<Vec<_>>()
                });

                if action.category == types::ActionCategory::Heal {
                    if let Some(ally) = findNeediestAlly(enemy, &snapshot) {
                        decision["allyTargetIndex"] = json!(ally.index);
                    }
                }

                decision
            }
            None => {
                let fallback = enemy.availableActions.first();
                match fallback {
                    Some(a) => json!({
                        "enemyIndex": enemy.index,
                        "actionId":   a.id,
                        "category":   "attack",
                        "reasoning":  "fallback - no valid actions scored",
                        "useConsumable": useConsumable,
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

fn buildReasoning(enemy: &types::EnemyState, action: &types::Action, snapshot: &CombatSnapshot) -> String {
    let player = &snapshot.player;
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
        types::ActionCategory::Heal => {
            match findNeediestAlly(enemy, snapshot) {
                Some(ally) => format!("Ally is low on HP ({}/{}), using basic heal", ally.hp, ally.maxHp),
                None => "Using basic heal".to_string(),
            }
        }
    }
}
