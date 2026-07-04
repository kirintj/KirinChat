import asyncio
import base64
import json
import logging
import time
from datetime import datetime
from typing import Optional

from fastapi import APIRouter, Depends, WebSocket, WebSocketDisconnect

from kirinchat.api.responses.builder import resp_200, resp_500, UnifiedResponseModel
from kirinchat.api.services.user import UserPayload, get_login_user
from kirinchat.api.services.voice_interview import VoiceInterviewService
from kirinchat.api.services.voice_asr import VoiceAsrService
from kirinchat.api.services.voice_tts import VoiceTtsService, pcm_to_wav
from kirinchat.api.services.voice_llm import VoiceLlmService, ChatMessage
from kirinchat.api.services.voice_prompt import VoicePromptService
from kirinchat.schemas.voice_interview import (
    VoiceInterviewCreateReq,
    VoiceInterviewSessionListResp,
)
from kirinchat.settings import app_settings

logger = logging.getLogger(__name__)

router = APIRouter(tags=["VoiceInterview"])

# --- Service singletons ---
_asr_service: Optional[VoiceAsrService] = None
_tts_service: Optional[VoiceTtsService] = None
_llm_service: Optional[VoiceLlmService] = None


def _get_voice_config():
    return getattr(app_settings, "voice_interview", {}) or {}


def _get_asr() -> VoiceAsrService:
    global _asr_service
    if _asr_service is None:
        cfg = _get_voice_config()
        asr_cfg = cfg.get("asr", {})
        _asr_service = VoiceAsrService(
            model=asr_cfg.get("model", "mimo-v2.5-asr"),
            api_key=getattr(app_settings, "mimo_api_key", ""),
            language=asr_cfg.get("language", "zh"),
            base_url=asr_cfg.get("base_url", "https://token-plan-cn.xiaomimimo.com/v1"),
        )
    return _asr_service


def _get_tts() -> VoiceTtsService:
    global _tts_service
    if _tts_service is None:
        cfg = _get_voice_config()
        tts_cfg = cfg.get("tts", {})
        _tts_service = VoiceTtsService(
            model=tts_cfg.get("model", "mimo-v2.5-tts"),
            api_key=getattr(app_settings, "mimo_api_key", ""),
            voice=tts_cfg.get("voice", "冰糖"),
            sample_rate=tts_cfg.get("sample_rate", 24000),
            speech_rate=tts_cfg.get("speech_rate", 1.0),
            volume=tts_cfg.get("volume", 60),
            timeout_seconds=tts_cfg.get("timeout_seconds", 8),
            base_url=tts_cfg.get("base_url", "https://token-plan-cn.xiaomimimo.com/v1"),
        )
    return _tts_service


def _get_llm() -> VoiceLlmService:
    global _llm_service
    if _llm_service is None:
        cfg = _get_voice_config()
        llm_cfg = cfg.get("llm", {})
        _llm_service = VoiceLlmService(
            max_chars=llm_cfg.get("max_chars", 120),
            stream_interval_ms=llm_cfg.get("stream_interval_ms", 180),
            min_chars_delta=llm_cfg.get("min_chars_delta", 12),
        )
    return _llm_service


def _to_session_resp(s) -> dict:
    return {
        "id": s.id,
        "skill_id": s.skill_id,
        "difficulty": s.difficulty,
        "resume_id": s.resume_id,
        "planned_duration": s.planned_duration,
        "current_phase": s.current_phase,
        "status": s.status,
        "evaluate_status": s.evaluate_status,
        "phases_enabled": s.phases_enabled,
        "start_time": s.start_time.isoformat() if s.start_time else None,
        "end_time": s.end_time.isoformat() if s.end_time else None,
        "actual_duration": s.actual_duration,
    }


def _to_message_resp(m) -> dict:
    return {
        "id": m.id,
        "session_id": m.session_id,
        "phase": m.phase,
        "user_text": m.user_text,
        "ai_text": m.ai_text,
        "sequence_num": m.sequence_num,
        "timestamp": m.timestamp.isoformat() if m.timestamp else None,
    }


def _to_eval_resp(e) -> dict:
    return {
        "id": e.id,
        "session_id": e.session_id,
        "overall_score": e.overall_score,
        "overall_feedback": e.overall_feedback,
        "category_scores": e.category_scores,
        "question_evaluations": e.question_evaluations,
        "strengths": e.strengths,
        "improvements": e.improvements,
        "reference_answers": e.reference_answers,
        "interviewer_role": e.interviewer_role,
        "interview_date": e.interview_date.isoformat() if e.interview_date else None,
    }


# --- REST Endpoints ---


