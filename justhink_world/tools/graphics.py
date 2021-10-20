import copy
import math


import pyglet

# from justhink_world.domain.state import Button

# from justhink_world.tools.graphics import center_image, Rectangle


WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
WHITEA = (255, 255, 255, 255)
BLACKA = (0, 0, 0, 255)


class Scene(object):
    """Abstract scene (i.e. activity) class for common methods."""

    def __init__(self, name, width, height):
        self.name = name
        self.graphics = Graphics(width, height)

    def on_key_press(self, symbol, modifiers, win):
        pass

    def on_close(self):
        pass

    def on_update(self, **kwargs):
        pass

    def on_mouse_press(self, x, y, button, modifiers, win):
        pass

    def on_mouse_drag(self, x, y, dx, dy, buttons, modifiers, win):
        pass

    def on_mouse_release(self, x, y, button, modifiers, win):
        pass

    def on_text(self, text):
        pass

    def on_text_motion(self, motion):
        pass

    def on_text_motion_select(self, motion):
        pass

    def on_state_update(self, **kwargs):
        pass


def check_node_hit(graph, x, y):
    for u, d in graph.nodes(data=True):
        if 'is_temp' in d and d['is_temp']:
            continue
        dist = (x - d['x'])**2 + (y - d['y'])**2
        if dist < max(d['sprite'].width, d['sprite'].height) ** 2 / 4:
            return u

    return None


def check_edge_hit(graph, x, y):
    for edge in graph.edges():
        n1 = graph.nodes[edge[0]]
        n2 = graph.nodes[edge[1]]

        n1x = n1['x']
        n1y = n1['y']
        n2x = n2['x']
        n2y = n2['y']

        # circle containing the edge
        ccx = (n1x + n2x) / 2.0  # circle center x
        ccy = (n1y + n2y) / 2.0  # circle center y
        r = ((n1x - n2x)**2 + (n1y - n2y)**2) / 4.0  # squared radius

        # squared distance of the point (x, y)
        # form the center of the circle above
        dp = (ccx - x)**2 + (ccy - y)**2

        if dp <= r:
            # magic, don't touch!
            a = n2y - n1y
            b = n1x - n2x
            c = n2x * n1y - n1x * n2y

            d = abs(a * x + b * y + c) / math.sqrt(a**2 + b**2)

            if d < 50:  # 50: # 5: # play
                return tuple(sorted(list(edge)))

    return None


def create_edge_sprite(
        image, ux, uy, vx, vy, batch=None, group=None, visible=True):
    dist = math.sqrt((ux-vx)**2 + (uy-vy)**2)
    w = int(math.floor(dist))
    image_part = image.get_region(x=0, y=0, width=w, height=image.height)
    if image_part.width > 0 and image_part.height > 0:
        center_image(image_part)
        s = pyglet.sprite.Sprite(
            image_part, x=(ux+vx)/2, y=(uy+vy)/2, batch=batch, group=group)
        s.rotation = -math.degrees(math.atan2(uy-vy, ux-vx))
        s.visible = visible

        return s
    else:
        return None


def create_ellipse(x, y, rx, ry, n_points=400, batch=None, group=None):
    verts = []
    for i in range(n_points):
        angle = math.radians(float(i)/n_points * 360.0)
        xx = rx*math.cos(angle) + x
        yy = ry*math.sin(angle) + y
        verts += [xx, yy]

    if batch is None:
        return pyglet.graphics.vertex_list(n_points, ('v2f', verts))
    else:
        return batch.add(n_points, pyglet.gl.GL_POINTS, group,
                         ('v2f', verts))


def transform_position(x, y, from_view, to_view):
    nx = translate(x,
                   from_view.x + from_view.pad[0],
                   from_view.x + from_view.width - from_view.pad[1],
                   to_view.x + to_view.pad[0],
                   to_view.x + to_view.width - to_view.pad[1])
    ny = translate(y,
                   from_view.y + from_view.pad[3],
                   from_view.y + from_view.height - from_view.pad[2],
                   to_view.y + to_view.pad[3],
                   to_view.y + to_view.height - to_view.pad[2])
    return nx, ny


def translate(value, left_min, left_max, right_min, right_max):
    """from https://stackoverflow.com/a/1969274"""
    # Figure out how 'wide' each range is.
    left_span = left_max - left_min
    right_span = right_max - right_min

    # Convert the left range into a 0-1 range (float).
    value_scaled = float(value - left_min) / float(left_span)

    # Convert the 0-1 range into a value in the right range.
    return right_min + (value_scaled * right_span)


def is_between(x, a, b): return \
    a < sorted([a, b])[1] and a > sorted([a, b])[0]


def slide_x(dt, sprite):
    if sprite.x > sprite.max_x:
        sprite.x = sprite.max_x
        sprite.dx = -sprite.dx
    elif sprite.x < sprite.min_x:
        sprite.x = sprite.min_x
        sprite.dx = -sprite.dx

    sprite.x += sprite.dx * dt


