import copy

import networkx as nx
import pomdp_py

from ..utils.graph_utils import in_undirected_edgeset
from ..domain.action import PickAction, SuggestPickAction, \
    UnpickAction, SubmitAction, SuggestSubmitAction, \
    ClearSuggestSubmitAction, AgreeAction, DisagreeAction, \
    ClearAction

from ..domain.state import *

# from ..env.app.utils import solve_mst, calculate_cost

EPSILON = 1e-9
# EPSILON = 0


class MstTransitionModel(pomdp_py.TransitionModel):
    """ The model is deterministic """

    def __init__(self,
                 action_types=[],
                 submit_mode='mst'):
        # self.states = states
        self.action_types = list(action_types)
        self.submit_mode = submit_mode

        self.attempt_no = 1
        self.max_attempts = 3  # for the activity.

    def probability(self, next_state, state, action,
                    normalized=False, **kwargs):
        '''deterministic'''
        # print('hi', next_state)
        if next_state == self.sample(state, action):
            return 1.0 - EPSILON
        else:
            return EPSILON

    def sample(self, state, action):
        # print('Sampling:', action, self.action_types)

        next_state = copy.deepcopy(state)

        # print('===== transition sampling', action, self.action_types)

        """Returns next mst state"""

        if 'pick' in self.action_types and isinstance(action, PickAction):
            if not state.terminal:
                u, v = action.edge
                if state.graph.has_edge(u, v) \
                        and not in_undirected_edgeset(u, v, state.edges):
                    next_state.edges = next_state.edges.union({(u, v)})
                next_state.submit_suggested = False

        elif 'suggest-pick' in self.action_types and isinstance(action, SuggestPickAction):
            u, v = action.edge
            if not state.terminal and state.graph.has_edge(u, v):
                if state.suggested is None:  # New suggestion.
                    next_state.suggested = (u, v)
                    # print(state, next_state)
                # Accept.
                elif state.suggested == (u, v) or state.suggested == (v, u):
                    # if in_undirected_edgeset(u, v, state.edges):
                    next_state.suggested = None
                    next_state.edges = next_state.edges.union({(u, v)})
                else:  # Reject and have a new suggestion.
                    next_state.suggested = (u, v)
                next_state.submit_suggested = False

        elif isinstance(action, ClearAction):
            next_state.suggested = None
            next_state.edges = frozenset()
            
        elif isinstance(action, AgreeAction):
            next_state.suggested = None
            next_state.edges = next_state.edges.union({state.suggested})

        elif isinstance(action, DisagreeAction):
            next_state.suggested = None

        elif 'unpick' in self.action_types and isinstance(action, UnpickAction):
            if not state.terminal:
                u, v = action.edge
                if state.graph.has_edge(u, v) \
                        and in_undirected_edgeset(u, v, state.edges):
                    next_state.edges = next_state.edges.difference(
                        {(u, v), (v, u)})
                next_state.submit_suggested = False
            # print('====== Unpicking', state, next_state, state.graph.has_edge(u, v),
            # in_undirected_edgeset(u, v, state.edges))

        elif 'suggest-submit' in self.action_types and isinstance(action, SuggestSubmitAction):
            if next_state.submit_suggested:
                next_state.terminal = True
            else:
                next_state.submit_suggested = True

        elif isinstance(action, ClearSuggestSubmitAction):
            next_state.submit_suggested = False

        elif 'submit' in self.action_types and isinstance(action, SubmitAction):
            if self.submit_mode == 'mst' and state.is_mst():
                next_state.terminal = True
            # elif state.is_spanning():
            elif self.submit_mode == 'once':
                next_state.terminal = True
            else:
                next_state.edges = frozenset()
                next_state.suggested = None
            # else:
            # leave as is - no change

        return next_state

    def argmax(self, state, action):
        """Returns the most likely next state"""
        return self.sample(state, action)

    # # the following is needed for value iteration
    # def get_all_states(self):
    #     return self.states
