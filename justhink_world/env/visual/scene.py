import importlib_resources

from .graphics import init_graphics

from justhink_world.tools.networks import compute_subgraph_cost
from justhink_world.domain.state import EnvironmentState


class EnvironmentScene(object):
    def __init__(self, state, width=1920, height=1080):

        assert isinstance(state, EnvironmentState)

        self._state = state

        # Create a container for the image resources.
        image_container = importlib_resources.files(
            'justhink_world.resources.images')

        # A network to contain the graphics as well.

        # Create the graphics.
        self._graphics = init_graphics(state.network.graph,
                                       width,
                                       height,
                                       image_container)

        # for key, obj in graphics.items():
        #     setattr(self._graphics, key, obj)
        # self._batch = batch

    # Windowing methods.

    def on_draw(self):
        self._graphics.batch.draw()

    def on_mouse_press(self, x, y, button, modifiers, win):
        pass

    def on_mouse_drag(self, x, y, dx, dy, buttons, modifiers, win):
        pass

    def on_mouse_release(self, x, y, button, modifiers, win):
        pass

    # Maintenance methods.

    def update(self, state, highlight=False):
        # # Update the available actions.
        # self._policy_model.update_available_actions(state)

        self._state = state

        # Update the selected edges.
        added_nodes = set()
        for u, v, d in self._graphics.layout.edges(data=True):
            is_added = state.network.subgraph.has_edge(u, v)
            e = state.network.suggested_edge
            is_suggested = (e == (u, v)) or (e == (v, u))
            d['added_sprite'].visible = is_added
            d['selectable_sprite'].visible = not is_added
            d['selected_sprite'].visible = False
            d['suggested_sprite'].visible = is_suggested

            if is_added:
                added_nodes.update((u, v))

        # Update the selected nodes.
        for u, d in self._graphics.layout.nodes(data=True):
            d['added_sprite'].visible = u in added_nodes
            # d['sprite'].visible = True # not u in added_nodes

        # Process highlights for edges.
        for u, v, d in self._graphics.layout.edges(data=True):
            if highlight:
                color = (255, 0, 0, 255)
                bold = True
            else:
                color = (0, 0, 0, 255)
                bold = False
            d['cost_label'].color = color
            d['cost_label'].bold = bold

        # Process highlights for nodes.
        for u, d in self._graphics.layout.nodes(data=True):
            if highlight:
                color = (255, 0, 0, 255)
                bold = True
            else:
                color = (0, 0, 0, 255)
                bold = False
            d['label'].color = color
            d['label'].bold = bold

        # Update the pausedness.
        self._update_paused()

        # Update the cost label.
        self._update_cost_label()

        # Update the attempt label.
        self._update_attempt_label()

        # Show or hide the confirm box.
        self._update_submit_box()

    def _update_cost_label(self, highlight=False):
        state = self._state
        graph = state.network.graph
        subgraph = state.network.subgraph

        if subgraph is not None:
            cost = compute_subgraph_cost(graph, subgraph)
        else:
            cost = 0
        self._graphics.cost_label.text = 'Spent: {:2d} francs'.format(cost)

        if highlight:
            self._graphics.cost_label.color = (255, 0, 0, 255)
            self._graphics.cost_label.bold = True
        else:
            self._graphics.cost_label.color = (0, 0, 0, 255)
            self._graphics.cost_label.bold = False

    def _update_attempt_label(self):
        state = self._state
        if state.max_attempts is not None:
            s = 'Attempt: {}/{}'.format(state.attempt_no, state.max_attempts)
            self._graphics.attempt_label.text = s

    def _update_paused(self):
        self.set_paused(self._state.is_terminal)

    def _update_submit_box(self):
        if self._state.is_submitting:
            self._graphics.confirm_rect.visible = True
            self._graphics.confirm_text_label.text = 'Do you want to submit?'
            self._graphics.yes_label.text = 'Ok'
            self._graphics.no_label.text = 'Cancel'
        else:
            self._graphics.confirm_rect.visible = False
            self._graphics.confirm_text_label.text = ''
            self._graphics.yes_label.text = ''
            self._graphics.no_label.text = ''

    def set_paused(self, is_paused):
        self._is_paused = is_paused
        self._graphics.paused_rect.visible = is_paused
