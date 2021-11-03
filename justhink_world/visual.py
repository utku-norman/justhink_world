import copy

import pyglet
from pyglet.window import key

from justhink_world.tools.graphics import Button, Graphics, check_node_hit, \
    REDA, WHITEA

from justhink_world.agent.visual import MentalWindow
from justhink_world.env.visual import EnvironmentScene, create_edge_sprite

from justhink_world.world import IndividualWorld, CollaborativeWorld
from justhink_world.agent import Agent
from justhink_world.domain.action import SetPauseAction,  \
    PickAction, SuggestPickAction, ClearAction, AgreeAction, DisagreeAction, \
    AttemptSubmitAction, ContinueAction, SubmitAction


def show_all(world, state_no=None):
    """TODO docstring for show_all"""
    world_window = WorldWindow(world, state_no=state_no)
    mind_window = MentalWindow(world)  # , offset=(1920, 0))

    @world_window.event
    def on_update():
        world_window.on_update()

        mind_window.cur_scene.graphics.next_label.text = \
            world_window.graphics.next_label.text

        mind_window.cur_scene.graphics.prev_label.text = \
            world_window.graphics.prev_label.text

        # Offset for the observe.
        index = world.state_no - 2
        if index < 0 or index > len(world.agent.history) - 1:
            s = 'None'
        else:
            s = str(world.agent.history[index][1])

        mind_window.cur_scene.graphics.observes_label.text = s
        # mind_window.cur_scene.state = world_window.world.cur_mental_state
        # print('Showing state:', mind_window.cur_scene.state)

        mind_window.dispatch_event('on_update')

        # Event is handled: do not run another on_update.
        return True

    world_window.push_handlers(on_update)

    @mind_window.event
    @world_window.event
    def on_key_press(symbol, modifiers):
        # print('Key pressed in mental')
        if symbol == key.ESCAPE:
            mind_window.close()
            world_window.close()
            return True

    # Enter the main event loop.
    try:
        pyglet.app.run()
    except KeyboardInterrupt:
        mind_window.close()
        world_window.close()
        print('Windows are closed.')


def show_world(world, state_no=None, screen_index=0):
    """TODO docstring for show_world

    By default showing the last state on the primary window."""
    window = WorldWindow(world, state_no=state_no, screen_index=screen_index)

    # Enter the main event loop.
    try:
        pyglet.app.run()
    except KeyboardInterrupt:
        window.close()
        print('Window is closed.')


