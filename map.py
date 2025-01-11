# Ten plik zawiera klasę Map, która obsługuje mapę gry i wyświetla jej aktualny stan.

class Map:
    def __init__(self):
        self.grid = [["Wioska", "Las", "Jaskinia"],
                     ["Łąka", "Jezioro", "Ruiny"],
                     ["Bagna", "Góra", "Opuszczona Chata"]]

    def display_map(self, player_position):
        for y, row in enumerate(self.grid):
            row_display = ""
            for x, location in enumerate(row):
                if [x, y] == player_position:
                    row_display += "[X] "  # Pozycja gracza
                else:
                    row_display += f"[{location[:1]}] "
            print(row_display)


