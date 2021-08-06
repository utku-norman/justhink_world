import pomdp_py

from ..tools.networks import find_mst, is_spanning, \
    compute_total_cost, compute_selected_cost

from ..agent.agent import HumanAgent, RobotAgent


class Button(object):
    """for button states"""
    NA = 'N'
    ENABLED = 'E'
    DISABLED = 'D'
    SELECTED = 'S'


class EnvironmentState(pomdp_py.State):
    """TODO

    Attributes:
        TODO
        is_terminal (bool, optional)
           whether the state is a final or terminal state,
           to designate the end of the activity (default False)
    """

    def __init__(self,
                 network,
                 layout,
                 active_agents={HumanAgent, RobotAgent},
                 submit_button=Button.NA,
                 clear_button=Button.NA,
                 yes_button=Button.NA,
                 no_button=Button.NA,
                 is_paused=False,
                 is_terminal=False):
        self.network = network
        self.layout = layout

        self.active_agents = active_agents

        self.submit_button = submit_button
        self.clear_button = clear_button
        self.yes_button = yes_button
        self.no_button = no_button

        self.is_paused = is_paused
        self.is_terminal = is_terminal

    def __hash__(self):
        return hash((self.network,
                     self.layout,
                     self.submit_button,
                     self.clear_button,
                     self.yes_button,
                     self.no_button))

    def __eq__(self, other):
        if isinstance(other, NetworkState):
            return (self.edges == other.edges)
        else:
            return False

    def __str__(self):
        return self.__repr__()

    def __repr__(self):
        s = 'EnvState({},a:{},s:{},c:{},y:{},n:{};p:{:d},t:{:d})'.format(
            self.network,
            self.active_agents,
            self.submit_button,
            self.clear_button,
            self.yes_button,
            self.no_button,
            self.is_paused,
            self.is_terminal)
        return s


class NetworkState(object):
    """A class used to represent the network's state.

    Attributes:
        graph (networkx.Graph):
           the background network with a cost function on edges
        edges (set, optional):
           the set of selected edges in the network
           (default to an empty set: frozenset())
        suggested_edge (tuple or None, optional)
            a suggested edge, e.g. (1, 2) (default None)
        is_submitting (bool, optional)
            True if an agent suggested to submit, False otherwise
            (default False)
    """

    def __init__(self,
                 graph,
                 edges=frozenset(),
                 suggested_edge=None):
        """Initialise a world state for a minimum-spanning tree problem."""
        self.graph = graph
        self.edges = edges
        self.suggested_edge = suggested_edge

    def __hash__(self):
        return hash((self.graph,
                     self.edges,
                     self.suggested_edge))

    def __eq__(self, other):
        if isinstance(other, NetworkState):
            return (self.edges == other.edges)
        else:
            return False

    def __str__(self):
        return self.__repr__()

    def __repr__(self):
        return 'NetworkState(e:{}+{},c:{}|n:{},e:{};s:{:d})'.format(
            len(self.edges),
            0 if self.suggested_edge is None else 1,
            self.get_cost(),
            self.graph.number_of_nodes(),
            self.graph.number_of_edges(),
            self.is_spanning())

    # def clear_selection(self):
    #     """Clear the selected edges."""
    #     self.edges = frozenset()

    def clear(self):  # reset
        """Clear the selected edges and the flags."""
        # self.clear_selection()
        self.edges = frozenset()
        self.suggested_edge = None

    def get_cost(self) -> float:
        """Compute the total cost on the selected edges.

        Returns:
            float: the cost.
        """
        return compute_selected_cost(self.graph, self.edges)

    def get_mst_cost(self) -> float:
        """Compute the cost of a minimum-spanning tree of the state's network.

        Returns:
            bool: The return value. True for success, False otherwise.
        """
        mst = find_mst(self.graph)
        return compute_total_cost(mst)

    def get_max_cost(self) -> float:
        """Compute the total cost on the state's network.

        Returns:
            float: the cost.
        """
        return compute_total_cost(self.graph)

    def is_spanning(self) -> bool:
        """Check if the selected edges spans the state's network.

        Returns:
            bool: True for spanning, False otherwise.
        """
        return is_spanning(self.graph, self.edges)

    def is_mst(self) -> bool:
        """Check if the selected edges is an MST (minimum-spanning tree).

        Returns:
            bool: True for MST, False otherwise.
        """
        if self.is_spanning():
            opt_cost = self.get_mst_cost()
            return self.get_cost() == opt_cost
        return False
