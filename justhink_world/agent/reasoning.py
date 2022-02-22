from justhink_world.domain.action import SuggestPickAction, AttemptSubmitAction

from justhink_world.agent import Agent

from pqdict import PQDict


# class TraversalPlanner(object):
#     """Define a greedy traversal planner.

#     It will produce a suboptimal result."""

#     def __init__(self, state, start=None):
#         self.state = state

#         if start is None:
#             available_starts = sorted(state.network.graph.nodes())
#             self.cur_node = available_starts[0]
#         else:

#             self.cur_node = start

#         self.last_explanation = None

#     def plan(self, agent):
#         """Select the next action by greedy traversal planning."""
#         # Select greedy.
#         self.state = agent.cur_belief.mpe()
#         self.cur_node = agent.cur_state.cur_node

#         # v = None
#         # note_iter = iter(state.graph.nodes)
#         # while v is None and (len(state.graph.edges)
#         # < state.graph.number_of_edges()-1):
#         # expl, min_v, alternatives = get_greedy_neighbour(
#         min_nodes, other_nodes = get_greedy_neighbour(
#             self.state.network.graph, self.cur_node,
#             self.state.network.subgraph)

#         # Make an explanation in terms of actions.
#         expl = BetterThanExplanation()
#         if len(min_nodes) == 0:
#             expl = ConnectedExplanation()
#             expl.best = {AttemptSubmitAction(agent=Agent.ROBOT)}
#         else:
#             expl.best = {SuggestPickAction((self.cur_node, u), agent=Agent.ROBOT)
#                          for u in min_nodes}
#             expl.others = {SuggestPickAction((self.cur_node, u), agent=Agent.ROBOT)
#                            for u in other_nodes}
#             # expl.others = {SuggestPickAction((self.cur_node, u), agent=Agent.ROBOT)
#             #                for u in expl.others}
#             # expl.best = SuggestPickAction((self.cur_node, v), agent=Agent.ROBOT)

#         # Choose the action.
#         action = sorted(expl.best)[0]
#         self.last_explanation = expl

#         return action


class TraversalJumpingPlanner(object):
    """Define a greedy traversal jumping planner.
    Instead of submitting, it will go around and try to continue connecting.

    It will produce a suboptimal result."""

    def __init__(self, state, start=None):
        self.state = state

        if start is None:
            available_starts = sorted(state.network.graph.nodes())
            if 3 in available_starts:
                self.cur_node = 3
            else:
                self.cur_node = available_starts[0]
        else:
            self.cur_node = start

        self.last_explanation = None
        self.last_plan = None

    def plan(self, state, cur_node):  # agent):
        """Select the next action by greedy traversal planning."""
        # Select greedy.
        # self.state = agent.cur_belief.mpe()
        # self.cur_node = agent.cur_state.cur_node
        self.state = state
        self.cur_node = cur_node

        # v = None
        # note_iter = iter(state.graph.nodes)
        # while v is None and (len(state.graph.edges)
        # < state.graph.number_of_edges()-1):
        # expl, min_v, alternatives = get_greedy_neighbour(
        min_nodes, other_nodes = get_greedy_neighbour(
            self.state.network.graph, self.cur_node,
            self.state.network.subgraph)

        # Decide to pick an edge if any, instead of submitting.
        if len(min_nodes) == 0:
            # For each selected node.
            for u in sorted(self.state.network.get_selected_nodes()):
                # Move the current.
                self.cur_node = u
                # agent.cur_state.cur_node = u #############
                # For each available action.
                min_nodes, other_nodes = get_greedy_neighbour(
                    self.state.network.graph, self.cur_node,
                    self.state.network.subgraph)
                if len(min_nodes) != 0:
                    break

        # Make an explanation in terms of actions.
        expl = BetterThanExplanation()
        if len(min_nodes) == 0:
            expl = ConnectedExplanation()
            expl.best = {AttemptSubmitAction(agent=Agent.ROBOT)}
        else:
            expl.best = {SuggestPickAction((self.cur_node, u), agent=Agent.ROBOT)
                         for u in min_nodes}
            expl.others = {SuggestPickAction((self.cur_node, u), agent=Agent.ROBOT)
                           for u in other_nodes}
            # expl.others = {SuggestPickAction((self.cur_node, u), agent=Agent.ROBOT)
            #                for u in expl.others}
            # expl.best = SuggestPickAction((self.cur_node, v), agent=Agent.ROBOT)

        # Choose the action.
        action = sorted(expl.best)[0]

        self.last_explanation = expl
        self.last_plan = action

        return action


