import itertools
import json
from datetime import datetime
from GameEngine import GameEngine
from SushiGo.SushiGoBoard import SushiGoBoard
from SushiGo.Card import Card
from SushiGo.SushiGoYOURNAMEPlayer import SushiGoYOURNAMEPlayer
from RandomPlayer import RandomPlayer

class ConfigurableYOURNAMEPlayer(SushiGoYOURNAMEPlayer):
    """Wrapper to allow setting custom priorities"""
    def __init__(self, name, priorities_dict):
        super().__init__(name)
        self.priorities = priorities_dict

def run_game(players, print_output=False):
    """Run a single game and return the scores"""
    board = SushiGoBoard(players)
    board.output = print_output
    engine = GameEngine(board)
    engine.run(False)
    return board.scoreBoard()

def evaluate_config(priorities_config, num_games=50):
    """
    Evaluate a priority configuration against random players.
    Returns the win rate of the configured player.
    """
    wins = 0
    
    for _ in range(num_games):
        # Create players: our configured player vs 3 random players
        our_player = ConfigurableYOURNAMEPlayer("Config Player", priorities_config)
        random_players = [RandomPlayer(f"Random {i}") for i in range(3)]
        players = [our_player] + random_players
        
        # Run game
        scores = run_game(players, print_output=False)
        
        # Check if our player won (highest score)
        max_score = max(scores.values())
        if scores[our_player] == max_score:
            wins += 1
    
    win_rate = wins / num_games
    return win_rate

