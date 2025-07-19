# define a hand class to represent cards held by a player or a dealer. 
# Method to add cards and calculate total value of hand

from .card import Card
from config import BLACKJACK_VALUE

class Hand:
    def __init__(self):
        """"""
        # starts with empty hand
        self.cards: list[Card] = []
    
    def add_card(self, card: Card):
        self.cards.append(card)

    def get_num_cards(self):
        return len(self.cards)
    
    def is_two_cards_similar(self):
        if self.get_num_cards() == 2:
            card1_rank = self.cards[0].rank
            card2_rank = self.cards[1].rank
            return card1_rank == card2_rank
        return False
    
    def split(self):
        """Removes and returns one card from the hand for splitting"""
        if self.get_num_cards() == 2:
            return self.cards.pop()
        return None

    def calculate_total_value(self):
        """Calculates the total value of the hand, accounting for aces.
        Aces are 11 unless that would cause a bust, in which case they are 1"""
        value = 0
        num_aces = 0

        for card in self.cards:
            value += card.get_value()
            if card.rank == 'A':
                num_aces += 1

        while value > BLACKJACK_VALUE and num_aces > 0:
            value -= 10
            num_aces -= 1
        
        return value
    
    def is_soft(self):
        """
        Checks if a hand is "soft" or not: whether 'A' can be considered as 11
        """
        value = 0
        num_aces = 0

        for card in self.cards:
            value += card.get_value()
            if card.rank == 'A':
                num_aces += 1

        return num_aces > 0 and value <= BLACKJACK_VALUE
    
    def __str__(self):
        return ", ".join(str(card) for card in self.cards) if self.cards else "Empty Hand"
    
    def __repr__(self):
        return self.__str__()
    
    