import os
import pyglet
from .utilities import center_image

pyglet.resource.path = ['../assets']
pyglet.resource.reindex()

# blue chip
blue_chip_image = pyglet.resource.image('images/chips/blue-poker-chip.png')
center_image(blue_chip_image)

# dealer button
dealer_button = pyglet.resource.image('images/chips/dealer-button.png')
center_image(dealer_button)

# table
green_table = pyglet.resource.image('images/tables/felt-green-1080p-vignette.png')

# white box
white_box = pyglet.resource.image('images/white_rect.png')
white_box.anchor_x = 0
white_box.anchor_y = white_box.height

# gui
gui_images = {}
for filename in [f for f in os.listdir('../assets/images/gui/buttons')]:
    gui = filename.split('.')[0]
    gui_images[gui] = pyglet.resource.image(f'images/gui/buttons/{filename}')

for filename in [f for f in os.listdir('../assets/images/gui/slider')]:
    gui = filename.split('.')[0]
    gui_images[gui] = pyglet.resource.image(f'images/gui/slider/{filename}')

# favicon
icon = pyglet.resource.image('images/favicons/favicon-32x32.png')

# cards
card_images = {}
for filename in [f for f in os.listdir('../assets/images/cards')]:
    card = filename.split('.')[0]
    card_images[card] = pyglet.resource.image(f'images/cards/{filename}')
    center_image(card_images[card])

# actor frame
actor_frame = pyglet.resource.image('images/white_frame.png')
center_image(actor_frame)

# sounds
card_placing_sounds = []
for filename in [f for f in os.listdir('../assets/sounds/card/cardplace')]:
    sound = pyglet.resource.media(f'sounds/card/cardplace/{filename}', streaming=False)
    card_placing_sounds.append(sound)

card_shoving_sounds = []
for filename in [f for f in os.listdir('../assets/sounds/card/cardshove')]:
    sound = pyglet.resource.media(f'sounds/card/cardshove/{filename}', streaming=False)
    card_shoving_sounds.append(sound)

chip_stacking_sounds = []
for filename in [f for f in os.listdir('../assets/sounds/chip/chipsstack')]:
    sound = pyglet.resource.media(f'sounds/chip/chipsstack/{filename}', streaming=False)
    chip_stacking_sounds.append(sound)

chip_laying_sound = pyglet.resource.media('sounds/chip/chipLay3.ogg')

chip_shoving_sound = pyglet.resource.media('sounds/chip/chipsHandle5.ogg')

tapping_sounds = []
for filename in [f for f in os.listdir('../assets/sounds/hand')]:
    sound = pyglet.resource.media(f'sounds/hand/{filename}', streaming=False)
    tapping_sounds.append(sound)

elimination_sound = pyglet.resource.media('sounds/impactGlass_heavy_004.ogg')
