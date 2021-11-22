#!/usr/bin/env python

import pyglet
from pyglet.window import key


from justhink_world.tools.graphics import DialogBox


def test_info_box():
    window = pyglet.window.Window(1920, 1080)

    window.label = pyglet.text.Label(
        'Hi!', font_name='Times New Roman', font_size=36, x=window.width//2,
        y=window.height//2, anchor_x='center', anchor_y='center')

    window.info_box = DialogBox(main_text='Hello World!')

    @window.event
    def on_draw():
        window.clear()
        window.label.draw()
        window.info_box.draw()

    @window.event
    def on_key_press(symbol, modifiers):
        if symbol == key.T:
            print('The "T" key was pressed: toggle the dialog box.')
            window.info_box.visible = not window.info_box.visible

    pyglet.app.run()


def test_confirm_box():
    window = pyglet.window.Window(1920, 1080)
    window.batch = pyglet.graphics.Batch()

    window.label = pyglet.text.Label(
        'Hi!', font_name='Times New Roman', font_size=36, x=window.width//2,
        y=window.height//2, anchor_x='center', anchor_y='center')

    window.confirm_box = DialogBox(
        main_text='Do you want to submit?',
        yes_text='Ok', no_text='Cancel',
        width=window.width, height=window.height, visible=True,
        batch=window.batch)

    @window.event
    def on_draw():
        window.clear()
        window.label.draw()

        window.batch.draw()

        # if window.confirm_box.visible:
        #     window.confirm_box.draw()

    @window.event
    def on_key_press(symbol, modifiers):
        if symbol == key.T:
            print('The "T" key was pressed: toggle the dialog box.')
            window.confirm_box.visible = not window.confirm_box.visible

    @window.event
    def on_mouse_press(x, y, button, modifiers):
        if window.confirm_box.check_yes_hit(x, y):
            print('Pressed yes!')
        elif window.confirm_box.check_no_hit(x, y):
            print('Pressed no!')

    print('Showing window. Press T to toggle the dialog box.')

    pyglet.app.run()


def test_select_box():
    window = pyglet.window.Window(1920, 1080)
    window.batch = pyglet.graphics.Batch()

    window.label = pyglet.text.Label(
        'Hi!', font_name='Times New Roman', font_size=36, x=window.width//2,
        y=window.height//2, anchor_x='center', anchor_y='center')

    window.select_box = DialogBox(
        main_text='What do you think?',
        yes_text="I think the robot's suggestion is useful.",
        no_text="I think the robot's suggestion is not useful.",
        width=window.width, height=window.height, response_fontsize=24,
        width_scaler=3.0/5,  height_scaler=1.0/3,
        visible=True, batch=window.batch)

    @window.event
    def on_draw():
        window.clear()
        window.label.draw()

        # if window.select_box.visible:
        #     window.select_box.draw()
        window.batch.draw()

    @window.event
    def on_key_press(symbol, modifiers):
        if symbol == key.T:
            print('The "T" key was pressed: toggle the dialog box.')
            window.select_box.visible = not window.select_box.visible

    @window.event
    def on_mouse_press(x, y, button, modifiers):
        if window.select_box.check_yes_hit(x, y):
            print('Pressed yes!')
        elif window.select_box.check_no_hit(x, y):
            print('Pressed no!')

    print('Showing window. Press T to toggle the dialog box.')

    pyglet.app.run()


if __name__ == '__main__':

    # test_info_box()

    test_select_box()

    test_confirm_box()
