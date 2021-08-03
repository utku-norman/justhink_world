import math
import pyglet

import importlib_resources

from .widgets import ButtonWidget

from ..domain.action import \
    PickAction, SuggestSubmitAction, SuggestPickAction, \
    AgreeAction, DisagreeAction, ClearAction
from ..tools.networks import in_edges, compute_selected_network_cost


def update_scene_buttons(scene):
    # Update submit button state.
    submit_suggested = hasattr(scene, '_submit_suggested') \
        and scene._submit_suggested
    if scene._terminal or submit_suggested:
        scene._submit_button.set_state('selected')
    else:
        scene._submit_button.set_state('enabled')

    # Update clear button state.
    if len(scene._edges) > 0:
        scene._erase_button.set_state('enabled')
    else:
        scene._erase_button.set_state('disabled')


def update_cost_label(graph, edges, label, highlight=False):
    if edges is not None:
        cost = compute_selected_network_cost(graph, edges)
    else:
        cost = 0
    label.text = 'Spent: {:2d} francs'.format(cost)
    if highlight:
        label.color = (255, 0, 0, 255)
        label.bold = True
    else:
        label.color = (0, 0, 0, 255)
        label.bold = False


def update_scene_paused(scene, paused):
    scene._paused = paused
    scene._paused_rect.visible = paused


def update_scene_press(scene, x, y, submit_action_type=SuggestSubmitAction):
    action = None
    if not scene._terminal and not scene._paused:
        action = check_buttons(
            scene, x, y, submit_action_type=submit_action_type)
        update_scene_drag(scene, x, y)
    return action


def check_buttons(scene, x, y, submit_action_type=SuggestPickAction):
    action = None
    if hasattr(scene, '_submit_button') \
        and scene._submit_button.state != 'disabled' \
            and scene._submit_button.check_hit(x, y):
        action = submit_action_type(agent_name='human')

    elif hasattr(scene, '_yes_button') \
        and scene._yes_button.state == 'enabled' \
            and scene._yes_button.check_hit(x, y):
        action = AgreeAction(agent_name='human')

    elif hasattr(scene, '_no_button') \
        and scene._no_button.state == 'enabled' \
            and scene._no_button.check_hit(x, y):
        action = DisagreeAction(agent_name='human')
        # scene._no_button.set_state('selected')

    return action


def update_scene_drag(scene, x, y, temp_suggested_image=None):
    if not scene._terminal:
        # # checking edges.
        # edge = check_edge_hit(scene._layout, x, y)
        # # Revert old selected.
        # if scene._selected_edge is not None:  # and edge is not None
        #     e = scene._layout.edges[scene._selected_edge]
        #     e['selected_sprite'].visible = False
        #     e['selectable_sprite'].visible = True

        # # Update new selected.
        # if edge is not None and edge not in scene._edges:
        #     scene._selected_edge = edge
        #     e = scene._layout.edges[edge]
        #     e['selected_sprite'].visible = True
        #     e['selectable_sprite'].visible = False
        #     e['added_sprite'].visible = False

        # Checking to draw from, if not already drawing.
        if scene.temp_from is None:
            node = check_node_hit(scene._layout, x, y)
            if node is not None:
                node_data = scene._layout.nodes[node]
                scene.temp_from = (node_data['x'], node_data['y'], node)
                node_data['added_sprite'].visible = True

        # check hover
        else:
            node = check_node_hit(scene._layout, x, y)
            selected = [u for e in scene._edges for u in e]

            if node is not None:
                # if hover a new node that is not already selected
                if node != scene.temp_from[2] and node not in selected:
                    scene._edges
                    scene.temp_to = node
                    node_data = scene._layout.nodes[node]
                    node_data['added_sprite'].visible = True

            # no longer hover a node
            else:
                # there is an old temp to and if not already selected
                if scene.temp_to is not None and scene.temp_to not in selected:
                    node_data = scene._layout.nodes[scene.temp_to]
                    node_data['added_sprite'].visible = False
                    scene.temp_to = None

        #     if scene.temp_to is None: # no highlighted nodes
        #         if node is not None: # hover a new node
        #             scene.temp_to = node
        #             node_data = scene._layout.nodes[node]
        #             node_data['added_sprite'].visible = True
        #     elif node is None: # no longer hover
        #         node_data = scene._layout.nodes[scene.temp_to]
        #         node_data['added_sprite'].visible = False
        #         scene.temp_to = None

        if temp_suggested_image is None:
            temp_suggested_image = scene.edge_suggested_image

        if scene.temp_from is not None:
            scene.temp_suggested_sprite = create_edge_sprite(
                temp_suggested_image,
                scene.temp_from[0], scene.temp_from[1],
                x, y)

        # if scene._submit_button.state == 'enabled' \
        #         and scene._submit_button.check_hit(x, y):
        #     scene._submit_button.set_state('selected')

        if scene._erase_button.state == 'enabled' \
                and scene._erase_button.check_hit(x, y):
            scene._erase_button.set_state('selected')
        elif scene._erase_button.state == 'selected' \
                and not scene._erase_button.check_hit(x, y):
            update_scene_buttons(scene)


