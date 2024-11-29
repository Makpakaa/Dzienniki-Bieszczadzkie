from seed import Seed

# Lista dostępnych roślin w grze
plants = [
    {
        "seed": Seed(
            seed_id=1,
            name="Nasiona Marchewki",
            growth_days=3,
            yield_name="Marchew",
            buy_price=3,
            sell_price=5,
            growth_season="Wiosna",
            quantity=1
        ),
        "description": "Marchew jest podstawową rośliną o krótkim czasie wzrostu.",
    },
    {
        "seed": Seed(
            seed_id=2,
            name="Sadzonka Ziemniaka",
            growth_days=12,
            yield_name="Ziemniak",
            buy_price=10,
            sell_price=15,
            growth_season="Wiosna, Lato",
            quantity=1
        ),
        "description": "Ziemniaki rosną długo, ale dają więcej plonów.",
    },
    {
        "seed": Seed(
            seed_id=3,
            name="Nasiona Pomidora",
            growth_days=10,
            yield_name="Pomidor",
            buy_price=6,
            sell_price=4,
            growth_season="Lato",
            quantity=1
        ),
        "description": "Pomidor to roślina letnia, idealna na ciepłe dni.",
    },
    # Możesz dodać więcej roślin według potrzeb
]
