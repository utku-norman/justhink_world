# ----------------------------------------------------------------------------
# pyglet
# Copyright (c) 2006-2008 Alex Holkner
# Copyright (c) 2008-2021 pyglet contributors
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions
# are met:
#
#  * Redistributions of source code must retain the above copyright
#    notice, this list of conditions and the following disclaimer.
#  * Redistributions in binary form must reproduce the above copyright
#    notice, this list of conditions and the following disclaimer in
#    the documentation and/or other materials provided with the
#    distribution.
#  * Neither the name of pyglet nor the names of its
#    contributors may be used to endorse or promote products
#    derived from this software without specific prior written
#    permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
# "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
# LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS
# FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE
# COPYRIGHT OWNER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT,
# INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING,
# BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
# LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER
# CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT
# LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN
# ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
# POSSIBILITY OF SUCH DAMAGE.
# ----------------------------------------------------------------------------

"""2D shapes.

This module provides classes for a variety of simplistic 2D shapes,
such as Rectangles, Circles, and Lines. These shapes are made
internally from OpenGL primitives, and provide excellent performance
when drawn as part of a :py:class:`~pyglet.graphics.Batch`.
Convenience methods are provided for positioning, changing color
and opacity, and rotation (where applicable). To create more
complex shapes than what is provided here, the lower level
graphics API is more appropriate.
See the :ref:`guide_graphics` for more details.

A simple example of drawing shapes::

    import pyglet
    from pyglet import shapes

    window = pyglet.window.Window(960, 540)
    batch = pyglet.graphics.Batch()

    circle = shapes.Circle(700, 150, 100, color=(50, 225, 30), batch=batch)
    square = shapes.Rectangle(200, 200, 200, 200, color=(55, 55, 255), batch=batch)
    rectangle = shapes.Rectangle(250, 300, 400, 200, color=(255, 22, 20), batch=batch)
    rectangle.opacity = 128
    rectangle.rotation = 33
    line = shapes.Line(100, 100, 100, 200, width=19, batch=batch)
    line2 = shapes.Line(150, 150, 444, 111, width=4, color=(200, 20, 20), batch=batch)
    star = shapes.Star(800, 400, 60, 40, num_spikes=20, color=(255, 255, 0), batch=batch)

    @window.event
    def on_draw():
        window.clear()
        batch.draw()

    pyglet.app.run()



.. versionadded:: 1.5.4
"""

import math

from pyglet.gl import GL_COLOR_BUFFER_BIT, GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA
from pyglet.gl import GL_TRIANGLES, GL_LINES, GL_BLEND
from pyglet.gl import glPushAttrib, glPopAttrib, glBlendFunc, glEnable, glDisable
from pyglet.graphics import Group, Batch


class _ShapeGroup(Group):
    """Shared Shape rendering Group.

    The group is automatically coalesced with other shape groups
    sharing the same parent group and blend parameters.
    """

    def __init__(self, blend_src, blend_dest, parent=None):
        """Create a Shape group.

        The group is created internally. Usually you do not
        need to explicitly create it.

        :Parameters:
            `blend_src` : int
                OpenGL blend source mode; for example,
                ``GL_SRC_ALPHA``.
            `blend_dest` : int
                OpenGL blend destination mode; for example,
                ``GL_ONE_MINUS_SRC_ALPHA``.
            `parent` : `~pyglet.graphics.Group`
                Optional parent group.
        """
        super(_ShapeGroup, self).__init__(parent)
        self.blend_src = blend_src
        self.blend_dest = blend_dest

    def set_state(self):
        glPushAttrib(GL_COLOR_BUFFER_BIT)
        glEnable(GL_BLEND)
        glBlendFunc(self.blend_src, self.blend_dest)

    def unset_state(self):
        glDisable(GL_BLEND)
        glPopAttrib()

    def __eq__(self, other):
        return (other.__class__ is self.__class__ and
                self.parent is other.parent and
                self.blend_src == other.blend_src and
                self.blend_dest == other.blend_dest)

    def __hash__(self):
        return hash((id(self.parent), self.blend_src, self.blend_dest))


