import copy

import pomdp_py

import networkx as nx

from ..domain.action import PickAction, SuggestPickAction, \
    SetPauseAction, SetStateAction, \
    AgreeAction, DisagreeAction, \
    ClearAction, \
    AttemptSubmitAction, ContinueAction, SubmitAction, \
    ObserveAction

from ..domain.state import Button
from ..agent import HumanAgent, RobotAgent

EPSILON = 1e-9


class IndivTransitionModel(pomdp_py.TransitionModel):
    """Transition model for an individual activity (e.g. tests)

    Allows pick, unpick and submit actions: see policy model.
    """

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

        if isinstance(action, SetStateAction):
            return action.state

        elif isinstance(action, SetPauseAction):
            next_state = copy.deepcopy(state)
            next_state.is_paused = action.is_paused
            return next_state

        # Like a wait action to fill observation.
        elif isinstance(action, ObserveAction):
            return state

        next_state = copy.deepcopy(state)
        network = state.network
        next_network = next_state.network

        # Pick action.
        if isinstance(action, PickAction):
            if not state.is_terminal:
                u, v = action.edge
                if network.graph.has_edge(u, v) \
                        and not network.subgraph.has_edge(u, v):
                    next_network.subgraph.add_edge(u, v)
                next_network.is_submitting = False
                next_state.clear_button = Button.ENABLED

        # Clear action.
        elif isinstance(action, ClearAction):
            next_network.suggested_edge = None
            next_network.subgraph = nx.Graph()

        # Attempt to submit action.
        elif isinstance(action, AttemptSubmitAction):
            next_state.is_submitting = True

        elif isinstance(action, ContinueAction):
            next_state.is_submitting = False

        elif isinstance(action, SubmitAction):
            next_state.is_terminal = True
            next_state.agents = frozenset()
            next_state.is_submitting = False

        next_state.network = next_network

        return next_state

    def argmax(self, state, action):
        """Returns the most likely next state"""
        return self.sample(state, action)


class CollabTransitionModel(pomdp_py.TransitionModel):
    """Transition model for a collaborative activity

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
        # Meta type of actions, intervention-like / god-mode.
        if isinstance(action, SetStateAction):
            return copy.deepcopy(action.state)

        elif isinstance(action, SetPauseAction):
            next_state = copy.deepcopy(state)
            next_state.is_paused = action.is_paused
            return next_state

        # Like a wait action to fill observation.
        elif isinstance(action, ObserveAction):
            return state

        # Validation.
        # If the agent can act.
        if action.agent not in state.agents:
            print('Invalid action {}: agent {} is not an active ({}).'.format(
                action, action.agent.name, state.agents))
            raise ValueError

        next_state = copy.deepcopy(state)
        network = state.network
        next_network = next_state.network

        # Normal actions
        if isinstance(action, SuggestPickAction):
            u, v = action.edge

            # Validity.
            assert network.graph.has_edge(u, v)

            if not state.is_terminal:
                s = network.suggested_edge

                # New suggestion.
                if s is None:
                    next_network.suggested_edge = (u, v)
                    # Maintain the agents that can act: suggestions swap turns.
                    next_state.agents = toggle_agent(state.agents)

                # Accept.
                elif s == (u, v) or s == (v, u):
                    next_network.suggested_edge = None
                    next_network.subgraph.add_edge(u, v)

                # Reject and have a new suggestion.
                else:
                    next_network.suggested_edge = (u, v)

                next_network.is_submitting = False

        # Clear action.
        elif isinstance(action, ClearAction):
            next_network.suggested_edge = None
            next_network.subgraph = nx.Graph()

        # Agree action.
        elif isinstance(action, AgreeAction):
            next_network.suggested_edge = None
            s = network.suggested_edge
            next_network.subgraph.add_edge(s[0], s[1])
            # next_state.yes_button = Button.DISABLED
            # next_state.no_button = Button.DISABLED

        # Disagree action.
        elif isinstance(action, DisagreeAction):
            next_network.suggested_edge = None
            # next_state.yes_button = Button.DISABLED
            # next_state.no_button = Button.DISABLED

        # elif isinstance(action, SuggestSubmitAction):
        #     if next_network.is_submitting:
        #         next_state.is_terminal = True
        #     else:
        #         next_network.is_submitting = True

        # elif isinstance(action, ClearSuggestSubmitAction):
        #     next_state.is_submitting = False

        # Attempt to submit action.
        elif isinstance(action, AttemptSubmitAction):
            next_state.is_submitting = True
            # Maintain the agents that can act: suggestions swap turns.
            next_state.agents = toggle_agent(state.agents)

        elif isinstance(action, ContinueAction):
            next_state.is_submitting = False

        elif isinstance(action, SubmitAction):
            if network.is_mst():
                next_state.is_terminal = True
                next_state.agents = frozenset()
            elif state.attempt_no == state.max_attempts:
                next_state.is_terminal = True
                next_state.agents = frozenset()
            else:
                next_network.subgraph = nx.Graph()
                next_network.suggested_edge = None
                next_state.attempt_no += 1

            next_state.is_submitting = False
            next_state.is_paused = False

        next_state.network = next_network

        return next_state

    def argmax(self, state, action):
        """Return the most likely next state."""
        return self.sample(state, action)


def toggle_agent(agents):
    if RobotAgent in agents:
        return frozenset({HumanAgent})
    else:
        return frozenset({RobotAgent})