def crop_edge(ux, uy, vx, vy, rx, ry):
    # xs = [ux, vx] if ux < vx else [vx, ux]
    # ys = [uy, vy] if uy < vy else [vy, uy]
    angle = math.atan2(uy-vy, ux-vx)

    ux_new = rx*math.cos(angle) + ux
    uy_new = ry*math.sin(angle) + uy
    if not (is_between(ux_new, ux, vx) and is_between(uy_new, uy, vy)):
        angle = angle + math.pi
        ux_new = rx*math.cos(angle) + ux
        uy_new = ry*math.sin(angle) + uy

    vx_new = rx*math.cos(angle) + vx
    vy_new = ry*math.sin(angle) + vy
    if not (is_between(vx_new, ux, vx) and is_between(vy_new, uy, vy)):
        angle = angle + math.pi
        vx_new = rx*math.cos(angle) + vx
        vy_new = ry*math.sin(angle) + vy

    return ux_new, uy_new, vx_new, vy_new


class Graphics(object):
    """docstring for Graphics"""

    def __init__(self, width=1920, height=1080, from_graph=None, batch=None):
        if from_graph is not None:
            self.layout = copy.deepcopy(from_graph)

        self.width = width
        self.height = height

        # self._temp_from = None
        # self._temp_to = None

        self.buttons = {}

        if batch is None:
            self.batch = pyglet.graphics.Batch()
        else:
            self.batch = batch


def center_image(image):
    """Set an image's anchor point to its center."""
    image.anchor_x = image.width // 2
    image.anchor_y = image.height // 2

    return image


class Rectangle(object):
    """Draws a rectangle into a batch."""

    def __init__(self, x1, y1, x2, y2, batch, group):
        self.vertex_list = batch.add(4, pyglet.gl.GL_QUADS, group,
                                     ('v2i', [x1, y1, x2, y1, x2, y2, x1, y2]),
                                     ('c4B', [192, 192, 192, 255] * 4)
                                     )


class Surface(object):
    def __init__(self, width, height,
                 x=0, y=0,
                 pad=(0, 0, 0, 0)):  # left, right, top, bottom
        self.height = height
        self.width = width
        self.x = x
        self.y = y
        self.pad = pad

    def check_hit(self, x, y):
        return (0 < x - self.x < self.width and
                0 < y - self.y < self.height)


class TextWidget(object):
    # built on https://pythonhosted.org/pyglet/programming_guide/text_input.py
    def __init__(self, text, x, y, width, name,
                 valid_func=lambda text: True,
                 entry_func=lambda char: True,
                 batch=None, group=None, font_size=50):

        self.document = pyglet.text.document.FormattedDocument(text)
        self.document.set_style(0, len(self.document.text),
                                dict(font_name='Times New Roman',
                                     font_size=font_size,
                                     color=(0, 0, 0, 255),
                                     valign='bottom')
                                )

        self.valid_func = valid_func
        self.entry_func = entry_func
        self.name = name
        self.fview_line_width = 16
        height = font_size + 40

        self.layout = pyglet.text.layout.IncrementalTextLayout(
            self.document, width, height, multiline=False,
            batch=batch, group=group)
        self.caret = pyglet.text.caret.Caret(self.layout)

        self.layout.x = x
        self.layout.y = y

        # Rectangular outline
        pad = 20
        self.rectangle = Rectangle(x - pad, y - pad,
                                   x + width + pad,
                                   y + height + pad, batch,
                                   group=group)

        self.caret.visible = False

    def check_hit(self, x, y):
        return (0 < x - self.layout.x < self.layout.width and
                0 < y - self.layout.y < self.layout.height)

    def check_valid(self):
        return self.valid_func(self.document.text)

    def get_content(self):
        return self.document.text

    def set_content(self, value):
        self.document.text = value


class Button(object):
    """A class to represent an abstract button and its possible states.

    Attributes:
        NA:
            the button is not available and will not be displayed.
        ENABLED:
            the button is available, e.g. can be pressed to trigger an action.
        DISABLED:
            the button is shown, but e.g. is grayed out, to indicate it was
            and/or will become available during the interaction
        SELECTED:
            the button is "selected", e.g. for a submit button, to indicate
            that the current solution is submitted for a submit button
    """
    NA = 'N'
    ENABLED = 'E'
    DISABLED = 'D'
    SELECTED = 'S'


class ButtonWidget(Button):
    def __init__(self, x, y, paths, state, scale=1, batch=None, group=None):
        self.x = x
        self.y = y
        self.state = state

        self.sprites = dict()
        for state, path in paths.items():
            with path as file:
                image = pyglet.image.load(str(file))
            center_image(image)
            s = pyglet.sprite.Sprite(
                image, x=x, y=y, batch=batch, group=group)
            s.scale = scale
            self.dist = (s.width**2 + s.height**2) / 4
            self.sprites[state] = s

        self.set_state(self.state)

    def set_state(self, state):
        assert state in self.sprites or state == Button.NA, \
            "Undefined state '{}' for button.".format(state)

        self.state = state
        for state, sprite in self.sprites.items():
            if state == self.state:
                sprite.visible = True
            else:
                sprite.visible = False

    def check_hit(self, x, y):
        if self.state != Button.NA:
            s = self.sprites[self.state]
            d = (s.x - x)**2 + (s.y - y)**2
            return d < self.dist
