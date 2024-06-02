import datetime
import json

import crud
import websocket
import yfinance as yf
from config import settings
from models import SAP_TimestampData
from telegram_messaging import send_telegram_message

yahoo_finance_websocket_link = "wss://streamer.finance.yahoo.com/"
sp500_ticker = yf.Ticker("SPY")


def on_message(ws, message):
    data = json.loads(message)
    current_price = data["data"][0]["last"]
    print(f"The current price of SPY is: ${current_price}")
    # crud.add_sap_timestamp_data(
    #    data=SAP_TimestampData(
    #        timestamp=datetime.now(),
    #        price=current_price,
    #    )
    # )


def on_open(ws):
    tg_popup = f"Data Gathering App launched SaP500 websocket connection."
    send_telegram_message(settings.TELEGRAM_CHAT_ID, message=tg_popup)


# TODO: Add kafka integration for messaging
def on_error(ws, message):
    tg_popup = f"Data Gathering App encounterd an error on SaP500 websocket or was simply closed. {message}"
    send_telegram_message(settings.TELEGRAM_CHAT_ID, message=tg_popup)


def on_close(ws, message, _):
    tg_popup = f"Data Gathering SaP500 websocket was closed."
    send_telegram_message(settings.TELEGRAM_CHAT_ID, message=tg_popup)


# Establish a websocket connection
def start_sap500_data_stream():
    try:
        ws = websocket.WebSocketApp(
            yahoo_finance_websocket_link,
            on_message=on_message,
            on_error=on_error,
            on_close=on_close,
            on_open=on_open,
        )
        ws.send('{"subscribe":["SPY"]}')
        ws.run_forever()
    except Exception as e:
        send_telegram_message(
            settings.TELEGRAM_CHAT_ID,
            message=f"Failed to establish SaP500 websocket connection. {e}",
        )
