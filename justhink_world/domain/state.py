import copy

import pomdp_py
import networkx as nx

from ..tools.network import find_mst, is_subgraph_spanning, \
    compute_total_cost, compute_subgraph_cost
# from ..agent import Agent


class EnvState(pomdp_py.State):
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
        agents (frozenset):
            the set of "active" agents that can are allowed to take actions
            in the environment
        attempt_no (int, optional):
            the current attempt number starting from 1 up to and including
            max_attempts (default 1). Can do infinitely many submissions,
            which is kept track of by the transition model operating
            on this state (default 1).
        max_attempts (int, optional):
            the maximum number of attempts allowed from this state onwards
            (default None)
        step_no (int, optional):
            the current step number, to sequence the Tutorial via a few
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
        is_highlighted (bool, optional):
           whether the cost labels, node names etc. are higlighted e.g.
           to emphasise on the cost in the tutorial (default False)
    """

    def __init__(
            self, network, agents,
            attempt_no=1, max_attempts=None, step_no=1, is_submitting=False,
            is_paused=False, is_terminal=False, is_highlighted=False):
        self.network = network
        self.agents = agents
        self.attempt_no = attempt_no
        self.max_attempts = max_attempts
        self.is_submitting = is_submitting
        self.step_no = step_no
        self.is_paused = is_paused
        self.is_terminal = is_terminal
        self.is_highlighted = is_highlighted

    def __hash__(self):
        return hash(
            (self.network, self.agents, self.attempt_no, self.max_attempts,
                self.step_no, self.is_submitting, self.is_paused,
                self.is_terminal, self.is_highlighted))

    def __eq__(self, other):
        return isinstance(other, self.__class__) \
            and self.__dict__ == other.__dict__

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
        # # compact
        # agents_str = ''.join([a.name[0] for a in self.agents]) \
        #     if len(self.agents) > 0 else 'x'
        # attempt_str = 'inf' if self.max_attempts is None else \
        # self.max_attempts
        # s = 'EnvState('
        # s += '{}@{}/{},a:{};p:{:d},t:{:d},s:{:d},h:{:d})'.format(
        #     self.network, self.attempt_no, attempt_str, agents_str,
        #     self.is_paused, self.is_terminal, self.is_submitting,
        #     self.is_highlighted)

        s = 'Situation({}'.format(self.network)
        if self.max_attempts is not None:
            s += ', attempt={}/{}'.format(
                self.attempt_no, self.max_attempts)
        if len(self.agents) > 0:
            s += ', {}'.format(''.join(self.agents))  # [a.name for a in ]))
        if self.is_paused:
            s += ', paused'
        if self.is_terminal:
            s += ', terminal'
        if self.is_submitting:
            s += ', submitting'
        if self.is_highlighted:
            s += ', highlighted'
        s += ')'

        return s


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
        edge_weight_key (str, optional)
            the key for the cost of an edge in edge attribute dictionary
            (default 'cost')
        node_name_key (str, optional)
            the key for the name of a node in node attribute dictionary
            (default 'text')
    """

    def __init__(self, graph, subgraph=None, suggested_edge=None,
                 edge_weight_key='cost', node_name_key='text'):
        self.graph = graph

        if subgraph is None:
            self.subgraph = nx.Graph()
        self.suggested_edge = suggested_edge

        self._edge_weight_key = edge_weight_key
        self._node_name_key = node_name_key

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
        # return 'NetworkState(e:{}+{},c:{}|n:{},e:{};s:{:d})'.format(
        #     self.subgraph.number_of_edges(),
        #     0 if self.suggested_edge is None else 1,
        #     self.get_cost(), self.graph.number_of_nodes(),
        #     self.graph.number_of_edges(), self.is_spanning())

        extra_info = ''
        num_nodes = self.subgraph.number_of_nodes()

        if num_nodes > 0:
            extra_info += ' where |V\'|={}'.format(num_nodes)
        if self.is_mst():
            extra_info += ' that minimally spans'
        elif self.is_spanning():
            extra_info += ' that spans'
        extra_info += ' with cost={}'.format(self.get_cost())

        return 'Network(|E\'|={}{} in G(|V|={}, |E|={})){}'.format(
            self.subgraph.number_of_edges(),
            '' if self.suggested_edge is None else '+1',
            self.graph.number_of_nodes(), self.graph.number_of_edges(),
            extra_info)

    def get_selected_nodes(self) -> nx.Graph.nodes:
        """Get an iterable for selected nodes from the selection subgraph."""
        return self.subgraph.nodes()

    def get_node_name(self, node, is_shortened=True) -> str:
        """Get the name of a node e.g. "Montreux".

        Attributes:
            node (int):
                a node id in the graph.
            is_shortened (bool, optional)
                Whether to shorten the node name e.g. from
                "Mount Montreux" to "Montreux" (default True)
        Returns:
            str: name of a node e.g. "Montreux" from the node's id e.g. 1.
        """
        if node not in self.graph.nodes:
            print('Node {} not found.'.format(node))
            return None
        name = self.graph.nodes[node][self._node_name_key]
        if is_shortened:
            name = name.split()[-1]
        return name

    def get_node_id(self, name) -> int:
        """Get the id of a node from its name, e.g. "Montreux" to '1'.

        Attributes:
            name (str):
                name of a node in the graph.
        Returns:
            int: id of a node e.g. 1, from the node's name e.g. "Montreux"
        """
        found_id = None
        for node_id in self.graph.nodes:
            node_name = self.graph.nodes[node_id][self._node_name_key]
            if name.lower() in node_name.lower():
                found_id = node_id
                break
        return found_id

    def get_edge_ids(self, edge) -> tuple:
        """Get the ids of the nodes of an edge.

        Attributes:
            edge (tuple):
                node id tuple of an edge in the graph.
        Returns:
            tuple: ids for an edge by the node id pair e.g. (1, 2).
        """
        return (self.get_node_id(edge[0]), self.get_node_id(edge[1]))

    def get_edge_name(self, edge) -> tuple:
        """Construct the name of an edge e.g. (Montreux, Neuchatel).

        Attributes:
            edge (tuple):
                an edge in the graph.
        Returns:
            tuple: name of an edge by the node name pair (Montreux, Neuchatel).
        """
        return self.get_node_name(edge[0]), self.get_node_name(edge[1])

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
            self.graph, self.subgraph, edge_weight_key=self._edge_weight_key)

    def get_mst_cost(self) -> float:
        """Compute the cost of a minimum-spanning tree of the state's network.

        Returns:
            bool: The return value. True for success, False otherwise.
        """
        return compute_total_cost(
            self.get_mst(), edge_weight_key=self._edge_weight_key)

    def get_mst(self) -> nx.Graph:
        """Get a minimum-spanning tree of the state's network.

        Returns:
            nx.Graph: TODO
        """
        return find_mst(self.graph, edge_weight_key=self._edge_weight_key)

    def get_max_cost(self) -> float:
        """Compute the total cost on the state's network.

        Returns:
            float: the cost.
        """
        return compute_total_cost(
            self.graph, edge_weight_key=self._edge_weight_key)

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
        return self.is_spanning() and (self.get_cost() == self.get_mst_cost())
