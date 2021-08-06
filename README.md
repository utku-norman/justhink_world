# JUSThink World

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

Python package for representing the problem and the state in the JUSThink human-robot collaborative activity


## Installation

This package exclusively targets Python 3. 
The main Python dependencies are:

* [pomdp_py](https://h2r.github.io/pomdp-py/html/) for describing the problem, state transitions etc.
* [networkx](https://networkx.org/) for representing and reasoning with the networks in the activity


### Steps to Install from Source

1) Clone this ([JUSThink World](https://github.com/utku-norman/justhink_world)) package.
```
git clone https://github.com/utku-norman/justhink_world.git
```

2) (optional-recommended) Create a new [virtual environment](https://docs.python.org/3/tutorial/venv.html) and activate it (can do so in the same folder, as folder name `venv` is [git-ignored](https://git-scm.com/docs/gitignore)).
```
cd justhink_world
rm -rf venv    # Delete if there is an existing virtual environment for a clean install
virtualenv venv
source venv/bin/activate
```

3) Install Python dependency pomdp_py with the following commands (or by following [here](https://h2r.github.io/pomdp-py/html/installation.html))
```
pip install Cython
pip install pomdp-py
```
If you encounter an error regarding Pygraphviz while installing pomdp_py, try installing it following [here](https://pygraphviz.github.io/documentation/stable/install.html).

4) Install this package, along with the remaining dependencies via `pip` (in '-e' i.e. editable mode for "developer mode": if you intend to edit the library)
```
pip install -e .
```


## Testing

You can check the installation by trying to import the messages and services in a Python interpreter (e.g. by running `python` in a terminal).

Print a list of available worlds, try to initialise all of the worlds.
```
from justhink_world.world import list_worlds, init_all_worlds

print(list_worlds())

worlds = init_all_worlds()

for name, world in worlds.items():
    print(name, world)
```

Try out an individual (i.e. a test) world.
```
from justhink_world.world import init_world
from justhink_world.visual import WorldWindow
from justhink_world.domain.action import PickAction, ClearAction, SubmitAction

# Create a world.
world = init_world('pretest-1')

# Act on the world.
world.act(PickAction((3, 1)))
world.act(PickAction((1, 4)))
world.act(ClearAction())
world.act(PickAction((5, 6)))
world.act(SubmitAction())

# Print state information. 
state = world.env.state
print(state, state.network.get_mst_cost())
# Print available actions at the current state.
print(world.agent.all_actions)

# Visualise the world.
WorldWindow(world)

```


Try out a collaborative world.
```
from justhink_world.world import init_world, init_all_worlds, list_worlds
from justhink_world.visual import WorldWindow
from justhink_world.domain.action import SuggestPickAction, SuggestSubmitAction, \
	AgreeAction, DisagreeAction
from justhink_world.agent.agent import HumanAgent, RobotAgent

# Print a list of available worlds.
print(list_worlds())

# Create a world.
world = init_world('collab-activity')

# Act on the world.
world.act(SuggestPickAction((3, 1), agent=RobotAgent))
world.act(AgreeAction(agent=HumanAgent))
world.act(SuggestPickAction((1, 4), agent=HumanAgent))

# Print state information.
state = world.env.state
print(state, state.network.get_mst_cost())
# Print available actions at the current state.
print(world.agent.all_actions)

# Visualise the world.
WorldWindow(world)

print(world.history)
```


