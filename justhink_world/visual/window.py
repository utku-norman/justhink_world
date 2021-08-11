import pyglet
from pyglet.window import key

from justhink_world.world import IndividualWorld, CollaborativeWorld

from .scene import CollabWorldScene, IndivWorldScene

from justhink_world.domain.action import SetPauseAction


class WorldWindow(pyglet.window.Window):
    def __init__(self, world,
                 title='JUSThink World',
                 width=1920,
                 height=1080,
                 screen_no=0):
        self._world = world

        assert isinstance(world, IndividualWorld) or \
            isinstance(world, CollaborativeWorld)

        if isinstance(world, IndividualWorld):
            scene_type = IndivWorldScene
        elif isinstance(world, CollaborativeWorld):
            scene_type = CollabWorldScene
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
            self._make_hist_label_text(),
            x=20, y=height-120,
            anchor_y='center',
            color=(0, 0, 0, 255),
            font_name='monospace',
            font_size=32,
            group=pyglet.graphics.OrderedGroup(5))

        # Role label.
        self._role_label = pyglet.text.Label(
            '',
            x=20, y=height-40,
            anchor_y='center',
            color=(0, 0, 0, 255),
            font_name='Sans',
            font_size=32,
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

    def act_via_window(self, action):
        self._world.act(action)
        self.update(self._world.get_state())

    def on_mouse_press(self, x, y, button, modifiers):
        self._scene.on_mouse_press(
            x, y, button, modifiers, win=self)

    def on_mouse_drag(self, x, y, dx, dy, buttons, modifiers):
        self._scene.on_mouse_drag(
            x, y, dx, dy, buttons, modifiers, win=self)

    def on_mouse_release(self, x, y, button, modifiers):
        self._scene.on_mouse_release(
            x, y, button, modifiers, win=self)

    def on_key_press(self, symbol, modifiers):
        if symbol == key.ESCAPE:
            self.close()
        elif symbol == key.LEFT:
            state = self._world.get_prev_state()
            self.update(state)
        elif symbol == key.RIGHT:
            state = self._world.get_next_state()
            self.update(state)
        elif symbol == key.HOME:
            state = self._world.get_prev_state(first=True)
            self.update(state)
        elif symbol == key.END:
            state = self._world.get_next_state(last=True)
            self.update(state)
        elif symbol == key.TAB:
            self._scene.toggle_role()
            self.update()
        elif symbol == key.P:
            is_paused = self._world.get_state().is_paused
            self.act_via_window(SetPauseAction(not is_paused))

    # Maintenance methods.

    def update(self, state=None):
        self._scene.update(state)

        # Update the history label.
        self._hist_label.text = self._make_hist_label_text()

        # Update the role label.
        # print('###########', self._scene.role)
        self._role_label.text = self._make_role_label_text()

    # Helper methods.

    def _make_role_label_text(self):
        return 'Role: {}'.format(self._scene.role.name)

    def _make_hist_label_text(self):
        return 'State: {}/{}'.format(
            self._world.state_no,
            self._world.get_state_count())
