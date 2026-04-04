from app.schemas.job_report import JobRecommendationReport
from app.schemas.job_view_api import JobCard, JobRecommendationViewResponse
from app.services.job_service import job_service

class JobViewService:
    def build_view_response(
        self,
        task_id: int,
        question: str,
        report: JobRecommendationReport,
    ) -> JobRecommendationViewResponse:
        job_cards = []

        for job_name in report.recommended_jobs:
            score = report.job_match_scores.get(job_name, 0.0)
            matched_skills = report.matched_skills.get(job_name, [])
            missing_skills = report.missing_skills.get(job_name, [])

            recommended_courses = []
            for missing_skill in missing_skills:
                courses = report.course_recommendations.get(missing_skill, [])
                for course in courses:
                    if course not in recommended_courses:
                        recommended_courses.append(course)

            job_cards.append(
                JobCard(
                    job_name=job_name,
                    score=score,
                    matched_skills=matched_skills,
                    missing_skills=missing_skills,
                    recommended_courses=recommended_courses,
                )
            )

        return JobRecommendationViewResponse(
            task_id=task_id,
            question=question,
            normalized_skills=report.input_skills,
            task_type=report.task_type,
            job_cards=job_cards,
            comparison=report.comparison,
            suggestions=report.suggestions,
        )

    def build_view_response_from_task(self, task, report_model: JobRecommendationReport) -> JobRecommendationViewResponse:
        return self.build_view_response(
            task_id=task.id,
            question=task.user_input,
            report=report_model,
        )

job_view_service = JobViewService()