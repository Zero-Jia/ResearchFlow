import json
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, Body
from fastapi.responses import StreamingResponse
from langchain_core.messages import HumanMessage
from sqlalchemy.orm import Session

from app.api.routes.auth import get_current_user
from app.db.session import get_db
from app.models.chat_message import ChatMessage
from app.models.chat_session import ChatSession
from app.models.user import User
from app.graph.job_graph_workflow import job_graph_app

router = APIRouter()


def _get_recent_messages(db: Session, session_id: int, limit: int = 10) -> list[dict]:
    messages = (
        db.query(ChatMessage)
        .filter(ChatMessage.session_id == session_id)
        .order_by(ChatMessage.created_at.asc(), ChatMessage.id.asc())
        .all()
    )

    messages = messages[-limit:]

    return [
        {
            "role": m.role,
            "content": m.content,
        }
        for m in messages
    ]


def _get_previous_skills_from_last_report(db: Session, session_id: int) -> list[str]:
    """
    从最近一条 assistant 的 report_json 中恢复上一轮技能。
    这是当前最稳的“短期记忆恢复”方案。
    """
    last_assistant_msg = (
        db.query(ChatMessage)
        .filter(
            ChatMessage.session_id == session_id,
            ChatMessage.role == "assistant",
            ChatMessage.report_json.isnot(None),
        )
        .order_by(ChatMessage.created_at.desc(), ChatMessage.id.desc())
        .first()
    )

    if not last_assistant_msg or not last_assistant_msg.report_json:
        return []

    try:
        report_data = json.loads(last_assistant_msg.report_json)
        skills = report_data.get("input_skills", [])
        if isinstance(skills, list):
            return [str(skill).strip() for skill in skills if str(skill).strip()]
        return []
    except Exception:
        return []


@router.post("/chat/reasoning-stream")
def reasoning_stream(
    payload: dict = Body(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    session_id = payload.get("session_id")
    question = (payload.get("question") or "").strip()

    if not session_id:
        raise HTTPException(status_code=400, detail="session_id 不能为空")
    if not question:
        raise HTTPException(status_code=400, detail="question 不能为空")

    session = (
        db.query(ChatSession)
        .filter(ChatSession.id == session_id, ChatSession.user_id == current_user.id)
        .first()
    )
    if not session:
        raise HTTPException(status_code=404, detail="会话不存在")

    # 1. 先保存用户消息
    user_msg = ChatMessage(
        session_id=session_id,
        role="user",
        content=question,
        report_json=None,
    )
    db.add(user_msg)
    db.commit()
    db.refresh(user_msg)

    # 2. 如果是默认标题，自动更新
    if session.title == "新会话" or not session.title.strip():
        session.title = question[:20]
        session.updated_at = datetime.utcnow()
        db.add(session)
        db.commit()
        db.refresh(session)

    # 3. 读取短期记忆所需的历史上下文
    history_messages = _get_recent_messages(db, session_id=session_id, limit=10)
    previous_skills = _get_previous_skills_from_last_report(db, session_id=session_id)

    def ndjson_generator():
        final_answer_text = ""
        final_report = {}

        try:
            initial_state = {
                "messages": [HumanMessage(content=question)],
                "session_id": session_id,
                "history_messages": history_messages,
                "previous_skills": previous_skills,
                "current_question": "",
                "conversation_text": "",
                "merged_skills": [],
                "task_type": "",
                "plan": [],
                "recommend_result": {},
                "gap_result": {},
                "course_result": {},
                "compare_result": {},
                "memory_result": {},
                "fallback_result": {},
                "report": {},
                "answer_text": "",
                "reasoning": [],
                "latest_reasoning": "",
            }

            for chunk in job_graph_app.stream(
                initial_state,
                stream_mode="updates",
            ):
                if isinstance(chunk, dict):
                    for node_name, update in chunk.items():
                        if not isinstance(update, dict):
                            continue

                        latest_reasoning = update.get("latest_reasoning")
                        if latest_reasoning:
                            yield json.dumps(
                                {
                                    "type": "reasoning",
                                    "step": node_name,
                                    "text": latest_reasoning,
                                },
                                ensure_ascii=False,
                            ) + "\n"

                        answer_text = update.get("answer_text")
                        report = update.get("report")

                        if answer_text:
                            final_answer_text = answer_text
                            final_report = report or {}

                            yield json.dumps(
                                {
                                    "type": "final",
                                    "text": answer_text,
                                    "report": final_report,
                                },
                                ensure_ascii=False,
                            ) + "\n"

            # 4. 流结束后，把 assistant 回复保存到数据库
            assistant_text = final_answer_text.strip() if final_answer_text else "已生成回复。"

            assistant_msg = ChatMessage(
                session_id=session_id,
                role="assistant",
                content=assistant_text,
                report_json=json.dumps(final_report, ensure_ascii=False) if final_report else None,
            )
            db.add(assistant_msg)

            session.updated_at = datetime.utcnow()
            db.add(session)
            db.commit()

            yield json.dumps({"type": "done"}, ensure_ascii=False) + "\n"

        except Exception as e:
            yield json.dumps(
                {"type": "error", "text": str(e)},
                ensure_ascii=False,
            ) + "\n"

    return StreamingResponse(
        ndjson_generator(),
        media_type="application/x-ndjson; charset=utf-8",
    )