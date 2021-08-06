import networkx as nx


def in_edges(u, v, edges) -> bool:
    '''Check if an undirected edge is in a collection of undirected edges.

    Args:
        u (str): One node of the edge.
        v (str): the other node of the edge.
        edges (List[tuple]): The list of edges where each edge is a 2-tuple.

    Returns:
        bool: True if exists, False otherwise.
    '''
    return (u, v) in edges or (v, u) in edges


def is_spanning(graph, edges) -> bool:
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


def find_mst(graph, weight_key='cost') -> nx.Graph:
    """Find a minimum-spanning tree for a given graph.

    Args:
        graph (nx.Graph): The graph with a cost function on edges.
        weight_key (str, optional): The attribute key for the weight.
            Defaults to 'cost'.

    Returns:
        bool: True for spanning, False otherwise.
    """
    # TODO: catch exception if weight key is not available.
    return nx.minimum_spanning_tree(graph, weight=weight_key)


def compute_total_cost(graph, weight_key='cost') -> float:
    """Compute the total cost for a given graph.

    Args:
        graph (nx.Graph): The graph with a cost function on edges.
        weight_key (str, optional): The attribute key for the weight.
            Defaults to 'cost'.

    Returns:
        float: the cost.
    """
    # TODO: catch exception if weight key is not available for that edge.
    return sum([d[weight_key] for u, v, d in graph.edges(data=True)])


def compute_selected_cost(graph, edges, weight_key='cost') -> float:
    """Compute the total cost on the selected edges for a given graph.

    Args:
        graph (nx.Graph): The graph with a cost function on edges.
        edges (List[tuple]): The list of edges where each edge is a 2-tuple.

    Returns:
        float: the cost.
    """
    # TODO: catch exception if weight key is not available for that edge.
    # TODO: catch exception of an edge is not in the graph.
    return sum([graph[u][v][weight_key] for u, v in edges])
