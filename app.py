"""Create a small web app to render a ChallengeGraph."""
from pathlib import Path
from typing import Dict
from typing import Tuple

import dash
import dash_core_components as dcc
import dash_html_components as html
import networkx as nx
import plotly.graph_objs as go

from graph_tools_playground.graph import ChallengeGraph


input_dir = Path("data")
G = ChallengeGraph.from_file(
    input_dir / "entity_properties.txt", input_dir / "entity_relationships.txt"
)

# We are only interested in cliques of length 3 or greater
friend_cliques = list(filter(lambda x: len(x) == 3, G.find_friend_cliques()))
person_cliques = list(filter(lambda x: len(x) == 3, G.find_person_cliques()))

pos = nx.spring_layout(G)


def get_edge_trace(graph: ChallengeGraph, pos: Dict) -> Tuple[go.Scatter, go.Scatter]:
    """Create plotly trace for edges.

    :param graph: Graph to be processe
    :type graph: ChallengeGraph
    :param pos: Dictionary with node positions in the layout
    :type pos: Dict
    :return: Scatter of edges and edges labels
    :rtype: Tuple[go.Scatter, go.Scatter]
    """
    edge_trace = go.Scatter(
        x=[], y=[], line=dict(width=0.5, color="#888"), hoverinfo="none", mode="lines"
    )

    edge_info_trace = go.Scatter(
        x=[],
        y=[],
        mode="text",
        marker_size=0.5,
        text=[],
        textposition="top center",
        hovertemplate="weight: %{text}<extra></extra>",
    )

    for edge in graph.edges(data=True):
        x0, y0 = pos[edge[0]]
        x1, y1 = pos[edge[1]]
        xtext, ytext = (x0 + x1) / 2, (y0 + y1) / 2
        edge_trace["x"] += (x0, x1, None)
        edge_trace["y"] += (y0, y1, None)
        edge_info_trace["x"] += (xtext,)
        edge_info_trace["y"] += (ytext,)
        edge_info_trace["text"] += (edge[2]["relation"],)
    return edge_trace, edge_info_trace


def get_node_trace(graph: ChallengeGraph, pos: Dict) -> go.Scatter:
    """Create node trace for plotly visualization.

    :param graph: Input graph
    :type graph: ChallengeGraph
    :param pos: Dict with the node positions in the layout
    :type pos: Dict
    :return: Plotly scatter of nodes
    :rtype: go.Scatter
    """
    node_trace = go.Scatter(
        x=[],
        y=[],
        text=[],
        mode="markers",
        hoverinfo="text",
        marker=dict(
            showscale=True,
            colorscale="YlGnBu",
            reversescale=True,
            color=[],
            size=10,
            colorbar=dict(
                thickness=15,
                title="Node Connections",
                xanchor="left",
                titleside="right",
            ),
            line=dict(width=2),
        ),
    )

    node_attrs = {}
    for node_info in graph.nodes(data=True):
        node, attrs = node_info
        node_attrs[node] = attrs
        x, y = pos[node]
        node_trace["x"] += tuple([x])
        node_trace["y"] += tuple([y])

    for _, adjacencies in enumerate(graph.adjacency()):
        node_trace["marker"]["color"] += tuple([len(adjacencies[1])])
        node_info = "<br>".join(
            f"{prop}: {value}" for prop, value in node_attrs[adjacencies[0]].items()
        )
        node_info = (
            f"Node ID: {adjacencies[0]}<br># of connections: {len(adjacencies[1]) + 1}<br>"
            f"{node_info}"
        )
        node_trace["text"] += tuple([node_info])
    return node_trace


fig = go.Figure(
    data=[*get_edge_trace(G, pos), get_node_trace(G, pos)],
    layout=go.Layout(
        title="<br>Challenge Graph ",
        titlefont=dict(size=16),
        showlegend=False,
        hovermode="closest",
        margin=dict(b=20, l=5, r=5, t=40),
        annotations=[
            dict(showarrow=False, xref="paper", yref="paper", x=0.005, y=-0.002)
        ],
        xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
        yaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
    ),
)


external_stylesheets = ["https://codepen.io/chriddyp/pen/bWLwgP.css"]
app = dash.Dash(__name__, external_stylesheets=external_stylesheets)

app.layout = html.Div(
    [
        html.Div(dcc.Graph(id="Graph", figure=fig)),
        html.Div(
            className="row",
            children=[
                html.Div(
                    [
                        html.H2("Overall Data"),
                        html.P(f"Num of nodes: {len(G.nodes)}"),
                        html.P(f"Num of edges: {len(G.edges)}"),
                    ],
                    className="three columns",
                ),
                html.Div(
                    [
                        html.H2("Graph Info"),
                        html.H3("Friend Cliques found (size > 3)"),
                        html.P(
                            f"{friend_cliques if friend_cliques else 'No cliques were found'}"
                        ),
                        html.H3("Person Cliques found (size > 3)"),
                        html.P(
                            f"{person_cliques if person_cliques else 'No cliques were found'}"
                        ),
                        html.Div(id="selected-data"),
                    ],
                    className="six columns",
                ),
            ],
        ),
    ]
)


if __name__ == "__main__":
    app.run_server(debug=True)