@router.post("/voice-interview/sessions", response_model=UnifiedResponseModel)
async def create_session(
    req: VoiceInterviewCreateReq,
    login_user: UserPayload = Depends(get_login_user),
):
    try:
        session = await VoiceInterviewService.create_session(
            user_id=login_user.user_id,
            skill_id=req.skill_id,
            difficulty=req.difficulty,
            planned_duration=req.planned_duration,
            phases=req.phases,
            resume_id=req.resume_id,
        )
        return resp_200(data=_to_session_resp(session))
    except Exception as e:
        return resp_500(message=str(e))


@router.get("/voice-interview/sessions", response_model=UnifiedResponseModel)
async def list_sessions(
    status: Optional[str] = None,
    login_user: UserPayload = Depends(get_login_user),
):
    try:
        sessions = await VoiceInterviewService.list_sessions(login_user.user_id, status)
        data = [_to_session_resp(s) for s in sessions]
        return resp_200(data=VoiceInterviewSessionListResp(sessions=data, total=len(data)).dict())
    except Exception as e:
        return resp_500(message=str(e))


@router.get("/voice-interview/sessions/{session_id}", response_model=UnifiedResponseModel)
async def get_session(
    session_id: str,
    login_user: UserPayload = Depends(get_login_user),
):
    try:
        session = await VoiceInterviewService.get_session(session_id)
        if not session:
            return resp_500(message="Session not found")
        return resp_200(data=_to_session_resp(session))
    except Exception as e:
        return resp_500(message=str(e))


@router.post("/voice-interview/sessions/{session_id}/end", response_model=UnifiedResponseModel)
async def end_session(
    session_id: str,
    login_user: UserPayload = Depends(get_login_user),
):
    try:
        await VoiceInterviewService.end_session(session_id)
        return resp_200(data={"message": "Session ended"})
    except Exception as e:
        return resp_500(message=str(e))


@router.put("/voice-interview/sessions/{session_id}/pause", response_model=UnifiedResponseModel)
async def pause_session(
    session_id: str,
    login_user: UserPayload = Depends(get_login_user),
):
    try:
        await VoiceInterviewService.pause_session(session_id)
        return resp_200(data={"message": "Session paused"})
    except Exception as e:
        return resp_500(message=str(e))


@router.put("/voice-interview/sessions/{session_id}/resume", response_model=UnifiedResponseModel)
async def resume_session(
    session_id: str,
    login_user: UserPayload = Depends(get_login_user),
):
    try:
        await VoiceInterviewService.resume_session(session_id)
        return resp_200(data={"message": "Session resumed"})
    except Exception as e:
        return resp_500(message=str(e))


@router.get("/voice-interview/sessions/{session_id}/messages", response_model=UnifiedResponseModel)
async def get_messages(
    session_id: str,
    login_user: UserPayload = Depends(get_login_user),
):
    try:
        messages = await VoiceInterviewService.get_messages(session_id)
        return resp_200(data=[_to_message_resp(m) for m in messages])
    except Exception as e:
        return resp_500(message=str(e))


@router.get("/voice-interview/sessions/{session_id}/evaluation", response_model=UnifiedResponseModel)
async def get_evaluation(
    session_id: str,
    login_user: UserPayload = Depends(get_login_user),
):
    try:
        evaluation = await VoiceInterviewService.get_evaluation(session_id)
        if not evaluation:
            return resp_200(data=None)
        return resp_200(data=_to_eval_resp(evaluation))
    except Exception as e:
        return resp_500(message=str(e))


@router.post("/voice-interview/sessions/{session_id}/evaluation", response_model=UnifiedResponseModel)
async def trigger_evaluation(
    session_id: str,
    login_user: UserPayload = Depends(get_login_user),
):
    try:
        from kirinchat.common.async_task.voice_interview_tasks import voice_interview_evaluation_task
        voice_interview_evaluation_task.delay(session_id)
        return resp_200(data={"message": "Evaluation task submitted"})
    except ImportError:
        return resp_500(message="Evaluation task module not available yet")
    except Exception as e:
        return resp_500(message=str(e))


# --- WebSocket ---

AI_SPEAK_COOLDOWN_MS = 800
PAUSE_TIMEOUT_MS = 300000
PAUSE_WARNING_MS = 270000


class WsSessionState:
    def __init__(self):
        self.merge_buffer: str = ""
        self.is_processing: bool = False
        self.ai_speaking: bool = False
        self.ai_speak_end_at: float = 0.0
        self.pause_task: Optional[asyncio.Task] = None
        self.last_activity: float = time.time()
        self.warning_sent: bool = False
        self.tts_cancel: asyncio.Event = asyncio.Event()

    def reset_activity(self):
        self.last_activity = time.time()
        self.warning_sent = False


