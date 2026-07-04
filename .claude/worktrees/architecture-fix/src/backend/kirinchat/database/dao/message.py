from kirinchat.database.models.message import MessageDownTable, MessageLikeTable
from sqlmodel import Session, select
from kirinchat.database.session import async_session_getter

class MessageLikeDao:

    @classmethod
    def _get_message_like_sql(cls, user_input: str, agent_output: str):
        like = MessageLikeTable(user_input=user_input, agent_output=agent_output)
        return like

    @classmethod
    async def create_message_like(cls, user_input: str, agent_output: str):
        async with async_session_getter() as session:
            session.add(cls._get_message_like_sql(user_input, agent_output))
            await session.commit()

    @classmethod
    async def get_message_like(cls):
        async with async_session_getter() as session:
            sql = select(MessageLikeTable)
            result = await session.exec(sql)
            return result.all()


class MessageDownDao:

    @classmethod
    def _get_message_down_sql(cls, user_input: str, agent_output: str):
        down = MessageDownTable(user_input=user_input, agent_output=agent_output)
        return down

    @classmethod
    async def create_message_down(cls, user_input: str, agent_output: str):
        async with async_session_getter() as session:
            session.add(cls._get_message_down_sql(user_input, agent_output))
            await session.commit()

    @classmethod
    async def get_message_down(cls):
        async with async_session_getter() as session:
            sql = select(MessageDownTable)
            result = await session.exec(sql)
            return result.all()
