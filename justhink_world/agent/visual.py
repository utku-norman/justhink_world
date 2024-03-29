import pyglet
from pyglet.window import key

import networkx as nx

from justhink_world.tools.graphics import Scene, Graphics, Surface, \
    crop_edge, create_ellipse, transform_position, \
    WHITE, WHITEA, BLACK


def show_mind(world):
    window = MentalWindow(world)

    # Enter the main event loop.
    try:
        pyglet.app.run()
    except KeyboardInterrupt:
        window.close()
        print('Window is closed.')


class MentalWindow(pyglet.window.Window):
    """A class to manage the window that visualizes agent's mental model."""

    def __init__(self, world, caption="Robot's Mind", width=1920, height=1080,
                 offset=(1920, 0), screen_index=0, max_level=2):

        self.scene = MentalScene(
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


class MentalScene(Scene):
    """A class to visualize the mental model of the agent."""
    def __init__(self, world, width, height, max_level=2):

        super().__init__(world.name, width, height)

        # Create the graphics.
        self.state = world.agent.cur_state
        self._init_graphics(
            world.env.state.network.graph, width, height, max_level=max_level)

    # GUI methods.

    def on_draw(self):
        self.graphics.batch.draw()

    def on_key_press(self, symbol, modifiers):
        if symbol == key.ESCAPE:
            self.close()

    # Custom public methods.

    def on_update(self):
        self._update_graphs()

        # Update the current node belief.
        cur_node = self.state.cur_node
        if cur_node is not None:
            for u, d in self.graphics.layout.nodes(data=True):
                if u == cur_node:
                    color = (255, 255, 0, 255)
                    is_bold = True
                else:
                    color = (255, 255, 255, 255)
                    is_bold = False
                d[0]['label'].color = color
                d[0]['label'].bold = is_bold

    # Private methods.

    def _update_graphs(self):
        # Update the choice beliefs.
        for level in range(0, 3):
            if level == 0:
                beliefs = self.state.beliefs['me']
            elif level == 1:
                beliefs = self.state.beliefs['me']['you']
            elif level == 2:
                beliefs = self.state.beliefs['me']['you']['me']

            for u, v, d in self.graphics.layout.edges(data=True):
                p = beliefs['world'][u][v]['is_optimal']
                s = '{:.1f}'.format(p) if p is not None else '?'
                d[level]['label'].text = s

                # Update is suggested or not.
                d[level]['suggested_sprite'].visible = \
                    beliefs['world'][u][v]['is_suggested']

                # Update is selected or not.
                d[level]['selected_sprite'].visible = \
                    beliefs['world'][u][v]['is_selected']

    def _init_graphics(self, graph, width, height, max_level, batch=None):
        font_size = 20
        graphics = Graphics(width, height, from_graph=graph, batch=batch)
        batch = graphics.batch

        groups = [pyglet.graphics.OrderedGroup(i) for i in range(10)]

        outer_pad = (50, 50, 60, 60)  # left, right, top, bottom

        # Next action if any label.
        graphics.next_label = pyglet.text.Label(
            '', x=width//2, y=height-20, anchor_y='center', color=WHITEA,
            font_name='Sans', font_size=font_size, batch=batch)

        # Previous action if any label.
        graphics.prev_label = pyglet.text.Label(
            '', x=outer_pad[0], y=height-20, anchor_y='center', color=WHITEA,
            font_name='Sans', font_size=font_size, batch=batch)

        # Active area
        width = graphics.width - (outer_pad[0] + outer_pad[1])
        height = graphics.height - (outer_pad[2] + outer_pad[3])

        # Find min max of the graph.
        layout = graphics.layout
        xs = list(nx.get_node_attributes(layout, 'x').values())
        layout.graph['min_x'] = min(xs)
        layout.graph['max_x'] = max(xs)

        ys = list(nx.get_node_attributes(layout, 'y').values())
        layout.graph['min_y'] = min(ys)
        layout.graph['max_y'] = max(ys)

        # Construct a fitted surface.
        fitted_surface = Surface(
            layout.graph['max_x']-layout.graph['min_x'],
            layout.graph['max_y']-layout.graph['min_y'],
            layout.graph['min_x'], layout.graph['min_y'])
        graphics.surface = fitted_surface

        # Construct a fitted surface.
        graphics.surfaces = dict()
        graphics.rects = dict()  # So that they are not garbage collected.
        graphics.labels = dict()

        # Initialize "does" texts.
        x_pad, y_pad = (300, 60)
        y = graphics.height - outer_pad[2] - 3 * y_pad
        graphics.observes_heading_label = pyglet.text.Label(
            '(robot observes)', x=outer_pad[0], y=y, font_name='Sans',
            font_size=font_size, batch=batch)
        graphics.observes_label = pyglet.text.Label(
            '', x=outer_pad[0]+x_pad, y=y, align='center', font_name='Sans',
            font_size=font_size, batch=batch)

        # Initialize "thinks" texts.
        y = graphics.height - outer_pad[2] - 5 * y_pad
        graphics.thinks_heading_label = pyglet.text.Label(
            '(robot believes)', x=outer_pad[0], y=y, font_name='Sans',
            font_size=font_size, batch=batch, group=groups[5])
        graphics.thinks_label = pyglet.text.Label(
            '', x=outer_pad[0]+x_pad, y=y, font_name='Sans', align='center',
            font_size=font_size, batch=batch, group=groups[1])

        # Create level rectangles and labels.
        level = 0
        p = 30  # 45
        rect = pyglet.shapes.BorderedRectangle(
            x=outer_pad[0]-p, y=outer_pad[3]-p, width=width+1.8*p,
            height=height-4*y_pad+2*p, border=10, color=BLACK,
            border_color=(100, 100, 100), batch=batch, group=groups[0])

        x = outer_pad[0]+(level)*(width//3)+width//6
        y = rect.height + rect.y - 3 * y_pad
        label = pyglet.text.Label(
            'L0: world facts', x=x, y=y, font_name='Sans', font_size=font_size,
            bold=True, anchor_x='center', anchor_y='bottom',
            batch=batch, group=groups[1])
        graphics.rects[level] = rect
        graphics.labels[level] = label

        level = 1
        x = outer_pad[0]+width//3-p
        rect = pyglet.shapes.BorderedRectangle(
            x=x, y=outer_pad[3]-p, width=2*width//3+1.8*p,
            height=height-5*y_pad+2*p, border=10, color=BLACK,
            border_color=(100, 100, 100), batch=batch, group=groups[0])

        x = outer_pad[0]+(level)*(width//3)+width//6
        label = pyglet.text.Label(
            'L1: about the other', x=x, y=y, font_name='Sans', bold=True,
            font_size=font_size, anchor_x='center', anchor_y='bottom',
            batch=batch, group=groups[1])
        graphics.rects[level] = rect
        graphics.labels[level] = label

        level = 2
        if level <= max_level:
            x = outer_pad[0]+2*width//3-p
            rect = pyglet.shapes.BorderedRectangle(
                x=x, y=outer_pad[3]-p, width=width//3+1.8*p,
                height=height-6*y_pad+2*p, border=10, color=BLACK,
                border_color=(100, 100, 100), batch=batch, group=groups[0])

            x = outer_pad[0]+(level)*(width//3)+width//6
            label = pyglet.text.Label(
                'L2: about the self-by-other', x=x, y=y, font_name='Sans',
                font_size=font_size, bold=True, anchor_x='center',
                anchor_y='bottom',  batch=batch, group=groups[1])
            graphics.rects[level] = rect
            graphics.labels[level] = label

        pad = (30, 100, 60, 60)  # left, right, top, bottom

        for level in range(0, max_level+1):  # for each level
            d = dict()

            # Initialize choice surface.
            context = 'choice'
            s = Surface(
                width//3, height//2, x=outer_pad[0]+level*(width//3),
                y=outer_pad[1], pad=pad)
            create_network_graphics(
                graphics.layout, s, graphics.surface, key=level,
                edge_font_size=18, scale=2.3, batch=batch)
            d[context] = s

            # Set as the panels of the current level.
            graphics.surfaces[key] = d

        self.graphics = graphics


def create_network_graphics(
        layout, surface, from_surface, key, rx=55, ry=25,
        node_font_size=14, edge_font_size=32, scale=1.3,
        label_func=lambda d: '?', batch=None):
    groups = [pyglet.graphics.OrderedGroup(i) for i in range(10)]

    def transform_func(x, y): return \
        transform_position(x, y, from_surface, surface)

    # Create node graphics.
    for u, d in layout.nodes(data=True):
        if key not in d:
            d[key] = dict()
        x, y = transform_func(d['x'], d['y'])

        # Create node name label.
        text = d['text'].split()[-1]
        d[key]['label'] = create_node_label(
            x, y, text, font_size=node_font_size, batch=batch, group=groups[2])

        # Create node border.
        d[key]['border'] = create_node_border(
            x, y, rx=rx, ry=ry, batch=batch, group=groups[2])

    # Create edge graphics.
    for u, v, d in layout.edges(data=True):
        if key not in d:
            d[key] = dict()
        u_node = layout.nodes[u]
        v_node = layout.nodes[v]

        ux, uy = transform_func(u_node['x'], u_node['y'])
        vx, vy = transform_func(v_node['x'], v_node['y'])

        d[key]['selectable_sprite'] = create_edge(
            ux, uy, vx, vy, width=3, opacity=128, rx=rx, ry=ry, batch=batch,
            group=groups[1])

        d[key]['selected_sprite'] = create_edge(
            ux, uy, vx, vy, width=42, visible=False, rx=rx, ry=ry, batch=batch,
            group=groups[1])

        d[key]['suggested_sprite'] = create_edge(
            ux, uy, vx, vy, width=16, visible=False, rx=rx, ry=ry, batch=batch,
            color=(255, 0, 0), group=groups[1])

        # Create edge data label.
        text = label_func(d)
        rect, label = create_label(
            ux, uy, vx, vy, text, font_size=edge_font_size,
            scale=scale, batch=batch, groups=[groups[5], groups[6]])
        d[key]['label_background'] = rect
        d[key]['label'] = label


def create_edge(
        ux, uy, vx, vy, rx=0, ry=0, width=1, visible=True,
        color=WHITE, opacity=255,
        batch=None, group=None):
    ux_new, uy_new, vx_new, vy_new = crop_edge(ux, uy, vx, vy, rx, ry)

    line = pyglet.shapes.Line(
        ux_new, uy_new, vx_new, vy_new, color=color, width=width, batch=batch,
        group=group)
    line.opacity = opacity
    line.visible = visible

    return line


def create_label(
        ux, uy, vx, vy, text='?', font_size=26, scale=1.3, batch=None,
        groups=[None, None]):
    x = (ux + vx) // 2
    y = (uy + vy) // 2
    anchor_x = 'center'
    anchor_y = 'center'
    s = scale
    width, height = s*font_size, s*font_size
    rect = pyglet.shapes.Rectangle(x-width//2, y-height//2,
                                   width, height,
                                   color=(0, 0, 0),
                                   batch=batch,
                                   group=groups[0])

    label = pyglet.text.Label(
        str(text), x=x, y=y, font_name='Sans', font_size=font_size,
        anchor_x=anchor_x, anchor_y=anchor_y, color=WHITEA, batch=batch,
        group=groups[1])

    return rect, label


def create_node_label(
        x, y, text, font_size=14, color=WHITEA, batch=None, group=None):
    return pyglet.text.Label(
        text, x=x, y=y, font_name='Sans', color=color,  font_size=font_size,
        anchor_x='center', anchor_y='center', batch=batch, group=group)


def create_node_border(
        x, y, rx=55, ry=25, n_points=400, batch=None, group=None):
    return create_ellipse(x, y, rx=rx, ry=ry, n_points=n_points, batch=batch)


def make_strategy_text(p, agent='self'):
    p_text = '{:1.1f}'.format(p) if p is not None else 'NotImpl.'
    return 'P_{} = {}'.format(agent, p_text)
