# TODO: Rewrite using asincio
import json
from datetime import datetime

import app.crud as crud
import numpy as np
import requests
import websocket
from app.config import settings
from app.models import BTC_TimestampData
from services_and_queue.telegram_messaging import send_telegram_message

btc_ticker_for_binance = "BTCUSDT"
btc_subscribtion_str = (
    btc_ticker_for_binance.lower()
    + "@kline_1s/"
    + btc_ticker_for_binance.lower()
    + "@depth"
)
binance_combined_websocket_url = (
    f"wss://stream.binance.com:9443/stream?streams={btc_subscribtion_str}"
)
time_format_string = "%Y-%m-%d %H:%M:%S"

current_order_book_snapshot_link = (
    f"https://api.binance.com/api/v3/depth?symbol={btc_ticker_for_binance}&limit=10000"
)
pure_price_url = f"https://api.binance.com/api/v3/ticker/price"
VOLUME_ARRAY_SIZE = 5000

current_bids_arr = np.array(1)
current_asks_arr = np.array(1)
current_price = 0
current_time = datetime.now().strftime(time_format_string)


def create_initial_order_book():
    response = requests.get(current_order_book_snapshot_link).json()
    global current_bids_arr, current_asks_arr
    current_bids_arr = np.asfarray(response["bids"])
    current_asks_arr = np.asfarray(response["asks"])


def price_data_parsing(data):
    global current_price, current_time
    current_price = data["data"]["k"]["c"]  # close price
    current_time = datetime.fromtimestamp(data["data"]["E"] / 1000).strftime(
        time_format_string
    )


def on_message(ws, message):
    global current_bids_arr, current_asks_arr
    message = json.loads(message)
    if message["stream"] == "btcusdt@kline_1s":
        price_data_parsing(message)
    else:
        volume_time = datetime.fromtimestamp(message["data"]["E"] / 1000).strftime(
            time_format_string
        )
        bid_arr_to_update = np.asfarray(message["data"]["b"])
        matching_bid_prices = current_bids_arr[
            np.where(np.isin(current_bids_arr[:, 0], bid_arr_to_update[:, 0]))
        ][0]

        for price, volume in bid_arr_to_update:
            ind = np.where(current_bids_arr[:, 0] == price)
            if volume == 0:
                current_bids_arr = np.delete(current_bids_arr, ind, axis=0)
            elif price in matching_bid_prices:
                current_bids_arr[ind, 1] = volume
            else:
                current_bids_arr = np.vstack([current_bids_arr, [price, volume]])

        partly_filtered_current_bids = current_bids_arr[
            current_bids_arr[:, 0] < np.float64(current_price)
        ]
        sorted_partly_filtered_current_bids = np.sort(
            partly_filtered_current_bids, axis=0
        )[::-1]
        highest_5000_bids = sorted_partly_filtered_current_bids[:5000]
        volume_of_5000_bids = np.sum(highest_5000_bids[:, 1])

        if volume_of_5000_bids == 0:
            weighted_avg_bid_price = 0
        else:
            weighted_avg_bid_price = np.average(
                highest_5000_bids[:, 0], weights=highest_5000_bids[:, 1]
            )

        ask_arr_to_update = np.asfarray(message["data"]["a"])
        matching_ask_prices = current_asks_arr[
            np.where(np.isin(current_asks_arr[:, 0], ask_arr_to_update[:, 0]))
        ][0]

        for price, volume in ask_arr_to_update:
            ind = np.where(current_asks_arr[:, 0] == price)
            if volume == 0:
                current_asks_arr = np.delete(current_asks_arr, ind, axis=0)
            elif price in matching_ask_prices:
                current_asks_arr[ind, 1] = volume
            else:
                current_asks_arr = np.vstack([current_asks_arr, [price, volume]])

        partly_filtered_current_asks = current_asks_arr[
            current_asks_arr[:, 0] > np.float64(current_price)
        ]
        sorted_partly_filtered_current_asks = np.sort(
            partly_filtered_current_asks, axis=0
        )
        lowest_5000_asks = sorted_partly_filtered_current_asks[:5000]
        volume_of_5000_asks = np.sum(lowest_5000_asks[:, 1])

        if volume_of_5000_asks == 0:
            weighted_avg_ask_price = 0
        else:
            weighted_avg_ask_price = np.average(
                lowest_5000_asks[:, 0], weights=lowest_5000_asks[:, 1]
            )

        crud.add_btc_timestamp_data(
            data=BTC_TimestampData(
                timestamp=volume_time,
                price=current_price,
                volume_5000_bids=volume_of_5000_bids,
                volume_5000_asks=volume_of_5000_asks,
                weighted_avg_bid_price=weighted_avg_bid_price,
                weighted_avg_ask_price=weighted_avg_ask_price,
            )
        )


def on_open(ws):
    tg_popup = f"Data Gathering App launched Bitcoin websocket connection."
    send_telegram_message.delay(settings.TELEGRAM_CHAT_ID, message=tg_popup)


# TODO: Add kafka integration for messaging
def on_error(ws, message):
    tg_popup = f"Data Gathering App encounterd an error on Bitcoin socket or was simply closed. {message}"
    send_telegram_message.delay(settings.TELEGRAM_CHAT_ID, message=tg_popup)


def on_close(ws, message, _):
    tg_popup = f"Data Gathering Bitcoin websocket was closed."
    send_telegram_message.delay(settings.TELEGRAM_CHAT_ID, message=tg_popup)


def start_bitcoin_data_stream():
    try:
        global current_price, current_time
        current_price = float(
            requests.get(
                pure_price_url, params={"symbol": btc_ticker_for_binance}
            ).json()["price"]
        )
        current_time = datetime.now().strftime(time_format_string)
        ws = websocket.WebSocketApp(
            binance_combined_websocket_url,
            on_message=on_message,
            on_error=on_error,
            on_close=on_close,
            on_open=on_open,
        )
        create_initial_order_book()
        ws.run_forever()
    except Exception as e:
        send_telegram_message.delay(
            settings.TELEGRAM_CHAT_ID,
            message=f"Failed to establish websocket connection. {e}",
        )
