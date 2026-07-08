import os
from loguru import  logger
from pydantic import BaseModel, Field

from kirinchat.settings import app_settings
from datetime import datetime, timedelta, timezone

class ImportedConfigInfo(BaseModel):
    name: str
    url: str
    type: str = "sse"
    headers: dict | None = None

def parse_imported_config(imported_config):
    name, info = next(iter(imported_config.get("mcpServers", {}).items()))

    return ImportedConfigInfo(
        name=name,
        url=info.get("url"),
        type=info.get("type"),
        headers=info.get("headers")
    )


def build_completion_system_prompt(system_prompt, history_summary, long_term_memory):
    if "{history}" in system_prompt:
        system_prompt = system_prompt.format(history=history_summary)
    else:
        system_prompt += f"\n📜 对话历史\n{'-' * 20}\n{history_summary}"

    if long_term_memory:
        system_prompt += f"\n\n🧠 长期记忆\n{'-' * 20}\n{long_term_memory}"

    return system_prompt


def get_cache_key(client_id, chat_id):
    return f'{client_id}_{chat_id}'

def build_completion_user_input(user_input, file_url):
    if file_url:
        return f"{user_input}, 上传的文件链接：{file_url}"
    else:
        return user_input

def get_now_beijing_time(delta: int = 0):

    # 设置北京时间时区（东八区）
    beijing_tz = timezone(timedelta(hours=8 + delta))

    # 获取当前时间
    now = datetime.now(beijing_tz)

    # 格式化输出到分钟
    current_time = now.strftime("%Y-%m-%d %H:%M")

    return current_time


def get_provider_from_model(model_name):
    MODEL_PROVIDER_MAP = {
        # 阿里系
        "qwen": "通义千问",
        # OpenAI系
        "gpt": "OpenAI",
        "o1": "OpenAI",
        # 深度求索
        "deepseek": "深度求索",
        # 百度系
        "ernie": "百度文心一言",
        "wenxin": "百度文心一言",
        # 字节系
        "doubao": "字节跳动",
        # 科大讯飞
        "xinghuo": "科大讯飞",
        # Anthropic
        "claude": "Anthropic",
        # 谷歌
        "gemini": "Google",
        "gemma": "Google",
        # 智谱AI
        "glm": "智谱AI",
        # 360
        "kimi": "KiMi",
        # 商汤
        "sensechat": "商汤商量",
        # MiniMax
        "abab": "MiniMax"
    }

    # 空值处理
    if not isinstance(model_name, str) or model_name.strip() == "":
        return "未知服务商"

    # 统一转为小写进行匹配
    model_name_lower = model_name.strip().lower()

    # 遍历匹配规则
    for keyword, provider in MODEL_PROVIDER_MAP.items():
        if keyword in model_name_lower:
            return provider

    # 未匹配到的默认返回
    return "未知服务商"

def delete_img(logo: str):
    try:
        if os.path.exists(logo) and logo != app_settings.default_config.get("agent_logo_url"):
            os.remove(logo)
        else:
            logger.info(f"The logo Path is no exist")
    except Exception as err:
        logger.error(f"delete img appear error: {err}")
