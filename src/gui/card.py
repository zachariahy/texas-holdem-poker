import treys
from src.gui import resources
import random
import pyglet
from src.gui.constants import COMMUNITY_CARDS_X, COMMUNITY_CARDS_Y


class CardSprite:
    def __init__(self, card_int, x, y, batch):
        self.card = card_int
        card_name = treys.Card.int_to_str(card_int)
        self.face_image = resources.card_images[card_name.upper()]
        self.back_image = resources.card_images['2B']
        self.sprite = pyglet.sprite.Sprite(self.back_image,  # default face down
                                           x=x + random.randint(-1, 1),
                                           y=y + random.randint(-1, 1),
                                           batch=batch
                                           )
        self.sprite.rotation = random.uniform(-1.5, 1.5)

    def face_up(self):
        self.sprite.image = self.face_image

    def face_down(self):
        self.sprite.image = self.back_image

    def delete(self):
        self.sprite.delete()
        self.sprite = None


class CommunityCardSprites:
    def __init__(self, cards, batch):
        self.cards = cards
        self.card_sprites = {}
        self.batch = batch

    def update(self):
        if self.cards:
            for card_int in self.cards:
                if card_int not in self.card_sprites:
                    self.card_sprites[card_int] = CardSprite(card_int,
                                                             x=COMMUNITY_CARDS_X - self.cards.index(card_int) * 105,
                                                             y=COMMUNITY_CARDS_Y,
                                                             batch=self.batch
                                                             )
                    self.card_sprites[card_int].face_up()
        else:
            for k, sprite in self.card_sprites.items():
                sprite.delete()
            self.card_sprites.clear()
