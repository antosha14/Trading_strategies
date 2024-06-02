from collections.abc import Generator
from typing import Annotated

from config import settings
from fastapi import Depends
from sqlmodel import Session, create_engine

engine = create_engine(str(settings.SQLALCHEMY_DATABASE_URI), echo=True)


def get_db() -> Generator[Session, None, None]:
    with Session(engine) as session:
        yield session


SessionDep = Annotated[Session, Depends(get_db)]
