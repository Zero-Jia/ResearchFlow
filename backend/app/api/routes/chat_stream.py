from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, Body
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session

from app.api.routes.auth import get_current_user
from app.db.session import get_db
from app.models.chat_message import ChatMessage
from app.models.chat_session import ChatSession
from app.models.user import User
from app.agent.job_streaming_agent import job_streaming_agent

router = APIRouter()


def _build_thread_id(session_id: int) -> str:
    return f"job-session-{session_id}"


@router.post("/chat/sessions/{session_id}/stream")
def stream_message(
    session_id: int,
    payload: dict = Body(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    session = (
        db.query(ChatSession)
        .filter(ChatSession.id == session_id, ChatSession.user_id == current_user.id)
        .first()
    )
    if not session:
        raise HTTPException(status_code=404, detail="会话不存在")

    question = (payload.get("question") or "").strip()
    if not question:
        raise HTTPException(status_code=400, detail="问题不能为空")

    # 先保存用户消息
    user_msg = ChatMessage(
        session_id=session_id,
        role="user",
        content=question,
    )
    db.add(user_msg)
    db.commit()
    db.refresh(user_msg)

    # 如果是默认标题，自动更新
    if session.title == "新会话":
        session.title = question[:20]
        session.updated_at = datetime.utcnow()
        db.add(session)
        db.commit()
        db.refresh(session)

    thread_id = _build_thread_id(session_id)

    def event_generator():
        assistant_parts = []

        try:
            for token in job_streaming_agent.stream_text(
                message=question,
                thread_id=thread_id,
            ):
                assistant_parts.append(token)
                yield token

            # 流结束后，把 assistant 完整回复保存到数据库
            assistant_text = "".join(assistant_parts).strip()
            if not assistant_text:
                assistant_text = "已生成回复。"

            assistant_msg = ChatMessage(
                session_id=session_id,
                role="assistant",
                content=assistant_text,
            )
            db.add(assistant_msg)

            session.updated_at = datetime.utcnow()
            db.add(session)
            db.commit()

        except Exception as e:
            yield f"\n[ERROR] {str(e)}"

    return StreamingResponse(
        event_generator(),
        media_type="text/plain; charset=utf-8",
    )