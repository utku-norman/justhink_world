import pyglet
from pyglet.window import key

from justhink_world.tools.graphics import Scene, Graphics, WHITEA


def show_observer(world):
    ObserverWindow(world)

    # Enter the main event loop.
    pyglet.app.run()


class ObserverWindow(pyglet.window.Window):
    """docstring for MentalWindow"""

    def __init__(self, world, caption="Robot's Mind", width=1920, height=1080,
                 offset=(1920, 0), screen_index=0, max_level=2):

        self.scene = ObserverScene(
            world, width=width, height=height, max_level=max_level)

        # style = pyglet.window.Window.WINDOW_STYLE_DEFAULT
        style = pyglet.window.Window.WINDOW_STYLE_BORDERLESS
        super().__init__(width, height, caption, style=style)

        # Move the window to a screen in possibly a dual-monitor setup.
        display = pyglet.canvas.get_display()
        screens = display.get_screens()
        # 0 for the laptop screen, e.g. 1 for the external screen
        active_screen = screens[screen_index]
        self.set_location(active_screen.x+offset[0], active_screen.y+offset[1])

        self.register_event_type('on_update')
        self.dispatch_event('on_update')

    @property
    def cur_scene(self):
        return self.scene

    @cur_scene.setter
    def cur_scene(self, value):
        self.scene = value

    # GUI methods.

    def on_draw(self):
        self.clear()
        self.scene.on_draw()

    def on_mouse_press(self, x, y, button, modifiers):
        self.scene.on_mouse_press(x, y, button, modifiers, win=self)

    def on_mouse_drag(self, x, y, dx, dy, buttons, modifiers):
        self.scene.on_mouse_drag(x, y, dx, dy, buttons, modifiers, win=self)

    def on_mouse_release(self, x, y, button, modifiers):
        self.scene.on_mouse_release(x, y, button, modifiers, win=self)

    # Custom public methods.

    def on_update(self):
        # Update the scene.
        self.scene.on_update()


class ObserverScene(Scene):
    """docstring for ObserverScene"""

    def __init__(self, world, width, height, max_level=2):

        super().__init__(world.name, width, height)

        # Create the graphics.
        self._init_graphics(width, height, max_level=max_level)

    # GUI methods.

    def on_draw(self):
        self.graphics.batch.draw()

    def on_key_press(self, symbol, modifiers):
        if symbol == key.ESCAPE:
            self.close()

    # Custom public methods.

    def on_update(self):
        pass

    # Private methods.

    def _init_graphics(self, width, height, max_level, batch=None):
        font_size = 20
        graphics = Graphics(width, height, batch=batch)
        batch = graphics.batch

        # groups = [pyglet.graphics.OrderedGroup(i) for i in range(10)]

        outer_pad = (50, 50, 60, 60)  # left, right, top, bottom

        # Next action if any label.
        graphics.next_label = pyglet.text.Label(
            '', x=width//2, y=height-20, anchor_y='center', color=WHITEA,
            font_name='Sans', font_size=font_size, batch=batch)

        # Previous action if any label.
        graphics.prev_label = pyglet.text.Label(
            '', x=outer_pad[0], y=height-20, anchor_y='center', color=WHITEA,
            font_name='Sans', font_size=font_size, batch=batch)

        # Initialise "observes" texts.
        # y = outer_pad[1]+3*height//6
        x_pad, y_pad = (300, 60)
        y = graphics.height - outer_pad[2] - 3 * y_pad
        graphics.observes_heading_label = pyglet.text.Label(
            '(robot observes)', x=outer_pad[0], y=y, font_name='Sans',
            font_size=font_size, batch=batch)
        graphics.observes_label = pyglet.text.Label(
            '', x=outer_pad[0]+x_pad, y=y, align='center', font_name='Sans',
            font_size=font_size, batch=batch)
