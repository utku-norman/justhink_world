import copy

import pyglet
from pyglet.window import key

from justhink_world.tools.graphics import Graphics, BLACKA

from justhink_world.agent.visual import MentalWindow
from justhink_world.env.visual import EnvironmentScene, create_edge_sprite
from justhink_world.tools.graphics import check_node_hit

from justhink_world.domain.state import Human, Robot, Button
from justhink_world.domain.action import SetPauseAction,  \
    PickAction, SuggestPickAction, ClearAction, AgreeAction, DisagreeAction, \
    AttemptSubmitAction, ContinueAction, SubmitAction

from justhink_world.world import IndividualWorld, CollaborativeWorld


def show_all(world):
    world_window = WorldWindow(world)
    mental_window = MentalWindow(world)

    @world_window.event
    def on_update():
        # print('Key pressed so updating')
        world_window.on_update()

        mental_window.graphics.next_label.text = \
            world_window.graphics.next_label.text

        mental_window.graphics.prev_label.text = \
            world_window.graphics.prev_label.text

        index = world.state_no-2
        if index < 0 or index > len(world.agent.history) - 1:
            s = 'None'
        else:
            s = str(world.agent.history[index][1])
        # s += 'state #{}'.format(world.state_no)
        mental_window.graphics.observes_label.text = s

        # Event handled.
        return True

    world_window.push_handlers(on_update)

    @mental_window.event
    @world_window.event
    def on_key_press(symbol, modifiers):
        # print('Key pressed in mental')
        if symbol == key.ESCAPE:
            mental_window.close()
            world_window.close()
            return True

    pyglet.app.run()


def show_world(world):
    WorldWindow(world)

    # Enter the main event loop.
    pyglet.app.run()


