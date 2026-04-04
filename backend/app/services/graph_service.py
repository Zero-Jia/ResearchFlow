from typing import List, Dict, Any

from app.core.neo4j_config import neo4j_config


class GraphService:
    def test_connection(self) -> Dict[str, Any]:
        query = "RETURN 1 AS result"

        with neo4j_config.driver.session(database=neo4j_config.database) as session:
            record = session.run(query).single()
            return {
                "status": "ok",
                "result": record["result"] if record else None
            }

    def create_job_node(self, job_name: str, category: str, description: str) -> None:
        query = """
        MERGE (j:Job {name: $job_name})
        SET j.category = $category,
            j.description = $description
        """

        with neo4j_config.driver.session(database=neo4j_config.database) as session:
            session.run(
                query,
                job_name=job_name,
                category=category,
                description=description,
            )

    def create_skill_node(self, skill_name: str) -> None:
        query = """
        MERGE (s:Skill {name: $skill_name})
        """

        with neo4j_config.driver.session(database=neo4j_config.database) as session:
            session.run(query, skill_name=skill_name)

    def create_course_node(self, course_name: str, platform: str) -> None:
        query = """
        MERGE (c:Course {name: $course_name})
        SET c.platform = $platform
        """

        with neo4j_config.driver.session(database=neo4j_config.database) as session:
            session.run(
                query,
                course_name=course_name,
                platform=platform,
            )

    def create_job_requires_skill(self, job_name: str, skill_name: str) -> None:
        query = """
        MATCH (j:Job {name: $job_name})
        MATCH (s:Skill {name: $skill_name})
        MERGE (j)-[:REQUIRES]->(s)
        """

        with neo4j_config.driver.session(database=neo4j_config.database) as session:
            session.run(query, job_name=job_name, skill_name=skill_name)

    def create_course_teaches_skill(self, course_name: str, skill_name: str) -> None:
        query = """
        MATCH (c:Course {name: $course_name})
        MATCH (s:Skill {name: $skill_name})
        MERGE (c)-[:TEACHES]->(s)
        """

        with neo4j_config.driver.session(database=neo4j_config.database) as session:
            session.run(query, course_name=course_name, skill_name=skill_name)

    def get_job_required_skills(self, job_name: str) -> List[str]:
        query = """
        MATCH (j:Job {name: $job_name})-[:REQUIRES]->(s:Skill)
        RETURN s.name AS skill_name
        ORDER BY skill_name
        """

        with neo4j_config.driver.session(database=neo4j_config.database) as session:
            result = session.run(query, job_name=job_name)
            return [record["skill_name"] for record in result]

    def get_courses_for_skill(self, skill_name: str) -> List[str]:
        query = """
        MATCH (c:Course)-[:TEACHES]->(s:Skill {name: $skill_name})
        RETURN c.name AS course_name
        ORDER BY course_name
        """

        with neo4j_config.driver.session(database=neo4j_config.database) as session:
            result = session.run(query, skill_name=skill_name)
            return [record["course_name"] for record in result]

    def get_all_jobs(self) -> List[Dict[str, Any]]:
        query = """
        MATCH (j:Job)
        RETURN j.name AS name, j.category AS category, j.description AS description
        ORDER BY name
        """

        with neo4j_config.driver.session(database=neo4j_config.database) as session:
            result = session.run(query)
            return [
                {
                    "name": record["name"],
                    "category": record["category"],
                    "description": record["description"],
                }
                for record in result
            ]

    def get_jobs_with_required_skills(self) -> List[Dict[str, Any]]:
        query = """
        MATCH (j:Job)-[:REQUIRES]->(s:Skill)
        RETURN j.name AS job_name,
            j.category AS category,
            j.description AS description,
            collect(s.name) AS required_skills
        ORDER BY job_name
        """

        with neo4j_config.driver.session(database=neo4j_config.database) as session:
            result = session.run(query)
            return [
                {
                    "job_name": record["job_name"],
                    "category": record["category"],
                    "description": record["description"],
                    "required_skills": list(record["required_skills"]),
                }
                for record in result
            ]

    def get_job_by_name(self, job_name: str) -> Dict[str, Any] | None:
        query = """
        MATCH (j:Job {name: $job_name})
        RETURN j.name AS name, j.category AS category, j.description AS description
        LIMIT 1
        """

        with neo4j_config.driver.session(database=neo4j_config.database) as session:
            record = session.run(query, job_name=job_name).single()
            if not record:
                return None
            return {
                "name": record["name"],
                "category": record["category"],
                "description": record["description"],
            }

    def get_courses_for_skills(self, skills: List[str]) -> List[Dict[str, Any]]:
        if not skills:
            return []

        query = """
        MATCH (c:Course)-[:TEACHES]->(s:Skill)
        WHERE s.name IN $skills
        RETURN c.name AS course_name, c.platform AS platform, collect(DISTINCT s.name) AS covered_skills
        ORDER BY course_name
        """

        with neo4j_config.driver.session(database=neo4j_config.database) as session:
            result = session.run(query, skills=skills)
            return [
                {
                    "course_name": record["course_name"],
                    "platform": record["platform"],
                    "covered_skills": list(record["covered_skills"]),
                }
                for record in result
            ]
        
    def get_two_jobs_required_skills(self, job_a: str, job_b: str) -> Dict[str, List[str]]:
        skills_a = self.get_job_required_skills(job_a)
        skills_b = self.get_job_required_skills(job_b)

        return {
            "job_a_skills": skills_a,
            "job_b_skills": skills_b,
        }


graph_service = GraphService()