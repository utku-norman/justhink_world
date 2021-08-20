import pyglet
from pyglet.window import key
from pyglet.gl import *


class ToggleWindow(pyglet.window.Window):

    def __init__(self, context=None, caption=''):
        super(ToggleWindow, self).__init__(context=context, caption=caption)
        self.color = 1.0

        # pyglet.clock.schedule(self.update)
        pyglet.clock.schedule_interval(self.update, 1/60.0)

    def toggle(self):
        if self.color == 1.0:
            self.color = 0.0
        else:
            self.color = 1.0

    def update(self, dt):
        pass

    def on_draw(self):
        # self.clear()
        # self.flip()
        # self.switch_to()

        glClear(GL_COLOR_BUFFER_BIT)
        glLoadIdentity()
        glColor3f(self.color, self.color, self.color)
        glBegin(GL_QUADS)
        glVertex2f(0, 0)
        glVertex2f(self.width, 0)
        glVertex2f(self.width, self.height)
        glVertex2f(0, self.height)
        glEnd()

    def on_key_press(self, symbol, modifiers):
        print('Toggling {}'.format(self.caption))
        if symbol == getattr(key, '_'+self.caption):
            # print(1)
            self.toggle()
        # elif symbol == key._2:
        #     print(2)
        #     self.toggle()
        # else:
        #     print(symbol)



def main():
    display = pyglet.canvas.get_display()
    screen = display.get_default_screen()

    # template = pyglet.gl.Config(alpha_size=8)
    # config = screen.get_best_config(template)
    # context = config.create_context(None)
    # window1 = pyglet.window.Window(context=context)
    # window2 = pyglet.window.Window(context=context)

    window1 = ToggleWindow(caption='1')

    window2 = ToggleWindow(caption='2')

    # @window1.event
    # def on_key_press(symbol, modifiers):
    #     print('Toggling 1')
    #     if symbol == key._1:
    #         print(1)
    #         window1.toggle()
    #     elif symbol == key._2:
    #         print(2)
    #         window2.toggle()
    #     else:
    #         print(symbol)

    # @window2.event
    # def on_key_press(symbol, modifiers):
    #     print('Toggling 2')
    #     if symbol == key._1:
    #         print(1)
    #         window1.toggle()
    #     elif symbol == key._2:
    #         print(2)
    #         window2.toggle()
    #     else:
    #         print(symbol)

    pyglet.app.run()


if __name__ == "__main__":
    main()
