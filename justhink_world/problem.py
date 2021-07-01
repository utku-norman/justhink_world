import copy

import pomdp_py

from .domain.state import State
from .env.env import MstEnvironment
from .domain.observation import NullObservation
from .models.policy_model import MstPolicyModel
from .models.transition_model import MstTransitionModel
from .models.observation_model import MstObservationModel
from .models.reward_model import MstRewardModel

from .utils.graph_utils import \
    load_graph_from_edgelist, load_graph_from_json


class Problem(pomdp_py.POMDP):
    def __init__(self,
                 layout_graph,
                 init_state,
                 action_types=['pick', 'submit'],
                 submit_mode='mst',
                 ):
        """init_belief is a Distribution."""
        init_belief = pomdp_py.Histogram({init_state: 1})  # fully observable

        self.layout_graph = layout_graph

        self.planner = None

        self.mental_history = list()
        self.world_history = list()
        transition_model = MstTransitionModel(action_types=action_types,
                                              submit_mode=submit_mode)
        reward_model = MstRewardModel()
        agent = pomdp_py.Agent(init_belief,
                               MstPolicyModel(),
                               transition_model,
                               MstObservationModel(),
                               MstRewardModel())
        env = MstEnvironment(init_state, transition_model,
                             reward_model)
        super().__init__(agent, env, name="Problem")


def init_problem(network_file, edges=frozenset(),
                 layout_file=None,
                 action_types=['pick', 'submit'],
                 submit_mode='mst',
                 verbose=False):
    if verbose:
        print('Initialising problem ...')

    # Load the graph.
    graph = load_graph_from_edgelist(network_file)

    # Load the layout.
    if layout_file is None:
        f = network_file.with_suffix('.json')
        layout_file = f.with_name(str(f.name).replace('edgelist', 'layout'))
        if not layout_file.exists():
            print('Layout file not found {} for {}'.format(
                network_file, layout_file))

    layout_graph = load_graph_from_json(layout_file)
    for u, v, d in graph.edges(data=True):
        layout_graph.add_edge(u, v, **d)
    # Print debug message on the graph and the layout.
    if verbose:
        print('Using graph: {} with layout: {}'.format(
            network_file.name, layout_file.name))

    # Construct the initial state.
    # Clean up the layout for nodes with no edges.
    for u in list(layout_graph.nodes()):
        neighbors = list(layout_graph.neighbors(u))
        if len(neighbors) == 0:
            layout_graph.remove_node(u)
    init_state = State(graph=graph, edges=edges)

    # Construct the problem.
    problem = Problem(layout_graph, init_state,
                      action_types=action_types,
                      submit_mode=submit_mode)

    if verbose:
        print('Done!')

    return problem


def reset_problem(problem, planner=None):
    problem.env.state.clear_selection()
    problem.env.state.terminal = False
    problem.env.state.suggested = None
    # Reset agent belief
    # problem.agent.set_belief(init_belief, prior=True)
    new_belief = pomdp_py.Histogram({problem.env.state: 1.0})
    problem.agent.set_belief(new_belief)

    # problem.agent.tree = None
    # if planner is not None:
    #     planner.plan(problem.agent)


def init_planner(problem, verbose=False):
    # print("*** Testing Value Interation ***")
    # works with histogram belief, needs explicit enumeration
    # planner = pomdp_py.ValueIteration(horizon=2, discount_factor=0.99)
    if verbose:
        # works with histogram belief
        print('Initialising a POUCT planner ...', end='')
    planner = pomdp_py.POUCT(max_depth=5, discount_factor=1,  # 1,  # 0.95,
                             num_sims=1000, exploration_const=110,  # 4096
                             rollout_policy=problem.agent.policy_model)
    # Attach the planner to the problem. Not the best practice.
    _ = planner.plan(problem.agent)
    problem.planner = planner

    if verbose:
        print('Done!')

    return planner

    # print("*** Testing POMCP ***") # needs particles belief
    # planner = pomdp_py.POMCP(max_depth=20, discount_factor=0.95,
    #                          num_sims=4096, exploration_const=20,
    #                          rollout_policy=agent.policy_model)
    # planner = CustomPlanner()


