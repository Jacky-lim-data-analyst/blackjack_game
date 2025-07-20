# contains function / class to process the data collected by the `simulation_runner`.
# This is to calculate statistics like `win/loss` percentages for each player,
# the dealer's bust rate, and generate reports.

import numpy as np
from collections import defaultdict
from typing import List, Dict, Any, Optional
import logging

# set up  logging for debugging
logging.basicConfig(level=logging.WARNING, format='%(asctime)s - %(name)s - %(levelname)s - %(messsage)s')
logger = logging.getLogger(__name__)

class DataValidationError(Exception):
    """Custom exception for data validation errors"""
    pass

class ResultsAnalyzer:
    """
    Analyzes the collected game history data to provide insights and statistics.
    """

    def __init__(self, game_history: List[Dict[str, Any]], players: List[Any], dealer: Any):
        """
        Initializes the ResultsAnalyzer with the game history.

        Args:
            game_history (list): A list of dictionaries, where each dictionary
                                 represents a round's data.
            players (list): A list of player objects.
            dealer (object): The dealer object.
        
        Raises:
            DataValidationError: If Input data is invalid
        """
        #--- Validate input data types at initialization ---
        if not isinstance(game_history, list):
            raise DataValidationError("Game history must be a list")
        if not isinstance(players, list):
            raise DataValidationError("Players must be a list of player objects")

        self.history = game_history
        self.players = {p.name: p for p in players}
        self.dealer = dealer

        try:
            self.stats = self._calculate_stats()
        except Exception as e:
            logger.error(f"Failed to calculate stats: {e}", exc_info=True)
            self.stats = self._get_empty_stats_structure()
            # raise DataValidationError(f"Stats calculation failed: {e}")
        
    def _get_empty_stats_structure(self) -> Dict[str, Any]:
        """
        Returns a default, empty structure for the stats.
        This is fallback when calculation failed
        """
        return {
            'game_summary': {
                'total_rounds': 0,
                'total_hands_played': 0,
                'total_wagered': 0,
                'errors': 1,   # Flag that an error occurred
            },
            'player_stats': defaultdict(dict),
            'dealer_stats': {}
        }

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

        for i, round_data in enumerate(self.history):
            if not isinstance(round_data, dict):
                logger.warning(f"Skipping round {i + 1}: round data is not a dictionary")
                continue

            # aggregate dealer stats
            dealer_hand = round_data.get('dealer_hand', {})
            if isinstance(dealer_hand, dict):
                dealer_stats['hands_played'] += 1
                if dealer_hand.get('is_busted', False):
                    dealer_stats['busts'] += 1
                if dealer_hand.get('is_blackjack', False):
                    dealer_stats['blackjacks'] += 1
            else:
                logger.warning(f"Skipping dealer stats for round {i + 1}: 'dealer_hand' invalid")

            # aggregate player stats
            players_in_round = round_data.get('players', [])
            if not isinstance(players_in_round, list):
                logger.warning(f"Skipping player stats for round {i + 1}: 'player' data is not a list")
                continue

            for player_round_data in players_in_round:
                if not isinstance(player_round_data, dict):
                    logger.warning(f"Skipping a player entry in round {i + 1}: player data is not a dictionary")
                    continue

                player_name = player_round_data.get('name')
                if not player_name:
                    logger.warning(f"Skipping a player entry in round {i+1}: missing 'name'.")
                    continue
                
                stats = player_stats[player_name]
                hands_in_round = player_round_data.get('hands', [])

                for hand in player_round_data['hands']:
                    if not isinstance(hand, dict):
                        logger.warning(f"Skipping a hand for player {player_name} in round {i+1}: hand data is not a dictionary.")
                        continue

                    # get the bet, payout and outcome of each hand
                    bet = hand.get('bet', 0)
                    payout = hand.get('payout', 0)
                    outcome = str(hand.get('outcome', 'unknown')).lower()

                    stats['hands_played'] += 1
                    stats['total_wagered'] += bet
                    stats['total_payout'] += payout
                    stats['payout_history'].append(payout)

                    total_wagered_game += bet
                    dealer_stats['total_profit'] -= payout

                    if outcome == 'blackjack':
                        stats['blackjacks'] += 1
                        stats['wins'] += 1
                    elif outcome == 'win':
                        stats['wins'] += 1
                    elif outcome in ('loss', 'bust', 'surrender'):
                        stats['losses'] += 1
                        if outcome == 'bust':
                            stats['busts'] += 1
                        elif outcome == 'surrender':
                            stats['surrenders'] += 1
                    elif outcome == 'push':
                        stats['pushes'] += 1

        # finalize calculations (percentages, RTP, variance)
        for name, stats in player_stats.items():
            hp = stats['hands_played']
            if hp > 0:
                stats['win_rate'] = stats['wins'] / hp
                stats['loss_rate'] = stats['losses'] / hp
                stats['push_rate'] = stats['pushes'] / hp
                stats['blackjack_rate'] = stats['blackjacks'] / hp
                stats['bust_rate'] = stats['busts'] / hp
                stats['rtp'] = (stats['total_payout'] + stats['total_wagered']) / stats['total_wagered'] if stats['total_wagered'] > 0 else 0
                
                if len(stats['payout_history']) > 1:
                    stats['payout_variance'] = np.var(stats['payout_history'])
                else:
                    stats['payout_variance'] = 0

        if dealer_stats['hands_played'] > 0:
            dealer_stats['bust_rate'] = dealer_stats['busts'] / dealer_stats['hands_played']
            dealer_stats['blackjack_rate'] = dealer_stats['blackjacks'] / dealer_stats['hands_played']

        return {
            'game_summary': {
                'total_rounds': len(self.history),
                'total_hands_played': sum(p['hands_played'] for p in player_stats.values()),
                'total_wagered': total_wagered_game,
            },
            'player_stats': dict(player_stats),   # convert back to regular dict
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
        summary = self.stats.get('game_summary', {})
        if not summary or summary.get('errors'):
            print("\nCould not generate a full report due to errors in data processing.")
            print("Please check the logs for more details.")
            print("="*50)
            return

        print("\n--- 1. Overall game information ---")
        print(f"Duration of play: {duration:.2f} seconds")
        print(f"Total rounds playered: {summary.get('total_rounds', 'N/A')}")
        print(f"Total hands played: {summary.get('total_hands_played', 'N/A')}")
        print(f"Total Amount Wagered: ${summary.get('total_wagered', 0):.2f}")

        # 2. Dealer Statistics
        d_stats = self.stats.get('dealer_stats', {})
        print("\n--- 2. Dealer Statistics ---")
        if d_stats:
            print(f"Total Profit / Loss: ${d_stats.get('total_profit', 0):.2f}")
            if d_stats.get('hands_played', 0) > 0:
                print(f"Blackjack Frequency: {d_stats.get('blackjacks', 0)} ({d_stats.get('blackjack_rate', 0):.2%})")
                print(f"Bust Frequency: {d_stats.get('busts', 0)} ({d_stats.get('bust_rate', 0):.2%})")
        else:
            print("No dealer statistics available")
        
        # 3. Player Statistics
        print("\n--- 3. Player Statistics & Performance ---")

        player_stats = self.stats.get('player_stats', {})
        if not player_stats:
            print("No player stats available")

        for name, p_stats in player_stats.items():
            player = self.players.get(name)
            print("\n" + "-"*40)
            if player:
                print(f"Player: {name} (Seat {getattr(player, 'seat', 'N/A')})")
                print(f"Final Chips: ${getattr(player, 'chips', 0):.2f}")
            else:
                print(f"Player: {name} (Seat N/A)")
                print("Final chip data not available")
            
            print(f"Net Profit / Loss: ${p_stats.get('total_payout', 0):.2f}")
            print(f"Total Wagered: ${p_stats.get('total_wagered', 0):.2f}")
            
            if p_stats.get('hands_played', 0) > 0:
                print("\n  Hand Outcomes:")
                print(f"    - Wins:       {p_stats.get('wins', 0)} ({p_stats.get('win_rate', 0):.2f})")
                print(f"    - Losses:     {p_stats.get('losses', 0)} ({p_stats.get('loss_rate', 0):.2f})")
                print(f"    - Pushes:     {p_stats.get('pushes', 0)} ({p_stats.get('push_rate', 0):.2f})")
                
                print("\n  Key Frequencies:")
                print(f"    - Blackjacks: {p_stats.get('blackjacks', 0)} ({p_stats.get('blackjack_rate', 0):.2f})")
                print(f"    - Busts:      {p_stats.get('busts', 0)} ({p_stats.get('bust_rate', 0):.2f})")

                print("\n  Financial Metrics:")
                print(f"    - Return to Player (RTP): {p_stats.get('rtp', 0):.2%}")
                print(f"    - Payout Variance: {p_stats.get('payout_variance', 0):.2f}")
            else:
                print("  No hands played.")
            print("-"*40)
        
        print("\n" + "="*50)
        print(" " * 17 + "END OF REPORT")
        print("="*50)