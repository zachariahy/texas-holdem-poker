import treys
from .constants import Position, ACTION_STR_TO_ENUM, Action


class View:
    @staticmethod
    def print_player_info(player):
        print(f'---------- {player.name} ----------')
        print(f'POSITION: {[position.value for position in player.positions]}')
        if player.is_human:
            print('HOLE CARDS: ', end='')
            treys.Card.print_pretty_cards(player.hole_cards)
        print(f'STACK: {player.stack}')
        print(f'BET: {player.total_bet}')
        print(f"ACTION: {player.action.value if player.action else 'None'}")

    @staticmethod
    def print_available_actions(available_actions):
        print('AVAILABLE ACTIONS:')
        for action, amount in available_actions.items():
            if isinstance(amount, tuple):
                print('\t', action.value, amount)
            else:
                print('\t', action.value)

    @staticmethod
    def print_betting_history(bets):
        print(f'CURRENT BET: {bets.current}')
        print(f'LAST BET: {bets.last}')

    @staticmethod
    def print_positions(players_manager):
        print('POSITIONS')
        print(f'\tD: {players_manager.get_player_in_position(Position.DEALER_BUTTON).name}')
        print(f'\tSM: {players_manager.get_player_in_position(Position.SMALL_BLIND).name}')
        print(f'\tBB: {players_manager.get_player_in_position(Position.BIG_BLIND).name}')

    @staticmethod
    def get_player_counts():
        # bot_count = input('Bot count: ')
        # human_count = input('Human count: ')
        bot_count = 3
        human_count = 0

        return bot_count, human_count

    @staticmethod
    def get_player_choice(available_actions, stack):
        View.print_available_actions(available_actions)

        choice = input('Choice: ')
        choice = choice.split()

        action = ACTION_STR_TO_ENUM.get(choice[0].lower())
        if not action or action not in available_actions:
            return View.get_player_choice(available_actions, stack)
        if len(choice) == 2:
            add_bet = int(choice[1])
            if isinstance(available_actions[action], tuple) and add_bet not in range(*available_actions[action]):
                return View.get_player_choice(available_actions, stack)
        else:
            if isinstance(available_actions[action], tuple):
                return View.get_player_choice(available_actions, stack)
            add_bet = available_actions.get(action)

        if add_bet == stack:
            action = Action.ALL_IN

        return action, add_bet

    @classmethod
    def print_new_hand(cls):
        print('=============== NEW HAND ===============')

    @classmethod
    def print_stage(cls, stage):
        print(f'========== {stage} ==========')

    @classmethod
    def print_pots(cls, pots):
        print(f'POTS: {[pot.amount for pot in pots]}')

    @classmethod
    def print_community_cards(cls, community_cards):
        print("COMMUNITY CARDS: ", end='')
        treys.Card.print_pretty_cards(community_cards)

    @classmethod
    def print_uncontested(cls):
        print(f'========== UNCONTESTED ==========')

    @classmethod
    def print_showdown(cls):
        print(f'========== SHOWDOWN ==========')

    @classmethod
    def print_tournament(cls):
        print(f'==================== TOURNAMENT ====================')

    @classmethod
    def print_tournament_winner(cls, players):
        print(f'==================== {[player.name for player in players if player.stack][0]} wins the Tournament! ====================')

    @classmethod
    def print_player_choice(cls, action, additional_bet):
        print(f'\'{action.value} {additional_bet}\'\n')

    @classmethod
    def print_hand_winner(cls, player_name, total_amount, pot_name, hand):
        print(f'{player_name} wins {total_amount} from {pot_name} with a {hand}!')

    @classmethod
    def print_game_state(cls, stage, pots_manager, community_cards):
        View.print_stage(stage.name)
        View.print_pots(pots_manager.pots)
        View.print_community_cards(community_cards)