def update_scene_release(scene, x, y, win, action_type=PickAction):
    action = None
    if not scene._terminal and not scene._paused:

        # # Apply action if release on edge.
        # edge = check_edge_hit(scene._layout, x, y)
        # if edge is not None:
        #     if edge not in scene._edges:
        #         e = scene._layout.edges[edge]
        #         if e['selected_sprite'].visible:
        #             # action = PickAction(edge, agent_name='human')
        #             if action_type == 'pick':
        #                 action = PickAction(edge, agent_name='human')
        #             elif action_type == 'suggest-pick':
        #                 action = SuggestPickAction(edge, agent_name='human')
        #             else:
        #                 print('Unknown action type')
        #             # print('Action:', action)
        #             win.execute_action_in_app(action)
        #     elif edge in scene._edges:
        #         action = UnpickAction(edge, agent_name='human')
        #         # , agent_name='human')
        #         win.execute_action_in_app(action)

        # Apply action if edge is drawn.
        if scene.temp_from is not None:
            # Drawing action.
            node = check_node_hit(scene._layout, x, y)
            if node is not None:
                from_node = scene.temp_from[2]
                edge = from_node, node
                is_added = in_edges(
                    edge[0], edge[1], scene._edges)
                has_edge = scene._layout.has_edge(*edge)

                if has_edge and (from_node != node) and not is_added:
                    # print(scene._layout.edges)
                    # print(edge)
                    # e = scene._layout.edges[edge]
                    # action = PickAction(edge, agent_name='human')
                    # if action_type == 'pick':
                    action = action_type(edge, agent_name='human')
                    # else:
                    # print('Unknown action type')
                    # print('Action:', action)
                    # win.execute_action_in_app(action)
                # elif edge in scene._edges:
        else:  # Edge not being drawn.
            # #### Disabling unpick action in favor of remove action.
            # # Check for erasing action.
            # edge = check_edge_hit(scene._layout, x, y)
            # if edge is not None:
            #     # e = scene._layout.edges[edge]
            #     if in_edges(edge[0], edge[1], scene._edges):
            #         # if e['selected_sprite'].visible:
            #         action = UnpickAction(edge, agent_name='human')
            #         # print('Action:', action)
            #         # win.execute_action_in_app(action)
            # enabled
            if scene._erase_button.state == 'selected' \
                    and scene._erase_button.check_hit(x, y):
                action = ClearAction(agent_name='human')
                scene._erase_button.set_state('disabled')

        # Clear selection.
        selected = [u for e in scene._edges for u in e]
        if scene.temp_from is not None and scene.temp_from[2] not in selected:
            # print("#########", scene.temp_from , selected)
            node_data = scene._layout.nodes[scene.temp_from[2]]
            node_data['added_sprite'].visible = False
            # node_data['sprite'].visible = True

        if scene.temp_to is not None and scene.temp_to not in selected:
            node_data = scene._layout.nodes[scene.temp_to]
            node_data['added_sprite'].visible = False
            scene.temp_to = None

        scene.temp_from = None
        scene.temp_suggested_sprite = None

        # # Clear selection.
        # if scene._selected_edge is not None:
        #     e = scene._layout.edges[scene._selected_edge]
        #     e['selected_sprite'].visible = False
        #     e['selectable_sprite'].visible = True
        # action = check_buttons(scene, x, y)

    return action


