from .base import Player, ELEMENTAL_RES, DIVINE_RES
from scripts.styles import console
from scripts.abilities import Effects
import random

MAGE_DESCRIPTIONS = {
    "Mage": "[class_mage]A master of the arcane arts, using the mystic forces as your own.[/class_mage]\n"
        "- Mana: You have Mana instead of Stamina. Regenerate a base of 5 Mana per turn. Max Mana is affected by changes to Max Stamina.\n"
        "- Upon attacking with Elemental or Arcane Damage, spend Mana equal to 20% of Damage Dealt. Gain Added Damage equal to Mana spent on attacks.\n"
        "- Whenever you deal Arcane Damage, gain 1 Mastery, to a maximum of 10. Mastery: +1% Crit Chance, +5% Crit Damage.\n"
        "- Whenever you take Elemental Damage, gain Adaptation for that damage type for the rest of combat.\n"
        "- Fire Adaptation: +25% Crit Damage.\n"
        "- Cold Adaptation: +0.2 Speed.\n"
        "- Earth Adaptation: +10% Elemental Resistance.\n"
        "- Lightning Adaptation: +10% Crit Chance.\n"
        "- If you have all Adaptations, gain Archmage: 50% Increased Arcane Damage, 20% Increased Mana Cost.\n"
        "[bold]Starting Stats:[/bold] 40 HP | 7 Damage | 5% Crit Chance | 175% Crit Damage | Arcane Damage | 0.95 Speed.",
    #ascendancies
    "Calamity": "[lore]The fire soothes. The cold cannot bite. The earth shields you. The lightning is your steed. Control them all, then cast them down. You are above such simple tools.[/lore]"
        "- Deal 20% Increased Arcane Damage. Take 10% Increased Arcane and Elemental Damage. Take 10% Less Non-Arcane and Non-Elemental Damage.\n"
        "- Upon killing an enemy with Divine Damage, all living enemies take Arcane Damage equal to 50% of your Damage.\n"
        "- Whenever you critically hit an enemy, Relinquish 1 random Adaptation and gain a buff for the rest of combat. The Relinquished Adaptation cannot be regained this combat.\n"
        "- Relinquish Fire: 30% Increased Arcane Damage, -10% Crit Chance.\n"
        "- Relinquish Cold: 100% Increased Mana Regeneration, -0.3 Speed.\n"
        "- Relinquish Earth: 20% Increased Defenses, 25% Increased Elemental Damage Taken.\n"
        "- Relinquish Lightning: 50% Increased Effect of Mana, -25% Crit Damage.\n"
        "- If you have Relinquished all Adaptations, gain Calamity: 100% Increased Damage Dealt, 20% Less Damage Taken, +50% Crit Chance, +100% Crit Damage.\n"
        "[bold]Stat Changes:[/bold] -20 HP. +6 Damage. +0.15 Speed. +10 Mana Regeneration.",
    "Arcanist": "[lore]Each spell contains another secret. Each secret requires another spell. Learn. Accumulate. Improve. Let the Arcane flow through you, until all knowledge is yours.[/lore]"
        "- Mastery also grants +2 Mana Regeneration per stack. At the start of your turn, gain 2% Max Mana Regeneration for the rest of combat, to a maximum of +20%.\n"
        "- If an attack has a Mana Cost equal to or more than 40% of your Max Mana, it is used for free, and you gain 50% of the Mana that would have been used as Mana and Health.\n"
        "- Attacks deal 1% Increased Arcane Damage per 1% Mana you have, starting from 50%. (At 50% Max Mana, you have no Increased Damage. At 100% Max Mana, you have 50% Increased Damage.)\n"
        "- Convert 10% of your Max HP into Max Mana. Healing effects apply to Mana at 50% Effectiveness. Upon taking Elemental Damage, gain 10% of Damage Taken as Mana.\n"
        "- Archmage grants 50% Increased Mana Regeneration and an additional 20% Increased Mana Cost. If an attack uses more than 60% of your Current Mana, it deals 40% Increased Arcane Damage.\n"
        "[bold]Stat Changes:[/bold] +20 HP. -4 Damage. -0.1 Speed. 10% Increased Max Mana. 10% Increased Mana Cost.",
    "Hierophant": "[lore]Fire scorches. Cold chills. Earth protects. Lightning sunders. But now... The light blesses. The darkness consumes. The arcane transcends. They have always been there, but now, you are not of the ignorant.[/lore]"
        "- For each Elemental Adaptation you have, gain 15% Increased Arcane Damage. If you are attacked by an Elemental Damage Type you are already Adapted to, gain a random Elemental Adaptation.\n"
        "- Whenever you take Divine Damage, gain Adaptation for that damage type for the rest of combat.\n"
        "- Holy Adaptation: Healing is applied to Shield as well, 10% Increased Arcane Damage.\n"
        "- Dark Adaptation: +15% Lifesteal, 10% Increased Arcane Damage.\n"
        "- Arcane Adaptation: Attacks deal extra damage equal to 10% of your Max Mana, 10% Increased Arcane Damage.\n"
        "- If you have all Divine Adaptations, gain Prophetic: 50% Increased Mana Cost, +25% Resistance Penetration.\n"
        "- If you have Archmage and Prophetic: +25% Crit Chance, +100% Crit Damage, +25% Resistance Penetration.\n"
        "[bold]Stat Changes:[/bold] +20 HP. +4 Damage. -0.1 Speed. +5% Elemental Resistance. +5% Divine Resistance.",
    "Empyrean": "[lore]You cannot know everything. Some secrets have no truths. Yet still, the Above calls to you, and in turn, It answers to you. So grasp it, and embark upon the road of omnipotence.[/lore]"
        "- Mastery has no maximum stack size. Archmage grants 2% Increased Arcane Damage per Mastery you have.\n"
        "- Gain Mastery when attacked. Gain an additional Mastery if the Damage Type was Elemental. Gain 2 Mastery upon dealing a critical hit.\n"
        "- Gain Max Mana equal to 20% Max Energy Shield. Gain Mana Regeneration equal to 10% Current Energy Shield.\n"
        "- Whenever your Energy Shield is broken, your next attack gains +25% Crit Chance, +10% Lifesteal and +25% Resistance Penetration.\n"
        "- Regenerate Energy Shield equal to 10% of Mana Spent on attacks. Double this Regeneration if you have Archmage.\n"
        "- Each Adaptation grants +10 Mana Regeneration. Whenever Mana is regenerated above 80% due to Mana Regeneration, Regenerate Energy Shield equal to your Mana Regeneration.\n"
        "[bold]Stat Changes:[/bold] +25 HP. -4 Damage. -0.1 Speed. +5% Crit Chance. +50 Energy Shield. +5 Mana Regeneration.",
    "Unmaker": "[lore]The rest seek power. Knowledge. Recognition. Their facades bore you. This world holds only evils, and you are the single truth. There is no place, after all, for these hideous miscreations.[/lore]"
        "- Whenever you deal a critical hit, or whenever you are critically hit, gain 1 Precision. Precision has a maximum of 10 stacks.\n"
        "- Precision: +1% Crit Chance, +15% Crit Damage, +1% Execution Threshold. At 10 Precision, double your Crit Chance.\n"
        "- Mana cannot be spent on non-critical attacks. Attacks always consume a minimum of 50% of your Current Mana. Spending Mana heals you for 75% of Mana Spent.\n"
        "- For each Elemental Adaptation you have, gain +3% Crit Chance, +10% Crit Multi, 5% Reduced Defenses.\n"
        "- Archmage also grants +30% Crit Resistance, 10% Increased Defenses, and 5% Lifesteal.\n"
        "- Whenever you kill an enemy, if you do not have Max Mastery, gain 1 Mastery, otherwise heal for 5% of the Damage Dealt.\n"
        "[bold]Stat Changes:[/bold] -20 HP. +5 Damage. +0.1 Speed. +25% Crit Damage."
}

