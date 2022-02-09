import copy

import importlib_resources

import pomdp_py

from .domain.state import EnvState
from .domain.action import ObserveAction, PickAction, SuggestPickAction, \
    AgreeAction,  DisagreeAction, SetStateAction, \
    AttemptSubmitAction, ContinueAction, SubmitAction

from .models.policy_model import IntroPolicyModel, TutorialPolicyModel, \
    IndividualPolicyModel, CollaborativePolicyModel
from .models.transition_model import IntroTransitionModel, \
    TutorialTransitionModel, \
    IndividualTransitionModel, CollaborativeTransitionModel
from .models.observation_model import FullObservationModel
from .models.reward_model import MstRewardModel

from .tools.read import make_network_resources, load_network
from .tools.write import Bcolors

from .agent import Agent, ModellingAgent
from .agent.reasoning import TraversalJumpingPlanner, PrimsPlanner

__STRATEGIES__ = ['greedy', 'optimal', 'aligning']


def list_worlds():
    """Create a list of the worlds that are available."""
    names = ['intro', 'tutorial']
    for test in ['pretest', 'posttest']:
        for i in range(1, 6):
            name = '{}-{}'.format(test, i)
            names.append(name)
    for i in range(1, 3):
        names.append('collaboration-{}'.format(i))
    names.append('bye')
    for i in range(1, 2):
        names.append('robot-individual-{}'.format(i))

    return names


def create_all_worlds(verbose=False, **kwargs):
    """Create all of the world instances."""
    # Create a list of world names to be initialised.
    names = list_worlds()

    # Initialise each world.
    worlds = {name: create_world(name, **kwargs, verbose=verbose)
              for name in names}

    return worlds


def create_world(name, history=None, state_no=None, verbose=False, **kwargs):
    """Create a world instance by the world's name."""

    if verbose:
        print('Initialising world {} ...'.format(name))

    # Create the file names for the world.
    resources = make_network_resources(name)

    # Determine the type of the world.
    if name == 'intro':
        world_type = IntroWorld
    elif name == 'tutorial':
        world_type = TutorialWorld
    elif 'collaboration' in name:
        world_type = CollaborativeWorld
    # elif 'test' in name:
    elif 'robot-individual' in name:
        world_type = RobotIndividualWorld
    else:
        world_type = HumanIndividualWorld
    # else:
        # raise NotImplementedError

    # Read the resources via temporary files and create a world instance.
    with importlib_resources.as_file(resources['graph']) as graph_file, \
            importlib_resources.as_file(resources['layout']) as layout_file:
        network = load_network(graph_file, layout_file, verbose=verbose)

    # Construct the initial state.
    if history is None:
        if world_type is HumanIndividualWorld:
            init_state = EnvState(
                network=network, agents=frozenset({Agent.HUMAN}),
                attempt_no=1, max_attempts=None, is_paused=False)
        elif world_type is RobotIndividualWorld:
            init_state = EnvState(
                network=network, agents=frozenset({Agent.ROBOT}),
                attempt_no=1, max_attempts=None, is_paused=False)
        elif world_type is CollaborativeWorld:
            init_state = EnvState(
                network=network, agents=frozenset({Agent.ROBOT}),
                attempt_no=1, max_attempts=3, is_paused=False)
        elif world_type is IntroWorld:
            init_state = EnvState(
                network=network, agents=frozenset())
        elif world_type is TutorialWorld:
            init_state = EnvState(
                network=network, agents=frozenset({Agent.HUMAN}))
        else:
            raise NotImplementedError
        history = [init_state]
    else:
        history = history

    # Construct the world.
    world = world_type(
        history, name=name, state_no=state_no, verbose=verbose, **kwargs)

    if verbose:
        print('Done!')

    return world


