import pyglet
from src.core.constants import Action
from src.gui import resources
from src.gui.constants import BUTTONS_X, BUTTONS_Y, OFF_SCREEN


class ActionButtons:
    def __init__(self, game_manager, batch):
        self.game_manager = game_manager
        self.action_buttons = {}
        self.current_action = None
        self.current_amount = None

        check_button = pyglet.gui.PushButton(BUTTONS_X, OFF_SCREEN,
                                             pressed=resources.gui_images['check-button'],
                                             depressed=resources.gui_images['check-button'],
                                             batch=batch)
        check_button.set_handler('on_press', self.on_check_press)
        self.action_buttons[Action.CHECK] = check_button

        fold_button = pyglet.gui.PushButton(BUTTONS_X, OFF_SCREEN,
                                            pressed=resources.gui_images['fold-button'],
                                            depressed=resources.gui_images['fold-button'],
                                            batch=batch)
        fold_button.set_handler('on_press', self.on_fold_press)
        self.action_buttons[Action.FOLD] = fold_button

        bet_button = pyglet.gui.ToggleButton(BUTTONS_X, OFF_SCREEN,
                                             pressed=resources.gui_images['bet-button'],
                                             depressed=resources.gui_images['bet-button'],
                                             batch=batch)
        bet_button.set_handler('on_toggle', self.on_bet_toggle)
        self.action_buttons[Action.BET] = bet_button

        call_button = pyglet.gui.PushButton(BUTTONS_X, OFF_SCREEN,
                                            pressed=resources.gui_images['call-button'],
                                            depressed=resources.gui_images['call-button'],
                                            batch=batch)
        call_button.set_handler('on_press', self.on_call_press)
        self.action_buttons[Action.CALL] = call_button

        raise_button = pyglet.gui.ToggleButton(BUTTONS_X, OFF_SCREEN,
                                               pressed=resources.gui_images['raise-button'],
                                               depressed=resources.gui_images['raise-button'],
                                               batch=batch)
        raise_button.set_handler('on_toggle', self.on_raise_toggle)
        self.action_buttons[Action.RAISE] = raise_button

        all_in_button = pyglet.gui.PushButton(BUTTONS_X, OFF_SCREEN,
                                              pressed=resources.gui_images['all-in-button'],
                                              depressed=resources.gui_images['all-in-button'],
                                              batch=batch)
        all_in_button.set_handler('on_press', game_manager.all_in)
        self.action_buttons[Action.ALL_IN] = all_in_button

        self.slider = pyglet.gui.Slider(x=BUTTONS_X + 150, y=OFF_SCREEN,
                                        base=resources.gui_images['grey_sliderHorizontal'],
                                        knob=resources.gui_images['grey_sliderDown'],
                                        batch=batch)

        self.current_amount_label = pyglet.text.Label(text=f'{self.current_amount}',
                                                      font_size=16,
                                                      bold=True,
                                                      x=OFF_SCREEN, y=OFF_SCREEN,
                                                      anchor_x='center', anchor_y='center',
                                                      batch=batch
                                                      )

        self.confirm_button = pyglet.gui.PushButton(x=BUTTONS_X + 170, y=OFF_SCREEN,
                                                    pressed=resources.gui_images['confirm-button'],
                                                    depressed=resources.gui_images['confirm-button'],
                                                    batch=batch)
        self.confirm_button.set_handler('on_press', self.on_confirm_press)

    def on_mouse_press(self, x, y, button, modifiers):
        for k, btn in self.action_buttons.items():
            btn.on_mouse_press(x, y, button, modifiers)
        self.confirm_button.on_mouse_press(x, y, button, modifiers)
        self.slider.on_mouse_press(x, y, button, modifiers)

    def on_mouse_drag(self, x, y, dx, dy, buttons, modifiers):
        self.slider.on_mouse_drag(x, y, dx, dy, buttons, modifiers)

    def show_slider(self):
        self.slider.y = BUTTONS_Y
        self.confirm_button.y = BUTTONS_Y - 100
        self.current_amount_label.y = BUTTONS_Y + 40

    def hide_slider(self):
        self.slider.y = OFF_SCREEN
        self.confirm_button.y = OFF_SCREEN
        self.current_amount_label.y = OFF_SCREEN

    def on_raise_toggle(self, is_pressed):
        if is_pressed:
            self.show_slider()
            self.current_action = Action.RAISE
        else:
            self.hide_slider()

    def on_bet_toggle(self, is_pressed):
        if is_pressed:
            self.show_slider()
            self.current_action = Action.BET
        else:
            self.hide_slider()

    def on_confirm_press(self):
        if self.current_action == Action.BET:
            self.game_manager.bet(self.current_amount)
        elif self.current_action == Action.RAISE:
            self.game_manager.raise_(self.current_amount)

        self.hide_slider()
        self.current_action = None
        self.slider.value = 0

    def on_call_press(self):
        self.hide_slider()
        self.game_manager.call()

    def on_fold_press(self):
        self.hide_slider()
        self.game_manager.fold()

    def on_check_press(self):
        self.hide_slider()
        self.game_manager.check()

    def update(self):
        current_available_actions = self.game_manager.get_available_actions()

        if not current_available_actions or not self.game_manager.game_state.actor.is_human:
            for action_name, action_button in self.action_buttons.items():
                action_button.y = OFF_SCREEN
            return

        button_count = 0
        for action_name, action_button in self.action_buttons.items():
            if action_name in current_available_actions:
                action_button.y = BUTTONS_Y - button_count * 50
                button_count += 1
            else:
                action_button.y = OFF_SCREEN

        # update current amount and amount label
        if Action.BET in current_available_actions or Action.RAISE in current_available_actions:
            amount_range = current_available_actions.get(Action.BET) if current_available_actions.get(Action.BET) \
                else current_available_actions.get(Action.RAISE)
            min_range = amount_range[0]
            max_range = amount_range[1]
            transformed_value = int(min_range + self.slider.value * (max_range - min_range) / 100)
            self.current_amount = transformed_value
            self.current_amount_label.text = str(self.current_amount)
            self.current_amount_label.x = self.slider._knob_spr.x + self.slider._half_knob_width
