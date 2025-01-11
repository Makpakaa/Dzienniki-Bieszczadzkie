# Ten plik zawiera klasę NPC, która reprezentuje postacie niezależne (NPC) w grze i obsługuje ich dialogi.

class NPC:
    def __init__(self, name, dialogue):
        self.name = name
        self.dialogue = dialogue  # Słownik z dialogami

    def talk(self):
        return self.dialogue


