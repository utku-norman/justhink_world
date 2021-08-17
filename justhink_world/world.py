import sys
import copy

import importlib_resources

import pomdp_py

from .domain.state import EnvironmentState, NetworkState
from .domain.action import ObserveAction, SetStateAction

# from .env.env import MstEnvironment

# from .domain.observation import Observation

from .models.policy_model import IntroPolicyModel, DemoPolicyModel, \
    IndividualPolicyModel, CollaborativePolicyModel

from .models.transition_model import IntroTransitionModel, \
    DemoTransitionModel, \
    IndividualTransitionModel, CollaborativeTransitionModel
from .models.observation_model import MstObservationModel
from .models.reward_model import MstRewardModel

from .tools.loaders import load_graph_from_edgelist, load_graph_from_json

from .agent import HumanAgent, RobotAgent


class World(pomdp_py.POMDP):
    """A world describing the interaction between an agent and the environment.

    An Agent operates in an environment by taking actions,
        receiving observations, and updating its belief.
    An Environment maintains the true state of the world.
    """

    def __init__(self,
                 history,
                 transition_model,
                 policy_model,
                 name='World'):

        self.name = name

        # States.
        if not isinstance(history, list):
            history = [history]

        # History, for navigating states.
        self._history = history
        self.state_no = self.num_states

        # Current state as the last state.
        cur_state = history[-1]

        # Create a reward model.
        reward_model = MstRewardModel()

        # Initialise an agent.
        # The state is fully observable.
        init_belief = pomdp_py.Histogram({cur_state: 1.0})
        agent = pomdp_py.Agent(init_belief,
                               policy_model,
                               transition_model,
                               MstObservationModel(),
                               reward_model)
        # Update the available actions in the policy model
        # to access agent.all_actions even at the initial state.
        agent.policy_model.update_available_actions(cur_state)

        # Initialise an environment.
        # MstEnvironment
        env = pomdp_py.Environment(cur_state,
                                   transition_model,
                                   reward_model)

        # Construct an instance from the agent and the environment.
        super().__init__(agent, env, name=name)

        # Update the agent.
        # self.act(ObserveAction())

    def __str__(self):
        return self.__repr__()

    def __repr__(self):
        return 'World({}:{})'.format(self.name, self.env.state)

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
        """Current state of the environment"""
        return self._history[self.state_index]

        # Similarly from observation history
        # if self.state_no == 0:
        #     return None
        # else:
        #     return self.agent.history[self.state_no-1][1].state

    @property
    def state_index(self):
        return (self.state_no - 1) * 2

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

        # Update the agent.
        real_observation = self.env.provide_observation(
            self.agent.observation_model, action)

        self.agent.update_history(action, real_observation)
        self.agent.policy_model.update(state, next_state, action)

        # TODO: run a belief update function.
        # Fully observable: immediate access to the state.
        new_belief = pomdp_py.Histogram({next_state: 1.0})
        self.agent.set_belief(new_belief)

        # Update the history.
        self._history.extend([action, next_state])
        self.state_no = self.num_states

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

    def __init__(self, state, name='IntroWorld'):
        transition_model = IntroTransitionModel()
        policy_model = IntroPolicyModel()

        super().__init__(
            state, transition_model=transition_model,
            policy_model=policy_model, name=name)


class DemoWorld(World):
    """TODO"""

    def __init__(self, state, name='DemoWorld'):
        transition_model = DemoTransitionModel()
        policy_model = DemoPolicyModel()

        super().__init__(
            state, transition_model=transition_model,
            policy_model=policy_model, name=name)


class IndividualWorld(World):
    """TODO"""

    def __init__(self, state, name='IndividualWorld'):
        transition_model = IndividualTransitionModel()
        policy_model = IndividualPolicyModel()

        super().__init__(
            state, transition_model=transition_model,
            policy_model=policy_model, name=name)


