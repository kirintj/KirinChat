from kirinchat.database import SystemUser
from kirinchat.database.models.agent import AgentTable
from sqlmodel import select, and_, update, desc, delete, or_

from kirinchat.database.session import async_session_getter


class AgentDao:

    @classmethod
    async def create_agent(
        cls,
        agent: AgentTable
    ):
        async with async_session_getter() as session:
            session.add(agent)
            await session.commit()
            await session.refresh(agent)
            return agent

    @classmethod
    async def get_agent(cls):
        async with async_session_getter() as session:
            statement = select(AgentTable).order_by(desc(AgentTable.create_time))
            result = await session.exec(statement)
            return result.all()

    @classmethod
    async def select_agent_by_name(cls, name: str):
        async with async_session_getter() as session:
            statement = select(AgentTable).where(AgentTable.name == name)
            result = await session.exec(statement)
            return result.first()

    @classmethod
    async def get_agent_user_id(cls, agent_id: str):
        async with async_session_getter() as session:
            statement = select(AgentTable).where(AgentTable.id == agent_id)
            agent = await session.exec(statement)
            return agent.first()

    @classmethod
    async def select_agent_by_custom(cls, is_custom: bool):
        async with async_session_getter() as session:
            statement = select(AgentTable).where(AgentTable.is_custom == is_custom)
            result = await session.exec(statement)
            return result.all()

    @classmethod
    async def delete_agent_by_id(cls, id: str):
        async with async_session_getter() as session:
            statement = delete(AgentTable).where(AgentTable.id == id)
            await session.exec(statement)
            await session.commit()

    @classmethod
    async def _get_logo_by_id(cls, id: str):
        async with async_session_getter() as session:
            statement = select(AgentTable).where(AgentTable.id == id)
            result = await session.exec(statement)
            rows = result.all()
            return rows[0][0].logo_url

    @classmethod
    async def check_repeat_name(cls, name: str, user_id: str):
        async with async_session_getter() as session:
            statement = select(AgentTable).where(
                and_(
                    AgentTable.name == name,
                    AgentTable.user_id == user_id
                )
            )
            result = await session.exec(statement)
            return result.all()

    @classmethod
    async def search_agent_name(
        cls,
        name: str,
        user_id: str
    ):
        async with async_session_getter() as session:
            statement = select(AgentTable).where(
                and_(
                    AgentTable.name.like(f'%{name}%'),
                    or_(
                        AgentTable.user_id == user_id,
                        AgentTable.user_id == SystemUser
                    )
                )
            )
            result = await session.exec(statement)
            return result.all()

    @classmethod
    async def get_agent_by_user_id(
        cls,
        user_id: str
    ):
        async with async_session_getter() as session:
            statement = select(AgentTable).where(AgentTable.user_id == user_id)
            result = await session.exec(statement)
            return result.all()

    @classmethod
    async def select_agent_by_id(
        cls,
        agent_id
    ):
        async with async_session_getter() as session:
            statement = select(AgentTable).where(AgentTable.id == agent_id)
            result = await session.exec(statement)
            return result.first()

    @classmethod
    async def update_agent_by_id(
        cls,
        agent_id: str,
        update_values: dict
    ):
        async with async_session_getter() as session:
            statement = (
                update(AgentTable)
                .where(AgentTable.id == agent_id)
                .values(**update_values)
            )
            await session.exec(statement)
            await session.commit()
