import copy

import pomdp_py

import networkx as nx

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
                 agents={HumanAgent, RobotAgent},
                 attempt_no=1,
                 max_attempts=None,
                 is_submitting=False,
                 is_paused=False,
                 is_terminal=False):
        self.network = network
        self.layout = layout

        self.agents = agents

        self.attempt_no = attempt_no
        self.max_attempts = max_attempts

        self.is_submitting = is_submitting

        self.is_paused = is_paused
        self.is_terminal = is_terminal

    def __hash__(self):
        return hash((self.network,
                     self.layout,
                     self.attempt_no,
                     self.max_attempts,
                     self.is_submitting,
                     self.is_paused,
                     self.is_terminal))
        # TODO update

    def __eq__(self, other):
        if isinstance(other, NetworkState):
            return (self.edges == other.edges)
        else:
            return False

    def __deepcopy__(self, memo, shared_attribute_names={'layout'}):
        """Create a copy of the state with shared attributes.

        Specifically, the layout is shared.
        Overriding follows https://stackoverflow.com/a/15774013"""
        cls = self.__class__
        result = cls.__new__(cls)
        memo[id(self)] = result
        for k, v in self.__dict__.items():
            if k in shared_attribute_names:
                setattr(result, k, copy.copy(v))
            else:
                setattr(result, k, copy.deepcopy(v, memo))
        return result

    def __str__(self):
        return self.__repr__()

    def __repr__(self):
        s = 'EnvState({},a:{};p:{:d},t:{:d},s:{:d})'.format(
            self.network,
            self.agents,
            self.is_paused,
            self.is_terminal,
            self.is_submitting)
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

    def get_selected_nodes(self):
        return {u for e in self.edges for u in e}

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
        mst = self.get_mst()
        return compute_total_cost(mst)

    def get_mst(self) -> nx.Graph:
        """Get a minimum-spanning tree of the state's network.

        Returns:
            nx.Graph: A m
        """
        return find_mst(self.graph)

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