class World(pomdp_py.POMDP):
    """A world describing the interaction between an agent and the environment.

    An Agent operates in an environment by taking actions,
        receiving observations, and updating its belief.
    An Environment maintains the true state of the world.
    """

    def __init__(self, history, transition_model, policy_model,
                 state_no=None, name='World',
                 agent_strategy='greedy', verbose=False):

        self.name = name

        self.verbose = verbose

        # States.
        if not isinstance(history, list):
            history = [history]

        # History, for navigating states.
        self._history = history

        # Set the state no if given, the last state otherwise.
        if state_no is not None:
            self.state_no = state_no
        else:
            self.state_no = self.num_states

        cur_state = history[self.state_index]

        # Create a reward model.
        reward_model = MstRewardModel()
        observation_model = FullObservationModel()

        # Initialise an agent.
        # The state is fully observable.
        # planner = TraversalPlanner(cur_state)
        # planner = TraversalJumpingPlanner(cur_state)

        # mental_state = MentalState(
        #     cur_state.network.graph, cur_node=planner.cur_node)

        # Assign update belief function as a method of ModellingAgent class.
        setattr(ModellingAgent, "update_belief", update_belief)
        # setattr(ModellingAgent, "planner",
        # TraversalJumpingPlanner(cur_state))

        try:
            assert agent_strategy in __STRATEGIES__
        except Exception as e:
            print(e, agent_strategy, __STRATEGIES__)
            raise ValueError

        if agent_strategy == 'greedy':
            planner_type = TraversalJumpingPlanner
        elif agent_strategy == 'optimal':
            planner_type = PrimsPlanner
        elif agent_strategy == 'aligning':
            planner_type = TraversalJumpingPlanner
        else:
            raise NotImplementedError

        planner = planner_type(cur_state)
        agent = ModellingAgent(
            cur_state, policy_model, transition_model=transition_model,
            observation_model=observation_model, reward_model=reward_model,
            planner=planner)  # , history=None)
        # planner = TraversalJumpingPlanner(cur_state)
        # agent.planner = MethodType(planner, agent, ModellingAgent)
        # agent.planner = planner

        # Initialise an environment.
        env = pomdp_py.Environment(cur_state, transition_model, reward_model)

        # Construct an instance from the agent and the environment.
        super().__init__(agent, env, name=name)

    def __str__(self):
        return self.__repr__()

    def __repr__(self):
        return 'World({}:{})'.format(self.name, self.env.state)

    @property
    def state_no(self):
        return self._state_no

    @state_no.setter
    def state_no(self, value):
        if value < 1:
            value = 1
        elif value > self.num_states:
            value = self.num_states

        self._state_no = value

    @property
    def state_index(self):
        return (self.state_no - 1) * 2

    @property
    def history(self):
        return self._history

    @property
    def num_states(self):
        """Number of states in the history"""
        return len(self._history) // 2 + 1
        # return len(self.agent.history)

    @property
    def cur_state(self):
        """Current state of the environment."""
        return self._history[self.state_index]
        # Similarly from observation history
        # if self.state_no == 0:
        #     return None
        # else:
        #     return self.agent.history[self.state_no-1][1].state

    # @property
    # def cur_mental_state(self):
    #     """Current mental state of the agent in the environment."""
    #     index = self.state_no - 1
    #     if index >= 0 and index < len(self.agent.mental_history):
    #         return self.agent.mental_history[index]
    #     else:
    #         return self.agent.mental_history[0]

    def act(self, action):
        """TODO: docstring for act of World"""
        # Validation: check if the action is feasible.
        if action not in self.agent.all_actions:
            s = 'Invalid action {}: it not feasible (i.e. in {}).'.format(
                action, sorted(self.agent.all_actions))
            s += '\nIgnoring the action request.'
            print(Bcolors.ok(s))
            return None  # False

        # Relocate in history if not at the last state.
        if self.state_no != self.num_states:
            # Rebase.
            self.env.state_transition(SetStateAction(self.cur_state))
            # Clean history.
            self._history = self._history[:self.state_index+1]

        # Apply the state transition.
        state = copy.deepcopy(self.env.state)
        env_reward = self.env.state_transition(action)
        next_state = self.env.state

        # Print info.
        if self.verbose:
            print()
            print('--------event--------')
            # print('==== Step %d ====' % (self._step+1))
            # self._step = self._step + 1
            print('State: {}'.format(state))
            print('Action: {}'.format(action))
            # print('Belief: %s' % str(cur_belief))
            # print('>> Observation: %s' % str(observation))
            # print('Reward: %s' % str(env_reward))
            # print('Reward (Cumulative): %s' % str(self._total_reward))
            # print('Reward (Cumulative Discounted): %s' %
            #       str(self._total_discounted_reward))
            print('Next state: {}'.format(next_state))

            # print('New Belief: %s' % str(new_belief))
            print('---------------------')
            print()

        # Update the history.
        self._history.extend([action, next_state])

        # Update the agent.
        observation = self.env.provide_observation(
            self.agent.observation_model, action)

        # self.agent.update_history(action, observation)
        self.agent.policy_model.update(state, next_state, action)
        self.agent.update_belief(observation, action, verbose=self.verbose)

        # # TODO: run a belief update function.
        # # Fully observable: immediate access to the state.
        # new_belief = pomdp_py.Histogram({next_state: 1.0})
        # self.agent.set_belief(new_belief)

        # Move to the new state.
        self.state_no = self.num_states

        # # Update the agent.
        # robot_action = self.agent.planner.plan(self.agent)
        # self.agent.update_belief(robot_action)  # , is_executed=False)

        # # Action successfully taken.
        # return True
        # print(next_state)

        return observation


