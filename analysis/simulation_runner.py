# contains class or function responsible for running the simulation for a specified number
# of rounds. Instantiate game and player objects, play the games and collect data from each
# round. (e.g., who won, what were the final hands)

import json
import time
from typing import List, Dict

from game_logic.table import Table
from players.base_player import Player
from players.basic_strategy_player import BasicStrategyPlayer
from players.dealer import Dealer
from players.human_player import HumanPlayer
from players.naive_strategy_player import NaiveStrategyPlayer
from players.ai_player import LLMPlayer
from .results_analyzer import ResultsAnalyzer
from config import BLACKJACK_VALUE, PAYOUT_RATIO_BLACKJACK_TO_PLAYER

class GameRunner:
    """
    Orchestrates the Blackjack game, manages players, run rounds,
    and collects data for analysis
    """

    def __init__(self, player_configs: List[dict]):
        """
        Initializes the GameRunner.

        Args:
            player_configs (List[dict]): A list of dictionaries, each defining a player.
                                        Example: [{'type': 'human', 'name': 'You'},
                                                  {'type': 'llm', 'name': 'Deepseek', 'model': 'deepseek-r1']
        """
        self.players = self._create_players(player_configs)
        self.dealer = Dealer()
        self.table = Table(self.players, self.dealer)
        self.round_history = []
        self.round_number = 0
        self.start_time = 0

    def _create_players(self, configs: List[dict]) -> List[Player]:
        """Creates player instances based on configuration"""
        players = []
        for i, config in enumerate(configs):
            player_type = config.get('type', '').lower()
            name = config.get('name', f'Player {len(players) + 1}')
            chips = config.get('chips', 1000)

            # add seat position to the player object for easy reference 
            player_instance = None
            if player_type == 'human':
                player_instance = HumanPlayer(name, chips)
            elif player_type == 'llm':
                model = config.get('model', 'deepseek-r1:8b')
                player_instance = LLMPlayer(name, chips, model)
            elif player_type == 'basic':
                player_instance = BasicStrategyPlayer(name, chips)
            elif player_type == 'naive':
                player_instance = NaiveStrategyPlayer(name, chips)
            else:
                raise ValueError(f"Unknown player type: {player_type}")
            
            if player_instance:
                player_instance.seat = i + 1
                players.append(player_instance)

        return players

    def _collect_round_data(self, initial_chip_counts: dict, initial_hands: Dict):
        """
        Collects and stores detailed data from the completed round. Includes 
        detailed info like initial hand, final hand and etc.
        """
        round_data = {
            'round': self.round_number,
            'dealer_hand': {
                'initial_hand': str(initial_hands['dealer']),
                'final_hand': str(self.table.dealer.hand),
                'final_value': self.table.dealer.get_hand_value(),
                'is_blackjack': self.table.dealer.has_blackjack(),
                'is_busted': self.table.dealer.get_hand_value() > BLACKJACK_VALUE
            },
            'players': []
        }
        
        for player in self.players:
            player_data = {
                'name': player.name,
                'seat': player.seat,
                'chips_before': initial_chip_counts[player.name],
                'chips_after': player.chips,
                'hands': []
            }

            outcomes = self.table.outcomes.get(player, [])
            for i, hand in enumerate(player.hand):
                bet = player.bets[i]
                outcome = outcomes[i] if i < len(outcomes) else 'Unknown'

                # calculate payout based on outcome 
                payout = 0
                if outcome == 'Blackjack':
                    payout = bet * PAYOUT_RATIO_BLACKJACK_TO_PLAYER
                elif outcome == 'Win':
                    payout = bet
                elif outcome == 'Loss' or outcome == 'Bust':
                    payout = -bet
                elif outcome == 'Surrender':
                    payout = -bet / 2
                # push results in a payout of 0

                hand_data = {
                    'initial_hand': str(initial_hands[player.name][i]),
                    'final_hand': str(hand),
                    'final_value': hand.calculate_total_value(),
                    'bet': bet,
                    'outcome': outcome,
                    'payout': payout,
                    'is_blackjack': hand.get_num_cards() == 2 and hand.calculate_total_value() == BLACKJACK_VALUE,
                    'is_busted': hand.calculate_total_value() > BLACKJACK_VALUE
                }

                player_data['hands'].append(hand_data)

            round_data['players'].append(player_data)

        self.round_history.append(round_data)
        print("\n[GameRunner] Round data collected")

    def play_round(self):
        """
        Plays a single round of Blackjack and collect the results
        """
        self.round_number += 1
        print(f"\n--- Round {self.round_number} ---")

        # store chip counts before the round starts
        initial_chip_counts = {player.name: player.chips for player in self.players}

        # 1. setup the rounds (resets hands, gets bets, shuffles deck)
        self.table._setup_round()

        # 2. deal initial cards
        self.table._deal_initial_cards()
        self.table._show_initial_cards()

        # context for decision making 
        initial_game_context = {
            "num_players": len(self.players),
            "cards_in_play": [card for player in self.table.players for card in player.hand[0].cards] + \
                [self.table.dealer.get_upcard()]
        }

        # capture initial hands for results analysis: make sure to not overwrite the "initial" hand data
        initial_hands = {
            'dealer': str(self.table.dealer.hand),
            **{p.name: [str(h) for h in p.hand] for p in self.players}
        }
        
        # 4. checks for and handle blackjacks. End the round if dealer or all players have blackjack
        round_over = self.table._handle_blackjacks()

        if not round_over:
            # player turns
            for player in self.players:
                # a player who has a blackjack or lost to a dealer blackjack already has an outcome and does not play
                if not self.table.outcomes.get(player, []):
                    self.table._player_turn(player, initial_context=initial_game_context)

            # dealer's turn, if any players are still in the game
            if any(i >= len(self.table.outcomes.get(player, [])) for player in self.players for i, h in enumerate(player.hand)):
                self.table._dealer_turn()

        # determine the final outcomes and conclude the round
        self.table._determine_outcomes()
        self.table._show_final_hands()
        self.table._conclude_round()

        # Collect data after the round is fully concluded
        self._collect_round_data(initial_chip_counts, initial_hands=initial_hands)

    def _run_game_loop(self, num_rounds: int = -1):
        """Internal game loop for both simulation and interactive game"""
        self.start_time = time.time()

        rounds_to_play = num_rounds if num_rounds > 0 else float('inf')
        current_round = 0

        while current_round < rounds_to_play:
            if all(p.chips <= 0 for p in self.players):
                print("All players are out of chips. Ending game")
                break

            self.play_round()

            if num_rounds == -1:
                play_again = input("\nPlay another round? (y/n): ").lower().strip()
                if play_again != 'y':
                    break
            
            current_round += 1
        
    def _finalize_and_analyze(self):
        """Calculates final stats and prints the analysis report"""
        end_time = time.time()
        duration = end_time - self.start_time

        print("\n--- Finalize and analyzing game results ---")
        analyzer = ResultsAnalyzer(self.round_history, self.players, self.dealer)
        analyzer.print_full_report(duration)

        self.save_history_to_json()

    def run_simulation(self, num_rounds: int):
        """
        Runs the simulation for a specified number of rounds
        """
        print("--- Starting Blackjack Simulation ---")
        self._run_game_loop(num_rounds)
        print("--- Simulation Complete ---")
        self._finalize_and_analyze()

    def start_interactive_game(self):
        """Starts a game that waits for user input to play new rounds"""
        print("\n--- Starting Interactive Blackjack Game ---")
        self._run_game_loop()
        print("--- Thanks for playing! ---")
        self._finalize_and_analyze()

    def save_history_to_json(self, filename: str = "game_history.json"):
        """Saves the round history to a JSON file"""
        try:
            with open(filename, 'w') as file:
                json.dump(self.round_history, file, indent=4)
            print(f"Round history saved to {filename}")
        except IOError as e:
            print(f"Error saving round history: {e}")

            