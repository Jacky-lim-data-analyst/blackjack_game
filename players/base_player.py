# defines an abstract Player base class. This class will define the common interface 
# for all player types, such as make_decision() method.

from abc import ABC, abstractmethod
from game_logic.card import Card
from game_logic.hand import Hand
from config import Decision, BLACKJACK_VALUE
from typing import Optional

class Player(ABC):
    """
    An abstract base class for a player in a Blackjack game.
    It defines the common interface for all player types.
    """
    def __init__(self, name: str, chips: int = 1000):
        """
        Initializes a Player object.

        Args:
            name (str): The name of the player.
            chips (int, optional): The value of chips the player has. Defaults to 1000.
        """
        self.name = name
        self.chips = chips
        self.hand = [Hand()]
        self.bets = []
        # Insurance bet
        self.insurance_bet = 0
    
    # other players' cards are also visible
    @abstractmethod
    def make_decision(self, hand: Hand, dealer_upcard: Card, context: Optional[dict] = None):
        """
        Decides on the next action (e.g. 'hit', 'stand', 'double-down', 'split', 'side-bet (insurance)' and 'surrender') for the player.
        This method must be implemented by subclasses.

        Args:
            hand (Hand): The player's hand.
            dealer_upcard (Card): The upcard of the dealer's hand.
            context (dict, optional): Additional context for decision-making. Defaults to None.

        Returns:
            Decision (enum): The decision made by the player.
        """
        pass

    @abstractmethod
    def make_decision_insurance(self, context: Optional[dict] = None) -> bool:
        """
        Decides on whether to place an insurance bet.

        Args:
            dealer_upcard (Card): The upcard of the dealer's hand.
            context (dict, optional): Additional context for decision-making. Defaults to None.

        Returns:
            bool: True if an insurance bet is placed, False otherwise.
        """ 
        pass

    @abstractmethod
    def get_possible_decisions(self, hand_index: int = 0) -> list[Decision]:
        """
        Calculates and returns a list of valid decisions for the player's current hand.
        
        Returns:
            list[Decision]: A list of valid decisions.
        """
        current_hand = self.hand[hand_index]
        current_bet = self.bets[hand_index]

        # No decisions if busted
        if current_hand.calculate_total_value() > BLACKJACK_VALUE:
            return []
        
        if current_hand.calculate_total_value == BLACKJACK_VALUE:
            return [Decision.STAND]
        
        # start with 2-cards hand first
        if current_hand.get_num_cards() == 2:
            # possible actions for normal 2-card hand
            decisions = [Decision.HIT, Decision.STAND, Decision.SURRENDER]
            # can only double down if chips are sufficient
            if self.chips >= current_bet:
                decisions.append(Decision.DOUBLE_DOWN)
            # can only split if cards rank match and chips are sufficient
            if self.chips >= current_bet and current_hand.is_two_cards_similar():
                decisions.append(Decision.SPLIT)
            return decisions
        
        # more than 2 cards
        if current_hand.get_num_cards() > 2:
            return [Decision.HIT, Decision.STAND] 
        
        return []  # should not reach here
        
    def can_split(self, hand: Hand):
        """Checks if a given hand can be split"""
        return hand.is_two_cards_similar() and self.chips >= self.bets[self.hand.index(hand)]
    
    def split_hand(self, hand_index: int):
        """Split a hand into two hands"""
        try:
            original_hand = self.hand[hand_index]
            original_bet = self.bets[hand_index]
            split_card = original_hand.split()

            if split_card is None:
                print("Split card not available")
                return False

            if not self.can_split(original_hand):
                return False

            # create a new hand with one of the cards
            new_hand = Hand()
            new_hand.add_card(split_card)

            # add a new hand and a new bet
            self.hand.append(new_hand)
            self.place_bet(original_bet, is_split_bet=True)

            return True
        except Exception as e:
            print(f"Error during hand splitting: {e}")
            return False

    def place_bet(self, bet_amount: int, is_split_bet: bool = False):
        """Place the bet for current round or for a split"""
        if bet_amount <= 0:
            raise ValueError("Bet amount must be positive.")
        if bet_amount > self.chips:
            raise ValueError(f"Bet amount {bet_amount} exceeds available chips {self.chips}.")
        
        if not is_split_bet:
            self.bets = [bet_amount]
        else:
            self.bets.append(bet_amount)
        
        self.chips -= bet_amount

    def place_insurance_bet(self):
        """
        Places an insurance bet, which is half of the original main bet.
        Returns True if the bet is successfully placed, False otherwise.
        """
        # insurance is based on the initial bet of the first hand
        original_bet = self.bets[0]
        insurance_amount = original_bet / 2
        if insurance_amount > self.chips:
            print(f"{self.name} does not have enough chips to place an insurance bet.")
            return False
        
        self.insurance_bet = insurance_amount
        self.chips -= insurance_amount
        print(f"{self.name} placed an insurance bet of ${insurance_amount}.")
        return True

    def add_card_to_hand(self, card: Card, hand_index: int = 0):
        """Adds a card to the player's hand and update their status"""
        self.hand[hand_index].add_card(card)

    def get_hand_value(self, hand_index: int = 0):
        """Calculates and returns total value of the player's hand"""
        return self.hand[hand_index].calculate_total_value()
    
    def reset_for_new_round(self):
        """Resets the player hand and status for a new round"""
        self.hand = [Hand()]
        self.bets = []
    
    def has_blackjack(self) -> bool:
        """
        Checks whether player has blackjack
        """
        hand = self.hand[0]
        return hand.get_num_cards() == 2 and hand.calculate_total_value() == BLACKJACK_VALUE
    
    def update_balance(self, amount: int | float):
        self.chips += amount
    
    def __str__(self):
        hand_strs = [f"Hand {i+1}: {hand} (Bet: {self.bets[i]})" for i, hand in enumerate(self.hand)]
        insurance_str = f", Insurance: {self.insurance_bet}" if self.insurance_bet > 0 else ""
        return f"Player: {self.name}, Chips: {self.chips}, Hands: [{'; '.join(hand_strs)}]{insurance_str}"
    
