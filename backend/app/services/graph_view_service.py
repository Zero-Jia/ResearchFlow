from app.schemas.graph_view_api import GraphJobViewResponse, GraphSkillItem
from app.services.graph_service import graph_service


class GraphViewService:
    def build_job_graph_view(self, job_name: str) -> GraphJobViewResponse | None:
        clean_job_name = job_name.strip() if job_name else ""
        if not clean_job_name:
            return None

        job = graph_service.get_job_by_name(clean_job_name)
        if job is None:
            return None

        required_skills = graph_service.get_job_required_skills(clean_job_name)

        skill_items = []
        for skill in required_skills:
            courses = graph_service.get_courses_for_skill(skill)
            skill_items.append(
                GraphSkillItem(
                    name=skill,
                    courses=courses or [],
                )
            )

        return GraphJobViewResponse(
            job_name=job["name"],
            category=job["category"],
            description=job["description"],
            skills=skill_items,
        )


graph_view_service = GraphViewService()