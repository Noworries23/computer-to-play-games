import random
import multiprocessing
from concurrent.futures import ProcessPoolExecutor
from SushiGo.Card import Card
from RandomPlayer import RandomPlayer
# (Assuming other imports like GameEngine, SushiGoBoard, etc. are available as before)

# --- GENETIC ALGORITHM PARAMETERS ---
POPULATION_SIZE = 100    # Number of different strategies in each generation
GENERATIONS = 50        # How many rounds of evolution to run
ELITISM_COUNT = 10      # Top 10 strategies are kept unchanged
MUTATION_RATE = 0.2     # 20% chance to swap card priorities
GAMES_PER_EVAL = 50     # Games played to determine fitness

CARD_TYPES = [
    Card.Type.TEMPURA, Card.Type.SASHIMI, Card.Type.DUMPLING,
    Card.Type.SINGLE_MAKI, Card.Type.DOUBLE_MAKI, Card.Type.TRIPLE_MAKI,
    Card.Type.SALMON_NIGIRI, Card.Type.SQUID_NIGIRI, Card.Type.EGG_NIGIRI,
    Card.Type.PUDDING, Card.Type.WASABI, Card.Type.CHOPSTICKS
]

def create_random_dna():
    """Generates a random priority list."""
    shuffled = CARD_TYPES.copy()
    random.shuffle(shuffled)
    return {card_type: idx + 1 for idx, card_type in enumerate(shuffled)}

def mutate(dna):
    """Randomly swaps the priority of two cards."""
    if random.random() < MUTATION_RATE:
        c1, c2 = random.sample(CARD_TYPES, 2)
        dna[c1], dna[c2] = dna[c2], dna[c1]
    return dna

def crossover(parent1, parent2):
    """Combines two priority lists (DNA) into one offspring."""
    # We take the order of cards from parent 1, but for some we use parent 2's rank
    split = random.randint(1, len(CARD_TYPES) - 1)
    new_order = CARD_TYPES.copy()
    # Simple crossover: shuffle based on a mix of parent preferences
    random.shuffle(new_order) 
    return {card_type: idx + 1 for idx, card_type in enumerate(new_order)}

def evaluate_fitness(dna):
    """Wrapper for your existing evaluate_config function."""
    # This function is what the workers will run
    win_rate = evaluate_config(dna, num_games=GAMES_PER_EVAL)
    return dna, win_rate

def evolve():
    # 1. Initialize Population
    population = [create_random_dna() for _ in range(POPULATION_SIZE)]
    
    print(f"Starting Evolution: {GENERATIONS} generations with {POPULATION_SIZE} individuals.")

    for gen in range(GENERATIONS):
        # 2. Parallel Evaluation (Fitness)
        with ProcessPoolExecutor(max_workers=90) as executor:
            results = list(executor.map(evaluate_fitness, population))
        
        # Sort by win rate (fitness)
        results.sort(key=lambda x: x[1], reverse=True)
        best_dna, best_win_rate = results[0]
        
        print(f"Gen {gen}: Best Win Rate = {best_win_rate:.2%}")

        # 3. Selection & Elitism
        new_population = [r[0] for r in results[:ELITISM_COUNT]]

        # 4. Reproduction (Crossover & Mutation)
        while len(new_population) < POPULATION_SIZE:
            p1, p2 = random.sample(new_population[:20], 2) # Pick from top 20
            child = crossover(p1, p2)
            child = mutate(child)
            new_population.append(child)
        
        population = new_population

    return results[0] # Return the ultimate winner

if __name__ == "__main__":
    best_strategy, final_win_rate = evolve()
    print("\n--- EVOLUTION COMPLETE ---")
    print(f"Final Best Win Rate: {final_win_rate:.2%}")
    print("Priority List:", best_strategy)