# def execute_pick_edge(problem, edge, planner=None, agent_name='robot'):
#     # if self._mst.has_edge(edge[0], edge[1]):
#     #     quality = 'optimal'
#     # else:
#     #     quality = 'sub-optimal'
#     # quality = '?'
#     action = PickAction(edge, agent_name=agent_name)  # , quality=quality)
#     execute_action(problem, action, planner=planner)


# def execute_submit(problem, planner=None, agent_name='robot'):
#     action = SubmitAction(agent_name=agent_name)
#     execute_action(problem, action, planner=planner)


def plan_action(problem, planner, verbose=False):
    if verbose:
        l = problem.agent.policy_model.get_all_actions()
        l = sorted(l, key=lambda a: str(a))
        print('Available: {}'.format(l))
    action = planner.plan(problem.agent)
    if verbose:
        print('Planned: {}'.format(action))
    return action
    # execute_action(problem, action, planner=planner)


def execute_action(problem, action, planner=None, verbose=False):
    if action is not None:
        true_state = copy.deepcopy(problem.env.state)
        env_reward = problem.env.state_transition(action, execute=True)
        # true_next_state = copy.deepcopy(problem.env.state)

        # real_observation = problem.env.provide_observation(
        #     problem.agent.observation_model, action)
        real_observation = NullObservation
        problem.agent.update_history(action, real_observation)
        if planner is not None:
            planner.update(problem.agent, action, real_observation)
            # print('update')
        problem.agent.policy_model.update(
            true_state, problem.env.state, action)

        # if not planner.updates_agent_belief:
        # cur_belief = copy.deepcopy(problem.agent.cur_belief)
        new_belief = pomdp_py.Histogram({problem.env.state: 1.0})
        problem.agent.set_belief(new_belief)
        # print("New Belief: %s" % str(problem.agent.cur_belief))

        # if isinstance(planner, pomdp_py.POUCT):
        #     print("Num sims: %d" % planner.last_num_sims, end=' | ')
        #     print("Plan time: %.5f" % planner.last_planning_time)

        # # if isinstance(tiger_problem.agent.cur_belief, pomdp_py.Histogram):
        # belief = problem.agent.cur_belief
        # new_belief = pomdp_py.update_histogram_belief(
        #     problem.agent.cur_belief,
        #     action, real_observation,
        #     problem.agent.observation_model,
        #     problem.agent.transition_model,
        #     next_state_space={problem.env.state})
        new_belief = pomdp_py.Histogram(
            {problem.env.state: 1})  # fully observable
        problem.agent.set_belief(new_belief)

        # # planner.update(rocksample.agent, action, real_observation)
        # self._total_reward += env_reward
        # self._total_discounted_reward += env_reward * self._gamma
        # self._gamma *= self._discount

        # Print info.
        # print("state: %s" % str(problem.env.state.edges))
        if verbose:
            print()
            print("---acting---")
            # print("==== Step %d ====" % (self._step+1))
            # self._step = self._step + 1
            print("True state: %s" % str(true_state))
            print("Action: %s" % repr(action))
            # print("Belief: %s" % str(cur_belief))
            # print(">> Observation: %s" % str(real_observation))
            print("Reward: %s" % str(env_reward))
            # print("Reward (Cumulative): %s" % str(self._total_reward))
            # print("Reward (Cumulative Discounted): %s" %
            #       str(self._total_discounted_reward))

            print("New Belief: %s" % str(new_belief))
            print("------------")
            print()

        # self._scenes[self._current].update_submit_button()

    # else:
    #     print('Action is None')


# ### Belief Update ###
# def belief_update(agent, real_action, real_observation, next_state, planner):
#     """Updates the agent's belief; The belief update may happen
#     through planner update (e.g. when planner is POMCP)."""

#     # Updates the planner; In case of POMCP, agent's belief is also updated.
#     planner.update(agent, real_action, real_observation)

