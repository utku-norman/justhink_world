import pomdp_py

from ..tools.networks import find_mst, is_spanning, \
    compute_total_network_cost, compute_selected_network_cost


class State(pomdp_py.State):
    """
    A class used to represent a world state
    for a minimum-spanning tree problem

    Attributes:
        network (networkx.Graph):
           the background network with a cost function on edges
        edges (set, optional):
           the set of selected edges in the network (default frozenset())
        terminal (bool, optional)
           whether the state is a final/terminal state (default False)
    """

    def __init__(self,
                 network,
                 edges=frozenset(),
                 suggested=None,
                 submit_suggested=False,
                 terminal=False):
        """Initialise a world state for a minimum-spanning tree problem."""
        self.network = network
        self.edges = edges
        self.suggested = suggested
        self.submit_suggested = submit_suggested
        self.terminal = terminal

    def __hash__(self):
        return hash((self.network,
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
            self.network.number_of_nodes(),
            self.network.number_of_edges(),
            len(self.edges),
            self.get_cost(),
            self.is_spanning(),
            self.terminal)

    def clear_selection(self):
        """Clear the selected edges."""
        self.edges = frozenset()

    def reset(self):
        """Clear the selected edges and the flags."""
        self.clear_selection()
        self.terminal = False
        self.suggested = None

    def get_cost(self) -> float:
        """Compute the total cost on the selected edges.

        Returns:
            float: the cost.
        """
        return compute_selected_network_cost(self.network, self.edges)

    def get_mst_cost(self) -> float:
        """Compute the cost of a minimum-spanning tree of the state's network.

        Returns:
            bool: The return value. True for success, False otherwise.
        """
        mst = find_mst(self.network)
        return compute_total_network_cost(mst)

    def get_max_cost(self) -> float:
        """Compute the total cost on the state's network.

        Returns:
            float: the cost.
        """
        return compute_total_network_cost(self.network)

    def is_spanning(self) -> bool:
        """Check if the selected edges spans the state's network.

        Returns:
            bool: True for spanning, False otherwise.
        """
        return is_spanning(self.network, self.edges)

    def is_mst(self) -> bool:
        """Check if the selected edges is an MST (minimum-spanning tree).

        Returns:
            bool: True for MST, False otherwise.
        """
        if self.is_spanning():
            opt_cost = self.get_mst_cost()
            return self.get_cost() == opt_cost
        return False
