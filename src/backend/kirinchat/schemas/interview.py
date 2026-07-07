from typing import Dict, List, Optional
from datetime import datetime
from pydantic import BaseModel, Field


# ==================== Request Schemas ====================


class InterviewStartReq(BaseModel):
    """开始面试请求"""
    skill_id: str = Field(..., description="技能ID")
    difficulty: str = Field(default="MEDIUM", description="难度: EASY / MEDIUM / HARD")
    question_count: int = Field(default=10, ge=1, le=50, description="题目数量")


class InterviewAnswerReq(BaseModel):
    """提交答案请求"""
    session_id: str = Field(..., description="面试会话ID")
    question_id: str = Field(..., description="题目ID")
    answer: str = Field(..., description="用户答案")


class InterviewCompleteReq(BaseModel):
    """完成面试请求"""
    session_id: str = Field(..., description="面试会话ID")


# ==================== Response Schemas ====================


class SkillCategoryResp(BaseModel):
    """Skill 分类响应"""
    key: str = Field(..., description="分类标识")
    label: str = Field(..., description="分类显示名称")
    priority: int = Field(..., description="优先级排序")


class SkillInfoResp(BaseModel):
    """Skill 简要信息"""
    id: str = Field(..., description="技能ID")
    name: str = Field(..., description="技能名称")
    description: str = Field(..., description="技能描述")
    icon: str = Field(default="", description="图标")
    categories: List[str] = Field(default=[], description="所属分类列表")


class QuestionResp(BaseModel):
    """题目响应"""
    id: str = Field(..., description="题目ID")
    type: str = Field(..., description="题目类型")
    category: str = Field(..., description="题目分类")
    content: str = Field(..., description="题目内容")
    user_answer: Optional[str] = Field(None, description="用户答案（未答则为 null）")


class InterviewStartResp(BaseModel):
    """开始面试响应"""
    session_id: str = Field(..., description="面试会话ID")
    first_question: QuestionResp = Field(..., description="第一道题目")


class InterviewAnswerResp(BaseModel):
    """提交答案响应"""
    next_question: Optional[QuestionResp] = Field(None, description="下一题，若无则表示已完成所有题目")
    is_completed: bool = Field(default=False, description="是否已完成所有题目")


class InterviewSessionResp(BaseModel):
    """面试会话响应"""
    id: str = Field(..., description="会话ID")
    skill_id: str = Field(..., description="技能ID")
    status: str = Field(..., description="会话状态")
    difficulty: Optional[str] = Field(None, description="难度等级")
    progress: Dict[str, int] = Field(default={}, description="进度信息")
    skill_name: str = Field(default="", description="技能名称")
    total_score: Optional[float] = Field(None, description="总分（已评估时有值）")
    create_time: Optional[datetime] = Field(None, description="创建时间")


class InterviewSessionDetailResp(BaseModel):
    """会话详情响应"""
    session: InterviewSessionResp = Field(..., description="会话信息")
    questions: List[QuestionResp] = Field(default=[], description="题目列表")


class InterviewCompleteResp(BaseModel):
    """完成面试响应"""
    evaluation_id: str = Field(default="", description="评估报告ID（异步评估时为空）")
    status: str = Field(..., description="评估状态")


class QuestionDetailResp(BaseModel):
    """单题评估详情响应"""
    question_id: str = Field(..., description="题目ID")
    session_id: str = Field(default="", description="所属会话ID")
    content: str = Field(default="", description="题目内容")
    user_answer: Optional[str] = Field(None, description="用户答案")
    type: str = Field(default="MAIN", description="题目类型")
    category: str = Field(default="", description="题目分类")
    score: int = Field(default=0, description="得分 (0-10)")
    feedback: str = Field(default="", description="AI 反馈")
    reference_answer: str = Field(default="", description="参考答案")
    skill_name: str = Field(default="", description="技能名称")


class QuestionDetailItem(BaseModel):
    """评估报告中的逐题摘要项"""
    question_id: str = Field(..., description="题目ID")
    content: str = Field(default="", description="题目内容")
    user_answer: Optional[str] = Field(None, description="用户答案")
    type: str = Field(default="MAIN", description="题目类型")
    category: str = Field(default="", description="题目分类")
    score: int = Field(default=0, description="得分 (0-10)")
    feedback: str = Field(default="", description="AI 反馈")
    reference_answer: str = Field(default="", description="参考答案")


class EvaluationReportResp(BaseModel):
    """评估报告响应"""
    id: str = Field(..., description="评估ID")
    total_score: float = Field(..., description="总分")
    category_scores: Dict[str, float] = Field(default={}, description="各分类得分")
    summary: str = Field(..., description="总结")
    strengths: List[str] = Field(default=[], description="优势列表")
    improvements: List[str] = Field(default=[], description="待改进列表")
    question_details: List[QuestionDetailItem] = Field(default=[], description="逐题详情")


class InterviewHistoryResp(BaseModel):
    """面试历史响应"""
    sessions: List[InterviewSessionResp] = Field(default=[], description="会话列表")
    total: int = Field(default=0, description="总记录数")
    page: int = Field(default=1, description="当前页码")
    page_size: int = Field(default=20, description="每页条数")


class SkillDetailResp(BaseModel):
    """Skill 详情响应"""
    skill: SkillInfoResp = Field(..., description="技能信息")
    categories: List[SkillCategoryResp] = Field(default=[], description="所属分类详情")
    references: List[str] = Field(default=[], description="参考资源列表")


class SkillListResp(BaseModel):
    """Skill 列表响应"""
    skills: List[SkillInfoResp] = Field(default=[], description="技能列表")
