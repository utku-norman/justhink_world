import random
import pomdp_py

from ..domain.action import PickAction, SuggestPickAction, \
    SubmitAction, \
    AgreeAction, DisagreeAction, \
    ClearAction, AttemptSubmitAction, ContinueAction

from ..agent.agent import Human, Robot


class PolicyModel(pomdp_py.RolloutPolicy):
    '''a PolicyModel:
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

    def rollout(self, state, history=None):
        return self.sample(state, history)

    # Helper methods.
    def update_available_actions(self, state):
        raise NotImplementedError


class IndividualPolicyModel(PolicyModel):
    '''TODO'''

    def update_available_actions(self, state):
        actions = set()

        # If it is not the end of the activity.
        if not state.is_terminal:

            # If not confirming a submission (i.e. normal gameplay).
            if not state.is_submitting:

                # Can pick the remaining edges.
                for u, v in state.network.graph.edges():
                    if not state.network.subgraph.has_edge(u, v):
                        actions.add(PickAction((u, v)))

                # Can clear if there is at least one edge.
                if state.network.subgraph.number_of_edges() > 0:
                    actions.add(ClearAction())

                # Can attempt to submit any time.
                actions.add(AttemptSubmitAction())

            # Confirming a submission.
            else:
                actions.add(ContinueAction())
                actions.add(SubmitAction())

        self.actions = actions


class CollaborativePolicyModel(PolicyModel):
    '''TODO'''

    def update_available_actions(self, state):
        actions = set()

        # For each active agent.
        for agent in state.agents:

            # If it is not the end of the activity.
            if not state.is_terminal:

                # If not confirming a submission (i.e. normal gameplay).
                if not state.is_submitting:

                    # If no edge is currently suggested.
                    if state.network.suggested_edge is None:
                        # The agent can suggest picking a non-selected edge.
                        for u, v in state.network.graph.edges():
                            if not state.network.subgraph.has_edge(u, v):
                                action = SuggestPickAction((u, v), agent=agent)
                                actions.add(action)

                        # The agent can submit.
                        actions.add(AttemptSubmitAction(agent=agent))

                        # The agent can clear, if there is at least one edge.
                        if state.network.subgraph.number_of_edges() > 0:
                            actions.add(ClearAction(agent=agent))

                    # If there is a suggested edge.
                    else:
                        # The agent can (dis)agree with the suggested edge.
                        actions.add(AgreeAction(agent=agent))
                        actions.add(DisagreeAction(agent=agent))

                # Confirming a submission.
                else:
                    actions.add(ContinueAction(agent=agent))
                    actions.add(SubmitAction(agent=agent))

        self.actions = actions


class IntroPolicyModel(PolicyModel):
    def update_available_actions(self, state):
        self.actions = {SubmitAction(agent=Human)}


class DemoPolicyModel(PolicyModel):
    def update_available_actions(self, state):
        actions = set()

        num_edges = state.network.subgraph.number_of_edges()

        if state.step_no < 4:
            for u, v in state.network.graph.edges():
                if not state.network.subgraph.has_edge(u, v):
                    action = PickAction((u, v), agent=Human)
                    actions.add(action)

        if state.step_no < 4 and num_edges > 0:
            actions.add(ClearAction(agent=Human))

        # if state.step_no == 3 and num_edges == 1:
        actions.add(SubmitAction(agent=Human))

        self.actions = actions
