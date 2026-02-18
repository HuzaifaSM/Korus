from .base import Player, ELEMENTAL_RES, DIVINE_RES
from scripts.styles import console, formatDamageType, pause
import random

WARRIOR_DESCRIPTIONS = {
    "Warrior": "A strong but slower fighter.\n"
        "+3 Damage dealt per rage. +1 Rage per 8 damage dealt. -1 Rage per 5 damage taken. +2 HP per leftover rage at the end of combat.\n"
        "Dealing fire damage grants 1 additional rage. Taking fire damage reduces rage loss by 2.\n"
        "Starting Stats: 50 Health | 4 Damage | 5% Crit Chance | 200% Crit Damage | Fire Damage | 0.8 Speed | 50 Max Rage | +1 Rage on Level Up.",
    #ascendancies
    "Warlord": "50% less rage decay, gain fury stacks on attack if you have more than 30 rage.\n"
        "Fury: 2% Increased Damage, +2% lifesteal. Max 10 stacks of fury. At max Fury, your next attack deals 200% increased damage to all enemies and consmes all Fury.\n"
        "While above 40 Rage, gain 15% Damage Reduction.\n"
        "+10 HP. +1 Damage. -0.05 Speed",
    "Pyromancer": "Fire damage has a 40% chance to apply 1 stack of Burn. Every third fire attack applies 2 stacks of Burn to all enemies.\n"
        "Gain 2 rage per Burn stack on enemies at the start of your turn.\n"
        "Burning enemies take 50% more damage from your attacks.\n"
        "-5 HP. +1 Damage. +0.05 Speed. +15% Fire Resistance",
    "Juggernaut": "Gain 1 Fortify per 10 Rage, up to 20 stacks. +1% All Resistance, +2% Crit Chance, +5% Crit Damage per Fortify.\n"
        "50% Slower Rage Decay. At max Fortify your next attack hits all enemies, applies Stun and consumes 100 Rage."
        "+15 HP. -1 Damage. -0.05 Speed. +50% Stun Avoidance.",
    "Blood Reaver": "Attacks cost 5% Current HP and deal 50% Increased Damage. Gain +3% Lifesteal per 10 Rage, up to a maximum of +45% Lifesteal at 150 Rage.\n"
        "When your Rage exceeds your Max Rage, overflow is converted to healing at 3 HP per excess Rage\n"
        "Heal 3 HP per Rage at the end of combat.\n"
        "Gain +2% Lifesteal per 10 Rage, up to 30%.\n"
        "+10 HP. +1 Damage. +0.05 Speed",
    "Flamewarden": "Phoenix Aspect: Whilst above 50 Rage, you have Phoenix Aspect, allowing you to survive one lethal hit.\n"
        "Upon consuming Phoenix Aspect, consume all Rage and heal 2% Max HP per Rage consumed and gain Phoenix Form for 3 turns\n"
        "Phoenix Form: All attacks apply 2 stacks of Burn, Deal 50% Increased Fire damage, +0.2 Speed, +10 Rage per turn.\n"
        "+5 HP. +1 Damage. +20% Fire Resistance.",
    "Annihilist": "Gain 1 Annihilation per 30 Rage generated in combat. Annihilation lasts for the rest of combat and has no maximum stack limit.\n"
        "Annihilation: +20% Fire Damage, +0.1 Speed, +5% Crit Chance. Upon killing an enemy, lose 1 Annihilation and heal for 5% of your Max HP.\n"
        "Rage no longer heals you at the end of combat.\n"
        "-20 HP. +3 Damage. -0.05 Speed. +25% Crit Damage.",
    #subtypes
    "Savage": "Rage no longer affects damage. 15% Increased Damage.\n"
        "+25% Crit Chance, +50% Crit Damage against enemies below 20% health."
        "Whenever a single attack deals more than 10% of your Max HP, permanently gain 1 Scar. +1 Rage Generation per Scar.\n"
        "-10 HP. +2 Damage. -0.1 Speed. +2% Crit Chance\n",
    "Colossus": "Rage has 2x effect on damage. 20% more rage generated. 25% less rage lost.\n"
        "Whenever you take damage, recover 20% of damage taken at the start of your next turn.\n"
        "+15 HP. -1 Damage. -0.3 Speed. +10 Max Rage.",
    "Titan": "10% Increased Health. Rage grants +2 Damage instead of +3.\n"
        "While at or above 30 Rage, gain 10% Damage Reduction. While below 30 Rage, gain +10% Crit Chance, +25% Crit Damage.\n"
        "When you drop below 30% Max HP for the first time each combat, gain Titan's Fury for 4 turns.\n"
        "Titan's Fury: +20% Increased Damage, +10% Lifesteal, +5 Rage Generation.\n"
        "+10 HP. -2 Damage. -0.1 Speed. +10% Physical Resistance. +5% Fire Resistance."
}

