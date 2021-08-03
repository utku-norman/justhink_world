import pomdp_py

from ..domain.observation import NullObservation


class MstObservationModel(pomdp_py.ObservationModel):
    """Observations are not implemented."""

    def __init__(self):
        self.observations = [NullObservation]

    def probability(self, observation, next_state, action,
                    normalized=False, **kwargs):
        # raise NotImplementedError  # Never used
        return 1.0

    def sample(self, next_state, action, normalized=False, **kwargs):
        return self.observations[0]

    def argmax(self, next_state, action, normalized=False, **kwargs):
        """Returns the most likely observation"""
        return self.observations[0]

    def get_distribution(self, next_state, action, **kwargs):
        """Returns the underlying distribution of the model.
        In this case, it's just a histogram"""
        return pomdp_py.Histogram({self.observations[0]: 1.0})

    def get_all_observations(self):
        return self.observations
