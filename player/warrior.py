from .base import Player, ELEMENTAL_RES, DIVINE_RES
from scripts.styles import console, formatDamageType, pause
import random

"""
replace flamewarden with new Tyrant ascendancy:
    - take 20% less damage from attacks that deal less damage than your base damage
    - added armour. taking damage hsa no effect on rage, gain rage based on amount of damage prevented from armour
    - intended as 'armour stacking' ascendancy
"""

WARRIOR_DESCRIPTIONS = {
    "Warrior": "[class_warrior]A proud and tenacious warrior, emboldened by the thrill of battle.[/class_warrior]\n"
        "+3 Damage dealt per Rage. +1 Rage per 6 damage dealt. -1 Rage per 8 damage taken. +2 HP per leftover Rage at the end of combat.\n"
        "Dealing [fire]Fire[/fire] damage grants +1 Rage. Taking [fire]Fire[/fire] damage reduces Rage loss by 2.\n"
        "Starting Stats: 50 [health]Health[/health] | 4 [damage]Damage[/damage] | 5% Crit Chance | 200% Crit Damage | [fire]Fire Damage[/fire] | 0.8 [speed]Speed[/speed] | Max 50 Rage | +1 Rage on Level Up.",
    #ascendancies
    "Warlord": "50% less Rage decay, gain Fury stacks on attack if you have more than 50 Rage.\n"
        "Fury: 2% Increased Damage, +2% Lifesteal. Max 10 stacks of Fury. At max Fury, your next attack deals 200% Increased Damage to all enemies and consumes all Fury.\n"
        "While above 40 Rage, gain 15% Damage Reduction. Upon dealing a Critical Hit, gain +20% Crit Multi per stack of Fury.\n"
        "Gain 1% Damage Reduction per 20 Rage. All damage prevented from Damage Reduction is gained as Shield. Whenever an enemy attacks you, deal 50 Fire Damage to them.\n"
        "-1% Crit Chance per 50 Shield. Deal 1% Increased Damage per 25 Shield. Whenever your shield is broken, heal for 3% of your Max HP and deal [fire]Fire[/fire] damage to all enemies equal to 5% of current HP.\n"
        "-10 HP. +2 [damage]Damage[/damage]. +0.05 [speed]Speed[/speed]. +15% Fire Resistance. +10% Physical Resistance.",
    "Juggernaut": "You have 1 Fortify per 10 Rage, up to 20 stacks. +1% Damage Reduction, +2% Crit Chance, +5% Crit Damage per Fortify.\n"
        "50% Slower Rage Decay. At max Fortify your next attack hits all enemies, applies [cc]Stun[/cc] and consumes 100 Rage.\n"
        "Whenever you are critically hit, take 35% less damage from that hit and gain Bastion until the end of your next turn.\n"
        "Bastion: +5% Damage Reduction, +20% Crit Chance, +50% Crit Damage, -0.2 Speed.\n"
        "+20 HP. -2 [damage]Damage[/damage]. -0.1 [speed]Speed[/speed]. +50% Stun Avoidance. +10% Fire Resistance.",
    "Blood Reaver": "Attacks cost 5% Current HP and deal 50% Increased Damage. Gain +3% Lifesteal per 10 Rage, up to a maximum of +45% Lifesteal at 150 Rage.\n"
        "When your Rage exceeds your Max Rage, overflow is converted to healing at 3 HP per excess Rage. At the end of combat, heal 1% Max HP per 1% Rage.\n"
        "At the start of your turn, if you are below 20% Max HP, gain Bloodlust: +10% Lifesteal, +10% Crit Chance, +25% Physical Resistance.\n"
        "Upon killing an enemy, gain 1% Increased Damage per 50 damage dealt for the rest of combat.\n"
        "+15 HP. -2 [damage]Damage[/damage]. -0.1 [speed]Speed[/speed]. +5% Lifesteal.",
    "Flamewarden": "Phoenix Aspect: Whilst above 50 Rage, you have Phoenix Aspect, allowing you to survive one lethal hit.\n"
        "Upon consuming Phoenix Aspect, consume all Rage and heal 2% Max HP per Rage consumed and gain Phoenix Form for 3 turns.\n"
        "Phoenix Form: All attacks apply 2 stacks of Burn, Deal 50% Increased Fire damage, +0.2 Speed, +10 Rage per turn.\n"
        "Whilst you are above 40% Max HP, gain: 25% Increased Fire damage, +2% Max HP Regenerated at the start of your turn, +0.2 Speed.\n"
        "If you kill an enemy with a critical hit, regain Phoenix Aspect if it was used up.\n"
        "+5 HP. +1 Damage. -0.1 Speed. +20% Fire Resistance. +10 HP Regen",
    "Annihilist": "Gain 1 Annihilation per 30 Rage generated in combat. Annihilation lasts for the rest of combat and has no maximum stack limit.\n"
        "Annihilation: +20% Fire Damage, +0.1 Speed, +5% Crit Chance. Upon killing an enemy, lose 1 Annihilation and heal for 5% of your Max HP.\n"
        "Rage no longer heals you at the end of combat. Whenever you critically hit an enemy, gain 2% of the enemy's damage as your own per stack of Annihilation you have.\n"
        "-20 HP. +3 [damage]Damage[/damage]. -0.05 [speed]Speed[/speed]. +25% Crit Damage.",
}

