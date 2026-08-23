from scripts.items import ItemRarity

x = ItemRarity.UNCOMMON
y = list(ItemRarity)
a = y[y.index(x)+1]
print(a)