class Warrior(Player): # higher damage, lower speed, fire damage
    def __init__(self, name, health = 50, damage = 4, damageType = "fire", speed = 0.8,
                 ascendancy = None, ascendancyDescription = None, subType = None):
        super().__init__(name, health, damage, 0.05, 2.0, damageType, speed,
                         className="Warrior", classDescription=WARRIOR_DESCRIPTIONS['Warrior'],
                         ascendancy=ascendancy, ascendancyDescription=ascendancyDescription, subType=subType)
        self._rage = 0 # build rage during combat, 1 rage = +3 damage
        self._maxRage = 30

        self._rageEffect = 1.0 # multiplier on rage effectiveness
        self._fury = 0
        self._maxFury = 10
        self.pyromancerAttacks = 0
        self.phoenixAspect = False
        self.phoenixUsed = False
        self._fortify = 0
        self._maxFortify = 20
        self.annihilationRage = 0
        self.annihilation = 0
        self.annihilationBuffs = {
            'fire': 0, 'speed': 0, 'critChance': 0
        }
        self.rageGeneration = 0
        self.scars = 0
        self.damageToRecoup = 0
        self.titanFuryTurns = 0
        self.titanFuryUsed = False

    def __str__(self):
        baseStr = super().__str__()
        
        if self._subType != "Savage":
            baseStr += f"\n[damage]Rage:[/damage] {self._rage} / {self._maxRage}"
        
        if self._ascendancy == "Warlord":
            baseStr += f"\n[gold1]Fury:[/gold1] {self._fury} / {self._maxFury}"
        elif self._ascendancy == "Juggernaut":
            baseStr += f"\n[buff]Fortify:[/buff] {self._fortify} / {self._maxFortify}"

        return baseStr

    def _serialise(self):
        temp = super()._serialise()
        temp['maxRage'] = self._maxRage
        temp['scars'] = self.scars
        temp['rageGeneration'] = self.rageGeneration
        return temp

    def deserialise(self, data):
        super().deserialise(data)
        self._maxRage = data.get('maxRage', 30)
        self.scars = data.get('scars', 0)
        self.rageGeneration = data.get('rageGeneration', 0)

    def rollCritical(self, target):
        critChance = self._stats['baseCritChance'] + (self._stats['Bonuses']['critChance']) + (self._stats['Permanent']['critChance']) + (self._stats['Temporary']['critChance'])
        critMulti = self._stats['baseCritMulti'] + (self._stats['Bonuses']['critMulti']) + (self._stats['Permanent']['critMulti']) + (self._stats['Temporary']['critMulti'])
        if self._subType == 'Savage':
            target = target.entity
            if target._health < (target._maxHealth * 0.2):
                critChance += 0.25
                critMulti += 0.5

        elif self._subType == 'Colossus' and self._rage < 30:
            critChance += 0.1
            critMulti += 0.25

        if self._ascendancy == 'Annihilist':
            critChance += self.annihilationBuffs['critChance']
            if random.random() < critChance:
                return True, critMulti
            
        if random.random() < critChance:
            return True, critMulti

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
            return super().damage(damage, damageType, combatUnit)

    def onAttack(self, damageDealt, damageType, target):
        super().onAttack(damageDealt, damageType)
        rageGain = damageDealt // 8
        if damageType == 'fire':
            rageGain += 1

        if self._ascendancy == 'Pyromancer':
            burnRage = sum(2 for effect in target.statusEffects if effect.name == 'burn')
            rageGain += burnRage
            self.pyromancerAttacks += 1

        if self._subType == 'Colossus':
            rageGain = int(rageGain * 1.2)

        self._rage = min(self._maxRage, self._rage + rageGain)
        self.annihilationRage += rageGain
        console.print(f"\n[damage]Your rage grows! +{rageGain} Rage. Current Rage: {self._rage} / {self._maxRage}[/damage]")
        
        if self._ascendancy == 'Annihilist':
            while self.annihilationRage >= 30:
                self.annihilationRage -= 30
                self.annihilation += 1

        if self._ascendancy == 'Annihilist' and damageType == 'fire':
            damageDealt = round(damageDealt * (1 + self.annihilationBuffs['fire']))

        if self._ascendancy == 'Flamewarden' and self._rage >= 50 and (not self.phoenixAspect or not self.phoenixUsed):
            self.phoenixAspect = True

        if self._ascendancy == 'Warlord' and self._rage >= 30 and self._fury < self._maxFury:
            self._fury += 1
            console.print(f"\n[bold damage]Your fury increases! Current Fury: {self._fury} / {self._maxFury}[/bold damage]")

        if self._subType == 'Savage':
            damageDealt = int(damageDealt * 1.15)
        elif self._subType == 'Titan':
            damageDealt = damageDealt + ((self._rage * 2) * self._rageEffect)
            if self.titanFuryTurns > 0:
                damageDealt = int(damageDealt * 1.2)
        else:
            damageDealt = damageDealt + ((self._rage * 3) * self._rageEffect)

        if self._ascendancy == 'Warlord':
            damageDealt = (damageDealt) * (1 + (0.02 * self._fury))
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
    
    def onHit(self, damageTaken, damageType):
        super().onHit(damageTaken, damageType)
        rageLoss = max(0, damageTaken // 5)
        if damageType != 'fire':
            rageLoss += 2

        if self._ascendancy == 'Warlord':
            rageLoss = rageLoss // 2
            if self._rage > 40:
                damageTaken = int(damageTaken * 0.85)

        if self._subType == 'Colossus':
            rageLoss = round(rageLoss * 0.75)
            recoup = int(damageTaken * 0.2)
            self.damageToRecoup += recoup
            console.print(f"  [buff]Colossus: Will recoup {recoup} HP at the start of your turn.[/buff]")

        elif self._subType == 'Savage':
            dmgPercent = damageTaken / self._maxHealth
            if dmgPercent > 0.1:
                self.scars += 1
                self.rageGeneration += 1
                console.print(f"  [gold1]Savage: Gained 1 Scar! +1 total Rage generation.[/gold1]")

        elif self._subType == 'Titan' and not self.titanFuryUsed:
            if self._health - damageTaken < self._maxHealth * 0.3:
                self.titanFuryTurns = 4
                self.titanFuryUsed = True
                console.print(f"\n[gold1]Titan: Dropped below 30% HP! Titan's Fury activated for 4 turns![/gold1]")
                console.print(f"  [gold1]+20% Damage, +10% Lifesteal, +5 Rage Generation![/gold1]")
                self._stats['Temporary']['lifesteal'] += 10
                self.rageGeneration += 5
                pause()
            
        if self._subType == 'Titan' and self._rage >= 30:
            damageTaken = int(damageTaken * 0.9)

        self._rage = max(0, min(self._maxRage, self._rage - rageLoss))
        console.print(f"\n[warning]Your rage wanes! -{rageLoss} Rage. Current Rage: {self._rage} / {self._maxRage}[/warning]")

        return damageTaken, damageType

    def onKill(self, entity):
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
        self.phoenixAspect = False
        self.phoenixUsed = False
        self.annihilationBuffs = {
            'fire': 0, 'speed': 0, 'critChance': 0
        }
        self.annihilation = 0
        self.damageToRecoup = 0
        if self.titanFuryUsed and self.titanFuryTurns > 0:
            self.rageGeneration -= 5
            self._Stats['Temporary']['lifesteal'] -= 10
        self.titanFuryTurns = 0
        self.titanFuryUsed = False
        super().onBattleEnd()

    def onTurnStart(self):
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
            self._stats['Temporary']['critChance'] += self.annihilationBuffs['critChance']
        
        if self._subType == 'Colossus':
            self.heal(self.damageToRecoup)
            console.print(f"  [heal]Colossus: Recouped {self.damageToRecoup} HP![/heal]")
            self.damageToRecoup = 0

        elif self._subType == 'Titan' and self.titanFuryTurns > 0:
            self.titanFuryTurns -= 1
            if self.titanFuryTurns == 0:
                self._stats['Temporary']['lifesteal'] -= 10
                self.rageGeneration -= 5
                console.print("\n[warning]Titan: Titan's Fury has worn off.[/warning]")

        super().onTurnStart()

    def _levelUp(self):
        self._maxRage += 1
        super()._levelUp()

    def _removeOldAscendancy(self):
        if self._ascendancy == 'Warlord':
            self._baseHealth -= 10
            self._baseDamage -= 1
            self._baseSpeed += 0.05
        elif self._ascendancy == 'Pyromancer':
            self._baseHealth += 5
            self._baseDamage -= 1
            self._baseSpeed -= 0.05
            self._stats['Permanent']['fire'] -= 15
        elif self.ascendancy == 'Juggernaut':
            self._baseHealth -= 15
            self._damage += 1
            self._baseSpeed += 0.05
            self._stats['Permanent']['stunAvoidance'] -= 50
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
        elif ascendancy == 'Pyromancer':
            self._baseHealth -= 5
            self._baseDamage += 1
            self._baseSpeed += 0.05
            self._stats['Permanent']['fire'] += 15
            self._ascendancy = 'Pyromancer'
            self.ascendancyDescription = WARRIOR_DESCRIPTIONS['Pyromancer']
        elif ascendancy == 'Juggernaut':
            self._baseHealth += 15
            self._damage -= 1
            self._baseSpeed -= 0.05
            self._stats['Permanent']['stunAvoidance'] += 50
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

    def _removeOldSubType(self):
        if self.subType == 'Savage':
            self._baseHealth += 10
            self._baseDamage -= 2
            self._baseSpeed += 0.1
            self._stats['baseCritChance'] -= 0.02
        elif self.subType == 'Colossus':
            self._baseHealth -= 15
            self._baseDamage += 1
            self._baseSpeed += 0.3
            self._maxRage -= 10
            self._rageEffect -= 1.0
        elif self.subType == 'Titan':
            self._baseHealth -= 10
            self._baseDamage += 2
            self._baseSpeed += 0.1
            self._stats['Permanent']['physical'] -= 10
            self._stats['Permanent']['fire'] -= 5
            self._stats['Permanent']['increased_health'] -= 10

    def updateSubType(self, subType):
        if self._subType is not None:
            self._removeOldSubType()
        if subType == None:
            self._subType = None
            self.subTypeDescription = None
        if subType == 'Savage':
            self._baseHealth -= 10
            self._baseDamage += 2
            self._baseSpeed -= 0.1
            self._stats['baseCritChance'] += 0.02
            self._subType = 'Savage'
            self.subTypeDescription = WARRIOR_DESCRIPTIONS['Savage']
        elif subType == 'Colossus':
            self._baseHealth += 15
            self._baseDamage -= 1
            self._baseSpeed -= 0.3
            self._maxRage += 10
            self._rageEffect += 1.0
            self._subType = 'Colossus'
            self.subTypeDescription = WARRIOR_DESCRIPTIONS['Colossus']
        elif subType == 'Titan':
            self._baseHealth += 10
            self._baseDamage -= 2
            self._baseSpeed -= 0.1
            self._stats['Permanent']['physical'] += 10
            self._stats['Permanent']['fire'] += 5
            self._stats['Permanent']['increased_health'] += 10
            self._subType = 'Titan'
            self.subTypeDescription = WARRIOR_DESCRIPTIONS['Titan']
        self._recalculateStats(False)

# Warlord = 1000+ damage in a single hit
# Pyromancer = 3+ enemies burning/ablaze simultaneously in 5 different combats
# Juggernaut = win a battle without dropping below 80% hp 10 times
# Bloodreaver = win 5 combats whilst staying below 30% hp
# Flamewarden = survive an attack on exaclty 1 hp 3 times
# Annihilist = kill 20 enemies with critical hits
# Savage = deal 10 critical hits in 1 combat
# Colossus = reach max rage 10 times
# Titan = have over 1000 max hp
