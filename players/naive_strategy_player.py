# a naive strategy player

import random

from .base_player import Player
from config import Decision, POSSIBLE_BETS

class NaiveStrategyPlayer(Player):
    def __init__(self, name, chips):
        super().__init__(name, chips)
        # self.type = PlayerTypes.NAIVE

    def choose_bets(self):
        return random.choice(POSSIBLE_BETS)

    def make_decision_insurance(self, context = None):
        return random.choice([True, False])

    def get_possible_decisions(self, hand_index = 0):
        return super().get_possible_decisions(hand_index)

    def make_decision(self, hand=None, dealer_upcard = None, context = None) -> Decision:
        possible_decisions = self.get_possible_decisions()

        if not possible_decisions:
            return Decision.STAND
        
        return random.choice(possible_decisions)
