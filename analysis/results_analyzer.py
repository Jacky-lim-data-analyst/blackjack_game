# contains function / class to process the data collected by the `simulation_runner`.
# This is to calculate statistics like `win/loss` percentages for each player,
# the dealer's bust rate, and generate reports.

import numpy as np
from collections import defaultdict

class ResultsAnalyzer:
    """
    Analyzes the collected game history data to provide insights and statistics.
    """

    def __init__(self, game_history: list, players: list, dealer: object):
        """
        Initializes the ResultsAnalyzer with the game history.

        Args:
            game_history (list): A list of dictionaries, where each dictionary
                                 represents a round's data.
            players (list): A list of player objects.
            dealer (object): The dealer object.
        """
        self.history = game_history
        self.players = {p.name: p for p in players}
        self.dealer = dealer
        self.stats = self._calculate_stats()

    def _calculate_stats(self):
        """
        Processes the entire game history to compute statistics for all participants
        """
        player_stats = defaultdict(lambda: {
            'hands_played': 0, 'total_wagered': 0, 'total_payout': 0,
            'wins': 0, 'losses': 0, 'pushes': 0, 'blackjacks': 0, 'busts': 0, 'surrenders': 0,
            'payout_history': []
        })

        dealer_stats = {
            'hands_played': 0, 'busts': 0, 'blackjacks': 0, 'total_profit': 0,
        }

        # total_hands_played = 0
        total_wagered_game = 0

        for round_data in self.history:
            # aggregate dealer stats
            dealer_stats['hands_played'] += 1
            if round_data['dealer_hand']['is_busted']:
                dealer_stats['busts'] += 1
            if round_data['dealer_hand']['is_blackjack']:
                dealer_stats['blackjacks'] += 1

            # aggregate player stats
            for player_round_data in round_data['players']:
                player_name = player_round_data['name']
                stats = player_stats[player_name]
                
                for hand in player_round_data['hands']:
                    stats['hands_played'] += 1
                    stats['total_wagered'] += hand['bet']
                    stats['total_payout'] += hand['payout']
                    stats['payout_history'].append(hand['payout'])

                    total_wagered_game += hand['bet']
                    dealer_stats['total_profit'] -= hand['payout']

                    outcome = hand['outcome'].lower()
                    if outcome == 'win':
                        stats['wins'] += 1
                    elif outcome == 'loss':
                        stats['losses'] += 1
                    elif outcome == 'push':
                        stats['pushes'] += 1
                    elif outcome == 'blackjack':
                        stats['blackjacks'] += 1
                        stats['wins'] += 1
                    elif outcome == 'bust':
                        stats['busts'] += 1
                        stats['losses'] += 1
                    elif outcome == 'surrender':
                        stats['surrenders'] += 1
                        stats['losses'] += 1

        # finalize calculations (percentages, RTP, variance)
        for name, stats in player_stats.items():
            hp = stats['hands_played']
            if hp > 0:
                stats['win_rate'] = stats['wins'] / hp
                stats['loss_rate'] = stats['losses'] / hp
                stats['push_rate'] = stats['pushes'] / hp
                stats['blackjack_rate'] = stats['blackjacks'] / hp
                stats['bust_rate'] = stats['busts'] / hp
                stats['rtp'] = (stats['total_payout'] / stats['total_wagered']) / stats['total_wagered'] if stats['total_wagered'] > 0 else 0
                stats['payout_variance'] = np.var(stats['payout_history']) if stats['payout_history'] else 0

        if dealer_stats['hands_played'] > 0:
            dealer_stats['bust_rate'] = dealer_stats['busts'] / dealer_stats['hands_played']
            dealer_stats['blackjack_rate'] = dealer_stats['blackjacks'] / dealer_stats['hands_played']

        return {
            'game_summary': {
                'total_rounds': len(self.history),
                'total_hands_played': sum(p['hands_played'] for p in player_stats.values()),
                'total_wagered': total_wagered_game,
            },
            'player_stats': player_stats,
            'dealer_stats': dealer_stats
        }

    def print_full_report(self, duration: float):
        """
        Prints a comprehensive, formatted report of all game statistics.

        Args:
            duration (float): The duration of the simulation in seconds.
        """
        print("\n" + "="*50)
        print(" " * 15 + "BLACKJACK GAME REPORT")
        print("="*50)

        # game info
        summary = self.stats['game_summary']
        print("\n--- 1. Overall game information ---")
        print(f"Duration of play: {duration:.2f} seconds")
        print(f"Total rounds playered: {summary['total_rounds']}")
        print(f"Total hands played: {summary['total_hands_played']}")
        print(f"Total Amount Wagered: ${summary['total_wagered']:.2f}")

        # 2. Dealer Statistics
        d_stats = self.stats['dealer_stats']
        print("\n--- 2. Dealer Statistics ---")
        print(f"Total Profit / Loss: ${d_stats['total_profit']:.2f}")
        if d_stats['hands_played'] > 0:
            print(f"Blackjack Frequency: {d_stats['blackjacks']} ({d_stats['blackjack_rate']:.2%})")
            print(f"Bust Frequency: {d_stats['busts']} ({d_stats['bust_rate']:.2%})")
        
        # 3. Player Statistics
        print("\n--- 3. Player Statistics & Performance ---")
        for name, p_stats in self.stats['player_stats'].items():
            player = self.players[name]
            print("\n" + "-"*40)
            print(f"Player: {name} (Seat {player.seat})")
            print(f"Final Chips: ${player.chips:.2f}")
            print(f"Net Profit / Loss: ${p_stats['total_payout']:.2f}")
            print(f"Total Wagered: ${p_stats['total_wagered']:.2f}")
            
            if p_stats['hands_played'] > 0:
                print("\n  Hand Outcomes:")
                print(f"    - Wins:       {p_stats['wins']} ({p_stats['win_rate']:.2%})")
                print(f"    - Losses:     {p_stats['losses']} ({p_stats['loss_rate']:.2%})")
                print(f"    - Pushes:     {p_stats['pushes']} ({p_stats['push_rate']:.2%})")
                
                print("\n  Key Frequencies:")
                print(f"    - Blackjacks: {p_stats['blackjacks']} ({p_stats['blackjack_rate']:.2%})")
                print(f"    - Busts:      {p_stats['busts']} ({p_stats['bust_rate']:.2%})")

                print("\n  Financial Metrics:")
                print(f"    - Return to Player (RTP): {p_stats['rtp']:.2%}")
                print(f"    - Payout Variance: {p_stats['payout_variance']:.2f}")
            else:
                print("  No hands played.")
            print("-"*40)
        
        print("\n" + "="*50)
        print(" " * 17 + "END OF REPORT")
        print("="*50)