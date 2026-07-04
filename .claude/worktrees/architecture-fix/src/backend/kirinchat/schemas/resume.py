from typing import Optional, Dict, List
from pydantic import BaseModel, Field


class ResumeInfoResp(BaseModel):
    """简历简要信息"""
    id: str = Field(..., description="简历ID")
    filename: str = Field(..., description="文件名")
    file_size: int = Field(..., description="文件大小")
    content_type: str = Field(..., description="MIME类型")
    status: str = Field(..., description="状态")
    score: Optional[float] = Field(default=None, description="评分")
    create_time: Optional[str] = Field(default=None, description="创建时间")


class ResumeDetailResp(BaseModel):
    """简历详情"""
    id: str = Field(..., description="简历ID")
    filename: str = Field(..., description="文件名")
    file_size: int = Field(..., description="文件大小")
    content_type: str = Field(..., description="MIME类型")
    status: str = Field(..., description="状态")
    score: Optional[float] = Field(default=None, description="评分")
    raw_text: Optional[str] = Field(default="", description="解析文本")
    analysis_result: Optional[Dict] = Field(default=None, description="分析结果")
    error_message: Optional[str] = Field(default="", description="错误信息")
    create_time: Optional[str] = Field(default=None, description="创建时间")


class ResumeStatusResp(BaseModel):
    """简历分析状态"""
    id: str = Field(..., description="简历ID")
    status: str = Field(..., description="状态")
    score: Optional[float] = Field(default=None, description="评分")


class ResumeListResp(BaseModel):
    """简历列表"""
    resumes: List[ResumeInfoResp] = Field(default=[], description="简历列表")
