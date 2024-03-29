import importlib_resources
import pyglet

from justhink_world.tools.read import load_image_from_reference
from justhink_world.tools.graphics import Graphics, center_image, slide_x, \
    BLACK, WHITEA, BLACKA, ButtonWidget, Scene, create_edge_sprite, DialogBox


class EnvironmentScene(Scene):
    def __init__(self, state, name='EnvScene', width=1920, height=1080):
        super().__init__(name=name, width=width, height=height)
        self.state = state

        # Create a container for the image resources.
        image_source = importlib_resources.files(
            'justhink_world.resources.images')

        # Create the graphics.
        self._init_graphics(state.network.graph, width, height, image_source)

    def on_draw(self):
        self.graphics.batch.draw()

    @property
    def state(self):
        return self._state

    @state.setter
    def state(self, value):
        self._state = value

    def on_update(self):
        # Update the selected edges.
        for u, v, d in self.graphics.layout.edges(data=True):
            is_selected = self.state.network.subgraph.has_edge(u, v)
            e = self.state.network.suggested_edge
            is_suggested = (e == (u, v)) or (e == (v, u))
            d['selectable_sprite'].visible = not is_selected
            d['selected_sprite'].visible = is_selected
            d['suggested_sprite'].visible = is_suggested

        # Update the selected nodes.
        selected_nodes = self.state.network.get_selected_nodes()
        for u, d in self.graphics.layout.nodes(data=True):
            d['selected_sprite'].visible = u in selected_nodes

        # Process highlight for edges.
        for u, v, d in self.graphics.layout.edges(data=True):
            if self.state.is_highlighted:
                color = (255, 0, 0, 255)
                bold = True
            else:
                color = (0, 0, 0, 255)
                bold = False
            d['cost_label'].color = color
            d['cost_label'].bold = bold

        # Process highlight for nodes.
        for u, d in self.graphics.layout.nodes(data=True):
            if self.state.is_highlighted:
                color = (255, 0, 0, 255)
                bold = True
            else:
                color = (0, 0, 0, 255)
                bold = False
            d['label'].color = color
            d['label'].bold = bold

        # Update the pausedness.
        self._update_paused()

        # Update the cost label.
        self._update_cost_label()

        # Update the attempt label.
        self._update_attempt_label()

        # Show or hide the confirm box.
        self.submit_box.visible = self._state.is_submitting

    def _update_cost_label(self):
        cost = self.state.network.get_cost()
        self.graphics.cost_label.text = 'Spent: {:2d} franc{}'.format(
            cost, 's' if cost != 1 else '')

        if self.state.is_highlighted:
            self.graphics.cost_label.color = (255, 0, 0, 255)
            self.graphics.cost_label.bold = True
        else:
            self.graphics.cost_label.color = (0, 0, 0, 255)
            self.graphics.cost_label.bold = False

    def _update_attempt_label(self):
        state = self._state
        if state.max_attempts is not None:
            s = 'Attempt: {}/{}'.format(state.attempt_no, state.max_attempts)
            self.graphics.attempt_label.text = s

    def _update_paused(self):
        self._set_paused(self._state.is_terminal)

    def _set_paused(self, is_paused):
        self.graphics.paused_rect.visible = is_paused

    def _init_graphics(
            self, graph, width, height, image_source, batch=None):
        graphics = Graphics(width, height, from_graph=graph, batch=batch)
        batch = graphics.batch

        # Create groups: higher the order, the more the foreground.
        groups = [pyglet.graphics.OrderedGroup(i) for i in range(16)]

        self.submit_box = DialogBox(
            main_text=('Did you connect all of the mines'
                       '\nto each other by some path,'
                       '\nand spend as little as possible,'
                       '\nat the same time?'),
            yes_text='Yes', no_text='No', height_scaler=1/2,
            main_fontsize=36, response_fontsize=56,
            width=width, height=height, batch=batch)

        # Load a cloud.
        ref = image_source.joinpath('cloud.png')
        image = load_image_from_reference(ref)
        s = pyglet.sprite.Sprite(image, batch=batch, group=groups[6])
        s.scale = 0.2
        s.dx = 20.0
        s.position = (220, height-150)
        s.min_x = 50
        s.max_x = 400
        graphics.cloud_sprite = s
        pyglet.clock.schedule_interval(slide_x, 1.0/60, graphics.cloud_sprite)

        # Cross sprite.
        ref = image_source.joinpath('cross.png')
        image = center_image(load_image_from_reference(ref))
        s = pyglet.sprite.Sprite(image, group=groups[12])
        s.scale = 0.5
        graphics.cross_sprite = s

        # Attempt label.
        graphics.attempt_label = pyglet.text.Label(
            '', x=20, y=height-280, anchor_y='center', color=BLACKA,
            font_name='Sans', font_size=32, group=groups[5], batch=batch)

        # Cost label.
        graphics.cost_label = pyglet.text.Label(
            '', x=20, y=height-340, anchor_y='center', color=BLACKA,
            font_name='Sans', font_size=32, batch=batch, group=groups[8])

        # Bottom label.
        graphics.status_label = pyglet.text.Label(
            '', x=width//2, y=20, anchor_x='center', color=WHITEA,
            font_name='Sans', font_size=24, batch=batch, group=groups[8])

        graphics.status_rect = pyglet.shapes.Rectangle(
            0, 0, width, 60, color=BLACK, batch=batch, group=groups[5])
        graphics.status_rect.opacity = 150
        graphics.status_rect.visible = False

        graphics.paused_rect = pyglet.shapes.Rectangle(
            0, 0, width, height, color=BLACK, batch=batch, group=groups[14])
        graphics.paused_rect.opacity = 100
        graphics.paused_rect.visible = False

        graphics.observe_rect = pyglet.shapes.Rectangle(
            0, 0, width, height, color=BLACK, batch=batch, group=groups[15])
        graphics.observe_rect.opacity = 170
        graphics.observe_rect.visible = False

        # Create a background image sprite.
        key = 'background_image_file'
        if key in graphics.layout.graph:
            ref = image_source.joinpath(graphics.layout.graph[key])
            image = load_image_from_reference(ref)
            graphics.bg_sprite = pyglet.sprite.Sprite(
                image, batch=batch, group=groups[0])

        # Create node images.
        for u, d in graphics.layout.nodes(data=True):
            # Main/default image.
            ref = image_source.joinpath(d['image_file'])
            image = center_image(load_image_from_reference(ref))
            d['sprite'] = pyglet.sprite.Sprite(
                image, d['x'], d['y'], batch=batch, group=groups[2])
            # Selected image.
            ref = image_source.joinpath(d['higlight_image_file'])
            image = center_image(load_image_from_reference(ref))
            d['selected_sprite'] = pyglet.sprite.Sprite(
                image, d['x'], d['y'], batch=batch, group=groups[3])
            d['selected_sprite'].visible = False
            # Highlighted image.
            # Quick fix not to query for the json, but construct immediately.
            file = d['higlight_image_file'].replace('selected', 'highlighted')
            ref = image_source.joinpath(file)
            image = center_image(load_image_from_reference(ref))
            d['highlighted_sprite'] = pyglet.sprite.Sprite(
                image, d['x'], d['y'], batch=batch, group=groups[4])
            d['highlighted_sprite'].visible = False

        # Create edge images.
        ref = image_source.joinpath('railroad_selected.png')
        edge_selected_image = center_image(load_image_from_reference(ref))
        graphics.edge_selected_image = edge_selected_image

        ref = image_source.joinpath('railroad_selected.png')
        edge_selected_image = center_image(load_image_from_reference(ref))

        ref = image_source.joinpath('railroad_selectable.png')
        selectable_sprite_image = center_image(load_image_from_reference(ref))

        ref = image_source.joinpath('railroad_suggested.png')
        edge_suggested_image = center_image(load_image_from_reference(ref))
        graphics.edge_suggested_image = edge_suggested_image

        for u, v, d in graphics.layout.edges(data=True):
            ud = graphics.layout.nodes[u]
            vd = graphics.layout.nodes[v]

            d['selectable_sprite'] = create_edge_sprite(
                selectable_sprite_image, ud['x'], ud['y'], vd['x'], vd['y'],
                batch=batch, group=groups[1], visible=True)

            d['selected_sprite'] = create_edge_sprite(
                edge_selected_image, ud['x'], ud['y'], vd['x'], vd['y'],
                batch=batch, group=groups[1], visible=False)

            d['selected_sprite'] = create_edge_sprite(
                edge_selected_image, ud['x'], ud['y'], vd['x'], vd['y'],
                batch=batch, group=groups[1], visible=False)

            d['suggested_sprite'] = create_edge_sprite(
                edge_suggested_image, ud['x'], ud['y'], vd['x'], vd['y'],
                batch=batch, group=groups[1], visible=False)

        # Create node labels.
        for u, d in graphics.layout.nodes(data=True):
            if 'label_x' in d and 'label_y' in d:
                x, y = d['label_x'], d['label_y']
            else:  # Default location is on the node image.
                x, y = d['x'], d['y']
            d['label'] = pyglet.text.Label(
                str(d['text']), x=x, y=y, font_name='Purisa', font_size=22,
                anchor_x='center', anchor_y='center', color=BLACKA,
                batch=batch, group=groups[5])

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

            d['cost_label'] = pyglet.text.Label(
                str(d['cost']), x=d[x_key], y=d[y_key], font_name='Sans',
                font_size=28, anchor_x=anchor_x, anchor_y='bottom',
                color=BLACKA, batch=batch, group=groups[8])

        # Load gold image/gif.
        ref = image_source.joinpath('gold.gif')
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
                animation, batch=batch, group=groups[5],
                x=d['gold_x']-animation.get_max_width(),
                y=d['gold_y']-animation.get_max_height())
            sprite.scale = 2

        # Initialize the submit button.
        button_pads, scale = (200, 180), 0.3
        c = image_source
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
        button_pads, scale = (300, 170), 0.3
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

        self.graphics = graphics


