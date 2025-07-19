from enum import Enum

# global configuration variables.
BLACKJACK_VALUE = 21
DEALER_STAND_VALUE = 17

# MODIFIABLE: game rules
NUM_DECKS = 2
NUM_CARDS_PER_DECK = 52
MINIMUM_BET_AMOUNT = 2
MAXIMUM_BET_AMOUNT = 500
PAYOUT_RATIO_BLACKJACK_TO_PLAYER = 1.5
PAYOUT_RATIO_BLACKJACK_SPLIT_PAIRS = 1.0
PAYOUT_RATIO_BLACKJACK_TO_DEALER = 1.0
# RATIO_SIDE_BET_TO_MAIN_BET = 0.5
INITIAL_BET = 10_000
POSSIBLE_BETS = (10, 20, 50, 100)

# card rank value dict
cards_rank_value_dict = {
    '2': 2,
    '3': 3,
    '4': 4,
    '5': 5,
    '6': 6,
    '7': 7,
    '8': 8,
    '9': 9,
    '10': 10,
    'J': 10,
    'Q': 10,
    'K': 10,
    'A': 11
}

card_suits = ('Hearts', 'Diamonds', 'Clubs', 'Spades')

# DECISIONS
class Decision(Enum):
    HIT = 'hit'
    STAND = 'stand'
    DOUBLE_DOWN = 'double-down'
    SPLIT = 'split'
    SURRENDER = 'surrender'