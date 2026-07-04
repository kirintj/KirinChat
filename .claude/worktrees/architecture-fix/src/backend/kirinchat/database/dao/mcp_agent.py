from datetime import datetime

from typing import List
from kirinchat.database.models.mcp_agent import MCPAgentTable
from sqlmodel import Session, select, and_, update, desc, delete
from kirinchat.utils.helpers import delete_img
from kirinchat.database.session import async_session_getter


class MCPAgentDao:

    @classmethod
    def _get_mcp_agent_sql(cls, name: str, description: str, logo: str, user_id: str, knowledges_id: List[str],
                           llm_id: str, mcp_servers_id: List[str], is_custom: bool, enable_memory: bool):
        agent = MCPAgentTable(name=name,
                              logo=logo,
                              user_id=user_id,
                              llm_id=llm_id,
                              mcp_servers_id=mcp_servers_id,
                              description=description,
                              knowledges_id=knowledges_id,
                              is_custom=is_custom,
                              enable_memory=enable_memory)
        return agent

    @classmethod
    async def create_mcp_agent(cls, name: str, description: str, logo: str, user_id: str, knowledges_id: List[str],
                         llm_id: str, mcp_servers_id: List[str], is_custom: bool, enable_memory: bool):
        async with async_session_getter() as session:
            session.add(cls._get_mcp_agent_sql(name, description, logo, user_id, knowledges_id, llm_id, mcp_servers_id,
                                               is_custom, enable_memory))
            await session.commit()

    @classmethod
    async def get_mcp_agent(cls):
        async with async_session_getter() as session:
            sql = select(MCPAgentTable).order_by(desc(MCPAgentTable.create_time))
            result = await session.exec(sql)
            return result.all()

    @classmethod
    async def select_mcp_agent_by_name(cls, name: str):
        async with async_session_getter() as session:
            sql = select(MCPAgentTable).where(MCPAgentTable.name == name)
            result = await session.exec(sql)
            return result.first()

    @classmethod
    async def get_mcp_agent_user_id(cls, agent_id: str):
        async with async_session_getter() as session:
            sql = select(MCPAgentTable).where(MCPAgentTable.id == agent_id)
            agent = await session.exec(sql)
            return agent.first()

    @classmethod
    async def select_mcp_agent_by_custom(cls, is_custom: bool):
        async with async_session_getter() as session:
            sql = select(MCPAgentTable).where(MCPAgentTable.is_custom == is_custom)
            result = await session.exec(sql)
            return result.all()

    @classmethod
    async def delete_mcp_agent_by_id(cls, id: str):
        async with async_session_getter() as session:
            sql = delete(MCPAgentTable).where(MCPAgentTable.id == id)
            await session.exec(sql)
            # 删除agent的logo地址
            agent_logo = await cls._get_logo_by_id(id)
            delete_img(logo=agent_logo)
            await session.commit()

    @classmethod
    async def _get_logo_by_id(cls, id: str):
        async with async_session_getter() as session:
            sql = select(MCPAgentTable).where(MCPAgentTable.id == id)
            result = await session.exec(sql)
            rows = result.all()
            return rows[0][0].logo

    @classmethod
    async def check_repeat_name(cls, name: str, user_id: str):
        async with async_session_getter() as session:
            sql = select(MCPAgentTable).where(and_(MCPAgentTable.name == name, MCPAgentTable.user_id == user_id))
            result = await session.exec(sql)
            return result.all()

    @classmethod
    async def search_mcp_agent_name(cls, name: str, user_id: str):
        async with async_session_getter() as session:
            sql = select(MCPAgentTable).where(and_(MCPAgentTable.name.like(f'%{name}%'),
                                                   MCPAgentTable.user_id == user_id))
            result = await session.exec(sql)
            return result.all()

    @classmethod
    async def get_mcp_agent_by_user_id(cls, user_id: int):
        async with async_session_getter() as session:
            sql = select(MCPAgentTable).where(MCPAgentTable.user_id == user_id)
            result = await session.exec(sql)
            return result.all()

    @classmethod
    async def select_mcp_agent_by_id(cls, agent_id):
        async with async_session_getter() as session:
            sql = select(MCPAgentTable).where(MCPAgentTable.id == agent_id)
            result = await session.exec(sql)
            return result.first()

    @classmethod
    async def update_mcp_agent_by_id(cls, id: str, name: str, description: str, knowledges_id: List[str],
                               logo: str, llm_id: str, mcp_servers_id: List[str], enable_memory: bool):
        async with async_session_getter() as session:
            # 构建 update 语句
            update_values = {}
            if name is not None:
                update_values['name'] = name
            if description is not None:
                update_values['description'] = description
            if llm_id is not None:
                update_values['llm_id'] = llm_id
            if mcp_servers_id is not None:
                update_values['mcp_servers_id'] = mcp_servers_id
            if knowledges_id is not None:
                update_values['knowledges_id'] = knowledges_id
            if enable_memory:
                update_values['enable_memory'] = enable_memory

            if logo is not None:
                # 删除agent的logo地址
                agent_logo = await cls._get_logo_by_id(id)
                delete_img(logo=agent_logo)
                update_values['logo'] = logo

            sql = update(MCPAgentTable).where(MCPAgentTable.id == id).values(**update_values)
            await session.exec(sql)
            await session.commit()
