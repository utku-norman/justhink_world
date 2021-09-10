# JUSThink World

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)


## Overview

This repository contains the [justhink_world] Python package to represent and visualise activities in a pedagogical scenario that contains a human-robot collaborative learning activity for school children, named [JUSThink](https://www.epfl.ch/labs/chili/index-html/research/animatas/justhink/). The scenario aims to improve their computational thinking skills by applying abstract and algorithmic reasoning to solve an unfamiliar problem on networks.

The scenario consists of individual (e.g. as in a test) and collaborative (with a robot) activities.

* In an individual activity, a human learner is given a network of gold mines with possible positions for railway tracks, where each track if it is built connects one mine to another. The cost of each track is visible. The goal is to collect the gold by connecting the gold mines to each other, while spending as little as possible to build the tracks.
* In a collaborative activity, the human and the robot as (same-status) peers collaboratively construct a solution to this problem by deciding together which tracks to build, and submit it as their solution to the system.  They take turns in suggesting to select a specific connection, where the other either agrees or disagrees with this suggestion. A track will be built only if it is suggested by one and accepted by the other.

A human learner participates in the pedagogical scenario through an application ([justhink_scenario]). The robot behaviour is generated by [justhink_agent] and manifested by [justhink_robot]. They serve as [ROS] nodes that communicate via the custom ROS headers in [justhink_msgs].

A `world` in [justhink_world] is used to represent an activity via describing an interaction between an agent and its environment, following the design principles [here](https://h2r.github.io/pomdp-py/html/design_principles.html) [[1]](#references).
Briefly: 

* a `state` represents the state of the world: it contains information on the current solution (i.e. the selected connections in the network), the agents that can take actions (for turn-taking), the current attempt number etc.
* an `environment` maintains the state of the world via state transitions defined in a `transition model`.
* an `agent` operates in this environment by taking `action`s, receiving observations (fully observable), and updating its belief. An agent can list the available actions for a given state via its `policy model`.

**Keywords:** human-robot interaction, situated dialogue, mutual modelling, collaborative learning, computational thinking

### License

The whole package is under MIT License, see [LICENSE](LICENSE).

This README is based on the project [ros_best_practices](https://github.com/leggedrobotics/ros_best_practices), Copyright 2015-2017, Péter Fankhauser. It is licensed under the BSD 3-Clause Clear License. See [doc/LICENSE](doc/LICENSE) for additional details.

**Author: Utku Norman<br />
Affiliation: [CHILI Lab, EPFL](https://www.epfl.ch/labs/chili/)<br />
Maintainer: Utku Norman, utku.norman@epfl.ch**

The [justhink_world] package has been tested under Python 3.8 on Ubuntu 20.04.
This is research code, expect that it changes often and any fitness for a particular purpose is disclaimed.


<img src="doc/collab_activity.jpg" width="768" />


### Publications

If you use this work in an academic context, please cite the following publication(s):

* U. Norman, B. Bruno, and P. Dillenbourg, **Mutual Modelling Ability for a Humanoid Robot: How can it improve my learning as we solve a problem together?,** in Robots for Learning Workshop in 16th annual IEEE/ACM Conference on Human-Robot Interaction (HRI 2021). ([PDF](http://infoscience.epfl.ch/record/283614))

        @inproceedings{norman_mutual_2021,
        	author = {Norman, Utku and Bruno, Barbara and Dillenbourg, Pierre},
        	booktitle = {Robots for Learning Workshop in 16th annual {IEEE}/{ACM} Conference on Human-Robot Interaction ({HRI} 2021)},
        	title = {Mutual Modelling Ability for a Humanoid Robot: How can it improve my learning as we solve a problem together?},
        	url = {http://infoscience.epfl.ch/record/283614},
        	year = {2021},
        }


## Installation

### Building from Source

#### Dependencies

* [pomdp_py](https://h2r.github.io/pomdp-py/html/) to describe the world/problem as an agent interacting with its environment [[1]](#references)
* [networkx](https://networkx.org/) to represent and reason with the networks in an activity
* [pyglet](https://pyglet.readthedocs.io/en/latest/) to visualise and interact with the activity from a role (human or the robot)
* [importlib_resources](https://importlib-resources.readthedocs.io/en/latest/) to access to the resources like the images
* [pqdict](https://pypi.org/project/pqdict/) to implement a priority queue, used in the Prim's algorithm


#### Building

1) Clone this ([justhink_world]) repository:
```
git clone https://github.com/utku-norman/justhink_world.git
```

2) Create a new [virtual environment](https://docs.python.org/3/tutorial/venv.html) and activate it (can do so in the same folder. Note that the folder name `venv` is [git-ignored](https://git-scm.com/docs/gitignore)):
```
cd justhink_world
python3 -m venv venv
source venv/bin/activate
```

If you do not have `venv`, first install it by: `sudo apt install python3-venv`

3) Install this package, along with the remaining dependencies via `pip` (in '-e' i.e. editable mode for "developer mode")
```
pip install -e .
```

If you encounter an error regarding Pygraphviz while installing pomdp_py, first install its dependencies (as in [here](https://pygraphviz.github.io/documentation/stable/install.html)): `sudo apt install graphviz graphviz-dev; pip install pygraphviz`

4) Check the installation by running the following in a Python interpreter:
```
from justhink_world import list_worlds, create_all_worlds
worlds = create_all_worlds()
```

## Usage

### Print the list of available worlds and initialise all these worlds.
```
from justhink_world import list_worlds, create_all_worlds

print(list_worlds())

worlds = create_all_worlds()

for name, world in worlds.items():
    print(name, world)
```

### Render a state (non-interactive).
```
from justhink_world import create_world, show_state
from justhink_world.domain.action import PickAction

world = create_world('pretest-1')
world.act(PickAction((3, 1)))
world.act(PickAction((1, 4)))

show_state(world.cur_state)
```

<img src="doc/example_show_state.jpg" width="768" />


### Try out a world (interactive).

* Use `LEFT`-`RIGHT` keys to navigate to the previous and the next state, 
* Use `HOME`-`END` keys to navigate to the first and the last state, 
* Use `P` to toggle pause, and `tab` to toggle the role.
* Take an action like picking an edge (by drawing from one node to another) at a navigated state: keep the states up to that state, execute that action, and show the the new state (permanently removes the earlier future history).

#### Try out an individual (i.e. a test) world.

##### For a given sequence of actions.
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

# Visualise the world, from the last state by default.
show_world(world)

# Take a few more actions.
world.act(AttemptSubmitAction())
world.act(SubmitAction())

# Visualise the world, from the first state, on the current screen.
show_world(world, state_no=1, screen_index=0)
```

##### For real log data from a child.
```
from justhink_world import create_world, show_world, load_log

world_name = 'pretest-1'

# Load the log table for a sample and activity.
history = load_log(sample_no=1, world_name=world_name)

# Create a world with that history.
world = create_world(world_name, history)

# Display from the first state in the log.
show_world(world, state_no=1)
```


<img src="doc/example_test_log.gif" width="768" />


#### Try out a collaborative world.

##### For a given sequence of actions.
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

# Visualise the world, from the last state by default.
show_world(world)
```

##### For real log data from a child.
```
from justhink_world import create_world, load_log, show_world

world_name = 'collaboration-1'

# Load the log table for a sample and activity.
history = load_log(sample_no=3, world_name=world_name)

# Create a world with that history.
world = create_world(world_name, history)

show_world(world, state_no=1)
```


<img src="doc/example_collab_log.gif" width="768" />


#### Playground
Visualising a mental state for the robot:
```
from justhink_world import create_world, show_world, show_mind, show_all
world = create_world('pretest-1'); show_all(world)



world = create_world('collaboration-1'); show_all(world)

show_mind(world)
show_world(world)
```

Printing various information:
```
# Print history.
print(world.history)

# Print the current state and MST cost.
state = world.env.state
print(state, state.network.get_mst_cost())

# Print available actions at the current state.
print(world.agent.all_actions)
```

## Acknowledgements

This project has received funding from the European Union's Horizon 2020 research and innovation programme under grant agreement No 765955. Namely, the [ANIMATAS Project](https://www.animatas.eu/).

## Bugs & Feature Requests

Please report bugs and request features using the [Issue Tracker](https://github.com/utku-norman/justhink_world/issues).


## References <a name="references"></a>

[1] Zheng, K., & Tellex, S. (2020). pomdp_py: A Framework to Build and Solve POMDP Problems. arXiv preprint arXiv:2004.10099.


[ROS]: http://www.ros.org
[justhink_world]: https://github.com/utku-norman/justhink_world
[justhink_scenario]: https://github.com/utku-norman/justhink_scenario
[justhink_agent]: https://github.com/utku-norman/justhink_agent
[justhink_robot]: https://github.com/utku-norman/justhink_robot
[justhink_msgs]: https://github.com/utku-norman/justhink_msgs
