import pyglet
from pyglet.window import key

from .scene import WorldScene


class WorldWindow(pyglet.window.Window):
    def __init__(self, world,
                 title='JUSThink World',
                 width=1920,
                 height=1080):
        self.world = world

        scene = WorldScene(state=world.env.state,
                           width=width, height=height)

        # layout = world.layout
        # policy_model = world.agent.policy_model
        # state = world.env.state

        self.scene = scene

        # window_style = pyglet.window.Window.WINDOW_STYLE_DEFAULT
        window_style = pyglet.window.Window.WINDOW_STYLE_BORDERLESS

        super().__init__(width, height, title,
                         style=window_style, fullscreen=False)

        # Move the window to a screen in possibly a dual-monitor setup.
        display = pyglet.canvas.get_display()
        screens = display.get_screens()
        active_screen = screens[0]  # the laptop screen
        # active_screen = screens[-1]  # the external screen
        self.set_location(active_screen.x, active_screen.y)

        # History label.
        self._hist_label = pyglet.text.Label(
            self.make_hist_label_text(),
            x=20, y=height-140,
            anchor_y='center',
            color=(0, 0, 0, 255),
            font_name='monospace',  # 'Sans',
            font_size=32,
            group=pyglet.graphics.OrderedGroup(5))

        # Enter the main event loop.
        pyglet.app.run()

    def __str__(self):
        return self.__repr__()

    def __repr__(self):
        return 'WorldWindow({}, width={}, height={})'.format(
            self.world.env.state, self.width, self.height)

    def on_draw(self):
        self.scene.on_draw()
        self._hist_label.draw()

    def on_key_press(self, symbol, modifiers):
        state = None

        if symbol == key.ESCAPE:
            self.close()
        elif symbol == key.LEFT:
            state = self.world.get_prev_state()
        elif symbol == key.RIGHT:
            state = self.world.get_next_state()
        elif symbol == key.HOME:
            state = self.world.get_prev_state(first=True)
        elif symbol == key.END:
            state = self.world.get_next_state(last=True)

        if state is not None:
            self.scene.update(state)
            self._hist_label.text = self.make_hist_label_text()

    # Helper methods.

    def make_hist_label_text(self):
        return 'State : {}/{}'.format(
            self.world.state_no,
            self.world.get_state_count())

    # def update_scene(self, verbose=False):
    #     # Get the indexed state.
    #     i = self.world.state_no
    #     if i == 0:  # initial state.
    #         state = self.world.init_state
    #     else:  # next state of the transition.
    #         state = self.world.history[i-1][2]

    #     # Update the scene with the indexed state.
    #     # self.scene.update(state)
    #     self.scene.update(state)

    #     if verbose:
    #         print('Updated state to {}'.format(state))
