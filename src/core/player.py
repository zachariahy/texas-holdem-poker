from .constants import Action, Stage, Position, MIN_BET_AMOUNT, BLIND_POSITIONS, BLIND_POS_TO_AMOUNT, BUY_IN_AMOUNT, \
    TWO_POSITIONS, THREE_POSITIONS
import random


class Player:
    def __init__(self, name, is_human, stack):
        self.name = name
        self.is_human = is_human
        self.stack = stack
        self.hole_cards = []

        self.positions = []
        self.action = None
        self.total_bet = 0

        self.hand = None
        self.hand_strength = None

    def is_response_needed(self, current_bet):
        if self.action in [None, Action.POST_BLIND] or self.total_bet < current_bet:
            return True
        return False

    def get_available_actions(self, bets, stage):
        min_raise = 2 * bets.current - bets.last
        facing_bet = bets.current
        facing_raise = bets.last
        has_the_option = stage == Stage.PREFLOP and Position.BIG_BLIND in self.positions and not facing_raise

        available_actions = {}

        if has_the_option:
            available_actions[Action.CHECK] = 0

            if self.stack >= min_raise - self.total_bet:  # can afford difference
                available_actions[Action.RAISE] = (min_raise - self.total_bet, self.stack)
            else:
                available_actions[Action.ALL_IN] = self.stack

        elif facing_bet:
            available_actions[Action.FOLD] = 0

            if self.stack >= bets.current - self.total_bet:  # can afford difference
                available_actions[Action.CALL] = bets.current - self.total_bet

            if self.stack >= min_raise - self.total_bet:  # can afford difference
                available_actions[Action.RAISE] = (min_raise - self.total_bet, self.stack)
            else:
                available_actions[Action.ALL_IN] = self.stack

        else:
            available_actions[Action.CHECK] = 0

            if self.stack >= MIN_BET_AMOUNT:  # can afford min bet
                available_actions[Action.BET] = (MIN_BET_AMOUNT, self.stack)
            else:
                available_actions[Action.ALL_IN] = self.stack

        return available_actions

    def execute_action(self, action, add_bet):
        self.action = action
        self.total_bet += add_bet
        self.stack -= add_bet

        if action == Action.FOLD:
            self.hole_cards = []

    def execute_post_blind(self):  # if blind amount >= player stack, player action is all-in
        blind_position = [position for position in self.positions if position in BLIND_POSITIONS].pop()
        blind_amount = BLIND_POS_TO_AMOUNT[blind_position]
        bet_amount = min(blind_amount, self.stack)

        if bet_amount == self.stack:
            action = Action.ALL_IN
        else:
            action = Action.POST_BLIND

        self.execute_action(action, bet_amount)

    def get_random_choice(self, available_actions):
        action = random.choice(list(available_actions.keys()))
        add_bet = available_actions[action]

        if isinstance(add_bet, tuple):
            add_bet = random.randint(add_bet[0], add_bet[1])

        if add_bet == self.stack:
            action = Action.ALL_IN

        return action, add_bet


class PlayersManager:
    PLAYER_NAMES = 'Greg Zach Tom Ethan Paul Sofia Marie Julia Grace'.split()

    def __init__(self, bot_count, human_count):
        self.players = None
        self.acting_player = None
        self.add_players(bot_count, human_count)

    def add_players(self, bot_count, human_count):
        players = []
        for i in range(bot_count):
            player = Player(self.PLAYER_NAMES[i], False, BUY_IN_AMOUNT)
            players.append(player)

        for i in range(1, human_count + 1):
            player = Player(f'Player {i}', True, BUY_IN_AMOUNT)
            players.append(player)

        self.players = players

    def get_player_in_position(self, position):
        for player in self.players:
            if position in player.positions:
                return player

    def get_active_players(self):
        return [player for player in self.players if player.action not in [Action.FOLD, Action.ALL_IN]]

    def get_first_acting_player(self, stage):
        if stage == Stage.PREFLOP:
            big_blind_player = self.get_player_in_position(Position.BIG_BLIND)
            return self.get_next_active_player(big_blind_player)
        else:
            dealer_button_player = self.get_player_in_position(Position.DEALER_BUTTON)
            return self.get_next_active_player(dealer_button_player)

    def get_next_active_player(self, current_player):
        index = self.players.index(current_player)
        number_of_players = len(self.players)

        for i in range(1, number_of_players + 1):
            index = (index + 1) % number_of_players
            player = self.players[index]

            if player.stack and player.action not in [Action.FOLD, Action.ALL_IN]:
                return player

    def is_single_active_player(self):  # active means not folded or all-in and able to continue betting or acting
        return len([player for player in self.players if player.action not in [Action.FOLD, Action.ALL_IN]]) == 1

    def get_players_not_folded(self):
        return [player for player in self.players if player.action != Action.FOLD]

    def is_single_player_not_folded(self):
        return len(self.get_players_not_folded()) == 1

    def is_bet(self):
        for player in self.players:
            if player.total_bet:
                return True
        return False

    def get_players_with_stack(self):
        return [player for player in self.players if player.stack]

    def is_single_player_with_stack(self):
        return len(self.get_players_with_stack()) == 1

    def get_next_player_with_stack(self, current_player):
        index = self.players.index(current_player)
        number_of_players = len(self.players)

        for i in range(1, number_of_players + 1):
            index = (index + 1) % number_of_players
            player = self.players[index]

            if player.stack:
                return player

    def get_positions(self):
        if len(self.get_players_with_stack()) == 2:
            return TWO_POSITIONS
        else:
            return THREE_POSITIONS

    def assign_positions(self):
        number_of_players = len(self.players)
        player_index = random.randint(0, number_of_players - 1)
        positions = self.get_positions()

        for position in positions:
            player = self.players[player_index]
            player.positions = position
            player_index = (player_index + 1) % number_of_players

    def rotate_positions(self):
        current_player = self.get_player_in_position(Position.DEALER_BUTTON)

        # clear old player positions
        for position in Position:
            player = self.get_player_in_position(position)
            if player:
                player.positions = []

        positions = self.get_positions()

        # assign new player positions
        for position in positions:
            current_player = self.get_next_player_with_stack(current_player)
            current_player.positions = position

    def post_blinds(self):
        for blind_position in BLIND_POSITIONS:
            blind_player = self.get_player_in_position(blind_position)
            blind_player.execute_post_blind()

    def reset_hole_cards(self):
        for player in self.players:
            player.hole_cards = []

    @staticmethod
    def reset_actions(players):
        for player in players:
            player.action = None
