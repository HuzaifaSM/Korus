from scripts.items import Equipment, ItemRarity

from scripts.crafting.growthRune import GROWTH_RUNES
from scripts.crafting.chaosRune import CHAOS_RUNES
from scripts.crafting.erasingRune import ERASING_RUNES
from scripts.crafting.uniqueRunes import UNIQUE_RUNES
from scripts.crafting.randomiserRunes import RANDOMISER_RUNES
from scripts.crafting.masteryRune import MASTERY_RUNES
from scripts.crafting.rarityRune import RARITY_RUNES
from scripts.crafting.destabilisationRune import DESTABILISATION_RUNES
from scripts.crafting.revealingRune import REVEALING_RUNES
from scripts.crafting.manipulationRune import MANIPULATION_RUNES

from scripts.styles import console

e = Equipment._generateEquipmentPiece(100, 'weapon', ItemRarity.LEGENDARY)

rune = ERASING_RUNES['blank']
rune.apply(e)


p = UNIQUE_RUNES['preservation']

rune = UNIQUE_RUNES['soulbound']
p.apply(e)
rune.apply(e)

p.apply(e)
rune = GROWTH_RUNES['divine']
rune.apply(e)
rune.apply(e)
console.print(e)

rune = REVEALING_RUNES['pinpoint']
p.apply(e)
rune.apply(e)
p.apply(e)
rune.apply(e)
p.apply(e)
rune.apply(e)

m = MASTERY_RUNES['divine']
m.apply(e)
m.apply(e)

p.apply(e)
rune = RANDOMISER_RUNES['perfect_value']
rune.apply(e)

rune = DESTABILISATION_RUNES['perfect']
rune.apply(e)

console.print(e)
