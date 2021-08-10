import math
# import pyglet


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
