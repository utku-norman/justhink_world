import random
import pomdp_py
from ..domain.action import PickAction, SubmitAction, NullAction
from ..utils.graph_utils import in_undirected_edgeset

# Policy Model
class MstPolicyModel(pomdp_py.RolloutPolicy):  # RandomRollout):
    '''
    a PolicyModel:
    (1) determines the action space at a given history or state, and 
    (2) samples an action from this space according to some probability distribution.
    '''

    def probability(self, action, state, normalized=False, **kwargs):
        raise NotImplementedError  # Never used

    def sample(self, state, normalized=False, **kwargs):
        return random.sample(self.get_all_actions(**kwargs), 1)[0]

    def argmax(self, state, normalized=False, **kwargs):
        # self.sample(state)
        """Returns the most likely reward"""
        raise NotImplementedError

    def update(self, state, next_state, action, **kwargs):
        # print('Updating rollout')
        # if hasattr(self, 'actions'):
        #     print(self.actions)
        #     print(state.edges)
        self._update_available_actions(next_state)
        
        # print(set(next_state.graph.edges()) - next_state.edges)
        # print(self.actions)
        # print(next_state.edges)

    def _update_available_actions(self, state):
        # if state.terminal:
        #     actions = set()
        # else:
        s = set(state.graph.edges())
        remaining_edges = {(u, v) for u, v in s if not in_undirected_edgeset(u, v, state.edges)}
        # remaining_edges = set(state.graph.edges()) - state.edges
        actions = set({PickAction(e) for e in remaining_edges})
        # if state.is_spanning():
        actions = actions | {SubmitAction()}
        self.actions = actions

    def get_all_actions(self, state=None, **kwargs):
        if state is not None:
            self._update_available_actions(state)
        return self.actions

    def rollout(self, state, history=None):
        # actions = self.get_all_actions(state=state, history=history)
        # if len(actions) > 0:
        #     return random.sample(actions, 1)[0]
        # else:
        #     return NullAction
        return self.sample(state, history)
        # return random.sample(self.get_all_actions(state=state, history=history), 1)[0]