class IntroWorld(World):
    """TODO"""

    def __init__(self, state, name='IntroWorld', **kwargs):
        transition_model = IntroTransitionModel()
        policy_model = IntroPolicyModel()

        super().__init__(
            state, transition_model=transition_model,
            policy_model=policy_model, name=name, **kwargs)


class TutorialWorld(World):
    """TODO"""

    def __init__(self, state, name='TutorialWorld', **kwargs):
        transition_model = TutorialTransitionModel()
        policy_model = TutorialPolicyModel()

        super().__init__(
            state, transition_model=transition_model,
            policy_model=policy_model, name=name, **kwargs)


class IndividualWorld(World):
    """TODO"""

    def __init__(
            self, state, name='IndividualWorld', agent=Agent.HUMAN, **kwargs):
        transition_model = IndividualTransitionModel()
        policy_model = IndividualPolicyModel(agent=agent)

        super().__init__(
            state, transition_model=transition_model,
            policy_model=policy_model, name=name, **kwargs)


class HumanIndividualWorld(IndividualWorld):
    """TODO"""

    def __init__(self, state, **kwargs):
        kwargs['name'] = 'HumanIndividualWorld'
        kwargs['agent'] = Agent.HUMAN
        super().__init__(state, **kwargs)


class RobotIndividualWorld(IndividualWorld):
    """TODO"""

    def __init__(self, state, **kwargs):
        kwargs['name'] = 'RobotIndividualWorld'
        kwargs['agent'] = Agent.ROBOT
        super().__init__(state, **kwargs)


class CollaborativeWorld(World):
    """TODO"""

    def __init__(self, state, name='CollaborativeWorld', **kwargs):
        transition_model = CollaborativeTransitionModel()
        policy_model = CollaborativePolicyModel()

        super().__init__(
            state, transition_model=transition_model,
            policy_model=policy_model, name=name, **kwargs)

        action = ObserveAction(Agent.ROBOT)
        observation = self.env.provide_observation(
            self.agent.observation_model, action)
        self.agent.update_belief(observation, action)


