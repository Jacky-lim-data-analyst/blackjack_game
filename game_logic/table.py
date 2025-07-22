# Table class handles the deck, players' hands, player and dealer turns and determine the outcomes 
# of a game round.

import random
from config import (
    Decision, 
    BLACKJACK_VALUE, PAYOUT_RATIO_BLACKJACK_TO_PLAYER, NUM_CARDS_PER_DECK, NUM_DECKS, POSSIBLE_BETS
)
from .deck import Deck
from players.base_player import Player
from players.dealer import Dealer
from .card import CardVisualizer

class Table:
    def __init__(self, players: list[Player], dealer: Dealer):
        """
        Initializes the table with players and a dealer

        Args:
            players (list[Player]): List of players in the game.
            dealer (Dealer): The dealer in the game.
        """
        self.players = players
        self.dealer = dealer
        self.deck = Deck()
        # dictionary to track the outcome for each player
        self.outcomes = {}
        self.visualizer = CardVisualizer()
        # self.player_initial_bets = {player.name: 0 for player in self.players}

    def play_round(self):
        """Manages the logic for a single round of Blackjack."""
        # 1. Setup the round (bets, reset hands, shuffle)
        self._setup_round()

        # 2. Deal initial cards
        self._deal_initial_cards()
        self._show_initial_cards()

        # 2a: collects relevant game info
        cards_in_play = [card for player in self.players for card in player.hand[0].cards] + \
                        [self.dealer.get_upcard()]

        # create an initial game context
        initial_game_context = {
            "num_players": len(self.players),
            "cards_in_play": cards_in_play,
        }

        # Insurance bet if dealer upcard is an Ace
        if self.dealer.get_upcard().rank == 'A':
            initial_game_context["prob_10_as_dealer_hc"] = self._calculate_prob_hc(cards_in_play)
            self._offer_insurance(initial_game_context)

        # 3. Check for blackjacks
        if self._handle_blackjacks():
            self._conclude_round()
            return  # Round is over if dealer or all players have blackjack

        # 4. Player turns
        for player in self.players:
            # if not player.has_blackjack():  # player with blackjack don't take a turn
            self._player_turn(player, initial_game_context)

        # 5. Dealer's turn, if any players are still in the game
        if any(hand for player in self.players for i, hand in enumerate(player.hand) if i >= len(self.outcomes.get(player, []))):
            self._dealer_turn()

        # 6. Determine outcomes for all players
        self._determine_outcomes()
        self._show_final_hands()
        self._conclude_round()

    def _setup_round(self):
        """Resets hands, bets, outcomes, and shuffles the deck (new round)"""
        print("\n--- New Round ---")
        # shuffle the deck
        self.deck = Deck()
        self.deck.shuffle()
        # reset the dealer / players' status
        self.dealer.reset_for_new_round()
        for player in self.players:
            player.reset_for_new_round()

        # self.bets = {}
        self.outcomes = {}

        # --- Game flow ---
        # players place their bets
        for player in self.players:
            player_bet = player.choose_bets()
            if player_bet is None:
                player_bet = 20
            player.place_bet(player_bet)
            print(f"{player.name} placed a bet of {player.bets[0]} chips")
            # self.player_initial_bets[player.name] = player_bet

    def _deal_initial_cards(self):
        """Deals two cards to each player and the dealer."""
        for _ in range(2):
            for player in self.players:
                player.add_card_to_hand(self.deck.deal_card(), 0)
            self.dealer.add_card_to_hand(self.deck.deal_card())

    def _show_initial_cards(self):
        """Shows the initial hands of all players and the dealer."""
        for player in self.players:
            print(f"{player.name}'s hand: {player.hand[0]} (Value: {player.get_hand_value(0)})")
            self.visualizer.display_cards(player.hand[0].cards, title=f"{player.name} hand")
            print()
        print(f"Dealer's upcard: {self.dealer.get_upcard()}")
        self.visualizer.display_card(self.dealer.get_upcard())
        print()

    def _calculate_prob_hc(self, cards):
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

    def _offer_insurance(self, context):
        """Offers players the option to place an insurance bet."""
        print("\nDealer has an Ace showing. Offering insurance...")
        for player in self.players:
            if player.make_decision_insurance(context):
                player.place_insurance_bet()
                
    def _handle_blackjacks(self):
        """
        Checks for and handles player and dealer blackjacks
        Returns True if the round should end, False otherwise
        """
        dealer_has_blackjack = self.dealer.has_blackjack()

        # --- Insurance bet ---
        # settle insurance bets if the dealer's upcard was an Ace
        if self.dealer.get_upcard().rank == 'A':
            print(f"\nDealer checks for blackjack... Hand: {self.dealer.hand}")
            if dealer_has_blackjack:
                print("Dealer has Blackjack! Insurance bets wins")
                for player in self.players:
                    if player.insurance_bet > 0:
                        # Insurance pays 2:1. The player gets their bet back plus double the bet in winnings
                        payout = player.insurance_bet * 2
                        player.update_balance(payout)
                        print(f"{player.name} wins {player.insurance_bet * 2} on insurance win")
                    else:
                        print("Dealer does not have blackjack. Insurance bets are lost")            

        if dealer_has_blackjack:
            print(f"Dealer has Blackjack! Hand: {self.dealer.hand}")
        
        for player in self.players:
            self.outcomes[player] = []
            if player.has_blackjack():
                if dealer_has_blackjack:
                    print(f"{player.name} has Blackjack! Hand: {player}. It is a push")
                    self.outcomes[player].append("Push")
            
                else:
                    print(f"{player.name} has Blackjack! Hand: {player.hand}. Player wins")
                    self.outcomes[player].append("Blackjack")
            else:
                if dealer_has_blackjack:
                    self.outcomes[player].append("Loss")
        
        # if the dealer has blackjack, the round ends for all players 
        return dealer_has_blackjack

    def _player_turn(self, player: Player, initial_context: dict):
        """
        Handles the decision-making loop for a single player, incorporating split,
        double_down and surrender actions."""

        context = initial_context.copy()

        hand_index = 0
        
        # use a while loop because the number of hands can change to 2 if the player splits
        while hand_index < len(player.hand):
            hand = player.hand[hand_index]
            bet = player.bets[hand_index]

            # player can only split once
            can_split_now = len(player.hand) == 1 and player.can_split(hand)

            print(f"\n{player.name}'s turn. Hand {hand_index+1}: {hand}, Value: {hand.calculate_total_value()}")

            # Loop for decisions on the current hand
            while True:
                # player can only perform special actions (surrender, double down or split) on their first two cards
                is_first_action = hand.get_num_cards() == 2

                # get the player's decision
                action = player.make_decision(hand, self.dealer.get_upcard(), context=context)
                print(f"{player.name} decides to {action} for hand {hand_index + 1}")

                # --- handle special first-action decisions ---
                if is_first_action:
                    if action == Decision.SURRENDER:
                        # player gets half of their bet back. The hand is over
                        player.chips += bet / 2
                        self.outcomes.setdefault(player, []).append("Surrender")
                        print(f"{player.name} surrenders hand {hand_index + 1}")
                        break  # player turn for this hand ends

                    if action == Decision.SPLIT and can_split_now:
                        # checks if the player is splitting Aces
                        is_splitting_aces = hand.cards[0].rank == 'A'

                        print(f"{player.name} splits")
                        player.split_hand(hand_index)
                        # deal a new card to both original and new hand
                        player.add_card_to_hand(self.deck.deal_card(), hand_index)
                        player.add_card_to_hand(self.deck.deal_card(), hand_index + 1)
                        print(f"New hand 1: {player.hand[hand_index]}")
                        print(f"New hand 2: {player.hand[hand_index + 1]}")
                        assert len(player.hand[hand_index].cards) == 2
                        assert len(player.hand[hand_index + 1].cards) == 2
                        player.hand[hand_index].split_hand = True
                        player.hand[hand_index + 1].split_hand = True
                        # visualize
                        self.visualizer.display_cards(player.hand[hand_index].cards, title=f"{player.name} hand {hand_index + 1}")
                        self.visualizer.display_cards(player.hand[hand_index + 1].cards, title=f"{player.name} hand {hand_index + 2}")
                        # update context
                        context["num_hands"] = len(player.hand)
                        context["cards_in_play"] = [card for p in self.players for hand in p.hand for card in hand.cards] + \
                            [self.dealer.get_upcard()]
                        # if player split aces, they only get one additional card on each hand and cannot hit again.
                        if is_splitting_aces:
                            print(f"{player.name} split Aces. Each hand gets one card and must stand.")
                            return
                        else:
                            continue   # restart the decision loop for this hand

                    if action == Decision.DOUBLE_DOWN:
                        # double the bet
                        if player.chips >= bet:
                            print(f"{player.name} doubles down")
                            # double the bet for this round
                            player.chips -= bet
                            player.bets[hand_index] *= 2
                            player.add_card_to_hand(self.deck.deal_card(), hand_index)
                            print(f"Hand {hand_index + 1} after double-down: {hand}, Value: {hand.calculate_total_value()}")
                            # TODO: visualize
                            self.visualizer.display_cards(player.hand[0].cards, title=f"{player.name} hand (double-down)")
                            # update context
                            context["cards_in_play"].append(hand.cards[-1])
                            if hand.calculate_total_value() > BLACKJACK_VALUE:
                                print(f"{player.name} busts on hand {hand_index + 1}!")
                                self.outcomes.setdefault(player, []).append("Bust")
                            break  # player turn for this hand ends
                        else:
                            print("Not enough chips to double down. Treating it as hit")
                            action = Decision.HIT
                # --- Handles regular hit, stand loop ---
                if action == Decision.STAND:
                    print(f"{player.name} stands on hand {hand_index + 1}")
                    break
                if action == Decision.HIT:
                    player.add_card_to_hand(self.deck.deal_card(), hand_index)
                    print(f"{player.name} hits on hand {hand_index + 1}. Hand: {hand}, Value: {hand.calculate_total_value()}")
                    # visualize
                    self.visualizer.display_cards(player.hand[0].cards, title=f"{player.name} hand")
                    # update context
                    context["cards_in_play"].append(hand.cards[-1])
                    if hand.calculate_total_value() > BLACKJACK_VALUE:
                        print(f"{player.name} busts on hand {hand_index + 1}!")
                        self.outcomes.setdefault(player, []).append("Bust")
                        break  # player turn for this hand ends
                else:
                    # if an invalid action is chosen after first turn
                    if not is_first_action:
                        print(f"Invalid action ({action}) after first turn. Please choose either hit or stand")
                        # the loop will checks for another action
                
            hand_index += 1


    def _dealer_turn(self):
        """Handles the dealer's fixed-logic turn."""
        # Reveal dealer's hole card
        print(f"\nDealer's turn. Hand: {self.dealer.hand}, Value: {self.dealer.get_hand_value()}")
        # TODO: visualize
        self.visualizer.display_cards(self.dealer.hand[0].cards, title=f"dealer hand")

        while self.dealer.make_decision(self.dealer.hand[0], self.dealer.hand[0].cards[0]) == Decision.HIT:
            self.dealer.add_card_to_hand(self.deck.deal_card())
            print(f"Dealer hits. Hand: {self.dealer.hand}, Value: {self.dealer.get_hand_value()}")
            # TODO: visualize
            self.visualizer.display_cards(self.dealer.hand[0].cards, title=f"dealer hand")

        if self.dealer.get_hand_value() > BLACKJACK_VALUE:
            print("Dealer busts!")
        else:
            print(f"Dealer stands with {self.dealer.hand}, Value: {self.dealer.get_hand_value()}")
        

    def _determine_outcomes(self):
        """Compares each remaining player's hand to the dealer's to determine results."""
        dealer_value = self.dealer.get_hand_value()
        dealer_busted = dealer_value > BLACKJACK_VALUE

        print("\n--- Results ---")
        for player in self.players:
            # ensure outcomes list is initialized
            if player not in self.outcomes:
                self.outcomes[player] = []

            for i, hand in enumerate(player.hand):
                # skip hand that already has outcome
                if i < len(self.outcomes[player]):
                    continue

                player_value = hand.calculate_total_value()

                if player_value > BLACKJACK_VALUE:
                    self.outcomes[player].append("Bust")
                elif dealer_busted or player_value > dealer_value:
                    self.outcomes[player].append("Win")
                elif not dealer_busted and player_value < dealer_value:
                    self.outcomes[player].append("Loss")
                else: 
                    self.outcomes[player].append("Push")

    def _show_final_hands(self):
        """Display all players' and dealers' first hands at the end of the game"""
        print("\n" + "=" * 60)
        print("FINAL HANDS SUMMARY")
        print("=" * 60)

        # show each player's final hand(s)
        for player in self.players:
            if len(player.hand) == 1:
                # single hand
                hand_value = player.hand[0].calculate_total_value()
                status = "BUST" if hand_value > BLACKJACK_VALUE else "BLACKJACK" if self.dealer.has_blackjack() else f"Value: {hand_value}"
                print(f"\n{player.name}'s final hand - {status}")
                self.visualizer.display_cards(player.hand[0].cards, title=f"{player.name}")
            else:
                # multiple hands
                print(f"\n{player.name}'s final hands:")
                for i, hand in enumerate(player.hand):
                    hand_value = hand.calculate_total_value()
                    status = "BUST" if hand_value > BLACKJACK_VALUE else f"Value: {hand_value}"
                    print(f"Hand {i + 1} - status")
                    self.visualizer.display_cards(hand.cards, title=f"{player.name} Hand {i + 1}")

        # Show dealer's final hand
        dealer_value = self.dealer.get_hand_value()
        dealer_status = "BUST" if dealer_value > BLACKJACK_VALUE else "BLACKJACK" if self.dealer.has_blackjack() else f"Value: {dealer_value}"
        print(f"\nDealer's Final Hand - {dealer_status}")
        self.visualizer.display_cards(self.dealer.hand[0].cards, title="Dealer")
        
        print("=" * 60)

    def _conclude_round(self):
        """Prints the final results and settles the bets with the players"""
        print("\n --- Final Results ---")
        for player, outcomes in self.outcomes.items():
            print(f"\n{player.name}'s results:")
            for i, outcome in enumerate(outcomes):
                bet = player.bets[i]
                payout = 0   # payout here refers to the gross amount: win amount + bet amount
                result_str = ""
                if outcome == "Blackjack":
                    if player.hand[0].split_hand:
                        payout = bet * 2
                    else:
                        payout = bet * PAYOUT_RATIO_BLACKJACK_TO_PLAYER + bet
                    result_str = f"Hand {i+1}: Wins {payout - bet} with Blackjack"
                elif outcome == "Win":
                    payout = bet * 2
                    result_str = f"Hand {i+1}: Wins {payout - bet}"
                elif outcome == "Loss" or outcome == "Bust":
                    payout = 0
                    result_str = f"Hand {i+1}: Loses {bet}"
                elif outcome == "Push":
                    payout = bet
                    result_str = f"Hand {i+1}: Pushes {bet}"

                player.update_balance(payout)
                print(result_str)

            print(f"{player.name} has {player.chips} chips remaining")