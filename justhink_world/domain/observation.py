import pomdp_py


class Observation(pomdp_py.Observation):
    """A class to represent a fully-observable observation of the
    current state."""

    def __init__(self, state):
        self.state = state

    def __hash__(self):
        return hash(self.state)

    def __eq__(self, other):
        if isinstance(other, Observation):
            return self.state == other.state

    def __str__(self):
        return str(self.state)

    def __repr__(self):
        return "Observation(%s)" % str(self.state)
