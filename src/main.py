import random
import pyglet
from gui import resources
from src.core.state import GameState
from src.core.manager import GameManager
from src.gui.actions import ActionButtons
from src.gui.game import GameGraphics
from src.gui.constants import WINDOW_WIDTH, WINDOW_HEIGHT, LAST_ACTION_X, LAST_ACTION_Y, NAMES


class PokerWindow(pyglet.window.Window):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.set_caption("No-Limit Texas Hold'em")
        self.set_icon(resources.icon)

        self.main_batch = pyglet.graphics.Batch()

        self.table_sprite = pyglet.sprite.Sprite(img=resources.green_table,
                                                 x=0, y=0,
                                                 batch=self.main_batch)

        self.last_action_box = pyglet.sprite.Sprite(img=resources.white_box,
                                                    x=LAST_ACTION_X, y=LAST_ACTION_Y,
                                                    batch=self.main_batch)

        self.overlay = pyglet.shapes.Rectangle(0, 0, WINDOW_WIDTH, WINDOW_HEIGHT,
                                               color=(0, 0, 0))
        self.overlay.opacity = 128

        self.prompting_label = pyglet.text.Label('',
                                                 font_size=18,
                                                 x=self.width // 2, y=self.height // 2 - 50,
                                                 anchor_x='center', anchor_y='center')

        self.hand_results_labels = []
        for i in range(1, 5):
            hand_result_label = pyglet.text.Label(f'',
                                                  font_size=24,
                                                  x=self.width // 2, y=self.height // 2 + i * 50,
                                                  anchor_x='center', anchor_y='center')
            self.hand_results_labels.append(hand_result_label)

        self.game_over = False

        self.game_state = GameState()
        self.game_manager = GameManager(self.game_state)

        # add players
        names = NAMES
        for _ in range(0, 5):
            random_name = random.choice(names)
            names.remove(random_name)
            self.game_state.add_player(random_name, False)
        self.game_state.add_player(f'Player', True)

        self.game_graphics = GameGraphics(self.game_state, self.main_batch)
        self.game_buttons = ActionButtons(self.game_manager, self.main_batch)

    def draw_hand_results_labels(self):
        for result, label in zip(self.game_state.hand_results, self.hand_results_labels):
            label.text = result
            label.draw()

    def on_draw(self):
        self.clear()
        self.game_graphics.update()
        self.game_buttons.update()
        self.main_batch.draw()

        if not self.game_state.in_tournament:
            self.overlay.draw()
            if not self.game_state.hand_results:
                self.prompting_label.text = '(Press \'Space\' to Start a Tournament)'
                self.prompting_label.draw()
            else:
                self.draw_hand_results_labels()
                self.game_over = True
                self.prompting_label.text = '(Game Over)'
                self.prompting_label.draw()
        elif not self.game_state.in_hand:
            # self.game_manager.start_hand()

            self.overlay.draw()
            self.prompting_label.text = '(Press \'Space\' to Start a Hand)'
            self.prompting_label.draw()
            if self.game_state.hand_results:
                self.draw_hand_results_labels()

    def on_key_press(self, symbol, modifiers):
        if self.game_over:
            return
        elif symbol == pyglet.window.key.SPACE and not self.game_state.in_tournament:
            self.game_manager.start_tournament()
        elif symbol == pyglet.window.key.SPACE and not self.game_state.in_hand:
            self.game_manager.start_hand()

    def on_mouse_press(self, x, y, button, modifiers):
        self.game_buttons.on_mouse_press(x, y, button, modifiers)

    def on_mouse_drag(self, x, y, dx, dy, buttons, modifiers):
        self.game_buttons.on_mouse_drag(x, y, dx, dy, buttons, modifiers)


if __name__ == '__main__':
    window = PokerWindow(WINDOW_WIDTH, WINDOW_HEIGHT)
    pyglet.clock.schedule_interval(window.game_manager.deal, 1 / 30)
    pyglet.clock.schedule_interval(window.game_manager.update, 1)
    pyglet.app.run()
