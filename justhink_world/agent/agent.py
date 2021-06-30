# Defines the agent. There's nothing special
# about the MOS agent in fact, except that
# it uses models defined in ..models, and
# makes use of the belief initialization
# functions in belief.py
import pomdp_py
from .belief import *
from ..models.transition_model import *
from ..models.observation_model import *
from ..models.reward_model import *
from ..models.policy_model import *

class MstAgent(pomdp_py.Agent):
    """One agent is one robot."""
    def __init__(self, init_state):
        # self.robot_id = robot_id
        # self._object_ids = object_ids
        # self.sensor = sensor

        # initialize belief
        # init_belief = initialize_belief(dim,
        #                                 self.robot_id,
        #                                 self._object_ids,
        #                                 prior=prior,
        #                                 representation=belief_rep,
        #                                 robot_orientations={self.robot_id:rth},
        #                                 num_particles=num_particles)

        

        prior = {init_state: 1.0}
        # init_belief = initialize_belief(prior=prior)
        init_belief = pomdp_py.Histogram({init_state: 1})  # fully observable (assuming state is observable perfectly)

        transition_model = MstTransitionModel()
        observation_model = MstObservationModel()
        reward_model = MstRewardModel()
        policy_model = MstPolicyModel(init_state.graph)
        super().__init__(init_belief, policy_model,
                         transition_model=transition_model,
                         observation_model=observation_model,
                         reward_model=reward_model)



    def clear_history(self):
        """Custom function; clear history"""
        self._history = None


        
        

# def init_particles_belief(num_particles, init_state, belief='uniform'):
#     num_particles = 200
#     particles = []
#     for _ in range(num_particles):
#         # if belief == "uniform":
#             # rocktypes = []
#             # for i in range(k):
#             #     rocktypes.append(RockType.random())
#             # rocktypes = tuple(rocktypes)
#         if belief == "groundtruth":
#             # rocktypes = copy.deepcopy(init_state.rocktypes)
#             edges = copy.deepcopy(init_state.edges)
#         particles.append(State(graph=init_state.graph, edges=edges))
#     init_belief = pomdp_py.Particles(particles)
#     return init_belief
