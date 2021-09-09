from justhink_world.domain.action import SuggestPickAction, SubmitAction

from justhink_world.agent import Robot

from pqdict import PQDict


class TraversalPlanner(object):
    """Define a greedy traversal planner.

    It will produce a suboptimal result."""

    def __init__(self, state, start=None):
        self.state = state

        if start is None:
            available_starts = sorted(state.network.graph.nodes())
            self.cur_node = available_starts[0]
        else:

            self.cur_node = start

        self.explanation = None

    def plan(self, agent):
        """select the next action by greedy traversal planning"""
        # Select greedy.
        self.state = agent.cur_belief.mpe()
        self.cur_node = agent.state.cur_node

        # state = self.state

        v = None
        # note_iter = iter(state.graph.nodes)
        # while v is None and (len(state.graph.edges)
        # < state.graph.number_of_edges()-1):
        expl, v = get_greedy_neighbour(
            self.state.network.graph, self.cur_node,
            self.state.network.subgraph)

        # Refine the explanation in terms of actions.
        if v is None:
            expl = ConnectedExplanation()
            expl.best = SubmitAction(agent=Robot)
        else:
            expl.others = {SuggestPickAction((self.cur_node, u), agent=Robot)
                           for u in expl.others}
            expl.best = SuggestPickAction((self.cur_node, v), agent=Robot)

        # Choose the action.
        action = expl.best
        self.explanation = expl

        return action

    # # def update(self, agent, action, observation):
    # def update(self, action, state):  # observation):
    #     """Update the current node."""
    #     if isinstance(action, SuggestPickAction):
    #         self.cur_node = action.edge[1]
    #         print('##### moved current to', self.cur_node,
    #               self.state.network.get_node_name(self.cur_node))

    #     # self.state = observation.state
    #     self.state = state
    #     # if self.cur_node == action.edge[1]:
    #     #     self.cur_node = action.edge[0]
    #     # else:
    #     #     self.cur_node = action.edge[1]


def get_greedy_neighbour(graph, u, visited):
    """TODO"""
    # Default explanation template.
    expl = BetterThanExplanation()

    # Find the minimum cost neighbuor.
    min_v = None
    min_cost = None
    for v in graph.neighbors(u):
        expl.others.add(v)
        if not visited.has_edge(u, v):
            cost = graph.edges[u, v]['cost']
            if min_v is None or cost < min_cost:
                min_v = v
                min_cost = cost
                expl.best = v
                expl.others.discard(v)
    return expl, min_v


class PrimsPlanner():
    """Define a Prim's (or JPD (Jarnik/Prim/Dijkstra)) planner."""

    def __init__(self, world, start=None):
        self.world = world

        if start is None:
            available_starts = sorted(
                self.world.env.state.network.graph.nodes())
            # print('Available starting points: {}'.format(available_starts))
            self.current = available_starts[0]
        else:
            self.current = start
        self.explanation = None

    def plan(self, agent):
        # Select greedy.
        state = self.world.agent.cur_belief.mpe()
        expl, e = get_prims_pick(
            state.graph, self.current, state.edges)

        # Refine the explanation in terms of actions.
        if e is None:
            expl.best = SubmitAction()
            expl = ConnectedExplanation()
        else:
            expl.best = SuggestPickAction(e)
            expl.others = {SuggestPickAction(edge) for edge in expl.others}

        # Choose the action.
        action = expl.best
        self.explanation = expl

        return action

    def update(self, agent, action, observation):
        """Update the current node"""
        if isinstance(action, SuggestPickAction):
            if self.current == action.edge[1]:
                self.current = action.edge[0]
            else:
                self.current = action.edge[1]


def get_prims_pick(graph, start, edges=frozenset(), weight_label='cost'):
    """Function receives a graph and a starting node, and return the next"""
    closed_set = {u for tup in edges for u in tup}
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

    e, weight = pq.popitem()

    expl.best = e
    expl.others.discard(e)

    return expl, e


class Explanation(object):
    def __str__(self):
        return self.__repr__()


class ConnectedExplanation(object):
    def __init__(self):
        self.others = set()

    def __repr__(self):
        return 'All are connected now!'


class BetterThanExplanation():
    def __init__(self, best=None, others=None):
        """action a is better than actions b"""
        self.best = best
        if others is None:
            self.others = set()
        else:
            self.others = others

    def __repr__(self):
        o = ','.join([str(a) for a in self.others])
        s = '{} > [{}]'.format(self.best, o)
        return s
