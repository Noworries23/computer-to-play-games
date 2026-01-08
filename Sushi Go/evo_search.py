import random
from datetime import datetime
from multiprocessing import Pool
from copy import deepcopy
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
    Returns (config_dict, win_rate)
    """
    config, num_games = config_tuple
    
    wins = 0
    for _ in range(num_games):
        our_player = ConfigurableYOURNAMEPlayer("Config Player", config)
        random_players = [RandomPlayer(f"Random {i}") for i in range(3)]
        players = [our_player] + random_players
        
        scores = run_game(players, print_output=False)
        max_score = max(scores.values())
        if scores[our_player] == max_score:
            wins += 1
    
    win_rate = wins / num_games
    return (config, win_rate)


class EvolutionarySearch:
    """Evolutionary algorithm for finding optimal card priorities"""
    
    def __init__(self, population_size=50, games_per_eval=15, num_workers=4):
        self.population_size = population_size
        self.games_per_eval = games_per_eval
        self.num_workers = num_workers
        
        self.card_types = [
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
        
        self.population = []
        self.fitness_scores = {}
        self.generation = 0
        self.best_overall = None
        self.best_overall_fitness = 0
    
    def create_random_config(self):
        """Create a random priority configuration"""
        shuffled = self.card_types.copy()
        random.shuffle(shuffled)
        return {card_type: idx + 1 for idx, card_type in enumerate(shuffled)}
    
    def initialize_population(self):
        """Create initial random population"""
        self.population = [self.create_random_config() for _ in range(self.population_size)]
    
    def evaluate_population(self):
        """Evaluate fitness of all individuals in population"""
        eval_tasks = [(config, self.games_per_eval) for config in self.population]
        self.fitness_scores = {}
        
        with Pool(processes=self.num_workers) as pool:
            for config, win_rate in tqdm(
                pool.imap_unordered(evaluate_config, eval_tasks),
                total=len(eval_tasks),
                desc=f"Gen {self.generation} Evaluation",
                unit="config"
            ):
                config_key = tuple(sorted(config.items(), key=lambda x: x[1]))
                self.fitness_scores[config_key] = win_rate
                
                # Track best found so far
                if win_rate > self.best_overall_fitness:
                    self.best_overall_fitness = win_rate
                    self.best_overall = config
                    tqdm.write(f"🎯 NEW BEST: {win_rate:.2%} win rate (Gen {self.generation})")
    
    def selection(self):
        """Select top individuals for breeding"""
        # Sort by fitness
        sorted_pop = sorted(
            self.population,
            key=lambda config: self.fitness_scores.get(tuple(sorted(config.items(), key=lambda x: x[1])), 0),
            reverse=True
        )
        
        # Keep top 50% (elitism)
        self.population = sorted_pop[:len(self.population) // 2]
    
    def crossover(self, parent1, parent2):
        """
        Crossover two parents to create offspring.
        Swap priority values between parents.
        """
        child = parent1.copy()
        
        # Randomly swap some card priorities with parent2
        num_swaps = random.randint(1, 4)
        swap_cards = random.sample(self.card_types, num_swaps)
        
        for card in swap_cards:
            child[card] = parent2[card]
        
        # Fix duplicate priorities
        self._fix_duplicates(child)
        return child
    
    def mutate(self, config):
        """
        Mutate a configuration by randomly changing priorities.
        """
        mutation_rate = 0.3
        child = config.copy()
        
        # Randomly shuffle some priorities
        if random.random() < mutation_rate:
            # Swap two random cards' priorities
            card1, card2 = random.sample(self.card_types, 2)
            child[card1], child[card2] = child[card2], child[card1]
        
        # Sometimes do a bigger mutation
        if random.random() < 0.1:
            # Re-randomize 2-3 cards
            cards_to_reshuffle = random.sample(self.card_types, random.randint(2, 3))
            values = [child[card] for card in cards_to_reshuffle]
            random.shuffle(values)
            for card, val in zip(cards_to_reshuffle, values):
                child[card] = val
        
        return child
    
    def _fix_duplicates(self, config):
        """Ensure all priorities are unique (1-12)"""
        used_priorities = set()
        available_priorities = set(range(1, len(self.card_types) + 1))
        
        # First pass: keep valid priorities
        for card in self.card_types:
            if config[card] in available_priorities and config[card] not in used_priorities:
                used_priorities.add(config[card])
                available_priorities.discard(config[card])
        
        # Second pass: reassign duplicates/invalid
        for card in self.card_types:
            if config[card] not in used_priorities:
                priority = available_priorities.pop()
                config[card] = priority
                used_priorities.add(priority)
    
    def breed(self):
        """Create new offspring through crossover and mutation"""
        new_population = self.population.copy()  # Keep elite
        
        # Generate offspring to reach population size
        while len(new_population) < self.population_size:
            parent1 = random.choice(self.population)
            parent2 = random.choice(self.population)
            
            # Crossover
            child = self.crossover(parent1, parent2)
            
            # Mutate
            child = self.mutate(child)
            
            new_population.append(child)
        
        self.population = new_population[:self.population_size]
    
    def evolve(self, num_generations=30):
        """Run the evolutionary algorithm"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print(f"\n{'='*70}")
        print(f"Evolutionary Search Started: {timestamp}")
        print(f"Population size: {self.population_size}")
        print(f"Games per evaluation: {self.games_per_eval}")
        print(f"Number of generations: {num_generations}")
        print(f"{'='*70}\n")
        
        self.initialize_population()
        
        for gen in range(num_generations):
            self.generation = gen
            
            print(f"\n--- Generation {gen + 1}/{num_generations} ---")
            
            # Evaluate
            self.evaluate_population()
            
            # Get stats
            fitness_values = list(self.fitness_scores.values())
            avg_fitness = sum(fitness_values) / len(fitness_values)
            max_fitness = max(fitness_values)
            
            print(f"Avg fitness: {avg_fitness:.2%} | Max fitness: {max_fitness:.2%} | Best overall: {self.best_overall_fitness:.2%}")
            
            # Selection
            self.selection()
            
            # Breeding
            self.breed()
        
        # Final evaluation
        self.generation = num_generations
        self.evaluate_population()
        
        print(f"\n{'='*70}")
        print(f"EVOLUTION COMPLETE")
        print(f"{'='*70}")
        print(f"Best Win Rate: {self.best_overall_fitness:.2%}")
        print(f"\nBest configuration to use:")
        print("self.priorities = {")
        for card_type, priority in sorted(self.best_overall.items(), key=lambda x: x[1]):
            print(f"    Card.Type.{card_type.name}: {priority},")
        print("}")
        print(f"{'='*70}\n")
        
        return self.best_overall, self.best_overall_fitness


if __name__ == "__main__":
    # Run evolutionary search
    evo = EvolutionarySearch(
        population_size=40,      # Population of 40 individuals
        games_per_eval=15,       # 15 games per evaluation (faster feedback)
        num_workers=4            # 4 parallel workers
    )
    
    best_config, best_fitness = evo.evolve(num_generations=25)
    
    # Save results
    import json
    result = {
        'best_config': {str(k): v for k, v in best_config.items()},
        'best_win_rate': best_fitness,
        'method': 'evolutionary_algorithm'
    }
    
    with open('evo_search_best_config.json', 'w') as f:
        json.dump(result, f, indent=2)
    
    print("Best configuration saved to 'evo_search_best_config.json'")
