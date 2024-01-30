from enum import Enum


class Action(Enum):
    FOLD = 'Fold'
    CHECK = 'Check'
    BET = 'Bet'
    CALL = 'Call'
    RAISE = 'Raise'
    ALL_IN = 'All-in'
    POST_BLIND = 'Post-blind'


class Position(Enum):
    DEALER_BUTTON = 'D'
    SMALL_BLIND = 'SB'
    BIG_BLIND = 'BB'


class Stage(Enum):
    PREFLOP = 'Preflop'
    FLOP = 'Flop'
    TURN = 'Turn'
    RIVER = 'River'
    SHOWDOWN = 'Showdown'


ACTION_STR_TO_ENUM = {'fold': Action.FOLD,
                      'check': Action.CHECK,
                      'bet': Action.BET,
                      'call': Action.CALL,
                      'raise': Action.RAISE,
                      'all-in': Action.ALL_IN
                      }

HOLE_CARD_COUNT = 2

SMALLEST_CHIP_DENOMINATION_AMOUNT = 1
SMALL_BLIND_AMOUNT = 1
BIG_BLIND_AMOUNT = 2 * SMALL_BLIND_AMOUNT
BUY_IN_AMOUNT = 40 * BIG_BLIND_AMOUNT
MIN_BET_AMOUNT = BIG_BLIND_AMOUNT

THREE_POSITIONS = [[Position.DEALER_BUTTON], [Position.SMALL_BLIND], [Position.BIG_BLIND]]
TWO_POSITIONS = [[Position.DEALER_BUTTON, Position.SMALL_BLIND], [Position.BIG_BLIND]]
BLIND_POSITIONS = [Position.SMALL_BLIND, Position.BIG_BLIND]
BLIND_POS_TO_AMOUNT = {Position.SMALL_BLIND: SMALL_BLIND_AMOUNT,
                       Position.BIG_BLIND: BIG_BLIND_AMOUNT
                       }

MAIN_STAGES = [Stage.FLOP, Stage.TURN, Stage.RIVER]