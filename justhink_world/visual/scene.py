import importlib_resources

from .graphics import init_graphics
from ..tools.networks import in_edges


from ..domain.state import EnvironmentState


class WorldScene(object):
    def __init__(self, state, width=1920, height=1080):
        assert isinstance(state, EnvironmentState)

        self._layout = state.layout

        # Create a container for the image resources.
        image_container = importlib_resources.files(
            'justhink_world.resources.images')

        # Create the graphics.
        batch, graphics = init_graphics(state.layout,
                                        width, height,
                                        image_container)
        for key, obj in graphics.items():
            setattr(self, key, obj)
        self._batch = batch

        # # Display the current state.
        if state is not None:
            self.update(state)

    # Windowing methods.
    def on_draw(self):
        self._batch.draw()

    # Maintenance methods.
    def update(self, state, highlight=False):
        # # Update the available actions.
        # self._policy_model.update_available_actions(state)

        # Update the selected edges.
        added_nodes = set()
        for u, v, d in self._layout.edges(data=True):
            is_added = in_edges(u, v, state.network.edges)
            e = state.network.suggested_edge
            is_suggested = (e == (u, v)) or (e == (v, u))
            d['added_sprite'].visible = is_added
            d['selectable_sprite'].visible = not is_added
            d['selected_sprite'].visible = False
            d['suggested_sprite'].visible = is_suggested

            if is_added:
                added_nodes.update((u, v))

        # Update the selected nodes.
        for u, d in self._layout.nodes(data=True):
            d['added_sprite'].visible = u in added_nodes
            # d['sprite'].visible = True # not u in added_nodes

        # Process highlights for edges.
        for u, v, d in self._layout.edges(data=True):
            if highlight:
                color = (255, 0, 0, 255)
                bold = True
            else:
                color = (0, 0, 0, 255)
                bold = False
            d['cost_label'].color = color
            d['cost_label'].bold = bold

        # Process highlights for nodes.
        for u, d in self._layout.nodes(data=True):
            if highlight:
                color = (255, 0, 0, 255)
                bold = True
            else:
                color = (0, 0, 0, 255)
                bold = False
            d['label'].color = color
            d['label'].bold = bold

        # Update the pausedness.
        paused = state.is_terminal or state.is_paused
        self.update_scene_paused(paused)

        # Update the buttons.
        self.update_scene_buttons(state)

    def update_scene_buttons(self, state):
        # # feasible actions.
        # actions = self._policy_model.get_all_actions(state)
        # # possible action types.
        # all_action_types = self._policy_model.get_action_space()
        self._submit_button.set_state(state.submit_button)
        self._erase_button.set_state(state.clear_button)
        self._check_button.set_state(state.yes_button)
        self._cross_button.set_state(state.no_button)

    def update_scene_paused(self, paused):
        self._paused = paused
        self._paused_rect.visible = paused
