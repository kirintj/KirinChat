import re
from loguru import logger


class PromptSanitizer:
    """清洗用户输入，防止 Prompt 注入。"""

    SUSPICIOUS_PATTERNS = [
        r"忽略.*(?:上面|之前|以上).*(?:指令|提示|规则)",
        r"ignore.*(?:above|previous).*(?:instructions|rules)",
        r"system\s*prompt",
        r"你是一个.*(?:而不是|不要)",
        r"(?:forget|disregard).*(?:instructions|rules)",
        r"new\s*instructions",
    ]

    MAX_INPUT_LENGTH = 50000

    @classmethod
    def sanitize(cls, user_input: str | None) -> str:
        if not user_input:
            return ""

        text = user_input[: cls.MAX_INPUT_LENGTH]

        for pattern in cls.SUSPICIOUS_PATTERNS:
            if re.search(pattern, text, re.IGNORECASE):
                logger.warning(f"Suspicious prompt pattern detected: {pattern}")

        text = text.replace("=== 用户提供的内容开始 ===", "")
        text = text.replace("=== 用户提供的内容结束 ===", "")

        return text.strip()