def get_greedy_neighbour(graph, u, excluded_subgraph):
    """TODO: Docstring."""
    # Default explanation template.
    # expl = BetterThanExplanation()

    # Find a minimum cost neighbour.
    min_cost = None
    min_nodes = set()
    other_nodes = set()

    # Find the min cost.
    for v in graph.neighbors(u):
        cost = graph.edges[u, v]['cost']
        if not excluded_subgraph.has_edge(u, v):
            if min_cost is None or cost < min_cost:
                min_cost = cost

    # Find the list of optimal/minimum and suboptimal nodes.
    for v in graph.neighbors(u):
        if not excluded_subgraph.has_edge(u, v):
            cost = graph.edges[u, v]['cost']
            if cost == min_cost:
                min_nodes.add(v)
            else:
                other_nodes.add(v)

    return min_nodes, other_nodes


class PrimsPlanner():
    """Define a Prim's (or JPD (Jarnik/Prim/Dijkstra)) planner."""

    def __init__(self, state, start=None):
        self.state = state

        if start is None:
            available_starts = sorted(state.network.graph.nodes())
            if 3 in available_starts:
                self.cur_node = 3
            else:
                self.cur_node = available_starts[0]
        else:
            self.cur_node = start

        self.last_explanation = None
        self.last_plan = None

    def plan(self, state, cur_node):  # agent):
        """Select the next action by Prim's planning."""
        # Select greedy.
        # self.state = agent.cur_belief.mpe()
        # self.cur_node = agent.cur_state.cur_node
        self.state = state
        self.cur_node = cur_node

        expl, min_edges = get_prims_pick(
            self.state.network.graph, self.cur_node, 
            self.state.network.subgraph.edges())

        # Refine the explanation in terms of actions.
        if min_edges is None:
            expl = ConnectedExplanation()
            expl.best = {AttemptSubmitAction(agent=Agent.ROBOT)}
        else:
            expl.best = {SuggestPickAction(e, agent=Agent.ROBOT) 
                         for e in min_edges}
            expl.others = {SuggestPickAction(e, agent=Agent.ROBOT)
                           for e in expl.others}

        # Choose the action.
        action = sorted(expl.best)[0]

        self.last_explanation = expl
        self.last_plan = action

        return action

    # def __init__(self, world, start=None):
    #     self.world = world

    #     if start is None:
    #         available_starts = sorted(
    #             self.world.env.state.network.graph.nodes())
    #         # print('Available starting points: {}'.format(available_starts))
    #         self.current = available_starts[0]
    #     else:
    #         self.current = start
    #     self.last_explanation = None

    # def plan(self, agent):
    #     # Select greedy.
    #     state = self.world.agent.cur_belief.mpe()
    #     expl, e = get_prims_pick(
    #         state.graph, self.current, state.edges)

    #     # Refine the explanation in terms of actions.
    #     if e is None:
    #         expl.best = AttemptSubmitAction()
    #         expl = ConnectedExplanation()
    #     else:
    #         expl.best = SuggestPickAction(e)
    #         expl.others = {SuggestPickAction(edge) for edge in expl.others}

    #     # Choose the action.
    #     action = expl.best
    #     self.last_explanation = expl
    #     self.last_plan = action

    #     return action

    # def update(self, agent, action, observation):
    #     """Update the current node"""
    #     if isinstance(action, SuggestPickAction):
    #         if self.current == action.edge[1]:
    #             self.current = action.edge[0]
    #         else:
    #             self.current = action.edge[1]


def get_prims_pick(graph, start, edges=frozenset(), weight_label='cost'):
    """Function receives a graph and a starting node, and return the next"""
    closed_set = {u for tup in edges for u in tup}

    if len(closed_set) == 0:
        closed_set = closed_set.union({start})

    # Default explanation template.
    expl = BetterThanExplanation()

    pq = PQDict()

    for u in closed_set:
        for v in graph.neighbors(u):
            if u not in closed_set or v not in closed_set:
                weight = graph.edges[u, v][weight_label]
                pq.additem((u, v), weight)
                # Add as an alternative choice.
                expl.others.add((u, v))

    if len(pq) == 0:
        return expl, None

    min_edges = list()

    edge, weight = pq.popitem()
    expl.others.discard(edge)

    min_weight = weight

    min_edges.append(edge)
    while len(pq) > 0:
        edge, weight = pq.popitem()
        expl.others.discard(edge)
        if weight == min_weight:  # an alternative
            min_edges.append(edge)
        else:
            break

    expl.best = min_edges

    return expl, min_edges


class Explanation(object):
    def __str__(self):
        return self.__repr__()


class ConnectedExplanation(object):
    def __init__(self):
        self.others = set()
        self.alternatives = set()

    def __repr__(self):
        return 'All are connected now!'


class BetterThanExplanation():
    def __init__(self, best=None, others=None, alternatives=None):
        """Action best is better than actions in others, with alternatives."""
        if others is None:
            others = set()
        if alternatives is None:
            alternatives = set()

        self.best = best
        self.others = others
        self.alternatives = alternatives

    def __repr__(self):
        o = ','.join([str(a) for a in self.others])
        s = '{} > [{}]'.format(self.best, o)
        return s
