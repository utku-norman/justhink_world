import copy

import pomdp_py

import networkx as nx

from ..tools.networks import find_mst, is_spanning, \
    compute_total_cost, compute_selected_cost

from ..agent.agent import AgentSet, HumanAgent, RobotAgent


class Edge(object):
    """An undirected edge"""
    def __init__(self, u, v):
        self.u = u
        self.v = v

class Button(object):
    """A class used to represent an abstract button and its possible states.

    Attributes:
        NA:
            the button not available and is not displayed.
        ENABLED:
            the button is available and e.g. can be pressed to
            trigger an action.
        DISABLED:
            the button is shown, but e.g. grayed out, to indicate it was
            and/or will become available during the interaction
        SELECTED:
            the button is "selected", e.g. to indicate that the current
            solution is submitted for a submit button
    """
    NA = 'N'
    ENABLED = 'E'
    DISABLED = 'D'
    SELECTED = 'S'


class EnvironmentState(pomdp_py.State):
    """A class to represent the JUSThink environment's state.

    Attributes:
        network (NetworkState):
            the state of the network, that contains the background graph,
            the selected edges etc.
        layout (networkx.Graph):
            the layout of the network, that contains the node names, positions,
            and image file names of the nodes etc.
        agents (AgentSet, optional):
            the set of "active" agents that can are allowed to take actions
            in the environment (default AgentSet(HumanAgent, RobotAgent))
        attempt_no (int, optional):
            the current attempt number starting from 1 up to and including
            max_attempts (default 1). Can do infinitely many submissions,
            which is kept track of by the transition model operating
            on this state (default 1).
        max_attempts (int, optional):
            the maximum number of attempts allowed from this state onwards
            (default None)
        is_submitting (bool, optional):
            whether an agent is currently submitting by attempting to submit
            so that a confirmation box opens (default False)
        is_paused (bool, optional):
            whether the state is "paused" e.g. by intervention or
            by a pausing action for instance by the robot, so that is no agent
            is allowed to take an action, except for unpausing (default False)
        is_terminal (bool, optional):
           whether the state is a final or terminal state,
           to designate the end of the activity (default False)
    """

    def __init__(self,
                 network,
                 layout,
                 agents=AgentSet([HumanAgent, RobotAgent]),
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
                     self.agents,
                     self.attempt_no,
                     self.max_attempts,
                     self.is_submitting,
                     self.is_paused,
                     self.is_terminal))

    def __eq__(self, other):
        if isinstance(other, self.__class__):
            return self.__dict__ == other.__dict__
        else:
            return False

    def __deepcopy__(self, memo, shared_attribute_names={'layout'}):
        """Create a copy of the state with shared attributes.

        Specifically, the layout is shared.
        Overriding modifies https://stackoverflow.com/a/15774013."""
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
        s = 'EnvState({}@{}/{},a:{};p:{:d},t:{:d},s:{:d})'.format(
            self.network,
            self.attempt_no,
            'inf' if self.max_attempts is None else self.max_attempts,
            self.agents,
            self.is_paused,
            self.is_terminal,
            self.is_submitting)
        return s


class NetworkState(object):
    """A class to represent the solution's state.

    Note:
        This is a minimal representation without the node names,
        positions etc., sufficient to compute the cost of the selected
        network, whether it is optimal or not etc.

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
        if isinstance(other, self.__class__):
            return self.__dict__ == other.__dict__
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
