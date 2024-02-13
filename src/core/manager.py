import treys
from src.core.bot import Bot
from src.core.constants import HOLE_CARD_COUNT, SMALLEST_CHIP_DENOMINATION_AMOUNT, BIG_BLIND_AMOUNT, Stage, Action, \
    MIN_BET_AMOUNT
from random import randint


class GameManager:
    def __init__(self, game_state):
        self.game_state = game_state
        self.evaluator = treys.Evaluator()

        self.advance_stage_needed = False
        self.hole_cards_needed = False
        self.community_cards_needed = False

    def deal_community_card(self):
        self.game_state.deck.draw(1)
        self.game_state.community_cards.extend(self.game_state.deck.draw(1))
        if len(self.game_state.community_cards) > 2:
            self.community_cards_needed = False

    def deal_hole_card(self):
        sb_index = self.game_state.players.index(self.game_state.positions.small_blind)
        players = self.game_state.players[sb_index:] + self.game_state.players[:sb_index]
        players_in_hand_needing_cards = [player for player in players if
                                         (player.stack_size or player.total_bet) and len(
                                             player.hole_cards) != HOLE_CARD_COUNT]

        if not players_in_hand_needing_cards:
            self.hole_cards_needed = False
            return

        card = self.game_state.deck.draw(1)

        for player in players_in_hand_needing_cards:
            if not player.hole_cards:
                player.hole_cards.extend(card)
                return

        for player in players_in_hand_needing_cards:
            player.hole_cards.extend(card)
            return

    def does_actor_have_option(self):
        is_actor_facing_raise = self.game_state.bets.last
        return (self.game_state.is_preflop_stage()
                and self.game_state.actor is self.game_state.positions.big_blind
                and not is_actor_facing_raise)

    def get_available_actions(self):
        if self.game_state.actor is None:
            return

        bets = self.game_state.bets
        stack_size = self.game_state.actor.stack_size
        total_bet = self.game_state.actor.total_bet

        min_raise = 2 * bets.current - bets.last
        is_actor_facing_bet = bets.current

        available_actions = {}

        if self.does_actor_have_option():
            available_actions[Action.CHECK] = 0

            if not self.game_state.is_less_two_active_players():
                if stack_size >= min_raise - total_bet:  # can afford difference
                    available_actions[Action.RAISE] = (min_raise - total_bet, stack_size)
                else:
                    available_actions[Action.ALL_IN] = stack_size

        elif is_actor_facing_bet:
            available_actions[Action.FOLD] = 0

            if stack_size >= bets.current - total_bet:  # can afford difference
                available_actions[Action.CALL] = bets.current - total_bet

            if not self.game_state.is_less_two_active_players():
                if stack_size >= min_raise - total_bet:  # can afford difference
                    available_actions[Action.RAISE] = (min_raise - total_bet, stack_size)
                elif bets.current - total_bet != stack_size:  # if call and all-in not the same
                    available_actions[Action.ALL_IN] = stack_size

        else:
            available_actions[Action.CHECK] = 0

            if stack_size >= MIN_BET_AMOUNT:  # can afford min bet
                available_actions[Action.BET] = (MIN_BET_AMOUNT, stack_size)
            else:
                available_actions[Action.ALL_IN] = stack_size

        return available_actions

    def assign_positions(self):
        player_count = len(self.game_state.players)

        dealer_index = randint(0, player_count - 1)
        small_blind_index = dealer_index if self.game_state.is_headsup() else (dealer_index + 1) % player_count
        big_blind_index = (small_blind_index + 1) % player_count

        self.game_state.positions.dealer = self.game_state.players[dealer_index]
        self.game_state.positions.small_blind = self.game_state.players[small_blind_index]
        self.game_state.positions.big_blind = self.game_state.players[big_blind_index]

    def get_next_player_with_stack(self, current_player):
        current_player_index = self.game_state.players.index(current_player)
        player_count = len(self.game_state.players)

        for offset in range(1, player_count):
            next_player_index = (current_player_index + offset) % player_count
            next_player = self.game_state.players[next_player_index]

            if next_player.stack_size:
                return next_player

    def rotate_positions(self):
        dealer = self.get_next_player_with_stack(self.game_state.positions.dealer)
        small_blind = dealer if self.game_state.is_headsup() else self.get_next_player_with_stack(dealer)
        big_blind = self.get_next_player_with_stack(small_blind)

        self.game_state.positions.dealer = dealer
        self.game_state.positions.small_blind = small_blind
        self.game_state.positions.big_blind = big_blind

    def assign_anchor(self):
        self.game_state.actor = self.game_state.positions.big_blind if self.game_state.is_preflop_stage() \
            else self.game_state.positions.dealer

    def rotate_actor(self):
        current_actor_index = self.game_state.players.index(self.game_state.actor)
        number_of_players = len(self.game_state.players)

        # for offset in range(1, number_of_players - 1):
        # for offset in range(1, number_of_players):
        for offset in range(1, number_of_players + 1):
            next_actor_index = (current_actor_index + offset) % number_of_players
            next_actor = self.game_state.players[next_actor_index]

            if next_actor.is_active():
                self.game_state.actor.is_acting = False
                self.game_state.actor = next_actor
                next_actor.is_acting = True
                return

        self.game_state.actor.is_acting = False
        self.game_state.actor = None

    def collect_bets(self):
        if not self.game_state.bets.is_bet():
            return

        for pot in self.game_state.pots:
            if pot.is_closed:
                continue

            for player in self.game_state.players:
                if player.is_folded() and player.total_bet:
                    pot.size += player.total_bet
                    player.total_bet = 0

            remaining_betting_players = [player for player in self.game_state.players if player.total_bet]
            smallest_bet = min([player.total_bet for player in remaining_betting_players])

            for player in remaining_betting_players:
                player.total_bet -= smallest_bet
                pot.size += smallest_bet

            remaining_betting_players = [player for player in self.game_state.players if player.total_bet]

            if remaining_betting_players:
                pot.is_closed = True
                self.game_state.create_pot(remaining_betting_players)

    def distribute_winnings(self):
        self.game_state.hand_results.clear()

        for pot in reversed(self.game_state.pots):
            eligible_players_not_folded = [player for player in pot.eligible_players if not player.is_folded()]
            strongest_hand = min([player.hand_strength for player in eligible_players_not_folded])

            # get winners and fold losers
            winners = []
            for player in eligible_players_not_folded:
                if player.hand_strength == strongest_hand:
                    winners.append(player)
                else:
                    player.fold()

            split_pot, odd_chips = divmod(pot.size, len(winners))

            for player in winners:
                player.stack_size += split_pot

                if odd_chips:
                    player.stack_size += SMALLEST_CHIP_DENOMINATION_AMOUNT
                    odd_chips -= SMALLEST_CHIP_DENOMINATION_AMOUNT
                    total_amount = split_pot + SMALLEST_CHIP_DENOMINATION_AMOUNT
                else:
                    total_amount = split_pot

                # record results of hand
                if player.hand and len(eligible_players_not_folded) != 1:
                    self.game_state.hand_results.append(
                        f'{player.name} wins ${total_amount} from {pot.name} with a {player.hand}!')
                else:
                    self.game_state.hand_results.append(
                        f'{player.name} wins ${total_amount} from {pot.name}!')

        self.game_state.pots.clear()

    def start_round(self):
        # reset action if active
        for player in self.game_state.players:
            if player.is_active():
                player.action = None
        self.set_bets()
        self.assign_anchor()
        self.rotate_actor()

    def is_round_over(self):
        # (OR no_actor,
        #     (AND actor.total_bet == current_bet,
        #          (OR actor_already_acted,
        #              no_other_active_players)),
        #     (AND actor_has_option
        #          under_two_active_players))
        return (not self.game_state.actor or
                (self.game_state.actor.total_bet == self.game_state.bets.current and
                 (self.game_state.actor.has_acted() or
                  self.game_state.is_less_two_active_players())) or
                self.does_actor_have_option() and self.game_state.is_less_two_active_players())

    def advance_stage(self):
        self.advance_stage_needed = False
        if self.is_hand_over():
            self.end_hand()
        elif self.game_state.stage == Stage.PREFLOP:
            self.game_state.stage = Stage.FLOP
            self.start_main_stage()
        elif self.game_state.stage == Stage.FLOP:
            self.game_state.stage = Stage.TURN
            self.start_main_stage()
        elif self.game_state.stage == Stage.TURN:
            self.game_state.stage = Stage.RIVER
            self.start_main_stage()
        elif self.game_state.stage == Stage.RIVER:
            self.end_hand()

    def end_round(self):
        if self.game_state.actor:
            self.game_state.actor.is_acting = False
            self.game_state.actor = None
        self.collect_bets()
        self.advance_stage_needed = True

    def start_preflop(self):
        self.game_state.stage = Stage.PREFLOP
        self.hole_cards_needed = True
        self.post_blinds()
        self.start_round()

    def start_main_stage(self):
        self.community_cards_needed = True
        if self.game_state.is_less_two_active_players():
            self.advance_stage_needed = True
        else:
            self.start_round()

    def evaluate_hands(self):
        for player in self.game_state.players:
            if not player.is_folded():
                player.hand_strength = self.evaluator.evaluate(player.hole_cards, self.game_state.community_cards)
                rank_class = self.evaluator.get_rank_class(player.hand_strength)
                player.hand = self.evaluator.class_to_string(rank_class)

    def start_showdown(self):
        self.game_state.stage = Stage.SHOWDOWN
        self.evaluate_hands()

    def start_hand(self):
        self.game_state.in_hand = True
        self.game_state.create_pot([player for player in self.game_state.players if player.stack_size])
        self.game_state.shuffle_deck()
        self.start_preflop()

    def is_hand_over(self):
        return self.game_state.is_single_player_not_folded()

    def end_hand(self):
        self.game_state.in_hand = False

        if not self.game_state.is_single_player_not_folded():
            self.start_showdown()

        self.distribute_winnings()

        # reset community cards
        self.game_state.community_cards.clear()

        # reset player hole cards, and if stack, action
        for player in self.game_state.players:
            player.hole_cards.clear()
            if player.stack_size:
                player.action = None

        # reset last action
        self.game_state.last_action = ''

        if self.game_state.is_single_player_with_stack():
            self.end_tournament()
        else:
            self.rotate_positions()

    def start_tournament(self):
        self.game_state.in_tournament = True
        self.assign_positions()
        self.start_hand()

    def end_tournament(self):
        self.game_state.in_tournament = False
        self.game_state.hand_results.clear()
        winner = [player for player in self.game_state.players if player.stack_size][0]
        self.game_state.hand_results.append(f'{winner.name} Wins the Tournament with a {winner.hand}!')

    def set_bets(self):
        self.game_state.bets.last = 0
        self.game_state.bets.current = BIG_BLIND_AMOUNT if self.game_state.is_preflop_stage() else 0

    def advance_turn(self):
        self.set_last_action()

        self.rotate_actor()

        if self.is_round_over():
            self.end_round()

    def bot_act(self):
        action, amount = Bot.get_random_action(self.get_available_actions())

        if action == Action.CHECK:
            self.check()
        elif action == Action.FOLD:
            self.fold()
        elif action == Action.BET:
            self.bet(amount)
        elif action == Action.CALL:
            self.call()
        elif action == Action.RAISE:
            self.raise_(amount)
        elif action == Action.ALL_IN:
            self.all_in()

    def post_blinds(self):
        self.game_state.positions.small_blind.post_small_blind()
        self.game_state.positions.big_blind.post_big_blind()

    def check(self):
        self.game_state.actor.check()
        self.advance_turn()

    def fold(self):
        self.game_state.actor.fold()
        self.advance_turn()

    def bet(self, add_bet):
        self.game_state.actor.bet(add_bet)
        self.game_state.bets.update(self.game_state.actor.total_bet)
        self.advance_turn()

    def call(self):
        add_bet = self.game_state.bets.current - self.game_state.actor.total_bet
        self.game_state.actor.call(add_bet)
        self.advance_turn()

    def raise_(self, add_bet):
        self.game_state.actor.raise_(add_bet)
        self.game_state.bets.update(self.game_state.actor.total_bet)
        self.advance_turn()

    def all_in(self):
        self.game_state.actor.all_in()
        self.game_state.bets.update(self.game_state.actor.total_bet)
        self.advance_turn()

    def set_last_action(self):
        if self.game_state.actor and self.game_state.actor.action:
            if self.game_state.actor.action in [Action.FOLD, Action.CHECK]:
                action = f'{self.game_state.actor.name} {self.game_state.actor.action.value.lower()}s.'
            elif self.game_state.actor.is_all_in():
                action = f'{self.game_state.actor.name} goes all-in for ${self.game_state.actor.total_bet}!'
            elif self.game_state.actor.action == Action.RAISE:
                action = f'{self.game_state.actor.name} raises to ${self.game_state.actor.total_bet}.'
            else:
                action = f'{self.game_state.actor.name} {self.game_state.actor.action.value.lower()}s ${self.game_state.actor.total_bet}.'
            self.game_state.last_action = action

    def update(self, dt):
        if self.hole_cards_needed or self.community_cards_needed:
            return

        elif self.game_state.actor and not self.game_state.actor.is_human:
            self.bot_act()

        elif self.advance_stage_needed:
            self.advance_stage()

    def deal(self, dt):
        if self.hole_cards_needed:
            self.deal_hole_card()

        elif self.community_cards_needed:
            self.deal_community_card()
