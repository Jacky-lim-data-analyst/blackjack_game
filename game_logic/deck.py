# define a deck class. Responsible for creating a standard 52-card deck (for multiple decks),
# shuffling the deck and dealing cards.

from config import NUM_DECKS, NUM_CARDS_PER_DECK, card_suits, cards_rank_value_dict
from .card import Card
import random

class Deck:
    def __init__(self):
        self.num_decks = NUM_DECKS
        self.num_cards = NUM_CARDS_PER_DECK * self.num_decks
        self.cards = []
        self.create_deck()
    
    def create_deck(self):
        """
        Initialize the deck comprising self.num_cards
        """
        for _ in range(self.num_decks):
            for suit in card_suits:
                for rank in cards_rank_value_dict.keys():
                    self.cards.append(Card(suit, rank))
    
    def shuffle(self):
        """
        Shuffle the deck
        """
        random.shuffle(self.cards)

    def deal_card(self):
        """
        Deal a card from the deck
        """
        return self.cards.pop()