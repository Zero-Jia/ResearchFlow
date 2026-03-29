import json
from typing import Optional

from sqlalchemy.orm import Session

from app.agent.structured_agent import structured_researchflow_agent
from app.models.research_task import ResearchTask
from app.models.research_report import ResearchReport
from app.schemas.report import ResearchReport as StructuredResearchReport


def _extract_topic(question: str) -> str:
    q = question.strip()
    if len(q) <= 80:
        return q
    return q[:80]


def _safe_json_dumps(value) -> str:
    return json.dumps(value, ensure_ascii=False)


def _safe_json_loads(value: Optional[str]):
    if not value:
        return []
    try:
        return json.loads(value)
    except Exception:
        return []


class ResearchService:
    def create_task_and_generate_report(
        self,
        db: Session,
        user_id: int,
        session_id: int,
        question: str,
    ) -> tuple[ResearchTask, ResearchReport]:
        task = ResearchTask(
            user_id=user_id,
            session_id=session_id,
            task_type="general",
            topic=_extract_topic(question),
            user_input=question,
            status="running",
        )
        db.add(task)
        db.commit()
        db.refresh(task)

        try:
            structured_report: StructuredResearchReport = structured_researchflow_agent.run(question)

            task.task_type = structured_report.task_type
            task.topic = structured_report.topic
            task.status = "completed"
            db.add(task)
            db.commit()
            db.refresh(task)

            report = ResearchReport(
                task_id=task.id,
                summary=structured_report.summary,
                key_points=_safe_json_dumps(structured_report.key_points),
                comparison=structured_report.comparison,
                sources=None,
                suggestions=_safe_json_dumps(structured_report.suggestions),
            )
            db.add(report)
            db.commit()
            db.refresh(report)

            return task, report

        except Exception:
            task.status = "failed"
            db.add(task)
            db.commit()
            db.refresh(task)
            raise

    def get_task_detail(self, db: Session, task_id: int) -> tuple[Optional[ResearchTask], Optional[ResearchReport]]:
        task = db.query(ResearchTask).filter(ResearchTask.id == task_id).first()
        if not task:
            return None, None

        report = db.query(ResearchReport).filter(ResearchReport.task_id == task_id).first()
        return task, report

    def list_tasks_by_user(self, db: Session, user_id: int) -> list[ResearchTask]:
        return (
            db.query(ResearchTask)
            .filter(ResearchTask.user_id == user_id)
            .order_by(ResearchTask.created_at.desc())
            .all()
        )

    def parse_report(self, report: Optional[ResearchReport]) -> Optional[dict]:
        if not report:
            return None

        return {
            "summary": report.summary,
            "key_points": _safe_json_loads(report.key_points),
            "comparison": report.comparison,
            "suggestions": _safe_json_loads(report.suggestions),
        }


research_service = ResearchService()