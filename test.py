from scripts.styles import console
from scripts.items import ItemRarity, Equipment

e = Equipment._generateEquipmentPiece(100, 'weapon', ItemRarity.MYTHIC)
console.print(e)
e.mastery = 20
e.update()
console.print(e)