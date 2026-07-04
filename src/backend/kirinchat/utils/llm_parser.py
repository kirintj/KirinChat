import json
from typing import Any


def parse_llm_json(content: str) -> dict:
    """从 LLM 响应文本中提取并解析 JSON 对象。

    支持处理以下格式：
    - 纯 JSON 字符串
    - ```json ... ``` 代码块包裹的 JSON
    - 带有前缀文字的 JSON
    """
    text = content.strip()

    if "```" in text:
        parts = text.split("```")
        for part in parts:
            part = part.strip()
            if part.startswith("json"):
                part = part[4:].strip()
            if part.startswith("{"):
                text = part
                break

    return json.loads(text)