def update_choice_beliefs(beliefs, cur_env_state, action):
    try:
        # Choice belief updates.
        if isinstance(action, PickAction) \
                or isinstance(action, SuggestPickAction):
            u, v = action.edge
            # print('### setting pick belief', action)
            beliefs['world'][u][v]['is_optimal'] = 1.0

        elif isinstance(action, AgreeAction):
            u, v = cur_env_state.network.suggested_edge
            beliefs['world'][u][v]['is_optimal'] = 1.0

        elif isinstance(action, DisagreeAction):
            u, v = cur_env_state.network.suggested_edge
            beliefs['world'][u][v]['is_optimal'] = 0.0

        # elif isinstance(action, ClearAction):
        #     # reset the beliefs.
        #     for u, v in cur_env_state.network.graph.edges():
        #         beliefs['world'][u][v]['is_optimal'] = None
        #     # # decrement the cleared.
        #     # for u, v in cur_env_state.network.subgraph.edges():
        #     #     value = beliefs['world'][u][v]['is_optimal']
        #     #     if value is None:
        #     #         value = 0
        #     #     value = value - 0.1
        #     #     if value < 0:
        #     #         value = 0
        #     #     beliefs['world'][u][v]['is_optimal'] = value

        elif isinstance(action, SubmitAction) or \
                isinstance(action, AttemptSubmitAction):
            for u, v in cur_env_state.network.graph.edges():
                if cur_env_state.network.subgraph.has_edge(u, v):
                    value = 1.0
                else:
                    value = 0.0
                beliefs['world'][u][v]['is_optimal'] = value

        elif isinstance(action, ContinueAction):
            for u, v in cur_env_state.network.subgraph.edges():
                value = beliefs['world'][u][v]['is_optimal']
                if value is None:
                    value = 0
                value = value - 0.1
                if value < 0:
                    value = 0
                beliefs['world'][u][v]['is_optimal'] = value

    except Exception as e:
        print(beliefs, e)


