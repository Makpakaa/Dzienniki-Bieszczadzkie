# shop.py

class Shop:
    def __init__(self, name):
        self.name = name
        self.items_for_sale = []  # lista krotek (nazwa, ilość, cena)

    def add_item(self, item_name, quantity, price):
        self.items_for_sale.append((item_name, quantity, price))

    def get_item(self, index):
        if 0 <= index < len(self.items_for_sale):
            return self.items_for_sale[index]
        else:
            return None

    def remove_item(self, index):
        if 0 <= index < len(self.items_for_sale):
            return self.items_for_sale.pop(index)
        else:
            return None

    def list_items(self):
        return [f"{name} ({quantity}) - {price} zł" for (name, quantity, price) in self.items_for_sale]

    def buy_item(self, index, player_money):
        item = self.get_item(index)
        if item:
            name, quantity, price = item
            if player_money >= price:
                self.remove_item(index)
                return name, quantity, price
            else:
                return None  # brak środków
        return None  # brak przedmiotu

