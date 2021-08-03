import pyglet


def center_image(image):
    """Sets an image's anchor point to its center"""
    image.anchor_x = image.width // 2
    image.anchor_y = image.height // 2


class TextWidget(object):
    # built on https://pythonhosted.org/pyglet/programming_guide/text_input.py
    def __init__(self, text, x, y, width, name,
                 valid_func=lambda text: True,
                 entry_func=lambda char: True,
                 batch=None, group=None, font_size=50):

        self.document = pyglet.text.document.FormattedDocument(text)
        # self.font_name = self.document.get_style('font_name', 0)
        # font_size = 50
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


class ButtonWidget:
    def __init__(self, x, y,
                 paths,  #
                 state,
                 scale=1,
                 batch=None,
                 group=None):
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
            self.sprites[state] = s

        s = self.sprites[self.state]
        self.dist = (s.width**2 + s.height**2) / 4

    def set_state(self, state):
        assert state in self.sprites, "Undefined state for button widget."

        self.state = state
        for state, sprite in self.sprites.items():
            if state == self.state:
                sprite.visible = True
            else:
                sprite.visible = False

    def check_hit(self, x, y):
        s = self.sprites[self.state]
        d = (s.x - x)**2 + (s.y - y)**2
        return d < self.dist


class Rectangle(object):
    """Draws a rectangle into a batch."""

    def __init__(self, x1, y1, x2, y2, batch, group):
        self.vertex_list = batch.add(4, pyglet.gl.GL_QUADS, group,
                                     ('v2i', [x1, y1, x2, y1, x2, y2, x1, y2]),
                                     ('c4B', [192, 192, 192, 255] * 4)
                                     )
