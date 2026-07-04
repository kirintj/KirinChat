import time
from typing import List, Dict, Any, AsyncGenerator

from langchain_core.messages import BaseMessage, HumanMessage, SystemMessage
from loguru import logger

from kirinchat.api.services.interview import InterviewService
from kirinchat.api.services.skill import SkillService
from kirinchat.core.models.manager import ModelManager
from kirinchat.database.models.interview import InterviewQuestionTable


# Difficulty level descriptions for prompt construction
_DIFFICULTY_MAP = {
    "EASY": "初级难度，考察基础概念和核心知识点",
    "MEDIUM": "中级难度，考察理解深度和实际应用能力",
    "HARD": "高级难度，考察综合分析能力、架构设计和边界场景",
}

# Category priority order (lower = higher priority)
_PRIORITY_ORDER = {
    "ALWAYS_ONE": 0,
    "CORE": 1,
    "NORMAL": 2,
}


class InterviewAgent:
    """Interview Agent responsible for interview conversation management, question generation, and follow-ups."""

    def __init__(self, agent_config):
        self.agent_config = agent_config
        self.skill = None
        self.conversation_model = None
        self.current_session_id = None

    async def init_interview_agent(self, skill_id: str):
        """Initialize the interview agent by loading the skill and setting up the LLM.

        Args:
            skill_id: The skill directory name to load.
        """
        self.skill = SkillService.get_skill_by_id(skill_id)
        if self.skill is None:
            raise ValueError(f"Skill not found: {skill_id}")

        self.conversation_model = ModelManager.get_conversation_model()
        logger.info(f"InterviewAgent initialized for skill: {self.skill['name']}")

    async def generate_first_question(self, session_id: str, difficulty: str = "MEDIUM") -> InterviewQuestionTable:
        """Generate the first interview question for a session.

        Fetches existing questions for deduplication, selects a category based
        on priority, builds a prompt with the skill persona and difficulty, calls
        the LLM to generate the question, then saves it and transitions the
        session status to IN_PROGRESS.

        Args:
            session_id: The interview session ID.
            difficulty: One of EASY / MEDIUM / HARD.

        Returns:
            The saved InterviewQuestionTable instance.
        """
        self.current_session_id = session_id

        # Gather existing question topics for deduplication
        existing_questions = await InterviewService.get_session_questions(session_id)
        existing_topics = [q.content for q in existing_questions]

        # Pick the next category to cover
        categories = self.skill.get("categories", [])
        category = self._select_category(categories, existing_questions)

        # Build the prompt
        difficulty_desc = _DIFFICULTY_MAP.get(difficulty, _DIFFICULTY_MAP["MEDIUM"])
        dedup_section = self._get_dedup_prompt(existing_topics)

        category_name = category.get("name", "") if category else ""
        category_desc = category.get("description", "") if category else ""

        prompt = f"""你是一位专业的技术面试官。

# 你的角色
{self.skill.get('persona', '')}

# 任务
请生成一道面试题目。

# 要求
- 分类: {category_name} - {category_desc}
- 难度: {difficulty_desc}
- 只输出题目内容，不要输出答案或其他说明
- 题目应简洁清晰，不超过 3 句话
{dedup_section}"""

        response = await self.conversation_model.ainvoke([HumanMessage(content=prompt)])
        content = response.content if hasattr(response, "content") else str(response)

        # Save the question
        question = InterviewQuestionTable(
            session_id=session_id,
            type="MAIN",
            category=category.get("key", "general") if category else "general",
            content=content.strip(),
        )
        saved_question = await InterviewService.save_question(question)

        # Transition session status
        await InterviewService.update_session_status(session_id, "IN_PROGRESS")

        logger.info(f"First question generated for session {session_id}: {content[:50]}...")
        return saved_question

    async def generate_follow_up(self, session_id: str, original_question: str, user_answer: str) -> InterviewQuestionTable | None:
        """Generate a follow-up question based on the user's answer.

        The LLM decides whether a follow-up is needed. If so, the follow-up
        question is saved and returned; otherwise returns None.

        Args:
            session_id: The interview session ID.
            original_question: The text of the original question.
            user_answer: The user's answer to the original question.

        Returns:
            A saved InterviewQuestionTable of type FOLLOW_UP, or None.
        """
        self.current_session_id = session_id

        prompt = f"""你是一位专业的技术面试官。

# 你的角色
{self.skill.get('persona', '')}

# 任务
候选人回答了以下面试题目，请判断是否需要追问。

# 原始题目
{original_question}

# 候选人回答
{user_answer}

# 规则
1. 如果回答过于简短、有明显遗漏、或存在可深挖的点，请生成一道追问
2. 如果回答已经完整且准确，回复 "NO_FOLLOW_UP"
3. 追问应引导候选人深入思考，不要重复原始题目
4. 只输出追问内容或 "NO_FOLLOW_UP"，不要输出其他说明"""

        response = await self.conversation_model.ainvoke([HumanMessage(content=prompt)])
        content = response.content if hasattr(response, "content") else str(response)
        content = content.strip()

        if content == "NO_FOLLOW_UP":
            logger.info(f"No follow-up needed for session {session_id}")
            return None

        question = InterviewQuestionTable(
            session_id=session_id,
            type="FOLLOW_UP",
            category="follow_up",
            content=content,
        )
        saved_question = await InterviewService.save_question(question)

        logger.info(f"Follow-up question generated for session {session_id}: {content[:50]}...")
        return saved_question

    async def generate_next_question(self, session_id: str, difficulty: str = "MEDIUM") -> InterviewQuestionTable | None:
        """Generate the next main question in an ongoing interview session.

        Checks whether the question limit has been reached (completing the
        session if so), selects an uncovered category with highest priority,
        and generates a new question.

        Args:
            session_id: The interview session ID.
            difficulty: One of EASY / MEDIUM / HARD.

        Returns:
            A saved InterviewQuestionTable, or None if the session is complete.
        """
        self.current_session_id = session_id

        session = await InterviewService.get_session(session_id)
        if session is None:
            raise ValueError(f"Session not found: {session_id}")

        # Check if we've reached the question limit
        existing_questions = await InterviewService.get_session_questions(session_id)
        main_questions = [q for q in existing_questions if q.type == "MAIN"]

        if len(main_questions) >= session.question_count:
            await InterviewService.update_session_status(session_id, "COMPLETED")
            logger.info(f"Session {session_id} completed: reached question limit")
            return None

        # Collect existing topics for deduplication
        existing_topics = [q.content for q in main_questions]

        # Gather covered categories for smart selection
        covered_categories = set(q.category for q in main_questions)

        # Select category, preferring uncovered ones
        categories = self.skill.get("categories", [])
        category = self._select_category(categories, existing_questions)

        # Build the prompt
        difficulty_desc = _DIFFICULTY_MAP.get(difficulty, _DIFFICULTY_MAP["MEDIUM"])
        dedup_section = self._get_dedup_prompt(existing_topics)

        category_name = category.get("name", "") if category else ""
        category_desc = category.get("description", "") if category else ""

        prompt = f"""你是一位专业的技术面试官。

# 你的角色
{self.skill.get('persona', '')}

# 任务
请生成下一道面试题目。这是第 {len(main_questions) + 1}/{session.question_count} 题。

# 已考察的分类
{', '.join(covered_categories) if covered_categories else '暂无'}

# 要求
- 分类: {category_name} - {category_desc}
- 难度: {difficulty_desc}
- 只输出题目内容，不要输出答案或其他说明
- 题目应简洁清晰，不超过 3 句话
{dedup_section}"""

        response = await self.conversation_model.ainvoke([HumanMessage(content=prompt)])
        content = response.content if hasattr(response, "content") else str(response)

        question = InterviewQuestionTable(
            session_id=session_id,
            type="MAIN",
            category=category.get("key", "general") if category else "general",
            content=content.strip(),
        )
        saved_question = await InterviewService.save_question(question)

        logger.info(f"Next question generated for session {session_id} ({len(main_questions) + 1}/{session.question_count}): {content[:50]}...")
        return saved_question

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _select_category(self, categories: list, existing_questions: list) -> dict | None:
        """Select the next category based on priority and coverage.

        Priority order:
        1. ALWAYS_ONE categories not yet covered
        2. CORE categories not yet covered
        3. NORMAL categories not yet covered
        4. Any category (fallback)

        Args:
            categories: List of category dicts from the skill definition.
            existing_questions: List of existing InterviewQuestionTable instances.

        Returns:
            The selected category dict, or None if no categories exist.
        """
        if not categories:
            return None

        covered_keys = set(q.category for q in existing_questions if q.type == "MAIN")

        # Sort by priority
        sorted_cats = sorted(
            categories,
            key=lambda c: _PRIORITY_ORDER.get(c.get("priority", "NORMAL"), 99),
        )

        # First pass: find uncovered categories in priority order
        for cat in sorted_cats:
            if cat.get("key") not in covered_keys:
                return cat

        # All categories covered; return the first (highest priority) for variety
        return sorted_cats[0]

    @staticmethod
    def _get_dedup_prompt(existing_topics: list) -> str:
        """Build a deduplication instruction section for the prompt.

        Args:
            existing_topics: List of existing question content strings.

        Returns:
            A formatted string to append to the prompt, or empty string.
        """
        if not existing_topics:
            return ""

        topics_text = "\n".join(f"  - {t}" for t in existing_topics)
        return f"""

# 已出过的题目（请避免重复）
{topics_text}"""

    # ------------------------------------------------------------------
    # Standard agent interface (duck-typing compatibility)
    # ------------------------------------------------------------------

    async def astream(self, messages: List[BaseMessage]) -> AsyncGenerator[Dict[str, Any], None]:
        """Streaming call following the project agent convention.

        Wraps messages with the skill persona as a system prompt, then streams
        the LLM response.

        Args:
            messages: List of BaseMessage objects.

        Yields:
            Dict chunks with 'type' and 'data' keys.
        """
        if not self.skill:
            raise RuntimeError("InterviewAgent not initialized. Call init_interview_agent() first.")

        wrapped = self._wrap_with_persona(messages)
        response_content = ""

        try:
            async for chunk in self.conversation_model.astream(wrapped):
                if chunk.content:
                    response_content += chunk.content
                    yield {
                        "type": "response_chunk",
                        "timestamp": time.time(),
                        "data": {
                            "chunk": chunk.content,
                            "accumulated": response_content,
                        },
                    }
        except Exception as err:
            logger.error(f"InterviewAgent stream error: {err}")
            yield {
                "type": "response_chunk",
                "timestamp": time.time(),
                "data": {
                    "chunk": "抱歉，处理过程中出现了错误，请重试。",
                    "accumulated": response_content,
                },
            }

    async def ainvoke(self, messages: List[BaseMessage]) -> str:
        """Non-streaming call following the project agent convention.

        Args:
            messages: List of BaseMessage objects.

        Returns:
            The full response content as a string.
        """
        if not self.skill:
            raise RuntimeError("InterviewAgent not initialized. Call init_interview_agent() first.")

        wrapped = self._wrap_with_persona(messages)
        response = await self.conversation_model.ainvoke(wrapped)
        return response.content if hasattr(response, "content") else str(response)

    def _wrap_with_persona(self, messages: List[BaseMessage]) -> List[BaseMessage]:
        """Prepend the skill persona as a system message if not already present.

        Args:
            messages: Original message list.

        Returns:
            A new list with a SystemMessage prepended (unless one already exists).
        """
        persona = self.skill.get("persona", "")
        if not persona:
            return messages

        if messages and isinstance(messages[0], SystemMessage):
            return messages

        return [SystemMessage(content=persona)] + list(messages)
