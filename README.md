# JUSThink World

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

Python package for representing and visualising the problem and its state for the JUSThink human-robot collaborative activity.

A `world` indicates the agent interacting with its environment, following the design principles [here](https://h2r.github.io/pomdp-py/html/design_principles.html) [1].

## Installation

This package exclusively targets Python 3. 
The main Python dependencies are:

* [pomdp_py](https://h2r.github.io/pomdp-py/html/) for describing the world/problem as an agent interacting with its environment [1]
* [networkx](https://networkx.org/) for representing and reasoning with the networks in the activity
* [pyglet](https://pyglet.readthedocs.io/en/latest/) for visualising and interacting with the activity from a role (human or the robot)

### Steps to Install from Source

1) Clone this ([JUSThink World](https://github.com/utku-norman/justhink_world)) package.
```
git clone https://github.com/utku-norman/justhink_world.git
```

2) Create a new [virtual environment](https://docs.python.org/3/tutorial/venv.html) and activate it (can do so in the same folder. Note that the folder name `venv` is [git-ignored](https://git-scm.com/docs/gitignore)).
```
cd justhink_world
rm -rf venv    # Delete if there is an existing virtual environment for a clean install.
python3 -m venv venv
source venv/bin/activate
```

3) Install this package, along with the remaining dependencies via `pip` (in '-e' i.e. editable mode for "developer mode", e.g. if you intend to edit the library)
```
pip install -e .
```


## Testing

You can check the installation in a Python interpreter (e.g. by running `python` in a terminal).

### Print a list of available worlds and try to initialise all of the worlds.
```
from justhink_world import list_worlds, create_all_worlds

# Print the list of available worlds (i.e. the pretest worlds, collaborative activity worlds etc.).
print(list_worlds())

worlds = create_all_worlds()

for name, world in worlds.items():
    print(name, world)
```


### Render an environment state (non-interactive).

```
from justhink_world import create_world, show_state
from justhink_world.domain.action import PickAction

world = create_world('pretest-1')
world.act(PickAction((3, 1)))
world.act(PickAction((1, 4)))

show_state(world.cur_state)
```


### Try out an individual (i.e. a test) world (interactive).
Use `left`-`right` keys to navigate to the previous and the next state, 
`home`-`end` keys to navigate to the first and the last state, 
`p` to toggle pause, and `tab` to toggle the role.

Taking an action like picking an edge at a navigated state clears the future history and moves the application to the new state.

#### For made up actions.
```
from justhink_world import create_world, show_world
from justhink_world.domain.action import PickAction, ClearAction, \
AttemptSubmitAction, ContinueAction, SubmitAction

# Create a world.
world = create_world('pretest-1')

# Act on the world.
world.act(PickAction((3, 1)))
world.act(PickAction((1, 4)))
world.act(AttemptSubmitAction())
world.act(ContinueAction())
world.act(ClearAction())
world.act(PickAction((5, 6)))
world.act(AttemptSubmitAction())
world.act(SubmitAction())

# Visualise the world.
show_world(world)


# Print the current state and MST cost.
state = world.cur_state
print(state, state.network.get_mst_cost())
# Print available actions at the current state.
print(world.agent.all_actions)
```

#### For actual logs.
```
from justhink_world import create_world, show_world, load_log

world_name = 'pretest-1'

# Load the log table for a sample and activity.
history = load_log(sample_no=1, world_name=world_name)

# Create a world with that history.
world = create_world(world_name, history)

show_world(world)
```


### Try out a collaborative world (interactive).
Use `left`-`right` keys to navigate to the previous and the next state, 
`home`-`end` keys to navigate to the first and the last state, 
`p` to toggle pause, and `tab` to toggle the role.

Taking an action like suggesting an edge at a navigated state clears the future history and moves the application to the new state.

```
from justhink_world import create_world, show_world
from justhink_world.agent import Human, Robot
from justhink_world.domain.action import SuggestPickAction, \
	AgreeAction, DisagreeAction

# Create a world.
world = create_world('collaboration-1')

# Act on the world.
world.act(SuggestPickAction((3, 1), agent=Robot))
world.act(AgreeAction(agent=Human))
world.act(SuggestPickAction((1, 4), agent=Human))

# Visualise the world.
show_world(world)
```

#### Replay actual logs.
```
from justhink_world import create_world, load_log, show_world

world_name = 'collaboration-1'

# Load the log table for a sample and activity.
history = load_log(sample_no=3, world_name=world_name)

# Create a world with that history.
world = create_world(world_name, history)

show_world(world)
```


#### Playground
```
from justhink_world import create_world, show_world, show_mind, show_all
world = create_world('pretest-1'); show_all(world)

world = create_world('collaboration-1'); show_all(world)



show_mind(world)




show_world(world)

# Print history.
print(world.history)
# Print the current state and MST cost.
state = world.env.state
print(state, state.network.get_mst_cost())
# Print available actions at the current state.
print(world.agent.all_actions)"

```


## Troubleshooting

### Installation Issues

Install Python dependency [pomdp_py](https://h2r.github.io/pomdp-py/html/) with the following commands (or by following [here](https://h2r.github.io/pomdp-py/html/installation.html))
```
pip install Cython
pip install pomdp-py
```
If you encounter an error regarding Pygraphviz while installing pomdp_py, first install that package by following [here](https://pygraphviz.github.io/documentation/stable/install.html), and than pomdp_py again.



## References <a name="references"></a>

[1] Zheng, K., & Tellex, S. (2020). pomdp_py: A Framework to Build and Solve POMDP Problems. arXiv preprint arXiv:2004.10099.
