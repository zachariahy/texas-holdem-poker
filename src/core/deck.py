import treys
from .constants import HOLE_CARD_COUNT


class DeckManager:
    def __init__(self):
        self.deck = treys.Deck()
        self.deck.shuffle()

    def deal_hole_cards(self, players):  # TODO deal starting with player left of dealer
        for _ in range(HOLE_CARD_COUNT):
            for player in players:
                player.hole_cards.extend(self.deck.draw(1))

    def deal_community_cards(self, community_cards):
        self.deck.draw(1)  # burn
        cards = self.deck.draw(1) if community_cards else self.deck.draw(3)  # turn/river else flop
        community_cards.extend(cards)
