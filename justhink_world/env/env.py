# import copy
# import pomdp_py


# class MstEnvironment(pomdp_py.Environment):
#     def __init__(self, init_state, transition_model, reward_model):
#         super().__init__(init_state,
#                          transition_model=transition_model,
#                          reward_model=reward_model)

#     def state_transition(self, action, execute=True):
#         """Simulates a state transition given `action`.

#         If `execute` is set to True, then the resulting state will be
#         the new current state of the environment.

#         Args:
#             action (Action): action that triggers the state transition
#             execute (bool): If True, the resulting state of the transition will
#                             become the current state.

#         Returns:
#             float or tuple: reward as a result of `action` and state
#             transition, if `execute` is True (next_state, reward) if `execute`
#             is False.

#         """
#         next_state = copy.deepcopy(self.state)
#         next_state = self.transition_model.sample(self.state, action)

#         reward = self.reward_model.sample(self.state, action, next_state)
#         # print(self.state, action, next_state, reward)

#         if execute:
#             self.apply_transition(next_state)
#             return reward
#         else:
#             return next_state, reward
