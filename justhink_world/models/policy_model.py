import random
import pomdp_py

from ..tools.networks import in_edges
from ..domain.action import PickAction, SuggestPickAction, \
    UnpickAction, SubmitAction, SuggestSubmitAction, \
    AgreeAction, DisagreeAction, \
    ClearAction

from ..agent.agent import HumanAgent, RobotAgent


class IndivPolicyModel(pomdp_py.RolloutPolicy):
    '''
    a PolicyModel:
    (1) determines the action space at a given history or state, and
    (2) samples an action from this space according
    to some probability distribution.
    '''

    def probability(self, action, state, normalized=False, **kwargs):
        raise NotImplementedError  # Never used

    def sample(self, state, normalized=False, **kwargs):
        return random.sample(self.get_all_actions(**kwargs), 1)[0]

    # def argmax(self, state, normalized=False, **kwargs):
    #     raise NotImplementedError

    def update(self, state, next_state, action, **kwargs):
        self.update_available_actions(next_state)

    def get_all_actions(self, state=None, **kwargs):
        """only the feasible actions"""
        if state is not None:
            self.update_available_actions(state)
        return self.actions

    def get_action_space(self):
        """all actions, only by type"""
        # Types of actions available in the action space
        # that are not necessarily feasible.
        # Available actions are enumerated, while
        # enumerating the action space is not necessary.
        return {
            PickAction,
            UnpickAction,
            ClearAction,
            SubmitAction,
        }

    def rollout(self, state, history=None):
        return self.sample(state, history)

    # Helper methods.
    def update_available_actions(self, state):
        actions = set()
        if not state.is_terminal:

            # Can pick the remaining edges.
            for u, v in state.network.graph.edges():
                if not in_edges(u, v, state.network.edges):
                    actions.add(PickAction((u, v)))

            # Can submit anytime.
            actions.add(SubmitAction())

            # Can clear if there is at least one edge.
            if len(state.network.edges) > 0:
                actions.add(ClearAction())

        self.actions = actions


class CollabPolicyModel(pomdp_py.RolloutPolicy):
    '''
    a PolicyModel:
    (1) determines the action space at a given history or state, and
    (2) samples an action from this space according
    to some probability distribution.
    '''

    # def __init__(self):
    #     # Set the agents that can act at the first state.
    #     self.agents = ['robot']
    #     super().__init__()

    def probability(self, action, state, normalized=False, **kwargs):
        raise NotImplementedError  # Never used

    def sample(self, state, normalized=False, **kwargs):
        return random.sample(self.get_all_actions(**kwargs), 1)[0]

    # def argmax(self, state, normalized=False, **kwargs):
    #     raise NotImplementedError

    def update(self, state, next_state, action, **kwargs):
        self.update_available_actions(next_state)

    def get_all_actions(self, state=None, **kwargs):
        if state is not None:
            self.update_available_actions(state)
        return self.actions

    def rollout(self, state, history=None):
        return self.sample(state, history)

    # Helper methods.
    def get_action_space(self):
        """all actions, only by type"""
        return {
            SuggestPickAction,
            SuggestSubmitAction,
            ClearAction,
            AgreeAction,
            DisagreeAction,
        }

    def update_available_actions(self, state):
        actions = set()

        # For each active agent.
        for agent in state.active_agents:
            # If it is not the end of the activity.
            if not state.is_terminal:

                # The agent can suggest picking a non-selected edge.
                for u, v in state.network.graph.edges():
                    if not in_edges(u, v, state.network.edges):
                        actions.add(SuggestPickAction((u, v), agent=agent))

                # The agent can submit (any time).
                actions.add(SubmitAction(agent=agent))

                # The agent can clear, if there is at least one edge.
                if len(state.network.edges) > 0:
                    actions.add(ClearAction(agent=agent))

        self.actions = actions
