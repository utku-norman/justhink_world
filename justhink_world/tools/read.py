import sys
import copy
import json
import pickle

import pyglet
import importlib_resources
import networkx as nx
import pathlib as pl

from ..domain.state import NetworkState


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


def load_all_logs(log_resource='justhink_spring21_transition_lists.pickle'):

    # Create a container for the image resources.
    data_container = importlib_resources.files(
        'justhink_world.resources.data')

    with data_container.joinpath(log_resource) as log_file:
        with log_file.open('rb') as handle:
            logs = pickle.load(handle)

    return logs


def load_log(sample_no, world_name):
    """TODO"""
    try:
        logs = load_all_logs()
        log_df = logs[sample_no][world_name]
        return log_df
    except Exception as e:
        print(e)
        raise ValueError


def load_network(graph_file, layout_file, verbose=False):
    """Load a world from its resource files."""

    # Load the graph.
    graph = load_graph_from_edgelist(graph_file)

    # Load the layout.
    layout = load_graph_from_json(layout_file)

    # Print debug message on the graph and the layout.
    if verbose:
        print('Using graph: {} with layout: {}'.format(
            graph_file.name, layout_file.name))

    # Fill in the possible edges and their attributes (e.g. cost).
    full_graph = copy.deepcopy(layout)
    for u, v, d in graph.edges(data=True):
        full_graph.add_edge(u, v, **d)

    network = NetworkState(graph=full_graph)

    return network


def load_image_from_reference(ref):
    """Read pyglet image from importlib reference."""
    with importlib_resources.as_file(ref) as file:
        return pyglet.image.load(file)




def make_network_resources(name):
    """Construct a world's resource file names by the world's name."""
    # Create a container for the world sources.
    package = importlib_resources.files('justhink_world.resources.networks')

    # Make the source file names.
    graph_file = '{}_edgelist.txt'.format(name)
    layout_file = '{}_layout.json'.format(name)

    # Make the sources.
    # Create a container for the world sources.
    graph_resource = package.joinpath(graph_file)
    layout_resource = package.joinpath(layout_file)

    # Check if the sources are available.
    for source in [graph_resource, layout_resource]:
        try:
            assert source.exists()
        except AssertionError:
            print('Resource file {} does not exist for world "{}".'.format(
                source, name))
            sys.exit(1)

    return {'graph': graph_resource, 'layout': layout_resource}
