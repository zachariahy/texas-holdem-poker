import treys
from src.core.constants import BUY_IN_AMOUNT, Action, Stage, SMALL_BLIND_AMOUNT, BIG_BLIND_AMOUNT


class GameState:
    def __init__(self):
        self.players = []

        self.community_cards = []
        self.deck = treys.Deck()
        self.positions = Positions()

        self.pots = []
        self.actor = None
        self.stage = None
        self.bets = Bets()

        self.in_tournament = False
        self.in_hand = False

        self.last_action = ''
        self.hand_results = []

    def add_player(self, name, is_human):
        self.players.append(PlayerState(name, is_human))

    def create_pot(self, eligible_players):
        name = f'Side Pot {len(self.pots)}' if self.pots else 'Main Pot'
        self.pots.append(PotState(name, eligible_players))

    def shuffle_deck(self):
        self.deck.shuffle()

    def is_preflop_stage(self):
        return self.stage == Stage.PREFLOP

    def is_headsup(self):
        return sum(1 for player in self.players if player.stack_size) == 2

    def is_less_two_active_players(self):
        return sum(1 for player in self.players if player.is_active()) < 2

    def is_single_player_not_folded(self):
        return sum(1 for player in self.players if not player.is_folded()) == 1

    def is_single_player_with_stack(self):
        return sum(1 for player in self.players if player.stack_size) == 1


class PlayerState:
    def __init__(self, name, is_human):
        self.name = name
        self.is_human = is_human
        self.hole_cards = []
        self.stack_size = BUY_IN_AMOUNT
        self.action = None
        self.total_bet = 0
        self.hand = None
        self.hand_strength = None

        self.is_acting = False

    def is_active(self):
        return self.stack_size and self.action not in [Action.FOLD, Action.ALL_IN]

    def is_folded(self):
        return self.action == Action.FOLD

    def is_all_in(self):
        return self.action == Action.ALL_IN

    def has_acted(self):
        return self.action not in [None, Action.POST_BLIND]

    def move_chips(self, add_bet):
        self.total_bet += add_bet
        self.stack_size -= add_bet

    def post_blind(self, blind_amount):
        add_bet = min(blind_amount, self.stack_size)
        self.move_chips(add_bet)
        self.action = Action.POST_BLIND if self.stack_size else Action.ALL_IN

    def post_small_blind(self):
        self.post_blind(SMALL_BLIND_AMOUNT)

    def post_big_blind(self):
        self.post_blind(BIG_BLIND_AMOUNT)

    def check(self):
        self.action = Action.CHECK

    def fold(self):
        self.action = Action.FOLD
        self.hole_cards = []

    def bet(self, add_bet):
        self.move_chips(add_bet)
        self.action = Action.BET if self.stack_size else Action.ALL_IN

    def call(self, add_bet):
        self.move_chips(add_bet)
        self.action = Action.CALL if self.stack_size else Action.ALL_IN

    def raise_(self, add_bet):
        self.move_chips(add_bet)
        self.action = Action.RAISE if self.stack_size else Action.ALL_IN

    def all_in(self):
        self.action = Action.ALL_IN
        self.total_bet += self.stack_size
        self.stack_size = 0


class PotState:
    def __init__(self, name, eligible_players):
        self.name = name
        self.eligible_players = eligible_players
        self.is_closed = False
        self.size = 0


class Bets:
    def __init__(self):
        self.last = 0
        self.current = 0

    def is_bet(self):
        return self.last or self.current

    def update(self, new_bet):
        if new_bet > self.current:
            self.last = self.current
            self.current = new_bet


class Positions:
    def __init__(self):
        self.dealer = None
        self.small_blind = None
        self.big_blind = None
