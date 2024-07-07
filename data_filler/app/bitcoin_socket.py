# TODO: Rewrite using asincio
import asyncio
import json
import os
import sys
from datetime import datetime
from pathlib import Path

import aiohttp
import app.crud as crud
import numpy as np
import requests
from app.config import settings
from app.models import BTC_TimestampData

sys.path.append(str(Path(os.path.dirname(__file__)).parent.parent))

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


async def create_order_book():
    async with aiohttp.ClientSession() as session:
        async with session.get(current_order_book_snapshot_link, proxy=None) as request:
            response = await request.json()
            global current_bids_arr, current_asks_arr
            current_bids_arr = np.asfarray(response["bids"])
            current_asks_arr = np.asfarray(response["asks"])
            return [current_bids_arr, current_asks_arr]


async def get_price():
    async with aiohttp.ClientSession() as session:
        async with session.get(
            pure_price_url, params={"symbol": btc_ticker_for_binance}, proxy=None
        ) as request:
            response = await request.json()
            timestamp = datetime.now()
            global current_price
            current_price = float(response["price"])
            return [current_price, timestamp]


async def commit_to_db(current_price, ask_arr, bid_arr, price_resp_time):
    timestamp = price_resp_time
    volume_of_returned_bids = np.sum(bid_arr[:, 1])
    volume_of_returned_asks = np.sum(ask_arr[:, 1])
    weighted_avg_bid_price = np.average(bid_arr[:, 0], weights=bid_arr[:, 1])
    weighted_avg_ask_price = np.average(ask_arr[:, 0], weights=ask_arr[:, 1])
    crud.add_btc_timestamp_data(
        data=BTC_TimestampData(
            timestamp=timestamp,
            price=current_price,
            volume_5000_bids=volume_of_returned_bids,
            volume_5000_asks=volume_of_returned_asks,
            weighted_avg_bid_price=weighted_avg_bid_price,
            weighted_avg_ask_price=weighted_avg_ask_price,
        )
    )


async def start_bitcoin_data_stream():
    send_telegram_message.delay(
        settings.TELEGRAM_CHAT_ID,
        message=f"Data Gathering App was launched",
    )
    while True:
        try:
            global current_price, current_time
            api_result = await asyncio.gather(
                create_order_book(), get_price(), asyncio.sleep(1)
            )
            waiting_and_commit = await asyncio.gather(
                commit_to_db(
                    api_result[1][0],
                    api_result[0][1],
                    api_result[0][0],
                    api_result[1][1],
                ),
            )
        except Exception as e:
            send_telegram_message.delay(
                settings.TELEGRAM_CHAT_ID,
                message=f"Data Gathering App encounterd an error on Bitcoin or was simply closed. {e}",
            )
            break
