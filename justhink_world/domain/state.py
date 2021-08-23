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
                    'world': self._create_view(graph),
                    'you': {
                        'world': self._create_view(graph),
                        'me': {
                            'world': self._create_view(graph),
                        }

                    },
                }
            }
        else:
            self.beliefs = {
                'me': {
                    'world': self._create_view(graph),
                }
            }
        self.cur_node = None

    def _create_view(self, from_graph):
        # graph = copy.deepcopy(from_graph) for u, v, d in graph.edges
        # (data=True): d['is_opt'] = None

        # About choices.
        d = {'is_opt': None}

        graph = nx.Graph()
        for u, v in from_graph.edges():
            graph.add_edge(u, v, **d)

        # About strategies.
        graph.graph['me'] = None
        graph.graph['you'] = None

        return graph

    def __str__(self):
        return self.__repr__()

    def __repr__(self):
        return 'MentalState({})'.format(self.get_beliefs())

    def get_beliefs(self):
        belief_list = list()
        # beliefs = self.beliefs['me']['you']
        pairs = [('world', self.beliefs['me']),
                 ('you', self.beliefs['me']['you']),
                 ('me-by-you', self.beliefs['me']['you']['me'])]
        for key, beliefs in pairs:
            for u, v, d in beliefs['world'].edges(data=True):
                value = d['is_opt']
                if value is not None:
                    belief_list.append(('you', u, v, value))

        return sorted(belief_list)


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

    def get_edge_name(self, edge) -> tuple:
        """Construct the name of an edge e.g. (Montreux, Neuchatel).

        Attributes:
            edge (tuple):
                an edge in the graph.
        Returns:
            tuple: name of an edge by the node name pair (Montreux, Neuchatel.
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
        is_highlighted (bool, optional):
           whether the cost labels, node names etc. are higlighted e.g.
           to emphasise on the cost in the demo (default False)
    """

    def __init__(
            self, network, agents=frozenset({Human, Robot}),
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
        agents_str = ''.join([a.name[0] for a in self.agents]) \
            if len(self.agents) > 0 else 'x'
        attempt_str = 'inf' if self.max_attempts is None else self.max_attempts

        s = 'EnvironmentState('
        s += '{}@{}/{},a:{};p:{:d},t:{:d},s:{:d},h:{:d})'.format(
            self.network, self.attempt_no, attempt_str, agents_str,
            self.is_paused, self.is_terminal, self.is_submitting,
            self.is_highlighted)

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


# class MentalState():  # pomdp_py.State):
#     def __init__(self, graph, probs, step=0):
#         self.graph = graph
#         self.probs = probs
#         self.step = step
#         # super().__init__()

#     # def __hash__(self):
#     #     # tuple casting could be very inefficient!
#     #     return hash((self.graph, tuple(self.edges)))
#     #     # return hash((self.graph, self.subgraph))

#     # def __eq__(self, other):
#     #     if isinstance(other, WorldState):
#     #         return self.edges == other.edges
#     #     else:
#     #         return False

#     # def __str__(self):
#     #     return self.__repr__()

#     # def __repr__(self):
#     #     return 'WorldState(n:{}, e:{} | e:{}, cost:{},
# spanning:{}, terminal:{})'.format(
#     #         self.graph.number_of_nodes(),
#     #         self.graph.number_of_edges(),
#     #         len(self.edges),
#     #         self.get_cost(),
#     #         self.is_spanning(),
#     #         self.terminal)


# def make_choice_index(action):
#     if action is None:
#         return None, None
#     if action.agent_name == 'human':
#         target = 'other'
#         key = make_edge_key(level=1, context='choice')
#     elif action.agent_name == 'robot':
#         target = 'self'
#         key = make_edge_key(level=2, context='choice')
#     else:
#         print('Unknown agent: {}'.format(action.agent_name))
#     return target, key


# def make_strategy_index(action, level=0):
#     if action is None:
#         return None, None
#     if action.agent_name == 'robot':
#         key = make_edge_key(level=level, context='strategy')
#         target = 'other'
#     elif action.agent_name == 'human':
#         key = make_edge_key(level=level, context='strategy')
#         target = 'self'
#     else:
#         print('Unknown agent: {}'.format(action.agent_name))
#     return target, key


# def update_mental_state_from_plan(problem):
#     state = problem.mental_history[-1]
#     state = copy.deepcopy(state)
#     state.step = state.step + 1

#     # Update state's self-beliefs about correctness of choices.
#     if hasattr(problem.agent, 'tree'):
#         print('##### Updating from plan')
#         root = problem.agent.tree
#         if root is not None:
#             actions = get_actions(root, max_depth=10)  # 7)
#             edges = [a.edge for a in actions if isinstance(a, PickAction)]
#             key = make_edge_key(level=0, context='choice')
#             for u, v, d in state.probs['choices'].edges(data=True):
#                 # print(d)
#                 if in_undirected_edgeset(u, v, edges):
#                     d[key] = 1.0
#                 else:
#                     d[key] = 0.0

#     problem.mental_history.append(state)


# def update_mental_state(problem, action):  # ,  # =None,
#     # ,
#     # edges=set(), is_spanning=False,
#     # terminal=False,
#     # step=0):
#     world_state = problem.env.state
#     # scene.update_state(
#     #     self._problem.env.state.edges,
#     #     self._problem.env.state.is_spanning(),
#     #     self._problem.env.state.terminal,
#     #     self._step,
#     # )

#     # print('Updating mental state step = {}'.format(step))
#     # Save the previous state.
#     state = problem.mental_history[-1]
#     state = copy.deepcopy(state)
#     state.step = state.step + 1

#     # Update the mental state.
#     # state.step = step
#     # Update state's edge list: "about the world".
#     # Add the new edges.
#     for u, v in world_state.edges:
#         if not state.graph.has_edge(u, v):
#             state.graph.add_edge(u, v)
#     # Remove extra edges.
#     for u, v in state.graph.edges():
#         if not in_undirected_edgeset(u, v, world_state.edges):
#             state.graph.remove_edge(u, v)

#     # Update state's L1 and L2 choices.
#     target, key = make_choice_index(action)
#     if isinstance(action, PickAction):
#         u, v = action.edge
#         # d = state.graph.edges[u, v]
#         d = state.probs['choices'].edges[u, v]
#         d[key] = 1.0
#     # elif isinstance(action, SubmitAction):
#     #     for u, v, d in state.graph.edges(data=True):
#     #         if tuple(sorted([u, v])) in self._edges:
#     #             d[key] = 1.0
#     #         else:
#     #             d[key] = 0.0
#     # Update L0 strategy.
#     target, key = make_strategy_index(action, level=0)
#     if isinstance(action, PickAction):
#         delta = 0.2
#         # if key not in state.probs:
#         #     print('Key {} not found'.format(key))
#         #     print(state.probs.keys())
#         p = state.probs[key][target]
#         if action.quality == 'optimal':
#             p = p + delta
#             if p > 1.0:
#                 p = 1.0
#         else:  # 'sub-optimal'
#             p = p - delta
#             if p < 0.0:
#                 p = 0.0
#         state.probs[key][target] = p
#     elif isinstance(action, SubmitAction):
#         delta = 0.2
#         p = state.probs[key][target]
#         if world_state.terminal:
#             p = p + delta
#             if p > 1.0:
#                 p = 1.0
#         else:  # 'sub-optimal'
#             p = p - delta
#             if p < 0.0:
#                 p = 0.0
#         state.probs[key][target] = p
#     # Update L0, L1, L2 self-or-other.
#     levels = [0, 1, 2]
#     for level in levels:
#         target, key = make_strategy_index(action, level=level)
#         if isinstance(action, SubmitAction):
#             delta = 0.3
#             p = state.probs[key][target]
#             if world_state.terminal:
#                 p = p + delta
#                 if p > 1.0:
#                     p = 1.0
#             else:  # 'sub-optimal'
#                 p = p - delta
#                 if p < 0.0:
#                     p = 0.0
#             state.probs[key][target] = p

#     problem.mental_history.append(state)


# def make_edge_key(level, context='world'):
#     return 'L{}-{}'.format(level, context)


# # class SolutionBeliefState(pomdp_py.State):
# #     def __init__(self, optimal_edges):
# #         '''optimal_edges is a dict from edges to a probability'''
# #         self.optimal_edges = optimal_edges

# #     def __hash__(self):
# #         # tuple casting could be very inefficient!
# #         return hash((tuple(self.optimal_edges)))
# #         # return hash((self.graph, self.subgraph))

# #     def __eq__(self, other):
# #         if isinstance(other, SolutionBeliefState):
# #             return self.optimal_edges == other.optimal_edges
# #         else:
# #             return False

# #     def __str__(self):
# #         return self.__repr__()

# #     def __repr__(self):
# #         # return 'State(n:{}, e:{} | e:{})'.format(
# #         #     self.graph.number_of_nodes(),
# #         #     self.graph.number_of_edges(),
# #         #     len(self.edges))
# #         return 'SolutionBeliefState(e:{}, optimal e:{})'.format(
# #             len(optimal_edges), sum(list(optimal_edges.items())))
