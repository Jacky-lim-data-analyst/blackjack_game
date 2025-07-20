# Black Simulator

A modular Python Blackjack simulator for running AI, human, and strategy-based players against a dealer. Supports simulation, interactive play, and statistical analysis.

## Features

- Multiple player types: Human, Naive, Basic Strategy, and LLM-powered AI
- Configurable game rules (number of decks, bet limits, payouts)
- Simulation and interactive game modes
- Detailed round history and statistical analysis (win rates, bust rates, RTP, variance)
- Extensible architecture for new strategies and player types

## Getting Started

### Requirements

- Python 3.10+
- [ollama](https://ollama.com/) (for LLMPlayer, optional)
- numpy (for analysis)

### Installation

1. Clone the repository:
    ```sh
    git clone https://github.com/yourusername/blackjack_simulator.git
    cd blackjack_simulator
    ```

2. (Optional) Create and activate a virtual environment:
    ```sh
    python3 -m venv .venv
    source .venv/bin/activate
    ```

3. Install dependencies:
    ```sh
    pip install -r requirements.txt
    ```

## Usage

### Run Interactive Game

```sh
python main.py
```

By default, the game starts in interactive mode. You can configure player types in `main.py`.

### Run Simulation
Uncomment the simulation line in `main.py`:
```python
game_runner.run_simulation(num_rounds=100)
```

This will run 100 rounds and print a statistical report.

## Player Types
- HumanPlayer: Prompts for user input for decisions and bets.
- NaiveStrategyPlayer: Makes random decisions. 
- BasicStrategyPlayer: Follows standard Blackjack basic strategy charts.
- LLMPlayer: Uses a local LLM (via Ollama) to make decisions (requires Ollama).

## Analysis and Reporting
After simulation or interactive play, the game generates a detailed report including:

- Win/loss rates
- Bust and blackjack frequencies
- Return to Player (RTP)
- Payout variance
- Dealer statistics

Results are saved to game_history.json for further analysis.

## Customization
1. Modify game rules in `config.py`.
2. Add new player strategies by subclassing Player.
3. Extend analysis/reporting in analysis/results_analyzer.py.
4. Extend the AI player capabilities by using state-of-the-art AI models with your API tokens by subclassing from the `Player` parent class.

## License
MIT License. See [LICENSE](./LICENSE) for details.