class Warrior(Player): # higher damage, lower speed, fire damage
    def __init__(self, name, health = 50, damage = 4, damageType = "fire", speed = 0.8):
        super().__init__(name, health, damage, 0.05, 2.0, damageType, speed, className="Warrior", classDescription=WARRIOR_DESCRIPTIONS['Warrior'])
        self._rage = 0 # build rage during combat, 1 rage = +3 damage
        self._maxRage = 30

        self._rageEffect = 1.0 # multiplier on rage effectiveness
        self._fury = 0
        self._maxFury = 10
        self.phoenixUsed = False
        self._fortify = 0
        self._maxFortify = 20
        self.annihilationRage = 0
        self.annihilation = 0
        self.annihilationBuffs = {
            'fire': 0, 'speed': 0, 'critChance': 0
        }
        self.rageGeneration = 0

    @property
    def phoenixAspect(self):
        return self._rage >= 50 and not self.phoenixUsed

    def __str__(self):
        baseStr = super().__str__()
        
        if self._ascendancy == "Warlord":
            baseStr += f"\n[gold1]Fury:[/gold1] {self._fury} / {self._maxFury}"
        elif self._ascendancy == "Juggernaut":
            baseStr += f"\n[buff]Fortify:[/buff] {self._fortify} / {self._maxFortify}"

        return baseStr

    def _serialise(self):
        temp = super().serialise()
        temp['maxRage'] = self._maxRage
        temp['rageGeneration'] = self.rageGeneration
        return temp

    def deserialise(self, data):
        super().deserialise(data)
        self._maxRage = data.get('maxRage', 30)
        self.rageGeneration = data.get('rageGeneration', 0)

    def rollCritical(self, target, damageDealt=None):
        critChance = self.critChance
        critMulti = self.critMulti

        if self._ascendancy == 'Annihilist':
            critChance += self.annihilationBuffs['critChance']

        if random.random() < critChance:
            return True, critMulti
        return False, 1.0

    def damage(self, damage, damageType, combatUnit=None):
        if self._ascendancy == 'Flamewarden' and self.phoenixAspect and not self.phoenixUsed:
            if combatUnit:
                resistMod = combatUnit.getResistanceModifier(damageType)
            else:
                resistMod = self._stats['Resistances'].get(damageType, 0) / 100
                if damageType in ELEMENTAL_RES:
                    resistMod += self._stats['Resistances']['elemental'] / 100
                elif damageType in DIVINE_RES:
                    resistMod += self._stats['Resistances']['divine'] / 100
                resistMod += self._stats['Resistances']['all'] / 100
                resistMod = min(0.75, resistMod)
            damage = damage - round(damage * resistMod)
            trueDamage = damage - self._shield
            damagePrevented = damage - trueDamage
            self._shield -= damagePrevented
            self._health -= damage
            damageTypeFormatted = formatDamageType(damageType, damageType)
            console.print(f" [damage]- {self._name} took {damage} {damageTypeFormatted} damage.[/damage] [dim buff]({damagePrevented} damage prevented with shield)[/dim buff] [dim]HP remaining: {self._health} / {self._maxHealth}[/dim]")
            if self._health <= 0 and not self._isDead: # prevented from phoenix
                self._health = 1
                healPercent = min(1, self._rage / 100)
                healAmount = self._maxHealth * healPercent
                console.print(f"\n[success] Flamewarden: You were dealt a fatal blow, but your Phoenix Aspect saved you!\n")
                self.heal(healAmount)
                self.phoenixUsed = True
                pause()
        else:
            super().damage(damage, damageType, combatUnit)

    def onAttack(self, damageDealt, damageType, target=None, combatManager=None):
        super().onAttack(damageDealt, damageType, target, combatManager)
        rageGain = damageDealt // 6
        if damageType == 'fire' and damageDealt > 0:
            rageGain += 1

        self._rage = min(self._maxRage, self._rage + rageGain)
        self.annihilationRage += rageGain
        if rageGain > 0:
            console.print(f"\n[damage]Your Rage grows! +{rageGain} Rage. Current Rage: {self._rage} / {self._maxRage}[/damage]")
        
        if self._ascendancy == 'Annihilist':
            while self.annihilationRage >= 30:
                self.annihilationRage -= 30
                self.annihilation += 1

        if self._ascendancy == 'Annihilist' and damageType == 'fire':
            damageDealt = round(damageDealt * (1 + self.annihilationBuffs['fire']))

        if self._ascendancy == 'Warlord' and self._rage >= 30 and self._fury < self._maxFury:
            self._fury += 1
            console.print(f"\n[bold damage]Your fury increases! Current Fury: {self._fury} / {self._maxFury}[/bold damage]")

        damageDealt = damageDealt + ((self._rage * 3) * self._rageEffect)

        if self._ascendancy == 'Warlord':
            damageDealt = int(damageDealt * (1 + (0.02 * self._fury)))
            damageDealt = int(damageDealt * (1 + (0.01 * (self._shield // 25))))
            self.heal(damageDealt * (0.02 * self._fury)) # lifesteal 2% per fury

        if self._ascendancy == 'Blood Reaver':
            healthPercent = (damageDealt // 50) / 100
            healthLoss = self._maxHealth * healthPercent
            damageMult = 1 + 0.01 * (healthLoss // 20)
            dmgPerc = (damageMult - 1) * 100
            damageDealt = damageDealt * damageMult
            if (self._health - healthLoss) < 1: # not through damage method
                self._health = 1
            else:
                self._health -= healthLoss
            console.print(f"\n[warning]You sacrifice {healthPercent} of your life ({healthLoss} HP) to deal {dmgPerc}% More Damage.[/warning]")
            lifestealPercent = min(30, self._rage // 10) / 100
            lifestealHeal = self._maxHealth * lifestealPercent
            console.print(f"\n[success]{lifestealPercent}% Blood Reaver Lifesteal:\n[/success]")
            self.heal(lifestealHeal)

        return damageDealt, damageType
    
    def onHit(self, damageTaken, damageType, isCrit, attacker, combatManager):
        super().onHit(damageTaken, damageType, isCrit, attacker, combatManager)
        if self._rage > 0:
            rageLoss = max(0, damageTaken // 8)
            if damageType != 'fire':
                rageLoss += 2

            if self._ascendancy == 'Warlord':
                damageTaken = int(damageTaken * (1 - (0.01 * (self._shield // 50))))
                rageLoss = rageLoss // 2
                if self._rage > 40:
                    damageTaken = int(damageTaken * 0.85)

            self._rage = max(0, min(self._maxRage, self._rage - rageLoss))
            console.print(f"\n[warning]Your Rage wanes! -{rageLoss} Rage. Current Rage: {self._rage} / {self._maxRage}[/warning]")

        return damageTaken, damageType

    def onKill(self, entity, data, combatManager):
        if self._ascendancy == 'Annihilist':
            if self.annihilation > 0:
                self.annihilation -= 1
                heal = int(self._maxHealth * 0.05)
                console.print("  [heal]- Annihilist: Consumed 1 Annihilation stack to Heal 5% Max HP![/heal]")
                self.heal(heal)
        return None

    def onBattleEnd(self):
        healAmount = self._rage // 2
        if self._ascendancy == 'Blood Reaver':
            healAmount += self._rage * 2
        if self._ascendancy != 'Annihilist':
            self.heal(healAmount)
        self._rage = 0
        self._fury = 0
        self._fortify = 0
        self.phoenixUsed = False
        self.annihilationBuffs = {
            'fire': 0, 'speed': 0, 'critChance': 0
        }
        self.annihilation = 0
        self.damageToRecoup = 0
        super().onBattleEnd()

    def onTurnStart(self, combatManager=None):
        if self.rageGeneration > 0:
            self._rage = min(self._maxRage, self._rage + self.rageGeneration)
            console.print(f"[dark_red] +{self.rageGeneration} Rage gained from Rage Generation![/dark_red]")
        if self._ascendancy == 'Juggernaut':
            self._fortify = min(self._maxFortify, self._rage // 10)
            console.print(f"[gold1]Juggernaut: Fortify set to {self._fortify} stacks. Current rage: {self._rage} / {self._maxRage} Rage.[/gold1]")
        
        if self._ascendancy == 'Juggernaut':
            self._fortify = min(self._maxFortify, self._rage // 10)
            console.print(f"\n[earth] Juggernaut: You now have {self._fortify} / {self._maxFortify} Fortify Stacks. (+{self._fortify}% All Resistance)")
        
        elif self._ascendancy == 'Annihilist':
            self.annihilationBuffs = {
                'fire': 0.2 * self.annihilation,
                'speed': 0.1 * self.annihilation,
                'critChance': 0.05 * self.annihilation
            }
            self._stats['Temporary']['speed'] += self.annihilationBuffs['speed']
            self._stats['Temporary']['crit_chance'] += self.annihilationBuffs['critChance']
        
        super().onTurnStart()

    def _levelUp(self):
        self._maxRage += 1
        super()._levelUp()

    def _removeOldAscendancy(self):
        if self._ascendancy == 'Warlord':
            self._baseHealth -= 10
            self._baseDamage -= 1
            self._baseSpeed += 0.05
        elif self.ascendancy == 'Juggernaut':
            self._baseHealth -= 15
            self._damage += 1
            self._baseSpeed += 0.05
            self._stats['Permanent']['stun_avoidance'] -= 50
        elif self.ascendancy == 'Blood Reaver':
            self._baseHealth -= 10
            self._baseDamage -= 1
            self._baseSpeed -= 0.05
        elif self.ascendancy == 'Flamewarden':
            self._baseHealth -= 5
            self._baseDamage -= 1
            self._stats['Permanent']['fire'] -= 20
        elif self.ascendancy == 'Annihilist':
            self._baseHealth += 20
            self._baseDamage -= 3
            self._baseSpeed += 0.05
            self._stats['baseCritMulti'] -= 0.25

    def updateAscendancy(self, ascendancy):
        if self._ascendancy is not None:
            self._removeOldAscendancy()
        if ascendancy == 'Warlord':
            self._baseHealth += 10
            self._baseDamage += 1
            self._baseSpeed -= 0.05
            self._ascendancy = 'Warlord'
            self.ascendancyDescription = WARRIOR_DESCRIPTIONS['Warlord']
        elif ascendancy == 'Juggernaut':
            self._baseHealth += 15
            self._damage -= 1
            self._baseSpeed -= 0.05
            self._stats['Permanent']['stun_avoidance'] += 50
            self._ascendancy = 'Juggernaut'
            self.ascendancyDescription = WARRIOR_DESCRIPTIONS['Juggernaut']
        elif ascendancy == 'Blood Reaver':
            self._baseHealth += 10
            self._baseDamage += 1
            self._baseSpeed += 0.05
            self._ascendancy = 'Blood Reaver'
            self.ascendancyDescription = WARRIOR_DESCRIPTIONS['Blood Reaver']
        elif ascendancy == 'Flamewarden':
            self._baseHealth += 5
            self._baseDamage += 1
            self._stats['Permanent']['fire'] += 20
            self._ascendancy = 'Flamewarden'
            self.ascendancyDescription = WARRIOR_DESCRIPTIONS['Flamewarden']
        elif ascendancy == 'Annihilist':
            self._baseHealth -= 20
            self._baseDamage += 3
            self._baseSpeed -= 0.05
            self._stats['baseCritMulti'] += 0.25
            self._ascendancy = 'Annihilist'
            self.ascendancyDescription = WARRIOR_DESCRIPTIONS['Annihilist']
        self._recalculateStats(False)

