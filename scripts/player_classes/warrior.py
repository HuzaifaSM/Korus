from .base import Player
from scripts.styles import console
from scripts.abilities import Effects
import random

WARRIOR_DESCRIPTIONS = {
    "Warrior": "[class_warrior]A proud and tenacious combatant, emboldened by the thrill of battle.[/class_warrior]\n"
        "- +2 Damage dealt per Rage. Gain Rage based on Damage Dealt when attacking. Gain Rage based on Damage Taken when being hit. +2 HP per leftover Rage at the end of combat.\n"
        "- Upon levelling up, gain 5% Increased Rage Effect. And +1 Max Rage. You start with 50 Max Rage."
        "- Dealing Fire damage increases Rage gain by 10%. Taking Fire damage increases Rage gain by 20%.\n"
        "[bold]Starting Stats:[/bold] 50 Health | 4 Damage | 5% Crit Chance | 200% Crit Damage | Fire Damage | 0.85 Speed",
    #ascendancies
    "Warlord": "[lore]Feel your Rage flow through your veins, empowering you to even greater heights. Embrace your inner Fury, and slaughter those who dare face you.[/lore]"
        "- 20% Increased Rage gained from dealing damage. Gain 1 Fury on attack if you have more than 50 Rage.\n"
        "- Fury: 5% Increased Damage, +2% Lifesteal. Max 10 stacks of Fury. At max Fury, your next attack deals 100% Increased Damage to all enemies and consumes all Fury.\n"
        "- While above 40 Rage, gain 15% Less Damage Taken. Upon dealing a Critical Hit, gain +20% Crit Multi per stack of Fury.\n"
        "- Gain 1% Damage Reduction per 20 Rage. All damage prevented from Damage Reduction is gained as Shield. Whenever an enemy attacks you, deal 50 Fire Damage to them.\n"
        "- -1% Crit Chance per 50 Shield. Deal 1% Increased Damage per 25 Shield. Whenever your shield is broken, heal for 3% of your Max HP and deal Fire damage to all enemies equal to 5% of current HP.\n"
        "[bold]Stat Changes:[/bold] +15 HP. +8 Damage. -0.05 Speed. +15% Fire Resistance. +10% Physical Resistance.",
    "Juggernaut": "[lore]An unstoppable force, trampling those in your way. Your Rage fuels your march, turning you into an immovable bastion of domination.[/lore]"
        "- You have 1 Fortify per 10 Rage, up to 15. +1% Damage Reduction, +2% Crit Chance, +5% Crit Damage per Fortify.\n"
        "- 25% Increased Rage gained from taking damage. At max Fortify your next attack hits all enemies, applies [cc]Stun[/cc] and consumes 100 Rage.\n"
        "- Whenever you are critically hit, gain Bastion until the start of your next turn. Take 25% Less Damage from critical hits.\n"
        "- Bastion: +25% Ailment Avoidance, +30% Crit Resistance, 10% Less Damage taken.\n"
        "[bold]Stat Changes:[/bold] +40 HP. -2 Damage. -0.05 Speed. +50% Stun Avoidance. +10% Fire Resistance. +20 Armour.",
    "Annihilist": "[lore]Kill them all. Rain hell upon your foes. Destroy all in your way. Let your wounds become another reason to demolish them.[/lore]"
        "- Gain 1 Annihilation per 50 Rage generated in combat. Annihilation lasts for the rest of combat and has no maximum stack limit.\n"
        "- Annihilation: +10% Fire Damage, +10% Crit Damage, +3% Crit Chance. Upon killing an enemy, lose 1 Annihilation and heal for 5% of your Max HP.\n"
        "- Rage no longer heals you at the end of combat. Whenever you critically hit an enemy, gain 2% of the enemy's damage as your own for the rest of combat per stack of Annihilation you have.\n"
        "- Whenever an enemy critically hits you, they take 5% of their Max HP as Fire damage per Annihilation stack you have. Killing an enemy this way is treated as if you killed them with a critical hit.\n"
        "[bold]Stat Changes[/bold] +15 HP. +8 Damage. +0.05 Speed. +5% Crit Chance. +25% Crit Damage.",
    "Tyrant": "[lore]Struggle no more. Endure no longer. Dominate. Cleave asunder all who misjudge your might, for the battlefield is your kingdom.[/lore]"
        "- Whenever you are attacked, if the damage taken is less than your base damage, take 20% Less Damage from that attack.\n"
        "- Taking damage does not grant Rage. When you are attacked, gain Rage equal to 25% of the Damage prevented by Armour and Damage Prevention.\n"
        "- Non-critical attacks gain 2% of your Armour value as Bonus Damage. Convert 25% of your Evasion and Energy Shield into Armour.\n"
        " -Whilst above 50 Rage: 10% Less Armour, 25% Increased Damage. Whenever you attack an enemy, gain Rage equal to 10% of the Damage prevented by their Armour.\n"
        "- If your attack is fully absorbed by Energy Shield or dodged due to Evasion, lose 40% of your current Rage and Heal 1 HP per Rage lost.\n"
        "[bold]Stat Changes:[/bold] -25 HP. +6 Damage. +0.05 Speed. -50% Crit Multi. +50 Armour.",
    "Conqueror": "[lore]Outnumbered? Never. Let them come. Their pitiful attacks mean nothing; dodge or endure, they only strengthen your conquest.[/lore]"
        "- Gain 20% Less Rage from dealing and taking damage. At the start of your turn, deal Fire damage to a random enemy equal to your current rage.\n"
        "- At the start of combat, if you are fighting more than 1 enemy, for every enemy you are fighting, gain 10% Increased Damage, +0.05 Speed and 5% Less Damage Taken.\n"
        "- Gain 10% of Armour as Evasion. Gain 10% of Evasion as Armour. Whenever you reduce damage from an incoming hit due to Armour, gain 50% of the prevented damage as damage on your next attack.\n"
        "- Whenever you dodge an attack due to Evasion, heal and gain Rage equal to 10% of the evaded damage.\n"
        "- Whenever you kill an enemy, gain HP Regeneration equal to 1% of their Max HP for 3 turns.\n"
        "[bold]Stat Changes:[/bold] +20 HP. +3 Damage. -0.1 Speed. +20% Healing Magnitude. +10% Enemy Quantity. +20 Armour. +20 Evasion."
}