class CollaborativeWorld(World):
    """TODO"""

    def __init__(self, state, name='CollaborativeWorld'):
        transition_model = CollaborativeTransitionModel()
        policy_model = CollaborativePolicyModel()

        super().__init__(
            state, transition_model=transition_model,
            policy_model=policy_model, name=name)


def list_worlds():
    """Create a list of the worlds that are available."""
    names = ['intro', 'demo']
    for test in ['pretest', 'posttest']:
        for i in range(1, 6):
            name = '{}-{}'.format(test, i)
            names.append(name)
    for i in range(1, 3):
        names.append('collab-activity-{}'.format(i))
    names.append('debriefing')

    return names


def init_all_worlds(verbose=False):
    """Create all of the world instances."""
    # Create a list of world names to be initialised.
    names = list_worlds()

    # Initialise each world.
    worlds = {name: init_world(name, verbose) for name in names}

    return worlds


def init_world(name, verbose=False):
    """Create a world instance by the world's name."""
    # Create the file names for the world.
    resources = select_world_resources(name)

    # Determine the type of the world.
    if name == 'intro':
        world_type = IntroWorld
    elif name == 'demo':
        world_type = DemoWorld
    elif 'collab-activity' in name:
        world_type = CollaborativeWorld
    # elif 'test' in name:
    else:
        world_type = IndividualWorld
    # else:
        # raise NotImplementedError

    # Read the resources via temporary files and create a world instance.
    with importlib_resources.as_file(resources['graph']) as graph_file, \
            importlib_resources.as_file(resources['layout']) as layout_file:
        return load_world(graph_file,
                          layout_file,
                          world_type=world_type,
                          name=name,
                          verbose=verbose)


def load_world(graph_file,
               layout_file,
               world_type,
               name=None,
               verbose=False):
    """Load a world from its resource files."""
    # # Type check for the world type.
    # assert world_type is IndividualWorld \
    #     or world_type is CollaborativeWorld

    if verbose:
        print('Initialising world {} ...'.format(name))

    # Load the graph.
    graph = load_graph_from_edgelist(graph_file)

    # Load the layout.
    layout = load_graph_from_json(layout_file)

    # Print debug message on the graph and the layout.
    if verbose:
        print('Using graph: {} with layout: {}'.format(
            graph_file.name, layout_file.name))

    # Fill in the possible edges and their attributes (e.g. cost).
    full_graph = copy.deepcopy(layout)
    for u, v, d in graph.edges(data=True):
        full_graph.add_edge(u, v, **d)

    # Construct the initial state.
    network = NetworkState(graph=full_graph)
    if world_type is IndividualWorld:
        init_state = EnvironmentState(
            network=network,
            agents=frozenset({HumanAgent}),
            attempt_no=1,
            max_attempts=None,
            is_paused=False,
        )
    elif world_type is CollaborativeWorld:
        init_state = EnvironmentState(
            network=network,
            agents=frozenset({RobotAgent}),
            attempt_no=1,
            max_attempts=4,
            is_paused=False,
        )
    elif world_type is IntroWorld:
        init_state = EnvironmentState(network=network)
    elif world_type is DemoWorld:
        init_state = EnvironmentState(network=network)
    else:
        raise NotImplementedError

    # Construct the world.
    world = world_type(init_state, name=name)

    if verbose:
        print('Done!')

    return world


def select_world_resources(name):
    """Select a world's resources by the world's name."""
    # Create a container for the world sources.
    package = importlib_resources.files('justhink_world.resources.networks')

    # Make the source file names.
    graph_file = '{}_edgelist.txt'.format(name)
    layout_file = '{}_layout.json'.format(name)

    # Make the sources.
    # Create a container for the world sources.
    graph_resource = package.joinpath(graph_file)
    layout_resource = package.joinpath(layout_file)

    # Check if the sources are available.
    for source in [graph_resource, layout_resource]:
        try:
            assert source.exists()
        except AssertionError:
            print('Resource file {} does not exist for world "{}".'.format(
                source, name))
            sys.exit(1)

    return {'graph': graph_resource, 'layout': layout_resource}
