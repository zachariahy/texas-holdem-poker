import pyglet

from src.core.constants import Action
from src.gui import load
from random import randint
from src.gui.card import CardSprite
from src.gui.constants import PLAYER_POSITIONS, OFF_SCREEN


class PlayerSprite:
    def __init__(self, player, x, y, batch):
        self.player = player
        self.x, self.y = x, y
        self.batch = batch

        self.name_x, self.name_y = x + 70, y + 90
        self.chip_x, self.chip_y = x - 80, y + 50
        self.stack_x, self.stack_y = self.chip_x, y
        self.action_x, self.action_y = self.chip_x, y - 70
        self.card_x, self.card_y = x + 40, y - 20

        self.name_label = pyglet.text.Label(text=player.name,
                                            font_size=18,
                                            bold=True,
                                            x=self.name_x,
                                            y=self.name_y,
                                            anchor_x='center',
                                            batch=batch
                                            )

        self.chip_sprite = load.chip(x=self.chip_x,
                                     y=self.chip_y,
                                     batch=batch)
        self.chip_sprite.rotation = randint(0, 360)

        self.stack_size_label = pyglet.text.Label(text=str(player.stack_size),
                                                  font_size=12,
                                                  x=self.stack_x,
                                                  y=self.stack_y,
                                                  anchor_x='center',
                                                  batch=batch
                                                  )

        self.action_label = pyglet.text.Label(text='',
                                              font_size=18,
                                              bold=True,
                                              color=(255, 255, 0, 255),
                                              x=self.action_x,
                                              y=self.action_y,
                                              anchor_x='center',
                                              batch=batch
                                              )

        self.card_sprites = {}

    def update(self):
        # name
        if not self.player.total_bet and not self.player.stack_size and self.player.action != Action.ALL_IN:
            self.name_label.x = OFF_SCREEN
        else:
            self.name_label.x = self.name_x

        # stack
        if self.player.stack_size:
            self.stack_size_label.text = f'${str(self.player.stack_size)}'
            self.chip_sprite.x = self.chip_x
        else:
            self.stack_size_label.text = ''
            self.chip_sprite.x = OFF_SCREEN

        # action
        if self.player.action not in [None, Action.POST_BLIND] and (self.player.stack_size or self.player.hole_cards):
            self.action_label.text = self.player.action.value
        else:
            self.action_label.text = ''

        # cards
        if self.player.hole_cards:
            for card_int in self.player.hole_cards:
                if card_int not in self.card_sprites:
                    self.card_sprites[card_int] = CardSprite(card_int,
                                                             x=self.card_x + self.player.hole_cards.index(
                                                                 card_int) * 25,
                                                             y=self.card_y - self.player.hole_cards.index(
                                                                 card_int) * 25,
                                                             batch=self.batch
                                                             )
                    self.card_sprites[card_int].face_down()
                elif self.player.is_acting and self.player.is_human:
                    self.card_sprites[card_int].face_up()
                else:
                    self.card_sprites[card_int].face_down()
        else:
            for k, sprite in self.card_sprites.items():
                sprite.delete()
            self.card_sprites.clear()


class PlayerSprites:
    def __init__(self, players, batch):
        self.batch = batch
        self.player_sprites = []

        for player in players:
            position = PLAYER_POSITIONS[players.index(player)]
            sprite = PlayerSprite(player=player,
                                  x=position[0],
                                  y=position[1],
                                  batch=batch)
            self.player_sprites.append(sprite)

    def update(self):
        for sprite in self.player_sprites:
            sprite.update()
