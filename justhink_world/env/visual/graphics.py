import copy
import math
import pyglet

import importlib_resources

from .widgets import ButtonWidget

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
WHITE_RGBA = (255, 255, 255, 255)
BLACK_RGBA = (0, 0, 0, 255)


class Graphics(object):
    """docstring for Graphics"""

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


def init_graphics(graph, width, height, image_container, batch=None):
    # , show_edge_costs=True, show_node_names=True
    graphics = Graphics(width, height, from_graph=graph, batch=batch)
    batch = graphics.batch

    # Create groups: higher the order, the more the foreground.
    groups = [pyglet.graphics.OrderedGroup(i) for i in range(16)]

    # Load a cloud.
    ref = image_container.joinpath('cloud.png')
    image = read_image_from_reference(ref)
    s = pyglet.sprite.Sprite(image, batch=batch, group=groups[6])
    s.scale = 0.2
    s.dx = 20.0
    s.position = (220, height-150)
    s.min_x = 50  # self.cloud.x
    s.max_x = 400
    graphics.cloud_sprite = s
    pyglet.clock.schedule_interval(slide_x, 1.0/60, graphics.cloud_sprite)

    # cow_img = pyglet.image.load(
    # str(self._images_dir.joinpath('cloud.png')))
    # self.cow = pyglet.sprite.Sprite(cow_img)

    # self.cow.scale = 0.35
    # self.cow.dx = 20.0
    # self.cow.position = (220, height - 670)
    # self.cow.min_x = self.cow.x
    # self.cow.max_x = 400

    # Attempt label.
    graphics.attempt_label = pyglet.text.Label(
        '', x=20, y=height-200, anchor_y='center', color=BLACK_RGBA,
        font_name='Sans', font_size=32, group=groups[5], batch=batch)

    # Create confirm box components.
    graphics.confirm_text_label = pyglet.text.Label(
        '', x=width//2, y=height//2+180, color=BLACK_RGBA,
        anchor_x='center', anchor_y='center', font_name='Sans', font_size=48,
        batch=batch, group=groups[11])

    graphics.yes_label = pyglet.text.Label(
        '', x=width//2-180, y=height//2-20, color=BLACK_RGBA,
        anchor_x='center', anchor_y='center', font_name='Sans',
        font_size=56, batch=batch, group=groups[11])

    graphics.no_label = pyglet.text.Label(
        '', x=width//2+180, y=height//2-20,  # width=width, height=50,
        color=BLACK_RGBA, anchor_x='center', anchor_y='center',
        font_name='Sans', font_size=56, batch=batch, group=groups[11])

    graphics.confirm_rect = pyglet.shapes.Rectangle(
        width//4, height//4+140, width//2, height//3,
        color=WHITE, batch=batch, group=groups[10])
    graphics.confirm_rect.opacity = 255
    graphics.confirm_rect.visible = False

    # Cost label.
    graphics.cost_label = pyglet.text.Label(
        '', x=20, y=height-290, anchor_y='center', color=BLACK_RGBA,
        font_name='Sans', font_size=32, batch=batch, group=groups[8])

    # Bottom label.
    graphics.status_label = pyglet.text.Label(
        '', x=width//2, y=20, anchor_x='center', color=WHITE_RGBA,
        font_name='Sans', font_size=24, batch=batch, group=groups[8])

    graphics.status_rect = pyglet.shapes.Rectangle(
        0, 0, width, 60, color=BLACK, batch=batch, group=groups[5])
    graphics.status_rect.opacity = 150
    graphics.status_rect.visible = False

    graphics.paused_rect = pyglet.shapes.Rectangle(
        0, 0, width, height, color=BLACK, batch=batch, group=groups[14])
    graphics.paused_rect.opacity = 100
    graphics.paused_rect.visible = False

    graphics.view_only_rect = pyglet.shapes.Rectangle(
        0, 0, width, height, color=BLACK, batch=batch, group=groups[15])
    graphics.view_only_rect.opacity = 170
    graphics.view_only_rect.visible = False

    # Create a background image sprite.
    key = 'background_image_file'
    if key in graphics.layout.graph:
        ref = image_container.joinpath(graphics.layout.graph[key])
        image = read_image_from_reference(ref)
        graphics.bg_sprite = pyglet.sprite.Sprite(
            image, batch=batch, group=groups[0])

    # Create node images.
    for u, d in graphics.layout.nodes(data=True):
        ref = image_container.joinpath(d['image_file'])
        image = center_image(read_image_from_reference(ref))
        d['sprite'] = pyglet.sprite.Sprite(
            image, d['x'], d['y'], batch=batch, group=groups[2])

        ref = image_container.joinpath(d['higlight_image_file'])
        image = center_image(read_image_from_reference(ref))
        d['added_sprite'] = pyglet.sprite.Sprite(
            image, d['x'], d['y'], batch=batch, group=groups[3])
        d['added_sprite'].visible = False

    # Create edge images.
    ref = image_container.joinpath('railroad_added.png')
    edge_added_image = center_image(read_image_from_reference(ref))
    graphics.edge_added_image = edge_added_image

    ref = image_container.joinpath('railroad_selected.png')
    edge_selected_image = center_image(read_image_from_reference(ref))

    ref = image_container.joinpath('railroad_selectable.png')
    edge_selectable_image = center_image(read_image_from_reference(ref))

    ref = image_container.joinpath('railroad_suggested.png')
    edge_suggested_image = center_image(read_image_from_reference(ref))
    graphics.edge_suggested_image = edge_suggested_image

    for u, v, d in graphics.layout.edges(data=True):
        ud = graphics.layout.nodes[u]
        vd = graphics.layout.nodes[v]

        d['selectable_sprite'] = create_edge_sprite(
            edge_selectable_image, ud['x'], ud['y'], vd['x'], vd['y'],
            batch=batch, group=groups[1], visible=True)

        d['selected_sprite'] = create_edge_sprite(
            edge_selected_image, ud['x'], ud['y'], vd['x'], vd['y'],
            batch=batch, group=groups[1], visible=False)

        d['added_sprite'] = create_edge_sprite(
            edge_added_image, ud['x'], ud['y'], vd['x'], vd['y'],
            batch=batch, group=groups[1], visible=False)

        d['suggested_sprite'] = create_edge_sprite(
            edge_suggested_image, ud['x'], ud['y'], vd['x'], vd['y'],
            batch=batch, group=groups[1], visible=False)

    # Create node labels.
    for u, d in graphics.layout.nodes(data=True):
        if 'label_x' in d and 'label_y' in d:
            x, y = d['label_x'], d['label_y']
        else:  # default location
            x, y = d['x'], d['y']
        d['label'] = pyglet.text.Label(
            d['text'], x=x, y=y, font_name='Purisa', font_size=22,
            anchor_x='center', anchor_y='center',
            bold=False, color=BLACK_RGBA, batch=batch, group=groups[5])

    # Create edge labels.
    x_key, y_key = 'label_x', 'label_y'
    for u, v, d in graphics.layout.edges(data=True):
        ud = graphics.layout.nodes[u]
        vd = graphics.layout.nodes[v]

        ux, uy = ud['x'], ud['y']
        vx, vy = vd['x'], vd['y']

        d[x_key] = (ux + vx) / 2
        d[y_key] = (uy + vy) / 2

        slope = (uy - vy) / (ux - vx)

        if slope > 0:
            anchor_x = 'right'
            d[x_key] = d[x_key] - 5
        else:
            anchor_x = 'left'
            d[x_key] = d[x_key] + 5

        # if show_edge_costs:
        text = str(d['cost'])
        # else:
        # text = ''
        d['cost_label'] = pyglet.text.Label(
            text, x=d[x_key], y=d[y_key], font_name='Sans', font_size=28,
            anchor_x=anchor_x, anchor_y='bottom',
            color=BLACK_RGBA, batch=batch, group=groups[8])

    # Load gold image/gif.
    ref = image_container.joinpath('gold.gif')
    with ref as file:
        animation = pyglet.image.load_animation(str(file))
    gold_bin = pyglet.image.atlas.TextureBin()
    animation.add_to_texture_bin(gold_bin)

    # Set gold location if not available.
    for u, d in graphics.layout.nodes(data=True):
        if 'gold_x' not in d:
            d['gold_x'] = d['x']
            d['gold_y'] = d['y']

        sprite = pyglet.sprite.Sprite(
            animation,
            x=d['gold_x']-animation.get_max_width(),
            y=d['gold_y']-animation.get_max_height(),
            batch=batch, group=groups[4])
        sprite.scale = 2

    # Initialise the submit button.
    button_pads, scale = (200, 200), 0.3
    c = image_container
    paths = {
        ButtonWidget.ENABLED: c.joinpath('submit_enabled.png'),
        ButtonWidget.DISABLED: c.joinpath('submit_disabled.png'),
        ButtonWidget.SELECTED: c.joinpath('submit_selected.png'),
    }
    button = ButtonWidget(
        x=width-button_pads[0], y=height-button_pads[1], paths=paths,
        state=ButtonWidget.NA, scale=scale, batch=batch, group=groups[4])
    graphics.submit_button = button
    graphics.buttons['submit'] = button

    # Erase button.
    button_pads, scale = (200, height//2), 0.25
    paths = {
        ButtonWidget.ENABLED: c.joinpath('erase_enabled.png'),
        ButtonWidget.DISABLED: c.joinpath('erase_disabled.png'),
        ButtonWidget.SELECTED: c.joinpath('erase_selected.png'),
    }
    button = ButtonWidget(
        x=width-button_pads[0], y=height-button_pads[1], paths=paths,
        state=ButtonWidget.NA, scale=scale, batch=batch, group=groups[4])
    graphics.clear_button = button
    graphics.buttons['clear'] = button

    # Yes button.
    button_pads, scale = (290, 160), 0.3
    paths = {
        ButtonWidget.ENABLED: c.joinpath('check_enabled.png'),
        ButtonWidget.DISABLED: c.joinpath('check_disabled.png'),
        ButtonWidget.SELECTED: c.joinpath('check_selected.png'),
    }
    button = ButtonWidget(
        x=button_pads[0], y=button_pads[1], paths=paths,
        state=ButtonWidget.NA, scale=scale, batch=batch, group=groups[4])
    graphics.yes_button = button
    graphics.buttons['yes'] = button

    # No button.
    paths = {
        ButtonWidget.ENABLED: c.joinpath('cross_enabled.png'),
        ButtonWidget.DISABLED: c.joinpath('cross_disabled.png'),
        ButtonWidget.SELECTED: c.joinpath('cross_selected.png'),
    }
    button = ButtonWidget(
        x=width-button_pads[0], y=button_pads[1], paths=paths,
        state=ButtonWidget.NA, scale=scale, batch=batch, group=groups[4])
    graphics.no_button = button
    graphics.buttons['no'] = button

    return graphics


def create_edge_sprite(image,
                       ux, uy, vx, vy,
                       batch=None,
                       group=None,
                       visible=True):
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


def center_image(image):
    """Set an image's anchor point to its center."""
    image.anchor_x = image.width // 2
    image.anchor_y = image.height // 2

    return image


def read_image_from_reference(ref):
    """Read pyglet image from importlib reference."""
    with importlib_resources.as_file(ref) as file:
        return pyglet.image.load(file)


def slide_x(dt, sprite):
    if sprite.x > sprite.max_x:
        sprite.x = sprite.max_x
        sprite.dx = -sprite.dx
    elif sprite.x < sprite.min_x:
        sprite.x = sprite.min_x
        sprite.dx = -sprite.dx

    sprite.x += sprite.dx * dt
