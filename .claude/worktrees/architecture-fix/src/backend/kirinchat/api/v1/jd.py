from loguru import logger
from fastapi import APIRouter, Depends

from kirinchat.api.services.jd import JdService
from kirinchat.schemas.jd import (
    JdParseReq,
    JdParseResp,
    JdCreateSkillReq,
    JdSkillResp,
)
from kirinchat.api.responses.builder import resp_200, resp_500, UnifiedResponseModel
from kirinchat.api.services.user import UserPayload, get_login_user

router = APIRouter(tags=["JD"])


# ---------------------------------------------------------------------------
# JD endpoints
# ---------------------------------------------------------------------------


@router.post("/jd/parse", response_model=UnifiedResponseModel)
async def parse_jd(
    req: JdParseReq,
    login_user: UserPayload = Depends(get_login_user),
):
    """Parse a JD (Job Description) text and extract structured information."""
    try:
        result = await JdService.parse_jd(req.jd_text)
        return resp_200(data=result.model_dump())
    except ValueError as err:
        logger.warning(f"Parse JD validation error: {err}")
        return resp_500(message=str(err))
    except Exception as err:
        logger.error(f"Parse JD error: {err}")
        return resp_500(message=str(err))


@router.post("/jd/create-skill", response_model=UnifiedResponseModel)
async def create_skill_from_jd(
    req: JdCreateSkillReq,
    login_user: UserPayload = Depends(get_login_user),
):
    """Create a temporary interview skill from parsed JD data."""
    try:
        result = await JdService.create_skill_from_jd(req)
        return resp_200(data=result.model_dump())
    except ValueError as err:
        logger.warning(f"Create skill from JD validation error: {err}")
        return resp_500(message=str(err))
    except Exception as err:
        logger.error(f"Create skill from JD error: {err}")
        return resp_500(message=str(err))
