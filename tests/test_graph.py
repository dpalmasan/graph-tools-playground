"""Unit tests for graph.py module."""
import pytest

from graph_tools_playground import graph


def test_graph_from_file(tmpdir):
    """Test load graph from file."""
    property_file = tmpdir.join("properties.txt")
    property_file.write(
        "ID      Property        Value\n"
        "Q       Name            Bulldogs\n"
        "A       Name            Ally\n"
        "A       Phone           12345\n"
        "C       Name            Oscar\n"
    )

    relationships_file = tmpdir.join("relationships.txt")
    relationships_file.write(
        "Relationship    ID1     Type1   ID2     Type2\n"
        "STUDIES_WITH    A       Person  C       Person\n"
        "FRIENDS_WITH    A       Person  Q       Person\n"
    )

    g = graph.ChallengeGraph.from_file(
        property_file.strpath, relationships_file.strpath
    )

    # Check idempotency (Won't change beyond initial operation)
    g.add_properties_from_file(property_file.strpath)

    assert g.nodes["A"] == {"Name": "Ally", "Phone": "12345", "Type": "Person"}

    assert g["A"] == {
        "C": {0: {"relation": "STUDIES_WITH"}},
        "Q": {0: {"relation": "FRIENDS_WITH"}},
    }

    unexistent_file = tmpdir.join("idontexist")
    with pytest.raises(FileNotFoundError):
        graph.ChallengeGraph.from_file(unexistent_file.strpath, unexistent_file.strpath)

    assert not g.nodes.get("X")
    property_file2 = tmpdir.join("properties2.txt")
    property_file2.write(
        "ID      Property        Value\n" "X       Name            NLP\n"
    )
    relationships_file2 = tmpdir.join("relationships2.txt")
    relationships_file2.write(
        "Relationship    ID1     Type1   ID2     Type2\n"
        "RESEARCHES      C       Person  X       Field\n"
    )

    # Add new information to the graph
    g.add_properties_from_file(property_file2.strpath)
    g.add_relationships_from_file(relationships_file2.strpath)
    assert g.nodes["X"] == {"Name": "NLP", "Type": "Field"}

    assert g["C"] == {
        "X": {0: {"relation": "RESEARCHES"}},
    }


def test_find_friend_cliques(tmpdir):
    """Test find friend cliques."""
    property_file = tmpdir.join("properties.txt")
    property_file.write(
        "ID      Property        Value\n"
        "A       Name            Frank\n"
        "B       Name            Ally\n"
        "C       Name            Oscar\n"
    )

    relationships_file = tmpdir.join("relationships.txt")
    relationships_file.write(
        "Relationship    ID1     Type1   ID2     Type2\n"
        "FRIENDS_WITH    A       Person  C       Person\n"
        "FRIENDS_WITH    A       Person  B       Person\n"
        "FRIENDS_WITH    B       Person  C       Person\n"
    )

    g = graph.ChallengeGraph.from_file(
        property_file.strpath, relationships_file.strpath
    )
    result = sorted([sorted(c) for c in g.find_friend_cliques()])
    assert result == [
        ["A"],
        ["A", "B"],
        ["A", "B", "C"],
        ["A", "C"],
        ["B"],
        ["B", "C"],
        ["C"],
    ]


def test_find_person_cliques(tmpdir):
    """Test find person cliques."""
    property_file = tmpdir.join("properties.txt")
    property_file.write(
        "ID      Property        Value\n"
        "A       Name            Frank\n"
        "B       Name            Ally\n"
        "C       Name            Oscar\n"
    )

    relationships_file = tmpdir.join("relationships.txt")
    relationships_file.write(
        "Relationship    ID1     Type1   ID2     Type2\n"
        "FRIENDS_WITH    A       Person  C       Person\n"
        "STUDIES_WITH    A       Person  B       Person\n"
        "CLASSMATE       B       Person  C       Person\n"
    )

    g = graph.ChallengeGraph.from_file(
        property_file.strpath, relationships_file.strpath
    )
    result = sorted([sorted(c) for c in g.find_person_cliques()])
    assert result == [
        ["A"],
        ["A", "B"],
        ["A", "B", "C"],
        ["A", "C"],
        ["B"],
        ["B", "C"],
        ["C"],
    ]