class WorldWindow(pyglet.window.Window):
    def __init__(self, world, width=1920, height=1080, screen_no=0):
        assert isinstance(world, IndividualWorld) or \
            isinstance(world, CollaborativeWorld)

        if isinstance(world, IndividualWorld):
            scene_type = IndividualWorldScene
        elif isinstance(world, CollaborativeWorld):
            scene_type = CollaborativeWorldScene
        self.scene = scene_type(world=world, width=width, height=height)

        self.world = world

        # window_style = pyglet.window.Window.WINDOW_STYLE_DEFAULT
        style = pyglet.window.Window.WINDOW_STYLE_BORDERLESS

        super().__init__(width, height, style=style, fullscreen=False)
        self._init_graphics(width, height)

        self.register_event_type('on_update')
        # self.set_handlers(self.scene.on_update)

        # Move the window to a screen in possibly a dual-monitor setup.
        display = pyglet.canvas.get_display()
        screens = display.get_screens()
        # 0 for the laptop screen, e.g. 1 for the external screen
        active_screen = screens[screen_no]
        self.set_location(active_screen.x, active_screen.y)

        self.dispatch_event('on_update')

    def __str__(self):
        return self.__repr__()

    def __repr__(self):
        return 'WorldWindow({},w={},h={})'.format(
            self.world.env.state, self.width, self.height)

    @property
    def world(self):
        return self._world

    @world.setter
    def world(self, value):
        self._world = value

    def on_draw(self):
        self.scene.on_draw()
        self.graphics.batch.draw()

    def act_via_window(self, action):
        self.world.act(action)
        self.scene.state = self.world.cur_state
        self.dispatch_event('on_update')

    def on_mouse_press(self, x, y, button, modifiers):
        self.scene.on_mouse_press(x, y, button, modifiers, win=self)

    def on_mouse_drag(self, x, y, dx, dy, buttons, modifiers):
        self.scene.on_mouse_drag(x, y, dx, dy, buttons, modifiers, win=self)

    def on_mouse_release(self, x, y, button, modifiers):
        self.scene.on_mouse_release(x, y, button, modifiers, win=self)

    def on_key_press(self, symbol, modifiers):
        if symbol == key.ESCAPE:
            self.close()
        elif symbol == key.LEFT:
            self.world.state_no = self.world.state_no - 1
            self.scene.state = self.world.cur_state
        elif symbol == key.RIGHT:
            self.world.state_no = self.world.state_no + 1
            self.scene.state = self.world.cur_state
        elif symbol == key.HOME:
            self.world.state_no = 1
            self.scene.state = self.world.cur_state
        elif symbol == key.END:
            self.world.state_no = self.world.num_states
            self.scene.state = self.world.cur_state
        elif symbol == key.TAB:
            self.scene.toggle_role()
            self.scene.state = self.world.cur_state
        elif symbol == key.P:
            is_paused = self.world.cur_state.is_paused
            self.act_via_window(SetPauseAction(not is_paused))

        self.dispatch_event('on_update')

    def on_update(self):
        # Update the scene.
        self.scene.on_update()

        # Update the window labels.
        self._update_hist_label()
        self._update_role_label()
        self._update_next_label()
        self._update_prev_label()

    def _update_role_label(self):
        self.graphics.role_label.text = 'Role: {}'.format(
            self.scene._role.name)

    def _update_next_label(self):
        self.graphics.next_label.text = 'Next: {}'.format(
            self._make_action_text(offset=1))

    def _update_prev_label(self):
        self.graphics.prev_label.text = 'Previous: {}'.format(
            self._make_action_text(offset=-1))

    def _update_hist_label(self):
        self.graphics.hist_label.text = 'State: {}/{}'.format(
            self.world.state_no, self.world.num_states)

    def _make_action_text(self, offset=1):
        index = self.world.state_index + offset
        try:
            action = self.world.history[index]
        except IndexError:
            action = None
        if index < 0:
            action = None

        if isinstance(self.world, CollaborativeWorld):
            if action is not None:
                action = copy.deepcopy(action)
                if hasattr(action, 'edge') and action.edge is not None:
                    edge_name = self.world.env.state.network.get_edge_name(
                        action.edge)
                    u, _, v = edge_name.split()
                    action = action.__class__(edge=(u, v), agent=action.agent)
        return str(action)

    def _init_graphics(self, width, height):
        graphics = Graphics(width, height)
        group = pyglet.graphics.OrderedGroup(5)

        # History label.
        graphics.hist_label = pyglet.text.Label(
            '', x=20, y=height-120, anchor_y='center', color=BLACKA,
            font_name='Sans', font_size=32, batch=graphics.batch, group=group)

        # Role label.
        graphics.role_label = pyglet.text.Label(
            '', x=20, y=height-60, anchor_y='center', color=BLACKA,
            font_name='Sans', font_size=32, batch=graphics.batch, group=group)

        # Next action if any label.
        graphics.next_label = pyglet.text.Label(
            '', x=width//2, y=height-20, anchor_y='center', color=BLACKA,
            font_name='Sans', font_size=24, batch=graphics.batch, group=group)

        # Previous action if any label.
        graphics.prev_label = pyglet.text.Label(
            '', x=20, y=height-20, anchor_y='center', color=BLACKA,
            font_name='Sans', font_size=24, batch=graphics.batch, group=group)

        self.graphics = graphics


