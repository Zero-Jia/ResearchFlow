from app.data.job_kg_mock import JOBS, COURSES
from app.services.graph_service import graph_service


def import_jobs():
    for job in JOBS:
        graph_service.create_job_node(
            job_name=job["name"],
            category=job["category"],
            description=job["description"],
        )

        for skill in job["required_skills"]:
            graph_service.create_skill_node(skill)
            graph_service.create_job_requires_skill(job["name"], skill)


def import_courses():
    for course in COURSES:
        graph_service.create_course_node(
            course_name=course["name"],
            platform=course["platform"],
        )

        for skill in course["teaches"]:
            graph_service.create_skill_node(skill)
            graph_service.create_course_teaches_skill(course["name"], skill)


def main():
    print("Importing jobs...")
    import_jobs()

    print("Importing courses...")
    import_courses()

    print("Done.")


if __name__ == "__main__":
    main()