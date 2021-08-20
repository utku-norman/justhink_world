import copy

import pomdp_py

import networkx as nx

from ..tools.networks import find_mst, is_subgraph_spanning, \
    compute_total_cost, compute_subgraph_cost

from ..agent import Human, Robot


class MentalState(object):
    """TODO: docstring for MentalState"""

    def __init__(self, graph, agents=set({Human, Robot})):
        if Human in agents:
            self.beliefs = {
                'me': {
                    'world': self.create_view(graph),
                    'you': {
                        'world': self.create_view(graph),
                        'me': {
                            'world': self.create_view(graph),
                        }

                    },
                }
            }
        else:
            self.beliefs = {
                'me': {
                    'world': self.create_view(graph),
                }
            }

    def create_view(self, from_graph):
        graph = copy.deepcopy(from_graph)
        for u, v, d in graph.edges(data=True):
            d['is_opt'] = None

        return graph


class NetworkState(object):
    """A class to represent a problem's solution network's state.

    Note:
        This is a minimal representation without the node names,
        positions etc., sufficient to compute the cost of the selected
        network, whether it is optimal or not etc.

    Attributes:
        graph (networkx.Graph):
           the background graph with a cost function on edges
        subgraph (networkx.Graph, optional):
           the subgraph of the selected edges (default networkx.Graph())
        suggested_edge (tuple or None, optional)
            a suggested edge, e.g. (1, 2) (default None)
        weight_key (str, optional)
            the key for the cost of an edge in edge attribute dictionary
            (default 'cost')
        name_key (str, optional)
            the key for the name of a node in node attribute dictionary
            (default 'text')
    """

    def __init__(self, graph, subgraph=nx.Graph(), suggested_edge=None,
                 weight_key='cost', name_key='text'):
        self.graph = graph
        self.subgraph = subgraph
        self.suggested_edge = suggested_edge

        self._weight_key = weight_key
        self._name_key = name_key

    def __hash__(self):
        return hash((self.graph, self.subgraph, self.suggested_edge))

    def __eq__(self, other):
        if isinstance(other, self.__class__):
            return self.__dict__ == other.__dict__
        else:
            return False

    def __deepcopy__(self, memo, shared_attribute_names={'graph'}):
        """Create a copy of the state with a set of shared attributes."""
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
        return 'NetworkState(e:{}+{},c:{}|n:{},e:{};s:{:d})'.format(
            self.subgraph.number_of_edges(),
            0 if self.suggested_edge is None else 1,
            self.get_cost(), self.graph.number_of_nodes(),
            self.graph.number_of_edges(), self.is_spanning())

    def get_selected_nodes(self) -> nx.Graph.nodes:
        """Get a set of selected nodes from the selection subgraph."""
        return self.subgraph.nodes()

    def get_node_name(self, node, is_shortened=True) -> str:
        """Get the name of a node e.g. "Montreux".

        Attributes:
            node (int or str):
                a node in the graph.
            is_shortened (bool, optional)
                Whether to shorten the node name e.g. from
                "Mount Montreux" to "Montreux" (default True)
        Returns:
            str: name of an edge e.g. "Montreux to Neuchatel".
        """
        name = self.graph.nodes[node][self._name_key]
        if is_shortened:
            name = name.split()[-1]
        return name

    def get_edge_name(self, edge) -> str:
        """Construct the name of an edge e.g. "Montreux to Neuchatel".

        Attributes:
            edge (tuple):
                an edge in the graph.
        Returns:
            str: name of an edge e.g. "Montreux to Neuchatel".
        """
        u, v = edge[0], edge[1]
        u_name = self.get_node_name(u)
        v_name = self.get_node_name(v)
        return '{} to {}'.format(u_name, v_name)

    def clear(self):
        """Clear the selected edges and the flags."""
        self.subgraph = nx.Graph()
        self.suggested_edge = None

    def get_cost(self) -> float:
        """Compute the total cost on the selected edges.

        Returns:
            float: the cost.
        """
        return compute_subgraph_cost(
            self.graph, self.subgraph, weight_key=self._weight_key)

    def get_mst_cost(self) -> float:
        """Compute the cost of a minimum-spanning tree of the state's network.

        Returns:
            bool: The return value. True for success, False otherwise.
        """
        mst = self.get_mst()
        return compute_total_cost(mst, weight_key=self._weight_key)

    def get_mst(self) -> nx.Graph:
        """Get a minimum-spanning tree of the state's network.

        Returns:
            nx.Graph: TODO
        """
        return find_mst(self.graph, weight_key=self._weight_key)

    def get_max_cost(self) -> float:
        """Compute the total cost on the state's network.

        Returns:
            float: the cost.
        """
        return compute_total_cost(self.graph, weight_key=self._weight_key)

    def is_spanning(self) -> bool:
        """Check if the selected edges spans the state's network.

        Returns:
            bool: True for spanning, False otherwise.
        """
        return is_subgraph_spanning(self.graph, self.subgraph)

    def is_mst(self) -> bool:
        """Check if the selected edges is an MST (minimum-spanning tree).

        Returns:
            bool: True for MST, False otherwise.
        """
        if self.is_spanning():
            opt_cost = self.get_mst_cost()
            return self.get_cost() == opt_cost
        return False


