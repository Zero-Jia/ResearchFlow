import json
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.api.routes.auth import get_current_user
from app.db.session import get_db
from app.models.chat_message import ChatMessage
from app.models.chat_session import ChatSession
from app.models.user import User
from app.schemas.chat_ui import (
    ChatSessionCreateRequest,
    ChatSessionItem,
    ChatSessionListResponse,
    ChatMessageItem,
    ChatMessageListResponse,
    ChatSendRequest,
    ChatSendResponse,
)
from app.services.job_service import job_service

router = APIRouter()


@router.get("/chat/sessions", response_model=ChatSessionListResponse)
def list_sessions(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    sessions = (
        db.query(ChatSession)
        .filter(ChatSession.user_id == current_user.id)
        .order_by(ChatSession.updated_at.desc())
        .all()
    )

    items = [
        ChatSessionItem(
            id=s.id,
            title=s.title,
            created_at=s.created_at.isoformat(),
            updated_at=s.updated_at.isoformat(),
        )
        for s in sessions
    ]
    return ChatSessionListResponse(items=items)


@router.post("/chat/sessions", response_model=ChatSessionItem)
def create_session(
    request: ChatSessionCreateRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    title = (request.title or "新会话").strip() or "新会话"

    session = ChatSession(
        user_id=current_user.id,
        title=title,
        session_type="job_chat",
    )
    db.add(session)
    db.commit()
    db.refresh(session)

    return ChatSessionItem(
        id=session.id,
        title=session.title,
        created_at=session.created_at.isoformat(),
        updated_at=session.updated_at.isoformat(),
    )


@router.get("/chat/sessions/{session_id}/messages", response_model=ChatMessageListResponse)
def list_messages(
    session_id: int,
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

    messages = (
        db.query(ChatMessage)
        .filter(ChatMessage.session_id == session_id)
        .order_by(ChatMessage.created_at.asc(), ChatMessage.id.asc())
        .all()
    )

    return ChatMessageListResponse(
        session_id=session_id,
        messages=[
            ChatMessageItem(
                id=m.id,
                role=m.role,
                content=m.content,
                created_at=m.created_at.isoformat(),
            )
            for m in messages
        ],
    )


@router.post("/chat/sessions/{session_id}/messages", response_model=ChatSendResponse)
def send_message(
    session_id: int,
    request: ChatSendRequest,
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

    question = request.question.strip()
    if not question:
        raise HTTPException(status_code=400, detail="问题不能为空")

    user_msg = ChatMessage(
        session_id=session_id,
        role="user",
        content=question,
        report_json=None,
    )
    db.add(user_msg)
    db.commit()
    db.refresh(user_msg)

    if session.title == "新会话" or not session.title.strip():
        session.title = question[:20]
        session.updated_at = datetime.utcnow()
        db.add(session)
        db.commit()
        db.refresh(session)

    normalized_skills, report = job_service.run_memory_chat(
        question=question,
        skills=request.skills,
        session_id=session_id,
        user_id=current_user.id,
    )

    if not report.input_skills:
        report.input_skills = normalized_skills

    assistant_text = job_service.render_report_to_text(report)

    assistant_msg = ChatMessage(
        session_id=session_id,
        role="assistant",
        content=assistant_text,
        report_json=json.dumps(report.model_dump(), ensure_ascii=False),
    )
    db.add(assistant_msg)

    session.updated_at = datetime.utcnow()
    db.add(session)

    db.commit()
    db.refresh(assistant_msg)

    return ChatSendResponse(
        session_id=session_id,
        user_message=ChatMessageItem(
            id=user_msg.id,
            role=user_msg.role,
            content=user_msg.content,
            created_at=user_msg.created_at.isoformat(),
        ),
        assistant_message=ChatMessageItem(
            id=assistant_msg.id,
            role=assistant_msg.role,
            content=assistant_msg.content,
            created_at=assistant_msg.created_at.isoformat(),
        ),
        report=report,
    )