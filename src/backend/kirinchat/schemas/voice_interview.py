from typing import Optional, List, Dict, Any
from pydantic import BaseModel


class VoiceInterviewCreateReq(BaseModel):
    skill_id: str
    difficulty: str = "medium"
    resume_id: Optional[str] = None
    planned_duration: int = 30
    phases: Dict[str, bool] = {
        "intro": True, "tech": True, "project": True, "hr": True
    }


class VoiceInterviewSubmitReq(BaseModel):
    text: str


class VoiceInterviewSessionResp(BaseModel):
    id: str
    skill_id: str
    difficulty: str
    resume_id: Optional[str]
    planned_duration: int
    current_phase: str
    status: str
    evaluate_status: str
    phases_enabled: Dict[str, bool]
    start_time: Optional[str]
    end_time: Optional[str]
    actual_duration: Optional[int]


class VoiceInterviewMessageResp(BaseModel):
    id: str
    session_id: str
    phase: str
    user_text: Optional[str]
    ai_text: Optional[str]
    sequence_num: int
    timestamp: Optional[str]


class VoiceInterviewEvaluationResp(BaseModel):
    id: str
    session_id: str
    overall_score: Optional[float]
    overall_feedback: Optional[str]
    category_scores: Optional[Dict[str, Any]]
    question_evaluations: Optional[List[Any]]
    strengths: Optional[List[str]]
    improvements: Optional[List[str]]
    reference_answers: Optional[List[Any]]
    interviewer_role: Optional[str]
    interview_date: Optional[str]


class VoiceInterviewSessionListResp(BaseModel):
    sessions: List[VoiceInterviewSessionResp]
    total: int