class WorldWindow(pyglet.window.Window):
    """TODO docstring for WorldWindow"""

    def __init__(
            self, world, state_no=None, caption='World', width=1920,
            height=1080, screen_index=0):
        assert isinstance(world, IndividualWorld) or \
            isinstance(world, CollaborativeWorld)

        if isinstance(world, IndividualWorld):
            scene_type = IndividualWorldScene
        elif isinstance(world, CollaborativeWorld):
            scene_type = CollaborativeWorldScene
        else:
            raise NotImplementedError

        self.world = world
        # # TODO try except
        if state_no is not None:
            self.world.state_no = state_no

        self.scene = scene_type(world=self.world, width=width, height=height)

        # style = pyglet.window.Window.WINDOW_STYLE_DEFAULT
        style = pyglet.window.Window.WINDOW_STYLE_BORDERLESS
        super().__init__(width, height, caption, style=style, fullscreen=False)

        self._init_graphics(width, height)

        self.register_event_type('on_update')
        self.dispatch_event('on_update')

        # Move the window to a screen in possibly a dual-monitor setup.
        display = pyglet.canvas.get_display()
        screens = display.get_screens()
        # 0 for the laptop screen, e.g. 1 for the external screen
        active_screen = screens[screen_index]
        self.set_location(active_screen.x, active_screen.y)

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

    # GUI methods.

    def on_draw(self):
        """TODO docstring for on_draw"""
        self.scene.on_draw()
        self.graphics.batch.draw()

    def on_mouse_press(self, x, y, button, modifiers):
        """TODO docstring for on_mouse_press"""
        self.scene.on_mouse_press(x, y, button, modifiers, win=self)

    def on_mouse_drag(self, x, y, dx, dy, buttons, modifiers):
        """TODO docstring for on_mouse_drag"""
        self.scene.on_mouse_drag(x, y, dx, dy, buttons, modifiers, win=self)

    def on_mouse_release(self, x, y, button, modifiers):
        """TODO docstring for on_mouse_release"""
        self.scene.on_mouse_release(x, y, button, modifiers, win=self)

    def on_key_press(self, symbol, modifiers):
        """TODO docstring for on_key_press"""
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
            self.execute_action(SetPauseAction(not is_paused, Agent.MANAGER))

        self.dispatch_event('on_update')

    # Custom public methods.

    def execute_action(self, action):
        """TODO docstring for execute_action"""
        self.world.act(action)
        self.scene.state = self.world.cur_state
        self.dispatch_event('on_update')

    def on_update(self):
        """TODO docstring for on_update"""
        # Update the scene.
        self.scene.on_update()

        # Update the window labels.
        self._update_state_label()
        self._update_state_no_label()
        self._update_role_label()
        self._update_next_label()
        self._update_prev_label()

    # Private methods.

    def _init_graphics(self, width, height):
        """TODO docstring for _init_graphics"""
        graphics = Graphics(width, height)
        group = pyglet.graphics.OrderedGroup(5)

        # State label.
        graphics.state_label = pyglet.text.Label(
            '', x=20, y=height-20, anchor_y='center', color=REDA,
            font_name='Sans', font_size=20, batch=graphics.batch, group=group)

        # Create a label for the state no.
        graphics.state_no_label = pyglet.text.Label(
            '', x=20, y=height-120, anchor_y='center', color=REDA,
            font_name='Sans', font_size=32, batch=graphics.batch, group=group)

        # Role label.
        graphics.role_label = pyglet.text.Label(
            '', x=20, y=height-60, anchor_y='center', color=REDA,
            font_name='Sans', font_size=32, batch=graphics.batch, group=group)

        # Next action if any label.
        graphics.next_label = pyglet.text.Label(
            '', x=width//2, y=80, anchor_y='center', color=REDA,
            font_name='Sans', font_size=20, batch=graphics.batch, group=group)

        # Previous action if any label.
        graphics.prev_label = pyglet.text.Label(
            '', x=20, y=80, anchor_y='center', color=REDA,
            font_name='Sans', font_size=20, batch=graphics.batch, group=group)

        self.graphics = graphics

    def _update_state_label(self):
        self.graphics.state_label.text = 'State: {}'.format(
            self.world.cur_state)
        self._update_label_color(self.graphics.state_label)

    def _update_state_no_label(self):
        self.graphics.state_no_label.text = 'State: {}/{}'.format(
            self.world.state_no, self.world.num_states)
        self._update_label_color(self.graphics.state_no_label)

    def _update_role_label(self):
        self.graphics.role_label.text = 'Role: {}'.format(self.scene._role)
        self._update_label_color(self.graphics.role_label)

    def _update_next_label(self):
        self.graphics.next_label.text = 'Next: {}'.format(
            self._make_action_text(offset=1))
        self._update_label_color(self.graphics.next_label)

    def _update_prev_label(self):
        self.graphics.prev_label.text = 'Previous: {}'.format(
            self._make_action_text(offset=-1))
        self._update_label_color(self.graphics.prev_label)

    def _update_label_color(self, label):
        if self.world.cur_state.is_terminal or self.world.cur_state.is_paused:
            color = WHITEA
        else:
            color = REDA
        label.color = color

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
                    u, v = self.world.env.state.network.get_edge_name(
                        action.edge)
                    action = action.__class__(edge=(u, v), agent=action.agent)

        if action is None:
            return '<No action>'

        return str(action)


