# a BasicStrategyPlayer class that implements standard Blackjack basic strategy.
# Its make_decision() method would use a predefined strategy chart to decide whether to
# hit, stand or double down based on his hands and the dealer's upcard.

import random
from typing import Optional
from .base_player import Player
from game_logic.card import Card
from game_logic.hand import Hand
from game_logic.deck import Deck
from config import Decision, NUM_DECKS, NUM_CARDS_PER_DECK

class BasicStrategyPlayer(Player):
    """
    Player class that acts rationally based on some well-known "good" strategy.
    """
    def __init__(self, name, chips = 1000):
        super().__init__(name, chips)

    def get_possible_decisions(self, hand_index = 0):
        return super().get_possible_decisions(hand_index)
    
    def make_decision_insurance(self, context=None):
        """Rational decision to side-bet insurance"""
        # always chose not to bet insurance if no context given
        if context is None:
            return False
        
        cards_in_play = context["cards_in_play"]
        
        prob_10s = self._calculate_prob_hc(cards_in_play)
        
        if prob_10s >= 0.3:
            return True
        return False
    
    def _calculate_prob_hc(self, cards: list[Card]):
        """Calculate the probability of hole card being a value of 10, making dealer Blackjack
        
        Args:
            cards (list[Card]): List of cards
            
        Return:
            float representing the probability of hole card being a value of 10"""
        total_cards = NUM_DECKS * NUM_CARDS_PER_DECK
        remaining_num_cards_in_deck = total_cards - len(cards)

        possible_cards = [card for card in Deck().cards if card not in cards]
        num_10s_in_deck = sum(1 for card in possible_cards if card.rank in ['10', 'J', 'Q', 'K'])
        return num_10s_in_deck / remaining_num_cards_in_deck

    def make_decision(self, hand: Hand, dealer_upcard: Card, context: Optional[dict] = None):
        """
        Decides on the next action based on basic Blackjack strategy.
        It considers hard totals, soft totals (with an Ace), and pairs
        Uses randomness with weights for some decisions to simulate uncertainty
        This decision logic comes from: 
        
        Args:
            dealer_upcard (Card): The upcard of the dealer

        Returns:
            str: The decision made 
        """
        player_hand = hand
        player_value = player_hand.calculate_total_value()
        dealer_value = dealer_upcard.get_value()

        possible_decisions = self.get_possible_decisions()

        # 1. Check for splitting pairs
        if Decision.SPLIT in possible_decisions:
            pair_card = player_hand.cards[0]

            # always split Aces and 8s
            if pair_card.rank == 'A' or pair_card.rank == '8':
                return Decision.SPLIT
            
            if pair_card.rank in ['10', 'J', 'Q', 'K']:
                return Decision.STAND
            
            if pair_card.rank == '5' or pair_card.rank == '4':
                return Decision.HIT
            
            # split 9s against dealer 2-6 or 8-9
            if pair_card.rank == '9':
                if dealer_value in [2, 3, 4, 5, 6, 8, 9]:
                    return Decision.SPLIT
                else:  # stand against 7, 10, ace
                    return Decision.STAND
                
            if pair_card.rank == '7':
                if player_value in range(2, 8):
                    return Decision.SPLIT
                else:
                    # random prob between stand and hit
                    return random.choice([Decision.SPLIT, Decision.HIT])
            
            if pair_card.rank == '6':
                if player_value in range(3, 7):
                    return Decision.SPLIT
                else:
                    return Decision.HIT
            
            if pair_card.rank == '2' or pair_card.rank == '3':
                if player_value in range(4, 8):
                    return Decision.SPLIT
                else:
                    return Decision.HIT

        # 2. Check for soft totals (hand with an Ace counted as 11)
        if player_hand.is_soft():
            if player_value >= 19:  # A,8 or A,9
                return Decision.STAND
            elif player_value == 18:  # A,7
                if dealer_value in [3, 4, 5, 6] and Decision.DOUBLE_DOWN in possible_decisions:
                    return Decision.DOUBLE_DOWN
                if dealer_value in [2, 7, 8]:
                    return Decision.STAND
                else:  # hit against 9, 10, A
                    return Decision.HIT
            elif player_value == 17:  # A,6
                if dealer_value in [3, 4, 5, 6] and Decision.DOUBLE_DOWN in possible_decisions:
                    return Decision.DOUBLE_DOWN
                return Decision.HIT
            elif player_value == 16 or player_value == 15:  # A,5 or A,4
                if dealer_value in [4, 5, 6] and Decision.DOUBLE_DOWN in possible_decisions:
                    return Decision.DOUBLE_DOWN
                return Decision.HIT
            elif player_value == 14 or player_value == 13:  # A,3 or A,2
                if dealer_value in [5, 6] and Decision.DOUBLE_DOWN in possible_decisions:
                    return Decision.DOUBLE_DOWN
                return Decision.HIT
            
        # 3. Handle hard totals (no ace or ace counted as 1)
        if player_value == 17:
            return Decision.STAND

        elif 13 <= player_value <= 16:
            if player_value == 16 and dealer_value in range(9, 12):
                return Decision.SURRENDER
            if player_value == 15 and dealer_value == 10:
                return Decision.SURRENDER
            if 2 <= dealer_value <= 6:
                return Decision.STAND
            else:
                return Decision.HIT
        elif player_value == 12:
            if 4 <= dealer_value <= 6:
                return Decision.STAND
            else:
                return Decision.HIT
        elif player_value == 11:
            if dealer_value != 11 and Decision.DOUBLE_DOWN in possible_decisions:
                return Decision.DOUBLE_DOWN
            else:
                return Decision.HIT
        elif player_value == 10:
            if 2 <= dealer_value <= 9 and Decision.DOUBLE_DOWN in possible_decisions:
                return Decision.DOUBLE_DOWN
            else:
                return Decision.HIT
        elif player_value == 9:
            if 3 <= dealer_value <= 6 and Decision.DOUBLE_DOWN in possible_decisions:
                return Decision.DOUBLE_DOWN
            else:
                return Decision.HIT
        elif player_value == 8:
            return Decision.HIT
        
        if player_value < 17:
            if Decision.HIT in possible_decisions:
                return Decision.HIT
            else:
                return Decision.STAND
        
        return random.choice(possible_decisions)