# main entry point

from analysis.simulation_runner import GameRunner

if __name__ == '__main__':
    # configuration 
    # define players who will be at the table
    player_configs = [
        {'type': 'basic', 'name': 'BasicBot'},
        {'type': 'naive', 'name': 'NaiveBot'},
        {'type': 'human', 'name': 'Noob'},
        {'type': 'llm', 'name': 'LLMBJMaster', 'model': 'deepseek-r1:1.5b'}
    ]

    # --- run the game ---
    game_runner = GameRunner(player_configs=player_configs)

    # 1. simulation mode
    # game_runner.run_simulation(num_rounds=100)

    # 2. interactive mode
    game_runner.start_interactive_game()
