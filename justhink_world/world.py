import copy

import importlib_resources

import pomdp_py

from .domain.state import EnvironmentState, MentalState
# from .domain.action import SetStateAction
from .domain.action import ObserveAction, PickAction, SuggestPickAction, \
    AgreeAction,  DisagreeAction, SetStateAction, ClearAction, \
    AttemptSubmitAction, ContinueAction, SubmitAction

from .models.policy_model import IntroPolicyModel, TutorialPolicyModel, \
    IndividualPolicyModel, CollaborativePolicyModel
from .models.transition_model import IntroTransitionModel, \
    TutorialTransitionModel, \
    IndividualTransitionModel, CollaborativeTransitionModel
from .models.observation_model import MstObservationModel
from .models.reward_model import MstRewardModel

from .tools.loaders import make_network_resources, load_network

from .agent import Human, Robot, RobotAgent
from .agent.reasoning import TraversalPlanner


def list_worlds():
    """Create a list of the worlds that are available."""
    names = ['intro', 'tutorial']
    for test in ['pretest', 'posttest']:
        for i in range(1, 6):
            name = '{}-{}'.format(test, i)
            names.append(name)
    for i in range(1, 3):
        names.append('collaboration-{}'.format(i))
    names.append('debriefing')

    return names


def create_all_worlds(verbose=False):
    """Create all of the world instances."""
    # Create a list of world names to be initialised.
    names = list_worlds()

    # Initialise each world.
    worlds = {name: create_world(name, verbose=verbose) for name in names}

    return worlds


def create_world(name, history=None, state_no=None, verbose=False):
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
    else:
        world_type = IndividualWorld
    # else:
        # raise NotImplementedError

    # Read the resources via temporary files and create a world instance.
    with importlib_resources.as_file(resources['graph']) as graph_file, \
            importlib_resources.as_file(resources['layout']) as layout_file:
        network = load_network(graph_file, layout_file, verbose=verbose)

    # Construct the initial state.
    if history is None:
        if world_type is IndividualWorld:
            init_state = EnvironmentState(
                network=network, agents=frozenset({Human}),
                attempt_no=1, max_attempts=None, is_paused=False)
        elif world_type is CollaborativeWorld:
            init_state = EnvironmentState(
                network=network, agents=frozenset({Robot}),
                attempt_no=1, max_attempts=4, is_paused=False)
        elif world_type is IntroWorld:
            init_state = EnvironmentState(network=network)
        elif world_type is TutorialWorld:
            init_state = EnvironmentState(network=network)
        else:
            raise NotImplementedError
        history = [init_state]
    else:
        history = history

    # Construct the world.
    world = world_type(history, name=name, state_no=state_no)

    if verbose:
        print('Done!')

    return world


def update_belief(agent, action, observation=None, is_executed=True):
    """TODO"""
    # print('### updating belief for', action, is_executed)
    cur_env_state = agent.cur_belief.mpe()

    if is_executed:
        next_state = copy.deepcopy(agent.state)
    else:
        next_state = agent.state

    # Update next state subgraph.
    beliefs_list = [
        next_state.beliefs['me'],
        next_state.beliefs['me']['you'],
        next_state.beliefs['me']['you']['me'],
    ]
    suggested = cur_env_state.network.suggested_edge
    for beliefs in beliefs_list:
        for u, v, d in beliefs['world'].edges(data=True):
            d['is_selected'] = cur_env_state.network.subgraph.has_edge(u, v)
            d['is_suggested'] = u, v == suggested or v, u == suggested

    if is_executed:
        if action.agent is Human:
            beliefs = next_state.beliefs['me']['you']
        elif action.agent is Robot:
            beliefs = next_state.beliefs['me']['you']['me']
        else:
            raise ValueError
    else:
        beliefs = next_state.beliefs['me']

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

        elif isinstance(action, ClearAction):
            for u, v in cur_env_state.network.subgraph.edges():
                value = beliefs['world'][u][v]['is_optimal']
                if value is None:
                    value = 0
                value = value - 0.1
                if value < 0:
                    value = 0
                beliefs['world'][u][v]['is_optimal'] = value

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

    # If robot, update others as not believed to be true.
    if action.agent is Robot:
        for action in agent.planner.explanation.others:
            if isinstance(action, PickAction):
                u, v = action.edge
                if cur_env_state.network.subgraph.has_edge(u, v):
                    value = None
                else:
                    value = 0.0
                beliefs['world'][u][v]['is_optimal'] = value

    # Update the current node if any.
    next_state.cur_node = agent.planner.cur_node

    if is_executed:
        agent.mental_history.append(next_state)
        agent.state = next_state


