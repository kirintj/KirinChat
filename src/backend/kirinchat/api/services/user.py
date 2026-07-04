"""
用户服务模块
提供用户认证、角色管理、密码处理等功能
"""
import json
import random
import hashlib
from base64 import b64decode
from typing import List, Union

import rsa
from fastapi import Request, Depends, HTTPException

from kirinchat.auth import AuthJWT
from kirinchat.services.storage import storage_client
from kirinchat.services.redis import redis_client
from kirinchat.database.dao.user_role import UserRoleDao
from kirinchat.database.models.role import AdminRole
from kirinchat.api.errcode.user import UserNameAlreadyExistError
from kirinchat.settings import app_settings
from kirinchat.utils.hash import md5_hash
from kirinchat.database.models.user import UserTable
from kirinchat.database.dao.user import UserDao
from kirinchat.utils.constants import RSA_KEY
from kirinchat.schemas.user import CreateUserReq
from kirinchat.utils.JWT import ACCESS_TOKEN_EXPIRE_TIME

# 常量定义
ADMIN_ROLE_ID = "1"
ADMIN_ROLE_NAME = "admin"
USER_ICONS_PATH = "icons/user"


class UserPayload:
    """
    用户载荷类，用于JWT认证后的用户信息存储
    包含用户ID、角色信息和用户名
    """

    def __init__(self, **kwargs):
        self.user_id: str = kwargs.get('user_id')
        self.user_role: Union[str, List[str]] = kwargs.get('role')
        self.user_name: str = kwargs.get('user_name')

        # 非管理员用户，需要获取他的角色列表
        if self.user_role != ADMIN_ROLE_NAME:
            roles = UserRoleDao.get_user_roles(self.user_id)
            self.user_role = [one.role_id for one in roles]

    def is_admin(self) -> bool:
        """检查是否为管理员"""
        if self.user_role == ADMIN_ROLE_NAME:
            return True
        if isinstance(self.user_role, list):
            return AdminRole in self.user_role
        return False


class UserService:
    """用户服务类，提供用户相关业务逻辑"""

    @classmethod
    def decrypt_md5_password(cls, password: str) -> str:
        """
        解密RSA加密的密码并进行MD5哈希
        如果存在RSA私钥则解密，否则直接进行MD5哈希
        """
        value = redis_client.get(RSA_KEY)
        if value:
            private_key = value[1]
            decrypted = rsa.decrypt(b64decode(password), private_key).decode('utf-8')
            return md5_hash(decrypted)
        return md5_hash(password)

    @classmethod
    def encrypt_sha256_password(cls, password: str) -> str:
        """
        使用SHA-256算法加密密码
        """
        sha256 = hashlib.sha256()
        sha256.update(password.encode('utf-8'))
        return sha256.hexdigest()

    @classmethod
    def verify_password(cls, password: str, encrypted_password: str) -> bool:
        """验证密码是否匹配"""
        return cls.encrypt_sha256_password(password) == encrypted_password

    @classmethod
    def create_user(cls, request: Request, login_user: UserPayload, req_data: CreateUserReq):
        """
        创建新用户

        Args:
            request: HTTP请求对象
            login_user: 当前登录用户
            req_data: 创建用户请求数据

        Raises:
            UserNameAlreadyExistError: 用户名已存在
        """
        exists_user = UserDao.get_user_by_username(req_data.user_name)
        if exists_user:
            raise UserNameAlreadyExistError.http_exception()

        user = UserTable(
            user_name=req_data.user_name,
            user_password=cls.decrypt_md5_password(req_data.password),
        )
        return UserDao.add_user_and_default_role(
            user_name=user.user_name,
            user_password=user.user_password
        )

    @classmethod
    def _build_avatar_urls(cls, file_paths: List[str]) -> List[str]:
        """
        构建完整的头像URL列表

        Args:
            file_paths: 相对路径列表

        Returns:
            完整URL列表
        """
        base_url = app_settings.storage.active.base_url.rstrip('/')
        return [f"{base_url}/{path.lstrip('/')}" for path in file_paths]

    @classmethod
    def get_random_user_avatar(cls) -> str:
        """获取随机用户头像URL"""
        file_paths = storage_client.list_files_in_folder(USER_ICONS_PATH)
        avatars = cls._build_avatar_urls(file_paths)
        return random.choice(avatars) if avatars else ""

    @classmethod
    def get_available_avatars(cls) -> List[str]:
        """获取所有可用头像URL列表"""
        file_paths = storage_client.list_files_in_folder(USER_ICONS_PATH)
        return cls._build_avatar_urls(file_paths)

    @classmethod
    def get_user_info_by_id(cls, user_id: str) -> dict:
        """根据用户ID获取用户信息字典"""
        user_info = UserDao.get_user(user_id)
        return user_info.to_dict()

    @classmethod
    def update_user_info(cls, user_id: str, user_avatar: str, user_description: str) -> None:
        """更新用户信息"""
        UserDao.update_user_info(user_id, user_avatar, user_description)

    @classmethod
    def get_user_id_by_name(cls, user_name: str) -> str:
        """根据用户名获取用户ID"""
        user = UserDao.get_user_by_username(user_name)
        return user.user_id


def get_login_user(request: Request, authorize: AuthJWT = Depends()) -> UserPayload:
    """
    获取当前登录的用户

    - 白名单路径：直接返回Admin
    - 非白名单路径：执行JWT验证

    Raises:
        HTTPException: 认证失败时抛出401错误
    """
    if request.state.is_whitelisted:
        return UserPayload(user_id="1", user_name="Admin")

    try:
        authorize.jwt_required()
        current_user = json.loads(authorize.get_jwt_subject())
        return UserPayload(**current_user)
    except Exception as e:
        raise HTTPException(status_code=401, detail="Invalid authentication credentials")


def get_user_role(db_user: UserTable) -> Union[str, List[str]]:
    """
    获取用户角色

    - 管理员返回 'admin' 字符串
    - 普通用户返回角色ID列表
    """
    user_roles = UserRoleDao.get_user_roles(db_user.user_id)
    role_ids = []

    for user_role in user_roles:
        if user_role.role_id == ADMIN_ROLE_ID:
            return ADMIN_ROLE_NAME
        role_ids.append(user_role.role_id)

    return role_ids


def get_user_jwt(db_user: UserTable) -> tuple:
    """
    获取用户JWT令牌

    Returns:
        (access_token, refresh_token, role) 元组
    """
    role = get_user_role(db_user)
    payload = {
        'user_name': db_user.user_name,
        'user_id': db_user.user_id,
        'role': role
    }

    access_token = AuthJWT().create_access_token(
        subject=json.dumps(payload),
        expires_time=ACCESS_TOKEN_EXPIRE_TIME
    )
    refresh_token = AuthJWT().create_refresh_token(subject=db_user.user_name)

    return access_token, refresh_token, role
