# Graph Playground

## Overview

Playing a little bit with graphs and visualization. For more info about the API and how they work, pleae check the [documentation](https://dpalmasan.github.io/graph-tools-playground).

## Approach

Current approach is naive, basically we consume data from files, and add to the graph in a batch approach. The files we consume contain information about Entities (each vertex in the graph) and relationships (edges in the graph). If more information is needed to be added to the graph, that is also possible, loading more files into the graph. You can check `tests/test_graph` to check how the approach work with mock data. 

As any python object, if the graph need to be persistent, it can be serialized into a [pickle](https://docs.python.org/3/library/pickle.html) object. Moreover, as the graph is a subclass of a graph from the [networkx](https://networkx.org/) library, it can be [serialized](https://networkx.org/documentation/stable/reference/readwrite/index.html) in several fashions.

As it might be seen, the approach is naive but simple; It assumes that the data will fit in memory. There are multiple approaches to serialize a graph, one could be storing the property tables and the relationship tables in a relational database. However, the semantics and analysis will be complex as this structure is not particularly friendly with graph data, we would require multiple queries that might be difficult to maintain. We could also use out-of-the box solutions such as [neo4j](https://neo4j.com/).

Nevertheless, if we'd like to scale up graph analysis, even using out-of-the-box solutions might not be appropiate. In some cases, we would need to scale to billion of nodes, and thus, require distributed processing. In that case, the solution turns out to be more complex as we would require a distributed approach to process the graph. In such cases, we could use already made solutions, for example using a Bulk Synchronous Parallel model to process the graph. Some frameworks already exists, such as [Apache Giraph](https://giraph.apache.org/).


### Running app

The app consists in loading data from `data` folder, and creates a small visualization that can be viewed in a browser. It also performs an analysis, looking for cliques of length 3 or more, to get interesting insights about the data, for example, who has big networks; meaning that they can influence people or events surrounding multiple entities in the network. The approach to get the cliques is also a naive one, as all the cliques are  searched. This is exponential with the number of vertices in the graph, so please, follow the cautions stated in the docs. For more details check [find_person_cliques](https://dpalmasan.github.io/graph-tools-playground/api_reference/graph.html#graph_tools_playground.graph.ChallengeGraph.find_person_cliques) docs, as an example.

Given the complexity of the approach, it is likely it will not scale to big graphs. Here, different approaches might be tried, depending on the graph size:

* Use approximate heuristics (e.g. graph-coloring based ones). This will lead to incomplete results, but at least we will have results.
* Limit the size of cliques to look up. For instance we can just search for k-cliques (heuristically)
* Even using heuristics, some analysis might take too long to process a big amount of data and we might miss deadlines (assuming there are deadlines for the analysis). In such cases, we could try using a distributed approach, for instance using a Bulk Synchronous Parallel model.

The graph rendering will not be performant if the graph increases to million or more nodes. Moreover, visual inspection would not even be useful. In such cases we could take the following approaches:

* Not rendering the full graph, but rendering small patches (this can be done using distributed processing)
* Dimentional reduction techniques (E.g factorizing the adjacency matrix, using more sophisticated approach such as graph2vec)
* Limiting the relationships and the entity types to specific types (however there is the tradeoff of missing some novel connection relationships)

#### Using Docker

* Get the code, your call here (`clone`, `fork` or `download`).
* First you need to build the image: `docker build -t graph-challenge .`
* Run `docker run -p 5000:5000 graph-challenge`
* Go to http://localhost:5000/

#### Locally

I am using `poetry` to manage dependencies, this will require installing [poetry](https://python-poetry.org/). The recommended way to do it, per the docs on Unix based environment is:

`curl -sSL https://raw.githubusercontent.com/python-poetry/poetry/master/get-poetry.py | python -`

Therefore, following these steps should suffice:

* Run `poetry install`
* Check app builds correctly, running unit tests: `poetry run pytest tests/`
* To run the app `poetry run python app.py`, and then go to http://localhost:5000/

## Thoughts and Nice to Haves

Performance testing would be nice to empirically get an operation characteristic for the scalability of the solution. The most expensive operation is enumerating the cliques, which is based on a modification of [Genome-scale computational approaches to memory-intensive applications in systems biology](https://laur.lau.edu.lb:8443/xmlui/handle/10725/5407). Nevertheless, the performance testing result of the paper gives us an insight on how will perform our solution, and up to which size of the network it might scale. The way to add performance testing could be generating a graph (or using existing graphs) and get an estimate of performance as a function of `N`, where `N` is the number of nodes. We already know beforehand that our current approach will be exponential in time, but we can get an estimate of how big can be `N` for the solution to be useful. Moreover, having this benchmark allows us to optimize the cliques functions (e.g. using heuristics or approximations), and we can get a ratio of improvement in time.

Regarding build and deploy, would be nice testing the library in isoltation. This can be achieved using [Tox](https://tox.readthedocs.io/en/latest/).

Finally, as a self-feedback, the most difficult part for me to implement was the interactive visualization, as I was not familiar with frameworks that could ease the development for graph drawings. The approach for me to implement this, was looking through documentation and checking if any of the libraries I know, had support for graph visualization (in my case, `plotly` did the trick!).
