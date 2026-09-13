from scripts.items.items import ItemRarity
from scripts.items.equipment import Equipment
from scripts.items.affixes import Affix, rollAffix
from copy import deepcopy

eq = Equipment._generateEquipmentPiece(50, 'chest', ItemRarity.LEGENDARY)
eq2 = deepcopy(eq)
eq2.prefixSlots[1].affix = None
eq2.prefixSlots[2].affix = None

for i in range(len(eq.prefixSlots)):
    
    if eq.prefixSlots[i].affix == eq2.prefixSlots[i].affix:
        print("same")
    else:
        print("different")