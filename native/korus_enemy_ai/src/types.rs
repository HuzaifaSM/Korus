use serde::Deserialize;
use std::collections::HashMap;

// full combat snapshot passed from python each turn
// serde automatically maps JSON keys to field names
#[derive(Debug, Deserialize)]
pub struct CombatSnapshot {
    pub enemies: Vec<EnemyState>,
    pub player: PlayerState,
}

#[derive(Debug, Deserialize)]
pub struct EnemyState {
    pub index: usize, // index into enemies vec so engine can reference which enemy it is
    pub hp: i32,
    pub maxHp: i32,
    pub baseDamage: Option<i32>,
    pub damageType: String,
    pub resources: HashMap<String, i32>, // key = resource name, value = current amount
    pub availableActions: Vec<Action>,
    pub difficulty: f32, // 0.0 = random, 1.0 = optimal
}

#[derive(Debug, Deserialize)]
pub struct PlayerState {
    pub hp: i32,
    pub maxHp: i32,
    pub resistances: HashMap<String, i32>, // key = damage type, value = resistance %
    pub speed: f32,
}

// single action the enemy can potentially take this turn
#[derive(Debug, Deserialize, Clone)]
pub struct Action {
    pub id: String,
    pub category: ActionCategory,
    pub damage: Option<i32>, // attack/ability actions - base damage before resistances
    pub damageType: Option<String>, // attack ability actions - damage type being dealt
    pub effect: Option<String>, // for buff/defensive actions - plain text description of effect
    pub heal: Option<i32>, // consumable/heal - flat hp restored
    pub cost: HashMap<String, i32>, // resource costs, must all be affordable for action to be valid
    pub effects: Option<Vec<ActionEffect>>, // status effects this action can apply on hit
}

// status effect that an action can apply. mirrors structure in abilities.json
#[derive(Debug, Deserialize, Clone)]
pub struct ActionEffect {
    pub mechanic: String,
    pub effectType: String,
    pub chance: Option<f32>,
    pub turns: Option<i32>,
    pub value: Option<f32>,
    // dot specific
    pub baseDamage: Option<f32>,
    pub damagePercent: Option<f32>, // fraction of attacker damage per tick
    // debuff specific
    pub amount: Option<f32>,
    pub resistanceReduction: Option<f32>,
}

impl ActionEffect {
    // estimates total value of effect in effective hp damage terms
    // used to score actions that apply status effects alongside damage
    //
    // enemyBaseDamage - needed for DoT scaling
    // playerMaxHp - used for CC scaling and debuff values
    pub fn estimatedValue(&self, enemyBaseDamage: i32, playerMaxHp: i32) -> f32 {
        let chance = self.chance.unwrap_or(1.0).clamp(0.0, 1.0);
        let turns = self.turns.unwrap_or(1) as f32;
        
        let rawValue = match self.effectType.as_str() {
            "dot" => {
                let base = self.baseDamage.unwrap_or(0.0);
                let scaling = self.damagePercent.unwrap_or(0.0) * enemyBaseDamage as f32;
                let perTick = base + scaling;

                // secondary effect bonus
                let secondaryBonus = match self.mechanic.as_str() {
                    // bleed: -0.05 speed per stack. lets enemy act first. estimated as 2% of player max hp over turns
                    "bleed" => playerMaxHp as f32 * 0.02,
                    // burn: -5 all resistances - subsequent hits are stronger. estimate as 5% of enemyBaseDamage * turns
                    "burn" => enemyBaseDamage as f32 * turns * 0.05,
                    // poison: -10% healing magnitude - less player recovery. worth 5% max hp over turns
                    "poison" => playerMaxHp as f32 * 0.05,
                    // curse: ignores resistances. effective damage is full value. without any resistance multiplier - already handled
                    "curse" => 0.0,
                    _ => 0.0,
                };

                (perTick * turns) + secondaryBonus
            }

            "cc" => {
                let turnValue = playerMaxHp as f32 * 0.1; // stun counts as 10% of player max hp
                let freezeBonus = if self.mechanic == "freeze" {
                    playerMaxHp as f32 * 0.03 // 3% extra player max hp, freeze has +25% crit damage taken
                } else { 
                    0.0 
                };
                (turnValue + freezeBonus) * turns
            }

            "debuff" => {
                match self.mechanic.as_str() {
                    // speed reductions - enemies act first more often. 0.1 speed loss ~~ 3% player max hp per turn
                    "chill" | "slow" | "daze" => {
                        let speedLoss = self.amount.unwrap_or(0.2);
                        (speedLoss / 0.1) * (playerMaxHp as f32 * 0.03) * turns
                    }
                    // blind - reduces player effective damage output. miss = loss attack ~~ 10% player max hp per turn
                    "blind" => {
                        let missChance = self.amount.unwrap_or(0.2);
                        missChance * (playerMaxHp as f32 * 0.1) * turns
                    }
                    // weaken - reduces player dmg dealt, reduction * 0.1 player mhp per turn - assumed player hits for 10% max hp
                    "weaken" => {
                        let reduction = self.amount.unwrap_or(0.25);
                        reduction * (playerMaxHp as f32 * 0.1) * turns
                    }
                    // exposed - reduces all resistances, enemy hits harder. 1% resistance loss = 1% more damage per turn
                    "exposed" => {
                        let resReduction = self.value.unwrap_or(10.0);
                        resReduction * enemyBaseDamage as f32 * turns
                    }
                    // resistance exposure - targeted version of exposed, less overall effective. 50% effective of exposed
                    "elemental_exposure" | "divine_exposure" |
                    "physical_exposure" | "otherworld_exposure" => {
                        let resReduction = self.value.unwrap_or(30.0);
                        resReduction * enemyBaseDamage as f32 * 0.5 * turns
                    }
                    _ => 5.0 * turns,
                }
            }

            "buff" => {
                match self.mechanic.as_str() {
                    "shield_generation" => self.value.unwrap_or(0.0) * turns, // flat effective hp gain per turn
                    "regeneration" => self.value.unwrap_or(0.0) * turns, // hp recovery per turn
                    "haste" => enemyBaseDamage as f32 * 0.1 * turns, // speed + damage buff, estimate as 10% enemy damage per turn
                    "might" => self.value.unwrap_or(0.0) * turns, // direct damage buff
                    // stoneskin - damage reduction, estimated in damage prevented
                    "stoneskin" => {
                        let reduction = self.value.unwrap_or(0.2);
                        (playerMaxHp as f32 * 0.1) * reduction * turns
                    }
                    _ => 5.0 * turns,
                }
            }

            "special" => {
                match self.mechanic.as_str() {
                    "first_strike" => {
                        let mult = self.value.unwrap_or(2.0);
                        enemyBaseDamage as f32 * (mult - 1.0)
                    }
                    _ => 0.0,
                }
            }

            _ => 0.0,
        };

        rawValue * chance
    }
}

// mirrors 'category' field in json
// serde maps string directly to enum variant
#[derive(Debug, Deserialize, Clone, PartialEq)]
#[serde(rename_all = "lowercase")]
pub enum ActionCategory {
    Attack,
    Ability,
    Consumable,
}