class EnvironmentState(pomdp_py.State):
    """A class to represent a JUSThink world's environment's state.

    Contains information on the current solution (i.e. the network),
    the agents that can take actions (for turn-taking), the current attempt
    number etc.
    It is manipulated via state transitions by a transition model.
    It is used to generate the available actions by a policy model.

    Attributes:
        network (NetworkState):
            the state of the network, that contains the background graph,
            the selected edges etc.
            the layout of the network, that contains the node names, positions,
            and image file names of the nodes etc.
        agents (frozenset, optional):
            the set of "active" agents that can are allowed to take actions
            in the environment (default frozenset({Human, Robot}))
        attempt_no (int, optional):
            the current attempt number starting from 1 up to and including
            max_attempts (default 1). Can do infinitely many submissions,
            which is kept track of by the transition model operating
            on this state (default 1).
        max_attempts (int, optional):
            the maximum number of attempts allowed from this state onwards
            (default None)
        step_no (int, optional):
            the current step number, to sequence the demo via a few
            intstruction steps, and to indicate the action count for an
            individual or collaborative activity (default 1)
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

    def __init__(
            self, network, agents=frozenset({Human, Robot}),
            attempt_no=1, max_attempts=None, step_no=1, is_submitting=False,
            is_paused=False, is_terminal=False):
        self.network = network
        self.agents = agents
        self.attempt_no = attempt_no
        self.max_attempts = max_attempts
        self.is_submitting = is_submitting
        self.step_no = step_no
        self.is_paused = is_paused
        self.is_terminal = is_terminal

    def __hash__(self):
        return hash(
            (self.network, self.agents, self.attempt_no, self.max_attempts,
                self.step_no, self.is_submitting, self.is_paused,
                self.is_terminal))

    def __eq__(self, other):
        if isinstance(other, self.__class__):
            return self.__dict__ == other.__dict__
        else:
            return False

    def __deepcopy__(self, memo, shared_attribute_names={}):
        """Create a copy of the state with a set of shared attributes."""
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
        if len(self.agents) > 0:
            agents_string = ''.join([a.name[0] for a in self.agents])
        else:
            agents_string = 'x'

        s = 'EnvironmentState({}@{}/{},a:{};p:{:d},t:{:d},s:{:d})'.format(
            self.network,
            self.attempt_no,
            'inf' if self.max_attempts is None else self.max_attempts,
            agents_string,
            self.is_paused,
            self.is_terminal,
            self.is_submitting)
        return s


class Button(object):
    """A class to represent an abstract button and its possible states.

    Attributes:
        NA:
            the button is not available and will not be displayed.
        ENABLED:
            the button is available, e.g. can be pressed to trigger an action.
        DISABLED:
            the button is shown, but e.g. is grayed out, to indicate it was
            and/or will become available during the interaction
        SELECTED:
            the button is "selected", e.g. for a submit button, to indicate
            that the current solution is submitted for a submit button
    """
    NA = 'N'
    ENABLED = 'E'
    DISABLED = 'D'
    SELECTED = 'S'
