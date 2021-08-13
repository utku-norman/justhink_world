import copy
import math
import pyglet

import importlib_resources

from .widgets import ButtonWidget


class Graphics(object):
    """docstring for Graphics"""

    def __init__(self, from_graph, width, height, batch=None):
        self.layout = copy.deepcopy(from_graph)
        self.width = width
        self.height = height

        if batch is None:
            self.batch = pyglet.graphics.Batch()
        else:
            self.batch = batch


def init_graphics(graph, width, height, image_container,
                  batch=None,
                  show_edge_costs=True,
                  show_node_names=True):

    graphics = Graphics(graph, width, height, batch=batch)

    # Create groups: higher the order, the more the foreground.
    groups = [pyglet.graphics.OrderedGroup(i) for i in range(16)]

    # Attempt label.
    label = pyglet.text.Label(
        '',
        x=20, y=height-200,
        anchor_y='center',
        color=(0, 0, 0, 255),
        font_name='Sans',
        font_size=32,
        group=groups[5],
        batch=graphics.batch)
    graphics.attempt_label = label

    # Create confirm box components.
    label = pyglet.text.Label(
        '',
        x=width//2, y=height//2+180,
        width=width, height=50,
        color=(0, 0, 0, 255),
        anchor_x='center',
        anchor_y='center',
        font_name='Sans',
        font_size=48,
        batch=graphics.batch,
        group=groups[11])
    label.visible = False
    graphics.confirm_text_label = label

    label = pyglet.text.Label(
        '',
        x=width//2-180, y=height//2-20,
        width=width, height=50,
        color=(0, 0, 0, 255),
        anchor_x='center',
        anchor_y='center',
        font_name='Sans',
        font_size=56,
        batch=graphics.batch, group=groups[11])
    label.visible = False
    graphics.yes_label = label

    label = pyglet.text.Label(
        '',
        x=width//2+180, y=height//2-20,
        width=width, height=50,
        color=(0, 0, 0, 255),
        anchor_x='center',
        anchor_y='center',
        font_name='Sans',
        font_size=56,
        batch=graphics.batch,
        group=groups[11])
    label.visible = False
    graphics.no_label = label

    rect = pyglet.shapes.Rectangle(
        width//4, height//4 + 140,
        width//2, height//3,
        color=(225, 225, 225),
        batch=graphics.batch,
        group=groups[10])
    rect.opacity = 255
    rect.visible = False
    graphics.confirm_rect = rect

    # Cost label.
    label = pyglet.text.Label(
        '',
        x=20, y=height-290,
        anchor_y='center',
        color=(0, 0, 0, 255),
        font_name='Sans',
        font_size=32,
        batch=graphics.batch,
        group=groups[8])
    graphics.cost_label = label

    # Bottom label.
    label = pyglet.text.Label(
        '',
        x=width//2, y=20,
        width=width, height=60,
        color=(255, 255, 255, 255),
        anchor_x='center',
        anchor_y='center',
        font_name='monospace',
        font_size=24,
        batch=graphics.batch,
        group=groups[8])
    graphics.status_label = label

    rect = pyglet.shapes.Rectangle(
        0, 0, width, 60,
        color=(0, 0, 0),
        batch=graphics.batch,
        group=groups[5])
    rect.opacity = 150
    rect.visible = False
    graphics.status_rect = rect

    rect = pyglet.shapes.Rectangle(
        0, 0, width, height,
        color=(0, 0, 0),
        batch=graphics.batch,
        group=groups[14])
    rect.opacity = 100
    rect.visible = False
    graphics.paused_rect = rect

    rect = pyglet.shapes.Rectangle(
        0, 0, width, height,
        color=(0, 0, 0),
        batch=graphics.batch,
        group=groups[15])
    rect.opacity = 170
    rect.visible = False
    graphics.view_only_rect = rect

    # Create a background image sprite.
    key = 'background_image_file'
    if key in graphics.layout.graph:
        ref = image_container.joinpath(graphics.layout.graph[key])
        image = read_image_from_reference(ref)
        graphics.bg_sprite = pyglet.sprite.Sprite(
            image,
            batch=graphics.batch,
            group=groups[0])

    # Create node images.
    for u, d in graphics.layout.nodes(data=True):
        ref = image_container.joinpath(d['image_file'])
        image = read_image_from_reference(ref)
        center_image(image)
        d['sprite'] = pyglet.sprite.Sprite(
            image,
            d['x'],
            d['y'],
            batch=graphics.batch,
            group=groups[2])

        ref = image_container.joinpath(d['higlight_image_file'])
        image = read_image_from_reference(ref)
        center_image(image)
        d['added_sprite'] = pyglet.sprite.Sprite(
            image,
            d['x'],
            d['y'],
            batch=graphics.batch,
            group=groups[3])
        d['added_sprite'].visible = False

    # Create edge images.
    ref = image_container.joinpath('railroad_added.png')
    edge_added_image = read_image_from_reference(ref)
    center_image(edge_added_image)
    graphics.edge_added_image = edge_added_image

    ref = image_container.joinpath('railroad_selected.png')
    edge_selected_image = read_image_from_reference(ref)
    center_image(edge_selected_image)

    ref = image_container.joinpath('railroad_selectable.png')
    edge_selectable_image = read_image_from_reference(ref)
    center_image(edge_selectable_image)

    ref = image_container.joinpath('railroad_suggested.png')
    edge_suggested_image = read_image_from_reference(ref)
    center_image(edge_suggested_image)
    graphics.edge_suggested_image = edge_suggested_image

    # graphics['temp_suggested_sprite'] = None
    # graphics['temp_from'] = None

    for u, v, d in graphics.layout.edges(data=True):
        u_node = graphics.layout.nodes[u]
        v_node = graphics.layout.nodes[v]

        s = create_edge_sprite(edge_selectable_image,
                               u_node['x'],
                               u_node['y'],
                               v_node['x'],
                               v_node['y'],
                               batch=graphics.batch,
                               group=groups[1],
                               visible=True)
        d['selectable_sprite'] = s

        s = create_edge_sprite(edge_selected_image,
                               u_node['x'],
                               u_node['y'],
                               v_node['x'],
                               v_node['y'],
                               batch=graphics.batch,
                               group=groups[1],
                               visible=False)
        d['selected_sprite'] = s

        s = create_edge_sprite(edge_added_image,
                               u_node['x'],
                               u_node['y'],
                               v_node['x'],
                               v_node['y'],
                               batch=graphics.batch,
                               group=groups[1],
                               visible=False)
        d['added_sprite'] = s

        s = create_edge_sprite(edge_suggested_image,
                               u_node['x'],
                               u_node['y'],
                               v_node['x'],
                               v_node['y'],
                               batch=graphics.batch,
                               group=groups[1],
                               visible=False)
        d['suggested_sprite'] = s

    # Create node labels.
    for u, d in graphics.layout.nodes(data=True):
        if 'label_x' in d and 'label_y' in d:
            x = d['label_x']
            y = d['label_y']
        else:  # default location
            x = d['x']
            y = d['y']
        if show_node_names:
            text = d['text']
        else:
            text = ''
        d['label'] = pyglet.text.Label(text,
                                       x=x, y=y,
                                       font_name='Purisa',
                                       font_size=22,
                                       bold=False,
                                       anchor_x='center',
                                       anchor_y='center',
                                       color=(0, 0, 0, 255),
                                       batch=graphics.batch,
                                       group=groups[5])

    # Create edge labels.
    label_x_key, label_y_key = 'label_x', 'label_y'
    for u, v, d in graphics.layout.edges(data=True):
        u_node = graphics.layout.nodes[u]
        v_node = graphics.layout.nodes[v]
        ux, uy = u_node['x'], u_node['y']
        vx, vy = v_node['x'], v_node['y']
        d[label_x_key] = (ux + vx) / 2
        d[label_y_key] = (uy + vy) / 2
        slope = (uy - vy) / (ux - vx)
        if slope > 0:
            anchor_x = 'right'
            d[label_x_key] = d[label_x_key] - 5
        else:
            anchor_x = 'left'
            d[label_x_key] = d[label_x_key] + 5

        if show_edge_costs:
            text = str(d['cost'])
        else:
            text = ''
        d['cost_label'] = pyglet.text.Label(
            text,
            font_name='Sans',
            font_size=28,
            anchor_x=anchor_x,
            anchor_y='bottom',
            color=(0, 0, 0, 255),
            x=d[label_x_key],
            y=d[label_y_key],
            batch=graphics.batch,
            group=groups[8])

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
        s = pyglet.sprite.Sprite(
            img=animation,
            x=d['gold_x']-animation.get_max_width(),
            y=d['gold_y']-animation.get_max_height(),
            batch=graphics.batch,
            group=groups[4])
        s.scale = 2  # 2.5

    # Initialise the submit button.
    button_pads, scale = (200, 200), 0.3
    c = image_container
    paths = {
        ButtonWidget.ENABLED: c.joinpath('submit_enabled.png'),
        ButtonWidget.DISABLED: c.joinpath('submit_disabled.png'),
        ButtonWidget.SELECTED: c.joinpath('submit_selected.png'),
    }
    graphics.submit_button = ButtonWidget(
        x=width-button_pads[0],
        y=height-button_pads[1],
        paths=paths,
        state=ButtonWidget.NA,
        scale=scale,
        batch=graphics.batch,
        group=groups[4])

    # Erase button.
    button_pads, scale = (200, height//2), 0.25
    paths = {
        ButtonWidget.ENABLED: c.joinpath('erase_enabled.png'),
        ButtonWidget.DISABLED: c.joinpath('erase_disabled.png'),
        ButtonWidget.SELECTED: c.joinpath('erase_selected.png'),
    }
    graphics.clear_button = ButtonWidget(
        x=width-button_pads[0],
        y=height-button_pads[1],
        paths=paths,
        state=ButtonWidget.NA,
        scale=scale,
        batch=graphics.batch,
        group=groups[4])

    # Yes button.
    button_pads, scale = (290, 160), 0.3
    paths = {
        ButtonWidget.ENABLED: c.joinpath('check_enabled.png'),
        ButtonWidget.DISABLED: c.joinpath('check_disabled.png'),
        ButtonWidget.SELECTED: c.joinpath('check_selected.png'),
    }
    graphics.yes_button = ButtonWidget(
        x=button_pads[0],
        y=button_pads[1],
        paths=paths,
        state=ButtonWidget.NA,
        scale=scale,
        batch=graphics.batch,
        group=groups[4])

    # No button.
    d = {
        ButtonWidget.ENABLED: c.joinpath('cross_enabled.png'),
        ButtonWidget.DISABLED: c.joinpath('cross_disabled.png'),
        ButtonWidget.SELECTED: c.joinpath('cross_selected.png'),
    }
    graphics.no_button = ButtonWidget(
        x=width-button_pads[0],
        y=button_pads[1],
        paths=d,
        state=ButtonWidget.NA,
        scale=scale,
        batch=graphics.batch,
        group=groups[4])

    return graphics


def create_edge_sprite(image,
                       ux, uy,
                       vx, vy,
                       batch=None,
                       group=None,
                       visible=True):
    dist = math.sqrt((ux-vx)**2 + (uy-vy)**2)
    w = int(math.floor(dist))
    image_part = image.get_region(
        x=0, y=0, width=w, height=image.height)
    if image_part.width > 0 and image_part.height > 0:
        center_image(image_part)
        s = pyglet.sprite.Sprite(
            image_part, x=(ux+vx)/2, y=(uy+vy)/2,
            batch=batch, group=group)
        s.rotation = -math.degrees(math.atan2(uy-vy, ux-vx))
        s.visible = visible

        return s
    else:
        return None


def center_image(image):
    """Set an image's anchor point to its center."""
    image.anchor_x = image.width // 2
    image.anchor_y = image.height // 2


def read_image_from_reference(ref):
    """Read pyglet image from importlib reference."""
    with importlib_resources.as_file(ref) as file:
        return pyglet.image.load(file)
