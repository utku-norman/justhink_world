import pyglet
from pyglet.window import key

from .world_scene import WorldScene


class WorldWindow(pyglet.window.Window):
    def __init__(self, world,
                 title='JUSThink World',
                 width=1920,
                 height=1080):
        self.scene = WorldScene(world=world, width=width, height=height)

        # window_style = pyglet.window.Window.WINDOW_STYLE_DEFAULT
        window_style = pyglet.window.Window.WINDOW_STYLE_BORDERLESS

        super().__init__(width, height, title,
                         style=window_style, fullscreen=False)

        # Move the window to a screen in possibly a dual-monitor setup.
        display = pyglet.canvas.get_display()
        screens = display.get_screens()
        # active_screen = screens[0]  # the laptop screen
        active_screen = screens[-1]  # the external screen
        self.set_location(active_screen.x, active_screen.y)

        # Enter the main event loop.
        pyglet.app.run()

    def on_draw(self):
        self.scene.on_draw()

    def on_key_press(self, symbol, modifiers):
        if symbol == key.ESCAPE:
            self.close()