class World(pomdp_py.POMDP):
    """A world describing the interaction between an agent and the environment.

    An Agent operates in an environment by taking actions,
        receiving observations, and updating its belief.
    An Environment maintains the true state of the world.
    """

    def __init__(self, history, transition_model, policy_model,
                 state_no=None, name='World'):

        self.name = name

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
        # except Exception as e:
        #     print(e)
        #     print('Can not set state to number {}'.format(state_no))

        # cur_state = history[-1]
        cur_state = history[self.state_index]
        # print('### cur state is', cur_state, state_no)

        # Create a reward model.
        reward_model = MstRewardModel()
        observation_model = MstObservationModel()

        # Initialise an agent.
        # The state is fully observable.
        # init_belief = pomdp_py.Histogram({cur_state: 1.0})
        # agent = pomdp_py.Agent(init_belief,
        #                        policy_model,
        #                        transition_model,
        #                        MstObservationModel(),
        #                        reward_model)

        # Initialise an agent.
        # The state is fully observable.
        mental_state = MentalState(cur_state.network.graph)
        agent = RobotAgent(
            cur_state, policy_model, transition_model=transition_model,
            observation_model=observation_model, reward_model=reward_model,
            mental_state=mental_state)
        agent.planner = TraversalPlanner(cur_state)

        # Initialise an environment.
        # MstEnvironment
        env = pomdp_py.Environment(cur_state, transition_model, reward_model)

        # Construct an instance from the agent and the environment.
        super().__init__(agent, env, name=name)

        # Update the agent.
        if self.num_states == 0:
            self.act(ObserveAction(agent=Robot))

        # Have the robot make a plan and update its beliefs.
        robot_action = self.agent.planner.plan()
        update_belief(self.agent, robot_action, is_executed=False)
        # print('### Robot made a plan to', action)

    def __str__(self):
        return self.__repr__()

    def __repr__(self):
        return 'World({}:{})'.format(self.name, self.env.state)

    @property
    def state_no(self):
        return self._state_no

    @state_no.setter
    def state_no(self, value):
        # if value is not None:
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
        """number of states in the history"""
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

    @property
    def cur_mental_state(self):
        """Current state of the environment."""
        index = self.state_no - 1  # - 2  #1
        if index >= 0 and index < len(self.agent.mental_history):
            return self.agent.mental_history[index]
        else:
            return self.agent.mental_history[0]

    def act(self, action, verbose=False):
        # Relocate in history if not at the last state.
        if self.state_no != self.num_states:
            # Rebase.
            self.env.state_transition(SetStateAction(self.cur_state))
            print()
            # Clean history.
            self._history = self._history[:self.state_index+1]

        # Apply the state transition.
        state = copy.deepcopy(self.env.state)
        env_reward = self.env.state_transition(action)
        next_state = self.env.state

        # Update the history.
        self._history.extend([action, next_state])

        # Update the agent.
        real_observation = self.env.provide_observation(
            self.agent.observation_model, action)

        self.agent.update_history(action, real_observation)
        # problem.agent.update_history(real_action, real_observation)
        update_belief(self.agent, action, real_observation)
        self.agent.policy_model.update(state, next_state, action)

        # TODO: run a belief update function.
        # Fully observable: immediate access to the state.
        new_belief = pomdp_py.Histogram({next_state: 1.0})
        self.agent.set_belief(new_belief)

        # Move to the new state.
        self.state_no = self.num_states

        # Reasoning.
        self.agent.planner.update(action, real_observation)
        robot_action = self.agent.planner.plan()
        update_belief(self.agent, robot_action, is_executed=False)

        # Update the planner.
        # if planner is not None:
        #     planner.update(self.agent, action, real_observation)

        # Print info.
        if verbose:
            print()
            print("---acting---")
            # print("==== Step %d ====" % (self._step+1))
            # self._step = self._step + 1
            print("True state: %s" % str(state))
            print("Action: %s" % repr(action))
            # print("Belief: %s" % str(cur_belief))
            # print(">> Observation: %s" % str(real_observation))
            print("Reward: %s" % str(env_reward))
            # print("Reward (Cumulative): %s" % str(self._total_reward))
            # print("Reward (Cumulative Discounted): %s" %
            #       str(self._total_discounted_reward))
            print("Next state: %s" % str(next_state))

            print("New Belief: %s" % str(new_belief))
            print("------------")
            print()

        # To print the world after the action.
        return self


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

    def __init__(self, state, name='IndividualWorld', **kwargs):
        transition_model = IndividualTransitionModel()
        policy_model = IndividualPolicyModel()

        super().__init__(
            state, transition_model=transition_model,
            policy_model=policy_model, name=name, **kwargs)


class CollaborativeWorld(World):
    """TODO"""

    def __init__(self, state, name='CollaborativeWorld', **kwargs):
        transition_model = CollaborativeTransitionModel()
        policy_model = CollaborativePolicyModel()

        super().__init__(
            state, transition_model=transition_model,
            policy_model=policy_model, name=name, **kwargs)


# make_strategy_text
# belief update
