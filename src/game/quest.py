# Ten plik zawiera klasę Quest, która definiuje zadania (questy) w grze i ich wymagania.

class Quest:
    def __init__(self, title, description, requirements):
        self.title = title
        self.description = description
        self.requirements = requirements
        self.completed = False

    def check_completion(self, player):
        if all(req in player.inventory for req in self.requirements):
            self.completed = True
            return True
        return False
