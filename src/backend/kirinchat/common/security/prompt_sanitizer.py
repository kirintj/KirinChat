import re
from loguru import logger


class PromptSanitizer:
    """清洗用户输入，防止 Prompt 注入。"""

    SUSPICIOUS_PATTERNS = [
        # ---- 原有规则 ----
        r"忽略.*(?:上面|之前|以上).*(?:指令|提示|规则)",
        r"ignore.*(?:above|previous).*(?:instructions|rules)",
        r"system\s*prompt",
        r"你是一个.*(?:而不是|不要)",
        r"(?:forget|disregard).*(?:instructions|rules)",
        r"new\s*instructions",
        # ---- 新增：角色扮演攻击 ----
        r"现在你是(?:一个)?(?:AI|助手|机器人|人工智能)",
        r"假装你是(?:一个)?(?:AI|助手|机器人|人工智能)",
        r"扮演(?:一个)?(?:AI|助手|机器人|人工智能)",
        r"you\s+are\s+now\s+(?:a|an)\s+(?:AI|assistant|bot|robot)",
        # ---- 新增：编码绕过攻击 ----
        r"(?:base64|hex|unicode|url)\s*(?:encode|decode)\s*(?:this|the)",
        r"(?:编码|解码)\s*(?:这段|这个|以下)",
        # ---- 新增：指令提取攻击 ----
        r"(?:显示|输出|打印|show|print|reveal|expose)\s*(?:你的|your)\s*(?:指令|提示|prompt|instructions|system\s*prompt)",
        r"(?:告诉我|tell\s+me)\s*(?:你的|your)\s*(?:指令|提示|prompt|instructions)",
        # ---- 新增：上下文操纵攻击 ----
        r"(?:对话|conversation|session)\s*(?:重新开始|重置|reset|start\s+over|restart)",
        r"(?:忽略|ignore|forget|discard)\s*(?:之前|previous|above|all|所有|全部)(?:\s+(?:之前|previous|above|all|所有|全部))?\s*(?:的)?(?:对话|conversation|context)",
        # ---- 新增：注入标记攻击 ----
        r"===\s*(?:用户|user)\s*(?:提供的|provided)?\s*(?:内容|content)\s*(?:开始|start)\s*===",
        r"===\s*(?:系统|system)\s*(?:指令|instruction)\s*(?:开始|start)\s*===",
    ]

    MAX_INPUT_LENGTH = 50000

    # 白名单短语：当输入仅包含这些常见正常用法时不判定为攻击
    WHITELIST_PHRASES = [
        "base64 编码",
        "reset password",
    ]

    @classmethod
    def _is_whitelisted(cls, text: str) -> bool:
        """检查文本是否完全匹配白名单短语。"""
        lowered = text.lower().strip()
        for phrase in cls.WHITELIST_PHRASES:
            if lowered == phrase.lower():
                return True
        return False

    @classmethod
    def is_safe(cls, user_input: str | None) -> bool:
        """检查用户输入是否安全（不包含 Prompt 注入模式）。

        Args:
            user_input: 原始输入文本

        Returns:
            True 表示安全，False 表示检测到可疑模式
        """
        if not user_input:
            return True

        if cls._is_whitelisted(user_input):
            return True

        text = user_input[: cls.MAX_INPUT_LENGTH]

        for pattern in cls.SUSPICIOUS_PATTERNS:
            if re.search(pattern, text, re.IGNORECASE):
                logger.warning("Prompt injection detected by is_safe: %s", pattern)
                return False

        return True

    @classmethod
    def sanitize(cls, user_input: str | None, *, block: bool = False) -> str:
        """清洗用户输入。

        Args:
            user_input: 原始输入文本
            block: 为 True 时检测到注入模式则抛出 ValueError 拒绝请求
        """
        if not user_input:
            return ""

        text = user_input[: cls.MAX_INPUT_LENGTH]

        for pattern in cls.SUSPICIOUS_PATTERNS:
            if re.search(pattern, text, re.IGNORECASE):
                logger.warning("Suspicious prompt pattern detected: %s", pattern)
                if block:
                    raise ValueError("检测到不安全的输入内容，请移除指令性文字后重试")

        text = text.replace("=== 用户提供的内容开始 ===", "")
        text = text.replace("=== 用户提供的内容结束 ===", "")

        return text.strip()
