import random
import pomdp_py
from ..domain.action import PickAction, SubmitAction
from ..tools.networks import in_edges


class MstPolicyModel(pomdp_py.RolloutPolicy):
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
        self._update_available_actions(next_state)

    def _update_available_actions(self, state):
        s = set(state.network.edges())

        remaining_edges = set()
        for u, v in s:
            if not in_edges(u, v, state.edges):
                remaining_edges.add((u, v))

        actions = set({PickAction(e) for e in remaining_edges})
        actions = actions | {SubmitAction()}
        self.actions = actions

    def get_all_actions(self, state=None, **kwargs):
        if state is not None:
            self._update_available_actions(state)
        return self.actions

    def rollout(self, state, history=None):
        return self.sample(state, history)
