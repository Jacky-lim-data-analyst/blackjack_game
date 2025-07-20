from game_logic.deck import Deck
from game_logic.hand import Hand
from players.dealer import Dealer
from players.naive_strategy_player import NaiveStrategyPlayer
from players.basic_strategy_player import BasicStrategyPlayer
from players.ai_player import LLMPlayer
from players.human_player import HumanPlayer
from config import Decision 

# Instantiate deck
my_deck = Deck()
my_deck.shuffle()

# --- Check for dealer (Ok)---
dealer = Dealer()

dealer.hand[0].add_card(my_deck.deal_card())
dealer.hand[0].add_card(my_deck.deal_card())

print(dealer.hand[0])
print(f"The dealer upcard: {dealer.get_upcard()}")
# print("-"*20)
# while True:
#     print(f"The dealer decides to {dealer.make_decision(hand=dealer.hand[0], dealer_upcard=dealer.get_upcard()).value}")
#     if dealer.make_decision(hand=dealer.hand[0], dealer_upcard=dealer.get_upcard()) == Decision.STAND:
#         break
#     dealer.add_card_to_hand(my_deck.deal_card())
#     print(dealer.hand[0])
    
# print(f"The final hand: {dealer.hand[0]}")

# --- check for naive strategy player (Ok)---
# naive_player = NaiveStrategyPlayer(name="haha")
# naive_player.place_bet(20)
# naive_player.hand[0].add_card(my_deck.deal_card())
# naive_player.hand[0].add_card(my_deck.deal_card())

# print(f"{naive_player.name} hand:")
# print(naive_player.hand[0])
# print("-"*20)
# print(f"Possible decisions: {naive_player.get_possible_decisions()}")
# decision = naive_player.make_decision()
# if decision:
#     print(f"{naive_player.name} decides to {decision.value}")
# else:
#     print("The decision is None")

# --- checks for basic strategy player (Ok)---
# basic_player = BasicStrategyPlayer(name="Optimus Prime")
# basic_player.place_bet(20)
# basic_player.hand[0].add_card(my_deck.deal_card())
# basic_player.hand[0].add_card(my_deck.deal_card())

# print(f"The basic player's hand: {basic_player.hand[0]}")
# print("-"*20)
# print(f"Possible decisions: {basic_player.get_possible_decisions()}")
# decision = basic_player.make_decision(hand=basic_player.hand[0], dealer_upcard=dealer.get_upcard())
# if decision:
#     print(f"{basic_player.name} decides to {decision.value}")
# else:
#     print("The decision is None")

# --- checks for the AI player (Ok)---
# ai_player = LLMPlayer(name="Deepseek", model="deepseek-r1:1.5b")
# ai_player.place_bet(20)

# ai_player.hand[0].add_card(my_deck.deal_card())
# ai_player.hand[0].add_card(my_deck.deal_card())

# print(f"The AI player's hand: {ai_player.hand[0]}")
# print("-"*20)
# print(f"Possible decisions: {ai_player.get_possible_decisions()}")
# decision = ai_player.make_decision(hand=ai_player.hand[0], dealer_upcard=dealer.get_upcard())
# if decision:
#     print(f"{ai_player.name} decides to {decision.value}")
# else:
#     print("The decision is None")

# --- checks for human player ---
human_player = HumanPlayer(name="YoloPlayer", chips=1000)
human_player.place_bet(20)

human_player.hand[0].add_card(my_deck.deal_card())
human_player.hand[0].add_card(my_deck.deal_card())

print(f"The human player's hand: {human_player.hand[0]}")
print("-"*20)
print(f"Possible decisions: {human_player.get_possible_decisions()}")

human_decision = human_player.make_decision(hand=human_player.hand[0], dealer_upcard=dealer.get_upcard())
