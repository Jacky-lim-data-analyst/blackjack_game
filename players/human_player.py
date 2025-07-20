from typing import Optional
from .base_player import Player
from game_logic.hand import Hand
from game_logic.card import Card
from config import Decision, BLACKJACK_VALUE, POSSIBLE_BETS

class HumanPlayer(Player):
    """
    Represents a human player in the Blackjack game.
    This player type will prompt the user for decisions.
    """
    def __init__(self, name, chips):
        super().__init__(name, chips)
        # self.type = PlayerTypes.HUMAN

    def choose_bets(self):
        """Prompts human player to choose bet amounts"""
        print(f"\n{'=' * 50}")
        print(f"CHOOSE YOUR BETS: {POSSIBLE_BETS}")
        print(f"\n{'=' * 50}")

        while True:
            user_input = input("What bet amount would you take? ")

            try:
                number_input = int(user_input)
                if number_input in POSSIBLE_BETS:
                    return number_input
                print("Please just enter the valid bets: ", POSSIBLE_BETS)
            except ValueError:
                print("Please enter valid bet amounts: ", POSSIBLE_BETS)


    def make_decision_insurance(self, context = None):
        """
        Prompts the human player to decide whether to place an insurance bet.
        """
        if context is None:
            print("No context given. You can't decide on whether to side-bet insurance")
            return False
        # extract info from context
        cards_in_play = context.get("cards_in_play", [])
        num_players = context.get("num_players", 1)

        # calculate insurance bet amount (half of original bet)
        original_bet = self.bets[0] if self.bets else 0
        insurance_amount = original_bet / 2

        print(f"\n{'='*50}")
        print("INSURANCE BET OPPORTUNITY")
        print(f"{'='*50}")

        # display game state info
        print(f"Cards in play: {cards_in_play}")
        print(f"Number of players: {num_players}")
        print(f"Your hand: {self.hand[0]} (Value: {self.hand[0].calculate_total_value()}")
        print(f"Your current bet: ${original_bet}")
        print(f"Insurance bet amount: ${insurance_amount}")
        print(f"Your remaining chips: ${self.chips}")

        # checks if player has enough chips for insurance
        if insurance_amount > self.chips:
            print(f"\nYou don't have enough chips to place an insurance bet.")
            print(f"Insurance requires ${insurance_amount}, but you only have ${self.chips}.")
            return False
        
        print(f"\nInsurance pays 2:1 if the dealer has blackjack.")
        print(f"If you take insurance and the dealer has blackjack, you'll win ${insurance_amount * 2}.")
        print(f"If the dealer doesn't have blackjack, you'll lose your insurance bet of ${insurance_amount}.")

        # get user input
        while True:
            user_input = input(f"\n{self.name}, do you want to place an insurance bet? (y/n): ").lower().strip()

            if user_input == 'y':
                return True
            elif user_input == 'n':
                return False
            else:
                print("Invalid input. Please enter 'y'/'yes' or 'n'/'no'.")

    def get_possible_decisions(self, hand_index = 0):
        return super().get_possible_decisions(hand_index)

    def make_decision(self, hand: Hand, dealer_upcard: Card, context: Optional[dict]=None):
        """
        Prompts the human player to make a decision based on available options.

        Args:
            hand (Hand): The player's hand.
            dealer_upcard (Card): The upcard of the dealer's hand.

        Returns:
            str: The decision made by the player.
        """
        # find the hand index
        hand_index = self.hand.index(hand) if hand in self.hand else 0

        # get possible decisions from parent class
        possible_decisions = self.get_possible_decisions(hand_index)

        # if no decisions available (busted or blackjack), return stand
        if not possible_decisions:
            return Decision.STAND
        
        # create a mapping of input characters to decisions
        decision_mapping = {
            'h': Decision.HIT,
            's': Decision.STAND,
            'd': Decision.DOUBLE_DOWN,
            'p': Decision.SPLIT,
            'r': Decision.SURRENDER
        }

        # create a display mapping for decision names
        decision_display = {
            Decision.HIT: '(H)it',
            Decision.STAND: '(S)tand',
            Decision.DOUBLE_DOWN: '(D)ouble Down',
            Decision.SPLIT: 'S(P)lit',
            Decision.SURRENDER: 'Su(R)render'
        }
        
        while True:
            print(f"\n{self.name}, your hand: {hand} (Value: {hand.calculate_total_value()})")
            if dealer_upcard:
                print(f"Dealer's upcard: {dealer_upcard}")
            print(f"Current bet: {self.bets[hand_index]} chips")
            print(f"Remaining chips: {self.chips}")

            # display available decisions
            print("\nAvailable decisions:")
            valid_chars = []
            for decision in possible_decisions:
                for char, mapped_decision in decision_mapping.items():
                    if decision == mapped_decision:
                        print(f"  {decision_display[decision]}")
                        valid_chars.append(char)
                        break

            # get user input
            user_input = input("Do you want to (h)it or (s)tand? ").lower().strip()

            if user_input in valid_chars:
                selected_decision = decision_mapping[user_input]
                
                # print the decision made
                decision_name = selected_decision.value.replace('-', ' ').title()
                print(f"{self.name} decides to {decision_name}")
                return selected_decision
            else:
                print(f"Invalid input. Please enter one of: {', '.join(valid_chars)}")
            
            
