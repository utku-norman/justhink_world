import sys
import copy

import importlib_resources

import pomdp_py

from .domain.state import EnvironmentState, NetworkState, Button
from .domain.action import SetStateAction

# from .env.env import MstEnvironment

# from .domain.observation import Observation

from .models.policy_model import IndivPolicyModel, CollabPolicyModel
from .models.transition_model import IndivTransitionModel, \
    CollabTransitionModel
from .models.observation_model import MstObservationModel
from .models.reward_model import MstRewardModel

from .tools.loaders import load_graph_from_edgelist, load_graph_from_json

from .agent.agent import AgentSet, HumanAgent, RobotAgent


class World(pomdp_py.POMDP):
    """A world describing the interaction between an agent and the environment.

    An Agent operates in an environment by taking actions,
        receiving observations, and updating its belief.
    An Environment maintains the true state of the world.
    """

    def __init__(self,
                 states,
                 transition_model,
                 policy_model,
                 name='World'):
        # self.layout = layout

        # States.
        if not isinstance(states, list):
            states = [states]

        # History, for navigating states.
        self.history = states
        self.state_no = self.get_state_count()
        # Current state as the last state.
        cur_state = states[-1]

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

    def __str__(self):
        return self.__repr__()

    def __repr__(self):
        return 'World({})'.format(self.env.state)

    # def reset(self):
    #     # Reset the state.
    #     self.env.state.reset()
    #     self.history = [self.init_state]

    #     # Reset the agent.
    #     new_belief = pomdp_py.Histogram({self.env.state: 1.0})
    #     self.agent.set_belief(new_belief)

    # def set_state(self, state):
    #     self.history.append((self.env.state, None, state))
    #     self.env.state = state

    def get_state_count(self):
        return len(self.history) // 2 + 1

    def get_prev_state(self, first=False):
        if first:
            self.state_no = 1
        elif self.state_no > 1:
            self.state_no -= 1

        return self.get_state()

    def get_next_state(self, last=False):
        n_states = self.get_state_count()
        if last:
            self.state_no = n_states
        elif self.state_no < n_states:
            self.state_no += 1

        return self.get_state()

    def get_state(self, state_no=None):
        '''Get the indexed state, or current state if None'''
        return self.history[self.get_state_index(state_no)]

    def get_state_index(self, state_no=None):
        '''Get the indexed state, or current state if None'''
        if state_no is None:
            index = (self.state_no - 1) * 2
        else:
            index = (state_no - 1) * 2

        return index

    # def update_scene(self, verbose=False):
    #     # Get the indexed state.
    #     i = self.state_no
    #     if i == 0:  # initial state.
    #         state = self.init_state
    #     else:  # next state of the transition.
    #         state = self.history[i-1][2]

    def act(self, action, verbose=False):
        # print('##### acting', action)

        # Relocate in history if not at the last state.
        # TODO: also agent's history? possibly drop world history
        # in favor of agent's history.
        if self.state_no != self.get_state_count():
            state = self.get_state()
            # Rebase.
            self.env.state_transition(SetStateAction(state))
            # Clean history.
            # print('### hist-bef', self.history)
            self.history = self.history[:self.get_state_index()+1]
            # print('### hist-aft', self.history)

        # Apply the state transition.
        state = copy.deepcopy(self.env.state)
        env_reward = self.env.state_transition(action)
        next_state = self.env.state

        # Update the history.
        self.history.extend([action, next_state])

        # Update the agent.
        real_observation = self.env.provide_observation(
            self.agent.observation_model, action)

        self.agent.update_history(action, real_observation)
        self.agent.policy_model.update(state, next_state, action)

        # TODO: run a belief update function.
        # Fully observable: immediate access to the state.
        new_belief = pomdp_py.Histogram({next_state: 1.0})
        self.agent.set_belief(new_belief)

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

        self.state_no = self.get_state_count()

        # To print the world after the action.
        return self


class IndividualWorld(World):
    """TODO"""

    def __init__(self, state):
        transition_model = IndivTransitionModel()
        policy_model = IndivPolicyModel()

        super().__init__(state,
                         transition_model=transition_model,
                         policy_model=policy_model,
                         name="IndividualWorld")


class CollaborativeWorld(World):
    """TODO"""

    def __init__(self, state):
        transition_model = CollabTransitionModel()
        policy_model = CollabPolicyModel()

        super().__init__(state,
                         transition_model=transition_model,
                         policy_model=policy_model,
                         name="CollaborativeWorld")


def list_worlds():
    names = ['intro', 'indiv-illustrate']
    for test in ['pretest', 'posttest']:
        for i in range(1, 6):
            name = '{}-{}'.format(test, i)
            names.append(name)
    names.append('collab-activity')
    names.append('collab-activity-2')
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
    if 'collab-activity' in name:
        world_type = CollaborativeWorld
    else:
        world_type = IndividualWorld

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
    # Type check for the world type.
    assert world_type is IndividualWorld \
        or world_type is CollaborativeWorld

    if verbose:
        print('Initialising world {} ...'.format(name))

    # Load the graph.
    graph = load_graph_from_edgelist(graph_file)

    # Load the layout.
    layout = load_graph_from_json(layout_file)
    # Fill in the possible edges and their attributes (e.g. cost).
    for u, v, d in graph.edges(data=True):
        layout.add_edge(u, v, **d)

    # Print debug message on the graph and the layout.
    if verbose:
        print('Using graph: {} with layout: {}'.format(
            graph_file.name, layout_file.name))

    # Construct the initial state.
    # init_state = graphState(graph=graph)
    network = NetworkState(graph=graph)
    if world_type is IndividualWorld:
        init_state = EnvironmentState(
            network=network,
            layout=layout,
            agents=AgentSet({HumanAgent}),
            attempt_no=1,
            max_attempts=None,
            is_paused=False,
        )
    elif world_type is CollaborativeWorld:
        init_state = EnvironmentState(
            network=network,
            layout=layout,
            agents=AgentSet({RobotAgent}),
            attempt_no=1,
            max_attempts=4,
            is_paused=False,
        )
    else:
        raise NotImplementedError

    # Construct the world.
    world = world_type([init_state])

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
