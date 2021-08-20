import copy

import pomdp_py

from .belief import initialize_belief
# from ..models.observation_model import MstObservationModel
# from ..models.reward_model import MstRewardModel


class Actor(object):
    pass


class Human(Actor):
    name = 'Human'

    def __str__(self):
        return self.__repr__()

    def __repr__(self):
        return self.name


class Robot(Actor):
    name = 'Robot'

    def __str__(self):
        return self.__repr__()

    def __repr__(self):
        return self.name


class RobotAgent(pomdp_py.Agent):
    def __init__(
            self, init_state, policy_model, transition_model,
            observation_model, reward_model, mental_state):

        self.state = mental_state

        # Defines the agent. There's nothing special
        # about the MST agent in fact, except that
        # it uses models defined in ..models, and
        # makes use of the belief initialization
        # functions in belief.py
        # fully observable (assuming state is observable perfectly).
        prior = {init_state: 1.0}
        init_belief = initialize_belief(prior=prior)

        # Update the available actions in the policy model
        # to access agent.all_actions even at the initial state.
        policy_model.update_available_actions(init_state)

        super().__init__(
            init_belief,
            policy_model=policy_model,
            transition_model=transition_model,
            observation_model=observation_model,
            reward_model=reward_model)

        # Create a reward model.
        # reward_model = MstRewardModel(

        # policy_model = MstPolicyModel(init_state.network)
        # super().__init__(init_belief, policy_model,
        #                  transition_model=transition_model,
        #                  observation_model=observation_model,
        #                  reward_model=reward_model)


# Defines the agent. There's nothing special
# about the MST agent in fact, except that
# it uses models defined in ..models, and
# makes use of the belief initialization
# functions in belief.py

# import pomdp_py
# from .belief import initialize_belief
# from ..models.transition_model import MstTransitionModel
# from ..models.reward_model import MstRewardModel


# from ..models.policy_model import MstPolicyModel


# class Agent(pomdp_py.Agent):
#     def __init__(self, init_state):
#         # fully observable (assuming state is observable perfectly).
#         prior = {init_state: 1.0}
#         init_belief = initialize_belief(prior=prior)

#         transition_model = MstTransitionModel()
#         observation_model = MstObservationModel()
#         reward_model = MstRewardModel()
#         policy_model = MstPolicyModel(init_state.network)
#         super().__init__(init_belief, policy_model,
#                          transition_model=transition_model,
#                          observation_model=observation_model,
#                          reward_model=reward_model)
