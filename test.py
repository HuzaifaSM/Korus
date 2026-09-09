from scripts.items.affixes import rollAffix
from scripts.items.items import ItemRarity

x = []
x.append(rollAffix('weapon', 'prefix', 10, ItemRarity.RARE))
x.append(rollAffix('weapon', 'prefix', 10, ItemRarity.RARE))
x.append(rollAffix('weapon', 'prefix', 10, ItemRarity.RARE))

y = ""
for a in x:
    y += f"- {a}\n"
print(y)