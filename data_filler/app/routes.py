import asyncio

from app.bitcoin_socket import start_bitcoin_data_stream
from fastapi import APIRouter

router = APIRouter(tags=["data"])


@router.get("/getdata/{ticker}")
def get_data_by_ticker(ticker: str) -> str:
    return f"Hello world. I see, that you are a man of culture, because you'd like to trade {ticker}"


@router.get("/status/")
def get_all_data() -> str:
    return f"App is working."


@router.get("/launch/")
def start_stream() -> str:
    asyncio.run(start_bitcoin_data_stream())
    return f"Launched successfully"
