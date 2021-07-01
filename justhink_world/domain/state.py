import pomdp_py
import networkx as nx

from ..utils.graph_utils import find_mst, get_graph_cost, \
    get_edgelist_cost


class State(pomdp_py.State):
    """
    A class used to represent a world state
    for a minimum-spanning tree problem

    Attributes:
        graph (networkx.Graph):
           the background graph with a cost function on edges
        edges (set, optional):
           the set of selected edges in the network (default frozenset())
        terminal (bool, optional)
           whether the state is a final/terminal state (default False)
    """

    def __init__(self,
                 graph,
                 edges=frozenset(),
                 suggested=None,
                 submit_suggested=False,
                 terminal=False):
        """Initialise a world state for a minimum-spanning tree problem."""
        self.graph = graph
        self.edges = edges
        self.suggested = suggested
        self.submit_suggested = submit_suggested
        self.terminal = terminal

    def __hash__(self):
        return hash((self.graph,
                     self.edges,
                     self.suggested,
                     self.submit_suggested,
                     self.terminal))

    def __eq__(self, other):
        if isinstance(other, State):
            return (self.edges == other.edges)
        else:
            return False

    def __str__(self):
        return self.__repr__()

    def __repr__(self):
        return 'State(n:{},e:{}|e:{},c:{},s:{},t:{})'.format(
            self.graph.number_of_nodes(),
            self.graph.number_of_edges(),
            len(self.edges),
            self.get_cost(),
            self.is_spanning(),
            self.terminal)

    def clear_selection(self):
        """Clear the selected edges."""
        self.edges = frozenset()

    def get_cost(self) -> float:
        """
        Compute the total cost on the selected edges.

        Returns:
            float: the cost.
        """
        return get_edgelist_cost(self.graph, self.edges)

    def get_mst_cost(self) -> float:
        """
        Compute the cost of a minimum-spanning tree of the state's graph.

        Returns:
            bool: The return value. True for success, False otherwise.
        """
        subgraph = find_mst(self.graph)
        return get_graph_cost(subgraph)

    def get_max_cost(self) -> float:
        """
        Compute the total cost on the state's graph.

        Returns:
            float: the cost .
        """
        return get_graph_cost(self.graph)

    def is_spanning(self) -> bool:
        """Check if the selected edges spans the state's graph.

        Returns:
            bool: True for spanning, False otherwise.
        """
        subgraph = self.graph.edge_subgraph(self.edges).copy()
        for u in self.graph.nodes():
            subgraph.add_node(u)
        return nx.is_connected(subgraph)

    def is_mst(self) -> bool:
        """Check if the selected edges is an MST (minimum-spanning tree).

        Returns:
            bool: True for MST, False otherwise.
        """
        if self.is_spanning():
            opt_cost = self.get_mst_cost()
            return self.get_cost() == opt_cost
        return False