class WorldScene(EnvironmentScene):
    def __init__(self, world, name=None, width=1920, height=1080):
        if name is None:
            name = world.name
        super().__init__(
            world.env.state, name=name, height=height, width=width)

        self._role = Human
        self._policy_model = world.agent.policy_model

        self._pick_action_type = PickAction
        self._submit_action_type = SubmitAction

        # self.temp_from = None
        # self.temp_to = None
        self.graphics.temp_suggested_sprite = None

        # self.temp_from = None
        # self.temp_to = None

        # self.graphics.has_status_label = False

        self._update_feasible_actions()

        self._temp_from = None
        self._temp_to = None

    @property
    def temp_from(self):
        return self._temp_from

    @property
    def temp_to(self):
        return self._temp_to

    @temp_from.setter
    def temp_from(self, value):
        print('Setting temp to', value)
        self._temp_from = value

    @temp_to.setter
    def temp_to(self, value):
        print('Setting temp from', value)
        self._temp_to = value

    # Custom public methods.

    def on_update(self):
        super().on_update()
        self._update_feasible_actions()
        self._update_buttons()
        self._update_status_label()

    def toggle_role(self):
        if self._role == Robot:
            self._role = Human
        elif self._role == Human:
            self._role = Robot
        else:
            raise NotImplementedError

        self._reset_drawing()

    # GUI methods.

    def on_draw(self):
        self.graphics.batch.draw()
        if self.graphics.temp_suggested_sprite is not None:
            self.graphics.temp_suggested_sprite.draw()

        # self._status_label.draw()
        # self._status_rect.draw()

    def on_mouse_press(self, x, y, button, modifiers, win):
        if self.state.is_paused:
            return

        action = None

        if self.state.is_submitting:
            if self._check_confirm_hit(x, y):
                action = SubmitAction(agent=self._role)
            elif self._check_continue_hit(x, y):
                action = ContinueAction(agent=self._role)
        else:
            # If can pick or suggest-pick an edge
            action = self._check_buttons(x, y)

            if self._role in self.state.agents and \
                    self._pick_action_type in self._action_types:
                self._process_drawing(x, y)

        # if action is not None:
        if action in self._actions:
            win.act_via_window(action)
            # print('Pressed', action)

    def on_mouse_drag(self, x, y, dx, dy, buttons, modifiers, win):
        if self.state.is_paused:
            return

        if self.temp_from is not None:  # i.e. drawing
            self._process_drawing(x, y)

    def on_mouse_release(self, x, y, button, modifiers, win):
        if self.state.is_paused:
            return

        if self._role in self.state.agents:
            action = self._process_drawing_done(x, y)

            if action is not None:
                win.act_via_window(action)

    def on_key_press(self, symbol, modifiers, win):
        pass

    def _process_drawing(self, x, y):
        # Check if a node is pressed.
        node = check_node_hit(self.graphics.layout, x, y)

        # Check if the agent started drawing from a node.
        if self.temp_from is None:
            if node is not None:
                d = self.graphics.layout.nodes[node]
                self.temp_from = (d['x'], d['y'], node)
                d['added_sprite'].visible = True

        # If the agent is already drawing from a node.
        else:
            selected = self.state.network.get_selected_nodes()

            # If mouse is on a new node that is not already selected
            if node is not None and node not in selected and \
                    node != self.temp_from[2]:
                self.temp_to = node
                d = self.graphics.layout.nodes[node]
                d['added_sprite'].visible = True

            # If mouse is not on a node, reset the previous drawing to node.
            elif self.temp_to is not None \
                    and self.temp_to not in selected:
                d = self.graphics.layout.nodes[self.temp_to]
                d['added_sprite'].visible = False
                self.temp_to = None

            # Update the temporary drawing edge to the new mouse position.
            # if self.temp_from is not None:
            self.graphics.temp_suggested_sprite = create_edge_sprite(
                self.temp_edge_image, self.temp_from[0],
                self.temp_from[1], x, y)

    # Private methods.

    def _check_buttons(self, x, y):
        action = None

        if self.graphics.submit_button.state == Button.ENABLED \
                and self.graphics.submit_button.check_hit(x, y):
            action = self._submit_action_type(agent=self._role)

        elif self.graphics.yes_button.state == Button.ENABLED \
                and self.graphics.yes_button.check_hit(x, y):
            action = AgreeAction(agent=self._role)

        elif self.graphics.no_button.state == Button.ENABLED \
                and self.graphics.no_button.check_hit(x, y):
            action = DisagreeAction(agent=self._role)

        elif self.graphics.clear_button.state == Button.ENABLED \
                and self.graphics.clear_button.check_hit(x, y):
            action = ClearAction(agent=self._role)

        return action

    def _check_confirm_hit(self, x, y):
        return (-320 < x - self.graphics.width//2 < -40 and
                -100 < y - self.graphics.height//2 < 60)

    def _check_continue_hit(self, x, y):
        return (40 < x - self.graphics.width//2 < 320 and
                -100 < y - self.graphics.height//2 < 60)

    def _update_feasible_actions(self):
        self._actions = self._policy_model.get_all_actions(self._state)
        self._action_types = {type(action) for action in self._actions}

    def _update_paused(self):
        """Override EnvironmentScene's _update_paused() with 'role'"""
        self.graphics.observe_rect.visible = \
            self._role not in self.state.agents
        self._set_paused(self.state.is_terminal or self.state.is_paused)

    def _update_buttons(self):
        if self._submit_action_type(self._role) in self._actions:
            button_state = Button.ENABLED
        elif self.state.is_terminal:
            button_state = Button.SELECTED
        else:
            button_state = Button.DISABLED
        self.graphics.submit_button.set_state(button_state)

        if ClearAction(self._role) in self._actions:
            button_state = Button.ENABLED
        else:
            button_state = Button.DISABLED
        self.graphics.clear_button.set_state(button_state)

    def _update_status_label(self):
        pass

    def _process_drawing_done(self, x, y):
        action = None

        # self.graphics.layout = self.graphics.self.graphics.layout

        # Check if an edge is drawn.
        if self.temp_from is not None:
            # Drawing action.
            node = check_node_hit(self.graphics.layout, x, y)
            if node is not None:
                from_node = self.temp_from[2]
                edge = from_node, node
                is_added = self.state.network.subgraph.has_edge(*edge)
                has_edge = self.graphics.layout.has_edge(*edge)

                if has_edge and (from_node != node) and not is_added:
                    action = self._pick_action_type(edge, agent=self._role)

        # Clear selection.
        selected = self.state.network.get_selected_nodes()
        if self.temp_from is not None \
                and self.temp_from[2] not in selected:
            node_data = self.graphics.layout.nodes[self.temp_from[2]]
            node_data['added_sprite'].visible = False

        if self.temp_to is not None \
                and self.temp_to not in selected:
            node_data = self.graphics.layout.nodes[self.temp_to]
            node_data['added_sprite'].visible = False
            self.temp_to = None

        self._reset_drawing()

        return action

    def _reset_drawing(self):
        self.temp_from = None
        self.temp_to = None
        self.graphics.temp_suggested_sprite = None


class IntroWorldScene(WorldScene):

    def __init__(self, **kwargs):

        super().__init__(**kwargs)

        # Hide node names if any.
        for u, d in self.graphics.layout.nodes(data=True):
            d['label'].text = ''

        # Hide edge costs if any.
        for u, v, d in self.graphics.layout.edges(data=True):
            d['cost_label'].text = ''

    def _update_cost_label(self, is_highlighted=False):
        # Hide cost label text.
        self.graphics.cost_label.text = ''
        self.graphics.cost_label.visible = False

    def _check_buttons(self, x, y):
        pass


class DemoWorldScene(WorldScene):

    def __init__(self, **kwargs):

        super().__init__(**kwargs)

        self.temp_edge_image = self.graphics.edge_added_image
        self._pick_action_type = PickAction
        self._submit_action_type = SubmitAction

        # Hide node names if any.
        for u, d in self.graphics.layout.nodes(data=True):
            d['label'].text = ''

        # # Hide cost label text.
        # self.graphics.cost_label.visible = False


class IndividualWorldScene(WorldScene):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.temp_edge_image = self.graphics.edge_added_image
        self._pick_action_type = PickAction
        self._submit_action_type = AttemptSubmitAction

        # Hide node names if any.
        for u, d in self.graphics.layout.nodes(data=True):
            d['label'].text = ''

    @property
    def graphics(self):
        return self._graphics

    @graphics.setter
    def graphics(self, value):
        # print('Setting temp to', value)
        self._graphics = value


class CollaborativeWorldScene(WorldScene):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.temp_edge_image = self.graphics.edge_suggested_image
        self._pick_action_type = SuggestPickAction
        self._submit_action_type = AttemptSubmitAction

    # Overridden private methods.

    def _update_buttons(self):
        super()._update_buttons()

        if AgreeAction(self._role) in self._actions:
            self.graphics.yes_button.set_state(Button.ENABLED)
        else:
            self.graphics.yes_button.set_state(Button.DISABLED)

        if DisagreeAction(self._role) in self._actions:
            self.graphics.no_button.set_state(Button.ENABLED)
        else:
            self.graphics.no_button.set_state(Button.DISABLED)

    def _update_status_label(self):
        s = ''
        if self.state.network.subgraph.number_of_edges() == 0 \
                and self.state.network.suggested_edge is None:
            if self.state.attempt_no == 1:
                s += "Let's go!"
            else:
                s += 'Try again!'
        elif self.state.is_terminal:
            if self.state.network.is_mst():
                s += 'Congratulations!'
            else:
                s += 'Game over!'

        if not self.state.is_terminal:
            if self._role in self.state.agents:
                s += ' (your turn)'
            else:
                s += " (your partner's turn)"
            # TODO: handle maybe simultaneous case

        is_visible = len(s) != 0

        self.graphics.status_label.text = s
        self.graphics.status_label.visible = is_visible
        self.graphics.status_rect.visible = is_visible