def update_belief(agent, observation, action=None, verbose=False):
    """TODO: docstring for update_belief"""
    # verbose = True

    if verbose:
        # print()
        print('----belief update----')
        if isinstance(action, SuggestPickAction):
            u, v = observation.state.network.get_edge_name(action.edge)
            verbose_action = action.__class__(edge=(u, v), agent=action.agent)
        else:
            verbose_action = action
        print('Action: {}'.format(verbose_action))
        print('Observation: {}'.format(observation))

    # Get the current environment state as known by the agent.
    cur_env_state = agent.cur_belief.mpe()

    # Update the belief to the new environment state.
    # if observation is not None:
    # Fully observable: immediate access to the state.
    # next_state = observation.state
    next_state = observation.state
    new_belief = pomdp_py.Histogram({next_state: 1.0})
    agent.set_belief(new_belief)

    # if is_executed:
    # if observation is not None:
    if not isinstance(action, ObserveAction):
        # Make a copy of the mental state.
        next_mental_state = copy.deepcopy(agent.cur_state)
    else:
        # Update in place.
        next_mental_state = agent.cur_state

    # Update the mental state's facts.
    beliefs_list = [
        next_mental_state.beliefs['me'],
        next_mental_state.beliefs['me']['you'],
        next_mental_state.beliefs['me']['you']['me'],
    ]
    suggested = next_state.network.suggested_edge
    for beliefs in beliefs_list:
        for u, v, d in beliefs['world'].edges(data=True):
            d['is_selected'] = next_state.network.subgraph.has_edge(u, v)
            d['is_suggested'] = suggested is not None \
                and set({u, v}) == set(suggested)

    # Select the beliefs about you or about me-by-you depending on the action.
    # if observation is not None:
    if action.agent is Agent.HUMAN:
        beliefs = next_mental_state.beliefs['me']['you']
    elif action.agent is Agent.ROBOT:
        beliefs = next_mental_state.beliefs['me']['you']['me']
    # else:
    #     return  # raise ValueError
    # else:
    #     beliefs = next_mental_state.beliefs['me']
    # Update the corresponding choice beliefs.
    update_choice_beliefs(beliefs, cur_env_state, action)

    # Update the current node the robot believes they are at.
    selected_nodes = cur_env_state.network.get_selected_nodes()
    new_selected_nodes = next_state.network.get_selected_nodes()

    # if observation is not None:
    # if isinstance(action, PickAction):
    #     _, new_cur_node = action.edge 
    # elif isinstance(action, SuggestPickAction):
    #     new_cur_node, _ = action.edge

    new_cur_node = None
    if isinstance(action, PickAction):  # go to the outer/new one.
        _, new_cur_node = action.edge 
    elif isinstance(action, SuggestPickAction):  # go to the inner/old one.
        # new_cur_node, _ = action.edge
        u, v = action.edge
        if v in selected_nodes:
            new_cur_node = v
        else:
            new_cur_node = u
    elif isinstance(action, AgreeAction):
        # # Move the current to the agreed end.
        # _, new_cur_node = cur_env_state.network.suggested_edge
        # Move the current to the agreed end, inferring the direction.
        # or at the direction of drawing.
        u, v = cur_env_state.network.suggested_edge
        if v in new_selected_nodes and v not in selected_nodes:
            new_cur_node = v
        else:
            new_cur_node = u

    if new_cur_node is not None:
        next_mental_state.cur_node = new_cur_node
        if verbose:
            print('Robot moved current to {} (Node {})'.format(
                next_state.network.get_node_name(new_cur_node),
                new_cur_node))

    # Plan and update beliefs according to the plan.
    agent.planner.plan(next_state, next_mental_state.cur_node)
    # print('New plan: going to {}'.format(planned_action))
    beliefs = next_mental_state.beliefs['me']
    # update_choice_beliefs(beliefs, next_state, action)
    # If robot, update others as not believed to be true.
    # if action.agent is Agent.ROBOT:
    for a in agent.planner.last_explanation.others:
        if isinstance(a, SuggestPickAction):
            u, v = a.edge
            if next_state.network.subgraph.has_edge(u, v):
                # value = None
                continue
            else:
                value = 0.0
            beliefs['world'][u][v]['is_optimal'] = value
    # update optimals believed to be true.
    for a in agent.planner.last_explanation.best:
        if isinstance(a, SuggestPickAction):
            u, v = a.edge
            if next_state.network.subgraph.has_edge(u, v):
                # value = None
                continue
            else:
                value = 1.0
            beliefs['world'][u][v]['is_optimal'] = value

    # self.agent.update_belief(robot_action)  # , is_executed=False)

    # Count the disagreements if the action is disagree by robot.
    if isinstance(action, DisagreeAction):
        u, v = cur_env_state.network.suggested_edge
        beliefs = next_mental_state.beliefs['me']['world']
        if action.agent == Agent.ROBOT:
            beliefs[u][v]['n_robot_disagree'] += 1
        elif action.agent == Agent.HUMAN:
            beliefs[u][v]['n_human_disagree'] += 1

        if verbose:
            print('{} disagreed with {} ({}-{}) {} times.'.format(
                action.agent,
                next_state.network.get_edge_name((u, v)), 
                u, v, beliefs[u][v]['n_human_disagree']))

    # Count the disagreements if the action is disagree by robot.
    if isinstance(action, AgreeAction):
        u, v = cur_env_state.network.suggested_edge
        beliefs = next_mental_state.beliefs['me']['world']
        if action.agent == Agent.ROBOT:
            beliefs[u][v]['n_robot_agree'] += 1
        elif action.agent == Agent.HUMAN:
            beliefs[u][v]['n_human_agree'] += 1

        if verbose:
            print('{} agreed with {} ({}-{}) {} times.'.format(
                action.agent,
                next_state.network.get_edge_name((u, v)), 
                u, v, beliefs[u][v]['n_human_agree']))

    # if observation is not None:
    # agent.mental_history.append(next_mental_state)
    # agent.state = next_mental_state

    # Update the mental history and move to that state.
    if not isinstance(action, ObserveAction):
        agent.history.extend([action, next_mental_state])
        agent.state_no = agent.num_states

    if verbose:
        print('---------------------')
        print()
