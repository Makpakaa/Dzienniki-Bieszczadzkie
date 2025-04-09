# container.py

class Container:
    def __init__(self, name, capacity):
        self.name = name
        self.capacity = capacity
        self.items = []  # lista krotek (nazwa, ilość)

    def add_item(self, item_name, quantity=1):
        if len(self.items) < self.capacity:
            self.items.append((item_name, quantity))
            return True
        else:
            return False  # brak miejsca

    def remove_item(self, index):
        if 0 <= index < len(self.items):
            return self.items.pop(index)
        else:
            return None  # nieprawidłowy indeks

    def is_empty(self):
        return len(self.items) == 0

    def can_pick_up(self):
        return self.is_empty()  # można podnieść tylko pustą skrzynię
