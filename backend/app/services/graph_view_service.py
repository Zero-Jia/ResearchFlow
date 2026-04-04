from app.schemas.graph_view_api import GraphJobViewResponse, GraphSkillItem
from app.services.graph_service import graph_service


class GraphViewService:
    def build_job_graph_view(self, job_name: str) -> GraphJobViewResponse | None:
        job = graph_service.get_job_by_name(job_name)
        if job is None:
            return None

        required_skills = graph_service.get_job_required_skills(job_name)

        skill_items = []
        for skill in required_skills:
            courses = graph_service.get_courses_for_skill(skill)
            skill_items.append(
                GraphSkillItem(
                    name=skill,
                    courses=courses,
                )
            )

        return GraphJobViewResponse(
            job_name=job["name"],
            category=job["category"],
            description=job["description"],
            skills=skill_items,
        )


graph_view_service = GraphViewService()