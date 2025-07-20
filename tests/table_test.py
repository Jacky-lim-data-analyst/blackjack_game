# from game_logic.table import Table
# from players.basic_strategy_player import BasicStrategyPlayer
# from players.naive_strategy_player import NaiveStrategyPlayer
# from players.dealer import Dealer
from analysis.simulation_runner import GameRunner

# player_list = [BasicStrategyPlayer(name="basic"), NaiveStrategyPlayer(name="naive")]

# table = Table(players=player_list, dealer=Dealer())

# table.play_round()

game = GameRunner(player_configs=[
    {'type': 'basic', 'name': 'basic'},
    {'type': 'naive', 'name': 'naive'}
])

game.run_simulation(num_rounds=5)