class _ShapeBase:
    """Base class for Shape objects"""

    _rgb = (255, 255, 255)
    _opacity = 255
    _visible = True
    _x = 0
    _y = 0
    _anchor_x = 0
    _anchor_y = 0
    _batch = None
    _group = None
    _vertex_list = None

    def __del__(self):
        if self._vertex_list is not None:
            self._vertex_list.delete()

    def _update_position(self):
        raise NotImplementedError

    def _update_color(self):
        raise NotImplementedError

    def draw(self):
        """Draw the shape at its current position.

        Using this method is not recommended. Instead, add the
        shape to a `pyglet.graphics.Batch` for efficient rendering.
        """
        self._group.set_state_recursive()
        self._vertex_list.draw(GL_TRIANGLES)
        self._group.unset_state_recursive()

    def delete(self):
        self._vertex_list.delete()
        self._vertex_list = None

    @property
    def x(self):
        """X coordinate of the shape.

        :type: int or float
        """
        return self._x

    @x.setter
    def x(self, value):
        self._x = value
        self._update_position()

    @property
    def y(self):
        """Y coordinate of the shape.

        :type: int or float
        """
        return self._y

    @y.setter
    def y(self, value):
        self._y = value
        self._update_position()

    @property
    def position(self):
        """The (x, y) coordinates of the shape, as a tuple.

        :Parameters:
            `x` : int or float
                X coordinate of the sprite.
            `y` : int or float
                Y coordinate of the sprite.
        """
        return self._x, self._y

    @position.setter
    def position(self, values):
        self._x, self._y = values
        self._update_position()

    @property
    def anchor_x(self):
        """The X coordinate of the anchor point

        :type: int or float
        """
        return self._anchor_x

    @anchor_x.setter
    def anchor_x(self, value):
        self._anchor_x = value
        self._update_position()

    @property
    def anchor_y(self):
        """The Y coordinate of the anchor point

        :type: int or float
        """
        return self._anchor_y

    @anchor_y.setter
    def anchor_y(self, value):
        self._anchor_y = value
        self._update_position()

    @property
    def anchor_position(self):
        """The (x, y) coordinates of the anchor point, as a tuple.

        :Parameters:
            `x` : int or float
                X coordinate of the anchor point.
            `y` : int or float
                Y coordinate of the anchor point.
        """
        return self._anchor_x, self._anchor_y

    @anchor_position.setter
    def anchor_position(self, values):
        self._anchor_x, self._anchor_y = values
        self._update_position()

    @property
    def color(self):
        """The shape color.

        This property sets the color of the shape.

        The color is specified as an RGB tuple of integers '(red, green, blue)'.
        Each color component must be in the range 0 (dark) to 255 (saturated).

        :type: (int, int, int)
        """
        return self._rgb

    @color.setter
    def color(self, values):
        self._rgb = tuple(map(int, values))
        self._update_color()

    @property
    def opacity(self):
        """Blend opacity.

        This property sets the alpha component of the color of the shape.
        With the default blend mode (see the constructor), this allows the
        shape to be drawn with fractional opacity, blending with the
        background.

        An opacity of 255 (the default) has no effect.  An opacity of 128
        will make the shape appear translucent.

        :type: int
        """
        return self._opacity

    @opacity.setter
    def opacity(self, value):
        self._opacity = value
        self._update_color()

    @property
    def visible(self):
        """True if the shape will be drawn.

        :type: bool
        """
        return self._visible

    @visible.setter
    def visible(self, value):
        self._visible = value
        self._update_position()


