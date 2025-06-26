import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))
from dzienniki.systems.item import Item

item = Item(name="Kurtka", count=2, item_type="clothing", slot="torso")
print(item.get_display_name())  # Oczekiwany wynik: Kurtka (2)
print(item.can_equip())         # Oczekiwany wynik: True
print(item.is_stackable())      # Oczekiwany wynik: True
