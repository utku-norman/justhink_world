import copy

import pyglet
from pyglet.window import key

from justhink_world.world import IndividualWorld, CollaborativeWorld

from .scene import CollaborativeWorldScene, IndividualWorldScene

from justhink_world.domain.action import SetPauseAction


class WorldWindow(pyglet.window.Window):
    def __init__(self, world, title='JUSThink World', width=1920, height=1080,
                 screen_no=0):
        self._world = world

        assert isinstance(world, IndividualWorld) or \
            isinstance(world, CollaborativeWorld)

        if isinstance(world, IndividualWorld):
            scene_type = IndividualWorldScene
        elif isinstance(world, CollaborativeWorld):
            scene_type = CollaborativeWorldScene
        self._scene = scene_type(world=world,
                                 width=width, height=height)
        self._scene.update(world.env.state)

        # window_style = pyglet.window.Window.WINDOW_STYLE_DEFAULT
        window_style = pyglet.window.Window.WINDOW_STYLE_BORDERLESS

        super().__init__(width, height, title,
                         style=window_style, fullscreen=False)

        # Move the window to a screen in possibly a dual-monitor setup.
        display = pyglet.canvas.get_display()
        screens = display.get_screens()
        # 0 for the laptop screen, e.g. 1 for the external screen
        active_screen = screens[screen_no]
        self.set_location(active_screen.x, active_screen.y)

        # History label.
        self._hist_label = pyglet.text.Label(
            self._make_hist_label_text(), x=20, y=height-120,
            anchor_y='center', color=(0, 0, 0, 255),
            font_name='monospace', font_size=32,
            group=pyglet.graphics.OrderedGroup(5))

        # Role label.
        self._role_label = pyglet.text.Label(
            '', x=20, y=height-60, anchor_y='center', color=(0, 0, 0, 255),
            font_name='Sans', font_size=32,
            group=pyglet.graphics.OrderedGroup(5))

        # Next action if any label.
        self._next_action_label = pyglet.text.Label(
            '', x=width//2, y=height-20, anchor_y='center',
            color=(0, 0, 0, 255), font_name='Sans', font_size=24,
            group=pyglet.graphics.OrderedGroup(5))

        # Previous action if any label.
        self._prev_action_label = pyglet.text.Label(
            '', x=20, y=height-20, anchor_y='center',
            color=(0, 0, 0, 255), font_name='Sans', font_size=24,
            group=pyglet.graphics.OrderedGroup(5))

        self.update()

        # Enter the main event loop.
        pyglet.app.run()

    def __str__(self):
        return self.__repr__()

    def __repr__(self):
        return 'WorldWindow({},w={},h={})'.format(
            self._world.env.state, self.width, self.height)

    def on_draw(self):
        self._scene.on_draw()
        self._hist_label.draw()
        self._role_label.draw()
        self._next_action_label.draw()
        self._prev_action_label.draw()

    def act_via_window(self, action):
        self._world.act(action)
        self.update(self._world.cur_state)

    def on_mouse_press(self, x, y, button, modifiers):
        self._scene.on_mouse_press(x, y, button, modifiers, win=self)

    def on_mouse_drag(self, x, y, dx, dy, buttons, modifiers):
        self._scene.on_mouse_drag(x, y, dx, dy, buttons, modifiers, win=self)

    def on_mouse_release(self, x, y, button, modifiers):
        self._scene.on_mouse_release(x, y, button, modifiers, win=self)

    def on_key_press(self, symbol, modifiers):
        world = self._world

        if symbol == key.ESCAPE:
            self.close()
        elif symbol == key.LEFT:
            world.state_no = world.state_no - 1
            self.update(world.cur_state)
        elif symbol == key.RIGHT:
            world.state_no = world.state_no + 1
            self.update(world.cur_state)
        elif symbol == key.HOME:
            world.state_no = 1
            self.update(world.cur_state)
        elif symbol == key.END:
            world.state_no = world.num_states
            self.update(world.cur_state)
        elif symbol == key.TAB:
            self._scene.toggle_role()
            self.update()
        elif symbol == key.P:
            is_paused = world.cur_state.is_paused
            self.act_via_window(SetPauseAction(not is_paused))

    # Maintenance methods.

    def update(self, state=None):
        self._scene.update(state)

        # Update the history label.
        self._hist_label.text = self._make_hist_label_text()

        # Update the role label.
        self._role_label.text = self._make_role_label_text()

        self._next_action_label.text = self._make_next_action_label_text()
        self._prev_action_label.text = self._make_prev_action_label_text()

    # Helper methods.

    def _make_role_label_text(self):
        return 'Role: {}'.format(self._scene.role.name)

    def _make_action_text(self, offset=1):
        world = self._world
        index = world.state_index + offset
        try:
            action = world.history[index]
        except IndexError:
            action = None
        if index < 0:
            action = None

        if isinstance(world, CollaborativeWorld):
            if action is not None:
                action = copy.deepcopy(action)
                if hasattr(action, 'edge') and action.edge is not None:
                    edge_name = world.env.state.network.get_edge_name(
                        action.edge)
                    u, _, v = edge_name.split()
                    action = action.__class__(edge=(u, v), agent=action.agent)
                    # print(action)
        return str(action)

    def _make_next_action_label_text(self):
        return 'Next: {}'.format(self._make_action_text(offset=1))

    def _make_prev_action_label_text(self):
        return 'Previous: {}'.format(self._make_action_text(offset=-1))

    def _make_hist_label_text(self):
        return 'State: {}/{}'.format(
            self._world.state_no,
            self._world.num_states)
