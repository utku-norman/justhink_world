import networkx as nx


def is_edgelist_spanning(graph, edges) -> bool:
    """Check if the selected edges spans the given graph.

    Args:
        graph (nx.Graph): The graph with a cost function on edges.
        edges (List[tuple]): The list of edges where each edge is a 2-tuple.

    Returns:
        bool: True for spanning, False otherwise.
    """
    subgraph = graph.edge_subgraph(edges).copy()
    for u in graph.nodes():
        subgraph.add_node(u)
    return nx.is_connected(subgraph)


def is_subgraph_spanning(graph, subgraph) -> bool:
    """Check if the selected edges spans the given graph.

    Args:
        graph (nx.Graph): The graph with a cost function on edges.
        edges (List[tuple]): The list of edges where each edge is a 2-tuple.

    Returns:
        bool: True for spanning, False otherwise.
    """
    return is_edgelist_spanning(graph, subgraph.edges)


def find_mst(graph, edge_weight_key='cost') -> nx.Graph:
    """Find a minimum-spanning tree for a given graph.

    Args:
        graph (nx.Graph): The graph with a cost function on edges.
        edge_weight_key (str, optional): The attribute key for the weight.
            Defaults to 'cost'.

    Returns:
        bool: True for spanning, False otherwise.
    """
    return nx.minimum_spanning_tree(graph, weight=edge_weight_key)


def compute_total_cost(graph, edge_weight_key='cost') -> float:
    """Compute the total cost for a given graph.

    Args:
        graph (nx.Graph): The graph with a cost function on edges.
        edge_weight_key (str, optional): The attribute key for the weight.
            Defaults to 'cost'.

    Returns:
        float: the cost.
    """
    return sum([d[edge_weight_key] for u, v, d in graph.edges(data=True)])


def compute_edgelist_cost(graph, edges, edge_weight_key='cost') -> float:
    """Compute the total cost on the selected edges for a given graph.

    Args:
        graph (nx.Graph): The graph with a cost function on edges.
        edges (List[tuple]): The list of edges where each edge is a 2-tuple.

    Returns:
        float: the cost.
    """
    return sum([graph[u][v][edge_weight_key] for u, v in edges])


def compute_subgraph_cost(graph, subgraph, edge_weight_key='cost') -> float:
    """Compute the total cost on the selected edges for a given graph.

    Args:
        graph (networkx.Graph): The graph with a cost function on edges.
        subgraph (networkx.Graph): The subgraph

    Returns:
        float: the cost.
    """
    return compute_edgelist_cost(
        graph, subgraph.edges, edge_weight_key=edge_weight_key)


def in_edgelist(u, v, edges) -> bool:
    """Check if an undirected edge is in a collection of undirected edges.

    Args:
        u (str): One node of the edge.
        v (str): the other node of the edge.
        edges (List[tuple]): The list of edges where each edge is a 2-tuple.

    Returns:
        bool: True if exists, False otherwise.
    """
    return (u, v) in edges or (v, u) in edges