class Rectangle(_ShapeBase):
    def __init__(self, x, y, width, height, color=(255, 255, 255), batch=None, group=None):
        """Create a rectangle or square.

        The rectangle's anchor point defaults to the (x, y) coordinates,
        which are at the bottom left.

        :Parameters:
            `x` : float
                The X coordinate of the rectangle.
            `y` : float
                The Y coordinate of the rectangle.
            `width` : float
                The width of the rectangle.
            `height` : float
                The height of the rectangle.
            `color` : (int, int, int)
                The RGB color of the rectangle, specified as
                a tuple of three ints in the range of 0-255.
            `batch` : `~pyglet.graphics.Batch`
                Optional batch to add the rectangle to.
            `group` : `~pyglet.graphics.Group`
                Optional parent group of the rectangle.
        """
        self._x = x
        self._y = y
        self._width = width
        self._height = height
        self._rotation = 0
        self._rgb = color

        self._batch = batch or Batch()
        self._group = _ShapeGroup(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA, group)
        self._vertex_list = self._batch.add(
            6, GL_TRIANGLES, self._group, 'v2f', 'c4B')
        self._update_position()
        self._update_color()

    def _update_position(self):
        if not self._visible:
            self._vertex_list.vertices = (0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0)
        elif self._rotation:
            x1 = -self._anchor_x
            y1 = -self._anchor_y
            x2 = x1 + self._width
            y2 = y1 + self._height
            x = self._x
            y = self._y

            r = -math.radians(self._rotation)
            cr = math.cos(r)
            sr = math.sin(r)
            ax = x1 * cr - y1 * sr + x
            ay = x1 * sr + y1 * cr + y
            bx = x2 * cr - y1 * sr + x
            by = x2 * sr + y1 * cr + y
            cx = x2 * cr - y2 * sr + x
            cy = x2 * sr + y2 * cr + y
            dx = x1 * cr - y2 * sr + x
            dy = x1 * sr + y2 * cr + y
            self._vertex_list.vertices = (
                ax, ay, bx, by, cx, cy, ax, ay, cx, cy, dx, dy)
        else:
            x1 = self._x - self._anchor_x
            y1 = self._y - self._anchor_y
            x2 = x1 + self._width
            y2 = y1 + self._height
            self._vertex_list.vertices = (
                x1, y1, x2, y1, x2, y2, x1, y1, x2, y2, x1, y2)

    def _update_color(self):
        self._vertex_list.colors[:] = [self._rgb[0], self._rgb[1], self._rgb[2], int(self._opacity)] * 6

    # def _update_color(self):
    #     # self._vertex_list.colors[:] = (self._rgb + tuple(int(self._opacity),)) * 6
    #     self._vertex_list.colors[:] = [list(self._rgb) + [int(self._opacity)]] * 6

    @property
    def width(self):
        """The width of the rectangle.

        :type: float
        """
        return self._width

    @width.setter
    def width(self, value):
        self._width = value
        self._update_position()

    @property
    def height(self):
        """The height of the rectangle.

        :type: float
        """
        return self._height

    @height.setter
    def height(self, value):
        self._height = value
        self._update_position()

    @property
    def rotation(self):
        """Clockwise rotation of the rectangle, in degrees.

        The Rectangle will be rotated about its (anchor_x, anchor_y)
        position.

        :type: float
        """
        return self._rotation

    @rotation.setter
    def rotation(self, rotation):
        self._rotation = rotation
        self._update_position()


