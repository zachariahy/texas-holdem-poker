from random import randint

import pyglet

from src.gui import load
from src.gui.constants import WINDOW_WIDTH, WINDOW_HEIGHT, PLAYER_POSITIONS, OFF_SCREEN, LAST_ACTION_X, LAST_ACTION_Y
from src.gui.player import PlayerSprites
from src.gui.pot import PotLabels
from src.gui.card import CommunityCardSprites


class GameGraphics:
    def __init__(self, game_state, batch):
        self.game_state = game_state

        self.player_graphics = PlayerSprites(game_state.players, batch)
        self.pot_graphics = PotLabels(game_state.pots, batch)
        self.community_card_graphics = CommunityCardSprites(game_state.community_cards, batch)

        self.button_sprite = load.button(OFF_SCREEN, OFF_SCREEN, batch)
        self.button_sprite.rotation = randint(-10, 10)

        self.frame_sprite = load.frame(OFF_SCREEN, OFF_SCREEN, batch)

        self.last_action_title_label = pyglet.text.Label(text='Last Action',
                                                         font_size=24,
                                                         color=(0, 61, 34, 255),
                                                         bold=True,
                                                         x=LAST_ACTION_X + 30, y=LAST_ACTION_Y - 40,
                                                         anchor_y='center',
                                                         batch=batch
                                                         )

        self.last_action_label = pyglet.text.Label(text='TEST',
                                                   font_size=16,
                                                   color=(0, 61, 34, 255),
                                                   x=LAST_ACTION_X + 30, y=LAST_ACTION_Y - 80,
                                                   anchor_y='center',
                                                   batch=batch
                                                   )

    def update(self):
        self.player_graphics.update()
        self.pot_graphics.update()
        self.community_card_graphics.update()

        for player in self.game_state.players:
            # update dealer button
            if player is self.game_state.positions.dealer:
                x, y = PLAYER_POSITIONS[self.game_state.players.index(player)]
                self.button_sprite.x = WINDOW_WIDTH / 2 + (x - WINDOW_WIDTH / 2) * .5
                self.button_sprite.y = WINDOW_HEIGHT / 2 + (y - WINDOW_HEIGHT / 2) * .6

            if self.game_state.actor:
                if player is self.game_state.actor:
                    # update actor frame
                    self.frame_sprite.x, self.frame_sprite.y = PLAYER_POSITIONS[self.game_state.players.index(player)]
            else:
                self.frame_sprite.y = OFF_SCREEN

        # update last action
        self.last_action_label.text = self.game_state.last_action
