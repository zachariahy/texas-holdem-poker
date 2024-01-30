import pyglet
from src.gui.constants import POT_X, POT_Y


class PotLabel:
    def __init__(self, x, y, pot, batch):
        self.pot = pot
        self.name = pot.name

        self.pot_label = pyglet.text.Label(text=f'{pot.name}: {pot.size}',
                                           font_size=24,
                                           bold=True,
                                           x=x, y=y,
                                           anchor_x='center', anchor_y='center',
                                           batch=batch
                                           )

    def update(self):
        self.pot_label.text = f'{self.name}: {self.pot.size}'


class PotLabels:
    def __init__(self, pots, batch):
        self.pots = pots
        self.pot_labels = {}
        self.batch = batch

    def update(self):
        if self.pots:
            for pot in self.pots:
                if pot.name in self.pot_labels:
                    self.pot_labels[pot.name].update()
                else:
                    self.pot_labels[pot.name] = PotLabel(x=POT_X,
                                                         y=POT_Y + self.pots.index(pot) * 50,
                                                         pot=pot,
                                                         batch=self.batch
                                                         )
        else:
            for k, label in self.pot_labels.items():
                self.pot_labels[k] = None
            self.pot_labels.clear()
