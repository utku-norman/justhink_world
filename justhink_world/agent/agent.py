# Defines the agent. There's nothing special
# about the MST agent in fact, except that
# it uses models defined in ..models, and
# makes use of the belief initialization
# functions in belief.py
import pomdp_py
from .belief import initialize_belief
from ..models.transition_model import MstTransitionModel
from ..models.observation_model import MstObservationModel
from ..models.reward_model import MstRewardModel
from ..models.policy_model import MstPolicyModel


class MstAgent(pomdp_py.Agent):
    def __init__(self, init_state):
        # fully observable (assuming state is observable perfectly).
        prior = {init_state: 1.0}
        init_belief = initialize_belief(prior=prior)

        transition_model = MstTransitionModel()
        observation_model = MstObservationModel()
        reward_model = MstRewardModel()
        policy_model = MstPolicyModel(init_state.network)
        super().__init__(init_belief, policy_model,
                         transition_model=transition_model,
                         observation_model=observation_model,
                         reward_model=reward_model)