class BorderedRectangle(_ShapeBase):
    def __init__(self, x, y, width, height, border=1, color=(255, 255, 255),
                 border_color=(100, 100, 100), batch=None, group=None):
        """Create a rectangle or square.

        The rectangle's anchor point defaults to the (x, y) coordinates,
        which are at the bottom left.

        :Parameters:
            `x` : float
                The X coordinate of the rectangle.
            `y` : float
                The Y coordinate of the rectangle.
            `width` : float
                The width of the rectangle.
            `height` : float
                The height of the rectangle.
            `border` : float
                The thickness of the border.
            `color` : (int, int, int)
                The RGB color of the rectangle, specified as
                a tuple of three ints in the range of 0-255.
            `border_color` : (int, int, int)
                The RGB color of the rectangle's border, specified as
                a tuple of three ints in the range of 0-255.
            `batch` : `~pyglet.graphics.Batch`
                Optional batch to add the rectangle to.
            `group` : `~pyglet.graphics.Group`
                Optional parent group of the rectangle.
        """
        self._x = x
        self._y = y
        self._width = width
        self._height = height
        self._rotation = 0
        self._border = border
        self._rgb = color
        self._brgb = border_color

        self._batch = batch or Batch()
        self._group = _ShapeGroup(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA, group)
        indices = [0, 1, 2, 0, 2, 3, 0, 4, 3, 4, 7, 3, 0, 1,
                   5, 0, 5, 4, 1, 2, 5, 5, 2, 6, 6, 2, 3, 6, 3, 7]
        self._vertex_list = self._batch.add_indexed(
            8, GL_TRIANGLES, self._group, indices, 'v2f', 'c4B')
        self._update_position()
        self._update_color()

    def _update_position(self):
        if not self._visible:
            self._vertex_list.vertices = (
                0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0)
        elif self._rotation:
            b = self._border
            x = self._x
            y = self._y

            bx1 = -self._anchor_x
            by1 = -self._anchor_y
            bx2 = bx1 + self._width
            by2 = by1 + self._height
            ix1 = bx1 + b
            iy1 = by1 + b
            ix2 = bx2 - b
            iy2 = by2 - b

            r = -math.radians(self._rotation)
            cr = math.cos(r)
            sr = math.sin(r)

            bax = bx1 * cr - by1 * sr + x
            bay = bx1 * sr + by1 * cr + y
            bbx = bx2 * cr - by1 * sr + x
            bby = bx2 * sr + by1 * cr + y
            bcx = bx2 * cr - by2 * sr + x
            bcy = bx2 * sr + by2 * cr + y
            bdx = bx1 * cr - by2 * sr + x
            bdy = bx1 * sr + by2 * cr + y

            iax = ix1 * cr - iy1 * sr + x
            iay = ix1 * sr + iy1 * cr + y
            ibx = ix2 * cr - iy1 * sr + x
            iby = ix2 * sr + iy1 * cr + y
            icx = ix2 * cr - iy2 * sr + x
            icy = ix2 * sr + iy2 * cr + y
            idx = ix1 * cr - iy2 * sr + x
            idy = ix1 * sr + iy2 * cr + y

            self._vertex_list.vertices[:] = (iax, iay, ibx, iby, icx, icy, idx, idy,
                                             bax, bay, bbx, bby, bcx, bcy, bdx, bdy,)
        else:
            b = self._border
            bx1 = self._x - self._anchor_x
            by1 = self._y - self._anchor_y
            bx2 = bx1 + self._width
            by2 = by1 + self._height
            ix1 = bx1 + b
            iy1 = by1 + b
            ix2 = bx2 - b
            iy2 = by2 - b
            self._vertex_list.vertices[:] = (ix1, iy1, ix2, iy1, ix2, iy2, ix1, iy2,
                                             bx1, by1, bx2, by1, bx2, by2, bx1, by2,)

    def _update_color(self):
        opacity = int(self._opacity)
        self._vertex_list.colors[:] = (self._rgb + [opacity]) * 4 + (self._brgb + [opacity]) * 4

    @property
    def width(self):
        """The width of the rectangle.

        :type: float
        """
        return self._width

    @width.setter
    def width(self, value):
        self._width = value
        self._update_position()

    @property
    def height(self):
        """The height of the rectangle.

        :type: float
        """
        return self._height

    @height.setter
    def height(self, value):
        self._height = value
        self._update_position()

    @property
    def rotation(self):
        """Clockwise rotation of the rectangle, in degrees.

        The Rectangle will be rotated about its (anchor_x, anchor_y)
        position.

        :type: float
        """
        return self._rotation

    @rotation.setter
    def rotation(self, value):
        self._rotation = value
        self._update_position()

    @property
    def border_color(self):
        """The rectangle's border color.

        This property sets the color of the border of a bordered rectangle.

        The color is specified as an RGB tuple of integers '(red, green, blue)'.
        Each color component must be in the range 0 (dark) to 255 (saturated).

        :type: (int, int, int)
        """
        return self._brgb

    @border_color.setter
    def border_color(self, values):
        self._brgb = tuple(map(int, values))
        self._update_color()


__all__ = ('Rectangle', 'BorderedRectangle')