_ws_sessions: dict[str, WsSessionState] = {}


def _ws_get_login_user(websocket: WebSocket) -> Optional[UserPayload]:
    """Validate JWT token from WebSocket query params and return user info.
    Returns None for unauthenticated clients."""
    token = websocket.query_params.get("token") or ""
    if not token:
        return None
    try:
        from kirinchat.auth import AuthJWT
        import json as _json
        authorize = AuthJWT()
        # jwt_required accepts a raw token string passed via WebSocket URL
        authorize.jwt_required("access", token)
        current_user = _json.loads(authorize.get_jwt_subject())
        return UserPayload(**current_user)
    except Exception:
        logger.warning("WebSocket token validation failed")
        return None


@router.websocket("/voice-interview/ws/{session_id}")
async def voice_interview_ws(websocket: WebSocket, session_id: str):
    await websocket.accept()

    # Validate user from WebSocket token
    user = _ws_get_login_user(websocket)
    if not user:
        await websocket.send_json({"type": "error", "message": "Unauthorized"})
        await websocket.close()
        return

    session = await VoiceInterviewService.get_session(session_id)
    if not session:
        await websocket.send_json({"type": "error", "message": "Session not found"})
        await websocket.close()
        return

    # Ensure the session belongs to this user
    if getattr(session, "user_id", None) and session.user_id != user.user_id:
        await websocket.send_json({"type": "error", "message": "Session not found"})
        await websocket.close()
        return

    state = WsSessionState()
    _ws_sessions[session_id] = state

    asr = _get_asr()
    tts = _get_tts()
    llm = _get_llm()

    try:
        await asr.start_session(
            session_id,
            on_partial=lambda text: asyncio.create_task(_send_subtitle(websocket, text, False)),
            on_final=lambda text: asyncio.create_task(_handle_final_stt(websocket, state, text)),
            on_ready=lambda: asyncio.create_task(
                websocket.send_json({"type": "control", "action": "asr_ready"})
            ),
        )
    except Exception as e:
        logger.error("Failed to start ASR for session %s: %s", session_id, e)
        await websocket.send_json({"type": "error", "message": f"ASR init failed: {e}"})
        await websocket.close()
        return

    # Send welcome + opening question if no history
    messages = await VoiceInterviewService.get_messages(session_id)
    if not messages:
        system_prompt = VoicePromptService.build_system_prompt(
            session.skill_id, session.current_phase
        )
        opening = await llm.chat([ChatMessage(role="system", content=system_prompt)])
        await websocket.send_json({"type": "control", "action": "welcome", "message": opening})
        wav = await tts.synthesize_to_wav(opening)
        if wav:
            await websocket.send_json(
                {"type": "audio", "data": base64.b64encode(wav).decode(), "text": opening}
            )

    state.pause_task = asyncio.create_task(_pause_monitor(websocket, session_id, state))

    try:
        while True:
            raw = await websocket.receive_text()
            msg = json.loads(raw)
            msg_type = msg.get("type")

            state.reset_activity()

            if msg_type == "audio":
                now = time.time() * 1000
                if state.ai_speaking or now < state.ai_speak_end_at + AI_SPEAK_COOLDOWN_MS:
                    continue
                audio_b64 = msg.get("data", "")
                if audio_b64:
                    audio_bytes = base64.b64decode(audio_b64)
                    await asr.send_audio(session_id, audio_bytes)

            elif msg_type == "control":
                action = msg.get("action")
                if action == "submit":
                    if state.is_processing:
                        continue
                    text = msg.get("data", {}).get("text", "") or state.merge_buffer
                    if not text.strip():
                        # MiMo ASR: send buffered audio for recognition
                        recognized = await asr.recognize(session_id)
                        if recognized:
                            text = recognized
                        else:
                            await websocket.send_json(
                                {"type": "subtitle", "text": "未检测到语音，请重试", "isFinal": True}
                            )
                    if text.strip():
                        state.merge_buffer = ""
                        asyncio.create_task(
                            _handle_submit(websocket, session_id, state, text, tts, llm)
                        )
                elif action == "end_interview":
                    await VoiceInterviewService.end_session(session_id)
                    await websocket.send_json({"type": "control", "action": "ended"})
                    break
                elif action == "start_phase":
                    phase = msg.get("phase", "")
                    if phase:
                        await VoiceInterviewService.update_phase(session_id, phase)
                        session.current_phase = phase
                        await websocket.send_json(
                            {"type": "control", "action": "phase_changed", "phase": phase}
                        )

    except WebSocketDisconnect:
        logger.info("WebSocket disconnected for session %s", session_id)
    except Exception as e:
        logger.exception("WebSocket error for session %s: %s", session_id, e)
    finally:
        state.tts_cancel.set()
        if state.pause_task:
            state.pause_task.cancel()
        await asr.stop_session(session_id)
        _ws_sessions.pop(session_id, None)


