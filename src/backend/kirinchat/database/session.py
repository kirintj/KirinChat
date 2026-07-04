import logging

from contextlib import contextmanager, asynccontextmanager
from typing import Iterator, AsyncIterator

from sqlmodel.ext.asyncio.session import AsyncSession
from sqlmodel import Session
from kirinchat.database import get_engine, get_async_engine

logger = logging.getLogger(__name__)

@contextmanager
def session_getter() -> Iterator[Session]:
    session = Session(get_engine())

    try:
        yield session
    except Exception as e:
        logger.info('Session rollback because of exception:{}', e)
        session.rollback()
        raise
    finally:
        session.close()

@asynccontextmanager
async def async_session_getter() -> AsyncIterator[AsyncSession]:
    session = AsyncSession(get_async_engine())

    try:
        yield session
    except Exception as e:
        logger.info('Session rollback because of exception: %s', e)
        await session.rollback()  # 异步回滚
        raise
    finally:
        await session.close()  # 异步关闭会话