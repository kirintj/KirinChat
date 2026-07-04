from datetime import datetime
from typing import List, Optional

from sqlmodel import Field, select, Session, delete
from kirinchat.database.session import async_session_getter
from kirinchat.database.models.role import AdminRole
from kirinchat.database.models.user_role import UserRoleBase, UserRole


class UserRoleDao(UserRoleBase):

    @classmethod
    async def get_user_roles(cls, user_id: str) -> List[UserRole]:
        async with async_session_getter() as session:
            result = await session.exec(select(UserRole).where(UserRole.user_id == user_id))
            return result.all()

    @classmethod
    async def get_roles_user(cls, role_ids: List[str], page: int = 0, limit: int = 0) -> List[UserRole]:
        """
        获取角色对应的用户
        """
        async with async_session_getter() as session:
            statement = select(UserRole).where(UserRole.role_id.in_(role_ids))
            if page and limit:
                statement = statement.offset((page - 1) * limit).limit(limit)
            result = await session.exec(statement)
            return result.all()

    @classmethod
    async def get_admins_user(cls) -> List[UserRole]:
        """
        获取所有超级管理的账号
        """
        async with async_session_getter() as session:
            statement = select(UserRole).where(UserRole.role_id == AdminRole)
            result = await session.exec(statement)
            return result.all()

    @classmethod
    async def set_admin_user(cls, user_id: str) -> UserRole:
        """
        设置用户为超级管理员
        """
        async with async_session_getter() as session:
            user_role = UserRole(user_id=user_id, role_id=AdminRole)
            session.add(user_role)
            await session.commit()
            await session.refresh(user_role)
            return user_role

    @classmethod
    async def add_user_roles(cls, user_id: str, role_ids: List[str]) -> List[UserRole]:
        """
        给用户批量添加角色
        """
        async with async_session_getter() as session:
            user_roles = [UserRole(user_id=user_id, role_id=role_id) for role_id in role_ids]
            session.add_all(user_roles)
            await session.commit()
            return user_roles

    @classmethod
    async def delete_user_roles(cls, user_id: str, role_ids: List[str]) -> None:
        """
        将用户从某些角色中移除
        """
        async with async_session_getter() as session:
            statement = delete(UserRole).where(UserRole.user_id == user_id).where(UserRole.role_id.in_(role_ids))
            await session.exec(statement)
            await session.commit()
