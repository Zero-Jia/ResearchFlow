import json
import uuid
from typing import Optional

from sqlalchemy.orm import Session

from app.agent.job_memory_agent import job_memory_agent
from app.models.research_task import ResearchTask
from app.models.research_report import ResearchReport
from app.schemas.job_report import JobRecommendationReport
from app.services.job_session_memory_service import job_session_memory_service
from app.services.user_profile_service import user_profile_service


def _extract_topic(question: str) -> str:
    q = question.strip()
    if len(q) <= 80:
        return q
    return q[:80]


def _safe_json_dumps(value) -> str:
    return json.dumps(value, ensure_ascii=False)


def _safe_json_loads(value: Optional[str], default=None):
    if value is None or value == "":
        return default if default is not None else []
    try:
        return json.loads(value)
    except Exception:
        return default if default is not None else []


def _build_thread_id(session_id: int | None, user_id: int | None = None) -> str:
    if session_id is not None:
        return f"job-session-{session_id}"
    if user_id is not None:
        return f"job-user-{user_id}-adhoc"
    return f"job-anonymous-{uuid.uuid4()}"


class JobService:
    def _build_memory_enhanced_prompt(
        self,
        current_question: str,
        accumulated_skills: list[str],
        current_turn_skills: list[str],
    ) -> str:
        """
        给 agent 一个更明确的输入，告诉它：
        1. 当前问题是什么
        2. 历史累计技能是什么
        3. 当前轮新提到的技能是什么
        4. 分析时应该优先使用累计技能
        """
        accumulated_text = "、".join(accumulated_skills) if accumulated_skills else "无"
        current_turn_text = "、".join(current_turn_skills) if current_turn_skills else "无"

        return (
            f"用户当前问题：{current_question or '无'}\n"
            f"该会话中已经累计确认的用户技能：{accumulated_text}\n"
            f"本轮新识别到的技能：{current_turn_text}\n"
            "请注意：\n"
            "1. 你必须优先使用“该会话中已经累计确认的用户技能”作为用户真实技能基础；\n"
            "2. 如果本轮没有新的明确技能，不要丢弃历史技能；\n"
            "3. 不要把“数据分析师、后端开发、数据分析”这类岗位名或方向词误当成用户已有技能；\n"
            "4. 输出 input_skills 时，应尽量反映累计后的真实技能集合；\n"
            "5. 再基于这些技能完成岗位推荐、技能差距分析、课程推荐或岗位对比。\n"
        )

    def _get_accumulated_skills(
        self,
        session_id: int,
        question: str,
        explicit_skills: list[str],
    ) -> tuple[list[str], list[str]]:
        """
        返回：
        1. current_turn_skills: 当前轮识别到的技能
        2. accumulated_skills: 合并历史后的技能
        """
        current_turn_skills = user_profile_service.merge_skills(
            explicit_skills=explicit_skills,
            question=question,
        )

        accumulated_skills = job_session_memory_service.merge_and_save_skills(
            session_id=session_id,
            new_skills=current_turn_skills,
        )

        return current_turn_skills, accumulated_skills

    def create_job_task_and_report(
        self,
        db: Session,
        user_id: int,
        session_id: int,
        question: str,
        skills: list[str],
    ) -> tuple[ResearchTask, ResearchReport, list[str], JobRecommendationReport]:
        question = question.strip() if question else ""

        current_turn_skills, accumulated_skills = self._get_accumulated_skills(
            session_id=session_id,
            question=question,
            explicit_skills=skills,
        )

        final_prompt = self._build_memory_enhanced_prompt(
            current_question=question,
            accumulated_skills=accumulated_skills,
            current_turn_skills=current_turn_skills,
        )

        task = ResearchTask(
            user_id=user_id,
            session_id=session_id,
            task_type="general_career_question",
            topic=_extract_topic(question if question else "职位推荐任务"),
            user_input=question if question else "职位推荐任务",
            status="running",
        )
        db.add(task)
        db.commit()
        db.refresh(task)

        try:
            thread_id = _build_thread_id(session_id=session_id, user_id=user_id)

            structured_report: JobRecommendationReport = job_memory_agent.run(
                message=final_prompt,
                thread_id=thread_id,
            )

            if not structured_report.input_skills:
                structured_report.input_skills = accumulated_skills
            else:
                structured_report.input_skills = job_session_memory_service._deduplicate(
                    accumulated_skills + structured_report.input_skills
                )

            task.task_type = structured_report.task_type
            task.topic = (
                structured_report.recommended_jobs[0]
                if structured_report.recommended_jobs
                else _extract_topic(question if question else "职位推荐任务")
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
                sources=_safe_json_dumps(structured_report.input_skills),
                suggestions=_safe_json_dumps(structured_report.suggestions),
                job_match_scores=_safe_json_dumps(structured_report.job_match_scores),
                matched_skills=_safe_json_dumps(structured_report.matched_skills),
                missing_skills=_safe_json_dumps(structured_report.missing_skills),
                course_recommendations=_safe_json_dumps(structured_report.course_recommendations),
            )
            db.add(report)
            db.commit()
            db.refresh(report)

            job_session_memory_service.save_skills(
                session_id=session_id,
                skills=structured_report.input_skills,
            )

            return task, report, structured_report.input_skills, structured_report

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

    def get_task_detail(self, db: Session, task_id: int) -> tuple[Optional[ResearchTask], Optional[ResearchReport]]:
        task = db.query(ResearchTask).filter(ResearchTask.id == task_id).first()
        if not task:
            return None, None

        report = db.query(ResearchReport).filter(ResearchReport.task_id == task_id).first()
        return task, report

    def rebuild_report_from_db(self, task: ResearchTask, report: Optional[ResearchReport]) -> Optional[JobRecommendationReport]:
        if not report:
            return None

        recommended_jobs = _safe_json_loads(report.key_points, default=[])
        normalized_skills = _safe_json_loads(report.sources, default=[])
        suggestions = _safe_json_loads(report.suggestions, default=[])
        job_match_scores = _safe_json_loads(report.job_match_scores, default={})
        matched_skills = _safe_json_loads(report.matched_skills, default={})
        missing_skills = _safe_json_loads(report.missing_skills, default={})
        course_recommendations = _safe_json_loads(report.course_recommendations, default={})

        return JobRecommendationReport(
            task_type=task.task_type,
            input_skills=normalized_skills,
            recommended_jobs=recommended_jobs,
            job_match_scores=job_match_scores,
            matched_skills=matched_skills,
            missing_skills=missing_skills,
            course_recommendations=course_recommendations,
            comparison=report.comparison,
            suggestions=suggestions,
        )

    def run_memory_chat(
        self,
        question: str,
        skills: list[str],
        session_id: int,
        user_id: int | None = None,
    ) -> tuple[list[str], JobRecommendationReport]:
        question = question.strip() if question else ""

        current_turn_skills, accumulated_skills = self._get_accumulated_skills(
            session_id=session_id,
            question=question,
            explicit_skills=skills,
        )

        final_prompt = self._build_memory_enhanced_prompt(
            current_question=question,
            accumulated_skills=accumulated_skills,
            current_turn_skills=current_turn_skills,
        )

        thread_id = _build_thread_id(session_id=session_id, user_id=user_id)

        structured_report: JobRecommendationReport = job_memory_agent.run(
            message=final_prompt,
            thread_id=thread_id,
        )

        if not structured_report.input_skills:
            structured_report.input_skills = accumulated_skills
        else:
            structured_report.input_skills = job_session_memory_service._deduplicate(
                accumulated_skills + structured_report.input_skills
            )

        job_session_memory_service.save_skills(
            session_id=session_id,
            skills=structured_report.input_skills,
        )

        return structured_report.input_skills, structured_report


job_service = JobService()