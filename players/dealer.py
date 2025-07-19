# Inherits from base_player.Player base class. Its make_decision() method will implement
# the fixed dealer rules.
from typing import Optional
from .base_player import Player
from game_logic.hand import Hand
from game_logic.card import Card
from config import Decision

class Dealer(Player):
    """
    Represents the dealer in a Blackjack game.
    Inherits from the Player class and implements the dealer's fixed playing rules
    """
    def __init__(self):
        super().__init__(name="Dealer", chips=1_000)

    def get_upcard(self):
        """Returns the upcard of the dealer's hand."""
        return self.hand[0].cards[0]

    def get_possible_decisions(self):
        pass

    def make_decision_insurance(self, context = None):
        pass

    def make_decision(self, hand: Hand, dealer_upcard: Card, context: Optional[dict]=None):
        """
        Implements the dealer's fixed playing rules based on their hand.
        The dealer must hit until their hand value is 17 or more.

        Args:
            dealer_upcard (Card): The upcard of the dealer. This is not
                used for the dealer's decision but is kept for compatibility with 
                the parent Player class's method signature.

        Returns:
            str: 'hit' if the dealer must hit, 'stand' otherwise.
        """
        hand_value = self.get_hand_value()
        if hand_value < 17:
            return Decision.HIT
        return Decision.STAND