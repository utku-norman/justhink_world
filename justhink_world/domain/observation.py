import pomdp_py


# class Observation(pomdp_py.Observation):
#     # NULL = None

#     def __init__(self, name):
#         self.name = name

#     def __hash__(self):
#         return hash(self.name)

#     def __eq__(self, other):
#         if isinstance(other, Observation):
#             return self.name == other.name
#         elif type(other) == str:
#             return self.name == other

#     def __str__(self):
#         return self.name

#     def __repr__(self):
#         return "Observation(%s)" % self.name


class Observation(pomdp_py.Observation):
    def __init__(self, state):
        self.state = state

    def __hash__(self):
        return hash(self.state)

    def __eq__(self, other):
        if isinstance(other, Observation):
            return self.state == other.state
        # elif type(other) == state:
            # return self.state == other

    def __str__(self):
        return str(self.state)

    def __repr__(self):
        return "Observation(%s)" % str(self.state)


# NullObservation = Observation('No-Obs')

# class ActionObservation(pomdp_py.Observation):
#     def __init__(self, action):
#         self.action = action

#     def __hash__(self):
#         return hash(self.action)

#     def __eq__(self, other):
#         if isinstance(other, ActionObservation):
#             return self.action == other.action
#         # elif type(other) == str:
#         #     return self.action. == other

#     def __str__(self):
#         return str(self.state)

#     def __repr__(self):
#         return "ActionObservation(%s)" % str(self.action)