#     # Update agent's belief.
#     if not isinstance(planner, pomdp_py.POMCP):
#         new_belief = pomdp_py.Histogram({next_state: 1.0})
#         agent.set_belief(new_belief)


# ### Solve the problem with POUCT/POMCP planner ###
# ### This is the main online POMDP solver logic ###
# def solve(problem,
#           max_depth=10,  # planning horizon
#           discount_factor=0.99,
#           planning_time=1.,       # amount of time (s) to plan each step
#           exploration_const=1000,  # exploration constant
#           visualize=True,
#          max_time=120,
#          # maximum amount of time allowed to solve the problem
#           max_steps=500),
#            # maximum number of planning steps the agent can take.

#     # Use POUCT
#     planner = pomdp_py.POUCT(max_depth=max_depth,
#                              discount_factor=discount_factor,
#                              planning_time=planning_time,
#                              exploration_const=exploration_const,
#                              rollout_policy=problem.agent.policy_model)
# Random by default

#     # Plan action
#     real_action = planner.plan(problem.agent)

#     # Execute action
#     reward = problem.env.state_transition(real_action, execute=True)

#     # Receive observation
#     _start = time.time()
#     real_observation = \
#         problem.env.provide_observation(
#             problem.agent.observation_model, real_action)

#     # Updates
#     problem.agent.clear_history()  # truncate history
#     problem.agent.update_history(real_action, real_observation)
#     belief_update(problem.agent, real_action, real_observation, planner)

    # def execute_robot_action(self):
    #     print()
    #     print('Executing robot action...')
    #     print('Robot behaviour:')
    #     problem = self._problem

    #     # add the edge planned by a planner.
    #     if problem.env.state.terminal:
    #         action = None
    #         opts = [
    #             'We are done!',
    #             'Congratulations!'
    #         ]
    #         # self.facial_expression_pub.publish("QT/happy")
    #         # self.body_gesture_pub.publish("QT/happy")
    #         # s = random.choice(opts)
    #         # self.say_pub.publish(s)
    #     else:
    #         action = self._planner.plan(problem.agent)
    #         action.agent_name = 'robot'
    #         if isinstance(action, PickAction):
    #             edge = action.edge
    #             if self._mst.has_edge(edge[0], edge[1]):
    #                 action.quality = 'optimal'
    #             else:
    #                 action.quality = 'sub-optimal'
    #         # pomdp_py.visual.visualize_pouct_search_tree(problem.agent.tree,
    #                 # visit_threshold=0,
    #                 # max_depth=, anonymize=False)

    #         s = None

    #         if isinstance(action, PickAction):
    #             u, v = action.edge
    #             u_node = self._layout_graph.nodes[u]
    #             v_node = self._layout_graph.nodes[v]
    #             u_name = u_node['text'].split()[-1]
    #             v_name = v_node['text'].split()[-1]

    #             opts = [
    #                 'I think we should connect',
    #                 "let's do",
    #                 "let's connect",
    #                 "let's go from",
    #             ]
    #             s = random.choice(opts)
    #             s += ' {} to {}'.format(u_name, v_name)

    #         if isinstance(action, SubmitAction):
    #             opts = [
    #                 'I think we should submit',
    #                 "let's submit",
    #                 "I think we are done, submit",
    #                 "let's check",
    #             ]
    #             s = random.choice(opts)

    #         if s is not None:
    #             # print('Robot: {}'.format(s))
    #             opts = [
    #                 # 'epfl/justhink/thinking2',
    #                 # 'epfl/justhink/observe',
    #                 'QT/show_tablet',
    #                 'QT/swipe_left',

    #                 # None, None,
    #             ]
    #             # b = random.choice(opts)
    #             # if b is not None:
    #             #     self.body_gesture_pub.publish(b)
    #             #     self.log_gesture('executing action', b)

    #             # self.talk_text_wrapper(s)
    #             # self.log_say('executing action', s)

    #     self.execute_action(action)
    #     print()
