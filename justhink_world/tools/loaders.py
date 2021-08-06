import json
import networkx as nx
import pathlib as pl


def load_graph_from_edgelist(file, nodetype=int):
    """Load a networkx networkx from an edgelist file."""
    assert pl.Path(file).is_file()
    try:
        network = nx.read_edgelist(file, nodetype=nodetype)
    except Exception as e:
        print(e)
    return network


def load_graph_from_json(file):
    """Load a network from a json file with node-link data format."""
    assert pl.Path(file).is_file()
    try:
        # Read json data.
        with file.open('r') as f:
            data = json.load(f)
        # Convert to networkx network.
        network = nx.node_link_graph(data)
    except Exception as e:
        print(e)
    return network
