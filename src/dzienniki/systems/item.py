from dataclasses import dataclass
from typing import Optional

@dataclass
class Item:
    name: str
    count: int = 1
    description: Optional[str] = None
    item_type: str = "misc"  # np. 'tool', 'food', 'clothing'
    max_stack: int = 50
    equipped: bool = False
    slot: Optional[str] = None  # np. 'head', 'torso', 'legs', itd.

    def is_stackable(self) -> bool:
        return self.max_stack > 1

    def can_equip(self) -> bool:
        return self.item_type == "clothing" and self.slot is not None

    def get_display_name(self) -> str:
        if self.count > 1:
            return f"{self.name} ({self.count})"
        return self.name