class WorldScene(EnvironmentScene):
    """TODO: docstring for WorldScene"""

    def __init__(self, world, role=Agent.HUMAN, name=None, width=1920, height=1080):
        if name is None:
            name = world.name
        super().__init__(
            world.cur_state, name=name, height=height, width=width)
        # world.env.state, name=name, height=height, width=width)

        self._role = role
        self._policy_model = world.agent.policy_model

        self._pick_action_type = PickAction
        self._submit_action_type = SubmitAction
        self.graphics.temp_suggested_sprite = None

        self._update_feasible_actions()

        self._temp_from = None
        self._temp_to = None

        self._cross_shown = False

    @property
    def temp_from(self):
        return self._temp_from

    @property
    def temp_to(self):
        return self._temp_to

    @temp_from.setter
    def temp_from(self, value):
        self._temp_from = value

    @temp_to.setter
    def temp_to(self, value):
        self._temp_to = value

    # GUI methods.

    def on_draw(self):
        self.graphics.batch.draw()
        if self.graphics.temp_suggested_sprite is not None:
            self.graphics.temp_suggested_sprite.draw()

        if self._cross_shown:
            self.graphics.cross_sprite.draw()

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

            if self._role in self.state.agents:
                if self._pick_action_type in self._action_types:
                    self._process_drawing(x, y)
                else:
                    # Put a cross at the node.
                    u = check_node_hit(self.graphics.layout, x, y)
                    if u is not None:
                        node_data = self.graphics.layout.nodes
                        self.graphics.cross_sprite.update(
                            x=node_data[u]['x'], y=node_data[u]['y'])
                        self._cross_shown = True

        if action in self._actions:
            win.execute_action(action)

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
                win.execute_action(action)

    def on_key_press(self, symbol, modifiers, win):
        """TODO docstring for on_key_press of WorldScene"""
        pass

    # Custom public methods.

    def on_update(self):
        """TODO docstring for on_update of WorldScene"""
        super().on_update()

        self._update_feasible_actions()

        self._update_buttons()
        self._update_status_label()

    def toggle_role(self):
        """TODO docstring for toggle_role of WorldScene"""
        if self._role == Agent.ROBOT:
            self._role = Agent.HUMAN
        elif self._role == Agent.HUMAN:
            self._role = Agent.ROBOT
        else:
            raise NotImplementedError

        self._reset_drawing()

    # Private methods.

    def _process_drawing(self, x, y):
        """TODO docstring for _process_drawing"""
        # Check if a node is pressed.
        node = check_node_hit(self.graphics.layout, x, y)

        node_data = self.graphics.layout.nodes

        # Check if the agent started drawing from a node.
        if self.temp_from is None:
            if node is not None:
                d = node_data[node]
                self.temp_from = (d['x'], d['y'], node)
                d['selected_sprite'].visible = True

        # If the agent is already drawing from a node.
        else:
            selected = self.state.network.get_selected_nodes()

            # If mouse is on a new node that is not already selected.
            if node is not None and node not in selected and \
                    node != self.temp_from[2]:
                self.temp_to = node
                d = node_data[node]
                d['selected_sprite'].visible = True

                # Put a cross on edge if this picking the edge is not feasible.
                from_node = self.temp_from[2]
                u, v = from_node, node
                is_selected = self.state.network.subgraph.has_edge(u, v)
                has_edge = self.graphics.layout.has_edge(u, v)

                # if has_edge and (from_node != node) and not is_selected:
                if not has_edge or is_selected:
                    self.graphics.cross_sprite.update(
                        x=(node_data[u]['x']+node_data[v]['x'])/2,
                        y=(node_data[u]['y']+node_data[v]['y'])/2)
                    self._cross_shown = True
                else:
                    self._cross_shown = False

            # If mouse was on a node and no longer is on a node,
            # reset the previous drawing-to node.
            elif self.temp_to is not None \
                    and self.temp_to not in selected:
                d = node_data[self.temp_to]
                d['selected_sprite'].visible = False
                self.temp_to = None
                self._cross_shown = False

            # Update the temporary drawing edge to the new mouse position.
            # if self.temp_from is not None:
            self.graphics.temp_suggested_sprite = create_edge_sprite(
                self.temp_edge_image, self.temp_from[0],
                self.temp_from[1], x, y)

    # Private methods.

    def _check_buttons(self, x, y):
        """TODO docstring for _check_buttons"""
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
        """TODO docstring for _check_confirm_hit"""
        return (-320 < x - self.graphics.width//2 < -40 and
                -100 < y - self.graphics.height//2 < 60)

    def _check_continue_hit(self, x, y):
        """TODO"""
        return (40 < x - self.graphics.width//2 < 320 and
                -100 < y - self.graphics.height//2 < 60)

    def _update_feasible_actions(self):
        """TODO"""
        self._actions = self._policy_model.get_all_actions(self._state)
        self._action_types = {type(action) for action in self._actions}

    def _update_paused(self):
        """Override EnvironmentScene's _update_paused() with 'role'"""
        self.graphics.observe_rect.visible = \
            self._role not in self.state.agents
        self._set_paused(self.state.is_terminal or self.state.is_paused)

    def _update_buttons(self):
        """TODO docstring for _update_buttons"""
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
        """TODO docstring for _process_drawing_done"""
        action = None

        # Check if an edge is drawn.
        if self.temp_from is not None:
            # Drawing action.
            to_node = check_node_hit(self.graphics.layout, x, y)
            if to_node is not None:
                from_node = self.temp_from[2]
                edge = from_node, to_node
                is_selected = self.state.network.subgraph.has_edge(*edge)
                has_edge = self.graphics.layout.has_edge(*edge)

                if has_edge and (from_node != to_node) and not is_selected:
                    action = self._pick_action_type(edge, agent=self._role)

        # Clear selection.
        selected = self.state.network.get_selected_nodes()
        if self.temp_from is not None \
                and self.temp_from[2] not in selected:
            node_data = self.graphics.layout.nodes[self.temp_from[2]]
            node_data['selected_sprite'].visible = False

        if self.temp_to is not None \
                and self.temp_to not in selected:
            node_data = self.graphics.layout.nodes[self.temp_to]
            node_data['selected_sprite'].visible = False
            self.temp_to = None

        self._reset_drawing()

        return action

    def _reset_drawing(self):
        """TODO docstring for _reset_drawing"""
        self.temp_from = None
        self.temp_to = None
        self.graphics.temp_suggested_sprite = None
        self._cross_shown = False


class IntroWorldScene(WorldScene):
    """TODO: docstring for IntroWorldScene"""

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


class TutorialWorldScene(WorldScene):
    """TODO: docstring for TutorialWorldScene"""

    def __init__(self, **kwargs):

        super().__init__(**kwargs)

        self.temp_edge_image = self.graphics.edge_selected_image
        self._pick_action_type = PickAction
        self._submit_action_type = SubmitAction

        # Hide node names if any.
        for u, d in self.graphics.layout.nodes(data=True):
            d['label'].text = ''

        # # Hide cost label text.
        # self.graphics.cost_label.visible = False


class IndividualWorldScene(WorldScene):
    """TODO: docstring for IndividualWorldScene"""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.temp_edge_image = self.graphics.edge_selected_image
        self._pick_action_type = PickAction
        self._submit_action_type = AttemptSubmitAction

        # Hide node names if any.
        for u, d in self.graphics.layout.nodes(data=True):
            d['label'].text = ''


class CollaborativeWorldScene(WorldScene):
    """TODO: docstring for CollaborativeWorldScene"""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.temp_edge_image = self.graphics.edge_suggested_image
        self._pick_action_type = SuggestPickAction
        self._submit_action_type = AttemptSubmitAction

    # Overridden private methods.

    def _update_buttons(self):
        """Update the button states."""
        # Update buttons of the superclass.
        super()._update_buttons()

        # Update agree button.
        if AgreeAction(self._role) in self._actions:
            self.graphics.yes_button.set_state(Button.ENABLED)
        else:
            self.graphics.yes_button.set_state(Button.DISABLED)

        # Update disagree button.
        if DisagreeAction(self._role) in self._actions:
            self.graphics.no_button.set_state(Button.ENABLED)
        else:
            self.graphics.no_button.set_state(Button.DISABLED)

    def _update_status_label(self):
        """Update the status label."""
        s = ''

        # At the start.
        if self.state.network.subgraph.number_of_edges() == 0 \
                and self.state.network.suggested_edge is None:
            if self.state.attempt_no == 1:
                s += "Let's go!"
            else:
                s += 'Try again!'

        # Terminal.
        elif self.state.is_terminal:
            if self.state.network.is_mst():
                s += 'Congratulations!'
            else:
                s += 'Game over!'

        # Role information.
        if not self.state.is_terminal:
            if self._role in self.state.agents:
                s += ' (your turn)'
            else:
                s += " (your partner's turn)"

        # The label is shown if not empty.
        is_visible = len(s) != 0

        # Update the label and its visibility.
        self.graphics.status_label.text = s
        self.graphics.status_label.visible = is_visible
        self.graphics.status_rect.visible = is_visible