def update_scene_graph(scene, edges, terminal=None,
                       suggested=None, highlight=False):

    if terminal is not None:
        scene._terminal = terminal

    added_nodes = set()
    if edges is not None:
        scene._edges = edges

        for u, v, d in scene._layout.edges(data=True):
            is_added = in_edges(u, v, edges)
            is_suggested = (suggested == (u, v)) or (suggested == (v, u))
            d['added_sprite'].visible = is_added
            d['selectable_sprite'].visible = not is_added
            d['selected_sprite'].visible = False
            # if is_suggested:
            #     print('Suggested', suggested)
            d['suggested_sprite'].visible = is_suggested

            if is_added:
                added_nodes.update((u, v))

        for u, d in scene._layout.nodes(data=True):
            d['added_sprite'].visible = u in added_nodes
            # d['sprite'].visible = True # not u in added_nodes

    # Following are inefficient; to improve.
    # Process highlights for edges.
    for u, v, d in scene._layout.edges(data=True):
        if highlight:
            d['cost_label'].color = (255, 0, 0, 255)
            d['cost_label'].bold = True
        else:
            d['cost_label'].color = (0, 0, 0, 255)
            d['cost_label'].bold = False

    # Process highlights for nodes.
    for u, d in scene._layout.nodes(data=True):
        if highlight:
            d['label'].color = (255, 0, 0, 255)
            d['label'].bold = True
        else:
            d['label'].color = (0, 0, 0, 255)
            d['label'].bold = False

    update_scene_paused(scene, scene._terminal)


def read_image_from_reference(ref):
    """read pyglet image from importlib refernce"""
    with importlib_resources.as_file(ref) as file:
        return pyglet.image.load(file)


