import pytest
from game.shop import Shop

@pytest.fixture
def shop():
    s = Shop("TestShop")
    s.add_item("Miecz", qty=1, price=100)
    s.add_item("Tarcza", qty=2, price=150)
    return s

def test_list_items(shop):
    items = shop.list_items()
    assert "Miecz (1) - 100 zł" in items
    assert "Tarcza (2) - 150 zł" in items

def test_buy_item_success(shop):
    name, qty, price = shop.buy_item(0, player_money=200)
    assert name == "Miecz"
    assert qty == 1
    assert price == 100
    assert len(shop.list_items()) == 1

def test_buy_item_insufficient_funds(shop):
    result = shop.buy_item(0, player_money=50)
    assert result is None

def test_buy_item_out_of_range(shop):
    assert shop.buy_item(10, player_money=1000) is None
