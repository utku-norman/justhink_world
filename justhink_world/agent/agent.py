import pomdp_py

from .belief import initialize_belief
# from .reasoning import TraversalPlanner


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

        self.mental_history = [self.state]

        # self.planner = TraversalPlanner(init_state)
        # action = self.current_planner.plan(world.agent)

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
            observation_model=observation_model, reward_model=reward_model)

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

    # # Update agent belief
    # current_mpe_state = agent.cur_belief.mpe()
    # next_robot_position = agent.transition_model.sample(
    #     current_mpe_state, real_action).robot_position

    # next_state_space = set({})
    # for state in agent.cur_belief:
    #     next_state = copy.deepcopy(state)
    #     next_state.robot_position = next_robot_position
    #     next_state_space.add(next_state)

    # new_belief = pomdp_py.update_histogram_belief(
    #     agent.cur_belief, real_action, real_observation,
    #     agent.observation_model, agent.transition_model,
    #     next_state_space=next_state_space)

    # agent.set_belief(new_belief)
