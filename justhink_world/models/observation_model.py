import pomdp_py

from ..domain.observation import Observation, NullObservation

# EPSILON = 1e-9


class MstObservationModel(pomdp_py.ObservationModel):
    """no observation"""

    def __init__(self): #, observations):
        self.observations = [NullObservation]
        # print("observations", observations)
        pass

    def probability(self, observation, next_state, action, normalized=False, **kwargs):
        # return 0.0
        # return 1.0 - EPSILON
        # raise NotImplementedError  # Never used
        return 1.0

    def sample(self, next_state, action, normalized=False, **kwargs):
        # raise NotImplementedError  # Never used
        return self.observations[0]


        # o = self.get_distribution(next_state, action).random()
        # print('o sampling', o)
        # return o
        # raise NotImplementedError  # Never used

    def argmax(self, next_state, action, normalized=False, **kwargs):
        """Returns the most likely observation"""
        # raise NotImplementedError  # Never used
        return self.observations[0]

        # return None
        # return max(self._probs[next_state][action], key=self._probs[next_state][action].get)

    def get_distribution(self, next_state, action, **kwargs):
        """Returns the underlying distribution of the model; In this case, it's just a histogram"""
        return pomdp_py.Histogram({self.observations[0]: 1.0})
        # raise NotImplementedError  # Never used

    # def get_all_observations(self):
    #     return self.observations



# class MstObservationModel(pomdp_py.ObservationModel):
#     def __init__(self): #, OBSERVATIONS):
#         # self.OBSERVATIONS = OBSERVATIONS
#         pass

#     def probability(self, observation, next_state, action):
#         # return 1
#         return 0

#     def sample(self, next_state, action, argmax=False):
#         # if not next_state.terminal and isinstance(action, PickAction):
#         # return Observation(Action)
#         return Observation(next_state)


#     def argmax(self, next_state, action):
#         """Returns the most likely observation"""
#         return self.sample(next_state, action, argmax=True)

#     # # the following is needed for value iteration
#     # def get_all_observations(self):
#     #     return {}
#     # #     # return justhink.OBSERVATIONS
#     # #     return self.OBSERVATIONS