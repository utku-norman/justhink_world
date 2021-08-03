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

```
from justhink_world.world import init_world, init_all_worlds
from justhink_world.visual import WorldWindow
from justhink_world.domain.action import PickAction, SubmitAction


# Visualise a world.
# world = init_world('collab-activity')
world = init_world('pretest-1')
state = world.env.state

state.get_mst_cost()  # state.network.edges

action = PickAction((3, 1))
world.act(action)

WorldWindow(world)

```
