import json
from typing import Optional

from sqlalchemy.orm import Session

from app.agent.job_structured_agent import job_structured_agent
from app.models.research_task import ResearchTask
from app.models.research_report import ResearchReport
from app.schemas.job_report import JobRecommendationReport
from app.services.user_profile_service import user_profile_service


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


class JobService:
    def create_job_task_and_report(
        self,
        db: Session,
        user_id: int,
        session_id: int,
        question: str,
        skills: list[str],
    ) -> tuple[ResearchTask, ResearchReport, list[str], JobRecommendationReport]:
        normalized_skills = user_profile_service.merge_skills(
            explicit_skills=skills,
            question=question,
        )

        final_prompt = user_profile_service.build_skill_prompt(
            skills=normalized_skills,
            question=question,
        )

        task = ResearchTask(
            user_id=user_id,
            session_id=session_id,
            task_type="general_career_question",
            topic=_extract_topic(question),
            user_input=question,
            status="running",
        )
        db.add(task)
        db.commit()
        db.refresh(task)

        try:
            structured_report: JobRecommendationReport = job_structured_agent.run(final_prompt)

            task.task_type = structured_report.task_type
            task.topic = (
                structured_report.recommended_jobs[0]
                if structured_report.recommended_jobs
                else _extract_topic(question)
            )
            task.status = "completed"
            db.add(task)
            db.commit()
            db.refresh(task)

            report = ResearchReport(
                task_id=task.id,
                summary=structured_report.comparison or "Job recommendation generated.",
                key_points=_safe_json_dumps(structured_report.recommended_jobs),
                comparison=structured_report.comparison,
                sources=_safe_json_dumps(normalized_skills),
                suggestions=_safe_json_dumps(structured_report.suggestions),
            )
            db.add(report)
            db.commit()
            db.refresh(report)

            return task, report, normalized_skills, structured_report

        except Exception:
            task.status = "failed"
            db.add(task)
            db.commit()
            db.refresh(task)
            raise

    def list_tasks_by_user(self, db: Session, user_id: int) -> list[ResearchTask]:
        return (
            db.query(ResearchTask)
            .filter(ResearchTask.user_id == user_id)
            .order_by(ResearchTask.created_at.desc())
            .all()
        )

    def get_task_detail(
        self, db: Session, task_id: int
    ) -> tuple[Optional[ResearchTask], Optional[ResearchReport]]:
        task = db.query(ResearchTask).filter(ResearchTask.id == task_id).first()
        if not task:
            return None, None

        report = db.query(ResearchReport).filter(ResearchReport.task_id == task_id).first()
        return task, report

    def rebuild_report_from_db(
        self, report: Optional[ResearchReport]
    ) -> Optional[JobRecommendationReport]:
        if not report:
            return None

        recommended_jobs = _safe_json_loads(report.key_points)
        normalized_skills = _safe_json_loads(report.sources)
        suggestions = _safe_json_loads(report.suggestions)

        return JobRecommendationReport(
            task_type="general_career_question",
            input_skills=normalized_skills,
            recommended_jobs=recommended_jobs,
            job_match_scores={},
            matched_skills={},
            missing_skills={},
            course_recommendations={},
            comparison=report.comparison,
            suggestions=suggestions,
        )


job_service = JobService()