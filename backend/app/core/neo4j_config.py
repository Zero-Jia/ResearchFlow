from neo4j import GraphDatabase

from app.core.config import settings


class Neo4jConfig:
    def __init__(self):
        self.driver = GraphDatabase.driver(
            settings.NEO4J_URI,
            auth=(settings.NEO4J_USERNAME, settings.NEO4J_PASSWORD),
        )
        self.database = settings.NEO4J_DATABASE

    def close(self):
        if self.driver:
            self.driver.close()


neo4j_config = Neo4jConfig()