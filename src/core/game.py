import treys
from .console_view import View
from .constants import BIG_BLIND_AMOUNT, Stage, MAIN_STAGES
from .pots import PotsManager
from .deck import DeckManager
from .player import PlayersManager


class Bets:  # TODO use list instead? Move to GameManager?
    def __init__(self, current, last):
        self.current = current
        self.last = last

    def update(self, total_bet):
        if total_bet > self.current:
            self.last = self.current
            self.current = total_bet


class GameState:  # model
    def __init__(self):
        self.players_manager = None
        self.pots_manager = None
        self.community_cards = None
        self.stage = None


class GameManager:  # controller
    def __init__(self, game_state):
        self.game_state = game_state
        self.evaluator = treys.Evaluator()

    def evaluate_player_hands(self, players_not_folded):
        for player in players_not_folded:
            player.hand_strength = self.evaluator.evaluate(player.hole_cards, self.game_state.community_cards)
            rank_class = self.evaluator.get_rank_class(player.hand_strength)
            player.hand = self.evaluator.class_to_string(rank_class)

    def handle_action(self, bets):
        acting_player = self.game_state.players_manager.acting_player

        available_actions = acting_player.get_available_actions(bets, self.game_state.stage)

        if acting_player.is_human:
            action, additional_bet = View.get_player_choice(available_actions, acting_player.stack)
        else:
            action, additional_bet = acting_player.get_random_choice(available_actions)
        View.print_player_choice(action, additional_bet)

        acting_player.execute_action(action, additional_bet)

        bets.update(acting_player.total_bet)

    def start_betting_round(self):
        players_manager = self.game_state.players_manager

        if players_manager.is_single_active_player():
            return

        # initialize betting round
        players_manager.acting_player = players_manager.get_first_acting_player(self.game_state.stage)
        bets = Bets(BIG_BLIND_AMOUNT if self.game_state.stage == Stage.PREFLOP else 0, 0)

        active_players = players_manager.get_active_players()
        players_manager.reset_actions(active_players)

        while (players_manager.acting_player
               and players_manager.acting_player.is_response_needed(bets.current)
               and not players_manager.is_single_active_player()):
            View.print_betting_history(bets)
            View.print_player_info(players_manager.acting_player)

            self.handle_action(bets)

            players_manager.acting_player = players_manager.get_next_active_player(players_manager.acting_player)

    def start_showdown(self):
        players_manager = self.game_state.players_manager

        if players_manager.is_single_player_not_folded():
            View.print_uncontested()
        else:
            # start showdown
            self.game_state.stage = Stage.SHOWDOWN
            View.print_showdown()

            self.evaluate_player_hands(players_manager.get_players_not_folded())

    def start_preflop(self, deck_manager, players_with_stack):
        self.game_state.stage = Stage.PREFLOP
        self.game_state.players_manager.post_blinds()
        deck_manager.deal_hole_cards(players_with_stack)
        self.start_betting_round()

    def start_hand(self):
        View.print_new_hand()

        players_manager = self.game_state.players_manager

        # initialize hand
        players_with_stack = players_manager.get_players_with_stack()
        players_manager.reset_actions(players_with_stack)
        players_manager.reset_hole_cards()
        self.game_state.pots_manager = PotsManager(players_with_stack)
        pots_manager = self.game_state.pots_manager
        self.game_state.community_cards = []
        deck_manager = DeckManager()

        View.print_positions(players_manager)

        self.start_preflop(deck_manager, players_with_stack)

        for stage in MAIN_STAGES:
            if players_manager.is_single_player_not_folded():
                break

            self.game_state.stage = stage

            deck_manager.deal_community_cards(self.game_state.community_cards)

            View.print_game_state(stage, pots_manager, self.game_state.community_cards)

            self.start_betting_round()

            pots_manager.collect_bets(players_manager)

        self.start_showdown()

        pots_manager.award_winners()

    def start_tournament(self):
        View.print_tournament()

        players_manager = self.game_state.players_manager

        players_manager.assign_positions()

        while not players_manager.is_single_player_with_stack():
            self.start_hand()

            players_manager.rotate_positions()

        View.print_tournament_winner(players_manager.players)

    def start_game(self):
        bot_count, human_count = View.get_player_counts()
        self.game_state.players_manager = PlayersManager(bot_count, human_count)

        self.start_tournament()
