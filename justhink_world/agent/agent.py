import pomdp_py

from .belief import initialize_belief
# from .reasoning import TraversalPlanner


class Actor(object):
    """TODO: docstring for Actor"""
    def __str__(self):
        return self.__repr__()

    def __repr__(self):
        return self.name


class Human(Actor):
    """TODO: docstring for Human"""
    name = 'Human'


class Robot(Actor):
    """TODO: docstring for Robot"""
    name = 'Robot'


class Admin(Actor):
    """TODO: docstring for Admin"""
    name = 'Admin'


class RobotAgent(pomdp_py.Agent):
    """TODO: docstring for RobotAgent"""
    def __init__(
            self, init_state, policy_model, transition_model,
            observation_model, reward_model, mental_state):

        self.state = mental_state

        self.mental_history = [self.state]

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
            init_belief, policy_model=policy_model,
            transition_model=transition_model,
            observation_model=observation_model, 
            reward_model=reward_model)
