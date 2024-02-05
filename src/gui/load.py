import pyglet
from .resources import card_images, blue_chip_image, dealer_button, actor_frame


def card(card_name, x, y, batch):
    card_image = card_images[card_name]
    card_sprite = pyglet.sprite.Sprite(img=card_image,
                                       x=x, y=y,
                                       batch=batch)
    return card_sprite


def chip(x, y, batch):
    chip_sprite = pyglet.sprite.Sprite(img=blue_chip_image,
                                       x=x, y=y,
                                       batch=batch
                                       )
    return chip_sprite


def button(x, y, batch):
    button_sprite = pyglet.sprite.Sprite(img=dealer_button,
                                         x=x, y=y,
                                         batch=batch)
    return button_sprite


def frame(x, y, batch):
    frame_sprite = pyglet.sprite.Sprite(img=actor_frame,
                                        x=x, y=y,
                                        batch=batch)
    return frame_sprite
