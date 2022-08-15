import pomdp_py

from ..domain.observation import Observation


class FullObservationModel(pomdp_py.ObservationModel):
    def __init__(self):
        pass

    def probability(self, observation, next_state, action,
                    normalized=False, **kwargs):
        return 1.0

    def sample(self, next_state, action, normalized=False, **kwargs):
        return Observation(next_state)

    def argmax(self, next_state, action, normalized=False, **kwargs):
        """Return the most likely observation."""
        return Observation(next_state)

    def get_distribution(self, next_state, action, **kwargs):
        """Return the underlying distribution of the model.
        In this case, it's just a histogram."""
        return pomdp_py.Histogram({Observation(next_state): 1.0})
