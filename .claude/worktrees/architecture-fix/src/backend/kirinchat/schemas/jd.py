from typing import List
from pydantic import BaseModel, Field


class JdParseReq(BaseModel):
    """JD 解析请求"""
    jd_text: str = Field(..., min_length=10, max_length=10000, description="职位描述文本")


class JdCategoryResp(BaseModel):
    """JD 分类"""
    key: str = Field(..., description="分类标识")
    label: str = Field(..., description="分类名称")
    priority: str = Field(default="CORE", description="优先级")
    keywords: List[str] = Field(default=[], description="关键词")


class JdParseResp(BaseModel):
    """JD 解析结果"""
    company: str = Field(..., description="公司名称")
    position: str = Field(..., description="职位名称")
    experience_required: str = Field(..., description="经验要求")
    categories: List[JdCategoryResp] = Field(default=[], description="技术分类")
    summary: str = Field(..., description="职位概要")


class JdCreateSkillReq(BaseModel):
    """基于 JD 创建 Skill 请求"""
    company: str = Field(..., description="公司名称")
    position: str = Field(..., description="职位名称")
    experience_required: str = Field(default="", description="经验要求")
    categories: List[JdCategoryResp] = Field(default=[], description="技术分类")
    summary: str = Field(default="", description="职位概要")


class JdSkillResp(BaseModel):
    """JD 创建的 Skill 响应"""
    skill_id: str = Field(..., description="Skill ID")
    name: str = Field(..., description="Skill 名称")
    description: str = Field(..., description="Skill 描述")
    categories: List[str] = Field(default=[], description="分类列表")