class Warrior(Player):
    def __init__(self, name, health = 50, damage = 4, damageType = "fire", speed = 0.85):
        super().__init__(name, health, damage, 0.05, 2.0, damageType, speed, className="Warrior", classDescription=WARRIOR_DESCRIPTIONS['Warrior'])
        self._rage = 0 # build rage during combat, 1 rage = +3 damage
        self._baseMaxRage = 50
        self.rageEffect = 1.0

        self._fury = 0
        self._maxFury = 10
        self._fortify = 0
        self._maxFortify = 15
        self.bastion = False
        self.annihilationRage = 0
        self.annihilation = 0
        self.annihilationBuffs = {
            'fire': 0, 'critMulti': 0, 'critChance': 0
        }
        self.annihilistDamage = 0
        self.rageGeneration = 0
        self.conquerorEnemies = 0
        self.conquerorDamageGain = 0
        self.conquerorRegenBuffs = {3: 0, 2: 0, 1: 0} # keys = number of turns left
        self._warlordShieldWasUp = False

    def __str__(self):
        baseStr = super().__str__()
        
        if self._ascendancy == "Warlord":
            baseStr += f"\n[gold1]Fury:[/gold1] {self._fury} / {self._maxFury}"
        elif self._ascendancy == "Juggernaut":
            baseStr += f"\n[buff]Fortify:[/buff] {self._fortify} / {self._maxFortify}"

        return baseStr

    @property
    def maxRage(self) -> int:
        return self._baseMaxRage + self._stats['Bonuses'].get('max_rage', 0)

    def serialise(self):
        temp = super().serialise()
        temp['maxRage'] = self._baseMaxRage
        temp['rageGeneration'] = self.rageGeneration
        temp['rageEffeect'] = self.rageEffect
        return temp

    def deserialise(self, data):
        super().deserialise(data)
        self._baseMaxRage = data.get('maxRage', 50)
        self.rageGeneration = data.get('rageGeneration', 0)
        self.rageEffect = data.get('rageEffect', 1.0)

    def juggernautForfityBuffs(self):
        if self._ascendancy != 'Juggernaut':
            return
        self._stats['Temporary']['crit_chance'] -= 0.02 * self._fortify
        self._stats['Temporary']['crit_multi'] -= 0.05 * self._fortify
        self._fortify = min(15, self._rage // 10)
        self._stats['Temporary']['crit_chance'] += 0.02 * self._fortify
        self._stats['Temporary']['crit_multi'] += 0.05 * self._fortify        

    def _recalculateStats(self, doPrint = True, inCombat = False):
        super()._recalculateStats(doPrint, inCombat)

        if self._ascendancy == 'Warlord' and self._rage > 40:
            self._stats['Bonuses']['less_damage_taken'] += 15

        if self._ascendancy == 'Tyrant':
            evConverted = int(0.25 * self.evasion)
            esConverted = int(0.25 * self.energyShield)
            self._stats['armour'] += evConverted + esConverted
            self._stats['evasion'] -= evConverted
            self._stats['energy_shield'] -= esConverted

            if inCombat and self._rage > 50:
                self._stats['armour'] = int(self.armour * 0.9)

            if doPrint:
                console.print(f"[asc_tyrant]Tyrant:[/asc_tyrant] Converted {evConverted} Evasion and {esConverted} Energy Shield into Armour")

        elif self._ascendancy == 'Conqueror':
            evGainedAsArmour = int(0.1 * self.evasion)
            armourGainedAsEv = int(0.1 * self.armour)
            self._stats['armour'] += evGainedAsArmour
            self._stats['evasion'] += armourGainedAsEv

            if doPrint:
                console.print(f"[asc_conqueror]Conqueror:[/asc_conqueror] Gained 10% of Evasion (+ {evGainedAsArmour}) as Armour. Gained 10% of Armour (+ {armourGainedAsEv}) as Evasion.")

    def rollCritical(self, target, damageDealt=None):
        critChance = self.critChance
        critMulti = self.critMulti

        if self._ascendancy == 'Annihilist':
            critChance += self.annihilationBuffs['critChance']
            critMulti += self.annihilationBuffs['critMulti']

        elif self._ascendancy == 'Warlord':
            critChance = max(0, critChance - 0.01 * (self._shield // 50))

        if random.random() < critChance:
            return True, critMulti
        return False, 1.0

    def onCrit(self, targets, combatManager, critDamage):
        if self._ascendancy == 'Annihilist':
            damageGain = 0
            for t in targets:
                damageGain += int(t._damage * 0.02 * self.annihilation)
            self.annihilistDamage += damageGain

        return critDamage

    def onCriticallyHit(self, attacker, combatManager, critDamage, damageType):
        critDamage = super().onCriticallyHit(attacker, combatManager, critDamage, damageType)
        if self._ascendancy == 'Juggernaut':
            console.print(f"[asc_juggernaut]Juggernaut: {self._name} takes 25% Less Damage from the Critical Hit![/asc_juggernaut]")
            critDamage = int(critDamage * 0.75)
            self.gainBastion()
        elif self._ascendancy == 'Annihilist':
            damage = int(0.05 * attacker._maxHealth * self.annihilation)
            attacker.damage(damage, 'fire')
            if attacker._isDead:
                self.onCrit([attacker], combatManager, critDamage)
                self.onKill(attacker, {}, combatManager)

        return critDamage

    def gainBastion(self):
        if not self.bastion and self._ascendancy == 'Juggernaut':
            self._stats['Temporary']['ailment_avoidance'] += 25
            self._stats['Temporary']['crit_resistance'] += 30
            self._stats['Temporary']['less_damage_taken'] += 10
            self.bastion = True

    def onBeforeDamage(self, ability, damage, damageType, targets, combatManager):
        if self._ascendancy == 'Warlord':
            if self._fury == self._maxFury:
                damage *= 2
                targets = combatManager.allAlive
                self._stats['Temporary']['lifesteal'] -= 2 * self._fury
                self._fury = 0
                console.print('[gold1]Warlord: Max Fury! 200% More Damage to all enemies! Fury reset to 0.[/gold1]')
        elif self._ascendancy == 'Juggernaut' and self._fortify >= self._maxFortify and self._rage >= 100:
            targets = combatManager.allAlive
            self._queueEffect(Effects.createStun())
            console.print('[gold1]Juggernaut: Max Fortify - Stunning all enemies! -100 Rage.[/gold1]')
            self._rage -= 100

        return damage, damageType, targets

    def onPrepareHit(self, target, targetUnit, finalDamage, damageType, combatManager):
        finalDamage = super().onPrepareHit(target, targetUnit, finalDamage, damageType, combatManager)
        if self._ascendancy == 'Tyrant':
            armourBonus = int(0.02 * self.armour)
            finalDamage += armourBonus
            self._logDamage("2% of Armour (Tyrant)", flat=armourBonus)
        return finalDamage

    def onBeforeHit(self, finalDamage, damageType, attacker, combatManager):
        finalDamage = super().onBeforeHit(finalDamage, damageType, attacker, combatManager)
        if self._ascendancy == 'Warlord':
            self._warlordShieldWasUp = self._shield > 0
            console.print(f"[asc_warlord]Warlord: {attacker._name} takes 50 Fire Damage from attacking you![/asc_warlord]")
            attacker.damage(50, 'fire')
        return finalDamage

    def onDamaged(self, attacker, damageReductionValue, armourDamagePrevented, combatManager):
        if self._ascendancy == 'Tyrant':
            rageGain = int((armourDamagePrevented + damageReductionValue) * 0.25)
            self._rage = min(self.maxRage, self._rage + rageGain)

        if self._ascendancy == 'Warlord':
            if self._warlordShieldWasUp and self._shield <= 0: # shield was broken on hit
                heal = int(0.03 * self._maxHealth)
                self.heal(heal, False)
                aoeDamage = int(0.05 * self._health)
                for e in combatManager.allAlive:
                    e.damage(aoeDamage, 'fire')
                console.print(f"[asc_warlord]Warlord: Shield broken! Healed for 3% Max HP ({heal}) and dealt 5% of your Current Health ({aoeDamage}) as damage to all enemies")

    def onAttack(self, damageDealt, damageType, target, combatManager, ability, crit):
        damageDealt, damageType = super().onAttack(damageDealt, damageType, target, combatManager, ability, crit)
        rageGain = damageDealt // (6 * (1 + self._level // 10)) + self._stats['Bonuses'].get('rage_gain_on_attack', 0)

        if self._ascendancy == 'Warlord':
            rageGain = int(rageGain * 1.2)

        elif self._ascendancy == 'Conqueror':
            rageGain = int(rageGain * 0.8)

        if damageType == 'fire' and damageDealt > 0:
            rageGain = int(rageGain * 1.1)

        self._rage = min(self.maxRage, self._rage + rageGain)
        self.annihilationRage += rageGain
        if rageGain > 0:
            console.print(f"\n[class_warrior]Your Rage grows! +{rageGain} Rage. Current Rage: {self._rage} / {self.maxRage}[/class_warrior]")

        if self._ascendancy == 'Annihilist':
            while self.annihilationRage >= 50:
                self.annihilationRage -= 50
                self.annihilation += 1

            if damageType == 'fire' and self.annihilationBuffs['fire']:
                self._logDamage(f"Annihilation ({self.annihilation} stacks)", percent=self.annihilationBuffs['fire'])
                damageDealt = round(damageDealt * (1 + self.annihilationBuffs['fire']))

            if self.annihilistDamage > 0:
                self._logDamage("Bonus Damage from Crits (Annihilist)", flat=self.annihilistDamage)
            damageDealt += self.annihilistDamage

        elif self._ascendancy == 'Warlord' and self._rage >= 50 and self._fury < self._maxFury:
            self._fury += 1
            self._stats['Temporary']['lifesteal'] += 2
            console.print(f"\n[bold damage]Your fury increases! Current Fury: {self._fury} / {self._maxFury}[/bold damage]")

        elif self._ascendancy == 'Conqueror':
            if self.conquerorDamageGain:
                self._logDamage("Stored Damage from Armour Mitigation (Conqueror)", flat=self.conquerorDamageGain)
            damageDealt += self.conquerorDamageGain
            self.conquerorDamageGain = 0
            if self.conquerorEnemies > 0:
                self._logDamage(f"Conqueror ({self.conquerorEnemies} Enemies)", percent=0.1 * self.conquerorEnemies)
                damageDealt = int(damageDealt * (1 + (0.1 * self.conquerorEnemies)))

        if self._rage > 0:
            self._logDamage("Rage", flat=self._rage * int(2 * self.rageEffect))
        damageDealt = damageDealt + ((self._rage * int(2 * self.rageEffect)))

        if self._ascendancy == 'Warlord':
            if self._fury > 0:
                self._logDamage("Fury", percent=0.05 * self._fury)
            damageDealt = int(damageDealt * (1 + (0.05 * self._fury)))
            if self._shield >= 25:
                self._logDamage("Shield", percent=0.01 * (self._shield // 25))
            damageDealt = int(damageDealt * (1 + (0.01 * (self._shield // 25))))

        elif self._ascendancy == 'Tyrant':
            if self._rage > 50:
                self._logDamage("Rage above 50 (Tyrant)", percent=0.25)
                damageDealt = int(damageDealt * 1.25)

        return damageDealt, damageType

    def onHit(self, damageTaken, damageType, isCrit, attacker, combatManager):
        damageTaken, damageType = super().onHit(damageTaken, damageType, isCrit, attacker, combatManager)
        rageGain = max(0, damageTaken // (10 * (1 + self._level // 12))) + self._stats['Bonuses'].get('rage_gain_on_hit', 0)
        if damageType == 'fire':
            rageGain = int(rageGain * 1.2)

        if self._ascendancy == 'Juggernaut':
            rageGain = int(rageGain * 1.25)
            damageTaken = int(damageTaken * (1 - (0.01 * self._fortify)))

        elif self._ascendancy == 'Tyrant':
            if damageTaken < self._baseDamage:
                attacker._logDamage(f"{self._name}'s Tyrant (Damage below Base Damage)", percent=-0.2)
                damageTaken = int(damageTaken * 0.8)
            rageGain = 0 # no rage change from taking damage

        elif self._ascendancy == 'Conqueror':
            rageGain = int(rageGain * 0.8)

        self._rage = min(self.maxRage, self._rage + rageGain)
        if rageGain > 0:
            console.print(f"\n[class_warrior]Your Rage grows! +{rageGain} Rage. Current Rage: {self._rage} / {self.maxRage}[/class_warrior]")

        return damageTaken, damageType

    def onCombatStart(self, combatManager, combatUnit):
        super().onCombatStart(combatManager, combatUnit)
        if self._ascendancy == 'Conqueror':
            self.conquerorEnemies = len(combatManager.allAlive) - 1
            self._stats['Temporary']['speed'] += 0.05 * self.conquerorEnemies
            self._stats['Temporary']['less_damage_taken'] += 5 * self.conquerorEnemies

    def onKill(self, entity, data, combatManager):
        super().onKill()
        if self._ascendancy == 'Annihilist':
            if self.annihilation > 0:
                self.annihilation -= 1
                heal = int(self._maxHealth * 0.05)
                console.print("  [heal]- Annihilist: Consumed 1 Annihilation stack to Heal 5% Max HP![/heal]")
                self.heal(heal, reason="Annihilist (Consumed 1 Annihilation stack)")
        elif self._ascendancy == 'Conqueror' and entity:
            regen = int(entity._maxHealth * 0.01)
            self.conquerorRegenBuffs[3] += regen
        return None

    def onCombatEnd(self):
        healAmount = self._rage // 2
        if self._ascendancy != 'Annihilist':
            self.heal(healAmount, reason="Leftover Rage")
        self._rage = 0
        self._fury = 0
        self._fortify = 0
        self.bastion = False
        self.annihilationBuffs = {
            'fire': 0, 'critMulti': 0, 'critChance': 0
        }
        self.annihilation = 0
        self.annihilistDamage = 0
        self.conquerorEnemies = 0
        self.conquerorDamageGain = 0
        self.conquerorRegenBuffs = {3: 0, 2: 0, 1: 0}
        super().onCombatEnd()

    def onTurnStart(self, combatManager):
        if self.rageGeneration > 0:
            self._rage = min(self.maxRage, self._rage + self.rageGeneration)
            console.print(f"[dark_red] +{self.rageGeneration} Rage gained from Rage Generation![/dark_red]")

        if self._ascendancy == 'Juggernaut':
            self.juggernautForfityBuffs()

            if self.bastion:
                self._stats['Temporary']['ailment_avoidance'] -= 25
                self._stats['Temporary']['crit_resistance'] -= 30
                self._stats['Temporary']['less_damage_taken'] -= 10
                self.bastion = False

        elif self._ascendancy == 'Annihilist':
            self._stats['Temporary']['crit_multi'] -= self.annihilationBuffs['critMulti']
            self._stats['Temporary']['crit_chance'] -= self.annihilationBuffs['critChance']
            self.annihilationBuffs = {
                'fire': 0.1 * self.annihilation,
                'critMulti': 0.1 * self.annihilation,
                'critChance': 0.03 * self.annihilation
            }
            self._stats['Temporary']['crit_multi'] += self.annihilationBuffs['critMulti']
            self._stats['Temporary']['crit_chance'] += self.annihilationBuffs['critChance']

        elif self._ascendancy == 'Conqueror':
            totalHeal = sum(self.conquerorRegenBuffs.values())
            self.conquerorRegenBuffs[1] = self.conquerorRegenBuffs[2]
            self.conquerorRegenBuffs[2] = self.conquerorRegenBuffs[3]
            self.conquerorRegenBuffs[3] = 0
            self.heal(totalHeal, reason="Conqueror HP Regeneration")

        super().onTurnStart(combatManager)

    def _levelUp(self):
        super()._levelUp()
        self._baseMaxRage += 1
        self.rageEffect += 0.05

    ASCENDANCY_DELTAS = {
        'Warlord': {
            '_baseHealth': 15,
            '_baseDamage': 8,
            '_baseSpeed': -0.05,
            '_stats.Permanent.fire': 15,
            '_stats.Permanent.physical': 10,
        },
        'Juggernaut': {
            '_baseHealth': 40,
            '_baseDamage': -2,
            '_baseSpeed': -0.05,
            '_stats.Permanent.stun_avoidance': 50,
            '_stats.Permanent.fire': 10,
            '_stats.Permanent.added_armour': 20,
        },
        'Annihilist': {
            '_baseHealth': +15,
            '_baseDamage': 8,
            '_baseSpeed': +0.05,
            '_stats.Permanent.crit_chance': 0.05,
            '_stats.Permanent.crit_multi': 0.25,
        },
        'Tyrant': {
            '_baseHealth': -25,
            '_baseDamage': 6,
            '_baseSpeed': 0.05,
            '_stats.Permanent.crit_multi': -0.5,
            '_stats.Permanent.added_armour': 50,
        },
        'Conqueror': {
            '_baseHealth': 20,
            '_baseDamage': 3,
            '_baseSpeed': -0.1,
            '_stats.Permanent.healing_magnitude': 20,
            '_stats.Permanent.enemy_quantity': 10,
            '_stats.Permanent.added_armour': 20,
            '_stats.Permanent.added_evasion': 20,
        },
    }

    def _removeOldAscendancy(self):
        delta = self.ASCENDANCY_DELTAS.get(self._ascendancy)
        if delta:
            self._applyStatDelta(delta, sign=-1)
        return True

    def updateAscendancy(self, ascendancy):
        if not super().updateAscendancy(ascendancy):
            return
        self._ascendancy = ascendancy
        self.ascendancyDescription = WARRIOR_DESCRIPTIONS[ascendancy]
        self._applyStatDelta(self.ASCENDANCY_DELTAS[ascendancy], sign=1)
        self._recalculateStats()
        self.gainClassAbilities(True)
        return True

...