async def _send_subtitle(ws: WebSocket, text: str, is_final: bool):
    try:
        await ws.send_json({"type": "subtitle", "text": text, "isFinal": is_final})
    except Exception:
        pass


async def _handle_final_stt(ws: WebSocket, state: WsSessionState, text: str):
    if state.merge_buffer:
        state.merge_buffer += " " + text
    else:
        state.merge_buffer = text
    await _send_subtitle(ws, state.merge_buffer, False)


async def _handle_submit(
    ws: WebSocket,
    session_id: str,
    state: WsSessionState,
    user_text: str,
    tts: VoiceTtsService,
    llm: VoiceLlmService,
):
    state.is_processing = True
    try:
        session = await VoiceInterviewService.get_session(session_id)
        if not session:
            return

        await VoiceInterviewService.save_message(session_id, session.current_phase, user_text, None)

        messages = await VoiceInterviewService.get_messages(session_id)
        resume_content = None
        if session.resume_id:
            from kirinchat.api.services.resume import ResumeService

            resume = await ResumeService.get_resume(session.resume_id)
            if resume:
                resume_content = getattr(resume, "content", None) or getattr(resume, "analysis", None)

        system_prompt = VoicePromptService.build_system_prompt(
            session.skill_id, session.current_phase, resume_content
        )
        chat_messages = VoicePromptService.build_conversation_history(messages, system_prompt)

        sentences: list[str] = []
        ai_text_parts: list[str] = []

        async def on_token(token: str):
            ai_text_parts.append(token)
            try:
                await ws.send_json({"type": "text", "content": token, "final": False})
            except Exception:
                pass

        async def on_sentence(sentence: str):
            sentences.append(sentence)

        await llm.chat_stream(chat_messages, on_token, on_sentence)

        full_ai_text = "".join(ai_text_parts)
        try:
            await ws.send_json({"type": "text", "content": "", "final": True})
        except Exception:
            pass

        await VoiceInterviewService.save_message(session_id, session.current_phase, None, full_ai_text)

        if sentences:
            state.ai_speaking = True
            try:
                await _synthesize_and_send_ordered(ws, tts, sentences, state.tts_cancel)
            finally:
                state.ai_speaking = False
                state.ai_speak_end_at = time.time() * 1000

            try:
                await ws.send_json({"type": "control", "action": "audio_complete"})
            except Exception:
                pass

    except Exception:
        logger.exception("_handle_submit error for session %s", session_id)
        try:
            await ws.send_json({"type": "error", "message": "处理回答时出错，请重试"})
        except Exception:
            pass
    finally:
        state.is_processing = False


async def _synthesize_and_send_ordered(
    ws: WebSocket, tts: VoiceTtsService, sentences: list[str],
    cancel: Optional[asyncio.Event] = None,
):
    queue: asyncio.Queue[tuple[int, Optional[bytes]]] = asyncio.Queue()
    tasks: list[asyncio.Task] = []

    async def tts_task(sentence: str, index: int):
        if cancel and cancel.is_set():
            return
        wav = await tts.synthesize_to_wav(sentence)
        await queue.put((index, wav))

    tasks = [asyncio.create_task(tts_task(s, i)) for i, s in enumerate(sentences)]
    total = len(sentences)
    sent = 0

    try:
        while sent < total:
            index, wav = await queue.get()
            if cancel and cancel.is_set():
                break
            if wav:
                try:
                    await ws.send_json(
                        {
                            "type": "audio_chunk",
                            "data": base64.b64encode(wav).decode(),
                            "index": index,
                            "isLast": index == total - 1,
                        }
                    )
                except Exception:
                    break
            sent += 1
    finally:
        for t in tasks:
            if not t.done():
                t.cancel()


async def _pause_monitor(ws: WebSocket, session_id: str, state: WsSessionState):
    try:
        while True:
            await asyncio.sleep(30)
            elapsed_ms = (time.time() - state.last_activity) * 1000
            if elapsed_ms > PAUSE_TIMEOUT_MS:
                await VoiceInterviewService.pause_session(session_id)
                try:
                    await ws.send_json({"type": "control", "action": "pause_timeout"})
                except Exception:
                    pass
                break
            elif elapsed_ms > PAUSE_WARNING_MS and not state.warning_sent:
                state.warning_sent = True
                try:
                    await ws.send_json({"type": "control", "action": "pause_timeout_warning"})
                except Exception:
                    pass
    except asyncio.CancelledError:
        pass