def init_graphics(layout, width, height, image_container,
                  batch=None,
                  show_edge_costs=True,
                  show_submit_button=True,
                  show_erase_button=True,
                  show_node_names=True,
                  show_yes_no_buttons=False):

    if batch is None:
        batch = pyglet.graphics.Batch()

    # higher the more foreground
    groups = [pyglet.graphics.OrderedGroup(i) for i in range(10)]

    graphics = dict()
    graphics['_selected_edge'] = None
    graphics['_paused'] = False

    # Cost label.
    label = pyglet.text.Label(
        '',
        x=20, y=height-290,  # -180,  # 120, 40
        anchor_y='center',
        color=(0, 0, 0, 255),
        font_name='Sans',
        # font_name='monospace',
        font_size=30,
        batch=batch)
    # label.font_size = 30  # 36
    graphics['_cost_label'] = label

    # Bottom label.
    label = pyglet.text.Label(
        '',
        x=width//2, y=20,  # 40,
        width=width, height=50,
        # color=(0, 0, 0, 255),
        color=(255, 255, 255, 255),
        anchor_x='center', anchor_y='center',
        font_name='monospace', font_size=24,  # 36,
        batch=batch, group=groups[8])
    # label.visible = False
    graphics['_status_label'] = label

    rect = pyglet.shapes.Rectangle(
        0, 0, width, 60,
        color=(0, 0, 0),
        batch=batch, group=groups[4])
    rect.opacity = 150
    rect.visible = False
    graphics['_status_rect'] = rect

    rect = pyglet.shapes.Rectangle(
        0, 0, width, height,
        color=(0, 0, 0),
        batch=batch, group=groups[5])
    rect.opacity = 100
    rect.visible = False  # True
    graphics['_paused_rect'] = rect

    # Create a background image sprite.
    key = 'background_image_file'
    if key in layout.graph:
        ref = image_container.joinpath(layout.graph[key])
        image = read_image_from_reference(ref)
        graphics['_bg_sprite'] = pyglet.sprite.Sprite(
            image, batch=batch, group=groups[0])

    # Create node images.
    for u, d in layout.nodes(data=True):
        ref = image_container.joinpath(d['image_file'])
        image = read_image_from_reference(ref)
        center_image(image)
        d['sprite'] = pyglet.sprite.Sprite(
            image, d['x'], d['y'],
            batch=batch, group=groups[2])

        ref = image_container.joinpath(d['higlight_image_file'])
        image = read_image_from_reference(ref)
        center_image(image)
        d['added_sprite'] = pyglet.sprite.Sprite(
            image, d['x'], d['y'],
            batch=batch, group=groups[3])
        d['added_sprite'].visible = False

    # Create edge images.
    ref = image_container.joinpath('railroad_added.png')
    edge_added_image = read_image_from_reference(ref)
    center_image(edge_added_image)
    graphics['edge_added_image'] = edge_added_image

    ref = image_container.joinpath('railroad_selected.png')
    edge_selected_image = read_image_from_reference(ref)
    center_image(edge_selected_image)
    # graphics['edge_selected_image'] = edge_selected_image

    ref = image_container.joinpath('railroad_selectable.png')
    edge_selectable_image = read_image_from_reference(ref)
    center_image(edge_selectable_image)
    # graphics['edge_selectable_image'] = edge_selectable_image

    ref = image_container.joinpath('railroad_suggested.png')
    edge_suggested_image = read_image_from_reference(ref)
    center_image(edge_suggested_image)
    graphics['edge_suggested_image'] = edge_suggested_image

    # s = create_edge_sprite(edge_suggested_image,
    #                        0, 0,
    #                        0, 0
    #                        batch=batch, group=groups[1],
    #                        visible=False)
    graphics['temp_suggested_sprite'] = None
    graphics['temp_from'] = None

    for u, v, d in layout.edges(data=True):
        u_node = layout.nodes[u]
        v_node = layout.nodes[v]

        s = create_edge_sprite(edge_selectable_image,
                               u_node['x'], u_node['y'],
                               v_node['x'], v_node['y'],
                               batch=batch, group=groups[1],
                               visible=True)
        d['selectable_sprite'] = s

        s = create_edge_sprite(edge_selected_image,
                               u_node['x'], u_node['y'],
                               v_node['x'], v_node['y'],
                               batch=batch, group=groups[1],
                               visible=False)
        d['selected_sprite'] = s

        s = create_edge_sprite(edge_added_image,
                               u_node['x'], u_node['y'],
                               v_node['x'], v_node['y'],
                               batch=batch, group=groups[1],
                               visible=False)
        d['added_sprite'] = s

        s = create_edge_sprite(edge_suggested_image,
                               u_node['x'], u_node['y'],
                               v_node['x'], v_node['y'],
                               batch=batch, group=groups[1],
                               visible=False)
        d['suggested_sprite'] = s

    # Create node labels.
    for u, d in layout.nodes(data=True):
        if 'label_x' in d and 'label_y' in d:
            x = d['label_x']
            y = d['label_y']
        else:  # default location
            x = d['x']
            y = d['y']  # - d['image'].height/ 2 - 5
        if show_node_names:
            text = d['text']
        else:
            text = ''
        d['label'] = pyglet.text.Label(text,
                                       x=x, y=y,
                                       font_name='Purisa',
                                       font_size=22, bold=False,
                                       anchor_x='center',
                                       anchor_y='center',
                                       color=(0, 0, 0, 255),
                                       batch=batch,
                                       group=groups[5])

    # Create edge labels.
    # if show_edge_costs:
    label_x_key = 'label_x'
    label_y_key = 'label_y'
    for u, v, d in layout.edges(data=True):
        u_node = layout.nodes[u]
        v_node = layout.nodes[v]
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
            font_name='Sans', font_size=29,  # bold=True, #26,
            anchor_x=anchor_x, anchor_y='bottom',
            color=(0, 0, 0, 255),
            x=d[label_x_key], y=d[label_y_key],
            batch=batch, group=groups[8])

    # Load gold image/gif.
    ref = image_container.joinpath('gold.gif')
    with ref as file:
        animation = pyglet.image.load_animation(str(file))
    gold_bin = pyglet.image.atlas.TextureBin()
    animation.add_to_texture_bin(gold_bin)

    # Set gold location if not available.
    for u, d in layout.nodes(data=True):
        if 'gold_x' not in d:  # or 'gold_y' not in d:
            d['gold_x'] = d['x']
            d['gold_y'] = d['y']
        s = pyglet.sprite.Sprite(
            img=animation,
            x=d['gold_x']-animation.get_max_width(),
            y=d['gold_y']-animation.get_max_height(),
            batch=batch, group=groups[4])
        s.scale = 2  # 2.5

    # Initialise the submit button.
    button_pads, scale = (200, 200), 0.3
    if show_submit_button:
        d = {
            'enabled': image_container.joinpath('submit_enabled.png'),
            'disabled': image_container.joinpath('submit_disabled.png'),
            'selected': image_container.joinpath('submit_selected.png'),
        }
        graphics['_submit_button'] = ButtonWidget(
            x=width-button_pads[0], y=height-button_pads[1],
            paths=d, state='disabled',
            scale=scale, batch=batch, group=groups[4])

    if show_erase_button:
        button_pads, scale = (200, height//2), 0.25
        d = {
            'enabled': image_container.joinpath('erase_enabled.png'),
            'disabled': image_container.joinpath('erase_disabled.png'),
            'selected': image_container.joinpath('erase_selected.png'),
        }
        graphics['_erase_button'] = ButtonWidget(
            x=width-button_pads[0], y=height-button_pads[1],
            paths=d, state='disabled',
            scale=scale, batch=batch, group=groups[4])

    # Yes button.
    button_pads, scale = (290, 160), 0.3
    if show_yes_no_buttons:
        d = {
            'enabled': image_container.joinpath('check_enabled.png'),
            'disabled': image_container.joinpath('check_disabled.png'),
            'selected': image_container.joinpath('check_selected.png'),
        }
        graphics['_yes_button'] = ButtonWidget(
            x=button_pads[0], y=button_pads[1],
            paths=d, state='disabled',
            scale=scale, batch=batch, group=groups[4])

        # No button.
        d = {
            'enabled': image_container.joinpath('cross_enabled.png'),
            'disabled': image_container.joinpath('cross_disabled.png'),
            'selected': image_container.joinpath('cross_selected.png'),
        }
        graphics['_no_button'] = ButtonWidget(
            x=width-button_pads[0], y=button_pads[1],
            paths=d, state='disabled',
            scale=scale, batch=batch, group=groups[4])

    # # Repeat button.
    # d = {
    #     'enabled': image_container.joinpath('repeat_enabled.png'),
    #     'disabled': image_container.joinpath('repeat_disabled.png'),
    #     'selected': image_container.joinpath('repeat_selected.png'),
    # }
    # scale = 0.1
    # graphics['_repeat_button'] = ButtonWidget(
    #     x=width-100, y=height-100,
    #     paths=d, state='disabled',
    #     scale=scale, batch=batch, group=groups[8])

    return batch, graphics


# def save_frame(window_name='window', frame_number=0,
#                x=0, y=0,
#                width=None, height=None,
#                target_dir=None):
#     file_num = str(frame_number).zfill(3)
#     # file_t=str(self.chrono)
#     # +file_num+'-@ '+file_t+'sec.png'
#     filename = '{}-frame-{}.png'.format(window_name, file_num)
#     image = pyglet.image.get_buffer_manager().get_color_buffer()
#     if width is not None:
#         image_part = image.get_region(x=x, y=y, width=width, height=height)
#     else:
#         image_part = image

#     if target_dir is not None:
#         filename = pl.Path(target_dir).joinpath(filename)

#     image_part.save(filename)
#     print('image file written {}, {}, {}, {}: {}'.format(
#         x, y, width, height, filename))


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


def center_image(image):
    """Sets an image's anchor point to its center"""
    image.anchor_x = image.width // 2
    image.anchor_y = image.height // 2


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


def create_edge_sprite(image,
                       ux, uy, vx, vy,
                       batch=None, group=None,
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
        # s.set_position((ux+vx)/2, (uy+vy)/2)

        return s
    else:
        return None


def draw_rect(x, y, width, height):
    pyglet.graphics.draw(4, pyglet.gl.GL_QUADS,
                         ('v2f', [x, y,
                                  x + width, y,
                                  x + width, y + height,
                                  x, y + height]))


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
    """ # from https://stackoverflow.com/a/1969274"""
    # Figure out how 'wide' each range is.
    left_span = left_max - left_min
    right_span = right_max - right_min

    # Convert the left range into a 0-1 range (float).
    value_scaled = float(value - left_min) / float(left_span)

    # Convert the 0-1 range into a value in the right range.
    return right_min + (value_scaled * right_span)


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


def is_between(x, a, b): return \
    a < sorted([a, b])[1] and a > sorted([a, b])[0]


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
