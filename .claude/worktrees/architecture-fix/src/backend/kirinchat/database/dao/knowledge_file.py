from kirinchat.database.session import async_session_getter
from kirinchat.database.models.knowledge_file import KnowledgeFileTable
from sqlmodel import Session, select, delete, update


class KnowledgeFileDao:

    @classmethod
    async def create_knowledge_file(cls, knowledge_file_id, file_name, knowledge_id, user_id, oss_url, file_size_bytes):
        async with async_session_getter() as session:
            session.add(KnowledgeFileTable(file_name=file_name, knowledge_id=knowledge_id, file_size=file_size_bytes,
                                           user_id=user_id, oss_url=oss_url, id=knowledge_file_id))
            await session.commit()

    @classmethod
    async def delete_knowledge_file(cls, knowledge_file_id):
        async with async_session_getter() as session:
            sql = delete(KnowledgeFileTable).where(KnowledgeFileTable.id == knowledge_file_id)
            await session.exec(sql)
            await session.commit()

    @classmethod
    async def select_knowledge_file(cls, knowledge_id):
        async with async_session_getter() as session:
            sql = select(KnowledgeFileTable).where(KnowledgeFileTable.knowledge_id == knowledge_id)
            results = await session.exec(sql)
            return results.all()

    @classmethod
    async def select_knowledge_file_by_id(cls, knowledge_file_id):
        async with async_session_getter() as session:
            sql = select(KnowledgeFileTable).where(KnowledgeFileTable.id == knowledge_file_id)
            results = await session.exec(sql)
            return results.first()

    @classmethod
    async def update_parsing_status(cls, knowledge_file_id, status):
        async with async_session_getter() as session:
            update_values = {"status": status}
            sql = update(KnowledgeFileTable).where(KnowledgeFileTable.id == knowledge_file_id).values(**update_values)
            await session.exec(sql)
            await session.commit()
