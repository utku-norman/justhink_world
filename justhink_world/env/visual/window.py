import pyglet

from .scene import EnvironmentScene


class EnvironmentWindow(pyglet.window.Window):
    def __init__(self, state,
                 title='JUSThink Environment',
                 width=1920,
                 height=1080):

        self.state = state
        self.scene = EnvironmentScene(state=state,
                                      width=width, height=height)
        self.scene.update(state)

        window_style = pyglet.window.Window.WINDOW_STYLE_BORDERLESS

        super().__init__(width, height, title,
                         style=window_style, fullscreen=False)

        # Move the window to a screen in possibly a dual-monitor setup.
        display = pyglet.canvas.get_display()
        screens = display.get_screens()
        active_screen = screens[0]  # the laptop screen
        self.set_location(active_screen.x, active_screen.y)

        # Enter the main event loop.
        pyglet.app.run()

    def __str__(self):
        return self.__repr__()

    def __repr__(self):
        return 'EnvironmentWindow({},w={},h={})'.format(
            self.state, self.width, self.height)

    def on_draw(self):
        self.scene.on_draw()

    def on_mouse_press(self, x, y, button, modifiers):
        self.scene.on_mouse_press(
            x, y, button, modifiers, win=self)

    def on_mouse_drag(self, x, y, dx, dy, buttons, modifiers):
        self.scene.on_mouse_drag(
            x, y, dx, dy, buttons, modifiers, win=self)

    def on_mouse_release(self, x, y, button, modifiers):
        self.scene.on_mouse_release(
            x, y, button, modifiers, win=self)
