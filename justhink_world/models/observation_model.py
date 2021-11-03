import pomdp_py

from ..domain.observation import Observation


class FullObservationModel(pomdp_py.ObservationModel):
    """Observations are not implemented."""

    def __init__(self):
        pass

    def probability(self, observation, next_state, action,
                    normalized=False, **kwargs):
        # raise NotImplementedError  # Never used
        return 1.0

    def sample(self, next_state, action, normalized=False, **kwargs):
        return Observation(next_state)
        # return self.observations[0]

    def argmax(self, next_state, action, normalized=False, **kwargs):
        """Return the most likely observation."""
        return Observation(next_state)
        # return self.observations[0]

    def get_distribution(self, next_state, action, **kwargs):
        """Return the underlying distribution of the model.
        In this case, it's just a histogram"""
        return pomdp_py.Histogram({Observation(next_state): 1.0})

    # def get_all_observations(self):
    #     return self.observations
