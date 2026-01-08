import itertools
import json
import random
from datetime import datetime
from multiprocessing import Pool, Manager
from tqdm import tqdm
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

def evaluate_config(config_tuple):
    """
    Evaluate a single priority configuration.
    Returns (config_name, priorities_dict, win_rate)
    """
    config_name, priorities_config, num_games = config_tuple
    
    wins = 0
    for _ in range(num_games):
        our_player = ConfigurableYOURNAMEPlayer("Config Player", priorities_config)
        random_players = [RandomPlayer(f"Random {i}") for i in range(3)]
        players = [our_player] + random_players
        
        scores = run_game(players, print_output=False)
        max_score = max(scores.values())
        if scores[our_player] == max_score:
            wins += 1
    
    win_rate = wins / num_games
    return (config_name, priorities_config, win_rate)

def generate_all_configs(num_random_perms=2000):
    """
    Generate a large number of random priority configurations.
    Tests strategic variations plus many random permutations.
    """
    
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
    
    configs = []
    
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
    configs.append(("default", default_priorities))
    
    # Test strategic variations
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
    configs.append(("maki_first", maki_first))
    
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
    configs.append(("nigiri_first", nigiri_first))
    
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
    configs.append(("combos_first", combos_first))
    
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
    configs.append(("pudding_aware", pudding_aware))
    
    # Generate many random permutations
    print(f"Generating {num_random_perms} random configurations...")
    for i in range(num_random_perms):
        shuffled = card_types.copy()
        random.shuffle(shuffled)
        random_config = {card_type: idx + 1 for idx, card_type in enumerate(shuffled)}
        configs.append((f"random_{i}", random_config))
    
    return configs

def grid_search_parallel(num_games_per_config=20, num_workers=4, num_random_perms=2000):
    """
    Perform comprehensive parallel grid search.
    """
    
    configs = generate_all_configs(num_random_perms=num_random_perms)
    total_configs = len(configs)
    
    # Prepare evaluation tasks
    eval_tasks = [(name, config, num_games_per_config) for name, config in configs]
    
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"\n{'='*70}")
    print(f"Parallel Grid Search Started: {timestamp}")
    print(f"Total configurations: {total_configs}")
    print(f"Games per config: {num_games_per_config}")
    print(f"Total game simulations: ~{total_configs * num_games_per_config:,}")
    print(f"Worker processes: {num_workers}")
    print(f"{'='*70}\n")
    
    best_win_rate = 0
    best_config = None
    results = []
    processed = 0
    
    # Use multiprocessing pool with live progress updates using tqdm
    with Pool(processes=num_workers) as pool:
        for config_name, priorities, win_rate in tqdm(pool.imap_unordered(evaluate_config, eval_tasks), total=total_configs, desc="Evaluating configs", unit="config"):
            processed += 1
            results.append({
                'config_name': config_name,
                'win_rate': win_rate,
                'priorities': priorities
            })
            
            # Track best found so far
            if win_rate > best_win_rate:
                best_win_rate = win_rate
                best_config = config_name
                tqdm.write(f"🎯 NEW BEST: {config_name} - {win_rate:.2%} win rate")
    
    # Sort results by win rate
    results.sort(key=lambda x: x['win_rate'], reverse=True)
    
    print(f"\n{'='*70}")
    print("FINAL RESULTS (Top 20)")
    print(f"{'='*70}\n")
    
    for idx, result in enumerate(results[:20]):
        print(f"{idx+1:2d}. {result['config_name']:20s} - {result['win_rate']:.2%} win rate")
    
    print(f"\n{'='*70}")
    print(f"BEST CONFIGURATION FOUND")
    print(f"{'='*70}")
    print(f"Name: {results[0]['config_name']}")
    print(f"Win Rate: {results[0]['win_rate']:.2%}")
    print(f"\nBest priorities configuration to use:")
    print("self.priorities = {")
    for card_type, priority in sorted(results[0]['priorities'].items(), key=lambda x: x[1]):
        print(f"    Card.Type.{card_type.name}: {priority},")
    print("}")
    print(f"{'='*70}\n")
    
    # Save results
    results_for_json = []
    for result in results:
        result_copy = result.copy()
        result_copy['priorities'] = {str(k): v for k, v in result_copy['priorities'].items()}
        results_for_json.append(result_copy)
    
    with open('grid_search_results_mp.json', 'w') as f:
        json.dump(results_for_json, f, indent=2)
    
    print(f"Full results saved to 'grid_search_results_mp.json'")
    
    return results

if __name__ == "__main__":
    # Run parallel grid search
    # - 20 games per config (fast feedback, reasonable sample size)
    # - 4 worker processes (adjust based on your CPU cores)
    # - 2000 random permutations (2000+ configurations total)
    results = grid_search_parallel(
        num_games_per_config=20,
        num_workers=4,
        num_random_perms=2000
    )
