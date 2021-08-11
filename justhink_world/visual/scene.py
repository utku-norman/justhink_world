from .graphics import check_node_hit
from ..tools.networks import in_edges

from justhink_world.env.visual import EnvironmentScene
from justhink_world.env.visual.graphics import create_edge_sprite

from justhink_world.domain.state import HumanAgent, RobotAgent, Button
from justhink_world.domain.action import \
    SubmitAction, AgreeAction, DisagreeAction, \
    ClearAction, PickAction, SuggestPickAction, \
    AttemptSubmitAction, ContinueAction


class WorldScene(EnvironmentScene):
    def __init__(self, world, width=1920, height=1080):

        self.role = HumanAgent
        self._state = world.env.state
        self._policy_model = world.agent.policy_model

        super().__init__(self._state,
                         height=height,
                         width=width)

        self._graphics.temp_from = None
        self._graphics.temp_to = None
        self._graphics.temp_suggested_sprite = None

        # Feasible actions.
        self._update_feasible_actions()

    # Windowing methods.

    def on_draw(self):
        self._graphics.batch.draw()
        if self._graphics.temp_suggested_sprite is not None:
            self._graphics.temp_suggested_sprite.draw()

        # self._status_label.draw()
        # self._status_rect.draw()

    def on_mouse_press(self, x, y, button, modifiers, win):
        # If can pick or suggest-pick an edge
        action = self._check_buttons(x, y)

        if self._state.is_submitting:
            if self._check_confirm_hit(x, y):
                action = SubmitAction(agent=self.role)
            elif self._check_continue_hit(x, y):
                action = ContinueAction(agent=self.role)
        # elif not self._is_paused and self.role in self._state.agents:

        if self.role in self._state.agents and \
                self._pick_action_type in self._action_types:
            self._process_drawing(x, y)

        # if action is not None:
        if action in self._actions:
            win.act_via_window(action)
            # print('Pressed', action)

    def on_mouse_drag(self, x, y, dx, dy, buttons, modifiers, win):
        if self._graphics.temp_from is not None:  # i.e. drawing
            self._process_drawing(x, y)

    def on_mouse_release(self, x, y, button, modifiers, win):
        if not self._is_paused and self.role in self._state.agents:
            action = self._process_drawing_done(x, y)  # , win)

            if action is not None:
                win.act_via_window(action)
                # print('Released', action)

    def on_key_press(self, symbol, modifiers, win):
        pass

    def _process_drawing(self, x, y):
        layout = self._graphics.layout

        # Check whether the agent is drawing from a node.
        if self._graphics.temp_from is None:
            node = check_node_hit(layout, x, y)
            if node is not None:
                node_data = layout.nodes[node]
                self._graphics.temp_from = (
                    node_data['x'], node_data['y'], node)
                node_data['added_sprite'].visible = True

        # Check pressing a node.
        else:
            node = check_node_hit(layout, x, y)
            selected = self._state.network.get_selected_nodes()

            if node is not None:
                # if hover a new node that is not already selected
                if node != self._graphics.temp_from[2] \
                        and node not in selected:
                    self._graphics.temp_to = node
                    node_data = layout.nodes[node]
                    node_data['added_sprite'].visible = True

            # no longer hover a node
            else:
                # there is an old temp to and if not already selected
                if self._graphics.temp_to is not None \
                        and self._graphics.temp_to not in selected:
                    node_data = layout.nodes[self._graphics.temp_to]
                    node_data['added_sprite'].visible = False
                    self._graphics.temp_to = None

        if self._graphics.temp_from is not None:
            self._graphics.temp_suggested_sprite = create_edge_sprite(
                self._graphics.temp_edge_image,
                self._graphics.temp_from[0],
                self._graphics.temp_from[1],
                x, y)

    def _process_drawing_done(self, x, y):
        action = None

        layout = self._graphics.layout

        # Check if an edge is drawn.
        if self._graphics.temp_from is not None:
            # Drawing action.
            node = check_node_hit(layout, x, y)
            if node is not None:
                from_node = self._graphics.temp_from[2]
                edge = from_node, node
                is_added = in_edges(
                    edge[0], edge[1], self._state.network.edges)
                has_edge = layout.has_edge(*edge)

                if has_edge and (from_node != node) and not is_added:
                    action = self._pick_action_type(edge, agent=self.role)
        # else:  # Edge not being drawn.
        #     if self._clear_button.state == 'selected' \
        #             and self._clear_button.check_hit(x, y):
        #         action = ClearAction(agent=self.role)
        #         # self._clear_button.set_state(Button.DISABLED)

        # Clear selection.
        selected = self._state.network.get_selected_nodes()
        if self._graphics.temp_from is not None \
                and self._graphics.temp_from[2] not in selected:
            node_data = layout.nodes[self._graphics.temp_from[2]]
            node_data['added_sprite'].visible = False

        if self._graphics.temp_to is not None \
                and self._graphics.temp_to not in selected:
            node_data = layout.nodes[self._graphics.temp_to]
            node_data['added_sprite'].visible = False
            self._graphics.temp_to = None

        self.reset_drawing()

        return action

    def reset_drawing(self):
        self._graphics.temp_from = None
        self._graphics.temp_to = None
        self._graphics.temp_suggested_sprite = None

    # Interaction methods.

    def toggle_role(self):
        if self.role == RobotAgent:
            self.role = HumanAgent
        elif self.role == HumanAgent:
            self.role = RobotAgent
        else:
            raise NotImplementedError

        self.reset_drawing()

    def _check_buttons(self, x, y):
        action = None

        if self._graphics.submit_button.state == Button.ENABLED \
                and self._graphics.submit_button.check_hit(x, y):
            action = self._submit_action_type(agent=self.role)

        elif self._graphics.yes_button.state == Button.ENABLED \
                and self._graphics.yes_button.check_hit(x, y):
            action = AgreeAction(agent=self.role)

        elif self._graphics.no_button.state == Button.ENABLED \
                and self._graphics.no_button.check_hit(x, y):
            action = DisagreeAction(agent=self.role)

        elif self._graphics.clear_button.state == Button.ENABLED \
                and self._graphics.clear_button.check_hit(x, y):
            action = ClearAction(agent=self.role)

        return action

    def _check_confirm_hit(self, x, y):
        return (-320 < x - self._graphics.width//2 < -40 and
                -100 < y - self._graphics.height//2 < 60)

    def _check_continue_hit(self, x, y):
        return (40 < x - self._graphics.width//2 < 320 and
                -100 < y - self._graphics.height//2 < 60)

    # Maintenance methods.

    def update(self, state=None):
        if state is None:
            state = self._state
        else:
            self._state = state

        # Update feasible actions.
        self._update_feasible_actions()

        # print('At state {} with actions {}'.format(
        # self._state, self._actions))

        # Update the buttons.
        self._update_buttons()

        if self._graphics.has_status_label:
            self._update_status_label()

        super().update(state)

    def _update_feasible_actions(self):
        self._actions = self._policy_model.get_all_actions(self._state)
        self._action_types = {type(action) for action in self._actions}

    def _update_paused(self):
        """Override EnvironmentScene's _update_paused() with 'role'"""
        state = self._state

        self._graphics.view_only_rect.visible = self.role not in state.agents

        is_paused = state.is_terminal or state.is_paused
        self.set_paused(is_paused)

    def _update_buttons(self):
        state = self._state
        actions = self._actions

        # print("Updating buttons for {} with {}".format(state, actions))

        # Action space.

        if self._submit_action_type(self.role) in actions:
            self._graphics.submit_button.set_state(Button.ENABLED)
        elif state.is_terminal:
            self._graphics.submit_button.set_state(Button.SELECTED)
        else:
            self._graphics.submit_button.set_state(Button.DISABLED)

        if ClearAction(self.role) in actions:
            self._graphics.clear_button.set_state(Button.ENABLED)
        else:
            self._graphics.clear_button.set_state(Button.DISABLED)

    def _update_status_label(self):
        pass


class IndivWorldScene(WorldScene):

    def __init__(self, **kwargs):

        super().__init__(**kwargs)

        self._graphics.temp_edge_image = self._graphics.edge_added_image
        self._pick_action_type = PickAction
        self._submit_action_type = AttemptSubmitAction
        self._graphics.has_status_label = False


class CollabWorldScene(WorldScene):

    def __init__(self, **kwargs):

        super().__init__(**kwargs)

        self._graphics.temp_edge_image = self._graphics.edge_suggested_image
        self._pick_action_type = SuggestPickAction
        self._submit_action_type = AttemptSubmitAction  # SubmitAction
        self._graphics.has_status_label = True

    def _update_buttons(self):
        actions = self._actions

        super()._update_buttons()

        if AgreeAction(self.role) in actions:
            self._graphics.yes_button.set_state(Button.ENABLED)
        else:
            self._graphics.yes_button.set_state(Button.DISABLED)

        if DisagreeAction(self.role) in actions:
            self._graphics.no_button.set_state(Button.ENABLED)
        else:
            self._graphics.no_button.set_state(Button.DISABLED)

    def _update_status_label(self):
        state = self._state

        s = ''
        if len(state.network.edges) == 0 \
                and state.network.suggested_edge is None:
            if state.attempt_no == 1:
                s += "Let's go!"
            else:
                s += 'Try again!'
        elif state.is_terminal:
            if state.network.is_mst():
                s += 'Congratulations!'
            else:
                s += 'Game over!'

        if not state.is_terminal:
            if self.role in state.agents:
                s += ' (your turn)'
            else:
                s += " (your partner's turn)"
            # TODO: handle simultaneous case

        is_visible = len(s) != 0

        self._graphics.status_label.text = s
        self._graphics.status_label.visible = is_visible
        self._graphics.status_rect.visible = is_visible
