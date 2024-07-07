from datetime import datetime
from decimal import Decimal

from sqlmodel import Field, SQLModel


class BTC_TimestampData(SQLModel, table=True):
    timestamp: datetime = Field(
        primary_key=True,
    )
    price: Decimal = Field(default=0, decimal_places=6)
    volume_5000_bids: float
    volume_5000_asks: float
    weighted_avg_bid_price: float
    weighted_avg_ask_price: float


class SAP_TimestampData(SQLModel, table=True):
    timestamp: datetime = Field(primary_key=True)
    price: Decimal = Field(default=0, decimal_places=6)
