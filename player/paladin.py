from .base import Player
from scripts.styles import console, pause
import random
from typing import Dict, Any

PALADIN_DESCRIPTIONS = {
    "Paladin": "A holy warrior blessed with divine favour.\n"
        "Favour: Gain 5-10 Favour per turn. Max 100 Favour. Gain +1 Max Favour on level up. At the start of your turn, you can decide whether Favour will be randomly spent this turn or not.\n"
        "Possible attack buffs per Favour spent: +2 Damage, +2% Increased Damage, +1% Crit Chance, +3% Crit Damage.\n"
        "Possible defense buffs per Favour spent: -2 Damage Taken, +0.1% Damage Reduction, 1% Max HP gained as Shield.\n"
        "+5% Increased Effect of Favour buffs per level. Heal for 20% of remaining Favour at the end of battle.\n"
        "Starting Stats: 55 Health | 4 Damage | 5% Crit Chance | 175% Crit Damage | Holy Damage | 1.05 Speed.",
    #ascendancies
    "Zealot": "-25 Max Favour. Attack buffs from Favour have 50% Increased Effect. Defense buffs from Favour have 20% Less Effect.\n"
        "Whilst at or above 50 favour, gain 20% Increased Damage, +5% Crit Chance and +10% Lifesteal.\n"
        "Upon spending Favour on attack buffs, gain 1 stack of Zealotry per 15 Favour spent. Zealotry has no max stack limit.\n"
        "Zealotry: +2% Increased Holy Damage, +1 Damage, +0.3% Damage Taken. At the end of combat, heal HP equal to Zealotry stacks.\n"
        "+10 HP. +2 Damage. -0.15 Speed. +15% Holy Resistance. -10% Psychic Resistance",
    "Guardian": "Attack buffs from Favour have 25% Less Effect. Defense buffs from Favour have 75% Increased Effect and 20% Increased Cost.\n"
        "+3 Favour Generated. At the start of your turn, gain Shield equal to 5% of your current Favour.\n"
        "Whilst at or above 60 Favour, gain 10% Increased Damage, 10% Damage Reduction, 50% Ailment Avoidance, and +10 HP Regeneration.\n"
        "Upon taking damage, spend up to 20 Favour and gain +0.5% Damage Reduction per Favour Spent. Whenever you spend at least 16 Favour this way, gain 1 Bulwark.\n"
        "Bulwark: +2% Damage Reduction, -0.05 Speed, +5% Increased Holy Damage. Bulwark has a maximum of 5 stacks.\n"
        "+20 HP. -2 Damage. -0.1 Speed. +20% Stun Avoidance. +100 Armour. +30 Energy Shield.",
    "Justicar": "Gain 1 Favour per 10 damage taken. Gain 2 Favour per 10 damage taken if the damage type was Otherworldly.\n"
        "Favour buffs have 20% Increased Effect and 10% Increased Cost. While you are at or above 70 Favour, your next attack deals 80% Increased Damage and consumes 40 Favour.\n"
        "Upon taking damage, gain Shield equal to a percentage of damage taken. The percentage is equal to your current favour percentage, to a maximum of 30%.\n"
        "Upon killing an enemy, gain Justice for 3 turns: +25% Increased Holy Damage, +5% Damage Reduction, +10% Crit Chance, +0.2 Speed.\n"
        "Upon dealing a critical hit, gain 5 Favour per living enemy in combat.\n"
        "-20 HP. +1 Damage. +0.1 Speed. +50% Crit Damage. +5% Dark Resistance. +5% Holy Resistance",
    "Crusader": "Favour generation is doubled while below 50% Max HP. For every 15 Favour spent throughout combat, heal 1 HP at the start of your turn.\n"
        "Attacks have +1% Increased Damage per 10 Favour spent on that attack. Defensive buffs have 5% Increased Effect per 10 Favour spent on them.\n"
        "While above 75% Max HP, gain 15% Increased Holy Damage, +5% Crit Chance and +0.2 Speed.\n"
        "Upon dealing damage greater than 10% of your Max HP, or upon killing an enemy, gain 1 stack of Valour. Valour has 10 Max Stacks.\n"
        "Valour: 10% Increased Holy Damage, +0.05 Speed, +1% Damage Taken, +2% Lifesteal.\n"
        "At the end of combat, gain +1 Permanent Max Favour Generation per 6 stacks of Valour.\n"
        "-15 HP. +2 Damage. +0.05 Speed. +25% Crit Damage. +5% Divine Resistance.",
    "Inquisitor": "50% Increased Favour generation. +50 Max Favour. Holy Damage has 5% Lifesteal.\n"
        "If you have 80+ Favour when attacking, consume 50% of your current Favour to deal 75% Increased Damage.\n"
        "If you have 60+ Favour when being attacked, consume 40% of your current Favour to gain Blessing for 2 turns.\n"
        "Blessing: +5 Favour Generation, +20 HP Regeneration, 10% Increased Holy Damage, 5% Damage Reduction.\n"
        "All Favour buffs have 30% Increased Effect, but have a minimum cost of 20 Favour.\n"
        "+10 HP. +2 Damage. -0.2 Speed. +15% Holy Resistance. +5 HP Regeneration. +100 Armour.",
}

