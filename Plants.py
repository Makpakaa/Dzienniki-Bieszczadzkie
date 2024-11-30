# Definicja klasy Seed
class Seed:
    def __init__(self, seed_id, growth_days, yield_range, sell_price, quantity=1, name=None, yield_name=None,
                 yield_frequency=None, max_harvests=None, is_perennial=False, fruiting_season=None,
                 max_fruits_per_day=None, fruit_duration=None):
        self.seed_id = seed_id
        self.growth_days = growth_days
        self.yield_range = yield_range
        self.sell_price = sell_price
        self.quantity = quantity
        self.name = name or f"Nasiono {seed_id}"
        self.yield_name = yield_name or f"Plon {seed_id}"
        self.yield_frequency = yield_frequency  # Dni między zbiorami (dla wielokrotnych zbiorów)
        self.max_harvests = max_harvests  # Maksymalna liczba zbiorów
        self.is_perennial = is_perennial  # Czy roślina jest wieloletnia
        self.fruiting_season = fruiting_season  # Sezon owocowania (dla drzew owocowych)
        self.max_fruits_per_day = max_fruits_per_day  # Maks. liczba owoców dziennie
        self.fruit_duration = fruit_duration  # Czas trwania owocowania (w dniach)



# Lista dostępnych roślin w grze
plants = [
    # Rośliny jednoroczne
    Seed(seed_id=1, growth_days=5, yield_range=(2, 4), sell_price=15, quantity=1, name="Nasiona Marchewki", yield_name="Marchew"),
    Seed(seed_id=2, growth_days=7, yield_range=(3, 5), sell_price=20, quantity=1, name="Nasiona Ziemniaka", yield_name="Ziemniak"),
    # Rośliny wielokrotnego zbioru
    Seed(seed_id=3, growth_days=8, yield_range=(1, 4), sell_price=10, quantity=1, name="Nasiona Pomidora", yield_name="Pomidor",
         yield_frequency=2, max_harvests=10),  # Pomidory można zbierać co 2 dni, maks. 10 zbiorów
    # Drzewa owocowe
    Seed(seed_id=4, growth_days=20, yield_range=(1, 3), sell_price=30, quantity=1, name="Sadzonka Jabłoni", yield_name="Jabłko",
         is_perennial=True, fruiting_season="jesień", max_fruits_per_day=3, fruit_duration=30),  # Jabłonie owocują jesienią przez 30 dni
    Seed(seed_id=5, growth_days=25, yield_range=(1, 2), sell_price=40, quantity=1, name="Sadzonka Gruszy", yield_name="Gruszka",
         is_perennial=True, fruiting_season="jesień", max_fruits_per_day=2, fruit_duration=25),  # Grusze owocują jesienią przez 25 dni
    # Dodaj kolejne rośliny według potrzeb
]
