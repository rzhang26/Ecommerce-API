from collections.abc import Generator, AsyncGenerator
from typing import Annotated
from fastapi import Depends
from sqlmodel import create_engine, Session
from app.config import get_settings

engine = create_engine(
    get_settings().DATABASE_URL,
    pool_size=20,
    max_overflow=30,
    pool_pre_ping=True
)

#why not async ? 
# async def get_session() -> AsyncGenerator[Session, None, None]:
#     with Session(engine) as session:
#         yield session

def get_session() -> Generator[Session, None, None]:
    with Session(engine) as session:
        yield session

SessionDep = Annotated[Session, Depends(get_session)]
#alternative to passing in 'session: Session = Depends(get_session)' as type-hinting for 
# session param in other files