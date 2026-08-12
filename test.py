from os.path import exists
from scripts.styles import console
from crafting.randomiserRunes import RANDOMISER_RUNES
from scripts.items import ItemRarity
from scripts.mythicAffixes import rollMythicAffix

af2 = rollMythicAffix('amulet', 'suffix', 80, ItemRarity.MYTHIC, set())
console.print(af2)
console.print(af2.name)