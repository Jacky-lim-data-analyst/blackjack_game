# define card class with attributes like suit and rank and
# method to get its value (e.g., King = 10, Ace = 1 or 11)

from config import cards_rank_value_dict, card_suits

class Card:
    def __init__(self, suit, rank):
        """
        Args:
            suit (str)
            rank (str)
        """
        self.suit = suit
        self.rank = rank
    
    def get_value(self):
        # add warning if no key is found
        if self.rank not in cards_rank_value_dict:
            print(f"Warning: No value found for rank {self.rank}")
            return 0
        
        return cards_rank_value_dict[self.rank]
    
    def __str__(self):
        return f"{self.rank} of {self.suit}"
    
    def __repr__(self):
        return self.__str__()
    
class CardVisualizer:
    def __init__(self):
        # Unicode symbols for suits
        self.suit_symbols = {
            card_suits[0]: '♥',
            card_suits[1]: '♦',
            card_suits[2]: '♣',
            card_suits[3]: '♠'
        }

        # colors for suits (ANSI color codes)
        self.suit_colors = {
            card_suits[0]: '\033[31m',   # red
            card_suits[1]: '\033[31m',   # red
            card_suits[2]: '\033[30m',   # black
            card_suits[3]: '\033[30m'    # black
        }

        self.reset_color = '\033[0m'

        self.rank_display = {
            'A': 'A', '2': '2', '3': '3', '4': '4', 
            '5': '5', '6': '6', '7': '7', '8': '8', 
            '9': '9', '10': '10', 'J': 'J', 'Q': 'Q', 'K': 'K'
        }

    def create_card_art(self, card):
        """Create ASCII art for a single card"""
        suit_symbol = self.suit_symbols[card.suit]
        color = self.suit_colors[card.suit]
        rank = self.rank_display[card.rank]

        # adjust spacing for 10
        if rank == '10':
            rank_top = '10'
            rank_bottom = '01'
        else:
            rank_top = rank + ' '
            rank_bottom = ' ' + rank

        card_art = f"""{color}┌───────┐
        |{rank_top}        |
        |         |
        |    {suit_symbol}    |
        |         |
        |        {rank_bottom}|
        └───────┘{self.reset_color}
        """

        return card_art
    
    def create_fancy_card_art(self, card):
        """Create fancy ASCII art for a single card with more details"""
        suit_symbol = self.suit_symbols[card.suit]
        color = self.suit_colors[card.suit]
        rank = self.rank_display[card.rank]

        # special patterns for face cards
        if card.rank in ['J', 'Q', 'K']:
            if card.rank == 'J':
                pattern = f"│   ┌─┐   │\n│   │{suit_symbol}│   │\n│   └─┘   │"
            elif card.rank == 'Q':
                pattern = f"│  ┌─♛─┐  │\n│  │ {suit_symbol} │  │\n│  └───┘  │"
            else:
                pattern = f"│  ┌─♔─┐  │\n│  │ {suit_symbol} │  │\n│  └───┘  │"

        elif card.rank == 'A':
            pattern = f"│         │\n│    {suit_symbol}    │\n│         │"

        else:
            # Number cards - show multiple suit symbols
            num = int(card.rank) if card.rank.isdigit() else 10
            if num <= 3:
                symbols = suit_symbol * num
                pattern = f"│         │\n│   {symbols}   │\n│         │"
            elif num <= 6:
                top_row = suit_symbol * (num // 2)
                bottom_row = suit_symbol * (num - num // 2)
                pattern = f"│  {top_row}  │\n│         │\n│  {bottom_row}  │"
            else:
                pattern = f"│  {suit_symbol} {suit_symbol} {suit_symbol}  │\n│   {suit_symbol} {suit_symbol}   │\n│  {suit_symbol} {suit_symbol} {suit_symbol}  │"

        # Adjust spacing for 10
        if rank == '10':
            rank_top = '10'
            rank_bottom = '01'
        else:
            rank_top = rank + ' '
            rank_bottom = ' ' + rank
        
        card_art = f"""{color}┌─────────┐
│{rank_top}       │
{pattern}
│       {rank_bottom}│
└─────────┘{self.reset_color}"""
        
        return card_art
    
    def display_card(self, card, fancy=False):
        """Display a single card"""
        if fancy:
            print(self.create_fancy_card_art(card))
        else:
            print(self.create_card_art(card))

    def display_cards(self, cards, fancy=False):
        """Display a list of cards"""
        if not cards:
            print("No cards to display")
            return

        # create art for all cards
        card_arts = []
        for card in cards:
            if fancy:
                card_arts.append(self.create_fancy_card_art(card).split('\n'))
            else:
                card_arts.append(self.create_card_art(card).split('\n'))

        # print cards side by side
        for i in range(len(card_arts[0])):
            line = ""
            for j, card_art in enumerate(card_arts):
                line += card_art[i]
                if j < len(card_arts) - 1:
                    line += " "   # spaces between cards
            print(line)

    def display_hand(self, cards, title="Hand", fancy=False):
        """Display a hand of cards"""
        print(f"\n{title}:")
        print("=" * len(title))
        for card in cards:
            self.display_card(card, fancy)
        print()