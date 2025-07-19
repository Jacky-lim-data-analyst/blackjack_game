# import random
from game_logic.deck import Deck
from game_logic.hand import Hand
# from game_logic.card import Card

# ---- 1. Test the formation of deck (Checked) ---
my_deck = Deck()

# for card in my_deck.cards:
#     print(card)

my_deck.shuffle()
# print(my_deck.deal_card())
# print(my_deck.deal_card())

# --- 2. Test the hand class ---
my_hand = Hand()
my_hand.add_card(my_deck.deal_card())
my_hand.add_card(my_deck.deal_card())
print(my_hand)

print(f"The number of cards: {my_hand.get_num_cards()}")
print(f"Does the 2 cards have the same rank? {my_hand.is_two_cards_similar()}")

print(f"The total value of the hand: {my_hand.calculate_total_value()}")
print(f"Is the hand soft? {my_hand.is_soft()}")