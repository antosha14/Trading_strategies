from app.db import engine
from app.models import BTC_TimestampData, SAP_TimestampData
from sqlmodel import Session


def add_btc_timestamp_data(*, data: BTC_TimestampData) -> BTC_TimestampData:
    with Session(engine) as session:
        db_obj = BTC_TimestampData.model_validate(data)
        session.add(db_obj)
        session.commit()
        session.refresh(db_obj)
        return db_obj


def add_sap_timestamp_data(*, data: SAP_TimestampData) -> SAP_TimestampData:
    with Session(engine) as session:
        db_obj = SAP_TimestampData.model_validate(data)
        session.add(db_obj)
        session.commit()
        session.refresh(db_obj)
        return db_obj
