from neo4j import GraphDatabase
from typing import Optional, Dict, Any

class Neo4jClient:
    def __init__(self, uri: str, user: str, password: str):
        self.driver = GraphDatabase.driver(uri, auth=(user, password))

    def close(self):
        self.driver.close()

    def run(self, query: str, params: Optional[Dict[str, Any]] = None):
        with self.driver.session() as session:
            result = session.run(query, params or {})
            return [r.data() for r in result]
