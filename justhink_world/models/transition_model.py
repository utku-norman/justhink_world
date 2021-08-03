import copy

import pomdp_py

from ..tools.networks import in_edges
from ..domain.action import PickAction, SuggestPickAction, \
    UnpickAction, SubmitAction, SuggestSubmitAction, \
    AgreeAction, DisagreeAction, \
    ClearAction
# ClearSuggestSubmitAction

EPSILON = 1e-9


class TestTransitionModel(pomdp_py.TransitionModel):
    """Transition model for the individual activity

    Allows pick, unpick and submit actions."""

    def __init__(self):
        pass

    def probability(self, next_state, state, action,
                    normalized=False, **kwargs):
        """deterministic"""
        if next_state == self.sample(state, action):
            return 1.0 - EPSILON
        else:
            return EPSILON

    def sample(self, state, action):
        next_state = copy.deepcopy(state)

        if isinstance(action, PickAction):
            if not state.terminal:
                u, v = action.edge
                if state.network.has_edge(u, v) \
                        and not in_edges(u, v, state.edges):
                    next_state.edges = next_state.edges.union({(u, v)})
                next_state.submit_suggested = False

        elif isinstance(action, ClearAction):
            next_state.suggested = None
            next_state.edges = frozenset()

        elif isinstance(action, UnpickAction):
            if not state.terminal:
                u, v = action.edge
                if state.network.has_edge(u, v) \
                        and in_edges(u, v, state.edges):
                    next_state.edges = next_state.edges.difference(
                        {(u, v), (v, u)})
                next_state.submit_suggested = False

        elif isinstance(action, SubmitAction):
            next_state.terminal = True

        return next_state

    def argmax(self, state, action):
        """Returns the most likely next state"""
        return self.sample(state, action)


class CollaborativeTransitionModel(pomdp_py.TransitionModel):
    """Transition model for the collaborative activity

    Allows suggest-a-pick, agree, disagree, and submit actions."""

    def __init__(self):
        pass

    def probability(self, next_state, state, action,
                    normalized=False, **kwargs):
        '''deterministic'''
        if next_state == self.sample(state, action):
            return 1.0 - EPSILON
        else:
            return EPSILON

    def sample(self, state, action):
        next_state = copy.deepcopy(state)

        if isinstance(action, SuggestPickAction):
            u, v = action.edge
            if not state.terminal and state.network.has_edge(u, v):
                if state.suggested is None:  # New suggestion.
                    next_state.suggested = (u, v)
                # Accept.
                elif state.suggested == (u, v) or state.suggested == (v, u):
                    # if in_edges(u, v, state.edges):
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

        elif isinstance(action, SuggestSubmitAction):
            if next_state.submit_suggested:
                next_state.terminal = True
            else:
                next_state.submit_suggested = True

        # elif isinstance(action, ClearSuggestSubmitAction):
        #     next_state.submit_suggested = False

        elif isinstance(action, SubmitAction):
            if state.is_mst():
                next_state.terminal = True
            else:
                next_state.edges = frozenset()
                next_state.suggested = None

        return next_state

    def argmax(self, state, action):
        """Returns the most likely next state"""
        return self.sample(state, action)
