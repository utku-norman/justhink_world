import pomdp_py
from ..domain.action import PickAction, SubmitAction

EPSILON = 1e-9


class MstRewardModel(pomdp_py.RewardModel):

    def _reward_func(self, state, action, next_state):
        reward = 0

        if isinstance(action, PickAction):
            u, v = action.edge
            if (u, v) not in state.edges and state.network.has_edge(u, v):
                reward = -state.network[u][v]['cost']
            else:
                reward = 0

        elif isinstance(action, SubmitAction):
            if next_state.terminal:
                reward = 1000
            else:
                reward = state.get_cost()

        return reward

    def sample(self, state, action, next_state, normalized=False, **kwargs):
        # deterministic
        return self._reward_func(state, action, next_state)

    def argmax(self, state, action, next_state, normalized=False, **kwargs):
        """Returns the most likely reward"""
        return self._reward_func(state, action, next_state)

    def probability(self, reward, state, action, next_state,
                    normalized=False, **kwargs):
        if reward == self._reward_func(state, action, next_state):
            return 1.0 - EPSILON
        else:
            return EPSILON

    def get_distribution(self, state, action, next_state, **kwargs):
        """Returns the underlying distribution of the model"""
        reward = self._reward_func(state, action, next_state)
        return pomdp_py.Histogram({reward: 1.0})