OTHERWORLDLY = ['psychic', 'chaos', 'ethereal']

class Paladin(Player): #higher health, lower damage, holy damage
    def __init__(self, name, health = 55, damage = 4, damageType = "holy", speed = 1.05):
        super().__init__(name, health, damage, 0.05, 1.75, damageType, speed, className="Paladin", classDescription=PALADIN_DESCRIPTIONS['Paladin'])
        self.favour = 0
        self.maxFavour = 100
        self.favourMinGain = 5
        self.favourMaxGain = 10
        self.favourSpendingEnabled = False
        self.favourEffect = 1.0
        self.favourSpent = 0
        self.favourBuffs = {
            'critChance': 0, 'critMulti': 0
        } # needed since not immediately applied, reset at turn start
        self.zealotry = 0
        self.zealotActiveLastTurn = False
        self.bulwark = 0
        self.guardianActiveLastTurn = False
        self.justiceTurns = 0
        self.valour = 0
        self.crusaderActiveLastTurn = False
        self.blessingTurns = 0

    @property
    def zealotActive(self):
        if self._ascendancy == 'Zealot':
            if self.favour >= 50:
                if not self.zealotActiveLastTurn:
                    self._stats['Temporary']['lifesteal'] += 10
                self.zealotActiveLastTurn = True
                return True
            if self.zealotActiveLastTurn:
                self._stats['Temporary']['lifesteal'] -= 10
            self.zealotActiveLastTurn = False
        return False

    @property
    def guardianActive(self):
        if self._ascendancy == 'Guardian':
            if self.favour >= 60:
                if not self.guardianActiveLastTurn:
                    self._stats['Temporary']['hpRegen'] += 10
                    self._stats['Temporary']['ailmentAvoidance'] += 50
                self.guardianActiveLastTurn = True
                return True
            if self.guardianActiveLastTurn:
                self._stats['Temporary']['hpRegen'] -= 10
                self._stats['Temporary']['ailmentAvoidance'] -= 50
            self.guardianActiveLastTurn = False
        return False

    @property
    def crusaderActive(self):
        if self._ascendancy == 'Crusader':
            if self._health > self._maxHealth * 0.75:
                if not self.crusaderActiveLastTurn:
                    self._stats['Temporary']['critChance'] += 0.05
                    self._stats['Temporary']['speed'] += 0.2
                self.crusaderActiveLastTurn = True
                return True
            if self.crusaderActiveLastTurn:
                self._stats['Temporary']['critChance'] -= 0.05
                self._stats['Temporary']['speed'] -= 0.2
            self.crusaderActiveLastTurn = False
        return False

    def _serialise(self):
        temp = super()._serialise()
        temp['maxFavour'] = self.maxFavour
        temp['favourMinGain'] = self.favourMinGain
        temp['favourMaxGain'] = self.favourMaxGain
        return temp

    def deserialise(self, data):
        super().deserialise(data)
        self.maxFavour = data.get('maxFavour', 100 + self._level)
        self.favourMinGain = data.get('minFavourGain', 5)
        self.favourMaxGain = data.get('maxFavourGain', 10)

    def _levelUp(self):
        super()._levelUp()
        self.maxFavour += 1
        self.favourEffect += 0.05

    def _spendFavourOffensive(self, amount: int) -> Dict[str, int]:
        if self.favour < amount or not self.favourSpendingEnabled or amount == 0:
            return {}
        if self._ascendancy == 'Inquisitor':
            if self.favour >= 20:
                amount = max(20, amount)
            else:
                return {}
        
        self.favour -= amount
        self.favourSpent += amount
        
        buffType = random.choice(['damage', 'increased_damage', 'critChance', 'critMulti'])
        val = 0
        if buffType == 'damage':
            val = 2
        elif buffType == 'increased_damage':
            val = 2
        elif buffType == 'critChance':
            val = 1
        elif buffType == 'critMulti':
            val = 3
            
        favourEffect = self.favourEffect
        if self._ascendancy == 'Zealot':
            favourEffect += 0.5
        elif self._ascendancy == 'Guardian':
            favourEffect -= 0.25
        elif self._ascendancy == 'Justicar':
            favourEffect += 0.2
        elif self._ascendancy == 'Inquisitor':
            favourEffect += 0.3

        val = int(val * amount * favourEffect)
        buff =  buffType.replace('crit', 'Crit ') if buffType.startswith('crit') else buffType.replace('_', ' ')
        buff = buff.title()
        ex = "" if buffType == 'damage' else "%"
        console.print(f"  [gold1]Spent {amount} Favour on offensive buff: +{val}{ex} {buff}.[/gold1]")
        pause()
        return {buffType: val}

    def _spendFavourDefensive(self, amount: int) -> Dict[str, int]:
        if self.favour < amount or not self.favourSpendingEnabled or amount == 0:
            return {}
        if self._ascendancy == 'Inquisitor':
            if self.favour >= 20:
                amount = max(20, amount)
            else:
                return {}
        
        self.favour -= amount
        self.favourSpent += amount

        buffType = random.choice(['damage_reduction', 'percent_damage_reduction', 'shield'])
        val = 0
        ex = ""
        if buffType == 'damage_reduction':
            val = 2
        elif buffType == 'percent_damage_reduction':
            val = 0.001
            ex = "%"
        elif buffType == 'shield':
            val = 0.01
            ex = "% of Max HP gained as"

        favourEffect = self.favourEffect
        if self._ascendancy == 'Zealot':
            favourEffect -= 0.2
        elif self._ascendancy == 'Guardian':
            favourEffect += 0.75
        elif self._ascendancy == 'Justicar':
            favourEffect += 0.2
        elif self._ascendancy == 'Crusader':
            favourEffect += amount / 10 * 0.05
        elif self._ascendancy == 'Inquisitor':
            favourEffect += 0.3

        val = int(val * amount * favourEffect)
        buff = buffType.replace('_', ' ').title()
        console.print(f"  [gold1]Spent {amount} Favour on defensive buff: +{val}{ex} {buff}.[/gold1]")
        return {buffType: val}

    def onAttack(self, damageDealt, damageType, target=None, combatManager=None):
        super().onAttack(damageDealt, damageType, target, combatManager)

        spent = 0
        if self.favourSpendingEnabled and self.favour > 0:
            spent = random.randint(1, self.favour)

            if self._ascendancy == 'Zealot':
                zGain = spent // 15
                if zGain > 0:
                    self.zealotry += zGain
                    console.print(f"[gold1]Zealot: Gained {zGain} Zealotry![/gold1]")

            elif self._ascendancy == 'Justicar':
                spent = int(spent * 1.1)

            buffs = self._spendFavourOffensive(spent)
            if buffs:
                buff, val = list(buffs.items())[0]
                if buff == 'damage':
                    damageDealt += val
                elif buff == 'increased_damage':
                    damageDealt = int(damageDealt * (1 + (val / 100)))
                else: # crit chance/multi
                    self.favourBuffs[buff] += val / 100

        if self._ascendancy == 'Zealot':
            if self.zealotry > 0:
                damageDealt += self.zealotry
                if damageType == 'holy':
                    damageDealt = int(damageDealt * (1 + (self.zealotry / 50)))
            if self.zealotActive:
                damageDealt = int(damageDealt * 1.2)
        
        elif self._ascendancy == 'Guardian':
            if self.guardianActive:
                damageDealt = int(damageDealt * 1.1)
            if self.bulwark > 0:
                damageDealt = int(damageDealt * (1 + (self.bulwark * 0.05)))

        elif self._ascendancy == 'Justicar':
            if self.justiceTurns > 0 and damageType == 'holy':
                damageDealt = int(damageDealt * 1.25)
            if self.favour >= 70:
                self.favour -= 40
                damageDealt = int(damageDealt * 1.8)
                console.print("  [holy]Justicar: Spent 40 Favour to gain +80% Increased Damage![/holy]")

        elif self._ascendancy == 'Crusader':
            bonus = 1 + (spent // 10 * 0.01)
            damageDealt = int(damageDealt * bonus)

            if self.valour > 0 and damageType == 'holy':
                damageDealt = int(damageDealt * (1 + (self.valour * 0.1)))

            if damageType == 'holy' and self.crusaderActive:
                damageDealt = int(damageDealt * 1.15)

            if damageDealt > self._maxHealth * 0.1 and self.valour < 10:
                self.valour += 1
                self._stats['Temporary']['speed'] += 0.05
                self._stats['Temporary']['lifesteal'] += 2

        elif self._ascendancy == 'Inquisitor':
            if self.favour >= 80:
                self.favour //= 2
                damageDealt = int(damageDealt * 1.75)
            if damageType == 'holy':
                if self.blessingTurns > 0:
                    damageDealt = int(damageDealt * 1.1)
                heal = int(damageDealt * 0.05)
                self.heal(heal)

        return damageDealt, damageType
    
    def onHit(self, damageTaken, damageType, attacker = None, combatManager=None):
        super().onHit(damageTaken, damageType, attacker, combatManager)
    
        if self.favourSpendingEnabled and self.favour > 0:
            spent = random.randint(1, self.favour)

            if self._ascendancy == 'Guardian':
                spent = int(spent * 1.2) # 20% increased cost, will auto-fail if not enough
            elif self._ascendancy == 'Justicar':
                spent = int(spent * 1.1)

            buffs = self._spendFavourDefensive(spent)
            if buffs:
                buff, val = list(buffs.items())[0]
                if buff == 'shield':
                    gain = int(self._maxHealth * val)
                    self._shield += gain
                elif buff == 'damage_reduction':
                    damageTaken = max(0, damageTaken - val)
                elif buff == 'percent_damage_reduction':
                    damageTaken = int(damageTaken * (1 - val))

        if self._ascendancy == 'Zealot' and self.zealotry > 0:
            bonus = 1 + (self.zealotry * 0.003)
            damageTaken = int(damageTaken * bonus)

        elif self._ascendancy == 'Guardian' and self.favour > 0:
            if self.guardianActive:
                damageTaken = int(damageTaken * 0.9)
            if self.bulwark > 0:
                damageTaken = int(damageTaken * (1 - (self.bulwark * 0.02)))
            spent = min(20, self.favour)
            dr = spent * 0.005
            console.print(f"  [holy]Guardian: Spent {spent} Favour to gain an additional +{(dr*100)}% Damage Reduction.[/holy]")
            damageTaken = int(damageTaken * (1 - dr))
            if spent >= 16 and self.bulwark < 5:
                self.bulwark += 1
                self._stats['Temporary']['speed'] -= 0.05

        elif self._ascendancy == 'Justicar':
            if self.justiceTurns > 0:
                damageTaken = int(damageTaken * 0.95)

            fGain = damageTaken // 10 * (2 if damageType in OTHERWORLDLY else 1)
            self.favour = min(self.maxFavour, self.favour + fGain)

            sGainPercent = min(0.3, round(self.favour / self.maxFavour, 2))
            sGain = int(damageTaken * sGainPercent)
            self._shield += sGain

        elif self._ascendancy == 'Crusader' and self.valour > 0:
            damageTaken = int(damageTaken * (1 + (self.valour * 0.01)))

        elif self._ascendancy == 'Inquisitor':
            if self.favour >= 60:
                self.favour = int(self.favour * 0.6)
                self.blessingTurns = 2
            if self.blessingTurns > 0:
                damageTaken = int(damageTaken * 0.95)

    def onKill(self, entity, attackData, combatManager=None):
        if self._ascendancy == 'Justicar':
            if self.justiceTurns == 0:
                self._stats['Temporary']['critChance'] += 0.1
                self._stats['Temporary']['speed'] += 0.2
            self.justiceTurns = 3

        elif self._ascendancy == 'Crusader' and self.valour < 10:
            self.valour += 1
            self._stats['Temporary']['speed'] += 0.05
            self._stats['Temporary']['lifesteal'] += 2

        return {}

    def rollCritical(self, target, damageDealt = None):
        target = target.entity
        critChance = self.critChance + self.favourBuffs['critChance']
        
        if self._ascendancy == 'Zealot' and self.favour >= 50:
            critChance += 0.05

        if random.random() < critChance:
            critMulti = min(1.0, self.critMulti + self.favourBuffs['critMulti'] * (1 - (target._stats['Bonuses']['critResistance'] / 100)))
            return True, critMulti
        return False, 1.0

    def onTurnStart(self, combatManager=None):
        for k in self.favourBuffs.keys():
            self.favourBuffs[k] = 0

        fgain = random.randint(self.favourMinGain, self.favourMaxGain)
        if self._ascendancy == 'Crusader':
            if self._health < self._maxHealth * 0.5:
                fgain = int(fgain * 1.5)
            heal = self.favourSpent // 15
            self.heal(heal)

        elif self._ascendancy == 'Inquisitor':
            if self.blessingTurns > 0:
                self.blessingTurns -= 1
                if self.blessingTurns == 0:
                    console.print("[warning]Inquisitor: Blessing has worn off![/warning]")
                else:
                    self.heal(20)
            fgain = int(fgain * 1.5)
            if self.blessingTurns > 0:
                fgain += 5

        self.favour = min(self.favour + fgain, self.maxFavour)
        console.print(f"[gold1]+{fgain} Favour. Current Favour: {self.favour} / {self.maxFavour}")

        if self._ascendancy == 'Guardian':
            sGain = self.favour // 20
            if sGain > 0:
                self._shield += sGain
                console.print(f"  [holy]Guardian: Gained {sGain} Shield from 5% of Favour![/holy]")

        elif self._ascendancy == 'Justicar' and self.justiceTurns > 0:
            self.justiceTurns -= 1
            if self.justiceTurns == 0:
                self._stats['Temporary']['critChance'] -= 0.1
                self._stats['Temporary']['speed'] -= 0.2

        console.print("[gold1]Paladin: Enable spending Favour this turn? (y/n):")
        choice = console.input("[cyan]> [/cyan]").strip().lower()
        self.favourSpendingEnabled = (choice == 'y')
        super().onTurnStart(combatManager)

    def onBattleEnd(self):
        heal = self.favour // 5
        if heal > 0:
            self.heal(heal)
            console.print(f"[gold1]Paladin: Healed {heal} HP from remaining Favour[/gold1]")

        if self._ascendancy == 'Zealot':
            self.heal(self.zealotry)
            console.print(f"  [gold1]Zealot: Healed {self.zealotry} HP from Zealotry stacks.[/gold1]")

        elif self._ascendancy == 'Crusader' and self.valour >= 6:
            genGain = self.valour // 6
            self.favourMaxGain += genGain

        self.favour = 0
        self.favourSpent = 0
        self.zealotry = 0
        self.zealotActiveLastTurn = False
        self.bulwark = 0
        self.guardianActiveLastTurn = False
        self.justiceTurns = 0
        self.valour = 0
        self.crusaderActiveLastTurn = False
        self.blessingTurns = 0
        self.fanaticism = 0
        self.clericFirstTurn = True
        self.templarCrit = 0
        self.templarDR = 0

        super().onBattleEnd()

    def updateAscendancy(self, ascendancy):
        if ascendancy == 'Zealot':
            self._baseHealth += 10
            self._baseDamage += 2
            self._baseSpeed -= 0.15
            self._stats['Permanent']['holy'] += 15
            self._stats['Permanent']['psychic'] -= 10
            self.maxFavour -= 25
            self._ascendancy = 'Zealot'
            self.ascendancyDescription = PALADIN_DESCRIPTIONS["Zealot"]
        elif ascendancy == 'Guardian':
            self._baseHealth += 20
            self._baseDamage -= 2
            self._baseSpeed -= 0.1
            self._stats['Permanent']['stunAvoidance'] += 20
            self._stats['Permanent']['added_armour'] += 100
            self._stats['Permanent']['added_energy_shield'] += 30
            self.favourMinGain += 3
            self.favourMaxGain += 3
            self._ascendancy = 'Guardian'
            self.ascendancyDescription = PALADIN_DESCRIPTIONS["Guardian"]
        elif ascendancy == 'Justicar':
            self._baseHealth -= 20
            self._baseDamage += 1
            self._baseSpeed += 0.1
            self._stats['baseCritMulti'] += 0.5
            self._stats['Permanent']['dark'] += 5
            self._stats['Permanent']['holy'] += 5
            self._ascendancy = 'Justicar'
            self.ascendancyDescription = PALADIN_DESCRIPTIONS["Justicar"]
        elif ascendancy == 'Crusader':
            self._baseHealth -= 15
            self._baseDamage += 2
            self._baseSpeed += 0.05
            self._stats['baseCritMulti'] += 0.25
            self._stats['Permanent']['divine'] += 5
            self._ascendancy = 'Crusader'
            self.ascendancyDescription = PALADIN_DESCRIPTIONS["Crusader"]
        elif ascendancy == 'Inquisitor':
            self._baseHealth += 10
            self._baseDamage += 2
            self._baseSpeed -= 0.2
            self._stats['Permanent']['holy'] += 15
            self._stats['Permanent']['hpRegen'] += 5
            self._stats['Permanent']['added_armour'] += 100
            self.maxFavour += 50
            self._ascendancy = 'Inquisitor'
            self.ascendancyDescription = PALADIN_DESCRIPTIONS["Inquisitor"]
