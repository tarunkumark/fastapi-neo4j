from neo4j import GraphDatabase
import logging
from neo4j.exceptions import ServiceUnavailable

class Journey:
    def __init__(self, uri, user, password):
        self.driver = GraphDatabase.driver(uri, auth=(user, password))    
        def close(self):
            self.driver.close()

    def find_journey(self, start_node, end_node, count):
        with self.driver.session() as session:
            result = session.read_transaction(self._find_and_return_journey, start_node, end_node, count)
            return result
    def find_all(self):
        with self.driver.session() as session:
            result = session.read_transaction(self._find_all)
            return result

    @staticmethod
    def _find_all(tx):
        query = (
            '''MATCH (n:Station)
            RETURN n.name AS name
            ORDER BY n.name'''
        )
        result = tx.run(query)
        try:
            return {row["name"]:row["name"].title() for row in result}
        except ServiceUnavailable as exception:
            logging.error("{query} raised an error: \n {exception}".format(query=query, exception=exception))
            raise
    @staticmethod
    def _find_and_return_journey(tx, start_node, end_node, count):
        query = (
            '''MATCH (start:Station {name: $start_node}), (end:Station {name: $end_node})
            CALL apoc.algo.dijkstra(start, end, 'TRAVEL_TO', 'time', 3, $count) YIELD path, weight
            RETURN path, weight'''
        )
        result = tx.run(query, start_node=start_node, end_node=end_node, count=count)
        try:
            return [{"path": row["path"], "weight": row["weight"]} for row in result]
        except ServiceUnavailable as exception:
            logging.error("{query} raised an error: \n {exception}".format(query=query, exception=exception))
            raise
    