"""Graph playground.

Contains an implementation to process a graph following a specific schema.
"""
from collections import defaultdict
from pathlib import Path
from typing import Any
from typing import Dict
from typing import List
from typing import Tuple
from typing import Union

import networkx as nx

from graph_tools_playground import errors


class ChallengeGraph(nx.MultiDiGraph):
    """Graph for this Challenge."""

    @classmethod
    def from_file(
        cls, properties: Union[str, Path], relationships: Union[str, Path]
    ) -> "ChallengeGraph":
        """Create a ChallengeGraph from file.

        :param properties: File containing Entity Properties
        :type properties: Union[str, Path]
        :param relationships: File containing Entity Relationships
        :type relationships: Union[str, Path]
        :return: Graph with loaded data
        :rtype: ChallengeGraph
        """
        graph = cls()
        graph.add_properties_from_file(properties)
        graph.add_relationships_from_file(relationships)
        return graph

    @staticmethod
    def parse_property_line(line: str) -> Tuple[str, str, str]:
        """Parse a line defining a property.

        :param line: String defining a property
        :type line: str
        :return: Triplet (id, property, value)
        :rtype: Tuple[str, str, str]
        """
        entity_property = line.split()
        id, property, value = (
            entity_property[0],
            entity_property[1],
            " ".join(entity_property[2:]),
        )
        return id, property, value

    @staticmethod
    def parse_relationship_line(line: str) -> Tuple[str, str, str, str, str]:
        """Parse a line defining a relationship.

        :param line: String containing a relationship.
        :type line: str
        :raises errors.InvalidRelationshipLine: If got error processing relationship.
        :return: Relationship row
        :rtype: Tuple[str, str, str, str, str]
        """
        relationship = line.split()
        if len(relationship) != 5:
            raise errors.InvalidRelationshipLine(
                f"Error processing relationship: {line}"
            )
        rel, id1, type1, id2, type2 = relationship
        return rel, id1, type1, id2, type2

    def add_properties_from_file(self, properties: Union[str, Path]) -> None:
        """Add properties to entities from file.

        It is assumed that the relationship file is a file
        with the following schema:

        +----+-----------+----------+
        | ID | Property  | Value    |
        +====+===========+==========+
        | D  | Name      | dpalma   |
        +----+-----------+----------+
        | D  | Phone     | 12345    |
        +----+-----------+----------+
        | A  | Name      | Qwerty   |
        +----+-----------+----------+

        :param properties: Property file
        :type properties: Union[str, Path]
        :raises FileNotFoundError: If file does not exist
        """
        if isinstance(properties, str):
            properties = Path(properties)
        if not properties.exists():
            raise FileNotFoundError(f"Properties file {properties} not found.")
        parsed_entities: Dict = defaultdict(dict)
        with open(properties, "r") as fp:
            # Skip header
            next(fp)
            for line in fp:
                line = line.strip()
                if line:
                    id, property, value = ChallengeGraph.parse_property_line(line)
                    parsed_entities[id][property] = value

        self.add_nodes_from(
            (id, properties) for id, properties in parsed_entities.items()
        )

    def add_relationships_from_file(self, relationships: Union[str, Path]) -> None:
        """Add relationships from a relationship file.

        It is assumed that the relationship file is a file
        with the following schema:

        +--------------+-------+---------+-----+---------+
        | Relationship | ID1   | Type1   | ID2 | Type2   |
        +==============+=======+========+======+=========+
        | STUDIES_WITH | A     | Person | B    | Person  |
        +--------------+-------+--------+------+---------+
        | FRIENDS_WITH | A     | Person | C    | Person  |
        +--------------+-------+--------+------+---------+

        :param relationships: Relationship file
        :type relationships: Union[str, Path]
        :raises FileNotFoundError: If file does not exist
        """
        if isinstance(relationships, str):
            relationships = Path(relationships)

        if not relationships.exists():
            raise FileNotFoundError(f"Relationship file {relationships} not found.")

        with open(relationships, "r") as fp:
            # Skip header
            next(fp)
            for line in fp:
                line = line.strip()
                if line:
                    (
                        rel,
                        id1,
                        type1,
                        id2,
                        type2,
                    ) = ChallengeGraph.parse_relationship_line(line)
                    self.nodes[id1].setdefault("Type", type1)
                    self.nodes[id2].setdefault("Type", type2)
                    self.add_edge(id1, id2, relation=rel)

    def find_friend_cliques(self) -> List[List[Any]]:
        """Find all cliques of friends.

        .. danger:: Note that this algorithm is exponential in the number of nodes
           and thus, it will not scale to big graphs. To workaround this, other
           approaches might be used, such as greedy or heuristic approaches. Probably
           for analysis purposes we are more interested in maximal cliques rather than
           finding all cliques.

        The graph is projected into an unidirected graph and only the relationship
        ``FRIENDS_WITH`` is considered.

        :return: All cliques in the graph.
        :rtype: List[List[Any]]
        """
        edges = set()
        for n1, n2, d in self.edges(data=True):
            edge = frozenset([n1, n2])
            if d["relation"] == "FRIENDS_WITH":
                edges.add(edge)

        G = nx.Graph()
        G.add_edges_from(edges)
        return nx.algorithms.clique.enumerate_all_cliques(G)

    def find_person_cliques(self) -> List[List[Any]]:
        """Find all cliques of persons.

        .. danger:: Note that this algorithm is exponential in the number of nodes
           and thus, it will not scale to big graphs. To workaround this, other
           approaches might be used, such as greedy or heuristic approaches. Probably
           for analysis purposes we are more interested in maximal cliques rather than
           finding all cliques.

        The graph is projected into an unidirected graph and only the nodes
        with ``Type`` attribute equals ``Person`` are considered.

        :return: All cliques in the graph.
        :rtype: List[List[Any]]
        """
        edges = set()
        for n1, n2 in self.edges():
            edge = frozenset([n1, n2])
            if self.nodes[n1].get("Type") == self.nodes[n2].get("Type") == "Person":
                edges.add(edge)

        G = nx.Graph()
        G.add_edges_from(edges)
        return nx.algorithms.clique.enumerate_all_cliques(G)
