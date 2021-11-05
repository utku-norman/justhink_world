# import copy

import networkx as nx

import pomdp_py

from .belief import initialize_belief
# from .reasoning import TraversalJumpingPlanner

# from ..domain.action import *
# from .state import MentalState
# import justhink_world.domain.action as action


class Agent(object):
    """TODO: docstring for Agent"""
    HUMAN = 'Human'
    ROBOT = 'Robot'
    MANAGER = 'Manager'


class TaskAgent(pomdp_py.Agent, Agent):
    """TODO: docstring for TaskAgent"""

    def __init__(
            self, init_state, policy_model, transition_model,
            observation_model=None, reward_model=None):

        prior = {init_state: 1.0}
        init_belief = initialize_belief(prior=prior)

        # Update the available actions in the policy model
        # to access agent.all_actions even at the initial state.
        policy_model.update_available_actions(init_state)

        super().__init__(
            init_belief, policy_model=policy_model,
            transition_model=transition_model,
            observation_model=observation_model,
            reward_model=reward_model)

    def update_belief(self, action, observation):
        pass


class ModellingAgent(TaskAgent):
    """TODO: docstring for ModellingAgent"""

    def __init__(
            self, init_state, policy_model, transition_model,
            observation_model, reward_model, planner,
            history=None, state_no=None):
        # , update_belief=None):

        # # self.planner = TraversalPlanner(cur_state)
        # self.planner = TraversalJumpingPlanner(init_state)
        self.planner = planner

        if history is None:
            mental_state = MentalState(
                init_state.network.graph, cur_node=self.planner.cur_node)
            history = mental_state

        # States.
        if not isinstance(history, list):
            history = [history]

        # History, for navigating states.
        self._history = history

        # Set the state no if given, the last state otherwise.
        if state_no is not None:
            self.state_no = state_no
        else:
            self.state_no = self.num_states

        # # belief_update
        # if update_belief is not None:
        #     self.update_belief = update_belief

        super().__init__(
            init_state=init_state, policy_model=policy_model,
            transition_model=transition_model,
            observation_model=observation_model,
            reward_model=reward_model)

    @property
    def state_no(self):
        return self._state_no

    @state_no.setter
    def state_no(self, value):
        if value < 1:
            value = 1
        elif value > self.num_states:
            value = self.num_states

        self._state_no = value

    @property
    def state_index(self):
        return (self.state_no - 1) * 2

    @property
    def history(self):
        return self._history

    @history.setter
    def history(self, value):
        self._history = value

    @property
    def num_states(self):
        """Number of states in the history"""
        return len(self._history) // 2 + 1

    @property
    def cur_state(self):
        """Current state of the environment."""
        return self._history[self.state_index]


class MentalState(object):
    """TODO: docstring for MentalState"""

    def __init__(
            self, graph, cur_node=None,
            agents=set({Agent.HUMAN, Agent.ROBOT})):
        if Agent.HUMAN in agents:
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
        self.cur_node = cur_node

    def _create_view(self, from_graph):
        """TODO"""
        # About choices.
        d = {
            'is_optimal': None,
            'is_selected': False,
            'is_suggested': False,
        }

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
        """TODO: docsring for get_beliefs"""
        belief_list = list()

        pairs = [('world', self.beliefs['me']),
                 ('you', self.beliefs['me']['you']),
                 ('me-by-you', self.beliefs['me']['you']['me'])]

        for key, beliefs in pairs:
            for u, v, d in beliefs['world'].edges(data=True):
                value = d['is_optimal']
                if value is not None:
                    belief_list.append((key, u, v, value))

        return sorted(belief_list)
