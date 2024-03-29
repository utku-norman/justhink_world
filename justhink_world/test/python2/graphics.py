from shapes import Rectangle
import copy

import pyglet

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
WHITEA = (255, 255, 255, 255)
BLACKA = (0, 0, 0, 255)
REDA = (255, 0, 0, 255)
BLUEA = (0, 0, 255, 255)


class DialogBox(object):
    def __init__(
            self, main_text='', yes_text='', no_text='',
            width_scaler=1/2.0, height_scaler=1/3.0,
            width=1920, height=1080, visible=False,
            main_fontsize=48, response_fontsize=56, batch=None):
        self._main_text = main_text
        self._yes_text = yes_text
        self._no_text = no_text

        self._init_graphics(
            width, height, main_fontsize, response_fontsize,
            width_scaler, height_scaler, batch=batch)

        self._set_visible(visible)

    def draw(self):
        """Draw manually the components of the dialog box.

        If you are not passing another batch that is already being drawn."""
        self.graphics.background_rect.draw()
        self.graphics.batch.draw()

    @property
    def visible(self):
        return self._visible

    @visible.setter
    def visible(self, value):
        # On change only.
        if value != self._visible:
            self._set_visible(value)

    def check_yes_hit(self, x, y):
        x_centered = x + self.x_pad / 2.0 - self.graphics.width / 2.0
        y_centered = y + self.y_pad / 2.0 - self.graphics.height / 2.0
        return (-self.yes_x_margin < x_centered < self.yes_x_margin and
                -self.yes_y_margin < y_centered < self.yes_y_margin)

    def check_no_hit(self, x, y):
        x_centered = x - self.x_pad / 2.0 - self.graphics.width / 2.0
        y_centered = y + self.y_pad / 2.0 - self.graphics.height / 2.0
        return (-self.no_x_margin < x_centered < self.no_x_margin and
                -self.no_y_margin < y_centered < self.no_y_margin)

    def _init_graphics(
            self, width, height, main_fontsize, response_fontsize,
            width_scaler, height_scaler, batch=None):
        graphics = Graphics(width, height, batch=batch)
        # Create groups: higher the order, the more the foreground.
        groups = [pyglet.graphics.OrderedGroup(i) for i in range(16)]

        # Set the distance between main label and yes/no labels (in pixels ).
        if self._yes_text == '' and self._no_text == '':
            self.y_pad = 0
        else:
            self.y_pad = 600 * height_scaler
        self.x_pad = 900 * width_scaler

        # Create the background rectangle (Rectangle or BorderedRectangle).
        w = width * width_scaler        # width of the rectangle.
        h = height * height_scaler      # height of the rectangle.
        # Centering on the screen.
        x = width / 2.0 - w / 2.0
        y = height / 2.0 - h / 2.0
        graphics.background_rect = Rectangle(
            x, y, w, h,  color=WHITE, group=groups[10])

        # Create the main text label.
        max_width = 700 * width_scaler
        graphics.main_label = pyglet.text.Label(
            self._main_text, x=width/2.0, y=height/2.0+self.y_pad/2.0,
            color=BLACKA, anchor_x='center', anchor_y='center',
            font_name='Sans', font_size=main_fontsize, batch=graphics.batch,
            group=groups[11])

        # Create a yes/confirm label.
        graphics.yes_label = pyglet.text.Label(
            self._yes_text, x=width/2.0-self.x_pad/2.0, 
            y=height/2.0-self.y_pad/2.0,
            color=BLACKA, anchor_x='center', anchor_y='center',
            multiline=True, width=max_width, align='center',
            font_name='Sans', font_size=response_fontsize,
            batch=graphics.batch, group=groups[11])

        # Create a no/reject label.
        graphics.no_label = pyglet.text.Label(
            self._no_text, x=width/2.0+self.x_pad/2.0, 
            y=height/2.0-self.y_pad/2.0,
            color=BLACKA, anchor_x='center', anchor_y='center',
            font_name='Sans', font_size=response_fontsize,
            multiline=True, width=max_width, align='center',
            batch=graphics.batch, group=groups[11])

        # clickable margin.
        x_margin, y_margin = 40, 40
        self.yes_x_margin = graphics.yes_label.content_width / 2.0 + x_margin
        self.yes_y_margin = graphics.yes_label.content_height / 2.0 + x_margin
        self.no_x_margin = graphics.no_label.content_width / 2.0 + y_margin
        self.no_y_margin = graphics.no_label.content_height / 2.0 + y_margin

        self.graphics = graphics

    def _set_visible(self, is_visible):
        # Show or hide the components.
        self.graphics.background_rect.visible = is_visible
        if is_visible:
            self.graphics.main_label.text = self._main_text
            self.graphics.yes_label.text = self._yes_text
            self.graphics.no_label.text = self._no_text
        else:
            self.graphics.main_label.text = ''
            self.graphics.yes_label.text = ''
            self.graphics.no_label.text = ''

        # Update the internal value.
        self._visible = is_visible


class Graphics(object):
    def __init__(self, width=1920, height=1080, from_graph=None, batch=None):
        if from_graph is not None:
            self.layout = copy.deepcopy(from_graph)

        self.width = width
        self.height = height

        self.buttons = {}

        if batch is None:
            self.batch = pyglet.graphics.Batch()
        else:
            self.batch = batch