def grid_search(num_games_per_config=50, num_configs=None):
    """
    Perform comprehensive grid search over priority configurations.
    
    Tests many random permutations to find the optimal configuration.
    """
    
    import random
    
    card_types = [
        Card.Type.TEMPURA,
        Card.Type.SASHIMI,
        Card.Type.DUMPLING,
        Card.Type.SINGLE_MAKI,
        Card.Type.DOUBLE_MAKI,
        Card.Type.TRIPLE_MAKI,
        Card.Type.SALMON_NIGIRI,
        Card.Type.SQUID_NIGIRI,
        Card.Type.EGG_NIGIRI,
        Card.Type.PUDDING,
        Card.Type.WASABI,
        Card.Type.CHOPSTICKS
    ]
    
    configs_to_test = []
    
    # Test 1: Default config
    default_priorities = {
        Card.Type.TEMPURA: 1,
        Card.Type.SASHIMI: 2,
        Card.Type.DUMPLING: 3,
        Card.Type.SINGLE_MAKI: 4,
        Card.Type.DOUBLE_MAKI: 5,
        Card.Type.TRIPLE_MAKI: 6,
        Card.Type.SALMON_NIGIRI: 7,
        Card.Type.SQUID_NIGIRI: 8,
        Card.Type.EGG_NIGIRI: 9,
        Card.Type.PUDDING: 10,
        Card.Type.WASABI: 11,
        Card.Type.CHOPSTICKS: 12
    }
    configs_to_test.append(("default", default_priorities))
    
    # Test strategic variations
    # Maki-focused (higher value first)
    maki_first = {
        Card.Type.TRIPLE_MAKI: 1,
        Card.Type.DOUBLE_MAKI: 2,
        Card.Type.SINGLE_MAKI: 3,
        Card.Type.SALMON_NIGIRI: 4,
        Card.Type.SQUID_NIGIRI: 5,
        Card.Type.EGG_NIGIRI: 6,
        Card.Type.DUMPLING: 7,
        Card.Type.SASHIMI: 8,
        Card.Type.TEMPURA: 9,
        Card.Type.WASABI: 10,
        Card.Type.CHOPSTICKS: 11,
        Card.Type.PUDDING: 12
    }
    configs_to_test.append(("maki_first", maki_first))
    
    # Nigiri-focused
    nigiri_first = {
        Card.Type.SALMON_NIGIRI: 1,
        Card.Type.SQUID_NIGIRI: 2,
        Card.Type.EGG_NIGIRI: 3,
        Card.Type.TRIPLE_MAKI: 4,
        Card.Type.DOUBLE_MAKI: 5,
        Card.Type.SINGLE_MAKI: 6,
        Card.Type.DUMPLING: 7,
        Card.Type.SASHIMI: 8,
        Card.Type.TEMPURA: 9,
        Card.Type.WASABI: 10,
        Card.Type.CHOPSTICKS: 11,
        Card.Type.PUDDING: 12
    }
    configs_to_test.append(("nigiri_first", nigiri_first))
    
    # Combos-focused (combos worth more)
    combos_first = {
        Card.Type.TEMPURA: 1,
        Card.Type.SASHIMI: 2,
        Card.Type.DUMPLING: 3,
        Card.Type.CHOPSTICKS: 4,
        Card.Type.WASABI: 5,
        Card.Type.TRIPLE_MAKI: 6,
        Card.Type.DOUBLE_MAKI: 7,
        Card.Type.SINGLE_MAKI: 8,
        Card.Type.SALMON_NIGIRI: 9,
        Card.Type.SQUID_NIGIRI: 10,
        Card.Type.EGG_NIGIRI: 11,
        Card.Type.PUDDING: 12
    }
    configs_to_test.append(("combos_first", combos_first))
    
    # Pudding-aware (pudding early to secure)
    pudding_aware = {
        Card.Type.PUDDING: 1,
        Card.Type.DUMPLING: 2,
        Card.Type.TEMPURA: 3,
        Card.Type.SASHIMI: 4,
        Card.Type.TRIPLE_MAKI: 5,
        Card.Type.DOUBLE_MAKI: 6,
        Card.Type.SINGLE_MAKI: 7,
        Card.Type.SALMON_NIGIRI: 8,
        Card.Type.SQUID_NIGIRI: 9,
        Card.Type.EGG_NIGIRI: 10,
        Card.Type.WASABI: 11,
        Card.Type.CHOPSTICKS: 12
    }
    configs_to_test.append(("pudding_aware", pudding_aware))
    
    # Generate hundreds of random permutations for comprehensive search
    print("Generating 500 random configurations...")
    for i in range(500):
        shuffled = card_types.copy()
        random.shuffle(shuffled)
        random_config = {card_type: idx + 1 for idx, card_type in enumerate(shuffled)}
        configs_to_test.append((f"random_{i}", random_config))
    
    results = []
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    print(f"\n{'='*60}")
    print(f"Grid Search Started: {timestamp}")
    print(f"Games per config: {num_games_per_config}")
    print(f"Total configs to test: {len(configs_to_test)}")
    print(f"{'='*60}\n")
    
    for idx, (config_name, priorities) in enumerate(configs_to_test):
        print(f"[{idx+1}/{len(configs_to_test)}] Testing config: {config_name}...", end="", flush=True)
        
        win_rate = evaluate_config(priorities, num_games=num_games_per_config)
        results.append({
            'config_name': config_name,
            'win_rate': win_rate,
            'priorities': priorities
        })
        
        print(f" Win Rate: {win_rate:.2%}")
    
    # Sort by win rate
    results.sort(key=lambda x: x['win_rate'], reverse=True)
    
    print(f"\n{'='*60}")
    print("RESULTS (Sorted by Win Rate)")
    print(f"{'='*60}\n")
    
    for idx, result in enumerate(results):
        print(f"{idx+1}. {result['config_name']}: {result['win_rate']:.2%} win rate")
    
    print(f"\n{'='*60}")
    print(f"BEST CONFIG: {results[0]['config_name']} with {results[0]['win_rate']:.2%} win rate")
    print(f"{'='*60}\n")
    
    # Save best config
    best_config = results[0]
    
    # Print the best priorities for easy copy-paste
    print("Best priorities configuration to use:")
    print("self.priorities = {")
    for card_type, priority in sorted(best_config['priorities'].items(), key=lambda x: x[1]):
        print(f"    Card.Type.{card_type.name}: {priority},")
    print("}")
    
    # Save to file (convert Card.Type keys to strings for JSON serialization)
    results_for_json = []
    for result in results:
        result_copy = result.copy()
        result_copy['priorities'] = {str(k): v for k, v in result_copy['priorities'].items()}
        results_for_json.append(result_copy)
    
    with open('grid_search_results.json', 'w') as f:
        json.dump(results_for_json, f, indent=2)
    
    print(f"\nDetailed results saved to 'grid_search_results.json'")
    
    return results

if __name__ == "__main__":
    # Run comprehensive grid search with 30 games per config
    # 505 configs * 30 games = ~15,150 games total (reasonable runtime)
    results = grid_search(num_games_per_config=30)
