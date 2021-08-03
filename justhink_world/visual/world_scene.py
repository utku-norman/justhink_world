# import pyglet
# import pathlib as pl

import importlib_resources

# from .utils import update_scene_buttons, \
#     update_scene_press, update_scene_paused, \
#     update_scene_graph, update_scene_drag, update_scene_release, \
#     init_graphics, update_cost_label

from .graphics import init_graphics
from ..tools.networks import in_edges

# from justhink_world.domain.action import SubmitAction, SuggestPickAction

# from .scene import Scene


class WorldScene(object):
    def __init__(self, world, width=1920, height=1080):
        layout = world.layout
        state = world.env.state
        edges = state.edges

        self.scene_type = 'problem'

        self._layout = layout
        self._edges = edges
        self._terminal = False
        self._submit_suggested = False

        # Create a container for the image resources.
        image_container = importlib_resources.files(
            'justhink_world.resources.images')

        # Create the graphics.
        batch, graphics = init_graphics(self._layout,
                                        width, height,
                                        image_container,
                                        show_yes_no_buttons=True)
        self._batch = batch
        for key, obj in graphics.items():
            setattr(self, key, obj)

        # Display the current state.
        self.update(state)

    # Windowing methods.
    def on_draw(self):
        self._batch.draw()

    # Maintenance methods.
    def update(self, state, highlight=False):
        self._terminal = state.terminal

        added_nodes = set()

        self._edges = state.edges

        for u, v, d in self._layout.edges(data=True):
            is_added = in_edges(u, v, state.edges)
            is_suggested = (state.suggested == (u, v)) \
                or (state.suggested == (v, u))
            d['added_sprite'].visible = is_added
            d['selectable_sprite'].visible = not is_added
            d['selected_sprite'].visible = False
            # if is_suggested:
            #     print('Suggested', suggested)
            d['suggested_sprite'].visible = is_suggested

            if is_added:
                added_nodes.update((u, v))

        for u, d in self._layout.nodes(data=True):
            d['added_sprite'].visible = u in added_nodes
            # d['sprite'].visible = True # not u in added_nodes

        # Following are inefficient; to improve.
        # Process highlights for edges.
        for u, v, d in self._layout.edges(data=True):
            if highlight:
                d['cost_label'].color = (255, 0, 0, 255)
                d['cost_label'].bold = True
            else:
                d['cost_label'].color = (0, 0, 0, 255)
                d['cost_label'].bold = False

        # Process highlights for nodes.
        for u, d in self._layout.nodes(data=True):
            if highlight:
                d['label'].color = (255, 0, 0, 255)
                d['label'].bold = True
            else:
                d['label'].color = (0, 0, 0, 255)
                d['label'].bold = False

        # update_scene_paused(scene, scene._terminal)
