import sys
import copy

import importlib_resources

import pomdp_py

from .domain.state import State

from .env.env import MstEnvironment

from .domain.observation import NullObservation

from .models.policy_model import MstPolicyModel
from .models.transition_model import TestTransitionModel, \
    CollaborativeTransitionModel
from .models.observation_model import MstObservationModel
from .models.reward_model import MstRewardModel

from .tools.loaders import load_network_from_edgelist, load_network_from_json


class World(pomdp_py.POMDP):
    """A world, represented as a POMDP instance i.e. agent + environment."""

    def __init__(self, state, layout, transition_model, name='World'):

        self.layout = layout

        # Create a reward model.
        reward_model = MstRewardModel()

        # Initialise an agent.
        # The state is fully observable.
        init_belief = pomdp_py.Histogram({state: 1})
        agent = pomdp_py.Agent(init_belief,
                               MstPolicyModel(),
                               transition_model,
                               MstObservationModel(),
                               reward_model)

        # Initialise an environment.
        env = MstEnvironment(state,
                             transition_model,
                             reward_model)

        # Construct an instance from the agent and the environment.
        super().__init__(agent, env, name=name)

    def reset(self):
        # Reset the state.
        self.env.state.reset()

        # Reset the agent.
        new_belief = pomdp_py.Histogram({self.env.state: 1.0})
        self.agent.set_belief(new_belief)

    def set_state(self, state):
        self.env.state = state

    def act(self, action, verbose=False):
        # planner=None,
        if action is not None:
            true_state = copy.deepcopy(self.env.state)
            env_reward = self.env.state_transition(action, execute=True)

            # Observations are not implemented.
            real_observation = NullObservation
            # real_observation = self.env.provide_observation(
            #     self.agent.observation_model, action)

            self.agent.update_history(action, real_observation)
            # if planner is not None:
            #     planner.update(self.agent, action, real_observation)
            self.agent.policy_model.update(true_state, self.env.state, action)

            # immediate access to the self state.
            new_belief = pomdp_py.Histogram({self.env.state: 1.0})
            self.agent.set_belief(new_belief)

            new_belief = pomdp_py.Histogram(
                {self.env.state: 1})  # fully observable
            self.agent.set_belief(new_belief)

            # Print info.
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


class CollaborativeWorld(World):
    """TODO"""

    def __init__(self, layout, state):
        transition_model = CollaborativeTransitionModel()

        super().__init__(state,
                         layout,
                         transition_model=transition_model,
                         name="CollaborativeWorld")


class TestWorld(World):
    """TODO"""

    def __init__(self, layout, state):
        transition_model = TestTransitionModel()

        super().__init__(state,
                         layout,
                         transition_model=transition_model,
                         name="TestWorld")


def init_all_worlds(verbose=False):
    """Create all of the world instances."""
    # Create a list of world names to be initialised.
    names = ['intro', 'indiv-illustrate']
    for test in ['pretest', 'posttest']:
        for i in range(1, 6):
            name = '{}-{}'.format(test, i)
            names.append(name)
    names.append('collab-activity')
    names.append('collab-activity-2')
    names.append('debriefing')

    # Initialise each world.
    worlds = {name: init_world(name, verbose) for name in names}

    return worlds


def init_world(name, verbose=False):
    """Create a world instance by the world's name."""
    # Create the file names for the world.
    resources = select_world_resources(name)

    # Determine the type of the world.
    if 'collab-activity' in name:
        world_type = CollaborativeWorld
    else:
        world_type = TestWorld

    # Read the resources via temporary files and create a world instance.
    with importlib_resources.as_file(resources['network']) as network_file, \
            importlib_resources.as_file(resources['layout']) as layout_file:
        return load_world(network_file,
                          layout_file,
                          world_type=world_type,
                          name=name,
                          verbose=verbose)


def select_world_resources(name):
    """Select a world's resources by the world's name."""
    # Create a container for the world sources.
    package = importlib_resources.files('justhink_world.resources.networks')

    # Make the source file names.
    network_file = '{}_edgelist.txt'.format(name)
    layout_file = '{}_layout.json'.format(name)

    # Make the sources.
    # Create a container for the world sources.
    network_resource = package.joinpath(network_file)
    layout_resource = package.joinpath(layout_file)

    # Check if the sources are available.
    for source in [network_resource, layout_resource]:
        try:
            assert source.exists()
        except AssertionError:
            print('Resource file {} does not exist for world "{}".'.format(
                source, name))
            sys.exit(1)

    return {'network': network_resource, 'layout': layout_resource}


def load_world(network_file,
               layout_file,
               world_type,
               name=None,
               verbose=False):
    """Load a world from its resource files."""
    # Type check for the world type.
    assert world_type is TestWorld \
        or world_type is CollaborativeWorld

    if verbose:
        print('Initialising world {} ...'.format(name))

    # Load the network.
    network = load_network_from_edgelist(network_file)

    # Load the layout.
    layout_network = load_network_from_json(layout_file)
    for u, v, d in network.edges(data=True):
        layout_network.add_edge(u, v, **d)

    # Print debug message on the network and the layout.
    if verbose:
        print('Using network: {} with layout: {}'.format(
            network_file.name, layout_file.name))

    # Construct the initial state.
    init_state = State(network=network)

    # Construct the world.
    world = world_type(layout_network, init_state)

    if verbose:
        print('Done!')

    return world