class EnvironmentWindow(pyglet.window.Window):
    def __init__(self, state, width=1920, height=1080, screen_index=0):
        self.scene = EnvironmentScene(state=state, width=width, height=height)

        style = pyglet.window.Window.WINDOW_STYLE_BORDERLESS
        super().__init__(width, height, style=style)

        self.register_event_type('on_update')
        self.set_handlers(self.scene.on_update)

        # Move the window to a screen.
        active_screen = pyglet.canvas.get_display().get_screens()[screen_index]
        self.set_location(active_screen.x, active_screen.y)

        self.dispatch_event('on_update')

    def __str__(self):
        return self.__repr__()

    def __repr__(self):
        return 'EnvironmentWindow({},w={},h={})'.format(
            self.scene.state, self.width, self.height)

    def on_draw(self):
        self.scene.on_draw()

    def on_mouse_press(self, x, y, button, modifiers):
        self.scene.on_mouse_press(x, y, button, modifiers, win=self)

    def on_mouse_drag(self, x, y, dx, dy, buttons, modifiers):
        self.scene.on_mouse_drag(x, y, dx, dy, buttons, modifiers, win=self)

    def on_mouse_release(self, x, y, button, modifiers):
        self.scene.on_mouse_release(x, y, button, modifiers, win=self)


def show_state(state):
    window = EnvironmentWindow(state)

    # Enter the main event loop.
    try:
        pyglet.app.run()
    except KeyboardInterrupt:
        window.close()
        print('Window is closed.')
