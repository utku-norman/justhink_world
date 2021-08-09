import importlib_resources

from .graphics import init_graphics, check_node_hit, create_edge_sprite
from ..tools.networks import in_edges, compute_selected_cost


from ..domain.state import EnvironmentState, HumanAgent, RobotAgent
from ..domain.action import SubmitAction, AgreeAction, DisagreeAction, \
    ClearAction, SuggestPickAction

from .widgets import ButtonWidget


class WorldScene(object):
    def __init__(self, state, width=1920, height=1080):

        assert isinstance(state, EnvironmentState)

        self.role = HumanAgent

        # self._layout = state.layout
        self._state = state

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

        self.temp_from = None
        self.temp_to = None
        self.temp_suggested_sprite = None

        # Display the current state.
        if state is not None:
            self.update(state)

    # Windowing methods.
    def on_draw(self):
        self._batch.draw()
        if self.temp_suggested_sprite is not None:
            self.temp_suggested_sprite.draw()

    def check_buttons(self, x, y):
        action = None

        if self._submit_button.state == ButtonWidget.ENABLED \
                and self._submit_button.check_hit(x, y):
            action = SubmitAction(agent=self.role)

        elif self._check_button.state == ButtonWidget.ENABLED \
                and self._check_button.check_hit(x, y):
            action = AgreeAction(agent=self.role)

        elif self._cross_button.state == ButtonWidget.ENABLED \
                and self._cross_button.check_hit(x, y):
            action = DisagreeAction(agent=self.role)

        elif self._erase_button.state == ButtonWidget.ENABLED \
                and self._erase_button.check_hit(x, y):
            action = ClearAction(agent=self.role)

        return action

    def on_mouse_press(self, x, y, button, modifiers, win):
        if not self._is_paused and self.role in self._state.active_agents:
            action = self.check_buttons(x, y)
            self.process_mouse_press(x, y)
            # win.world.act(action)
            print('Pressed', action)

        # # if not self._is_paused:
        # # , submit_action_type=SubmitAction)
        # action = update_scene_press(self, x, y)
        # # if isinstance(action, SubmitAction):
        # #     self._attempt += 1
        # # # win.execute_action_in_app(action)

    def on_mouse_drag(self, x, y, dx, dy, buttons, modifiers, win):
        if not self._is_paused and self.role in self._state.active_agents:
            self.process_mouse_press(x, y)
        # win.execute_action_in_app(action)
        # win.world.act(action)

    def on_mouse_release(self, x, y, button, modifiers, win):
        if not self._is_paused and self.role in self._state.active_agents:
            action = self.process_mouse_release(x, y)  # , win)
            print('Released', action)
            # win.world.act(action)
        # win.execute_action_in_app(action)

    def process_mouse_press(self, x, y, temp_suggested_image=None):
        # if not self._terminal:
        layout = self._state.layout

        # Check whether the agent is drawing from a node.
        if self.temp_from is None:
            node = check_node_hit(layout, x, y)
            print('###', node)
            if node is not None:
                node_data = layout.nodes[node]
                self.temp_from = (node_data['x'], node_data['y'], node)
                node_data['added_sprite'].visible = True

        # Check pressing a node.
        else:
            node = check_node_hit(layout, x, y)
            selected = self.get_selected_nodes()

            if node is not None:
                # if hover a new node that is not already selected
                if node != self.temp_from[2] and node not in selected:
                    self.temp_to = node
                    node_data = layout.nodes[node]
                    node_data['added_sprite'].visible = True

            # no longer hover a node
            else:
                # there is an old temp to and if not already selected
                if self.temp_to is not None and self.temp_to not in selected:
                    node_data = layout.nodes[self.temp_to]
                    node_data['added_sprite'].visible = False
                    self.temp_to = None

        if temp_suggested_image is None:
            temp_suggested_image = self.edge_suggested_image

        if self.temp_from is not None:
            self.temp_suggested_sprite = create_edge_sprite(
                temp_suggested_image,
                self.temp_from[0], self.temp_from[1],
                x, y)

        # if self._erase_button.state == ButtonWidget.ENABLED \
        #         and self._erase_button.check_hit(x, y):
        #     self._erase_button.set_state('selected')
        # elif self._erase_button.state == 'selected' \
        #         and not self._erase_button.check_hit(x, y):
        #     pass
        #     # update_scene_buttons(scene)
        #     # self.update()

    def process_mouse_release(self, x, y):  # , win):
        action = None

        layout = self._state.layout
        # # if not self._terminal and not self._is_paused:

        # # Check if an edge is erased.
        # edge = check_edge_hit(layout, x, y)
        # if edge is not None:
        #     if edge not in self._edges:
        #         e = layout.edges[edge]
        #         if e['selected_sprite'].visible:
        #             # action = PickAction(edge, agent=HumanAgent)
        #             if action_type == 'pick':
        #                 action = PickAction(edge, agent=HumanAgent)
        #             elif action_type == 'suggest-pick':
        #                 action = SuggestPickAction(edge, agent=HumanAgent)
        #             else:
        #                 print('Unknown action type')
        #             # print('Action:', action)
        #             win.execute_action_in_app(action)
        #     elif edge in self._edges:
        #         action = UnpickAction(edge, agent=HumanAgent)
        #         # , agent=HumanAgent)
        #         win.execute_action_in_app(action)

        # Check if an edge is drawn.
        if self.temp_from is not None:
            # Drawing action.
            node = check_node_hit(layout, x, y)
            if node is not None:
                from_node = self.temp_from[2]
                edge = from_node, node
                is_added = in_edges(
                    edge[0], edge[1], self._state.network.edges)
                has_edge = layout.has_edge(*edge)

                if has_edge and (from_node != node) and not is_added:
                    action = SuggestPickAction(edge, agent=self.role)
        else:  # Edge not being drawn.
            if self._erase_button.state == 'selected' \
                    and self._erase_button.check_hit(x, y):
                action = ClearAction(agent=self.role)
                # self._erase_button.set_state(ButtonWidget.DISABLED)

        # Clear selection.
        selected = self.get_selected_nodes()
        if self.temp_from is not None and self.temp_from[2] not in selected:
            node_data = layout.nodes[self.temp_from[2]]
            node_data['added_sprite'].visible = False

        if self.temp_to is not None and self.temp_to not in selected:
            node_data = layout.nodes[self.temp_to]
            node_data['added_sprite'].visible = False
            self.temp_to = None

        self.temp_from = None
        self.temp_suggested_sprite = None

        return action

    # Retriee.
    def get_selected_nodes(self):
        return [u for e in self._state.network.edges for u in e]

    # Interaction methods.
    def toggle_role(self):
        if self.role == RobotAgent:
            self.role = HumanAgent
        elif self.role == HumanAgent:
            self.role = RobotAgent
        else:
            raise NotImplementedError

        # Update the role label.
        self.update()
        # self.update_role_label()
        # self.update_paused()

    # Maintenance methods.

    def update(self, state=None, highlight=False):
        # # Update the available actions.
        # self._policy_model.update_available_actions(state)
        if state is None:
            state = self._state
        # Update the retained state.
        else:
            self._state = state

        layout = self._state.layout

        # Update the selected edges.
        added_nodes = set()
        for u, v, d in layout.edges(data=True):
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
        for u, d in layout.nodes(data=True):
            d['added_sprite'].visible = u in added_nodes
            # d['sprite'].visible = True # not u in added_nodes

        # Process highlights for edges.
        for u, v, d in layout.edges(data=True):
            if highlight:
                color = (255, 0, 0, 255)
                bold = True
            else:
                color = (0, 0, 0, 255)
                bold = False
            d['cost_label'].color = color
            d['cost_label'].bold = bold

        # Process highlights for nodes.
        for u, d in layout.nodes(data=True):
            if highlight:
                color = (255, 0, 0, 255)
                bold = True
            else:
                color = (0, 0, 0, 255)
                bold = False
            d['label'].color = color
            d['label'].bold = bold

        # Update the pausedness.
        self.update_paused(state)

        # Update the buttons.
        self.update_buttons(state)

        # Update the cost label.
        self.update_cost_label(state)

        # Update the role label.
        self.update_role_label()

    def update_cost_label(self, state, highlight=False):
        graph = state.network.graph
        edges = state.network.edges

        if edges is not None:
            cost = compute_selected_cost(graph, edges)
        else:
            cost = 0
        self._cost_label.text = 'Spent: {:2d} francs'.format(cost)

        if highlight:
            self._cost_label.color = (255, 0, 0, 255)
            self._cost_label.bold = True
        else:
            self._cost_label.color = (0, 0, 0, 255)
            self._cost_label.bold = False

    def update_role_label(self):
        self._role_label.text = 'Role: {}'.format(self.role.name)

    def update_buttons(self, state=None):
        # # feasible actions.
        # actions = self._policy_model.get_all_actions(state)
        # # possible action types.
        # all_action_types = self._policy_model.get_action_space()
        if state is None:
            state = self._state

        self._submit_button.set_state(state.submit_button)
        self._erase_button.set_state(state.clear_button)
        self._check_button.set_state(state.yes_button)
        self._cross_button.set_state(state.no_button)

    def update_paused(self, state=None):
        if state is None:
            state = self._state

        is_paused = state.is_terminal or state.is_paused \
            or self.role not in state.active_agents

        self.set_paused(is_paused)

    def set_paused(self, is_paused):
        self._is_paused = is_paused
        self._paused_rect.visible = is_paused
