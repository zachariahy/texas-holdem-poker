from .constants import Action, SMALLEST_CHIP_DENOMINATION_AMOUNT
from .console_view import View


class Pot:
    def __init__(self, eligible_players, name):
        self.name = name
        self.size = 0
        self.eligible_players = eligible_players
        self.is_closed = False


class PotsManager:
    def __init__(self, main_pot_eligible_players):
        self.pots = []
        self.side_pot_count = 0

        self.create_main_pot(main_pot_eligible_players)

    def create_main_pot(self, eligible_players):
        main_pot = Pot(eligible_players, "the Main Pot")
        self.pots.append(main_pot)

    def create_side_pot(self, eligible_players):
        self.side_pot_count += 1
        side_pot = Pot(eligible_players, f'Side Pot {self.side_pot_count}')
        self.pots.append(side_pot)

    def collect_bets(self, players_manager):
        if not players_manager.is_bet():
            return

        players = players_manager.players

        for pot in self.pots:
            if pot.is_closed:
                continue

            for player in players:
                if player.action == Action.FOLD and player.total_bet:
                    pot.size += player.total_bet
                    player.total_bet = 0

            betting_players = [player for player in players if player.total_bet]
            smallest_bet = min([player.total_bet for player in betting_players])

            for player in betting_players:
                player.total_bet -= smallest_bet
                pot.size += smallest_bet

            betting_players = [player for player in players if player.total_bet]

            if betting_players:
                pot.is_closed = True
                self.create_side_pot(betting_players)
            else:
                return

    def award_winners(self):
        for pot in reversed(self.pots):
            eligible_players_not_folded = [player for player in pot.eligible_players if player.action != Action.FOLD]
            strongest_hand = min([player.hand_strength for player in eligible_players_not_folded])

            # get winners and fold losers
            winners = []
            for player in eligible_players_not_folded:
                if player.hand_strength == strongest_hand:
                    winners.append(player)
                else:
                    player.action = Action.FOLD

            split_pot, odd_chips = divmod(pot.size, len(winners))

            for player in winners:
                player.stack_size += split_pot

                if odd_chips:  # TODO award odd chips starting with winner left of dealer
                    player.stack_size += SMALLEST_CHIP_DENOMINATION_AMOUNT
                    odd_chips -= SMALLEST_CHIP_DENOMINATION_AMOUNT
                    total_amount = split_pot + SMALLEST_CHIP_DENOMINATION_AMOUNT
                else:
                    total_amount = split_pot

                View.print_hand_winner(player.name, total_amount, pot.name, player.hand)
