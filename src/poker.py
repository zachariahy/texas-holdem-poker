import random

import pyglet
from gui import resources
from src.core.state import GameState
from src.core.manager import GameManager
from src.gui.actions import ActionButtons
from src.gui.game import GameGraphics
from src.gui.constants import WINDOW_WIDTH, WINDOW_HEIGHT, LAST_ACTION_X, LAST_ACTION_Y

window = pyglet.window.Window(WINDOW_WIDTH, WINDOW_HEIGHT)
window.set_caption("No-Limit Texas Hold'em")
window.set_icon(resources.icon)

main_batch = pyglet.graphics.Batch()

table_sprite = pyglet.sprite.Sprite(img=resources.green_table,
                                    x=0, y=0,
                                    batch=main_batch)

last_action_box = pyglet.sprite.Sprite(img=resources.white_box,
                                       x=LAST_ACTION_X, y=LAST_ACTION_Y,
                                       batch=main_batch)

game_state = GameState()
game_manager = GameManager(game_state)

names = ['Moose', 'Cracker', 'Tulip', 'Sofa', 'Nemo', 'Zoo', 'Sack', 'Ambulance', 'Sun']

for i in range(1, 4):
    random_name = random.choice(names)
    names.remove(random_name)
    game_state.add_player(random_name, False)
# game_state.add_player(f'Player', True)
# for i in range(5, 9):
#     game_state.add_player(f'Bot {i}', False)

game_graphics = GameGraphics(game_state, main_batch)
game_buttons = ActionButtons(game_manager, main_batch)

overlay = pyglet.shapes.Rectangle(0, 0, WINDOW_WIDTH, WINDOW_HEIGHT,
                                  color=(0, 0, 0))
overlay.opacity = 128

start_label = pyglet.text.Label('',
                                font_size=18,
                                x=window.width // 2, y=window.height // 2 - 75,
                                anchor_x='center', anchor_y='center')

hand_results_labels = []
for i in range(1, 4):
    hand_result_label = pyglet.text.Label('',
                                          font_size=36,
                                          x=window.width // 2, y=window.height // 2 + i * 75,
                                          anchor_x='center', anchor_y='center')
    hand_results_labels.append(hand_result_label)

game_over = False


def draw_hand_results():
    for result, label in zip(game_state.hand_results, hand_results_labels):
        label.text = result
        label.draw()


@window.event
def on_key_press(symbol, modifiers):
    if game_over:
        return
    elif symbol == pyglet.window.key.SPACE and not game_state.in_tournament:
        game_manager.start_tournament()
    elif symbol == pyglet.window.key.SPACE and not game_state.in_hand:
        game_manager.start_hand()


@window.event
def on_draw():
    global game_over

    window.clear()
    game_graphics.update()
    game_buttons.update()
    main_batch.draw()

    if not game_state.in_tournament:
        overlay.draw()
        if not game_state.hand_results:
            start_label.text = '(Press \'Space\' to Start a Tournament)'
            start_label.draw()
        else:
            draw_hand_results()
            game_over = True
    elif not game_state.in_hand:
        overlay.draw()
        start_label.text = '(Press \'Space\' to Start a Hand)'
        start_label.draw()
        if game_state.hand_results:
            draw_hand_results()


@window.event
def on_mouse_press(x, y, button, modifiers):
    game_buttons.on_mouse_press(x, y, button, modifiers)


@window.event
def on_mouse_drag(x, y, dx, dy, buttons, modifiers):
    game_buttons.on_mouse_drag(x, y, dx, dy, buttons, modifiers)


if __name__ == '__main__':
    pyglet.clock.schedule_interval(game_manager.deal, 1 / 30)
    pyglet.clock.schedule_interval(game_manager.update, 1)
    pyglet.app.run()

# TODO fix player frame covering dealer button
# TODO put human in bottom center position at table

# TODO add sounds
# TODO AI BOTS
# TODO add depressed image to buttons
# TODO setup menu
#   single hand or tournament
#   number of bots
# TODO evenly distribute bots around table

# TODO display winning hand after round?
# TODO end game when player is out of chips?
