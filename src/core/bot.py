import random


class Bot:
    @staticmethod
    def get_random_action(available_actions):
        action = random.choice(list(available_actions.keys()))
        add_bet = available_actions[action]

        if isinstance(add_bet, tuple):
            add_bet = random.randint(add_bet[0], add_bet[1])

        return action, add_bet