class Mage(Player): # higher damage, lower health, arcane damage
    def __init__(self, name, health = 40, damage = 7, damageType = "arcane", speed = 1):
        super().__init__(name, health, damage, 0.05, 1.75, damageType, speed, className="Mage", classDescription=MAGE_DESCRIPTIONS['Mage'])
        self._maxMana = self._maxHealth
        self._mana = self._maxMana
        self.manaRegen = 5
        self.manaCostMultiplier = 1.0
        self.manaRegenMultiplier = 1.0
        self.manaEffect = 1.0
        self.mastery = 0
        self.maxMastery = 10
        self.fireAdaptation = False
        self.coldAdaptation = False
        self.earthAdaptation = False
        self.lightningAdaptation = False
        self.elementalAdaptations = 0
        self.archmage = False

        self.relinquishedFire = False
        self.relinquishedCold = False
        self.relinquishedEarth = False
        self.relinquishedLightning = False
        self.calamity = False

        self.arcanistRegenGain = 0

        self.holyAdaptation = False
        self.darkAdaptation = False
        self.arcaneAdaptation = False
        self.divineAdaptations = 0
        self.prophetic = False
        self.hierophantSuperBuff = False
        self.empyreanManaRegen = 0
        self.empyreanEsBroken = False
        self.unmakerPrecision = 0
        self.unmakerCritChanceDoubled = False

    def _recalculateStats(self, doPrint=True, inCombat=False):
        super()._recalculateStats(doPrint, inCombat)
        self._maxMana += self._maxStamina - 100

        if self._ascendancy == 'Arcanist':
            hpToMana = int(self._maxHealth * 0.1)
            self._maxMana += hpToMana
            self._maxHealth -= hpToMana
            self._maxMana = int(self._maxMana * 1.1)

            if doPrint:
                console.print(f"[asc_arcanist]Converted 10% of Max HP into Mana, +{hpToMana} Mana. 10% Increased Mana. Total Mana: {self._maxMana}")

        elif self._ascendancy == 'Empyrean':
            esAsMana = int(self.maxEnergyShield * 0.2)
            self._maxMana += esAsMana

            if doPrint:
                console.print(f"[asc_empyrean]Gained 20% of Maximum Energy Shield as Mana, +{esAsMana} Mana.")

    def _serialise(self):
        temp = super().serialise()
        temp['maxMana'] = self._maxMana
        return temp

    def deserialise(self, data):
        super().deserialise(data)
        self._maxMana = data['maxMana']
        self._mana = data['maxMana']

    def gainMastery(self):
        if self.mastery < self.maxMastery or self._ascendancy == 'Empyrean':
            self.mastery += 1
            self._stats['Temporary']['crit_chance'] += 0.01
            self._stats['Temporary']['crit_multi'] += 0.05
            if self._ascendancy == 'Arcanist':
                self.manaRegen += 2

    def gainFireAdaptation(self):
        if not self.fireAdaptation and not (self._ascendancy == 'Calamity' and self.relinquishedFire):
            self._stats['Temporary']['crit_multi'] += 0.25
            self.fireAdaptation = True
            self.elementalAdaptations += 1
            if self._ascendancy == 'Unmaker':
                self._stats['Temporary']['crit_chance'] += 0.03
                self._stats['Temporary']['crit_multi'] += 0.1
                self._stats['Temporary']['increased_defenses'] -= 5
            return True
        return False

    def relinquishFire(self):
        if self.fireAdaptation:
            self._stats['Temporary']['crit_multi'] -= 0.25
            self._stats['Temporary']['crit_chance'] -= 0.1
            self.relinquishedFire = True
            self.fireAdaptation = False
            self.elementalAdaptations -= 1

    def gainColdAdaptation(self):
        if not self.coldAdaptation and not (self._ascendancy == 'Calamity' and self.relinquishedCold):
            self._stats['Temporary']['speed'] += 0.2
            self.coldAdaptation = True
            self.elementalAdaptations += 1
            if self._ascendancy == 'Unmaker':
                self._stats['Temporary']['crit_chance'] += 0.03
                self._stats['Temporary']['crit_multi'] += 0.1
                self._stats['Temporary']['increased_defenses'] -= 5
            return True
        return False

    def relinquishCold(self):
        if self.coldAdaptation:
            self._stats['Temporary']['speed'] -= 0.5
            self.manaRegenMultiplier += 1
            self.relinquishedCold = True
            self.coldAdaptation = False
            self.elementalAdaptations -= 1

    def gainEarthAdaptation(self):
        if not self.earthAdaptation and not (self._ascendancy == 'Calamity' and self.relinquishedEarth):
            self._stats['Temporary']['elemental'] += 10
            self.earthAdaptation = True
            self.elementalAdaptations += 1
            if self._ascendancy == 'Unmaker':
                self._stats['Temporary']['crit_chance'] += 0.03
                self._stats['Temporary']['crit_multi'] += 0.1
                self._stats['Temporary']['increased_defenses'] -= 5
            return True
        return False

    def relinquishEarth(self):
        if self.earthAdaptation:
            self._stats['Temporary']['elemental'] -= 10
            self._stats['Temporary']['increased_defenses'] += 20
            self.relinquishedEarth = True
            self.earthAdaptation = False
            self.elementalAdaptations -= 1

    def gainLightningAdaptation(self):
        if not self.lightningAdaptation and not (self._ascendancy == 'Calamity' and self.relinquishedLightning):
            self._stats['Temporary']['crit_chance'] += 0.1
            self.elementalAdaptations += 1
            if self._ascendancy == 'Unmaker':
                self._stats['Temporary']['crit_chance'] += 0.03
                self._stats['Temporary']['crit_multi'] += 0.1
                self._stats['Temporary']['increased_defenses'] -= 5
            return True
        return False

    def relinquishLightning(self):
        if self.lightningAdaptation:
            self._stats['Temporary']['crit_chance'] -= 0.1
            self._stats['Temporary']['crit_multi'] -= 0.25
            self.manaEffect += 0.5
            self.relinquishedLightning = True
            self.lightningAdaptation = False
            self.elementalAdaptations -= 1

    def gainHolyAdaptation(self):
        if not self.holyAdaptation:
            self.holyAdaptation = True
            self.divineAdaptations += 1

    def gainDarkAdaptation(self):
        if not self.darkAdaptation:
            self.darkAdaptation = True
            self._stats['Temporary']['lifesteal'] += 15
            self.divineAdaptations += 1

    def gainArcaneAdaptation(self):
        if not self.arcaneAdaptation:
            self.arcaneAdaptation = True
            self.divineAdaptations += 1

    def checkArchmage(self):
        if not self.archmage:
            if self.fireAdaptation and self.coldAdaptation and self.earthAdaptation and self.lightningAdaptation:
                self.archmage = True
                self.manaCostMultiplier += 0.2
                if self._ascendancy == 'Arcanist':
                    self.manaRegenMultiplier += 0.5
                    self.manaCostMultiplier += 0.2
                elif self._ascendancy == 'Hierophant':
                    self.checkHierophantBuff()
                elif self._ascendancy == 'Unmaker':
                    self._stats['Temporary']['crit_resistance'] += 30
                    self._stats['Temporary']['increased_defenses'] += 10
                    self._stats['Temporary']['lifestea'] += 5

    def checkCalamity(self):
        if not self.calamity and self._ascendancy == 'Calamity':
            if self.relinquishedFire and self.relinquishedCold and self.relinquishedEarth and self.relinquishedLightning:
                self.calamity = True
                self._stats['Temporary']['crit_chance'] += 0.5
                self._stats['Temporary']['crit_multi'] += 1

    def checkProphetic(self):
        if not self.prophetic and self._ascendancy == 'Hierophant':
            if self.holyAdaptation and self.darkAdaptation and self.arcaneAdaptation:
                self.prophetic = True
                self.manaCostMultiplier += 0.5
                self._stats['Temporary']['resistance_penetration'] += 25
                self.checkHierophantBuff()

    def checkHierophantBuff(self):
        if not self.hierophantSuperBuff:
            if self.prophetic and self.archmage:
                self.hierophantSuperBuff = True
                self._stats['Temporary']['crit_chance'] += 0.25
                self._stats['Temporary']['crit_multi'] += 1
                self._stats['Temporary']['resistance_penetration'] += 25

    def gainAdaptation(self, damageType):
        if damageType in ELEMENTAL_RES:
            adaptGained = False
            if damageType == 'fire':
                adaptGained = self.gainFireAdaptation()
            elif damageType == 'cold':
                adaptGained = self.gainColdAdaptation()
            elif damageType == 'earth':
                adaptGained = self.gainEarthAdaptation()
            elif damageType == 'lightning':
                adaptGained = self.gainLightningAdaptation()
            self.checkArchmage()

            if self._ascendancy == 'Hierophant' and not adaptGained and not self.archmage:
                available = []
                if not self.fireAdaptation:
                    available.append('fire')
                if not self.coldAdaptation:
                    available.append('cold')
                if not self.earthAdaptation:
                    available.append('earth')
                if not self.lightningAdaptation:
                    available.append('lightning')
                dType = random.choice(available)
                self.gainAdaptation(dType)
        
        elif damageType in DIVINE_RES and self._ascendancy == 'Hierophant':
            if damageType == 'holy':
                self.gainHolyAdaptation()
            elif damageType == 'dark':
                self.gainDarkAdaptation()
            elif damageType == 'arcane':
                self.gainArcaneAdaptation()
            self.checkProphetic()

    def gainPrecision(self):
        if self._ascendancy == 'Unmaker' and self.unmakerPrecision < 10:
            self.unmakerPrecision += 1
            self._stats['Temporary']['crit_chance'] += 0.01
            self._stats['Temporary']['crit_chance'] += 0.15

    def onAttack(self, damageDealt, damageType, target, combatManager, ability, crit):
        damageDealt, damageType = super().onAttack(damageDealt, damageType, target, combatManager, ability, crit)

        if damageType in ELEMENTAL_RES or damageType == 'arcane':
            baseCost = damageDealt // 5 + 5
            manaCost = min(self._mana, int(baseCost * self.manaCostMultiplier))

            if self._ascendancy == 'Arcanist':
                arcFree = False
                arc60ManaUsed = False
                if manaCost >= (self._maxMana * 0.4):
                    self._mana = min(self._maxMana, self._mana + int(manaCost * 1.5))
                    arcFree = True
                if manaCost >= (self._mana * 0.6):
                    arc60ManaUsed = True
            
            elif self._ascendancy == 'Unmaker':
                if not crit:
                    manaCost = 0
                else:
                    manaCost = max(self._mana // 2, manaCost)
                    heal = int(manaCost * 0.75)
                    self.heal(heal)

            self._mana = max(0, self._mana - manaCost)

            damageDealt += manaCost
            if manaCost > 0:
                console.print(f"[class_mage]Used {manaCost} mana to empower attack with +{manaCost} damage.[/class_mage]")
            if self._ascendancy == 'Arcanist':
                if arcFree:
                    console.print(f"  [asc_arcanist]Arcanist:[/asc_arcanist] Attack consumed no Mana! Regained {int(0.5 * manaCost)} Mana.")

            if damageType == 'arcane':
                self.gainMastery()
                if self.archmage:
                    bonus = 0
                    if self._ascendancy == 'Empyrean':
                        bonus = 0.02 * self.mastery
                    damageDealt = int(damageDealt * (1.5 + bonus))

        if self._ascendancy == 'Calamity':
            if damageType == 'arcane':
                damageDealt = int(damageDealt * 1.2)
                if self.relinquishedFire:
                    damageDealt = int(damageDealt * 1.3)
            if self.calamity:
                damageDealt *= 2

        elif self._ascendancy == 'Arcanist':
            if damageType == 'arcane':
                manaPercent = max(0, 50 - int(self._mana / self._maxMana)) / 100
                damageDealt = int(damageDealt * (1 + manaPercent))
                if arc60ManaUsed:
                    damageDealt = int(damageDealt * 1.4)

        elif self._ascendancy == 'hierophant':
            if damageType == 'arcane':
                dGain = (0.15 * self.elementalAdaptations) + (0.1 * self.divineAdaptations)
                damageDealt = int(damageDealt * (1 + dGain))

        elif self._ascendancy == 'Empyrean':
            esRegen = int(manaCost * 0.1)
            if self.archmage:
                esRegen *= 2
            esRegen = min(self.maxEnergyShield - self.energyShield, esRegen)
            self._stats['energy_shield'] += esRegen

        return damageDealt, damageType

    def onExecuteCheck(self, target, combatManager):
        if self._ascendancy == 'Empyrean':
            if target._health < (target._maxHealth * (self.unmakerPrecision / 100)):
                console.print(f"[asc_unmaker]Unmaker: {target._name} was Executed from Precision![/asc_unmaker]")

                target.damage(target._health, 'true')
                combatManager.checkDead(target)

    def onBeforeCritRoll(self, targetUnit, targets, combatManager):
        if self._ascendancy == 'Unmaker' and self.unmakerPrecision == 10 and not self.unmakerCritChanceDoubled:
            self._stats['baseCritChance'] *= 2
            self._stats['Bonuses']['crit_chance'] *= 2
            self._stats['Temporary']['crit_chance'] *= 2
            self.unmakerCritChanceDoubled = True

    def onCrit(self, targets, combatManager, critDamage):
        if self._ascendancy == 'Calamity':
            relinquish = []
            if self.fireAdaptation:
                relinquish.append('fire')
            if self.coldAdaptation:
                relinquish.append('cold')
            if self.earthAdaptation:
                relinquish.append('earth')
            if self.lightningAdaptation:
                relinquish.append('lightning')
            if relinquish != []:
                rel = random.choice(relinquish)
                if rel == 'fire':
                    self.relinquishFire()
                elif rel == 'cold':
                    self.relinquishCold()
                elif rel == 'earth':
                    self.relinquishEarth()
                elif rel == 'lightning':
                    self.relinquishLightning()
                console.print(f"[asc_calamity]Calamity:[/asc_calamity] Relinquished {rel.title()} Adaptation.")
                if not self.calamity:
                    self.checkCalamity()

        elif self._ascendancy == 'Empyrean':
            self.gainMastery()
            self.gainMastery()

        elif self._ascendancy == 'Unmaker':
            self.gainPrecision()

        return critDamage

    def onBeforeCritRoll(self, targetUnit, targets, combatManager):
        if self._ascendancy == 'Unmaker' and self.unmakerPrecision == 10 and self.unmakerCritChanceDoubled:
            self._stats['baseCritChance'] /= 2
            self._stats['Bonuses']['crit_chance'] /= 2
            self._stats['Temporary']['crit_chance'] /= 2
            self.unmakerCritChanceDoubled = False

    def onCriticallyHit(self, attacker, combatManager, critDamage, damageType):
        if self._ascendancy == 'Unmaker':
            self.gainPrecision()
        
        return critDamage

    def onAfterAttack(self, target, targetUnit, finalDamage, combatManager):
        if self._ascendancy == 'Empyrean' and self.empyreanEsBroken:
            self.empyreanEsBroken = False
            self._stats['Temporary']['crit_chance'] -= 0.25
            self._stats['Temporary']['lifesteal'] -= 10
            self._stats['Temporary']['resistance_penetration'] -= 25

    def onHeal(self, healAmount):
        if self._ascendancy == 'Arcanist':
            mGain = healAmount // 2
            self._mana = min(self._maxMana, self._mana + mGain)

    def onEnergyShieldBroken(self, combatManager):
        if self._ascendancy == 'Empyrean' and not self.empyreanEsBroken:
            self.empyreanEsBroken = True
            self._stats['Temporary']['crit_chance'] += 0.25
            self._stats['Temporary']['lifesteal'] += 10
            self._stats['Temporary']['resistance_penetration'] += 25

    def onHit(self, damageTaken, damageType, crit=False, attacker=None, combatManager=None):
        damageTaken, damageType = super().onHit(damageTaken, damageType, crit, attacker, combatManager)

        if damageType in ELEMENTAL_RES:
            self.gainAdaptation(damageType)

        if self._ascendancy == 'Calamity':
            if damageType in ELEMENTAL_RES or damageType == 'arcane':
                damageTaken = int(damageTaken * 1.1)
            else:
                damageTaken = int(damageTaken * 0.9)
            if self.calamity:
                damageTaken = int(damageTaken * 0.8)

        elif self._ascendancy == 'Arcanist' and damageType in ELEMENTAL_RES:
            mGain = int(damageTaken * 0.1)
            self._mana = min(self._maxMana, self._mana + mGain)

        elif self._ascendancy == 'Empyrean':
            self.gainMastery()
            if damageType in ELEMENTAL_RES:
                self.gainMastery()

        return damageTaken, damageType

    def onKill(self, entity, attackData, combatManager):
        super().onKill(entity, attackData, combatManager)

        if self._ascendancy == 'Calamity' and attackData['damageType'] in DIVINE_RES:
            for e in combatManager.allAlive:
                e.damage(self._damage // 2, 'arcane')

        elif self._ascendancy == 'Unmaker':
            if self.mastery < self.maxMastery:
                self.gainMastery()
            else:
                heal = int(attackData['damage'] * 0.05)
                self.heal(heal)

        return {}

    def onTurnStart(self, combatManager=None):
        super().onTurnStart(combatManager)

        flatManaRegen = 0

        if self._ascendancy == 'Arcanist' and self.arcanistRegenGain < 0.2:
            self.manaRegenMultiplier += 0.02
            self.arcanistRegenGain += 0.02

        elif self._ascendancy == 'Empyrean':
            self.empyreanManaRegen = int(self.energyShield * 0.1)
            flatManaRegen += self.empyreanManaRegen + (10 * self.elementalAdaptations)
            mPercentBefore = self._mana / self._maxMana

        manaGain = int((self.manaRegen + flatManaRegen) * self.manaRegenMultiplier)

        self._mana = min(self._maxMana, self._mana + manaGain)

        if self._ascendancy == 'Empyrean':
            if (mPercentBefore < 0.8) and (self._mana / self._maxMana > 0.8):
                esRegen = min(self.maxEnergyShield - self.energyShield, manaGain)
                self._stats['energy_shield'] += esRegen

    def onCombatEnd(self):
        if self._ascendancy == 'Arcanist':
            self.manaRegen -= 2 * self.mastery

        self._mana = self._maxMana
        self.manaCostMultiplier = 1.0
        if self._ascendancy == 'Arcanist':
            self.manaCostMultiplier += 0.1
        self.manaRegenMultiplier = 1.0
        self.manaEffect = 1.0
        self.mastery = 0
        self.fireAdaptation = False
        self.coldAdaptation = False
        self.earthAdaptation = False
        self.lightningAdaptation = False
        self.archmage = False

        self.relinquishedFire = False
        self.relinquishedCold = False
        self.relinquishedEarth = False
        self.relinquishedLightning = False
        self.calamity = False

        self.arcanistRegenGain = 0

        self.holyAdaptation = False
        self.darkAdaptation = False
        self.arcaneAdaptation = False
        self.divineAdaptations = 0
        self.prophetic = False
        self.hierophantSuperBuff = False
        self.empyreanManaRegen = 0
        self.empyreanEsBroken = False
        self.unmakerPrecision = 0
        self.unmakerCritChanceDoubled = False
        super().onCombatEnd()

    def _removeOldAscendancy(self):
        if self._ascendancy == 'Calamity':
            self._baseHealth += 20
            self._baseDamage -= 6
            self._baseSpeed -= 0.15
            self.manaRegen -= 10
        elif self._ascendancy == 'Arcanist':
            self._baseHealth -= 20
            self._baseDamage += 4
            self._baseSpeed += 0.1
            self.manaCostMultiplier -= 0.1
        elif self._ascendancy == 'Hierophant':
            self._baseHealth -= 20
            self._baseDamage -= 4
            self._baseSpeed += 0.1
            self._stats['Permanent']['elemental'] -= 5
            self._stats['Permanent']['divine'] -= 5
        elif self._ascendancy == 'Empyrean':
            self._baseHealth -= 25
            self._baseDamage += 4
            self._baseSpeed += 0.1
            self.manaRegen -= 5
            self._stats['baseCritChance'] -= 0.05
            self._stats['Permanent']['added_energy_shield'] -= 50
        elif self._ascendancy == 'Unmaker':
            self._baseHealth += 20
            self._baseDamage -= 5
            self._baseSpeed -= 0.1
            self._stats['baseCritMulti'] -= 0.25
        return True

    def updateAscendancy(self, ascendancy):
        if not super().updateAscendancy(ascendancy):
            return
        self._recalculateStats(False)
        self._ascendancy = ascendancy
        self.ascendancyDescription = MAGE_DESCRIPTIONS[ascendancy]
        if ascendancy == 'Calamity':
            self._baseHealth -= 20
            self._baseDamage + 6
            self._baseSpeed += 0.15
            self.manaRegen += 10
        elif ascendancy == 'Arcanist':
            self._baseHealth += 20
            self._baseDamage -= 4
            self._baseSpeed -= 0.1
            self.manaCostMultiplier += 0.1
        elif ascendancy == 'Hierophant':
            self._baseHealth += 20
            self._baseDamage += 4
            self._baseSpeed -= 0.1
            self._stats['Permanent']['elemental'] += 5
            self._stats['Permanent']['divine'] += 5
        elif ascendancy == 'Empyrean':
            self._baseHealth += 25
            self._baseDamage -= 4
            self._baseSpeed -= 0.1
            self.manaRegen += 5
            self._stats['baseCritChance'] += 0.05
            self._stats['Permanent']['added_energy_shield'] += 50
        elif ascendancy == 'Unmaker':
            self._baseHealth -= 20
            self._baseDamage += 5
            self._baseSpeed += 0.1
            self._stats['baseCritMulti'] += 0.25

...