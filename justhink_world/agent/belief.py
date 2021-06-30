# # import pomdp_py
# # import random
# # import copy
# # from ..domain.state import *


# def initialize_belief(prior={}, representation="histogram"): # edges, 
#     """
#     Returns a GenerativeDistribution that is the belief representation for
#     the multi-object search problem.

#     Args:
#         edges (dict): a set of edges that we want to model the belief distribution over
#         prior (dict): A mapping {edge -> [0,1]}. If used, then 
#                       all locations not included in the prior will be treated to have 0 probability.
#                       If unspecified for an object, then the belief over that object is assumed
#                       to be a uniform distribution.
#         num_particles (int): Maximum number of particles used to represent the belief

#     Returns:
#         GenerativeDistribution: the initial belief representation.
#     """
#     if representation == "histogram":
#         return _initialize_histogram_belief(edges, prior)
#     else:
#         raise ValueError("Unsupported belief representation %s" %
#                          representation)



    
# def _initialize_histogram_belief(prior):
#     """
#     Returns the belief distribution represented as a histogram
#     """
# # #     oo_hists = {}  # objid -> Histogram
# # #     width, length = dim
# # #     for objid in object_ids:
# # #         hist = {}  # pose -> prob
# # #         total_prob = 0
# # #         if objid in prior:
# # #             # prior knowledge provided. Just use the prior knowledge
# # #             for pose in prior[objid]:
# # #                 state = ObjectState(objid, "target", pose)
# # #                 hist[state] = prior[objid][pose]
# # #                 total_prob += hist[state]
# # #         else:
# # #             # no prior knowledge. So uniform.
# # #             for x in range(width):
# # #                 for y in range(length):
# # #                     state = ObjectState(objid, "target", (x,y))
# # #                     hist[state] = 1.0
# # #                     total_prob += hist[state]

# # #         # Normalize
# # #         for state in hist:
# # #             hist[state] /= total_prob

# # #         hist_belief = pomdp_py.Histogram(hist)
# # #         oo_hists[objid] = hist_belief

# # #     # For the robot, we assume it can observe its own state;
# # #     # Its pose must have been provided in the `prior`.
# # #     assert robot_id in prior, "Missing initial robot pose in prior."
#     init_robot_pose = list(prior[robot_id].keys())[0]
#     belief = pomdp_py.Histogram({SolutionBeliefState(robot_id, init_robot_pose, (), None): 1.0})
        
#     return MosOOBelief(robot_id, oo_hists)
