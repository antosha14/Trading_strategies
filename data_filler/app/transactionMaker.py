from decimal import ROUND_DOWN, Decimal

from app.config import settings
from binance.spot import Spot

client = Spot()

BINANCE_API_KEY = settings.BINANCE_API_KEY
BINANCE_API_SECRET = settings.BINANCE_API_SECRET

client = Spot(api_key=BINANCE_API_KEY, api_secret=BINANCE_API_SECRET)


def round_down(value, decimals):
    d = Decimal(value)
    return d.quantize(Decimal("1." + "0" * decimals), rounding=ROUND_DOWN)


def get_coin_amount(ticker):
    coin_info = client.coin_info()
    for coin in coin_info:
        if coin["coin"] == ticker:
            return coin["free"]


def makeBuyTransaction(price):
    quantity = round_down(round(float(get_coin_amount("USDT")) / price, 7), 4)
    params = {
        "symbol": "BTCUSDT",
        "side": "BUY",
        "type": "MARKET",
        "quantity": quantity,
    }
    print(quantity)
    response = client.new_order(**params)
    print(response)


def makeSellTransaction():
    quantity = round_down(round(float(get_coin_amount("BTC")), 7), 4)
    params = {
        "symbol": "BTCUSDT",
        "side": "SELL",
        "type": "MARKET",
        "quantity": quantity,
    }
    print(quantity)
    response = client.new_order(**params)
    print(response)
