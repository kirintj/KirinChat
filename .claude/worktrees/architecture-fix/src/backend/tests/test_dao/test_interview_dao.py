import pytest
import asyncio
from kirinchat.database.dao.interview import InterviewSessionDao
from kirinchat.database.models.interview import InterviewSessionTable


@pytest.mark.asyncio
async def test_create_session_async():
    """Test that create_session uses async session correctly."""
    test_session = InterviewSessionTable(
        user_id="test_user",
        skill_id="test_skill",
        status="created",
    )

    result = await InterviewSessionDao.create_session(test_session)

    assert result is not None
    assert result.user_id == "test_user"
    assert result.id is not None


@pytest.mark.asyncio
async def test_select_session_by_id_async():
    """Test that select_session_by_id uses async session correctly."""
    test_session = InterviewSessionTable(
        user_id="test_user_2",
        skill_id="test_skill_2",
        status="created",
    )

    created = await InterviewSessionDao.create_session(test_session)
    result = await InterviewSessionDao.select_session_by_id(created.id)

    assert result is not None
    assert result.id == created.id
    assert result.user_id == "test_user_2"
