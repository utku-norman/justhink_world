import json
import networkx as nx
import pathlib as pl

# def check_spanning(graph, edges):
#     subgraph = nx.Graph()
#     for u in graph.nodes():
#         subgraph.add_node(u)
#     for u, v in edges:
#         subgraph.add_edge(u, v)

#     return nx.is_connected(subgraph)


def in_undirected_edgeset(u, v, edges):
    return (u, v) in edges or (v, u) in edges


def find_mst(graph, weight_key='cost'):
    '''find a minimum-spanning tree of a the graph'''
    return nx.minimum_spanning_tree(graph, weight=weight_key)


def get_graph_cost(graph, weight_key='cost'):
    '''compute the total cost on the graph'''
    return sum([d[weight_key] for u, v, d in graph.edges(data=True)])


def get_edgelist_cost(graph, edges, weight_key='cost'):
    '''compute the total a selected edgelist on the graph'''
    return sum([graph[u][v][weight_key] for u, v in edges])


def load_graph_from_edgelist(file, nodetype=int):
    '''load a networkx graph from an edgelist file'''
    assert pl.Path(file).is_file()
    try:
        graph = nx.read_edgelist(file, nodetype=nodetype)
    except Exception as e:
        print(e)
    return graph


def load_graph_from_json(file):
    '''load a networkx graph from a json file with node-link formatted graph data'''
    assert pl.Path(file).is_file()
    try:
        # Read json data.
        with file.open('r') as f:
            data = json.load(f)
        # Convert to networkx graph.
        graph = nx.node_link_graph(data)
    except Exception as e:
        print(e)
    return graph
